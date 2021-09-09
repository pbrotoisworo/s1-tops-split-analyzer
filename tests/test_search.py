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
    'SCENE_ID': 'S1B_IW_SLC__1SDV_20210817T161547_20210817T161613_028288_036013_900E',
    'UUID': '742a9324-3375-4aef-bc96-d4a2cfd6ac42',
    'XML_FILES': [
        's1b-iw1-slc-vh-20210817t161548-20210817t161613-028288-036013-001.xml',
        's1b-iw1-slc-vv-20210817t161548-20210817t161613-028288-036013-004.xml',
        's1b-iw2-slc-vh-20210817t161547-20210817t161612-028288-036013-002.xml',
        's1b-iw2-slc-vv-20210817t161547-20210817t161612-028288-036013-005.xml',
        's1b-iw3-slc-vh-20210817t161547-20210817t161613-028288-036013-003.xml',
        's1b-iw3-slc-vv-20210817t161547-20210817t161613-028288-036013-006.xml'
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

def test_scene1():
    "Download XML files using API"
    
    
    download = DownloadXML(
        image=data1['SCENE_ID'],
        user=username,
        password=password
    )
    download.download_xml(output_directory=TESTS_DIR)
    output_files = os.listdir(TESTS_DIR)
    for item in data1['XML_FILES']:
        assert item in output_files, f'Missing file! Expected {item} in output file. Output directory contains: {output_files}'
