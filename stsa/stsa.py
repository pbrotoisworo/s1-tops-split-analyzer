###########################################
# Author: Panji P. Brotoisworo
# License: Apache License 2.0 (Apache-2.0)
###########################################

import argparse
import json
import glob
import os
import re
import sys
from typing import Union
import xml.etree.ElementTree as ET
import warnings
from zipfile import ZipFile

import folium
import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd

try:
    from search import DownloadXML, DownloadError
except ImportError:
    # Handle import errors when testing
    from .search import DownloadXML, DownloadError


class TopsSplitAnalyzer:

    def __init__(self, target_subswaths: Union[None, str, list] = None, polarization: str = 'vv',
                 verbose: bool = True, streamlit_mode: bool = False):
        """
        Class to interpret and visualize S1-TOPS-SPLIT data as seen in ESA SNAP software.
        
        :param target_subswath: String or list containing strings of subswaths to load. Defaults to all subswaths.
        :param polarization: Polarization of imagery. Valid options are 'vv' or 'vh' polarizations. Defaults to 'vv'
        :param verbose: Print statements. Defaults to True
        :param streamlit_mode: Run stsa for streamlit
        """

        if isinstance(target_subswaths, str):
            if target_subswaths.lower() not in ['iw1', 'iw2', 'iw3']:
                raise ValueError(f'Target subswath "{target_subswaths.lower()}" not a valid subswath')

        if isinstance(target_subswaths, list):
            target_subswaths = [x.lower() for x in target_subswaths]

        if polarization is None:
            polarization = 'vv'
        if polarization.lower() not in ['vv', 'vh', 'hh', 'hv']:
            raise ValueError(f'Input polarization "{polarization}" not recognized.')

        # Load and check user inputs
        if target_subswaths is None:
            # Defaults to all bands if no target subswath specified
            target_subswaths = ['iw1', 'iw2', 'iw3']

        if polarization is None:
            # Defaults to VV polarization
            polarization = 'vv'

        self._image = None
        self.archive = None
        self._download_id = None
        self._download_folder = None
        self._api_user = None
        self._api_download = None
        self.api_product_is_online = None
        self._is_downloaded_scene = None
        self._is_manifest_safe = None
        self._api_password = None
        self._target_subswath = target_subswaths
        self.polarization = polarization.lower()
        self._verbose = verbose
        self._streamlit_mode = streamlit_mode

        # Declare variables
        self._metadata = None
        self.metadata_file_list = []
        self.total_num_bursts = None
        self.df = None

    def load_api(self, username: str, scene_id: str, password: Union[str, None] = None,
                 download_folder: Union[str, None] = None) -> None:
        """
        Load Sentinel-1 scene through the Copernicus API. Only the relevant XML data will be downloaded.
        Create an account here: https://scihub.copernicus.eu/dhus/#/self-registration

        :param username: Username for Copernicus Scihub
        :param password: Password for Copernicus Scihub. For more secure input do not input a password. User will be
            prompted to enter password via hidden input.
        :param download_folder: Download folder for the XML files
        """

        self._api_user = username
        self._api_password = password
        self._download_id = scene_id
        self._download_folder = download_folder
        self._is_downloaded_scene = True

        if self._download_folder is None:
            raise ValueError('User selected to download from API but no output folder is defined')

        download = DownloadXML(
            image=self._download_id,
            user=self._api_user,
            password=self._api_password,
            verbose=self._verbose,
            streamlit_mode=self._streamlit_mode
        )
        download.download_xml(
            output_directory=self._download_folder,
            polarization=self.polarization
        )

        if not len(download.xml_paths):

            # If running in streamlit mode the app will launch a troubleshooting process to ensure
            # continuous running of the app
            if not self._streamlit_mode:
                raise DownloadError('No matching XML found! Try different parameters')

            print('No matching XML found! Trying again with different polarization.')
            # If not metadata is found try one more time with other default value
            if self.polarization == 'vv' or self.polarization == 'vh':
                print('Vertical polarization detected. Setting polarization to "hh"')
                self.polarization = 'hh'
            elif self.polarization == 'hh' or self.polarization == 'hv':
                print('Horizontal polarization detected. Setting polarization to "vv"')
                self.polarization = 'vv'

            download.download_xml(
                output_directory=self._download_folder,
                polarization=self.polarization
            )
            if not len(download.xml_paths):
                raise DownloadError('No XML files found after troubleshooting!')
            else:
                print(f'Troubleshooting method found {len(download.xml_paths)} files using "{self.polarization}" polarization')

        self.api_product_is_online = download.product_is_online
        self.metadata_file_list = download.xml_paths
        if self.api_product_is_online is False:
            return

        # Load metadata
        self._load_metadata_paths()

        # Load geometry
        self._create_subswath_geometry()

        if self._verbose:
            print(f'Found {len(self.metadata_file_list)} XML paths')

        return

    def load_zip(self, zip_path: Union[str, None] = None):
        """
        Load ZIP file containing Sentinel-1 SLC data. XML data containing the burst regions will be loaded.

        :param zip_path:
        :return:
        """
        self._is_downloaded_scene = False
        self._image = zip_path
        self.archive = ZipFile(self._image)
        if self._verbose:
            print(f'Loaded ZIP file: {os.path.basename(self._image)}')

        # Load metadata
        self._load_metadata_paths()

        # Load geometry
        self._create_subswath_geometry()

        if self._verbose:
            print(f'Found {len(self.metadata_file_list)} XML paths')

        return

    def load_safe(self, safe_path: Union[str, None] = None):
        """
        Load SAFE file containing Sentinel-1 SLC data. XML data containing
        the burst regions will be loaded.

        :param safe_path: Path to the manifest.safe file inside the .SAFE
        directory.
        :return:
        """
        self._is_downloaded_scene = False
        self._image = os.path.dirname(safe_path)
        self._is_manifest_safe = True
        if self._verbose:
            print(f'Loaded SAFE file {self._image}')

        # Load metadata
        self._load_metadata_paths()

        # Load geometry
        self._create_subswath_geometry()

    def load_data(self, zip_path: Union[str, None] = None, download_id: Union[str, None] = None,
                  download_folder: Union[str, None] = None, api_user: Union[str, None] = None,
                  api_password: Union[str, None] = None):
        """
        Load Sentinel-1 XML metadata

        :param zip_path: Path of ZIP file containing full Sentinel-1 image, defaults to None
        :param download_id: Scene ID of Sentinel-1 which will be downloaded, defaults to None
        :param download_folder: Folder where downloaded XML files will be saved, defaults to None
        :param api_user: Username for Copernicus Scihub, defaults to None
        :param api_password: Password for Copernicus Scihub, defaults to None
        """

        # Deprecation message
        warnings.warn('"load_data" is deprecated and will be removed soon. Please use "load_api" or "load_zip" '
                      'in the future.')

        if zip_path is None and download_id is None:
            raise ValueError('No input data detected!')

        self._image = zip_path
        self._download_id = download_id
        self._download_folder = download_folder
        self._api_user = api_user
        self._api_password = api_password
        self._is_downloaded_scene = False

        # Use ZIP file
        if self._image is not None and self._download_id is None:
            self.archive = ZipFile(self._image)
            if self._verbose:
                print(f'Loaded ZIP file: {os.path.basename(self._image)}')

        # Download data
        else:
            self._is_downloaded_scene = True

            if self._download_folder is None:
                raise ValueError('User selected to download from API but no output folder is defined')

            download = DownloadXML(
                image=self._download_id,
                user=self._api_user,
                password=self._api_password,
                verbose=self._verbose
            )
            download.download_xml(
                output_directory=self._download_folder,
                polarization=self.polarization
            )
            self.metadata_file_list = download.xml_paths
            if download.product_is_online is False:
                return

        # Load metadata
        self._load_metadata_paths()

        # Load geometry
        self._create_subswath_geometry()

        if self._verbose:
            print(f'Found {len(self.metadata_file_list)} XML paths')
        return

    def _load_metadata_paths(self):
        """
        Get paths of metadata files based on RegEx string match
        """

        if self._is_downloaded_scene is False:

            # Reset metadata list before loading
            self.metadata_file_list = []

            # Get file list
            if self._is_manifest_safe:
                archive_files = glob.glob(os.path.join(self._image, 'annotation', '*.xml'), recursive=True)
            else:
                archive_files = self.archive.namelist()

            # Get metadata files
            regex_filter = r's1(?:a|b)-iw\d-slc-(?:vv|vh|hh|hv)-.*\.xml'

            for item in archive_files:
                if 'calibration' in item:
                    continue
                match = re.search(regex_filter, item)
                if match:
                    self.metadata_file_list.append(item)
            if not self.metadata_file_list:
                raise Exception(f'No metadata files found in {os.path.basename(self._image)}')
        else:
            if len(self.metadata_file_list) == 0:
                raise Exception(f'No XML files found in {self._download_folder}')

    # Get metadata
    def _load_metadata(self, target_subswath=None, target_polarization=None):
        """
        Load XML data
        :param target_subswath: Desired subswath for metadata extraction
        :param target_polarization: Desired polarization for metadata extraction
        :return: ZipFle object which contains XML file to be loaded into ElementTree
        """

        if not target_subswath:
            target_subswath = self._target_subswath
        if not target_polarization:
            target_polarization = self.polarization

        assert isinstance(target_subswath, str) is True, f'Expected string for target_subswath for _load_metadata. Got {target_subswath} which is type {type(target_subswath)}'

        target_file = None
        for item in self.metadata_file_list:
            if target_subswath in item and target_polarization in item:
                target_file = item
        if not target_file:
            raise Exception(f'Found no matching XML file with target subswath "{target_subswath}" and target polarization "{target_polarization}". \
                            Possible matches: {self.metadata_file_list}')

        if self._is_downloaded_scene is False:
            if self._is_manifest_safe:
                metadata = open(target_file)
            else:
                # Open XML from ZIP
                metadata = self.archive.open(target_file)
        else:
            # Open XML from downloaded or SAFE files
            metadata = target_file

        self._metadata = metadata

        self._check_metadata_loaded = True

    def _parse_location_grid(self):
        """
        Parse the XML metadata and get the coordinate data stored in geolocationGrid
        """

        tree = ET.parse(self._metadata)
        root = tree.getroot()

        # Get subswath and burst coordinates
        lines = []
        coord_list = []
        for grid_list in root.iter('geolocationGrid'):
            for point in grid_list:
                for item in point:
                    lat = item.find('latitude').text
                    lon = item.find('longitude').text
                    line = item.find('line').text
                    lines.append(line)
                    coord_list.append((float(lat), float(lon)))
        if self.total_num_bursts is None and self._verbose:
            print(f'Loaded location grid with {len(set(lines)) - 1} bursts and {len(coord_list)} coordinates')
        self.total_num_bursts = len(set(lines)) - 1

        return coord_list

    def _parse_subswath_geometry(self, coord_list):
        """
        Create geometry from location grid XML data
        :param coord_list: Input coord list loaded from geolocationGrid metadata
        :return:
        """
        def get_coords(index, coord_list):
            coord = coord_list[index]
            assert isinstance(coord[1], float)
            assert isinstance(coord[0], float)
            return coord[1], coord[0]

        bursts_dict = {}
        top_right_idx = 0
        top_left_idx = 20
        bottom_left_idx = 41
        bottom_right_idx = 21

        for burst_num in range(1, self.total_num_bursts + 1):
            # Create polygon
            burst_polygon = Polygon(
                [
                    [get_coords(top_right_idx, coord_list)[0], get_coords(top_right_idx, coord_list)[1]],  # Top right
                    [get_coords(top_left_idx, coord_list)[0], get_coords(top_left_idx, coord_list)[1]],  # Top left
                    [get_coords(bottom_left_idx, coord_list)[0], get_coords(bottom_left_idx, coord_list)[1]],  # Bottom left
                    [get_coords(bottom_right_idx, coord_list)[0], get_coords(bottom_right_idx, coord_list)[1]] # Bottom right
                ]
            )

            top_right_idx += 21
            top_left_idx += 21
            bottom_left_idx += 21
            bottom_right_idx += 21

            bursts_dict[burst_num] = burst_polygon

        return bursts_dict

    def _create_subswath_geometry(self):
        """
        Create geodataframe from the XML metadata
        """

        if isinstance(self._target_subswath, list):
            # Create empty dataframe for subswaths to be added into
            df_all = gpd.GeoDataFrame(columns=['subswath', 'burst', 'geometry'], crs='EPSG:4326')
            for subswath in self._target_subswath:
                self._load_metadata(subswath, self.polarization)
                coord_list = self._parse_location_grid()
                subswath_geom = self._parse_subswath_geometry(coord_list)
                df = gpd.GeoDataFrame(
                    {'subswath': [subswath.upper()] * len(subswath_geom),
                     'burst': [x for x in subswath_geom.keys()],
                     'geometry': [x for x in subswath_geom.values()]
                     },
                    crs='EPSG:4326'
                )
                # Concat to main dataframe
                df_all = gpd.GeoDataFrame(pd.concat([df_all, df]), crs='EPSG:4326')
        else:
            # Write one subswath only
            self._load_metadata()
            coord_list = self._parse_location_grid()
            subswath_geom = self._parse_subswath_geometry(coord_list)
            df_all = gpd.GeoDataFrame(
                {'subswath': [self._target_subswath.upper()] * len(subswath_geom),
                 'burst': [x for x in subswath_geom.keys()],
                 'geometry': [x for x in subswath_geom.values()]
                 },
                crs='EPSG:4326'
            )

        self.df = df_all
        if self.df is None:
            raise Exception('Dataframe is empty. Please check data is loaded properly')

        if self._streamlit_mode is True:
            for item in self.metadata_file_list:
                os.remove(item)

    def to_json(self, output_file):
        """
        Returns S1-TOPS-SPLIT data in JSON format
        :return: JSON
        """
        json_data = json.loads(self.df.to_json())
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=4)

    def to_shapefile(self, output_file):
        """
        Write shapefile of S1-TOPS-SPLIT data
        :param output_file: Path of output shapefile
        """
        self.df.to_file(filename=output_file)

    def to_csv(self, output_file):
        """
        Write CSV of S1-TOPS-SPLIT data
        :param output_file: Path of output CSV file
        """
        self.df.to_csv(output_file, index=False)

    def visualize_webmap(self, polygon=None):
        """
        Visualize S1-TOPS data on a Folium webmap. Intended for Jupyter Notebook environments
        :param polygon: Path of additional shapefile to visualize
        :return: Folium webamp
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            location_x = self.df.centroid.map(lambda p: p.x).iloc[0]
            location_y = self.df.centroid.map(lambda p: p.y).iloc[0]
        m = folium.Map(location=[location_y, location_x], zoom_start=8)

        boundary = folium.FeatureGroup(name='Sentinel-1 Data').add_to(m)

        for item in self.df.iterrows():
            subswath = item[1]['subswath']
            burst = item[1]['burst']
            geom = item[1]['geometry']
            info = f'SUBSWATH: {subswath}<br>Burst: {burst}'
            feature = folium.GeoJson(data=geom, tooltip=info).add_to(boundary)
            boundary.add_child(feature)

        if polygon:
            if self._verbose:
                print('Loading custom shapefile:', polygon)
            # Visualize additional polygon in red color
            style = {'fillColor': '#cc0000', 'color': '#cc0000'}
            df_mask = gpd.read_file(polygon)
            folium.GeoJson(data=df_mask, tooltip='User loaded shapefile', style_function=lambda x: style, name='Additional Polygon').add_to(m)
            folium.LayerControl().add_to(m)
        return m

    def close(self):
        """
        Close connection to ZIP file
        """
        self.archive.close()


if __name__ == '__main__':

    # Define CLI flags and parse inputs
    parser = argparse.ArgumentParser(description='S-1 TOPS SPLIT Analyzer')

    main_args = parser.add_argument_group('Script Parameters')
    main_args.add_argument('-v', help='Verbose mode', action='store_true')
    main_args.add_argument('--zip', help='Input Sentinel-1 ZIP file')
    main_args.add_argument('--api-scene', help='Target scene ID to download')
    main_args.add_argument('--api-user', help='Username for Copernicus Scihub API')
    main_args.add_argument('--api-password', help='Password for Copernicus Scihub API')
    main_args.add_argument('--api-folder', help='Folder for downloaded XML files')
    main_args.add_argument('--safe', help='Input Sentinel-1 manifest.safe file')

    xml_args = parser.add_argument_group('XML Parsing Parameters')
    xml_args.add_argument('--swaths', help='List of subswaths', nargs='*', choices=['iw1', 'iw2', 'iw3'])
    xml_args.add_argument('--polar', help='Polarization', choices=['vv', 'vh'])
    xml_args.add_argument('--shp', help='Output path of shapefile')
    xml_args.add_argument('--csv', help='Output path of CSV file')
    xml_args.add_argument('--json', help='Output path of JSON file')

    args = parser.parse_args()
    args = vars(args)

    s1 = TopsSplitAnalyzer(
        target_subswaths=args['swaths'],
        polarization=args['polar']
    )

    if args['zip'] and (args['api_user'] and args['api_password']):
        print('Error! Input detected for ZIP and API methods. Please use one method only.')
        sys.exit()

    if args['zip'] is not None:
        s1.load_zip(zip_path=args['zip'])
    elif args['safe'] is not None:
        s1.load_safe(safe_path=args['safe'])
    else:
        s1.load_api(
            username=args['api_user'],
            password=args['api_password'],
            scene_id=args['api_scene'],
            download_folder=args['api_folder']
        )

    if args['shp']:
        print('Writing shapefile to', args['shp'])
        s1.to_shapefile(args['shp'])
    if args['csv']:
        print('Writing CSV to', args['csv'])
        s1.to_csv(args['csv'])
    if args['json']:
        print('Writing JSON to', args['json'])
        s1.to_json(args['json'])
