import os
import requests
import json

import streamlit as st

# Custom errors for download XML
class DownloadError(Exception):
    pass


class DownloadXML:
    
    def __init__(self, image: str, user: str, password: str, verbose=False, streamlit_mode=False):
        """
        Download XML data from Copernicus Scihub API

        :param image: Scene ID of Sentinel-1 image
        :param user: Username for Copernicus Scihub
        :param password: Password for Copernicus Scihub
        :param verbose: Show print statements, defaults to False
        :param streamlit_mode: Run stsa for streamlit
        """
        self._image = image
        self._user = user
        self._password = password
        self._verbose = verbose
        self._url = None
        self._CATALOGUE_ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        self._DOWNLOAD_ODATA_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products"
        self._streamlit_mode = streamlit_mode
        self.session, self.response = self._authenticate(user, password)
        self.product_is_online = None
        self.xml_paths = []
        
        if 'SLC' not in self._image:
            msg = 'Scene ID does not belong to an SLC image'
            if self._streamlit_mode:
                st.error(msg)
                st.stop()
            else:
                raise DownloadError(msg)
            
    def _authenticate(self, username, password):
        """
        Authenticate with Copernicus Dataspace API
        """
        data = {
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        session = requests.Session()
        response = session.post(url, data=data)
        response.raise_for_status()
        return session, response

    
    def download_xml(self, output_directory: str, polarization: str = 'vv'):
        """
        Download XML metadata from Copernicus Scihub

        :param output_directory: Output folder for downloaded files
        :param polarization: Polarization of the image. Default is 'vv'
        """
        
        # Check polarization argument
        if polarization.lower() not in ['vv', 'vh', 'hh', 'hv']:
            raise DownloadError(f'Polarization "{polarization}" is not accepted.')
        polarization = polarization.lower()
        
        # Get UUID from scene ID
        link = self._get_product_uuid_link()
        
        # Construct URL that shows XML files
        # Looks like:
        # https://download.dataspace.copernicus.eu/odata/v1/Products({scene_id})/Nodes({scene}.SAFE)/Nodes(annotation)/Nodes
        self._url = f"{link}/Nodes({self._image}.SAFE)/Nodes(annotation)/Nodes"
        
        # Connect and check response code
        if self._verbose is True:
            print('Connecting to Copernicus API...')        
        response = self.session.get(self._url)
        self._check_requests_status_code(response.status_code)
        response_json = json.loads(response.text)
        
        # Parse response and download XML files
        for item in response_json["result"]:
            if item["Name"].endswith(".xml") and f'-{polarization}-' in item["Name"]:
                # Download XML File
                download_url = f"{self._url}({item['Name']})/$value"
                token = self.response.json()["access_token"]
                response_metadata = self.session.get(download_url, headers={"Authorization": f"Bearer {token}"})
                outpath = os.path.join(output_directory, item["Name"])
                with open(outpath, 'wb') as f:
                    f.write(response_metadata.content)
                self.xml_paths.append(outpath)

    def _check_product_is_online(self, url: str) -> bool:
        """
        Check if product is online or not

        :param url: URL of product
        :return: True if product is online, False otherwise
        :rtype: bool
        """
        # Access API
        response = self.session.get(url)
        self._check_requests_status_code(response.status_code)
        response_json = json.loads(response.text)
        
        # Check if product is online
        if response_json["Online"]:
            return True
        return False
                
    def _check_requests_status_code(self, code: int):
        """
        Check return code of the API.

        :param code: Return code received from server in integer format
        """

        if code == 200:
            if self._verbose:
                print('Connection successful')
            return
        elif 200 < code < 300:
            msg = f'Connected to server but something went wrong. Status code: {code}'
            if self._streamlit_mode:
                st.warning(msg)
            else:
                print(f'Connected to server but something went wrong. Status code: {code}')
        elif code == 401:
            msg = f'Username and password not valid. Status code: {code}'
            if self._streamlit_mode:
                st.error(msg)
                st.stop()
            else:
                raise DownloadError(msg)
        elif code == 404:
            msg = f'Could not connect to server. Status code: {code}'
            if self._streamlit_mode:
                st.error(msg)
                st.stop()
            else:
                raise DownloadError(msg)
        else:
            msg = f'API status code: {code}'
            if self._streamlit_mode:
                st.warning(msg)
            else:
                print(msg)
        return
    
    def _get_product_uuid_link(self) -> str:
        """
        Prepare UUID link according to the scene ID.
        Result looks like https://download.dataspace.copernicus.eu/odata/v1/Products(scene_id)

        :return: URL of scene
        :rtype: str
        """
        
        # Search Products archive first. If it is not present there then
        # search in the DeletedProducts archive
        # Access API
        # url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Name eq '{self._image}.SAFE'"
        url = f"{self._CATALOGUE_ODATA_URL}?$filter=Name eq '{self._image}.SAFE'"
        response = self.session.get(url)
        self._check_requests_status_code(response.status_code)
        response_json = json.loads(response.text)
        # Get UUID
        if len(response_json["value"]) == 0:
            raise DownloadError(f'Scene ID not found for "{self._image}"')
        scene_id = response_json["value"][0]["Id"]
        # return f"https://download.dataspace.copernicus.eu/odata/v1/Products({scene_id})"
        return f"{self._DOWNLOAD_ODATA_URL}({scene_id})"


if __name__ == '__main__':
    pass
