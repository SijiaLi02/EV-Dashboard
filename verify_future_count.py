#!/usr/bin/env python3
"""
Verify the future site count after duplicate removal (dedup only, no status filter).
Prints: future rows before dedup, duplicates removed, future unique sites after dedup.

Usage:
  python verify_future_count.py
  DEDUP_THRESHOLD=0.0008 python verify_future_count.py   # try different threshold
"""

import os
import pandas as pd
import numpy as np

AFDC_CSV = "data/data/afdc_current.csv"
FUTURE_CSV = "data/data/ev_future_under_construction.csv"
DEFAULT_THRESHOLD = 0.001


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
        closest_idx = distances.idxmin()
        if min_distance < distance_threshold:
            duplicates.append({"future_idx": idx, "distance": float(min_distance)})
    return duplicates


def main():
    threshold = float(os.environ.get("DEDUP_THRESHOLD", DEFAULT_THRESHOLD))
    print("=" * 60)
    print("OUTCOME (dedup only – no Online Status / DCFC filter)")
    print("=" * 60)

    if not os.path.isfile(AFDC_CSV) or not os.path.isfile(FUTURE_CSV):
        print("Missing AFDC or Future CSV. Paths:", AFDC_CSV, FUTURE_CSV)
        return

    # Existing: load, IL, dedupe by ID, IL bounds, clean coords
    afdc = pd.read_csv(AFDC_CSV)
    afdc["lat"] = pd.to_numeric(afdc["Latitude"], errors="coerce")
    afdc["lon"] = pd.to_numeric(afdc["Longitude"], errors="coerce")
    if "State" in afdc.columns:
        afdc = afdc[afdc["State"].astype(str).str.upper().str.strip().isin(["IL", "ILLINOIS"])]
    if "ID" in afdc.columns:
        afdc = (
            afdc.groupby("ID", as_index=False)
            .agg(lat=("lat", "first"), lon=("lon", "first"))
        )
    afdc = afdc[afdc["lat"].between(36.8, 42.7) & afdc["lon"].between(-91.7, -87.0)]
    existing = clean_coords(afdc)

    # Future: load, IL bounds, clean coords
    fut = pd.read_csv(FUTURE_CSV)
    fut["lat"] = pd.to_numeric(fut["LatDD"], errors="coerce")
    fut["lon"] = pd.to_numeric(fut["LongDD"], errors="coerce")
    fut = fut[fut["lat"].between(36.8, 42.7) & fut["lon"].between(-91.7, -87.0)]
    future = clean_coords(fut)

    dupes = check_for_duplicates(existing, future, distance_threshold=threshold)
    future_drop_idx = [d["future_idx"] for d in dupes]
    future_clean = future.reset_index(drop=True).drop(index=future_drop_idx, errors="ignore")

    print("existing rows (coord-clean):", len(existing))
    print("future rows (coord-clean, before dedup):", len(future))
    print("duplicates removed (future near existing):", len(future_drop_idx))
    print("future final (unique rows after dedup):", len(future_clean))
    print()
    print("Future unique sites AFTER duplicate removal:", len(future_clean))
    print("(This is the number on the map and in the legend. Target ~409.)")


if __name__ == "__main__":
    main()
