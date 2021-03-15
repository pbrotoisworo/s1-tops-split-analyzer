import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from stsa import TopsSplitAnalyzer

def test_data1_all_subswaths_vv():
    
    data1 = r'tests\data1\S1A_IW_SLC__1SDV_20201123T142458_20201123T142525_035377_042241_C054.SAFE.zip'
    s1 = TopsSplitAnalyzer(image=data1, target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vv')
    
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
        r'tests\data1\swaths_all.cpg',
        r'tests\data1\swaths_all.dbf',
        r'tests\data1\swaths_all.prj',
        r'tests\data1\swaths_all.shp',
        r'tests\data1\swaths_all.shx'
    ]
    s1.to_shapefile(out_shp_items[3])
    for item in out_shp_items:
        expected = True
        actual = os.path.exists(item)
        assert actual == True, f'Shapefile was not generated correctly. Missing: {item}'
    
    ########################################################################
    # Check JSON was generated correctly
    ########################################################################
        
    json_out = r'tests\data1\test_json.json'
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
        
    csv_out = r'tests\data1\test_csv.csv'
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
