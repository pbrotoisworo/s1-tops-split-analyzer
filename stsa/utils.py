import geopandas as gpd

def gdf_from_wkt(wkt: str) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from a WKT string
    """
    gs = gpd.GeoSeries.from_wkt([wkt])
    df = gpd.GeoDataFrame(gs, columns=['geometry'], crs='EPSG:4326')
    return df
