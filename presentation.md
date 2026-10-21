# R27-280 Half-Year Report — Full Content Extraction
**Source:** ict27-280_halfyear_report-ek-172025.pptx (January 7th, 2025 Update)

---

## Slide 1: Title

**Economic, Environmental, and Equity Outcomes Assessment of the Electric Vehicle Charging Network Expansion in Illinois**
**R27-280**

- **PI:** Eleftheria (Ria) Kontou, PhD — Assistant Professor, Civil and Environmental Engineering, University of Illinois Urbana-Champaign
- **Joint work with:** Sijia Li, MSc student
- **Date:** January 7th, 2025 Update

---

## Slide 2: R27-280 Objectives

(1) Estimate the worth of IL EV charging network to IL EV drivers

(2) Economic impact assessment, estimating holistic IL benefits associated with job creation, increased local investments, consumer demand growth in local businesses, drivers' total ownership cost savings from EV ownership

(3) Lifecycle assessment modeling to estimate reductions in air pollutants and emissions from increased light-duty vehicle mile electrification in Illinois

(4) Equity analytics, devising metrics for assessing the impacts of charging deployment across socioeconomic and urban/rural categories as well as in disadvantaged communities (e.g., based on poverty metrics, energy burden, etc.)

(5) Identify best locations for DC fast charger deployment based on usage and benefits to communities

(6) Impact of changes in policymaking and funding allocation on public charger buildout

---

## Slide 3: Task 1 Overview — Tasks 1.1 & 1.2

### Task 1: Value of EV Charging to EV Users in IL

#### Task 1.1 — Data Collection & Integration
- Existing chargers, EV registrations, new NEVI stations, traffic on interstates, policies, etc.

#### Task 1.2 — DCFC Coverage Gaps
- Network-based service area modeling and spatial clustering methods to identify regions that lack adequate access to charging infrastructure
- Visual: Y 2022 IL Charger Inaccessibility (%) map shown (county-level choropleth with intensity gradient 0.00–1.00)
- Reference: Project report: https://doi.org/10.36501/0197-9191/22-023

---

## Slide 4: Task 1 Overview — Tasks 1.3 & 1.4

#### Task 1.3 — Electrified Miles Estimation
- Estimating heterogeneous travel patterns and calculating additional vehicle miles that become electrified due to increased charging deployment, particularly in rural areas (Greene et al. 2020)
- Visual: Graph from Greene et al. (2020) showing "Annual vehicle miles traveled with a battery EV as a function of DC Fast Charging stations in Seattle WA"
  - Reference: https://doi.org/10.1016/j.trd.2019.11.011
  - Formula shown: y = 330.13ln(x) + 8741.2, R² = 0.9807
  - X-axis: DCFC Station Count (0–100); Y-axis: Annual Vehicle Miles (9300–10300)

#### Task 1.4 — Worth of EV Charging to EV Drivers in IL
- Translating additional electrified miles enabled to EV drivers' value in IL

---

## Slide 5: Progress Status

| Task | Description | Status |
|------|-------------|--------|
| Task 1.1 | Data Collection and Integration | ✔ Completed |
| Task 1.2 | Gap and Accessibility Analysis | ✔ Completed (inaccessibility framework with spillover capacity) |
| Task 1.3 | Electrified Miles Estimation | ✔ Completed |
| Task 1.4 | Worth of EV Charging to Illinois EV Drivers | ✔ Completed |
| Task 2.1 | Economic Impact Assessment Framework | Ongoing |

---

## Slide 6: Data Resources

### Geospatial Layers & Shapefiles
**U.S. Census TIGER/Line Shapefiles**
- State, county, place, and census tract boundaries
- Primary & secondary road centerlines

**Illinois GIS / IDOT Open Data**
- Statewide boundary layers
- Transportation and roadway reference layers

**Geographic Crosswalks**
- Tract–county and place–county crosswalk files
- Used for spatial aggregation and reporting consistency

*Used for spatial joins, network construction, and aggregation across all tasks.*

### Charging Infrastructure Data
**DOE Alternative Fuels Data Center (AFDC)**
- Public charging station locations
- Charger type and power (L2 vs DCFC)

**NEVI & Illinois State Programs**
- NEVI Round 1 site lists and planning documents
- Illinois EPA / IDOT charging investment records

### Mobility, Travel & Network Data
- Illinois statewide origin–destination (OD) travel demand — from previous project
- Road network topology and shortest-path routing (OSM)

### Vehicle Performance & Behavioral Parameters
**EPA / DOE (fueleconomy.gov)**
- Vehicle efficiency and range characteristics

**Greene et al. (2020)**
- Charging behavior and valuation parameters
- Used as reference values with sensitivity analysis

---

## Slide 7: Task 1.1 — Example Data & Visualizations

**Current and planned EV charging stations**
- Source: https://afdc.energy.gov/stations

Two maps shown:
1. **All EV Charging Stations (Size = Number of Ports)**
   - Existing: 1,559 stations
   - Future/New: 403 stations
   - Plotted by latitude (37–42) and longitude (–91 to –87)

2. **Future/New Stations by Charging Level**
   - Future DC Fast: 351 stations
   - Future Level 2: 52 stations
   - Plotted by latitude and longitude across Illinois

---

## Slide 8: Task 1.2 — Gap and Accessibility Analysis (Framework)

**Objective:** Assess whether charging infrastructure can meet local EV demand at the census-tract level.

### Key Quantities
- **T_j**: charging service capacity in tract j
- **V_j**: local EV demand in tract j

### Accessibility Index Formula

$$A_j = \frac{T_j - V_j}{V_j + T_j}$$

### Interpretation
- **A_j ≈ 0**: supply and demand are balanced
- **A_j > 0**: charging capacity exceeds local demand
- **A_j < 0**: charging demand exceeds available capacity (accessibility gap)

*Reference: "Electric Vehicle Infrastructure Plan (2022). https://doi.org/10.36501/0197-9191/22-023*

---

## Slide 9: Task 1.2 — Gap and Accessibility Analysis (Map Results)

**Current Charging Accessibility (Accessibility Index)**

Map shown: **EV Charging Station Accessibility (A), Illinois Census Tracts, 2025**

### Metric
- A_j compares local EV charging demand with available charging service capacity
- Higher A_j indicates better charging accessibility
- Lower A_j indicates a larger mismatch between demand and capacity

### Purpose
This map identifies where charging gaps currently exist, providing a baseline for evaluating future infrastructure deployment.

**Legend categories:**
- Strong Spillover Capacity (A>0): IA –1.00 to –0.70
- Moderate Spillover Capacity (A>0): IA –0.70 to –0.38
- Mid Spillover Capacity (A>0): IA –0.38 to 0.00
- Mild Undersupply (A<0): IA 0.00 to 0.34
- Moderate Undersupply (A<0): IA 0.34 to 0.73
- Severe Undersupply (A<0): IA 0.73 to 1.00
- Missing Data
- Illinois Interstate Routes

---

## Slide 10: Task 1.2 — Gap and Accessibility Analysis (Scenario Comparison)

**Scenario comparison:** Accessibility under the future charging network (AFDC Planned stations added) relative to the current network

### Accessibility Change Metric

$$\Delta\log A = \ln\left(\frac{A_{future}}{A_{current}}\right)$$

### Interpretation (unitless)
- **ΔlogA > 0**: charging accessibility improves with future stations
- **ΔlogA ≈ 0**: little or no accessibility change
- **ΔlogA < 0**: limited or uneven accessibility improvement relative to demand

Map shown: **EV Charging Station Accessibility Change (Log Ratio) with Future Stations, Illinois Census Tracts**
- Color scale: –2.0 to +2.0 (Log Ratio Change)
- Overlaid: Improved accessibility (Δlog_r > 0), No change (Δlog_r = 0), Reduced accessibility (Δlog_r < 0)
- Station markers: Level 3 Fast Charging Stations, Level 2 Charging Stations, Mixed L2/L3 Stations

---

## Slide 11: Task 1.3 — Electrified Miles Estimation (Overview)

### Workflow Diagram

```
OD Travel Demand
        ↓
Shortest-Path Routing on IL Road Network
        ↓
Charging Feasibility Check
  • Vehicle range & reserve
  • Public charging availability
        ↓
Feasible BEV Trips
        ↓
Electrified VMT
(sum of miles from the feasible trips)
```

### Definition
**Electrified VMT** is defined as the total vehicle miles traveled from trips that are feasible to complete using a battery electric vehicle, given public charging availability and network constraints.

---

## Slide 12: Task 1.3 — Electrified Miles Estimation (Data Inputs)

### Data Inputs (Illinois-specific)

**Travel Demand**
- Illinois OD trips (statewide)
- Trip distance on road network: shortest path assumption

**Infrastructure**
- Public DC fast charging stations (baseline + scenarios)

**Electric Vehicles**
- Nominal BEV driving range assumed to be **250 miles**, consistent with current U.S. BEV makes and models characteristics
- Public DC fast charging sessions assumed to reach **~80% state-of-charge**, reflecting observed charging behavior and time penalties
- Initial available range at a trip's origin varies by home charging access, which is correlated with income and housing characteristics
- Charging behavior is simplified to emphasize trip feasibility under DCFC infrastructure constraints

*References: Greene et al. (2020); Borlaug et al. (2018); Nicholas et al. (2019); Guo & Kontou (2021)*

---

## Slide 13: Task 1.3 — Electrified Miles Estimation (Modeling Steps)

### Modeling Steps
1. Assign OD trips to shortest-path routes
2. Check trip feasibility under charging constraints
3. Identify infeasible trips requiring public charging
4. Incrementally add charging stations
5. Recompute feasible VMT → generate electrified VMT curve

Visual: Diagram showing individual trips going through trip-level feasibility check (checkmarks and X marks), producing aggregated Electrified VMT bar.

---

## Slide 14: Task 1.3 — Electrified Miles Estimation (Illinois VMT Curve)

### Illinois Electrified VMT Curve Results

Graph: X-axis = Number of Charging Stations (0–800); Y-axis = VMT Coverage (%) (93–101)
- Fitted curve formula: **y = 0.75ln(x) + 93.1**, R² = 0.8132
- Red dot at baseline (N=1, VMT Coverage ≈ 94.something%)
- Curve shows logarithmic saturation behavior

### Key Findings
- The relationship between charging deployment and electrified VMT is **highly nonlinear**
- **Early additions** of charging stations unlock disproportionately large gains in electrified miles
- As the network becomes denser, marginal gains diminish, indicating **decreasing returns** to additional stations

---

## Slide 15: Task 1.4 — Worth of EV Charging to IL EV Drivers (Framework)

### Three-Stage Framework

| Stage 1 | Stage 2 | Stage 3 |
|---------|---------|---------|
| Infrastructure Deployment | Mobility Enablement | Economic Valuation |
| Charging deployment: Public charging stations, Charger type (DCFC), Spatial coverage & network | Electrified VMT (Task 1.3): Feasible EV Trips, Additional Electric Miles | Economic Benefits (Task 1.4): Fuel Cost Savings, Time & Detour Savings, Monetized User Benefits ($) |
| Supply: Public-Private Investment | User: Electric Mileage | User: Benefit and Value! |

- **Task 1.3** quantifies *how many additional miles can be electrified*
- **Task 1.4** quantifies *what those additional electrified miles are worth*
- **Focus: direct benefits to Illinois EV drivers**

---

## Slide 16: Task 1.4 — Worth of EV Charging to IL EV Drivers (Conceptual Framework)

**Conceptual Framework: From Electrified VMT to Economic Value**

### Fuel Cost Savings
- Gasoline cost avoided
- Electricity cost incurred
- Net fuel savings per electrified mile

### Time & Detour Cost Savings
- Reduced detours to refuel
- Reduced charging-related travel deviations
- Value-of-time applied to saved minutes

### Charging Access Value
- Additional feasible long-distance trips
- Particularly important for corridor and rural travel

### WTP Formula

$$WTP = \left[(\alpha_0 + \alpha_1 \ln(I_j))(e^{-b(R-R_0)})m_j\left(v_j - \frac{w_j}{\partial R_i}\left(K(\phi^a - 1) + \frac{\partial R_i e_i}{d}\right)\right)\right]D_j$$

*Parameter values follow Greene et al. (2020); Illinois-specific travel inputs are derived from Task 1.3.*

---

## Slide 17: Task 1.4 — Worth of EV Charging to IL EV Drivers (Key Outcomes)

### Key Outcomes (Illinois, Inter-regional DCFC)

**Findings:**
- Electrified inter-regional VMT increases **logarithmically** with DCFC deployment
- Early stations generate **disproportionately large benefits**
- **Marginal value declines** as the network densifies

> **At current deployment (N = 348): +1 DCFC station ⇒ ≈ $39.15M statewide, or ≈ $415 per BEV driver (average)**

### Two Graphs Shown:

**Graph 1 — Inter-regional Electrified VMT Coverage vs DCFC Stations (Illinois)**
- Fitted formula: f(N) = 93.22 + 0.75·ln(N), R² = 0.8488
- Total inter-regional VMT: 4.31B miles/year
- Baseline coverage (N=1): 93.22%
- Current coverage (N=348): 97.61%
- Enabled coverage: 4.39%
- N = 348 marked at 97.61%

**Graph 2 — Enabled VMT vs DCFC Infrastructure Relative to Baseline (N=1)**
- Y-axis: Annual Enabled Inter-regional VMT (billion miles)
- X-axis: Number of Physical DCFC Stations (N), 0–500
- Key points:
  - N=100: 0.1498 billion miles
  - N=300: 0.1718 billion miles
  - N=348 (Current): ~0.1895 billion miles
- Calculation: ΔVMT = [f(N) - f(1)] × M, where M = 4.31B miles/year
- Current enabled VMT = 0.189 billion miles/year = 4.39% of total VMT

---

## Slide 18: Task 1.4 — Worth of EV Charging to IL EV Drivers (Economic Value)

### Economic Value of DCFC Deployment to Illinois EV Drivers

**Chart title:** Willingness to Pay per Traveler for Inter-regional DCFC Infrastructure — Illinois BEV Fleet (N=94,303 vehicles, R=250mi)

**Parameters shown:**
- M = 4.31B mi/yr
- D = 9.11 (r=7%, 15yr)
- R = 250 miles
- N_BEVs = 94,303

**Current Infrastructure result:**
- N = 348 stations
- WTP = $8,611 per BEV
- Range: [$5,870 – $11,170]

**Legend:**
- Base (v=$0.50/mi) — solid line
- High (v=$0.64/mi) — upper dashed line
- Low (v=$0.35/mi) — lower dashed line
- Sensitivity range — shaded band
- Current (N=348) — red dot

### Summary Result

> **Total WTP (N = 348): ≈ $0.8 billion (range: $0.55B – $1.05B)**

BEVs are assumed to represent approximately **65%** of the Illinois plug-in EV passenger vehicles, consistent with national estimates reported by the U.S. DOE Alternative Fuels Data Center.

---

## Slide 19: Task 1.4 — Worth of EV Charging to IL EV Drivers (Sensitivity Analysis)

Two 3D surface plots showing WTP sensitivity:

### a) WTP Sensitivity to Value per Mile (v)
- **Base case:** r=7%, R=250mi, K=0.1536hr
- X-axis: Value per Mile ($/mi), range 0.35–0.65
- Y-axis: Number of DCFC Stations (N), range 0–500
- Z-axis: WTP ($ Billions), range 0.0–1.0+
- Color scale: blue (low) → red (high)
- Red dot: Current (N=348)

### b) WTP Sensitivity to Discount Rate (r)
- **Base case:** v=$0.50/mi, R=250mi, K=0.1536hr
- X-axis: Discount Rate (%), range 3–10
- Y-axis: Number of DCFC Stations (N), range 0–500
- Z-axis: WTP ($ Billions), range 0.0–1.0+
- Color scale: blue (low) → red (high)
- Red dot: Current (N=348)

*M = 4.31 billion mi/yr | Vehicle lifetime: 15 years | Greene et al. (2020) Equation 17*

---

## Slide 20: Anticipated Work Next Quarter

**Task 2.1:** Develop an Illinois-specific economic impact assessment framework for EV charging investments, linking infrastructure deployment to employment and regional economic outcomes

**Task 2.2:** Prepare preliminary results and scenarios to support stakeholder feedback and virtual townhall discussions
- Compile county-level economic, employment, and infrastructure investment data
- Generate initial statewide and regional economic impact estimates

---

## Slide 21: Task 2 — Economic Impact Assessment of EV Charging

### Task 2.1 — Modeling Framework
- Econometrics modeling to uncover associations between charging infrastructure investments & macro-economic indicators

### Task 2.2 — Collect Feedback from Stakeholders
- Townhall meeting to revise scenarios for future economic impact assessment

---

## Slide 22: Closing Slide
(Illinois logo/branding — orange background)

---

## Key Numbers & Parameters Summary

| Parameter | Value |
|-----------|-------|
| Illinois BEV fleet size | 94,303 vehicles |
| BEV share of plug-in EVs | ~65% |
| Assumed BEV range | 250 miles |
| DC fast charge SoC target | ~80% |
| Total inter-regional VMT (IL) | 4.31 billion miles/year |
| Current DCFC stations (N) | 348 |
| VMT coverage at N=348 | 97.61% |
| Baseline VMT coverage (N=1) | 93.22% |
| Enabled VMT at N=348 | 0.189 billion miles/year (4.39% of total) |
| Fitted VMT curve | f(N) = 93.22 + 0.75·ln(N), R²=0.8488 |
| Discount rate (base) | 7% |
| Vehicle lifetime | 15 years |
| Discount factor D | 9.11 |
| Value per mile (base) | $0.50/mi |
| Value per mile (high) | $0.64/mi |
| Value per mile (low) | $0.35/mi |
| K (time penalty parameter) | 0.1536 hr |
| WTP per BEV at N=348 | $8,611 (range: $5,870–$11,170) |
| Total WTP at N=348 | ~$0.8 billion (range: $0.55B–$1.05B) |
| Marginal value of +1 DCFC at N=348 | ~$39.15M statewide / ~$415 per BEV driver |
| Existing charging stations | 1,559 |
| Future/planned stations | 403 (351 DC Fast + 52 L2) |

---

## Key References
- Greene et al. (2020) — https://doi.org/10.1016/j.trd.2019.11.011 (Seattle VMT-DCFC relationship, WTP equation parameters)
- Borlaug et al. (2018)
- Nicholas et al. (2019)
- Guo & Kontou (2021)
- Electric Vehicle Infrastructure Plan (2022) — https://doi.org/10.36501/0197-9191/22-023 (inaccessibility framework)
- DOE Alternative Fuels Data Center — https://afdc.energy.gov/stations
