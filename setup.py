from setuptools import setup, find_packages

setup(
    name='stsa',
    author='Panji P. Brotoisworo',
    url='https://github.com/pbrotoisworo/s1-tops-split-analyzer',
    version=0.1,
    packages=[
        'tests',
        r'tests.data1',
        r'tests.data2'
    ],
    include_package_data=True,
    package_data={
        r'tests': ['*'],
        r'tests.data1': ['*'],
    },
    install_requires=[
        'descartes',
        'fiona',
        'geopandas',
        'folium'
    ]
)