from setuptools import setup, find_packages

setup(
    name='stsa',
    author='Panji P. Brotoisworo',
    url='https://github.com/pbrotoisworo/s1-tops-split-analyzer',
    version=0.2,
    description='Interface to extract subswath data from Sentinel-1 SAR metadata',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'descartes',
        'fiona',
        'geopandas',
        'folium',
        'xmltodict',
        'pytest'
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="SAR, Sentinel-1, Remote Sensing",
)