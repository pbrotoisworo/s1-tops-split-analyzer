import streamlit as st
from streamlit_folium import folium_static

from stsa.stsa import TopsSplitAnalyzer

st.set_page_config(layout="wide")

st.title('S1-TOPS Split Analyzer')

st.markdown("""
Simple web app implementation of the stsa [Github repo](https://github.com/pbrotoisworo/s1-tops-split-analyzer).

This web app extracts burst and subswath data from Sentinel-1 SAR data into usable data formats such as shapefiles, 
GeoJSON, and 
more.

To be able to access the API please use your Copernicus Scihub account. If you don't have one you can make one 
[here](https://scihub.copernicus.eu/) 
""")

with st.form(key='api'):
    scene = st.text_input(
        label='Sentinel-1 SLC scene ID'
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        username = st.text_input(
            label='Scihub Username'
        )
    with col2:
        password = st.text_input(
            label='Scihub Password',
            type='password'
        )
    with col3:
        pass
    load_button = st.form_submit_button(label='Load data')

if load_button:

    loading_text = st.empty()
    loading_text.write('Loading data...')

    s1 = TopsSplitAnalyzer()
    s1.load_api(
        username=username,
        password=password,
        scene_id=scene,
        download_folder=''
    )
    if s1.api_product_is_online is False:
        st.error(f'Error: Scene is offline')
    folium_static(s1.visualize_webmap(), width=1200, height=800)
    loading_text = st.empty()
