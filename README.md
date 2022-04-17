# S-1 TOPS SPLIT Analyzer (STSA)

[![Build Status](https://travis-ci.com/pbrotoisworo/s1-tops-split-analyzer.svg?branch=main)](https://travis-ci.com/pbrotoisworo/s1-tops-split-analyzer) 
[![codecov](https://codecov.io/gh/pbrotoisworo/s1-tops-split-analyzer/branch/main/graph/badge.svg?token=EYS8DNVPXL)](https://codecov.io/gh/pbrotoisworo/s1-tops-split-analyzer) 
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/pbrotoisworo/s1-tops-split-analyzer/main/app.py)

This code intends to help users easily work with the S-1 TOPS SPLIT function in [SNAP software](https://step.esa.int/main/download/snap-download/) by parsing the XML metadata of Sentinel-1 satellite data and converting it into usable data such as shapefiles or webmaps.

Using S-1 TOPS SPLIT Analyzer you are able to:
* Download XML data directly from [Copernicus Scihub](https://scihub.copernicus.eu/) and view TOPS-SPLIT data. No need to download the full 4 GB image to view the TOPS SPLIT data
* View TOPS-SPLIT data from downloaded ZIP files containing full size Sentinel-1 imagery
* View all subswaths at the same time
* Save S1-TOPS-SPLIT data as a shapefile, JSON, or CSV
* View and interact with S1-TOPS-SPLIT data using a webmap. In addition, you can add a polygon to visualize its extent with regards to the S1-TOPS-SPLIT data

Comments and feedback are welcome.

# Live Web App

For easier usage. STSA has a web app which is hosted by Streamlit. [Access it here!](https://share.streamlit.io/pbrotoisworo/s1-tops-split-analyzer/main/app.py) You can view data and download it in GeoJSON format.

# Installation

This has been tested to work in Python versions 3.8 to 3.9

**If you are using Windows you need to manually install the [GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and [Fiona](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona) wheels OR install Fiona using Anaconda**:

`conda install -c conda-forge fiona`

Linux or MacOS users can disregard the previous instruction. Install stsa into your environment by typing this command:

`pip install git+https://github.com/pbrotoisworo/s1-tops-split-analyzer.git`

# Usage
STSA can be used in the command line and as a Python import.

## Command Line
CLI access is available if you directly run `stsa.py`. The available flags are:

| Flag      | Description                 |
| --------  |:---------------------------:|
| -v        | Print all statements        |
| --zip     | Path of Sentinel-1 ZIP file |
| --safe    | Path of Sentinel-1 manifest.safe file |
| --swaths  | List of target subswaths    |
| --polar   | Polarization                |
| --shp     | Path of output shapefile    |
| --csv     | Path of output CSV file     |
| --json    | Path of output JSON file    |
| --api-user | Copernicus username |
| --api-password | Copernicus password (Leave empty for secure input) |
| --api-scene | Sentinel-1 scene ID to download |
| --api-folder | Folder for downloaded XML files |

Below is a sample command where user selects subswath IW2 and IW3, specifies VV polarization, and specifies output data.

```bash
python stsa.py --zip S1_image.zip --swaths iw2 iw3 --polar vv --shp out_shp.shp --csv out_csv.csv --json out_json.json
```

## Python Import

Below are code samples of using `TopsSplitAnalyzer`. When loading Sentinel-1 data please choose either API or ZIP 
method only. 

```python
############################################
# Load data using `load_api` or `load_zip`
############################################

import stsa

s1 = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'], polarization='vh')

# METHOD 1: Load using local ZIP file
s1.load_zip(zip_path='S1_image.zip')

# METHOD 2: Load using Copernicus Scihub API
s1.load_api(
    'myusername',
    'S1A_IW_SLC__1SDV_20210627T043102_20210627T043130_038521_048BB9_DA44',
    'mypassword'
)
```
```python
##################################################################
# Export the data in your preferred format.
# To visualize on a webmap you need to be using Jupyter Notebook.
##################################################################

# Write to shapefile
s1.to_shapefile('data.shp')

# Get JSON
s1.to_json('json_output.json')

# Write to CSV
s1.to_csv('output.csv')

# Visualize on a webmap with additional polygon
s1.visualize_webmap(polygon='mask.shp')
```

<p align="center">
  <img width="460" height="300" src="sample_webmap.png">
  <br>
  Output shown on a webmap
</p>

# Tests

If you plan on contributing ensure that is passes all tests by installing `pytest` and typing this in the project directory:

`pytest tests`
