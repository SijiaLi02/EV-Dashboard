# Research Documentation
## What we found vs. what still needs your input

Sources reviewed:
- IDOT-ICT TRP Meeting Minutes, R27-280, January 7, 2026
- Greene, Kontou, Borlaug, Brooker & Muratori (2020), "Public charging infrastructure for plug-in electric vehicles: What is it worth?" *Transportation Research Part D*, 78, 102182.

---

## 1.1 Data Integration

### ✅ Found in documents
| Question | Answer | Source |
|---|---|---|
| Why AFDC? | AFDC is the national DOE-maintained standard database for EV station locations — no competing source exists at this scale. Used explicitly in the project. | TRP Minutes |
| What does "future stations" mean? | NEVI (National Electric Vehicle Infrastructure) Formula Program — federally funded stations that are awarded but not yet operational. | TRP Minutes |
| What was analyzed in 1.1? | Locations of existing chargers, NEVI station locations, EV registrations in Illinois, coverage gaps in the network. | TRP Minutes |

### ❓ Still need from you
| Question | Why it matters |
|---|---|
| How did you decide on the 0.001° deduplication threshold? Was it Sijia's call or did you test a few values? | Helps write the sentence explaining *why* that cutoff was chosen |
| Was there any manual review of deduplication results, or was it fully automated? | Adds credibility detail to the paragraph |

---

## 1.2 Accessibility Gap

### ✅ Found in documents
| Question | Answer | Source |
|---|---|---|
| What does the index measure? | "Normalize the difference between EV charging demand and network capacity" at the census-tract level. | TRP Minutes |
| What did the map show? | "Where charging gaps currently exist, providing a baseline for evaluating future infrastructure deployment." | TRP Minutes |
| Why is a map-based approach used? | To show spatial variation — aggregate state counts mask local gaps. | Implied in TRP Minutes (Lange's question about the maps) |

### ❓ Still need from you
| Question | Why it matters |
|---|---|
| Why census tracts specifically (vs. counties, ZIP codes, grid cells)? | Were tracts chosen because ACS data is at that level? Or did Sijia specify? |
| The index formula changed to log-ratio (−∞ to +∞) — what was the original bounded formula, and what motivated the change? | Helps explain the reasoning behind the formula choice in the paragraph |

---

## 1.3 Electrified Miles Estimation

### ✅ Found in documents
| Question | Answer | Source |
|---|---|---|
| Plain-English VMT coverage | "The relationship between charging deployment and electrified VMT is highly nonlinear — early additions of charging stations unlock disproportionately large gains in electrified miles, and as the network becomes denser, marginal gains diminish." | TRP Minutes (verbatim from Li's presentation) |
| What the curve means | First stations cover highest-traffic corridors → large gains. Later stations extend to lower-demand rural areas → diminishing returns. | TRP Minutes |
| Functional form | Logarithmic: y = 0.75 ln(x) + 93.1, R² = 0.8132 | Code / presentation |

### ❓ Still need from you
| Question | Why it matters |
|---|---|
| Why 10 simulation runs? Was this Sijia's specification, or did you try more and find results stabilized? | If it's a standard statistical choice, say so; if Sijia set it, credit the methodology |
| What spatial data drove the simulation — was it statewide GPS traces, synthetic travel demand, or something else? | The paragraph currently says "spatial deployment model" which is vague |

---

## 1.4 Willingness to Pay

### ✅ Found in documents
| Question | Answer | Source |
|---|---|---|
| What does WTP mean here? | Maximum amount a driver would give up (in present-value dollars) to have DCFC infrastructure available — tied to how many extra electric miles it enables and what those miles are worth. | Greene et al. (2020) — Kontou is co-author |
| What the framework covers | "Fuel cost savings, time and detour cost savings, and charging access value." | TRP Minutes |
| Total benefit range | Between **$0.8 and $1.05 billion** for Illinois. | TRP Minutes |
| Why benefits decline as N grows | Marginal gains in coverage fall as network densifies — same log curve as 1.3. | TRP Minutes + Greene et al. |
| Foundation paper | Greene, Kontou et al. (2020) is the direct methodological source — Kontou co-authored it. | Greene et al. (2020) |

### ❓ Still need from you
| Question | Why it matters |
|---|---|
| The $0.35–$0.64/mi range — the Greene paper gives ~$0.27–$0.49/mi from econometrics. How did you get to $0.35–$0.64? Inflation adjustment? Illinois-specific calibration? Sijia's range? | This is the most important number in section 1.4 — the paragraph needs to explain where it comes from |
| Is the discount rate range (3–10%) standard IDOT/federal guidance, or chosen by the team? | One sentence of justification makes it much more credible |
| What is N_gas = 3,670 based on? (gasoline stations in Illinois used to calibrate access cost) | Background detail for the access cost formula explanation |

---

## Summary table

| Section | Confidence level | Main gap |
|---|---|---|
| 1.1 | High — data sources well documented | Deduplication threshold justification |
| 1.2 | Medium — framework clear, formula motivation unclear | Why census tracts; why log-ratio specifically |
| 1.3 | High — TRP minutes have near-verbatim description | Why 10 runs; what simulation data |
| 1.4 | Medium-high — Greene paper is the foundation | Where $0.35–$0.64/mi comes from |
