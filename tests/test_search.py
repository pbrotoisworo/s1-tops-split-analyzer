import json
import os
import subprocess
import sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STSA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'stsa')
TESTS_DIR = os.path.abspath('tests')
# sys.path.append(REPO_ROOT)
sys.path.append(STSA_DIR)

import pandas as pd
import pytest

from search import DownloadXML

username = os.environ['USERNAME']
password = os.environ['PASSWORD']

data1 = {
    'SCENE_ID': 'S1A_IW_SLC__1SDV_20210907T043106_20210907T043134_039571_04AD68_B6C1',
    'UUID': '701b2515-5a29-44f3-9ce1-f185fcebf4de',
    'XML_FILES': [
        's1a-iw1-slc-vh-20210907t043106-20210907t043134-039571-04ad68-001.xml',
        's1a-iw1-slc-vv-20210907t043106-20210907t043134-039571-04ad68-004.xml',
        's1a-iw2-slc-vh-20210907t043107-20210907t043132-039571-04ad68-002.xml',
        's1a-iw2-slc-vh-20210907t043107-20210907t043132-039571-04ad68-002.xml',
        's1a-iw2-slc-vv-20210907t043107-20210907t043132-039571-04ad68-005.xml',
        's1a-iw3-slc-vh-20210907t043108-20210907t043133-039571-04ad68-003.xml',
        's1a-iw3-slc-vv-20210907t043108-20210907t043133-039571-04ad68-006.xml'
    ]
}

@pytest.mark.xfail
def test_invalid_item():
    "Test downloading a GRDH scene"
    image = r'S1A_IW_GRDH_1SDV_20210907T043107_20210907T043132_039571_04AD68_65B4'
    download = DownloadXML(
        image=image,
        user='',
        password=''
    )

def test_api_connection():
    "Test Copernicus API connection"
    
    
    download = DownloadXML(
        image=data1['SCENE_ID'],
        user=username,
        password=password
    )
    download.download_xml(output_directory=TESTS_DIR)
    output_files = os.listdir(TESTS_DIR)
    for item in data1['XML_FILES']:
        assert item in output_files, f'Missing file! Expected {item} in output file. Output directory contains: {output_files}'
