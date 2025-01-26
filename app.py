import geopandas as gpd
from shapely.errors import ShapelyError
import streamlit as st
import streamlit_folium

from stsa.stsa import TopsSplitAnalyzer
from stsa.utils import gdf_from_wkt

st.set_page_config(layout="wide")

st.title('S1-TOPS Split Analyzer (STSA)')

st.markdown("""
Simple web app implementation of STSA. If you have issues or suggestions please raise them in the
 [Github repo](https://github.com/pbrotoisworo/s1-tops-split-analyzer). This project is open-source and licensed under
 the [Apache-2.0 License](https://github.com/pbrotoisworo/s1-tops-split-analyzer/blob/main/LICENSE).

This web app extracts burst and subswath data from Sentinel-1 SLC data and visualizes on a webmap. The data itself can
be downloaded as GeoJSON format for viewing in GIS software. To be able to access the API please use your Copernicus
Dataspace account. If you don't have one you can make one [here](https://dataspace.copernicus.eu/).

This web app allows you to add one geometry overlay. You can specify the overlay using Well Known Text (WKT) or 
upload any geometry that is accepted by [Geopandas](https://geopandas.org/en/stable/docs/reference/api/geopandas.read_file.html).
""")

err_form = False

scene = st.text_input(
    label='Sentinel-1 SLC scene ID'
)
aoi_type = st.selectbox('AOI input type', ['File upload', 'Well Known Text (WKT)'])
if aoi_type == 'Well Known Text (WKT)':
    aoi = st.text_input(
        label='WKT of geometry overlay (optional)'
    )
    # Check WKT input before connecting to API
    if aoi:
        try:
            geom_overlay = gdf_from_wkt(aoi)
        except ShapelyError:
            st.error('Error: Failed to parse WKT string for geometry overlay.')
            st.stop()
    else:
        geom_overlay = None
else:
    aoi = st.file_uploader(
    label='AOI Geometry (optional)',
    help='Upload any geometry file that is accepted by Geopandas'
    )
    if aoi:
        try:
            geom_overlay = gpd.read_file(aoi)
            st.success(f"File '{aoi.name}' accepted")
        except:
            st.error('Error: Invalid AOI file')
            err_form = True
    else:
        geom_overlay = None

col1, col2, col3 = st.columns(3)
with col1:
    username = st.text_input(
        label='Copernicus Dataspace Username'
    )
with col2:
    password = st.text_input(
        label='Copernicus Dataspace Password',
        type='password'
    )
with col3:
    pass

load_button = st.button('Load SLC Scene')

if load_button:

    if err_form:
        st.error('Please fix errors before searching.')
        st.stop()

    st.markdown("""---""") 

    s1 = TopsSplitAnalyzer(streamlit_mode=True, verbose=False)
    with st.spinner('Connecting to API...'):
        s1.load_api(
            username=username,
            password=password,
            scene_id=scene,
            download_folder=''
        )
    if s1.api_product_is_online is False:
        st.error(f'Error: Scene is offline')
        st.stop()

    st.header('Search Results')

    if geom_overlay is not None:
        st.subheader('AOI Information')
        st.dataframe(geom_overlay['geometry'].astype(str))
        df_intersect = gpd.GeoDataFrame(
            s1.intersecting_bursts(geom_overlay), columns=['subswath', 'burst']
        )
        if len(df_intersect) > 0:
            st.text('Geometry overlay intersects with the following bursts:')
            st.dataframe(df_intersect)
        else:
            st.text('No overlap found with the geometry overlay.')

    st.subheader('Burst Data')
    download = st.empty()
    streamlit_folium.st_folium(s1.visualize_webmap(geom_overlay), width=1200, height=800)
    # streamlit_folium.folium_static(s1.visualize_webmap(geom_overlay), width=1200, height=800)

    filename = f'{scene}.geojson'
    download.download_button('Download GeoJSON', data=s1.df.to_json(), file_name=filename)
