#!/usr/bin/env python3
"""
EV Station Count Reconciliation Script
=====================================
Diagnoses why "existing stations" count (~1559 target) differs from raw row count (~4000).
Outputs: counts under multiple definitions, duplicate reports, and a diagnosis.
"""

import pandas as pd
import numpy as np
import os
import hashlib
import re

# ---- Configurable paths ----
DATASET_A_CSV = "data/data/ev_future_under_construction.csv"   # future/under construction (site list)
DATASET_B_CSV = "data/data/afdc_current.csv"                    # existing (AFDC - often connector-level)
OUTPUT_DIR = "data/reconciliation_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize_columns(df):
    """Standardize column names to snake_case; strip whitespace."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # snake_case
    def to_snake(s):
        s = re.sub(r"[^\w\s]", "", s)
        s = re.sub(r"\s+", "_", s).lower()
        return s
    rename = {c: to_snake(c) for c in df.columns}
    df = df.rename(columns=rename)
    return df


def infer_port_columns(df, which="B"):
    """Infer L2/L3 port column names; log what we use."""
    cols = list(df.columns)
    l2_candidates = [
        "ev_level2_evse_num", "ev level2 evse num", "level_2_ports", "level 2 ports",
        "level2_ports", "ev_level2_evse_num"
    ]
    l3_candidates = [
        "ev_dc_fast_count", "ev dc fast count", "ev_dc_fast_num", "level_3_ports",
        "level 3 ports", "level3_ports", "dcfc_ports"
    ]
    l2 = next((c for c in l2_candidates if c in cols), None)
    l3 = next((c for c in l3_candidates if c in cols), None)
    if which == "B":
        # AFDC uses exact names with spaces sometimes
        if not l2:
            for c in cols:
                if "level" in c.lower() and "2" in c and "port" in c.lower():
                    l2 = c
                    break
        if not l3:
            for c in cols:
                if "dc_fast" in c.lower() or ("level" in c.lower() and "3" in c):
                    l3 = c
                    break
    print(f"  Inferred L2 column: {l2}, L3 column: {l3}")
    return l2, l3


def numeric_ports(df, l2_col, l3_col):
    """Convert port columns to numeric; blanks -> 0."""
    if l2_col and l2_col in df.columns:
        df["level_2_ports"] = pd.to_numeric(df[l2_col], errors="coerce").fillna(0)
    else:
        df["level_2_ports"] = 0
    if l3_col and l3_col in df.columns:
        df["level_3_ports"] = pd.to_numeric(df[l3_col], errors="coerce").fillna(0)
    else:
        df["level_3_ports"] = 0
    df["ports_total"] = (df["level_2_ports"] + df["level_3_ports"]).clip(lower=0)
    return df


def add_site_and_geo_keys(df, name, lat_col, lon_col, id_col=None, global_id_col=None):
    """Add site_key and geo_key."""
    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lon = pd.to_numeric(df[lon_col], errors="coerce")
    df["_lat"] = lat
    df["_lon"] = lon
    df["geo_key"] = (
        lat.round(5).astype("string") + "_" + lon.round(5).astype("string")
    )

    if global_id_col and global_id_col in df.columns:
        df["site_key"] = df[global_id_col].astype(str).str.strip()
        df["site_key_source"] = "globalid"
    elif id_col and id_col in df.columns:
        df["site_key"] = df[id_col].astype(str).str.strip()
        df["site_key_source"] = "id"
    else:
        # hash(normalized_name + city + county + round(lat,5)+round(lon,5))
        name_col = next((c for c in df.columns if "name" in c.lower() or "host" in c.lower() or "station" in c.lower()), None)
        city_col = next((c for c in df.columns if c == "city"), None)
        county_col = next((c for c in df.columns if c == "county"), None)
        n = (df.get(name_col, "") if name_col else "").astype(str).str.strip().str.lower()
        ci = (df.get(city_col, "") if city_col else "").astype(str).str.strip().str.lower()
        co = (df.get(county_col, "") if county_col else "").astype(str).str.strip().str.lower()
        combo = n + "|" + ci + "|" + co + "|" + lat.round(5).astype("string") + "|" + lon.round(5).astype("string")
        df["site_key"] = combo.apply(lambda x: hashlib.md5(x.encode()).hexdigest())
        df["site_key_source"] = "hash"
    return df


def load_and_prep(path, which="B"):
    """Load CSV, normalize, infer ports, add keys."""
    if not os.path.exists(path):
        print(f"Missing: {path}")
        return None
    df = pd.read_csv(path)
    df = normalize_columns(df)
    # Get original column names for common variants
    if which == "B":
        lat_col = next((c for c in df.columns if "latitude" in c.lower() or c == "lat"), None)
        lon_col = next((c for c in df.columns if "longitude" in c.lower() or c == "lon" or "longdd" in c.lower()), None)
        id_col = next((c for c in df.columns if c == "id" or c == "station_id"), None)
        global_id_col = next((c for c in df.columns if "global" in c.lower() and "id" in c.lower()), None)
        l2_col, l3_col = None, None
        for c in df.columns:
            if "level2" in c.lower() or "level_2" in c.lower() or "ev level2" in c.lower():
                l2_col = c
            if "dc_fast" in c.lower() or "dc fast" in c.lower() or "level_3" in c.lower():
                l3_col = c
        if not l2_col:
            l2_col = "ev_level2_evse_num" if "ev_level2_evse_num" in df.columns else None
        if not l3_col:
            l3_col = "ev_dc_fast_count" if "ev_dc_fast_count" in df.columns else None
    else:
        lat_col = next((c for c in df.columns if "latdd" in c.lower() or "latitude" in c.lower()), None)
        lon_col = next((c for c in df.columns if "longdd" in c.lower() or "longitude" in c.lower()), None)
        id_col = next((c for c in df.columns if "objectid" in c.lower() or c == "id"), None)
        global_id_col = next((c for c in df.columns if "global" in c.lower() and "id" in c.lower()), None)
        l2_col = next((c for c in df.columns if "level" in c.lower() and "2" in c and "port" in c.lower()), None)
        l3_col = next((c for c in df.columns if "level" in c.lower() and "3" in c and "port" in c.lower()), None)

    print(f"Dataset {which}: lat={lat_col}, lon={lon_col}, id={id_col}, globalid={global_id_col}, l2={l2_col}, l3={l3_col}")
    df = numeric_ports(df, l2_col, l3_col)
    df = add_site_and_geo_keys(df, which, lat_col, lon_col, id_col=id_col, global_id_col=global_id_col)
    return df


def main():
    print("=" * 60)
    print("EV STATION RECONCILIATION")
    print("Target: existing stations ~1559 (sites), not ~4000 (rows/connectors)")
    print("=" * 60)

    # Load datasets (B = existing AFDC, A = future list)
    print("\n--- Loading Dataset B (existing / AFDC) ---")
    B = load_and_prep(DATASET_B_CSV, "B")
    if B is None:
        return

    print("\n--- Loading Dataset A (future / under construction) ---")
    A = load_and_prep(DATASET_A_CSV, "A")
    if A is None:
        return

    # Illinois filter for B
    if "state" in B.columns:
        B_all = B.copy()
        B = B[B["state"].astype(str).str.upper().str.strip().isin(["IL", "ILLINOIS"])].copy()
        non_il = len(B_all) - len(B)
        print(f"\nDataset B: Dropped {non_il} non-Illinois rows. IL rows: {len(B)}")
    else:
        B_all = B

    # ---- Counts matrix ----
    def counts_table(dff, label):
        row_count = len(dff)
        unique_sites = dff["site_key"].nunique()
        unique_geo = dff["geo_key"].nunique()
        ports_total = dff["ports_total"].sum()
        dc_ports = dff["level_3_ports"].sum()
        return {
            "dataset": label,
            "row_count": row_count,
            "unique_sites": unique_sites,
            "unique_geo": unique_geo,
            "ports_total": int(ports_total),
            "dc_ports": int(dc_ports),
        }

    counts_b = counts_table(B, "B_existing_AFDC")
    counts_a = counts_table(A, "A_future")

    counts_df = pd.DataFrame([counts_b, counts_a])
    out_path = os.path.join(OUTPUT_DIR, "counts_summary.csv")
    counts_df.to_csv(out_path, index=False)
    print("\n--- Counts summary ---")
    print(counts_df.to_string(index=False))
    print(f"\nSaved: {out_path}")

    # ---- Duplicate diagnostics ----
    dup_site_b = B.groupby("site_key").size()
    dup_site_b = dup_site_b[dup_site_b > 1].sort_values(ascending=False)
    dup_geo_b = B.groupby("geo_key").size()
    dup_geo_b = dup_geo_b[dup_geo_b > 1].sort_values(ascending=False)

    dup_site_a = A.groupby("site_key").size()
    dup_site_a = dup_site_a[dup_site_a > 1].sort_values(ascending=False)
    dup_geo_a = A.groupby("geo_key").size()
    dup_geo_a = dup_geo_a[dup_geo_a > 1].sort_values(ascending=False)

    duplicates_b = pd.DataFrame({
        "key_type": ["site_key"] * len(dup_site_b) + ["geo_key"] * len(dup_geo_b),
        "key_value": list(dup_site_b.index) + list(dup_geo_b.index),
        "count": list(dup_site_b.values) + list(dup_geo_b.values),
    })
    if len(duplicates_b) > 0:
        duplicates_b.to_csv(os.path.join(OUTPUT_DIR, "duplicates_b.csv"), index=False)
        print(f"\nDataset B: {len(dup_site_b)} site_keys with duplicates, {len(dup_geo_b)} geo_keys with duplicates")
        print("Sample duplicated site_key counts (B):")
        print(dup_site_b.head(10).to_string())

    duplicates_a = pd.DataFrame({
        "key_type": ["site_key"] * len(dup_site_a) + ["geo_key"] * len(dup_geo_a),
        "key_value": list(dup_site_a.index) + list(dup_geo_a.index),
        "count": list(dup_site_a.values) + list(dup_geo_a.values),
    })
    if len(duplicates_a) > 0:
        duplicates_a.to_csv(os.path.join(OUTPUT_DIR, "duplicates_a.csv"), index=False)

    # ---- Diagnosis ----
    print("\n" + "=" * 60)
    print("DIAGNOSIS: Why ~4000 vs target 1559?")
    print("=" * 60)
    reasons = []
    if counts_b["row_count"] > counts_b["unique_sites"]:
        reasons.append(
            f"B has one row per CONNECTOR/EVSE, not per SITE. "
            f"row_count={counts_b['row_count']}, unique_sites(site_key)={counts_b['unique_sites']}. "
            f"Use dedupe by site_key (or ID) to get ~1559."
        )
    if counts_b["unique_sites"] > 1559:
        reasons.append(
            f"After dedupe by site_key, unique_sites={counts_b['unique_sites']} still > 1559. "
            f"Check: status filter (e.g. online-only), or geography."
        )
    if counts_b["unique_sites"] <= 1600 and counts_b["unique_sites"] >= 1500:
        reasons.append(
            f"B unique_sites={counts_b['unique_sites']} is close to 1559. "
            f"The gap was row_count (connectors) vs sites. Dedupe by ID/site_key fixes it."
        )

    for r in reasons:
        print("\n*", r)

    print("\n--- Recommendation for dashboard ---")
    print("In render_11(), after loading AFDC:")
    print("  1. Filter to State == 'IL'")
    print("  2. Deduplicate by site (ID column): keep one row per ID")
    print("  3. Aggregate ports per site: for each ID take max(EV Level2 EVSE Num) + max(EV DC Fast Count)")
    print("  Then use that site-level dataframe for the map so count ≈ 1559.")

    return counts_df, B, A


if __name__ == "__main__":
    main()
