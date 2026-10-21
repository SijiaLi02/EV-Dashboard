"""Verify tl_2020_17_tract.shp has expected columns (e.g. GEOID). Run once: python verify_shapefile.py"""
import geopandas as gpd

# Shapefile lives in ArcGIS visualizations/
shapefile_path = "ArcGIS visualizations/tl_2020_17_tract.shp"
gdf = gpd.read_file(shapefile_path)

print("Columns:", list(gdf.columns))
print("GEOID present:", "GEOID" in gdf.columns)

if "GEOID" in gdf.columns:
    print("OK: You are 100% good.")
else:
    print("WARNING: GEOID column not found.")
