from setuptools import setup, find_packages

setup(
    name='stsa',
    author='Panji P. Brotoisworo',
    url='https://github.com/pbrotoisworo/s1-tops-split-analyzer',
    version=0.1,
    description='Interface to extract subswath data from Sentinel-1 SAR metadata'
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'descartes',
        'fiona',
        'geopandas',
        'folium'
    ]
)