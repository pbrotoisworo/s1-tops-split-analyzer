import json
import os
import subprocess
import sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STSA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'stsa')
# sys.path.append(REPO_ROOT)
# sys.path.append(STSA_DIR)

import pandas as pd
import pytest

from stsa import TopsSplitAnalyzer

global data1
global data2

TEST_DIR = os.path.abspath('tests')
data1 = os.path.join(TEST_DIR, 'data1', 'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE.zip')
data2 = os.path.join(TEST_DIR, 'data2', 'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE.zip')

#################################################################################
# Input tests
#################################################################################

def test_TopsSplitAnalyzer_string_subswath():
    
    s1 = TopsSplitAnalyzer(target_subswaths='iw2')
    s1.load_data(zip_path=data2)
    out_file = 'test_json.json'
    s1.to_json(out_file)
    
    assert os.path.exists(out_file), 'No output detected for string input of subswath'
    os.remove(out_file)
    
def test_TopsSplitAnalyzer_use_defaults():
    
    s1 = TopsSplitAnalyzer()
    s1.load_data(zip_path=data2)
    expected = 'vv'
    actual = s1.polarization
    assert expected == actual, f'Polarization does not match. Actual is {actual}. Expected is {expected}'
    
    expected = ['iw1', 'iw2', 'iw3']
    actual = s1._target_subswath
    
    assert actual == expected, f'Subswaths do not match. Actual is {actual}. Expected is {expected}'
    
def test_TopsSplitAnalyzer_string_caps_input():
    "Check input if in all caps"
    s1 = TopsSplitAnalyzer(target_subswaths=['IW1', 'IW2', 'IW3'], polarization='VV')
    s1.load_data(zip_path=data2)
    
    expected = 'vv'
    actual = s1.polarization
    assert actual == expected, f'Polarization does not match. Actual is {actual}. Expected is {Expected}'
    
    expected = ['iw1', 'iw2', 'iw3']
    actual = s1._target_subswath
    assert actual == expected, f'Subswaths do not match. Actual is {actual}. Expected is {expected}'
    
    # Check internal dataframe
    s1.to_json('scratch.json')
    expected = 'IW1'
    actual = s1.df.iloc[0]['subswath']
    assert actual == expected, f'Subswath string does not match. Actual is {actual}. Expected us {expected}'
    os.remove('scratch.json')
    
@pytest.mark.xfail
def test_TopsSplitAnalyzer_xfail_subswath1():
    "Should fail due to improper input for subswaths"
    s1 = TopsSplitAnalyzer(target_subswaths=['iw1' 'iw2' 'iw3'], polarization='vv')
    s1.load_data(zip_path=data2)
    
@pytest.mark.xfail
def test_TopsSplitAnalyzer_xfail_subswath2():
    "Should fail due to iw4 not being a valid subswath"
    s1 = TopsSplitAnalyzer(target_subswaths=['iw1', 'iw4'], polarization='vv')
    s1.load_data(zip_path=data2)
    
@pytest.mark.xfail
def test_TopsSplitAnalyzer_xfail_invalid_polarization():
    "Should fail due to invalid polarization"
    s1 = TopsSplitAnalyzer(image=data2, polarization='HV')
    s1.load_data(zip_path=data2)
  
def test_TopsSplitAnalyzer_cli_json():
    "CLI with JSON output"
    
    out_file = os.path.join(TEST_DIR, 'cli_json_out.json')
    cmd = f'python stsa.py --zip {data1} --json {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    assert os.path.exists(out_file), f'CLI did not generate expected output. Expected output file {out_file}'
    os.remove(out_file)
    
def test_TopsSplitAnalyzer_cli_shp():
    "CLI with shp output"
    
    out_file = os.path.join(TEST_DIR, 'cli_shp_out.shp')
    cmd = f'python stsa.py --zip {data1} --shp {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    assert os.path.exists(out_file), f'CLI did not generate expected output. Expected output file {out_file}'
    
    out_file_basename = out_file.replace('.shp', '') 
    os.remove(out_file_basename + '.cpg')
    os.remove(out_file_basename + '.dbf')
    os.remove(out_file_basename + '.prj')
    os.remove(out_file_basename + '.shx')
    os.remove(out_file_basename + '.shp')
    
def test_TopsSplitAnalyzer_cli_csv():
    "CLI with CSV output"
    
    out_file = os.path.join(TEST_DIR, 'cli_csv_out.csv')
    cmd = f'python stsa.py --zip {data1} --csv {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    assert os.path.exists(out_file), f'CLI did not generated expected output file {out_file}'
    os.remove(out_file)
    
def test_TopsSplitAnalyzer_cli_subswaths():
    "CLI with different subswath inputs"
    
    out_file = os.path.join(TEST_DIR, 'out_csv.csv')
    
    cmd = f'python stsa.py --zip {data1} --swaths iw1 --csv {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    df = pd.read_csv(out_file)
    expected = 9
    actual = len(df)
    assert actual == expected, f'CSV length did not match expected output. Actual was {actual}. Expected is {expected}'
    os.remove(out_file)
    
    cmd = f'python stsa.py --zip {data1} --swaths iw1 iw3 --csv {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    df = pd.read_csv(out_file)
    expected = 18
    actual = len(df)
    assert actual == expected, f'CSV length did not match expected output. Actual was {actual}. Expected is {expected}'
    os.remove(out_file)
    
    cmd = f'python stsa.py --zip {data1} --swaths iw1 iw3 iw2 --csv {out_file}'.split()
    subprocess.call(cmd, cwd=STSA_DIR)
    
    df = pd.read_csv(out_file)
    expected = 27
    actual = len(df)
    assert actual == expected, f'CSV length did not match expected output. Actual was {actual}. Expected is {expected}'
    os.remove(out_file)

#################################################################################
# Output tests
#################################################################################

# Using data1 folder
def test_TopsSplitAnalyzer_data1_all_vv():
    
    s1 = TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vv')
    s1.load_data(zip_path=data1)
    
    ########################################################################
    # Check metadata list. All 6 items should be loaded regardless of user input
    ########################################################################
    
    expected = ['S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw1-slc-vh-20201123t142500-20201123t142525-035377-042241-001.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw1-slc-vv-20201123t142500-20201123t142525-035377-042241-004.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw2-slc-vh-20201123t142458-20201123t142524-035377-042241-002.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw2-slc-vv-20201123t142458-20201123t142524-035377-042241-005.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw3-slc-vh-20201123t142459-20201123t142524-035377-042241-003.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw3-slc-vv-20201123t142459-20201123t142524-035377-042241-006.xml']
    actual = s1.metadata_file_list
    assert expected == actual, 'Metadata list does not match'
    
    ########################################################################
    # Check shapefile data was generated
    ########################################################################
    
    out_shp_items = [
        os.path.join(TEST_DIR, 'swaths_all_vv.cpg'),
        os.path.join(TEST_DIR, 'swaths_all_vv.dbf'),
        os.path.join(TEST_DIR, 'swaths_all_vv.prj'),
        os.path.join(TEST_DIR, 'swaths_all_vv.shp'),
        os.path.join(TEST_DIR, 'swaths_all_vv.shx')
    ]
    s1.to_shapefile(out_shp_items[3])
    for item in out_shp_items:
        expected = True
        actual = os.path.exists(item)
        assert actual == expected, f'Shapefile was not generated correctly. Missing: {item}'
    
    ########################################################################
    # Check JSON was generated correctly
    ########################################################################
        
    json_out = os.path.join(TEST_DIR, 'test_json.json')
    s1.to_json(json_out)
    
    # Read output JSON file
    with open(json_out) as json_file:
        data = json.load(json_file)        
    assert isinstance(data, dict) == True, 'Error when loading JSON as Python dictionary'
    
    # Test contents
    expected = 'FeatureCollection'
    actual = data['type']
    assert expected == actual, f'JSON data for "type" does not match'
    
    # Test id 0
    expected = {'burst': 1, 'subswath': 'IW1'}
    actual = data['features'][0]['properties']
    assert expected == actual, f'JSON features with ID 0 do not match. Actual is {actual}. Expected is {expected}'
    # Test id 23
    expected = {'burst': 6, 'subswath': 'IW3'}
    actual = data['features'][23]['properties']
    assert expected == actual, f'JSON features with ID 23 do not match. Actual is {actual}. Expected is {expected}'
    
    ########################################################################
    # Check CSV was generated correctly
    ########################################################################
        
    csv_out = os.path.join(TEST_DIR, 'test_csv.csv')
    s1.to_csv(csv_out)
    
    df = pd.read_csv(csv_out)
    
    # Test CSV size
    expected = 27
    actual = len(df)
    assert expected == actual, f'CSV file does not match. Actual is {actual} rows. Expected {expected} rows'
    
    # Check id 0
    expected = 'IW1'
    actual = df.iloc[0]['subswath']
    assert expected == actual, f'Subswath for row 0 does not match. Actual is {actual}. Expected is {expected}'
    
    expected = 1
    actual = df.iloc[0]['burst']
    assert expected == actual, f'Burst for row 0 does not match. Actual is {actual}. Expected is {expected}'
        
    # Delete files after tests
    for item in out_shp_items:
        os.remove(item)
    os.remove(json_out)
    os.remove(csv_out)
    
def test_TopsSplitAnalyzer_data1_all_vh():

    s1 = TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vh')
    s1.load_data(zip_path=data1)
    
    ########################################################################
    # Check metadata list. All 6 items should be loaded regardless of user input
    ########################################################################
    
    expected = ['S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw1-slc-vh-20201123t142500-20201123t142525-035377-042241-001.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw1-slc-vv-20201123t142500-20201123t142525-035377-042241-004.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw2-slc-vh-20201123t142458-20201123t142524-035377-042241-002.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw2-slc-vv-20201123t142458-20201123t142524-035377-042241-005.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw3-slc-vh-20201123t142459-20201123t142524-035377-042241-003.xml',
                'S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE/annotation/s1a-iw3-slc-vv-20201123t142459-20201123t142524-035377-042241-006.xml']
    actual = s1.metadata_file_list
    assert expected == actual, 'Metadata list does not match'
    
    ########################################################################
    # Check shapefile data was generated
    ########################################################################
    
    out_shp_items = [
        os.path.join(TEST_DIR, 'swaths_all_vh.cpg'),
        os.path.join(TEST_DIR, 'swaths_all_vh.dbf'),
        os.path.join(TEST_DIR, 'swaths_all_vh.prj'),
        os.path.join(TEST_DIR, 'swaths_all_vh.shp'),
        os.path.join(TEST_DIR, 'swaths_all_vh.shx')
    ]
    s1.to_shapefile(out_shp_items[3])
    for item in out_shp_items:
        expected = True
        actual = os.path.exists(item)
        assert actual == expected, f'Shapefile was not generated correctly. Missing: {item}'
    
    ########################################################################
    # Check JSON was generated correctly
    ########################################################################
        
    json_out = os.path.join(TEST_DIR, 'test_json.json')
    s1.to_json(json_out)
    
    # Read output JSON file
    with open(json_out) as json_file:
        data = json.load(json_file)        
    assert isinstance(data, dict) == True, 'Error when loading JSON as Python dictionary'
    
    # Test contents
    expected = 'FeatureCollection'
    actual = data['type']
    assert expected == actual, f'JSON data for "type" does not match'
    
    # Test id 0
    expected = {'burst': 1, 'subswath': 'IW1'}
    actual = data['features'][0]['properties']
    assert expected == actual, f'JSON features with ID 0 do not match. Actual is {actual}. Expected is {expected}'
    # Test id 23
    expected = {'burst': 6, 'subswath': 'IW3'}
    actual = data['features'][23]['properties']
    assert expected == actual, f'JSON features with ID 23 do not match. Actual is {actual}. Expected is {expected}'
    
    ########################################################################
    # Check CSV was generated correctly
    ########################################################################
        
    csv_out = os.path.join(TEST_DIR, 'test_csv.csv')
    s1.to_csv(csv_out)
    
    df = pd.read_csv(csv_out)
    
    # Test CSV size
    expected = 27
    actual = len(df)
    assert expected == actual, f'CSV file does not match. Actual is {actual} rows. Expected {expected} rows'
    
    # Check id 0
    expected = 'IW1'
    actual = df.iloc[0]['subswath']
    assert expected == actual, f'Subswath for row 0 does not match. Actual is {actual}. Expected is {expected}'
    
    expected = 1
    actual = df.iloc[0]['burst']
    assert expected == actual, f'Burst for row 0 does not match. Actual is {actual}. Expected is {expected}'
        
    # Delete files after tests
    for item in out_shp_items:
        os.remove(item)
    os.remove(json_out)
    os.remove(csv_out)

# Using data2 folder
def test_TopsSplitAnalyzer_data2_all_vv():
    
    s1 = TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vv')
    s1.load_data(zip_path=data2)
    
    ########################################################################
    # Check metadata list. All 6 items should be loaded regardless of user input
    ########################################################################
    
    expected = ['S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw1-slc-vh-20200929t214703-20200929t214728-034579-04068c-001.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw1-slc-vv-20200929t214703-20200929t214728-034579-04068c-004.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw2-slc-vh-20200929t214701-20200929t214726-034579-04068c-002.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw2-slc-vv-20200929t214701-20200929t214726-034579-04068c-005.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw3-slc-vh-20200929t214702-20200929t214727-034579-04068c-003.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw3-slc-vv-20200929t214702-20200929t214727-034579-04068c-006.xml']
    
    actual = s1.metadata_file_list
    assert expected == actual, 'Metadata list does not match'
    
    ########################################################################
    # Check shapefile data was generated
    ########################################################################
    
    out_shp_items = [
        os.path.join(TEST_DIR, 'swaths_all_vv.cpg'),
        os.path.join(TEST_DIR, 'swaths_all_vv.dbf'),
        os.path.join(TEST_DIR, 'swaths_all_vv.prj'),
        os.path.join(TEST_DIR, 'swaths_all_vv.shp'),
        os.path.join(TEST_DIR, 'swaths_all_vv.shx')
    ]
    s1.to_shapefile(out_shp_items[3])
    for item in out_shp_items:
        expected = True
        actual = os.path.exists(item)
        assert actual == expected, f'Shapefile was not generated correctly. Missing: {item}'
    
    ########################################################################
    # Check JSON was generated correctly
    ########################################################################
        
    json_out = os.path.join(TEST_DIR, 'test_json.json')
    s1.to_json(json_out)
    
    # Read output JSON file
    with open(json_out) as json_file:
        data = json.load(json_file)        
    assert isinstance(data, dict) == True, 'Error when loading JSON as Python dictionary'
    
    # Test contents
    expected = 'FeatureCollection'
    actual = data['type']
    assert expected == actual, f'JSON data for "type" does not match'
    
    # Test id 0
    expected = {'burst': 1, 'subswath': 'IW1'}
    actual = data['features'][0]['properties']
    assert expected == actual, f'JSON features with ID 0 do not match. Actual is {actual}. Expected is {expected}'
    # Test id 23
    expected = {'burst': 6, 'subswath': 'IW3'}
    actual = data['features'][23]['properties']
    assert expected == actual, f'JSON features with ID 23 do not match. Actual is {actual}. Expected is {expected}'
    
    ########################################################################
    # Check CSV was generated correctly
    ########################################################################
        
    csv_out = os.path.join(TEST_DIR, 'test_csv.csv')
    s1.to_csv(csv_out)
    
    df = pd.read_csv(csv_out)
    
    # Test CSV size
    expected = 27
    actual = len(df)
    assert expected == actual, f'CSV file does not match. Actual is {actual} rows. Expected {expected} rows'
    
    # Check id 0
    expected = 'IW1'
    actual = df.iloc[0]['subswath']
    assert expected == actual, f'Subswath for row 0 does not match. Actual is {actual}. Expected is {expected}'
    
    expected = 1
    actual = df.iloc[0]['burst']
    assert expected == actual, f'Burst for row 0 does not match. Actual is {actual}. Expected is {expected}'
        
    # Delete files after tests
    for item in out_shp_items:
        os.remove(item)
    os.remove(json_out)
    os.remove(csv_out)

# Using data2 folder
def test_TopsSplitAnalyzer_data2_all_vh():
    
    s1 = TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vh')
    s1.load_data(zip_path=data2)
    
    ########################################################################
    # Check metadata list. All 6 items should be loaded regardless of user input
    ########################################################################
    
    expected = ['S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw1-slc-vh-20200929t214703-20200929t214728-034579-04068c-001.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw1-slc-vv-20200929t214703-20200929t214728-034579-04068c-004.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw2-slc-vh-20200929t214701-20200929t214726-034579-04068c-002.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw2-slc-vv-20200929t214701-20200929t214726-034579-04068c-005.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw3-slc-vh-20200929t214702-20200929t214727-034579-04068c-003.xml',
                'S1A_IW_SLC__1SDV_20200929T214701_20200929T214728_034579_04068C_4E7A.SAFE/annotation/s1a-iw3-slc-vv-20200929t214702-20200929t214727-034579-04068c-006.xml']
    
    actual = s1.metadata_file_list
    assert expected == actual, 'Metadata list does not match'
    
    ########################################################################
    # Check shapefile data was generated
    ########################################################################
    
    out_shp_items = [
        os.path.join(TEST_DIR, 'swaths_all_vh.cpg'),
        os.path.join(TEST_DIR, 'swaths_all_vh.dbf'),
        os.path.join(TEST_DIR, 'swaths_all_vh.prj'),
        os.path.join(TEST_DIR, 'swaths_all_vh.shp'),
        os.path.join(TEST_DIR, 'swaths_all_vh.shx')
    ]
    s1.to_shapefile(out_shp_items[3])
    for item in out_shp_items:
        expected = True
        actual = os.path.exists(item)
        assert actual == expected, f'Shapefile was not generated correctly. Missing: {item}'
    
    ########################################################################
    # Check JSON was generated correctly
    ########################################################################
        
    json_out = os.path.join(TEST_DIR, 'test_json.json')
    s1.to_json(json_out)
    
    # Read output JSON file
    with open(json_out) as json_file:
        data = json.load(json_file)        
    assert isinstance(data, dict) == True, 'Error when loading JSON as Python dictionary'
    
    # Test contents
    expected = 'FeatureCollection'
    actual = data['type']
    assert expected == actual, f'JSON data for "type" does not match'
    
    # Test id 0
    expected = {'burst': 1, 'subswath': 'IW1'}
    actual = data['features'][0]['properties']
    assert expected == actual, f'JSON features with ID 0 do not match. Actual is {actual}. Expected is {expected}'
    # Test id 23
    expected = {'burst': 6, 'subswath': 'IW3'}
    actual = data['features'][23]['properties']
    assert expected == actual, f'JSON features with ID 23 do not match. Actual is {actual}. Expected is {expected}'
    
    ########################################################################
    # Check CSV was generated correctly
    ########################################################################
        
    csv_out = os.path.join(TEST_DIR, 'test_csv.csv')
    s1.to_csv(csv_out)
    
    df = pd.read_csv(csv_out)
    
    # Test CSV size
    expected = 27
    actual = len(df)
    assert expected == actual, f'CSV file does not match. Actual is {actual} rows. Expected {expected} rows'
    
    # Check id 0
    expected = 'IW1'
    actual = df.iloc[0]['subswath']
    assert expected == actual, f'Subswath for row 0 does not match. Actual is {actual}. Expected is {expected}'
    
    expected = 1
    actual = df.iloc[0]['burst']
    assert expected == actual, f'Burst for row 0 does not match. Actual is {actual}. Expected is {expected}'
        
    # Delete files after tests
    for item in out_shp_items:
        os.remove(item)
    os.remove(json_out)
    os.remove(csv_out)
