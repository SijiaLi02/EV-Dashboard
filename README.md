# Illinois EV Charging Infrastructure Dashboard

An interactive web-based dashboard for analyzing EV charging accessibility, VMT coverage, and willingness to pay for DCFC infrastructure in Illinois.

## 📁 Project Structure

```
ev_dashboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── figures/           # Directory for figures organized by section
    ├── 1.1/           # Income analysis figures
    ├── 1.2/           # Gap & accessibility analysis figures
    ├── 1.3.png        # VMT coverage figure
    └── 1.4/           # Willingness to pay figures
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

```
pkill -f streamlit
```

### 2. Run the Dashboard

'''

'''


```bash
streamlit run app.py
```

### 3. Open in Browser

The dashboard will automatically open at `http://localhost:8501`

## 📊 Dashboard Sections

### Section 1.1: Income Analysis (Static)
- Displays median and mean household income maps
- **Type:** Static images
- **Data Source:** ACS 2023

### Section 1.2: Gap & Accessibility Analysis (Static + Formula)
- Shows accessibility change index and log ratio maps
- Includes LaTeX-rendered formulas for methodology
- **Type:** Static images with formula display

### Section 1.3: VMT Coverage (Interactive)
- Interactive coverage curve: f(N) = a + b·ln(N)
- **Interactive Controls:**
  - Number of DCFC stations (N): slider
  - Model coefficients (a, b): number inputs
  - Total VMT: number input

### Section 1.4: Willingness to Pay (Interactive)
- Multiple visualization tabs with parameter controls
- **Interactive Controls:**
  - Value per mile (v): 0.35 - 0.64 $/mi
  - Discount rate (r): 3%, 5%, 7%, 10%
  - BEV Range (R): 200 - 300 miles
  - Access time factor (K)
  - Access time exponent (a)

## 🔧 Customization Guide

### Adding Your Images

1. Place your static images in the appropriate `figures/` subdirectory (organized by section)
2. Update the image paths in `app.py`:

```python
# In Section 1.1
image_path_1 = "figures/1.1/your_income_map.png"

# In Section 1.2
image_path_2 = "figures/1.2/your_accessibility_map.png"
image_path_3 = "figures/1.2/your_log_ratio_map.png"
```

### Modifying the Coverage Function

The default model is:
```python
def coverage_function(N, a=93.22, b=0.75):
    return a + b * np.log(N)
```

Update with your fitted coefficients from the regression.

### Modifying the WTP Function

The simplified WTP function uses:
```python
def wtp_function(N, v, M, D, a=93.22, b=0.75, N0=1):
    delta_f = (coverage_function(N, a, b) - coverage_function(N0, a, b)) / 100
    C = 0.1 * np.log(N / N0) if N > N0 else 0
    wtp = delta_f * M * (v - C) * D
    return np.maximum(wtp, 0)
```

Replace with your actual Greene Equation 17 implementation when you have the full parameters.

### Adding New Parameters

To add a new slider/control:

```python
# In the sidebar or main area
new_param = st.slider(
    "Parameter Name",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1,
    help="Description of what this parameter does"
)

# Then use new_param in your calculations
result = some_function(new_param, ...)
```

### Adding New Tabs or Sections

```python
# Add to the sidebar navigation
section = st.sidebar.radio(
    "Select Section:",
    ["🏠 Overview", 
     "1.1 Income Analysis", 
     # ... existing sections
     "1.5 New Section"],  # Add here
)

# Add the section content
elif section == "1.5 New Section":
    st.markdown("## New Section Content")
    # Your code here
```

## 📈 Data Integration

### When You Receive Real Data

1. **CSV/Excel Data:**
```python
import pandas as pd
df = pd.read_csv("your_data.csv")
# or
df = pd.read_excel("your_data.xlsx")
```

2. **Pre-computed Results:**
```python
# If your PhD provides pre-computed curves for different parameter combinations
results = pd.read_csv("precomputed_results.csv")
# Filter based on user-selected parameters
filtered = results[(results['v'] == v_value) & (results['r'] == r_value)]
```

3. **Real-time Computation:**
```python
# If calculations are fast enough
@st.cache_data
def compute_wtp(N, v, r, R, K, a, M):
    # Your actual computation here
    return wtp_value
```

## 🎨 Styling

The dashboard uses custom CSS for UIUC colors:
- Primary: `#13294B` (UIUC Navy)
- Accent: `#E84A27` (UIUC Orange)

Modify the CSS in the `st.markdown()` block near the top of `app.py`.

## 🚀 Deployment Options

### Streamlit Cloud (Recommended for Sharing)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Deploy

### Local Network Sharing
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📝 To-Do Checklist

- [ ] Receive data from PhD advisor
- [ ] Replace placeholder images with actual maps
- [ ] Update model coefficients with fitted values
- [ ] Implement actual Greene Equation 17
- [ ] Add data source citations
- [ ] Test all interactive controls
- [ ] Deploy to Streamlit Cloud

## 📧 Contact

For questions about this dashboard structure, consult with your PhD advisor for data integration specifics.
