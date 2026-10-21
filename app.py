"""
Illinois EV Charging Infrastructure Dashboard
=============================================
A web-based interactive dashboard for analyzing EV charging accessibility,
VMT coverage, and willingness to pay for DCFC infrastructure.

Sections:
- 1.1 Income Analysis (Static maps)
- 1.2 Gap and Accessibility Analysis (Static maps + Formula)
- 1.3 Electrified Miles Estimation
- 1.4 Willingness to Pay for the DCFC Network (per BEV, with sensitivity controls)
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
# WTP MODEL (DCFC network; single-pass minimum-detour, Greene Eq. 17)
# Source: dcfc_wtp_detour_rerun_with_delta_curves notebook (final results).
# WTP per BEV = Delta_M * net_per_mile * D(r,15) / N_passenger
# =============================================================================

UIUC_BLUE = "#122a4b"
UIUC_ORANGE = "#d83404"

WTP_VOT = 20.0            # value of time, $/hr (w)
WTP_KWH_PER_MI = 0.32     # energy use, kWh/mi (e)
WTP_DCFC_KW = 150.0       # DCFC power, kW (d)
WTP_DETOUR_MPH = 35.0     # detour speed, mph (u)
WTP_N_PASSENGER = 7.1e6   # passenger vehicles behind the OD matrix
WTP_T_YEARS = 15
WTP_C_CHARGE_BASE = WTP_VOT * WTP_KWH_PER_MI / WTP_DCFC_KW   # $/mi before s_DCFC

# Per detour buffer delta (mi): enabled annual VMT (Delta_M), share of enabled
# miles beyond initial range (s_DCFC), and VMT-weighted detour ratio (r_detour).
WTP_BY_DELTA = {
    0.1:  dict(dM=3_977_954_439.870156, s_dcfc=0.2518, r_detour=2.8665456149012626e-05),
    1.0:  dict(dM=6_638_038_558.212712, s_dcfc=0.2545, r_detour=0.0007106584171871601),
    2.0:  dict(dM=7_933_392_364.061326, s_dcfc=0.2640, r_detour=0.0013929199176437846),
    5.0:  dict(dM=8_538_373_381.510010, s_dcfc=0.2645, r_detour=0.002024709336412145),
    10.0: dict(dM=8_750_067_762.593248, s_dcfc=0.2651, r_detour=0.002619178576543419),
}
WTP_BASE = dict(v=0.50, r=0.03, delta=2.0)   # headline case (matches final slide)


def calculate_discount_factor(r, T=WTP_T_YEARS):
    """D(r,T) = sum_{t=1..T} (1+r)^-t, rounded to 2 dp as in the notebook (11.94 at 3%)."""
    return round((1 - (1 + r) ** -T) / r, 2)


def wtp_net_per_mile(v, delta):
    p = WTP_BY_DELTA[delta]
    c_charge = WTP_C_CHARGE_BASE * p["s_dcfc"]
    c_detour = (WTP_VOT / WTP_DETOUR_MPH) * p["r_detour"]
    return v - c_charge - c_detour, c_charge, c_detour


def wtp_per_bev(v=WTP_BASE["v"], r=WTP_BASE["r"], delta=WTP_BASE["delta"], D=None):
    net, _, _ = wtp_net_per_mile(v, delta)
    D = calculate_discount_factor(r) if D is None else D
    return WTP_BY_DELTA[delta]["dM"] * net * D / WTP_N_PASSENGER


# Expected random-prefix VMT coverage curve (delta = 2 mi, multi-charge rule "all")
COVERAGE_CURVE_CSV = "data/coverage/delta_coverage_curves_all.csv"
COVERAGE_FITS_CSV = "data/coverage/delta_coverage_curve_fits_all.csv"
COVERAGE_DELTA = 2


@st.cache_data
def load_coverage_curve(delta=COVERAGE_DELTA):
    """Return (curve_df, fit_row). curve_df: N_stations, coverage_pct, enabled_vmt (annual)."""
    cur = pd.read_csv(COVERAGE_CURVE_CSV)
    cur = cur[cur["delta_mi"] == delta].sort_values("N_nodes").copy()
    cur["N_stations"] = cur["N_stations_equiv"]
    cur["coverage_pct"] = cur["vmt_coverage_pct"]
    cur["enabled_vmt"] = cur["single_expected_vmt"] + cur["multi_expected_vmt"]
    fit = pd.read_csv(COVERAGE_FITS_CSV)
    fit = fit[fit["delta_mi"] == delta].iloc[0]
    return cur[["N_nodes", "N_stations", "coverage_pct", "enabled_vmt"]].reset_index(drop=True), fit

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
<p style="margin: 0.2rem 0 0.6rem 0;"><b>1.4.</b> Willingness to pay: the value of DCFC access per battery EV</p>
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
Next, we asked how much the DCFC network expands what a battery EV can do. Without any public
fast charging, trips within a vehicle's starting range are already feasible; they cover
<b>94.57%</b> of annual Illinois VMT and form the baseline. Each added DCFC station makes some
longer trips feasible (within a 2-mile detour), and the miles from those newly enabled trips are
<b>electrified miles</b>.
<br><br>
The curve shows expected VMT coverage when stations are added in random order, up to today's
348 DCFC stations (99.19%). It follows $f(N) = 94.57 + 1.76\\ln(1 + N/27.9)$ ($R^2 = 0.9999$):
the first stations unlock the busiest corridors, and later additions add less because the
easy wins are already captured.
""", unsafe_allow_html=True)


def render_14_text():
    st.markdown('<div id="section-14"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">1.4 Willingness to Pay for the DCFC Network (Per BEV)</div>',
                unsafe_allow_html=True)
    st.markdown("""
We value the Illinois DCFC network by the trips it makes feasible for battery EVs. For every
origin–destination trip longer than a vehicle's starting range, we find the charging station that
requires the smallest detour; the trip counts as <b>enabled</b> if that detour is within a buffer
δ (2 miles in the base case). Enabled annual VMT is valued at <i>v</i> per mile, net of charging-time
and detour costs, discounted over a 15-year vehicle lifetime, and expressed per vehicle.
""", unsafe_allow_html=True)
    st.latex(r"\text{WTP per BEV} = \frac{\Delta M \cdot (v - C_{\text{charge}} - C_{\text{detour}}) \cdot D(r, 15)}{N_{\text{passenger}}}")


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

                # Illinois-centred Transverse Mercator so the state is upright (UTM 16N tilts it)
                IL_TM = ("+proj=tmerc +lat_0=36.5 +lon_0=-89.25 +k=1 "
                         "+x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
                tracts_lr = tracts_lr.to_crs(IL_TM)
                future_gdf_m = future_gdf_m.to_crs(IL_TM)
                if roads_gdf is not None:
                    roads_gdf = roads_gdf.to_crs(IL_TM)

                # Portrait canvas, equal aspect: Illinois is taller than wide
                fig_lr, ax_lr = plt.subplots(1, 1, figsize=(6.2, 7), dpi=200)
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
                cax = ax_lr.inset_axes([1.02, 0.05, 0.035, 0.38])
                cbar = fig_lr.colorbar(sm, cax=cax)
                cbar.ax.tick_params(labelsize=7)
                cbar.set_label("Log ratio change", fontsize=7.5)
                legend_patches = [mpatches.Patch(color=no_data_grey, edgecolor="none", label="No data")]
                if roads_gdf is not None and len(roads_gdf) > 0:
                    legend_patches.append(mpatches.Patch(color=interstate_dark_grey, edgecolor="none", label="Interstate Routes"))
                for t in type_order:
                    if len(future_gdf_m[future_gdf_m["station_type"] == t]) > 0:
                        legend_patches.append(mpatches.Patch(color=point_colors.get(t, "gray"), label=t))
                # Legend to the right of the map, above the colorbar
                ax_lr.legend(
                    handles=legend_patches,
                    loc="upper left",
                    bbox_to_anchor=(1.0, 0.98),
                    frameon=False,
                    fontsize=7.5,
                    handlelength=1.0,
                    labelspacing=0.6,
                )
                ax_lr.set_aspect("equal")
                ax_lr.margins(x=0.02, y=0.02)
                ax_lr.set_axis_off()
                fig_lr.subplots_adjust(left=0.01, right=0.68, top=0.99, bottom=0.01)
                # Display at ~50% of container width
                _lc, _lm, _lr = st.columns([0.25, 0.50, 0.25])
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

    curve, fit = load_coverage_curve()
    a_fit, b_fit, c_fit = float(fit["baseline_pct"]), float(fit["b_stations"]), float(fit["c_stations"])
    r2 = float(fit["r_squared_nodes"])
    n_max = float(curve["N_stations"].max())

    # Marker points at the same network sizes as the notebook figure
    pts = curve[curve["N_nodes"].isin([1, 2, 3, 5, 10, 20, 50, 100, 150, 200, int(curve["N_nodes"].max())])]
    x_fit = np.linspace(0, n_max, 400)
    y_fit = a_fit + b_fit * np.log1p(x_fit / c_fit)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, n_max * 1.06], y=[a_fit, a_fit], mode="lines",
        line=dict(color="rgba(140,140,140,1)", width=1.5, dash="dash"),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode="lines", line=dict(color="black", width=3),
        hovertemplate="Fitted curve<br>N: %{x:.0f}<br>VMT coverage: %{y:.3f}%<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=pts["N_stations"], y=pts["coverage_pct"], mode="markers",
        marker=dict(size=8, color="white", line=dict(color="rgba(140,140,140,1)", width=2)),
        hovertemplate="N: %{x:.0f}<br>Expected VMT coverage: %{y:.3f}%<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[a_fit], mode="markers", marker=dict(size=12, color="red"),
        hovertemplate="Baseline (no public DCFC)<br>VMT coverage: %{y:.2f}%<extra></extra>",
        showlegend=False,
    ))
    fig.add_annotation(
        x=n_max * 0.97, y=a_fit + 0.55, xanchor="right",
        text=f"y = {a_fit:.2f} + {b_fit:.2f} ln(1 + N/{c_fit:.1f})<br>R<sup>2</sup> = {r2:.4f}",
        showarrow=False, font=dict(color="rgba(80,80,80,1)", size=14), align="right",
    )
    fig.add_annotation(
        x=n_max * 0.97, y=a_fit + 0.12, xanchor="right", text=f"baseline = {a_fit:.2f}%",
        showarrow=False, font=dict(color="rgba(120,120,120,1)", size=12),
    )
    fig.update_layout(
        template="plotly_white",
        height=560,
        margin=dict(l=80, r=40, t=10, b=70),
        xaxis=dict(title="Number of DCFC Stations", range=[-8, n_max * 1.08],
                   showgrid=True, gridcolor="rgba(220,220,220,1)", zeroline=False),
        yaxis=dict(title="VMT Coverage (%)", range=[94, 100],
                   showgrid=True, gridcolor="rgba(220,220,220,1)", zeroline=False),
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Figure 5. Expected electrified VMT coverage vs. number of DCFC stations (2-mile detour buffer; "
               "a multi-stop trip counts only when all of its charging stops are in the network).")


def render_14():
    st.markdown('<div id="appendix-14"></div>', unsafe_allow_html=True)
    # Baseline values (final results)
    v_baseline = WTP_BASE["v"]
    r_baseline = WTP_BASE["r"] * 100
    delta = WTP_BASE["delta"]

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

    # Expected enabled VMT along the coverage curve (delta = 2 mi, rule "all"), up to today's network
    curve, _ = load_coverage_curve(COVERAGE_DELTA)
    N_grid = curve["N_stations"].values
    dM_grid = curve["enabled_vmt"].values
    N_current = int(round(N_grid.max()))          # 348 DCFC stations
    D = calculate_discount_factor(r)

    def per_bev(v):
        net, _, _ = wtp_net_per_mile(v, delta)
        return dM_grid * net * D / WTP_N_PASSENGER

    per_base = per_bev(v_value)
    per_low = per_bev(0.35)
    per_high = per_bev(0.64)
    per_current, per_current_low, per_current_high = per_base[-1], per_low[-1], per_high[-1]

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
        ax=-90, ay=60,
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="rgba(232, 74, 39, 0.9)",
        borderwidth=1
    )

    fig.update_layout(
        title=dict(text="WTP per BEV vs DCFC Stations (Illinois)", font=dict(size=22, color="#E8572A"), pad=dict(b=20)),
        xaxis_title=dict(text="Number of DCFC Stations (N)", font=dict(size=16)),
        yaxis_title=dict(text="WTP per BEV ($/BEV)", font=dict(size=16)),
        xaxis=dict(tickfont=dict(size=13), range=[0, N_current * 1.08]),
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

    st.caption(f"Scenario settings: r={r_percent:.1f}%, detour buffer δ={delta:g} mi (fixed), "
               f"15-year lifetime. Curve follows the expected VMT coverage in 1.3.")

    c1, c2, c3 = st.columns(3)

    # 1. Main Metric
    c1.metric("Current WTP / BEV (base)", f"${per_current:,.0f}")

    # 2. Range
    with c2:
        st.markdown(f"**Range**")
        st.markdown(
            f"<div style='font-size: 1.8rem; font-weight: 400; color: var(--illini-blue); margin-top: -10px;'>"
            f"[ ${per_current_low:,.0f} – ${per_current_high:,.0f} ]"
            f"</div>",
            unsafe_allow_html=True
        )

    # 3. Discount Factor
    c3.metric("Discount factor D (15y)", f"{D:.2f}")


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
