import streamlit as st
import streamlit_folium

from stsa.stsa import TopsSplitAnalyzer

st.set_page_config(layout="wide")

st.title('S1-TOPS Split Analyzer (STSA)')

st.markdown("""
Simple web app implementation of STSA. If you have issues or suggestions please raise them in the
 [Github repo](https://github.com/pbrotoisworo/s1-tops-split-analyzer). This project is open-source and licensed under
 the [Apache-2.0 License](https://github.com/pbrotoisworo/s1-tops-split-analyzer/blob/main/LICENSE).

This web app extracts burst and subswath data from Sentinel-1 SLC data and visualizes on a webmap. The data itself can
be downloaded as GeoJSON format for viewing in GIS software. To be able to access the API please use your Copernicus
Scihub account. If you don't have one you can make one [here](https://scihub.copernicus.eu/) 
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

    download = st.empty()
    streamlit_folium.folium_static(s1.visualize_webmap(), width=1200, height=800)

    filename = f'{scene}.geojson'
    download.download_button('Download GeoJSON', data=s1.df.to_json(), file_name=filename)
