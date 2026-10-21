# Professor Feedback Checklist

Feedback received from advisor (Sijia) after dashboard review.  
Use this file to track progress on each requested change.

---

## [x] 1. Overview section — replace bullets with numbered format

**Issue:** The bullet list in the Overview looks too AI-generated.  
**Fix:** Replaced `<ul><li>` bullets with `1.1. ... / 1.2. ... / 1.3. ... / 1.4. ...` paragraph format.  
**Location:** `app.py` → `render_overview()` (~line 405–418)  
**Status:** ✅ Done

---

## [x] 2. Section 1.2 — Update accessibility index definition to −∞ to +∞

**Issue (per Sijia):** The accessibility index $A_j$ was changed in the document to range from $-\infty$ to $+\infty$ (not the original bounded ratio form).  
**Fix:**
- Updated the displayed formula from the ratio form to the log ratio: $A_j = \ln\left(\frac{T_j + \varepsilon}{V_j + \varepsilon}\right)$
- Deleted the three bullet interpretation points
- Replaced with a prose paragraph explaining the index and its interpretation  
- Also removed the "Objective:" and "Key Quantities:" bullet block since the paragraph covers it  
**Location:** `app.py` → `render_12()` (~lines 1279–1299)  
**Status:** ✅ Done

---

## [x] 3. Add detailed discussion paragraphs for each section (1.1 – 1.4)

**Issue:** Professor wants each section to have a paragraph of detailed discussion; visuals are supporting reference only.  
**Fix:** Added comprehensive prose paragraphs for all four sections, written in a clear, human college-student style.  
- **1.1** — covers data sources (AFDC, NEVI), cross-deduplication, demographic/spatial inputs  
- **1.2** — covers the equity question, what $T_j$ and $V_j$ represent, why tract-level analysis matters  
- **1.3** — covers the simulation approach, the log curve, diminishing returns interpretation  
- **1.4** — covers the WTP framework, parameter sensitivity, what the shaded band means  
**Location:** `app.py` → `render_11()`, `render_12()`, `render_13()`, `render_14()`  
**Status:** ✅ Done

---

## [x] 4. Fix Plotly map zoom to focus on Illinois (Fig 1, Fig 2 in 1.1; Fig 3 in 1.2)

**Issue:** The three interactive Plotly maps showed too much surrounding territory (other states dominant in view).  
**Fix:** Increased `zoom` from `5.2` → `6.2` in:
- `plot_all_stations_map_plotly()` (Fig 1, 1.1)
- `plot_future_by_type_map_plotly()` (Fig 2, 1.1)
- `render_12()` choropleth mapbox (Fig 3, 1.2)  
**Location:** `app.py` ~lines 917, 971, 1347  
**Status:** ✅ Done

---

## [x] 5. Fix matplotlib log-ratio map margins (Fig 4 in 1.2)

**Issue:** `ax_lr.margins(x=1.6, y=0.05)` added 160% horizontal padding, showing a huge empty expanse around Illinois.  
**Fix:** Changed to `ax_lr.margins(x=0.02, y=0.02)` so Illinois fills the frame.  
**Location:** `app.py` → `render_12()` ~line 1597  
**Status:** ✅ Done

---

## Summary

| # | Task | Status |
|---|------|--------|
| 1 | Overview: numbered format | ✅ Done |
| 2 | 1.2: index −∞ to +∞, delete bullets, add paragraph | ✅ Done |
| 3 | Paragraphs for 1.1 – 1.4 | ✅ Done |
| 4 | Plotly map zoom (3 maps) | ✅ Done |
| 5 | Matplotlib map margins (1 map) | ✅ Done |
