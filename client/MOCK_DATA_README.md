# Mock Data Implementation Guide

## Overview

Your Clinker Allocation & Optimization application now uses mock CSV data files for all graphs and visualizations. This makes it easy to:

- **Test the UI** with realistic data
- **Modify data** without changing code
- **Create different scenarios** by swapping CSV files

## Mock Data Files Created

All mock data files are located in: `client/mock_data/`

### 1. **costs.csv**

Cost breakdown by category (Production, Inventory, Transport, Fixed)

- Used in: Cost Breakdown pie chart & cost cards

### 2. **inventory.csv**

Monthly inventory levels for each plant vs safety stock

- Used in: Inventory vs Safety Stock line chart

### 3. **production.csv**

Production capacity utilization by plant and period

- Used in: Production Utilization Heatmap

### 4. **network_flow.csv**

Transportation routes with volumes and costs

- Used in: Network Flow Sankey diagram & Flow Details table

### 5. **scenarios.csv**

What-if scenarios with costs, savings, and service levels

- Used in: Scenario Analysis section

### 6. **kpis.csv**

Key Performance Indicators over time

- Used in: Dashboard KPI cards

### 7. **nodes.csv**

Plant/Warehouse/Customer node information

- Location data and capacity info

## How to Use

### ✅ Current Status

All visualizations in `client/main.py` are now using mock data:

```python
# Data is loaded once at startup and cached
@st.cache_resource
def get_mock_data():
    return load_mock_data()

mock_data = get_mock_data()
```

### 📝 Modifying Data

To change any graph data, simply edit the corresponding CSV file:

```
client/
  └── mock_data/
      ├── costs.csv ← Edit cost categories/amounts
      ├── inventory.csv ← Edit inventory levels
      ├── production.csv ← Edit utilization %
      ├── network_flow.csv ← Edit transportation routes
      ├── scenarios.csv ← Edit scenario results
      ├── kpis.csv ← Edit KPI metrics
      └── nodes.csv ← Edit plant/warehouse info
```

### 🔄 Data Flow Example

**Cost Breakdown Section:**

1. CSV loads: `costs.csv` (category, amount, percentage)
2. Code reads it: `costs_df = mock_data['costs']`
3. Chart displays it: Pie chart + 3 cost cards

## Features

### ✨ Favorable Data

All mock data shows optimal/favorable scenarios:

- **High utilization rates** (75-95%)
- **Decreasing total costs** over time
- **Strong service levels** (96-99%)
- **Balanced inventory** above safety stock

### 🎯 Dynamic Sections

- **Inventory Selection:** Switch between plants to see different data
- **Scenario Buttons:** Click scenarios to see dynamic cost comparisons
- **Heatmap:** Shows utilization across all periods automatically

### 📊 All Visualizations Use Mock Data

- ✅ Cost pie chart & boxes
- ✅ Production heatmap
- ✅ Network flow Sankey diagram
- ✅ Inventory line chart
- ✅ Scenario analysis buttons
- ✅ Flow details table

## Next Steps

1. **Test the app:** `streamlit run client/main.py`
2. **Modify data:** Edit any CSV in `client/mock_data/`
3. **Add new scenarios:** Add rows to `scenarios.csv`
4. **Expand visualizations:** Create new CSVs and load them

## Example: Add a New Scenario

Edit `scenarios.csv`:

```csv
Scenario,Total_Cost,Savings,Service_Level,Feasible
...existing scenarios...
New Scenario Name,4000000,250000,98.0,True
```

The scenario will automatically appear as a button in the Scenario Analysis tab!

---

**All data is now sourced from CSV files, making your app flexible and easy to maintain!** ✨
