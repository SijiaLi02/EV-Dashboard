#!/usr/bin/env python3
"""
Scan distance_threshold (dedup only, no status filter) to find value that gives ~409.

Usage: python scan_dedup_threshold.py
"""

import os
import pandas as pd
import numpy as np

AFDC_CSV = "data/data/afdc_current.csv"
FUTURE_CSV = "data/data/ev_future_under_construction.csv"


def clean_coords(gdf, lat_col="lat", lon_col="lon"):
    gdf = gdf.copy()
    gdf[lat_col] = pd.to_numeric(gdf[lat_col], errors="coerce")
    gdf[lon_col] = pd.to_numeric(gdf[lon_col], errors="coerce")
    return gdf.dropna(subset=[lat_col, lon_col])


def check_for_duplicates(existing_gdf, future_gdf, distance_threshold, lat_col="lat", lon_col="lon"):
    if future_gdf is None or len(future_gdf) == 0:
        return []
    existing_gdf = existing_gdf.reset_index(drop=True)
    future_gdf = future_gdf.reset_index(drop=True)
    duplicates = []
    for idx, future_station in future_gdf.iterrows():
        future_lat = future_station[lat_col]
        future_lon = future_station[lon_col]
        distances = np.sqrt(
            (existing_gdf[lat_col] - future_lat) ** 2 + (existing_gdf[lon_col] - future_lon) ** 2
        )
        min_distance = distances.min()
        if min_distance < distance_threshold:
            duplicates.append(idx)
    return duplicates


def main():
    if not os.path.isfile(AFDC_CSV) or not os.path.isfile(FUTURE_CSV):
        print("Missing CSV files.")
        return

    afdc = pd.read_csv(AFDC_CSV)
    afdc["lat"] = pd.to_numeric(afdc["Latitude"], errors="coerce")
    afdc["lon"] = pd.to_numeric(afdc["Longitude"], errors="coerce")
    if "State" in afdc.columns:
        afdc = afdc[afdc["State"].astype(str).str.upper().str.strip().isin(["IL", "ILLINOIS"])]
    if "ID" in afdc.columns:
        afdc = afdc.groupby("ID", as_index=False).agg(lat=("lat", "first"), lon=("lon", "first"))
    afdc = afdc[afdc["lat"].between(36.8, 42.7) & afdc["lon"].between(-91.7, -87.0)]
    existing = clean_coords(afdc)

    fut = pd.read_csv(FUTURE_CSV)
    fut["lat"] = pd.to_numeric(fut["LatDD"], errors="coerce")
    fut["lon"] = pd.to_numeric(fut["LongDD"], errors="coerce")
    fut = fut[fut["lat"].between(36.8, 42.7) & fut["lon"].between(-91.7, -87.0)]
    future = clean_coords(fut)

    print("Scanning distance_threshold (deg) -> future final count (target ~409):\n")
    for th in [0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.0012, 0.0015]:
        drop_idx = check_for_duplicates(existing, future, distance_threshold=th)
        final = len(future) - len(drop_idx)
        mark = "  <-- closest to 409" if 400 <= final <= 420 else ""
        print(f"  {th:.4f}  ->  {final}{mark}")


if __name__ == "__main__":
    main()
