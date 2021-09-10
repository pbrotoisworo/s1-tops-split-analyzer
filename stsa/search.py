import os
import re
import requests
from requests.auth import HTTPBasicAuth
import xmltodict


class DownloadXML:
    
    def __init__(self, image: str, user: str, password: str, verbose=False):
        """
        Download XML data from Copernicus Scihub API

        :param image: Scene ID of Sentinel-1 image
        :param user: Username for Copernicus Scihub
        :param password: Password for Copernicus Scihub
        :param verbose: Show print statements, defaults to False
        """
        
        self._image = image
        self._user = user
        self._password = password
        self._verbose = verbose
        self._auth = HTTPBasicAuth(self._user, self._password)
        self._url = None
        
        if 'SLC' not in self._image:
            raise Exception('Scene ID does not belong to an SLC image')
        
        # Set OData API environment parameters
        os.environ['DHUS_USER'] = user
        os.environ['DHUS_PASSWORD'] = password
    
    def download_xml(self, output_directory: str):
        """
        Download XML metadata from Copernicus Scihub

        :param output_directory: Output folder for downloaded files
        """
        # Get UUID from scene ID
        link = self._get_product_uuid_link()
        
        # If product is offline exit operation
        is_online = self._product_is_online()
        if is_online is False:
            print(f'Warning! Product {self._image} is offline! Please select another image')
            return
        
        # Construct URL that shows XML files
        self._url = f"{link}/Nodes('{self._image}.SAFE')/Nodes('annotation')/Nodes"
        if self._verbose is True:
            print('Connecting to Copernicus API...')
        response = requests.get(self._url, auth=self._auth)
        if self._verbose is True and response.status_code == 200:
            print('Connection successful')
            
        xml_string = response.content
        root = xmltodict.parse(xml_string)
        
        # Get XML files
        for item in range(len(root['feed']['entry'])):
            
            url = root['feed']['entry'][item]['id']
            
            if url.endswith(".xml')"):    
                
                # If it finds an XML file then add /$value to link to the XML file contents
                url += r'/$value'
                
                # Connect to API
                response_metadata = requests.get(url, auth=self._auth)
                
                # Prepare output file
                pattern = r's1[ab]-iw\d-slc-v[vh]-\d{8}t\d{6}-\d{8}t\d{6}-\d{6}-.{6}-\d{3}.xml'
                try:
                    match = re.findall(pattern, url)[0]
                except IndexError:
                    raise IndexError(f'No RegEx match found! String that was searched is: {url}')
                output_file = os.path.join(output_directory, match)
                
                if self._verbose is True:
                    print('Writing', output_file)
                
                # Write metadata file
                with open(output_file, 'wb') as f:
                    f.write(response_metadata.content)
    
    def _product_is_online(self, url: str) -> bool:
        """
        Check if product is online

        :param url: URL containing product details
        :return: Boolean True if online. False if offline
        """
        response = requests.get(url, auth=self._auth)
        xml = response.content
        root = xmltodict.parse(xml)
        is_online = eval(root['entry']['m:properties']['d:Online'].title())
        return is_online
    
    def _get_product_uuid_link(self) -> str:
        """
        Prepare UUID link according to the scene ID
        :return: URL of scene
        :rtype: str
        """
        
        # Search Products archive first. If it is not present there then
        # search in the DeletedProducts archive
        try:
            link = self._search_products_archive('Products')
        except KeyError:
            try:
                link = self._search_products_archive('DeletedProducts')
            except KeyError:
                raise ValueError('XML not detected in DeletedProducts and Products archives. Check if input download scene ID is valid')
        return link
    
    def _search_products_archive(self, data_entity: str) -> str:
        """
        Look up UUID using a Scene ID and return the proper URL

        :param data_entity: Name of data archive. Should be "Products" or "DeletedProducts"
        :return: Constructed URL containing UUID and scene ID
        """
        # Access API
        url = r'https://scihub.copernicus.eu/dhus/odata/v1/{}?$filter=Name%20eq%20%27{}%27'.format(data_entity, self._image)
        response = requests.get(url, auth=HTTPBasicAuth(self._user, self._password))
        xml_string = response.content
        
        # Get UUID link
        root = xmltodict.parse(xml_string)
        link = root['feed']['entry']['id']
        
        return link
    

if __name__ == '__main__':
    pass
