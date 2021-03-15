# S-1 TOPS SPLIT Analyzer (STSA)

[![Build Status](https://travis-ci.com/pbrotoisworo/s1-tops-split-analyzer.svg?branch=main)](https://travis-ci.com/pbrotoisworo/s1-tops-split-analyzer) [![codecov](https://codecov.io/gh/pbrotoisworo/s1-tops-split-analyzer/branch/main/graph/badge.svg?token=EYS8DNVPXL)](https://codecov.io/gh/pbrotoisworo/s1-tops-split-analyzer) [![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)


This code intends to help users easily work with the S-1 TOPS SPLIT function in [SNAP software](https://step.esa.int/main/download/snap-download/) by parsing the XML metadata of Sentinel-1 satellite data and converting it into usable data such as shapefiles or webmaps.

Using S-1 TOPS SPLIT Analyzer you are able to:
* View all subswaths at the same time
* Save S1-TOPS-SPLIT data as a shapefile, JSON, or CSV
* View and interact with S1-TOPS-SPLIT data using a webmap. In addition, you can add a polygon to visualize its extent with regards to the S1-TOPS-SPLIT data

Comments and feedback are welcome.

# Installation
This has been tested to work in Python versions 3.6 and above. Python dependencies are `descartes fiona folium geopandas`.

List of dependencies is available in `requirements.txt` which can be installed used to prepare the environment using this command:

`pip install -r requirements.txt`

# Usage
STSA can be used in the command line and as a Python import.

## Command Line
The available flags are:

| Flag     | Description                |
| -------- |:--------------------------:|
| -v       | Print all statements       |
| -zip     | Path of Sentinel-1 ZIP file|
| --swaths | List of target subswaths   |
| -polar   | Polarization               |
| -shp     | Path of output shapefile   |
| -csv     | Path of output CSV file    |
| -json    | Path of output JSON file   |

Below is a sample command where user selects subswath IW2 and IW3, specifies VV polarization, and specifies output data.

```bash
python stsa.py -zip S1_image.zip --swath iw2 iw3 -polar vv -shp out_shp.shp -csv out_csv.csv -json out_json.json
```

## Python Import

To use it as a module copy `stsa.py` to your work directory. Then import the Class by typing:

```python
from stsa import TopsSplitAnalyzer
```

Below is a sample of using `TopsSplitAnalyzer` to create a shapefile and visualize on a webmap. To visualize on a webmap you need to be using Jupyter Notebook.

```python
# Create object
s1 = TopsSplitAnalyzer(image='S1_image.zip', target_subswaths=['iw1, iw2, iw3'], polarization='vh')

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