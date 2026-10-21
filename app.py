"""
Illinois EV Charging Infrastructure Dashboard
=============================================
A web-based interactive dashboard for analyzing EV charging accessibility,
VMT coverage, and willingness to pay for DCFC infrastructure.

Sections:
- 1.1 Income Analysis (Static maps)
- 1.2 Gap and Accessibility Analysis (Static maps + Formula)
- 1.3 Electrified Miles Estimation
- 1.4 Willingness to Pay Analysis (Interactive with parameter controls)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import os
import base64

# Optional: for Map 1 (Accessibility A) choropleth
try:
    import pandas as pd
    import geopandas as gpd
    _HAS_GEOPANDAS = True
except ImportError:
    _HAS_GEOPANDAS = False

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Economic Environmental and Equity Outcomes Assessment of the Electric Vehicle Charging Network Expansion in Illinois Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS FOR ACADEMIC STYLING
# =============================================================================
st.markdown("""
    <style>
    :root{
    --illini-blue:#122a4b;
    --illini-orange:#d83404;
    }

    /* global font only */
    html, body, [class*="css"]  {
    font-family: Arial, Helvetica, sans-serif !important;
    }

    /* Your custom headers */
    .main-header{
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--illini-blue) !important;
    text-align: center !important;
    padding: 0.7rem 0 !important;
    border-bottom: 2px solid var(--illini-blue) !important;
    margin-bottom: 1.2rem !important;
    }
    .section-header{
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: var(--illini-blue) !important;
    margin: 1rem 0 0.6rem 0 !important;
    }
    .subsection-header{
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    color: var(--illini-orange) !important;
    margin: 0.7rem 0 0.4rem 0 !important;
    }

    /* Streamlit markdown headings (THIS is what changes your ### / ## etc) */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2{
    color: var(--illini-blue) !important;
    }
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4{
    color: var(--illini-orange) !important;
    }

    /* Center all images */
    div[data-testid="stImage"],
    div[data-testid="stImage"] > img,
    div[data-testid="stImage"] > div {
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
    }
    /* Center plotly charts */
    div[data-testid="stPlotlyChart"] {
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
    }
    /* Sidebar container */
    section[data-testid="stSidebar"] {
        background-color: #f7f9fc;
        padding: 0.9rem 0.85rem; /* smaller */
    }

    /* Sidebar title */
    section[data-testid="stSidebar"] h2 {
        color: var(--illini-blue);
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    /* Sidebar divider */
    .sidebar-divider {
        border-top: 1px solid #d0d7e2;
        margin: 0.75rem 0;
    }

    /* About card */
    .about-box{
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-left: 4px solid var(--illini-blue);
        border-radius: 10px;
        padding: 0.85rem 0.9rem;
        margin-top: 0.75rem;
        font-size: 0.86rem;
        line-height: 1.45;
        color: #1f2937;
    }

    .about-box ul{
        margin: 0.4rem 0 0.5rem 1.1rem;
    }
    .about-box li{
        margin: 0.25rem 0;
    }
    .about-box p{
        margin: 0.35rem 0;
    }
    
    .uiuc-orange-bar {
        background: var(--illini-orange);
        height: 3px;
        width: 100%;
        margin: 0;
        padding: 0;
    }

    
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# UIUC & IDOT BRAND HEADER (MATCHED HEIGHT)
# =============================================================================
st.markdown('<div class="uiuc-orange-bar"></div>', unsafe_allow_html=True)

# Helper function to encode image to base64
def get_image_base64(image_path):
    """Safely encode image to base64, handling None values or missing files"""
    if image_path and os.path.exists(image_path):  # Added 'image_path and' to fix TypeError
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# We use two main columns: one for all logos, one for the text
col_logos, col_text = st.columns([0.45, 0.55])

with col_logos:
    # Find the logo files
    block_i_path = "figures/Image_20260112141204_1012_2.png"
    idot_logo_paths = [
        "figures/idot_logo.png", "figures/IDOT_logo.png", 
        "figures/idot.png", "figures/IDOT.png", 
        "figures/ict_logo.png"
    ]
    idot_path = next((p for p in idot_logo_paths if os.path.exists(p)), None)
    
    # Encode images to base64
    block_i_base64 = get_image_base64(block_i_path) if os.path.exists(block_i_path) else None
    idot_base64 = get_image_base64(idot_path) if idot_path else None
    
    # Build the flex container with logos
    logos_html = '<div style="display: flex; align-items: center; gap: 25px; height: 90px;">'
    
    # Block I logo
    if block_i_base64:
        logos_html += f'<img src="data:image/png;base64,{block_i_base64}" style="height: 80px; width: auto; object-fit: contain;">'
    else:
        logos_html += '<div style="width: 80px; height: 80px; background: var(--illini-orange); border: 2px solid var(--illini-blue); border-radius: 4px;"></div>'
    
    # IDOT logo
    if idot_base64:
        logos_html += f'<img src="data:image/png;base64,{idot_base64}" style="height: 65px; width: auto; object-fit: contain; opacity: 0.9;">'
    
    logos_html += '</div>'
    
    st.markdown(logos_html, unsafe_allow_html=True)

with col_text:
    st.markdown("""
    <div style="border-left: 1px solid #ddd; padding-left: 1.5rem; margin-top: 0.8rem; height: 80px; display: flex; flex-direction: column; justify-content: center;">
        <div style="font-size: 0.8rem; font-weight: 600; color: #122a4b; letter-spacing: 0.05em; text-transform: uppercase; line-height: 1.2;">
            University of Illinois Urbana-Champaign
        </div>
        <div style="font-size: 0.75rem; color: #122a4b; margin-top: 0.2rem;">
            The Grainger College of Engineering
        </div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #d83404; margin-top: 0.3rem; line-height: 1.1;">
            Civil & Environmental Engineering
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 1.5rem; border-bottom: 1px solid #e5e7eb;'></div>", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.markdown("## Dashboard Navigation")
st.sidebar.markdown(
    """
    <ul style="list-style:none; padding-left:0; font-size:0.95rem;">
      <li><a href="#overview">Overview</a></li>
      <li><a href="#section-11">1.1 Data integration</a></li>
      <li><a href="#section-12">1.2 Gap & accessibility</a></li>
      <li><a href="#section-13">1.3 Electrified miles</a></li>
      <li><a href="#section-14">1.4 Willingness to pay</a></li>
    </ul>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)




# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Standard column ratio for consistent centering across all sections
CENTER_COL_RATIO = (0.8, 4.0, 0.8)

# Map palette (1.1 Figure 1 and 1.2 Figure 4)
C_FUTURE_ORANGE = "#fea07a"   # 1.1 Future/New
C_EXISTING_BLUE = "#6796ec"   # 1.1 Existing
C_DCFAST = "#6887e8"          # 1.2 Figure 4: DC Fast points
C_LEVEL2 = "#83aaf1"          # 1.2 Figure 4: Level 2 points
PINK = "#d89292"              # roads (interstates) on maps

# ----- Paper exact colors (Accessibility A and log-ratio maps) -----
C_SPILL_STRONG = "#2c7cb6"   # Strong Spillover (-1.00 to -0.69)
C_SPILL_MOD    = "#5ca3d0"   # Moderate Spillover (-0.69 to -0.38)
C_SPILL_MILD   = "#8fccea"   # Mild Spillover (-0.38 to -0.00)
C_UNDER_MILD   = "#f1a8a8"   # Mild Undersupply (0.00 to 0.34)
C_UNDER_MOD    = "#e28b8b"   # Moderate Undersupply (0.34 to 0.73)
C_UNDER_SEV    = "#d16e6e"   # Severe Undersupply (0.73 to 1.00)
C_MISSING      = "#9e9e9e"   # Missing Data
C_INTERSTATE   = "#7c8788"   # Interstate Routes (line in legend)

def in_center_container(fn):
    """Execute a function inside a consistently centered container"""
    left, mid, right = st.columns(CENTER_COL_RATIO)
    with mid:
        fn()

def load_image_placeholder(width=600, height=400, text="Image Placeholder"):
    """Create a placeholder image when actual image is not available"""
    fig = go.Figure()
    fig.add_annotation(
        x=0.5, y=0.5,
        text=text,
        font=dict(size=20, color="gray"),
        showarrow=False,
        xref="paper", yref="paper"
    )
    fig.update_layout(
        width=width, height=height,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='#f0f0f0'
    )
    return fig

# =============================================================================
# WTP MODEL FUNCTIONS
# =============================================================================

UIUC_BLUE = "#122a4b"
UIUC_ORANGE = "#d83404"

a_stations = 93.222
b_stations = 0.75
M_j = 4.310773e9

w = 20.0
theta = 0.8
e = 0.32
d = 150
K_base = 0.1536
a_access_base = 1.0
N_gas_base = 3670

N0 = 1

def coverage_fraction(N):
    N = np.asarray(N, dtype=float)
    return (a_stations + b_stations * np.log(N)) / 100.0

f0 = float(coverage_fraction(N0))

def calculate_discount_factor(r, T=15):
    return (1 - (1/(1+r))**T) / r

def calculate_cost(N, R=250, K=K_base, a=a_access_base, N_gas=N_gas_base):
    N = np.asarray(N, dtype=float)
    phi = N / N_gas
    access_cost = K * (phi**a - 1)
    charging_time = (theta * R * e) / d
    cost_per_mile = (w / (theta * R)) * (access_cost + charging_time)
    return cost_per_mile

def net_value_per_mile(N, v, R=250, K=K_base, a=a_access_base, N_gas=N_gas_base):
    return v - calculate_cost(N, R, K, a, N_gas)

def calculate_WTP(N, v, r, R=250, K=K_base, a=a_access_base, N_gas=N_gas_base, T=15):
    N = np.asarray(N, dtype=float)
    delta_f = coverage_fraction(N) - f0
    D_j = calculate_discount_factor(r, T)
    net_value = net_value_per_mile(N, v, R, K, a, N_gas)
    WTP = delta_f * M_j * net_value * D_j
    return np.maximum(WTP, 0.0)

def calculate_marginal_WTP(N, v, r, R=250, K=K_base, a=a_access_base, N_gas=N_gas_base, T=15):
    N = np.asarray(N, dtype=float)
    D_j = calculate_discount_factor(r, T)
    cost = calculate_cost(N, R, K, a, N_gas)
    net_value = v - cost

    phi = N / N_gas
    dC_dN = (w / (theta * R)) * K * a * (phi**(a-1)) / N_gas

    log_ratio = np.log(N / N0)
    term1 = (b_stations / N) * net_value
    term2 = b_stations * log_ratio * (-dC_dN)

    marginal_WTP = M_j * D_j * (term1 + term2)
    return marginal_WTP

def centered_image_fixed(path, width, placeholder_text, ph_h=375):
    """Display an image in a consistently centered container"""
    def _render():
        if os.path.exists(path):
            st.image(path, width=width)
        else:
            st.plotly_chart(
                load_image_placeholder(width, ph_h, placeholder_text),
                width="content"
            )
    in_center_container(_render)

def centered_plotly_fixed(fig):
    """Display a Plotly chart in a consistently centered container"""
    def _render():
        st.plotly_chart(fig, width="stretch")
    in_center_container(_render)

def centered_formula_row(label, latex):
    """Display a formula row (label + equation) in a consistently centered container"""
    def _render():
        c1, c2 = st.columns([1.2, 3.8])
        with c1:
            st.markdown(f"**{label}**")
        with c2:
            st.latex(latex)
    in_center_container(_render)

def centered_block(title, path, width, caption=None, placeholder_text="", ph_h=375, col_ratio=(0.8, 4, 0.8)):
    left, mid, right = st.columns(col_ratio)
    with mid:
        st.markdown(f"<h4 style='text-align:center; margin-bottom: 0.4rem;'>{title}</h4>", unsafe_allow_html=True)

        if os.path.exists(path):
            st.image(path, width=width)
        else:
            st.plotly_chart(
                load_image_placeholder(width, ph_h, placeholder_text),
                width="content"
            )

        if caption:
            st.markdown(
                f"<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>{caption}</div>",
                unsafe_allow_html=True
            )

def render_overview():
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">Economic, Environmental, and Equity Outcomes Assessment of the EV Charging Network Expansion in IL</div>', 
                unsafe_allow_html=True)
    st.markdown("""
<div style="max-width: 860px; margin: 0 auto; font-size: 1.02rem; line-height: 1.65;">
This dashboard summarizes interim findings from <b>R27-280</b> on the economic, environmental, and equity
outcomes of expanding Illinois&apos; EV charging network.

<p style="margin: 0.6rem 0 0.2rem 0;"><b>1.1.</b> Data integration: charging, demographic, and spatial inputs</p>
<p style="margin: 0.2rem 0;"><b>1.2.</b> Accessibility gaps: tract-level inaccessibility with spillover capacity</p>
<p style="margin: 0.2rem 0;"><b>1.3.</b> Electrified VMT: additional electrified miles enabled by DCFC expansion</p>
<p style="margin: 0.2rem 0 0.6rem 0;"><b>1.4.</b> Willingness to pay: access improvements translated into consumer benefits</p>
</div>
""", unsafe_allow_html=True)


# ---- Section 1.1: Cross-dedup + Figure 2 (AFDC Future/New by charging level) ----
def _pick_col(df, candidates):
    """First column name that exists in df (for AFDC column name variants)."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _clean_coords_11(gdf, lat_col="lat", lon_col="lon"):
    """Drop rows with missing or invalid lat/lon."""
    gdf = gdf.copy()
    gdf[lat_col] = pd.to_numeric(gdf[lat_col], errors="coerce")
    gdf[lon_col] = pd.to_numeric(gdf[lon_col], errors="coerce")
    return gdf.dropna(subset=[lat_col, lon_col])


def _check_for_duplicates_11(existing_gdf, future_gdf, distance_threshold=0.001, lat_col="lat", lon_col="lon"):
    """
    Find future stations within distance_threshold (degrees) of an existing station.
    Returns list of dicts with future_idx, existing_idx, distance, etc.
    """
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
            duplicates.append({
                "future_idx": idx,
                "existing_idx": int(closest_idx),
                "distance": float(min_distance),
                "future_city": future_station.get("City", "Unknown"),
                "existing_city": existing_gdf.loc[closest_idx].get("City", "Unknown"),
                "future_coords": (float(future_lat), float(future_lon)),
                "existing_coords": (
                    float(existing_gdf.loc[closest_idx, lat_col]),
                    float(existing_gdf.loc[closest_idx, lon_col]),
                ),
            })
    return duplicates


def _remove_future_duplicates_against_existing_11(existing_df, future_df, distance_threshold=0.001):
    """
    Dedup only: clean coords → drop future points within distance_threshold of existing.
    Returns (future_clean, dupes_df, outcome_dict). No Online Status or DCFC filter.
    """
    existing = _clean_coords_11(existing_df.copy())
    future = _clean_coords_11(future_df.copy())
    dupes = _check_for_duplicates_11(existing, future, distance_threshold=distance_threshold)
    future_drop_idx = [d["future_idx"] for d in dupes]
    future_clean = future.reset_index(drop=True).drop(index=future_drop_idx, errors="ignore")
    dupes_df = pd.DataFrame(dupes).sort_values("distance") if dupes else pd.DataFrame()
    outcome = {
        "existing_rows": len(existing),
        "future_rows": len(future),
        "duplicates_removed": len(future_drop_idx),
        "future_final": len(future_clean),
    }
    return future_clean, dupes_df, outcome


def _future_by_charging_level_from_afdc_11(afdc_raw, state="IL", coord_round=5):
    """
    Figure 2: Future/New from AFDC (Status Code = 'P' or != 'E'), dedupe by site, split DC Fast vs Level 2.
    Paper target: Future DC Fast = 351, Future Level 2 = 52 (total 403).
    Returns (df_dc, df_l2, n_dc, n_l2, debug_info) with columns lat, lon for plotting.
    """
    df = afdc_raw.copy()
    # Strip column names for matching (AFDC exports sometimes have leading/trailing space)
    df.columns = df.columns.str.strip()
    lat_col = _pick_col(df, ["Latitude", "latitude", "LATITUDE"])
    lon_col = _pick_col(df, ["Longitude", "longitude", "LONGITUDE"])
    state_col = _pick_col(df, ["State", "state", "STATE"])
    status_col = _pick_col(df, ["Status Code", "Status", "status_code", "STATUS_CODE"])
    # Extended L2/DC column candidates (cover common AFDC export variants)
    l2_col = _pick_col(df, [
        "EV Level2 EVSE Num", "EV Level2 EVSE Count", "EV Level 2 EVSE Num",
        "EV Level2 Num", "EV Level2 Ports", "EV Level 2 Ports",
        "EVSE Level2", "ev_level2_evse_num", "Level2", "L2", "L2 Ports",
    ])
    if not l2_col:
        for c in df.columns:
            if "level" in c.lower() and "2" in c and ("evse" in c.lower() or "num" in c.lower() or "port" in c.lower()):
                l2_col = c
                break
    dc_col = _pick_col(df, [
        "EV DC Fast Count", "EV DC Fast EVSE Num", "EV DC Fast EVSE Count",
        "EV DC Fast Num", "EV DC Fast Ports", "EVSE DC Fast",
        "ev_dc_fast_count", "ev_dc_fast_num", "DC Fast", "DC", "DCFC",
        "Level3", "L3", "L3 Ports",
    ])
    if not dc_col:
        for c in df.columns:
            if ("dc" in c.lower() or "fast" in c.lower()) and ("count" in c.lower() or "num" in c.lower() or "evse" in c.lower() or "port" in c.lower()):
                dc_col = c
                break
    if not lat_col or not lon_col or not state_col or not status_col:
        return None, None, 0, 0, {"error": "Missing required columns (lat/lon/state/status)"}
    if not l2_col:
        df["_l2"] = 0
        l2_col = "_l2"
    if not dc_col:
        df["_dc"] = 0
        dc_col = "_dc"

    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    df = df[df[lat_col].between(36.8, 42.7) & df[lon_col].between(-91.7, -87.0)]

    status_upper = df[status_col].astype(str).str.strip().str.upper()
    il_mask = (df[state_col].astype(str).str.strip().str.upper() == state)
    # Paper-style Future/New: everything not Existing/Open (exclude E and blank/nan)
    df_future = df[
        il_mask
        & (status_upper != "E")
        & (status_upper != "")
        & (status_upper != "NAN")
    ].copy()
    status_filter_used = "!= 'E' (paper-style Future/New)"

    df_future["_l2_num"] = pd.to_numeric(df_future[l2_col], errors="coerce").fillna(0)
    df_future["_dc_num"] = pd.to_numeric(df_future[dc_col], errors="coerce").fillna(0)

    # Status breakdown for IL rows (to tune whitelist if total ≠ 403)
    debug_info = {
        "total_rows": len(df),
        "il_rows": int(il_mask.sum()),
        "status_filter_used": status_filter_used,
        "future_rows_after_filter": len(df_future),
        "future_status_counts": status_upper[il_mask].value_counts().to_dict(),
        "l2_col": l2_col,
        "dc_col": dc_col,
        "l2_nonzero": int((df_future["_l2_num"] > 0).sum()),
        "dc_nonzero": int((df_future["_dc_num"] > 0).sum()),
    }

    # Dedupe by site: round coords; aggregate max L2/DC per site
    df_future["lat_r"] = df_future[lat_col].round(coord_round)
    df_future["lon_r"] = df_future[lon_col].round(coord_round)
    df_future = (
        df_future.groupby(["lat_r", "lon_r"], as_index=False)
        .agg({lat_col: "first", lon_col: "first", "_l2_num": "max", "_dc_num": "max"})
    )
    df_future["lat"] = df_future[lat_col]
    df_future["lon"] = df_future[lon_col]

    # Paper: combined Future/New = 403. Of these, 52 = Future Level 2 (L2 only). So Future DC Fast = 403 - 52 = 351.
    # Future Level 2 = no DC, has L2. Future DC Fast = has ≥1 DC port (the rest of the 403).
    df_l2 = df_future[(df_future["_dc_num"] <= 0) & (df_future["_l2_num"] > 0)].copy()
    df_dc = df_future[df_future["_dc_num"] > 0].copy()
    n_l2 = len(df_l2)
    n_dc = len(df_dc)
    debug_info["future_dc_sites"] = n_dc
    debug_info["future_l2_sites"] = n_l2
    debug_info["future_total_sites"] = n_dc + n_l2
    return df_dc, df_l2, n_dc, n_l2, debug_info


def _future_by_charging_level_from_future_csv_11(future_csv_path, coord_round=5):
    """
    Fallback for Figure 2 when AFDC has no future rows: use NEVI future CSV (Level 2 Ports, Level 3 Ports).
    Returns (df_dc, df_l2, n_dc, n_l2) with lat, lon for plotting.
    """
    if not os.path.exists(future_csv_path):
        return None, None, 0, 0
    df = pd.read_csv(future_csv_path)
    df.columns = df.columns.str.strip()
    lat_col = _pick_col(df, ["LatDD", "Latitude", "latitude"])
    lon_col = _pick_col(df, ["LongDD", "Longitude", "longitude"])
    l2_col = _pick_col(df, ["Level 2 Ports", "Level2 Ports", "EV Level2 EVSE Num"])
    dc_col = _pick_col(df, ["Level 3 Ports", "Level3 Ports", "EV DC Fast Count"])
    if not lat_col or not lon_col:
        return None, None, 0, 0
    if not l2_col:
        df["_l2"] = 0
        l2_col = "_l2"
    if not dc_col:
        df["_dc"] = 0
        dc_col = "_dc"
    df["lat"] = pd.to_numeric(df[lat_col], errors="coerce")
    df["lon"] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    df = df[df["lat"].between(36.8, 42.7) & df["lon"].between(-91.7, -87.0)]
    df["_l2_num"] = pd.to_numeric(df[l2_col], errors="coerce").fillna(0)
    df["_dc_num"] = pd.to_numeric(df[dc_col], errors="coerce").fillna(0)
    df["lat_r"] = df["lat"].round(coord_round)
    df["lon_r"] = df["lon"].round(coord_round)
    df = df.groupby(["lat_r", "lon_r"], as_index=False).agg(
        {"lat": "first", "lon": "first", "_l2_num": "max", "_dc_num": "max"}
    )
    # Combined Future/New = 403; 52 = Level 2 only → Future DC Fast = 351 (sites with ≥1 DC port).
    df_l2 = df[(df["_dc_num"] <= 0) & (df["_l2_num"] > 0)].copy()
    df_dc = df[df["_dc_num"] > 0].copy()
    return df_dc, df_l2, len(df_dc), len(df_l2)


# ---- 1.1 Plotly maps: loaders and hover (info-card style) ----
def compute_station_type_11(l2_ports, dcfc_ports):
    """Return station_type: Mixed (L2 + DCFC), DCFC, Level 2 (L2), or Unknown."""
    l2 = float(l2_ports or 0)
    dc = float(dcfc_ports or 0)
    if dc > 0 and l2 > 0:
        return "Mixed (L2 + DCFC)"
    if dc > 0:
        return "DCFC"
    if l2 > 0:
        return "Level 2 (L2)"
    return "Unknown"


def load_existing_afdc(csv_path="data/data/afdc_current.csv"):
    """
    Load AFDC current as Existing: filter IL, standardize to lat, lon, l2_ports, dcfc_ports,
    ports_total, station_type, status_group. Dedupe by ID; keep hover fields (station_name, address, etc.).
    """
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    lat_c = _pick_col(df, ["Latitude", "latitude"])
    lon_c = _pick_col(df, ["Longitude", "longitude"])
    state_c = _pick_col(df, ["State", "state"])
    l2_c = _pick_col(df, ["EV Level2 EVSE Num", "EV Level2 EVSE Count", "EV Level 2 EVSE Num", "Level 2 Ports"])
    dc_c = _pick_col(df, ["EV DC Fast Count", "EV DC Fast Num", "Level 3 Ports"])
    id_c = _pick_col(df, ["ID", "id", "Id"])
    name_c = _pick_col(df, ["Station Name", "Station Name", "Site Host"])
    addr_c = _pick_col(df, ["Street Address", "Street Address"])
    city_c = _pick_col(df, ["City", "city"])
    state_col = _pick_col(df, ["State", "state"])
    zip_c = _pick_col(df, ["ZIP", "Zip", "ZIP Code"])
    status_c = _pick_col(df, ["Status Code", "Status", "Online Status"])
    access_c = _pick_col(df, ["Access Days Time", "Access Days Time"])
    net_c = _pick_col(df, ["EV Network", "EV Network", "Network"])
    if not lat_c or not lon_c:
        return None
    df = df.copy()
    df["lat"] = pd.to_numeric(df[lat_c], errors="coerce")
    df["lon"] = pd.to_numeric(df[lon_c], errors="coerce")
    df["l2_ports"] = pd.to_numeric(df[l2_c], errors="coerce").fillna(0) if l2_c else 0
    df["dcfc_ports"] = pd.to_numeric(df[dc_c], errors="coerce").fillna(0) if dc_c else 0
    if state_c:
        df = df[df[state_c].astype(str).str.upper().str.strip().isin(["IL", "ILLINOIS"])]
    df = df.dropna(subset=["lat", "lon"])
    df = df[df["lat"].between(36.8, 42.7) & df["lon"].between(-91.7, -87.0)]
    # Dedupe by site (ID)
    if id_c and id_c in df.columns:
        agg_d = {
            "lat": ("lat", "first"),
            "lon": ("lon", "first"),
            "l2_ports": ("l2_ports", "max"),
            "dcfc_ports": ("dcfc_ports", "max"),
        }
        if name_c:
            agg_d["_name"] = (name_c, "first")
        if addr_c:
            agg_d["_addr"] = (addr_c, "first")
        if city_c:
            agg_d["_city"] = (city_c, "first")
        if state_col:
            agg_d["_state"] = (state_col, "first")
        if zip_c:
            agg_d["_zip"] = (zip_c, "first")
        if status_c:
            agg_d["_status"] = (status_c, "first")
        if access_c:
            agg_d["_access"] = (access_c, "first")
        if net_c:
            agg_d["_network"] = (net_c, "first")
        df = df.groupby(id_c, as_index=False).agg(**agg_d)
    if "_name" not in df.columns:
        df["_name"] = df.get(name_c, "—") if name_c else "—"
    if "_addr" not in df.columns:
        df["_addr"] = df[addr_c] if addr_c and addr_c in df.columns else ""
    if "_city" not in df.columns:
        df["_city"] = df.get(city_c, "") if city_c else ""
    if "_state" not in df.columns:
        df["_state"] = df.get(state_col, "") if state_col else ""
    if "_zip" not in df.columns:
        df["_zip"] = df.get(zip_c, "") if zip_c else ""
    if "_status" not in df.columns:
        df["_status"] = df.get(status_c, "—") if status_c else "—"
    if "_access" not in df.columns:
        df["_access"] = df.get(access_c, "—") if access_c else "—"
    if "_network" not in df.columns:
        df["_network"] = df.get(net_c, "—") if net_c else "—"
    df["ports_total"] = (df["l2_ports"] + df["dcfc_ports"]).clip(lower=0).replace(0, 1)
    df["station_type"] = df.apply(lambda r: compute_station_type_11(r["l2_ports"], r["dcfc_ports"]), axis=1)
    df["status_group"] = "Existing"
    df["address"] = df["_addr"].astype(str) + ", " + df["_city"].astype(str) + ", " + df["_state"].astype(str) + " " + df["_zip"].astype(str)
    df["station_name"] = df["_name"].astype(str)
    df["status_or_group"] = df["_status"].astype(str)
    df["access_days_time"] = df["_access"].astype(str)
    df["ev_network"] = df["_network"].astype(str)
    df["city_il"] = (df["_city"].astype(str) + ", " + df["_state"].astype(str)).str.strip(", ")
    return df[["lat", "lon", "l2_ports", "dcfc_ports", "ports_total", "station_type", "status_group",
               "station_name", "address", "status_or_group", "access_days_time", "ev_network", "city_il"]].copy()


def load_future_nevi(csv_path="data/data/ev_future_under_construction.csv"):
    """
    Load future CSV: standardize to lat, lon, l2_ports, dcfc_ports, ports_total, station_type, status_group.
    Hover fields: station_name (Site Host), address (City, County), status_or_group (Online Status).
    """
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    lat_c = _pick_col(df, ["LatDD", "Latitude"])
    lon_c = _pick_col(df, ["LongDD", "Longitude"])
    l2_c = _pick_col(df, ["Level 2 Ports", "Level2 Ports"])
    dc_c = _pick_col(df, ["Level 3 Ports", "Level3 Ports", "EV DC Fast Count"])
    name_c = _pick_col(df, ["Site Host", "Station Name"])
    city_c = _pick_col(df, ["City", "city"])
    county_c = _pick_col(df, ["County", "County"])
    status_c = _pick_col(df, ["Online Status", "Status Code", "Status"])
    if not lat_c or not lon_c:
        return None
    df = df.copy()
    df["lat"] = pd.to_numeric(df[lat_c], errors="coerce")
    df["lon"] = pd.to_numeric(df[lon_c], errors="coerce")
    df["l2_ports"] = pd.to_numeric(df[l2_c], errors="coerce").fillna(0) if l2_c else 0
    df["dcfc_ports"] = pd.to_numeric(df[dc_c], errors="coerce").fillna(0) if dc_c else 0
    df = df.dropna(subset=["lat", "lon"])
    df = df[df["lat"].between(36.8, 42.7) & df["lon"].between(-91.7, -87.0)]
    df["ports_total"] = (df["l2_ports"] + df["dcfc_ports"]).clip(lower=0).replace(0, 1)
    df["station_type"] = df.apply(lambda r: compute_station_type_11(r["l2_ports"], r["dcfc_ports"]), axis=1)
    df["status_group"] = "Future/New"
    df["station_name"] = df[name_c].astype(str) if name_c else "—"
    if city_c and city_c in df.columns and county_c and county_c in df.columns:
        df["address"] = (df[city_c].fillna("").astype(str) + ", " + df[county_c].fillna("").astype(str)).str.strip(", ")
    elif city_c and city_c in df.columns:
        df["address"] = df[city_c].fillna("").astype(str)
    else:
        df["address"] = "—"
    df["status_or_group"] = df[status_c].astype(str) if status_c else "Future/New"
    df["access_days_time"] = "—"
    df["ev_network"] = "—"
    df["city_il"] = (df[city_c].fillna("").astype(str) + ", IL").str.strip(", ") if city_c and city_c in df.columns else "—"
    return df[["lat", "lon", "l2_ports", "dcfc_ports", "ports_total", "station_type", "status_group",
               "station_name", "address", "status_or_group", "access_days_time", "ev_network", "city_il"]].copy()


# Illinois state fill for 1.1 maps: light blue-grey consistent with carto-positron and dashboard palette
IL_STATE_FILL = "rgba(235,242,249,0.42)"
IL_STATE_LINE = "#2c3e50"


def get_illinois_geojson(tract_shp_path="ArcGIS visualizations/tl_2020_17_tract.shp"):
    """Return Illinois state boundary as GeoJSON dict (WGS84) for map layers, or None if unavailable."""
    if not _HAS_GEOPANDAS or not os.path.exists(tract_shp_path):
        return None
    try:
        tracts = gpd.read_file(tract_shp_path)
        il = tracts.dissolve()
        il = il.to_crs("EPSG:4326")
        return il.__geo_interface__
    except Exception:
        return None


def get_illinois_interstates_plotly(roads_shp_path="data/roads/tl_2023_17_prisecroads.shp"):
    """Return (lats, lons) for interstate lines in WGS84 for Plotly Scattermap, or (None, None) if unavailable."""
    if not _HAS_GEOPANDAS or not os.path.exists(roads_shp_path):
        return None, None
    try:
        roads = gpd.read_file(roads_shp_path).to_crs("EPSG:4326")
        if "RTTYP" not in roads.columns:
            return None, None
        roads = roads[roads["RTTYP"].isin(["I"])].copy()
        lats, lons = [], []
        for geom in roads.geometry:
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type == "LineString":
                for c in geom.coords:
                    lons.append(c[0])
                    lats.append(c[1])
                lons.append(None)
                lats.append(None)
            else:
                for part in geom.geoms:
                    for c in part.coords:
                        lons.append(c[0])
                        lats.append(c[1])
                    lons.append(None)
                    lats.append(None)
        return (lats, lons) if lats and lons else (None, None)
    except Exception:
        return None, None


def make_hover_html(row):
    """Build hover info-card text for 1.1 maps (Plotly accepts <br>)."""
    name = str(row.get("station_name", "—"))
    status = str(row.get("status_group", "—"))
    stype = str(row.get("station_type", "—"))
    ports = int(row.get("ports_total", 0) or 0)
    l2 = int(row.get("l2_ports", 0) or 0)
    dcfc = int(row.get("dcfc_ports", 0) or 0)
    city_il = str(row.get("city_il", "—"))
    return (
        f"<b>{name}</b><br>"
        "---------------------------------<br>"
        f"Status: {status}<br>"
        f"Type: {stype}<br>"
        f"Total Ports: {ports}<br>"
        f"L2: {l2} | DCFC: {dcfc}<br>"
        f"{city_il}"
    )


def make_hover_html_12(row):
    """Build hover info-card text for 1.2 map (Deployment: Future, L2/DCFC Ports, City IL)."""
    name = str(row.get("station_name", row.get("Site Host", "—")))
    stype = str(row.get("station_type", "—"))
    l2 = int(row.get("l2_ports", row.get("l2", 0)) or 0)
    dcfc = int(row.get("dcfc_ports", row.get("l3", 0)) or 0)
    city_il = str(row.get("city_il", "—"))
    if city_il == "—" and row.get("City"):
        city_il = str(row.get("City", "")) + ", IL"
    return (
        f"<b>{name}</b><br>"
        "---------------------------------<br>"
        "Deployment: Future<br>"
        f"Type: {stype}<br>"
        f"L2 Ports: {l2}<br>"
        f"DCFC Ports: {dcfc}<br>"
        f"{city_il}"
    )


def plot_all_stations_map_plotly(existing_df, future_df, size_max=14, size_min=4, il_geojson=None, interstates_lat_lon=None):
    """Map A: All stations, Existing (blue) + Future/New (orange), marker size by ports_total. Hover = info card."""
    if (existing_df is None or len(existing_df) == 0) and (future_df is None or len(future_df) == 0):
        return None
    fig = go.Figure()
    # Interstates first (below station markers)
    if interstates_lat_lon is not None:
        lats_i, lons_i = interstates_lat_lon
        if lats_i and lons_i:
            fig.add_trace(
                go.Scattermap(
                    lat=lats_i,
                    lon=lons_i,
                    mode="lines",
                    line=dict(color=C_INTERSTATE, width=1.5),
                    name="Interstates",
                    showlegend=True,
                )
            )
    # Size scaling (smaller circles)
    def scale_size(ports, smin=size_min, smax=size_max):
        p = np.clip(ports.astype(float), 1, None)
        return smin + (smax - smin) * (np.log1p(p) / np.log1p(p.max()) if p.max() > 0 else 0)
    if existing_df is not None and len(existing_df) > 0:
        existing_df = existing_df.copy()
        existing_df["_size"] = scale_size(existing_df["ports_total"].values)
        existing_df["_hover"] = existing_df.apply(make_hover_html, axis=1)
        fig.add_trace(
            go.Scattermap(
                lat=existing_df["lat"],
                lon=existing_df["lon"],
                mode="markers",
                marker=dict(size=existing_df["_size"], color=C_EXISTING_BLUE, opacity=0.75, symbol="circle"),
                text=existing_df["_hover"],
                hoverinfo="text",
                name="Existing",
            )
        )
    if future_df is not None and len(future_df) > 0:
        future_df = future_df.copy()
        future_df["_size"] = scale_size(future_df["ports_total"].values)
        future_df["_hover"] = future_df.apply(make_hover_html, axis=1)
        fig.add_trace(
            go.Scattermap(
                lat=future_df["lat"],
                lon=future_df["lon"],
                mode="markers",
                marker=dict(size=future_df["_size"], color=C_FUTURE_ORANGE, opacity=0.75, symbol="circle"),
                text=future_df["_hover"],
                hoverinfo="text",
                name="Future/New",
            )
        )
    map_kw = dict(style="carto-positron", zoom=5.8, center=dict(lat=40.0, lon=-89.2))
    if il_geojson:
        map_kw["layers"] = [
            dict(sourcetype="geojson", source=il_geojson, type="fill", color=IL_STATE_FILL),
            dict(sourcetype="geojson", source=il_geojson, type="line", color=IL_STATE_LINE, line=dict(width=1.8)),
        ]
    fig.update_layout(
        map=map_kw,
        height=740,
        margin=dict(l=0, r=0, t=24, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return fig


def plot_future_by_type_map_plotly(future_df, size_default=8, il_geojson=None, interstates_lat_lon=None):
    """Map B: Future/New by station_type — 3 traces: Level 2 (L2), DCFC, Mixed (L2 + DCFC). Hover = info card."""
    if future_df is None or len(future_df) == 0:
        return None
    order = ["Level 2 (L2)", "DCFC", "Mixed (L2 + DCFC)"]
    colors = {"Level 2 (L2)": C_LEVEL2, "DCFC": "#e67f23", "Mixed (L2 + DCFC)": "#9b59b6"}
    future_df = future_df.copy()
    future_df["_hover"] = future_df.apply(make_hover_html, axis=1)
    fig = go.Figure()
    # Interstates first (below station markers)
    if interstates_lat_lon is not None:
        lats_i, lons_i = interstates_lat_lon
        if lats_i and lons_i:
            fig.add_trace(
                go.Scattermap(
                    lat=lats_i,
                    lon=lons_i,
                    mode="lines",
                    line=dict(color=C_INTERSTATE, width=1.5),
                    name="Interstates",
                    showlegend=True,
                )
            )
    for stype in order:
        sub = future_df[future_df["station_type"] == stype]
        if len(sub) == 0:
            continue
        fig.add_trace(
            go.Scattermap(
                lat=sub["lat"],
                lon=sub["lon"],
                mode="markers",
                marker=dict(size=size_default, color=colors.get(stype, "gray"), opacity=0.85, symbol="circle"),
                text=sub["_hover"],
                hoverinfo="text",
                name=stype,
            )
        )
    map_kw = dict(style="carto-positron", zoom=5.8, center=dict(lat=40.0, lon=-89.2))
    if il_geojson:
        map_kw["layers"] = [
            dict(sourcetype="geojson", source=il_geojson, type="fill", color=IL_STATE_FILL),
            dict(sourcetype="geojson", source=il_geojson, type="line", color=IL_STATE_LINE, line=dict(width=1.8)),
        ]
    fig.update_layout(
        map=map_kw,
        height=740,
        margin=dict(l=0, r=0, t=24, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return fig


# =============================================================================
# TEXT-ONLY FUNCTIONS (rendered first, as main body)
# =============================================================================

def render_11_text():
    st.markdown('<div id="section-11"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">1.1 Current and planned EV charging stations</div>',
                unsafe_allow_html=True)
    st.markdown("""
We started by pulling existing station data from the Alternative Fuels Data Center (AFDC)
through the project's coordination with IDOT, and planned stations from the NEVI Formula Program
dataset covering federally funded sites not yet operational. We then ran a spatial check to drop
any planned station within roughly 100 meters of an existing one to avoid double-counting.
""", unsafe_allow_html=True)


def render_12_text():
    st.markdown('<div id="section-12"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">1.2 Gap and Accessibility Analysis</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
From there, we wanted to understand whether the existing network actually serves the people who
need it. For each census tract $j$, we estimated how many EVs the nearby network can service
given charger speed and utilization, then compared that to local EV registrations. $T_j$ is
the tract-level service capacity and $V_j$ is local demand. The accessibility index $A_j$
shows how well the two line up.
""")
    st.markdown("#### Key Formulas and Accessibility Index")
    st.markdown("""
    The accessibility index $A_j$ compares local EV charging demand with available charging service capacity:
    """)
    centered_formula_row("Port service potential",
                         r"E2_{i_2,j}=\frac{C_2U_2}{D_jA_{i_2,k}},\quad E3_{i_3,j}=\frac{C_3U_3}{D_jA_{i_3,k}}")
    centered_formula_row("Tract serviceable EVs",
                         r"T_j = Pop_j\left(\sum_{i_2=1}^{N_{2,j}}E2_{i_2,j}+\sum_{i_3=1}^{N_{3,j}}E3_{i_3,j}\right)")
    centered_formula_row("Accessibility index",
                         r"A_j = \frac{T_j - V_j}{T_j + V_j}")
    st.markdown("""
    $A_j$ ranges from $-1$ to $+1$. Positive means a tract has more charging capacity than local
    demand. Negative means demand is outpacing supply. Around zero, the two are roughly balanced.
    """, unsafe_allow_html=True)


def render_13_text():
    st.markdown('<div id="section-13"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">1.3 Electrified Miles Estimation</div>',
                unsafe_allow_html=True)
    st.markdown("""
Next, we wanted to understand how much the charging network actually expands what an EV can do.
To get there, we first asked: if there were no public DCFC stations at all, how many of Illinois's
daily trips could someone still complete in a battery EV, just on a home charge? That gives us
a baseline, meaning the trips short enough to be feasible with no public charging at all. Every
station we add on top of that baseline makes some previously-infeasible trips now doable, and
the miles from those newly-enabled trips are what we call <b>electrified miles</b>.
<br><br>
We ran 10 simulations at each network size $N$ and averaged the results. They fit a logarithmic
curve, $f(N) = 0.75\\ln(N) + 93.1$ ($R^2 = 0.8132$): the first few hundred stations unlock
the highest-traffic corridors and produce the biggest jumps, while later additions reach into
lower-demand areas where the marginal gain is smaller. This is why the curve flattens. It is not
because charging stops mattering, but because the easy wins are already captured.
""", unsafe_allow_html=True)


def render_14_text():
    st.markdown('<div id="section-14"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">1.4 Willingness to Pay (Per Traveler)</div>',
                unsafe_allow_html=True)
    st.markdown("""
Finally, we put a dollar value on what the network expansion is actually worth to drivers.
The willingness to pay (WTP) figure is built up from three separate sources of benefit that
charging access creates:
<ul>
  <li><b>Fuel cost savings:</b> every electrified mile is a mile not paid for at the gas pump.
  We net out the electricity cost, so this captures the real take-home saving per mile driven electrically.</li>
  <li><b>Time and detour savings:</b> without nearby charging, drivers either reroute significantly
  to find a station or cut trips short. More stations mean less of that detour overhead, and
  we translate the saved travel time into dollars using a standard value-of-time.</li>
  <li><b>Charging access value:</b> some trips are simply not possible in a BEV without a station
  along the way. This component captures the benefit of trips that go from impossible to feasible,
  which is especially significant for longer inter-regional and rural corridors.</li>
</ul>
We sum these three components across all Illinois BEV drivers and discount them over the vehicle
lifetime. The benefit per traveler is highest when stations are scarce, because each new one unlocks
a lot of previously-infeasible trips. It drops off as the network fills in, which is consistent with
what we saw in section 1.3. We tested per-mile values from \\$0.35 to \\$0.64, and the shaded band
shows how sensitive the total estimate is to that assumption.
""", unsafe_allow_html=True)


# =============================================================================
# VISUAL-ONLY FUNCTIONS (rendered in appendix)
# =============================================================================

def render_11():
    import pandas as pd
    import numpy as np

    st.markdown('<div id="appendix-11"></div>', unsafe_allow_html=True)
    st.markdown("#### All EV Charging Stations (Size = Number of Ports)")

    # ---- Paths (using actual file locations) ----
    tract_shp = "ArcGIS visualizations/tl_2020_17_tract.shp"
    afdc_csv = "data/data/afdc_current.csv"  # existing
    future_csv = "data/data/ev_future_under_construction.csv"  # awarded/under construction

    # Check if files exist
    if not os.path.exists(afdc_csv):
        st.error(f"AFDC file not found at {afdc_csv}")
        centered_image_fixed(
            "figures/1.1/plot1_all_stations_by_ports_副本.png",
            width=700,
            placeholder_text="All EV Charging Stations\n(Upload image to display)",
            ph_h=311
        )
        return
    if not os.path.exists(future_csv):
        st.error(f"Future stations file not found at {future_csv}")
        centered_image_fixed(
            "figures/1.1/plot1_all_stations_by_ports_副本.png",
            width=700,
            placeholder_text="All EV Charging Stations\n(Upload image to display)",
            ph_h=311
        )
        return

    try:
        # ---- Load data (1.1 Plotly: standardized loaders) ----
        existing_11 = load_existing_afdc(afdc_csv)
        future_11 = load_future_nevi(future_csv)
        if existing_11 is None:
            existing_11 = pd.DataFrame()
        if future_11 is None:
            future_11 = pd.DataFrame()
        # Cross-dedup: drop future points near existing (optional, keeps behavior consistent)
        if len(existing_11) > 0 and len(future_11) > 0:
            future_11, _, _ = _remove_future_duplicates_against_existing_11(
                existing_11,
                future_11,
                distance_threshold=0.001,
            )
        existing_n = len(existing_11)
        future_n = len(future_11)
        tract_shp = "ArcGIS visualizations/tl_2020_17_tract.shp"
        roads_shp = "data/roads/tl_2023_17_prisecroads.shp"
        il_geojson = get_illinois_geojson(tract_shp)
        interstates_lat_lon = get_illinois_interstates_plotly(roads_shp)
        if interstates_lat_lon == (None, None):
            interstates_lat_lon = None

        # ---- Map A: All EV Charging Stations (Size = # Ports) ----
        fig_a = plot_all_stations_map_plotly(
            existing_11, future_11, il_geojson=il_geojson, interstates_lat_lon=interstates_lat_lon
        )
        if fig_a is not None:
            st.plotly_chart(fig_a, width="stretch", key="sec11_map_all_stations")
            st.caption(
                f"Figure 1. All EV charging stations in Illinois (size = number of ports). "
                f"Existing ({existing_n}) and Future/New ({future_n}) stations. Hover for details."
            )
        else:
            centered_image_fixed(
                "figures/1.1/plot1_all_stations_by_ports_副本.png",
                width=700,
                placeholder_text="All EV Charging Stations\n(Upload image to display)",
                ph_h=311
            )
            st.caption("Figure 1. All EV charging stations in Illinois (size = number of ports).")

        st.markdown("#### Future/New Stations by Charging Level")
        # ---- Map B: Future/New by Charging Level (Level 2, DCFC, Mixed) ----
        fig_b = plot_future_by_type_map_plotly(
            future_11, il_geojson=il_geojson, interstates_lat_lon=interstates_lat_lon
        )
        if fig_b is not None:
            st.plotly_chart(fig_b, width="stretch", key="sec11_map_future_by_type")
            n_l2 = len(future_11[future_11["station_type"] == "Level 2 (L2)"]) if len(future_11) > 0 else 0
            n_dcfc = len(future_11[future_11["station_type"] == "DCFC"]) if len(future_11) > 0 else 0
            n_mixed = len(future_11[future_11["station_type"] == "Mixed (L2 + DCFC)"]) if len(future_11) > 0 else 0
            st.caption(
                f"Figure 2. Future/New EV charging stations by charging level: "
                f"Level 2 (L2) ({n_l2}), DCFC ({n_dcfc}), Mixed (L2 + DCFC) ({n_mixed}) across Illinois. Hover for details."
            )
        else:
            centered_image_fixed(
                "figures/1.1/plot3_future_by_charging_level_副本.png",
                width=700,
                placeholder_text="Future/New Stations by Charging Level\n(Upload image to display)",
                ph_h=311
            )
            st.caption(
                "Figure 2. Future/New EV charging stations by charging level: Level 2 (L2), DCFC, Mixed (L2 + DCFC) across Illinois."
            )

        st.markdown(
            "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.5rem;'>"
            "Data source: <a href='https://afdc.energy.gov/stations#/find/nearest' target='_blank'>Alternative Fuels Data Center (AFDC)</a>, "
            "accessed 2025-06-22</div>",
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Error generating plot: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        # Fallback to static image if dynamic plot fails
        st.info("Falling back to static image...")
        centered_image_fixed(
            "figures/1.1/plot1_all_stations_by_ports_副本.png",
            width=700,
            placeholder_text="All EV Charging Stations\n(Upload image to display)",
            ph_h=311
        )


# ---- Section 1.2: Accessibility log-ratio (Δ = log(A_future+ε) - log(A_current+ε)) ----
def _stations_to_xy_weights(df, lat_col="lat", lon_col="lon", l2_col="l2", dc_col="l3", use_port_weights=True):
    """Return (n,2) xy in meters (EPSG:26916) and (n,) weights. df must have lat, lon, l2, dc."""
    import geopandas as gpd
    gdf = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326",
    )
    gdf = gdf.to_crs("EPSG:26916")
    xy = np.column_stack([gdf.geometry.x.values, gdf.geometry.y.values])
    if use_port_weights:
        w = (gdf[l2_col].values.astype(float) + gdf[dc_col].values.astype(float))
        w = np.maximum(w, 1.0)
    else:
        w = np.ones(len(gdf), dtype=float)
    return xy, w, gdf


def _accessibility_at_targets(targets_xy, station_xy, station_w, alpha=1.5, max_dist_m=80000):
    """A_i = sum_j w_j / (d_ij^alpha) for targets within max_dist_m of stations. Uses scipy cKDTree."""
    from scipy.spatial import cKDTree
    tree = cKDTree(station_xy)
    idx_lists = tree.query_ball_point(targets_xy, r=max_dist_m)
    A = np.zeros(len(targets_xy), dtype=float)
    for i, idxs in enumerate(idx_lists):
        if not idxs:
            continue
        pts = station_xy[idxs]
        d = np.sqrt(((pts - targets_xy[i]) ** 2).sum(axis=1))
        d = np.maximum(d, 1.0)
        A[i] = np.sum(station_w[idxs] / (d ** alpha))
    return A


def _categorize_station(row, l2_col="l2", dc_col="l3"):
    l2, dc = float(row.get(l2_col, 0) or 0), float(row.get(dc_col, 0) or 0)
    if dc > 0 and l2 > 0:
        return "Mixed (L2 + DCFC)"
    if dc > 0:
        return "DCFC"
    if l2 > 0:
        return "Level 2 (L2)"
    return "Unknown"


def _build_log_ratio_map(tract_shp, current_df, future_df, alpha=1.5, eps=1e-6, max_km=80):
    """
    Compute delta_log_ratio = log(A_future + ε) - log(A_current + ε) per tract.
    current_df, future_df must have columns: lat, lon, l2, l3 (or l2_col/dc_col).
    Returns (tracts_gdf with delta_log_ratio and chg_cat, future_gdf_m with station_type, success).
    """
    import geopandas as gpd
    from scipy.spatial import cKDTree
    try:
        tracts = gpd.read_file(tract_shp)
    except Exception:
        return None, None, False
    if "GEOID" not in tracts.columns and "geoid" in [c.lower() for c in tracts.columns]:
        gcol = [c for c in tracts.columns if c.lower() == "geoid"][0]
        tracts["GEOID"] = tracts[gcol].astype(str).str.zfill(11)
    elif "GEOID" not in tracts.columns:
        return None, None, False
    tracts = tracts.to_crs("EPSG:26916")
    tracts["centroid"] = tracts.geometry.centroid
    targets_xy = np.column_stack([tracts["centroid"].x.values, tracts["centroid"].y.values])

    cur_xy, cur_w, _ = _stations_to_xy_weights(current_df, use_port_weights=True)
    fut_xy, fut_w, future_gdf_m = _stations_to_xy_weights(future_df, use_port_weights=True)

    A_cur = _accessibility_at_targets(targets_xy, cur_xy, cur_w, alpha=alpha, max_dist_m=max_km * 1000)
    A_fut = _accessibility_at_targets(
        targets_xy,
        np.vstack([cur_xy, fut_xy]),
        np.hstack([cur_w, fut_w]),
        alpha=alpha,
        max_dist_m=max_km * 1000,
    )
    delta = np.log(A_fut + eps) - np.log(A_cur + eps)
    tracts["delta_log_ratio"] = delta
    tracts["chg_cat"] = np.where(delta > 0, "Improved", np.where(delta < 0, "Reduced", "No change"))

    future_gdf_m["station_type"] = future_gdf_m.apply(
        lambda r: _categorize_station(r, "l2", "l3"), axis=1
    )
    return tracts, future_gdf_m, True


def _plot_change_index_like_paper(ax, tracts_gdf, value_col="delta_log_ratio", roads_gdf=None):
    """
    Choropleth with discrete bins + paper colors (blue = spillover, red = undersupply).
    Bins: [-1, -0.69), [-0.69, -0.38), [-0.38, 0), [0, 0.34), [0.34, 0.73), [0.73, 1].
    Missing data = gray. Optional roads overlay.
    """
    import matplotlib.patches as mpatches
    from matplotlib.colors import ListedColormap, BoundaryNorm

    gdf = tracts_gdf.copy()
    gdf[value_col] = pd.to_numeric(gdf[value_col], errors="coerce")
    gdf["val_clip"] = gdf[value_col].clip(-1.0, 1.0)

    bins = [-1.0, -0.69, -0.38, 0.0, 0.34, 0.73, 1.0]
    colors = [
        C_SPILL_STRONG,
        C_SPILL_MOD,
        C_SPILL_MILD,
        C_UNDER_MILD,
        C_UNDER_MOD,
        C_UNDER_SEV,
    ]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bins, cmap.N, clip=True)

    missing = gdf[gdf["val_clip"].isna()]
    if len(missing) > 0:
        missing.plot(ax=ax, color=C_MISSING, linewidth=0.2, edgecolor="white", zorder=1)

    non_missing = gdf[~gdf["val_clip"].isna()]
    if len(non_missing) > 0:
        non_missing.plot(
            ax=ax,
            column="val_clip",
            cmap=cmap,
            norm=norm,
            linewidth=0,
            edgecolor=None,
            zorder=2,
        )

    if roads_gdf is not None and len(roads_gdf) > 0:
        roads_gdf.plot(
            ax=ax,
            color=C_INTERSTATE,
            linewidth=1.2,
            alpha=0.95,
            zorder=3,
        )

    labels = [
        "Strong Spillover Capacity (-1.00 to -0.69)",
        "Moderate Spillover Capacity (-0.69 to -0.38)",
        "Mild Spillover Capacity (-0.38 to -0.00)",
        "Mild Undersupply (0.00 to 0.34)",
        "Moderate Undersupply (0.34 to 0.73)",
        "Severe Undersupply (0.73 to 1.00)",
        "Missing Data",
    ]
    legend_patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(6)]
    legend_patches.append(mpatches.Patch(color=C_MISSING, label=labels[6]))
    if roads_gdf is not None and len(roads_gdf) > 0:
        legend_patches.append(mpatches.Patch(color=C_INTERSTATE, label="Interstate Routes"))
    return ax, legend_patches


def render_12():
    st.markdown('<div id="appendix-12"></div>', unsafe_allow_html=True)
    st.markdown("#### Current Charging Accessibility (A)")
    # Map 1: Interactive choropleth (Accessibility A) when shapefile + CSV + geopandas available
    tract_shp = "ArcGIS visualizations/tl_2020_17_tract.shp"
    access_csv = "data/final_ev_accessibility_results_副本.csv"
    map_ok = (
        _HAS_GEOPANDAS
        and os.path.exists(tract_shp)
        and os.path.exists(access_csv)
    )

    if map_ok:
        try:
            tracts = gpd.read_file(tract_shp)
            tracts["GEOID"] = tracts["GEOID"].astype(str).str.zfill(11)
            df = pd.read_csv(access_csv, dtype={"GEOID": str})
            df["GEOID"] = df["GEOID"].str.zfill(11)
            gdf = tracts.merge(df, on="GEOID", how="left")
            geojson = gdf.__geo_interface__

            # Paper bins: 1 = blue (spillover), -1 = red (undersupply). Normalized 0..1 for Plotly.
            _norm = lambda x: (x + 1) / 2
            _paper_scale = [
                [0, C_UNDER_SEV],       # -1 -> red
                [_norm(-0.69), C_UNDER_MOD],
                [_norm(-0.38), C_UNDER_MILD],
                [_norm(0), C_SPILL_MILD],
                [_norm(0.34), C_SPILL_MOD],
                [_norm(0.73), C_SPILL_STRONG],
                [1, C_SPILL_STRONG],    # 1 -> blue
            ]
            fig = px.choropleth_map(
                gdf,
                geojson=geojson,
                locations="GEOID",
                featureidkey="properties.GEOID",
                color="accessibility_index",
                range_color=(-1, 1),
                color_continuous_scale=_paper_scale,
                hover_data={
                    "GEOID": True,
                    "accessibility_index": ":.3f",
                    "ev_count": ":.1f",
                    "nearby_stations": True,
                    "a_category": True,
                },
                map_style="carto-positron",
                zoom=5.8,
                center={"lat": 40.0, "lon": -89.2},
                opacity=0.80,
            )
            fig.update_traces(marker_line_color="white", marker_line_width=0.2)
            fig.update_layout(
                height=740,
                margin=dict(l=0, r=0, t=40, b=0),
                coloraxis_colorbar=dict(title="Accessibility (A)"),
            )

            # Interstate roads layer (same source as other maps)
            roads_shp_a = "data/roads/tl_2023_17_prisecroads.shp"
            if os.path.exists(roads_shp_a):
                try:
                    roads_a = gpd.read_file(roads_shp_a).to_crs("EPSG:4326")
                    if "RTTYP" in roads_a.columns:
                        roads_a = roads_a[roads_a["RTTYP"].isin(["I"])].copy()
                    lats, lons = [], []
                    for geom in roads_a.geometry:
                        if geom is None or geom.is_empty:
                            continue
                        if geom.geom_type == "LineString":
                            for c in geom.coords:
                                lons.append(c[0])
                                lats.append(c[1])
                            lons.append(None)
                            lats.append(None)
                        else:
                            for part in geom.geoms:
                                for c in part.coords:
                                    lons.append(c[0])
                                    lats.append(c[1])
                                lons.append(None)
                                lats.append(None)
                    if lats and lons:
                        fig.add_trace(
                            go.Scattermap(
                                lat=lats,
                                lon=lons,
                                mode="lines",
                                line=dict(color=C_INTERSTATE, width=1.5),
                                name="Interstates",
                                showlegend=True,
                            )
                        )
                except Exception:
                    pass

            st.plotly_chart(
                fig,
                width="stretch",
                key="map1_accessibility_a",
            )
        except Exception as e:
            st.warning(f"Interactive map could not be loaded: {e}. Showing static image.")
            centered_image_fixed(
                "figures/1.2/illinois_ev_accessibility_A_keep_original_naturalbreaks_副本.png",
                width=700,
                placeholder_text="Accessibility (A) Map\n(Upload image to display)",
                ph_h=488,
            )
    else:
        centered_image_fixed(
            "figures/1.2/illinois_ev_accessibility_A_keep_original_naturalbreaks_副本.png",
            width=700,
            placeholder_text="Accessibility (A) Map\n(Upload image to display)",
            ph_h=488,
        )

    st.markdown(
        "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>Figure 3. EV Charging Station Accessibility (A) Illinois Census Tracts, 2025. This map identifies where charging gaps currently exist, providing a baseline for evaluating future infrastructure deployment.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Accessibility Change (Log Ratio) with Future Stations")
    # Replicate paper: Δ_i = log(A_i_future + ε) - log(A_i_current + ε); choropleth + future station points
    tract_shp_12 = "ArcGIS visualizations/tl_2020_17_tract.shp"
    afdc_csv_12 = "data/data/afdc_current.csv"
    future_csv_12 = "data/data/ev_future_under_construction.csv"
    log_ratio_ok = (
        _HAS_GEOPANDAS
        and os.path.exists(tract_shp_12)
        and os.path.exists(afdc_csv_12)
        and os.path.exists(future_csv_12)
    )
    if log_ratio_ok:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.colors as mcolors
            # Load current: AFDC, IL, dedupe by ID
            afdc_12 = pd.read_csv(afdc_csv_12)
            afdc_12["lat"] = pd.to_numeric(afdc_12["Latitude"], errors="coerce")
            afdc_12["lon"] = pd.to_numeric(afdc_12["Longitude"], errors="coerce")
            afdc_12["l2"] = pd.to_numeric(afdc_12["EV Level2 EVSE Num"], errors="coerce").fillna(0)
            afdc_12["l3"] = pd.to_numeric(afdc_12["EV DC Fast Count"], errors="coerce").fillna(0)
            afdc_12 = afdc_12[afdc_12["State"].astype(str).str.upper().str.strip().isin(["IL", "ILLINOIS"])]
            if "ID" in afdc_12.columns:
                afdc_12 = (
                    afdc_12.groupby("ID", as_index=False)
                    .agg(lat=("lat", "first"), lon=("lon", "first"), l2=("l2", "max"), l3=("l3", "max"))
                )
            afdc_12 = afdc_12.dropna(subset=["lat", "lon"])
            afdc_12 = afdc_12[afdc_12["lat"].between(36.8, 42.7) & afdc_12["lon"].between(-91.7, -87.0)]

            # Load future: same l2/l3 column convention
            fut_12 = pd.read_csv(future_csv_12)
            fut_12["lat"] = pd.to_numeric(fut_12["LatDD"], errors="coerce")
            fut_12["lon"] = pd.to_numeric(fut_12["LongDD"], errors="coerce")
            fut_12["l2"] = pd.to_numeric(fut_12["Level 2 Ports"], errors="coerce").fillna(0)
            fut_12["l3"] = pd.to_numeric(fut_12["Level 3 Ports"], errors="coerce").fillna(0)
            fut_12 = fut_12.dropna(subset=["lat", "lon"])
            fut_12 = fut_12[fut_12["lat"].between(36.8, 42.7) & fut_12["lon"].between(-91.7, -87.0)]

            # Prefer mentor-style CSV (inaccessibility_index_future) if available
            mentor_csv = "data/ev_accessibility_log_ratio_change_results_副本.csv"
            if not os.path.exists(mentor_csv):
                mentor_csv = "data/ev_accessibility_log_ratio_change_results.csv"
            use_mentor_csv = os.path.exists(mentor_csv)

            if use_mentor_csv:
                tracts_lr = gpd.read_file(tract_shp_12)
                if "GEOID" not in tracts_lr.columns and "geoid" in [c.lower() for c in tracts_lr.columns]:
                    gcol = [c for c in tracts_lr.columns if c.lower() == "geoid"][0]
                    tracts_lr["GEOID"] = tracts_lr[gcol].astype(str).str.zfill(11)
                tracts_lr["GEOID"] = tracts_lr["GEOID"].astype(str).str.zfill(11)
                tracts_lr = tracts_lr.to_crs("EPSG:26916")
                res = pd.read_csv(mentor_csv, dtype={"GEOID": str})
                res["GEOID"] = res["GEOID"].astype(str).str.zfill(11)
                if "log_ratio_change" in res.columns:
                    tracts_lr = tracts_lr.merge(
                        res[["GEOID", "log_ratio_change"]], on="GEOID", how="left"
                    )
                else:
                    use_mentor_csv = False
                _, _, future_gdf_m = _stations_to_xy_weights(fut_12, use_port_weights=True)
                future_gdf_m["station_type"] = future_gdf_m.apply(
                    lambda r: _categorize_station(r, "l2", "l3"), axis=1
                )
            if not use_mentor_csv:
                tracts_lr, future_gdf_m, success = _build_log_ratio_map(
                    tract_shp_12, afdc_12, fut_12, alpha=1.5, eps=1e-6, max_km=80
                )
                if not success or tracts_lr is None or future_gdf_m is None:
                    tracts_lr = None
                elif tracts_lr is not None:
                    tracts_lr["log_ratio_change"] = tracts_lr["delta_log_ratio"]

            if tracts_lr is not None and future_gdf_m is not None:
                import matplotlib.patches as mpatches
                from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
                roads_shp = "data/roads/tl_2023_17_prisecroads.shp"
                roads_gdf = None
                if os.path.exists(roads_shp):
                    try:
                        roads_gdf = gpd.read_file(roads_shp).to_crs("EPSG:26916")
                        if roads_gdf is not None and "RTTYP" in roads_gdf.columns:
                            roads_gdf = roads_gdf[roads_gdf["RTTYP"].isin(["I"])].copy()
                    except Exception:
                        roads_gdf = None

                # Diverging colormap: -2 = deep red, 0 = white, +2 = blue
                cmap_lr = LinearSegmentedColormap.from_list(
                    "custom_diverging",
                    [
                        (0.0, "#5f031d"),   # -2.0 (deep red)
                        (0.5, "#ebf2f9"),   #  0.0 (light blue-grey, zero)
                        (1.0, "#4a91e2"),   # +2.0 (blue)
                    ],
                )
                norm_lr = TwoSlopeNorm(vmin=-2, vcenter=0, vmax=2)

                # Keep visual size but render at higher DPI for sharper output
                fig_lr, ax_lr = plt.subplots(1, 1, figsize=(8, 5), dpi=200)
                tracts_lr["log_ratio_change"] = pd.to_numeric(tracts_lr["log_ratio_change"], errors="coerce")
                missing_lr = tracts_lr[tracts_lr["log_ratio_change"].isna()]
                non_missing_lr = tracts_lr[tracts_lr["log_ratio_change"].notna()]
                # No-data and interstate colors for this figure only
                no_data_grey = "#e0e0e0"
                interstate_dark_grey = "#505050"
                if len(missing_lr) > 0:
                    missing_lr.plot(ax=ax_lr, color=no_data_grey, linewidth=0.1, edgecolor="white", zorder=1)
                if len(non_missing_lr) > 0:
                    non_missing_lr.plot(
                        column="log_ratio_change",
                        cmap=cmap_lr,
                        norm=norm_lr,
                        linewidth=0.1,
                        edgecolor="white",
                        ax=ax_lr,
                        zorder=2,
                    )
                if roads_gdf is not None and len(roads_gdf) > 0:
                    roads_gdf.plot(
                        ax=ax_lr,
                        color=interstate_dark_grey,
                        linewidth=0.35,
                        alpha=0.95,
                        zorder=3,
                    )
                type_order = ["DCFC", "Level 2 (L2)", "Mixed (L2 + DCFC)"]
                point_colors = {
                    "DCFC": "#e67f23",              # orange (rectangle)
                    "Level 2 (L2)": C_LEVEL2,
                    "Mixed (L2 + DCFC)": "#9b59b6", # purple (diamond)
                }
                point_markers = {
                    "DCFC": "s",                    # square/rectangle
                    "Level 2 (L2)": "o",            # circle
                    "Mixed (L2 + DCFC)": "D",       # diamond
                }
                for t in type_order:
                    sub = future_gdf_m[future_gdf_m["station_type"] == t]
                    if len(sub) == 0:
                        continue
                    sub.plot(
                        ax=ax_lr,
                        markersize=4,
                        color=point_colors.get(t, "gray"),
                        marker=point_markers.get(t, "o"),
                        alpha=0.9,
                        label=t,
                        zorder=4,
                    )
                # Colorbar for log ratio: much smaller, no label (title deleted)
                sm = plt.cm.ScalarMappable(cmap=cmap_lr, norm=norm_lr)
                sm.set_array([])
                cbar = fig_lr.colorbar(sm, ax=ax_lr, shrink=0.45, fraction=0.035, aspect=28, pad=0.06)
                cbar.ax.tick_params(labelsize=5)
                legend_patches = [mpatches.Patch(color=no_data_grey, edgecolor="none", label="No data")]
                if roads_gdf is not None and len(roads_gdf) > 0:
                    legend_patches.append(mpatches.Patch(color=interstate_dark_grey, edgecolor="none", label="Interstate Routes"))
                for t in type_order:
                    if len(future_gdf_m[future_gdf_m["station_type"] == t]) > 0:
                        legend_patches.append(mpatches.Patch(color=point_colors.get(t, "gray"), label=t))
                # Legend: compact row above the map for a cleaner look
                ax_lr.legend(
                    handles=legend_patches,
                    loc="lower center",
                    bbox_to_anchor=(0.5, 1.02),
                    frameon=False,
                    fontsize=6,
                    ncol=4,
                    handlelength=0.9,
                    borderpad=0.2,
                    labelspacing=0.4,
                    columnspacing=0.8,
                )
                # Fill the landscape canvas with Illinois — no equal-aspect so portrait state fits 8×5
                ax_lr.margins(x=0.03, y=0.03)
                ax_lr.set_axis_off()
                plt.tight_layout(rect=[0, 0.10, 1, 0.98])
                # Display at 70% of container width
                _lc, _lm, _lr = st.columns([0.15, 0.70, 0.15])
                with _lm:
                    st.pyplot(fig_lr, width="stretch")
                st.markdown(
                    "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>"
                    "Figure 4. EV Charging Station Accessibility Change (Log Ratio) with Future Stations, Illinois Census Tracts. "
                    "Δ = log(A_future+ε) − log(A_current+ε). Blue shades: improved; red shades: reduced. Points: future stations by type.</div>",
                    unsafe_allow_html=True,
                )
            else:
                centered_image_fixed(
                    "figures/1.2/illinois_ev_accessibility_log_ratio_with_stations_副本.png",
                    width=700,
                    placeholder_text="Log Ratio Change Map\n(Upload image to display)",
                    ph_h=438,
                )
                st.markdown(
                    "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>Figure 4. EV Charging Station Accessibility Change (Log Ratio) with Future Stations Illinois Census Tracts. Blue shades indicate improved accessibility, red shades indicate reduced accessibility relative to demand.</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.warning(f"Log-ratio map could not be generated: {e}. Showing static image.")
            centered_image_fixed(
                "figures/1.2/illinois_ev_accessibility_log_ratio_with_stations_副本.png",
                width=700,
                placeholder_text="Log Ratio Change Map\n(Upload image to display)",
                ph_h=438,
            )
            st.markdown(
                "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>Figure 4. EV Charging Station Accessibility Change (Log Ratio) with Future Stations Illinois Census Tracts. Blue shades indicate improved accessibility, red shades indicate reduced accessibility relative to demand.</div>",
                unsafe_allow_html=True,
            )
    else:
        centered_image_fixed(
            "figures/1.2/illinois_ev_accessibility_log_ratio_with_stations_副本.png",
            width=700,
            placeholder_text="Log Ratio Change Map\n(Upload image to display)",
            ph_h=438,
        )
        st.markdown(
            "<div style='text-align:center; color:gray; font-size:0.85rem; margin-top:0.35rem;'>Figure 4. EV Charging Station Accessibility Change (Log Ratio) with Future Stations Illinois Census Tracts. Blue shades indicate improved accessibility, red shades indicate reduced accessibility relative to demand.</div>",
            unsafe_allow_html=True,
        )

def render_13():
    st.markdown('<div id="appendix-13"></div>', unsafe_allow_html=True)
    st.markdown("#### Electrified VMT Coverage")

    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go

    raw_path = "data/incremental_results_raw_副本.csv"  # raw 10-run results
    df = pd.read_csv(raw_path)

    # Mean across 10 runs for each N (matches lead's instruction)
    agg = (
        df.groupby("N")
          .agg(
              mean_vmt=("vmt_coverage_%", "mean"),
              std_vmt=("vmt_coverage_%", "std"),
              n_runs=("repeat", "nunique"),
          )
          .reset_index()
          .sort_values("N")
    )

    # --- Fitted curve from the figure (in %) ---
    # y = 0.75 ln(x) + 93.1  (ln(0) undefined, so draw curve for x >= 1)
    x_curve = np.arange(1, int(agg["N"].max()) + 1)
    y_curve = 0.75 * np.log(x_curve) + 93.1

    # --- Plot ---
    fig = go.Figure()

    # Gray hollow points (mean values)
    fig.add_trace(go.Scatter(
        x=agg["N"],
        y=agg["mean_vmt"],
        mode="markers",
        name="Simulation mean (10 runs)",
        marker=dict(
            size=8,
            color="white",  # white fill
            line=dict(color="rgba(140,140,140,1)", width=2),  # gray outline
        ),
        hovertemplate=(
            "N: %{x}<br>"
            "Mean VMT coverage: %{y:.3f}%<br>"
            "Std (10 runs): %{customdata[0]:.3f}<br>"
            "Runs: %{customdata[1]}<extra></extra>"
        ),
        customdata=np.column_stack([
            agg["std_vmt"].fillna(0),
            agg["n_runs"],
        ]),
        showlegend=False,  # to match static figure
    ))

    # Black fitted curve
    fig.add_trace(go.Scatter(
        x=x_curve,
        y=y_curve,
        mode="lines",
        line=dict(color="black", width=3),
        hovertemplate="Fitted curve<br>N: %{x}<br>VMT coverage: %{y:.3f}%<extra></extra>",
        showlegend=False,
    ))

    # Red baseline dot: use N=0 if it exists, otherwise first N
    if (agg["N"] == 0).any():
        base_row = agg.loc[agg["N"] == 0].iloc[0]
        x0, y0 = 0, float(base_row["mean_vmt"])
    else:
        base_row = agg.iloc[0]
        x0, y0 = int(base_row["N"]), float(base_row["mean_vmt"])

    fig.add_trace(go.Scatter(
        x=[x0],
        y=[y0],
        mode="markers",
        marker=dict(size=12, color="red"),
        hovertemplate="Baseline<br>N: %{x}<br>VMT coverage: %{y:.3f}%<extra></extra>",
        showlegend=False,
    ))

    # Equation + R^2 annotation (positioned like the figure)
    fig.add_annotation(
        x=350, y=94.2,  # tweak if you want exact placement
        text="y=0.75ln(x)+93.1<br>R<sup>2</sup>=0.8132",
        showarrow=False,
        font=dict(color="rgba(80,80,80,1)", size=14),
        align="left",
    )

    # Layout to mimic the static plot
    fig.update_layout(
        template="plotly_white",
        height=560,
        margin=dict(l=80, r=40, t=10, b=70),
        xaxis=dict(
            title="Number of Charging Stations",
            range=[-10, max(agg["N"].max(), 800) + 20],
            showgrid=True,
            gridcolor="rgba(220,220,220,1)",
            zeroline=False,
        ),
        yaxis=dict(
            title="VMT Coverage (%)",
            range=[93, 101],  # matches figure's look
            showgrid=True,
            gridcolor="rgba(220,220,220,1)",
            zeroline=False,
        ),
    )

    st.plotly_chart(fig, width="stretch")

    st.caption("Figure 5. Electrified VMT coverage relationship used to quantify mobility impacts of DCFC expansion.")

def render_14():
    st.markdown('<div id="appendix-14"></div>', unsafe_allow_html=True)
    # Baseline values
    v_baseline = 0.50
    r_baseline = 7.0
    R_baseline = 250
    N_baseline = 348

    v_value = st.slider("Value per mile (v), $/mi", 0.25, 0.64, v_baseline, 0.01)
    v_is_baseline = abs(v_value - v_baseline) < 0.001
    st.markdown(
        f"<div style='font-size:0.75rem; color:{'#d83404' if not v_is_baseline else '#666'}; margin-top:-0.5rem; margin-bottom:0.5rem;'>"
        f"{'🔴 Baseline: ' if not v_is_baseline else 'Baseline: '}${v_baseline:.2f}/mi</div>",
        unsafe_allow_html=True
    )

    r_percent = st.slider("Discount rate (r), %", 3.0, 10.0, r_baseline, 0.5)
    r = r_percent / 100.0
    r_is_baseline = abs(r_percent - r_baseline) < 0.01
    st.markdown(
        f"<div style='font-size:0.75rem; color:{'#d83404' if not r_is_baseline else '#666'}; margin-top:-0.5rem; margin-bottom:0.5rem;'>"
        f"{'🔴 Baseline: ' if not r_is_baseline else 'Baseline: '}{r_baseline:.1f}%</div>",
        unsafe_allow_html=True
    )

    # BEV range (R) is fixed at baseline value of 250 miles
    R_value = R_baseline  # Fixed at 250 miles

    N_current = st.slider("Current DCFC stations (N)", 50, 500, N_baseline, 1)
    N_is_baseline = abs(N_current - N_baseline) < 1
    st.markdown(
        f"<div style='font-size:0.75rem; color:{'#d83404' if not N_is_baseline else '#666'}; margin-top:-0.5rem; margin-bottom:0.5rem;'>"
        f"{'🔴 Baseline: ' if not N_is_baseline else 'Baseline: '}{N_baseline} stations</div>",
        unsafe_allow_html=True
    )

    N_BEVs_base = 94303

    N_grid = np.arange(1, 501)

    wtp_base = calculate_WTP(N_grid, v=v_value, r=r, R=R_value)
    wtp_low  = calculate_WTP(N_grid, v=0.35,   r=r, R=R_value)
    wtp_high = calculate_WTP(N_grid, v=0.64,   r=r, R=R_value)

    per_base = wtp_base / N_BEVs_base
    per_low  = wtp_low  / N_BEVs_base
    per_high = wtp_high / N_BEVs_base

    per_current = float(calculate_WTP(N_current, v=v_value, r=r, R=R_value) / N_BEVs_base)
    per_current_low  = float(calculate_WTP(N_current, v=0.35, r=r, R=R_value) / N_BEVs_base)
    per_current_high = float(calculate_WTP(N_current, v=0.64, r=r, R=R_value) / N_BEVs_base)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=N_grid,
        y=per_base,
        mode="lines",
        name=f"Base (v=${v_value:.2f}/mi)",
        line=dict(color=UIUC_BLUE, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=N_grid,
        y=per_high,
        mode="lines",
        name="High (v=$0.64/mi)",
        line=dict(dash="dash", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=N_grid,
        y=per_low,
        mode="lines",
        name="Low (v=$0.35/mi)",
        line=dict(dash="dash", width=2, color="#2ECC71")
    ))

    fig.add_trace(go.Scatter(
        x=np.concatenate([N_grid, N_grid[::-1]]),
        y=np.concatenate([per_high, per_low[::-1]]),
        fill="toself",
        fillcolor="rgba(232, 74, 39, 0.18)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Sensitivity range",
        showlegend=True,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[N_current], y=[per_current],
        mode="markers",
        name=f"Current (N={N_current})",
        marker=dict(size=12, color="red")
    ))

    fig.add_annotation(
        x=N_current, y=per_current,
        text=f"Current N={N_current}<br>${per_current:,.0f}/BEV",
        showarrow=True,
        arrowhead=2,
        ax=60, ay=-40,
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="rgba(232, 74, 39, 0.9)",
        borderwidth=1
    )

    fig.update_layout(
        title=dict(text="WTP per Traveler vs DCFC Stations (Illinois)", font=dict(size=22, color="#E8572A"), pad=dict(b=20)),
        xaxis_title=dict(text="Number of DCFC Stations (N)", font=dict(size=16)),
        yaxis_title=dict(text="WTP per Traveler ($/BEV)", font=dict(size=16)),
        xaxis=dict(tickfont=dict(size=13)),
        yaxis=dict(tickfont=dict(size=13)),
        template="plotly_white",
        height=560,
        margin=dict(l=80, r=40, t=130, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12)
        )
    )

    st.plotly_chart(fig, width="stretch")
    
    st.caption(f"Scenario settings: r={r_percent:.1f}%, R={R_baseline} mi (fixed)")

    # Updated Range Display for Section 1.4
    c1, c2, c3 = st.columns(3)

    # 1. Main Metric
    c1.metric("Current WTP / traveler (base)", f"${per_current:,.0f}")

    # 2. Cleaned Range (Removing the green box)
    with c2:
        st.markdown(f"**Range**")
        st.markdown(
            f"<div style='font-size: 1.8rem; font-weight: 400; color: var(--illini-blue); margin-top: -10px;'>"
            f"[ ${per_current_low:,.0f} – ${per_current_high:,.0f} ]"
            f"</div>", 
            unsafe_allow_html=True
        )

    # 3. Discount Factor
    c3.metric("Discount factor D (15y)", f"{calculate_discount_factor(r, 15):.2f}")


# ── Main body: overview, then each section (text + visual together) ─────────
render_overview()

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
render_11_text()
render_11()

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
render_12_text()
render_12()

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
render_13_text()
render_13()

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
render_14_text()
render_14()

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(to right, #f7f9fc 0%, #ffffff 50%, #f7f9fc 100%);'>
<div style='text-align: center; color: gray; font-size: 0.9rem;'>
    Illinois EV Charging Infrastructure Dashboard | University of Illinois at Urbana-Champaign<br>
    Data Sources: ACS 2023, AFDC, Illinois DOT
""", unsafe_allow_html=True)
st.markdown('<div class="uiuc-orange-bar"></div>', unsafe_allow_html=True)
