# Cost Breakdown Feature - Quick Start Guide

## What's New?

The backend now computes and returns detailed cost breakdowns directly from the solved Pyomo model. Every optimization run now includes transparent, auditable cost component breakdown.

## For Users

### Running an Optimization

1. **Start Backend**
   ```powershell
   cd D:\Projects\clink-allocation
   uvicorn backend.main:app --reload
   ```

2. **Start Frontend**
   ```powershell
   cd D:\Projects\clink-allocation
   streamlit run client/main.py
   ```

3. **Run Optimization**
   - Open: http://localhost:8501
   - Click "Run Optimization" button
   - Wait for results (1-5 minutes)

### Viewing Cost Breakdown

#### Overview Tab
- **Cost Cards**: See production, inventory, and transport costs in Indian Rupees
- **Total Cost**: Displayed at the top in KPI metrics

#### Detailed Results Tab
New **"Cost Breakdown"** tab shows:

1. **Cost Summary** (4 metrics)
   - Production Cost
   - Inventory Cost
   - Transport Variable Cost
   - Trip Fixed Cost

2. **Cost Distribution Pie Chart**
   - Visual breakdown by percentage

3. **Validation Section**
   - ✅ Breakdown verified
   - Variance: ₹0.000000
   - Ensures costs are computed correctly

4. **Detailed Table**
   - All components with amounts in ₹
   - Percentage of total for each

## For Developers

### Understanding the Cost Breakdown

**5 Cost Components:**
```
1. Production Cost    = Σ (prod_cost × Prod quantity)
2. Inventory Cost     = Σ (inv_cost × Inv quantity)
3. Transport Var Cost = Σ (trans_cost × Shipment quantity)
4. Trip Fixed Cost    = Σ (0.01 × Number of trips)
5. Transport Cost     = Transport Var + Trip Fixed
```

**Total = Production + Inventory + Transport**

### API Response Format

**New Response Fields:**
```json
{
  "cost_breakdown": {
    "production_cost": 2500000.00,
    "inventory_cost": 750000.00,
    "transport_variable_cost": 950000.00,
    "trip_cost": 50000.50,
    "transport_cost": 1000000.50
  },
  "cost_details": {
    "computed_total": 4250000.50,
    "objective_total": 4250000.50,
    "variance": 0.000000,
    "breakdown_valid": true
  }
}
```

### Backend Implementation

**File: `backend/main.py`**

New function `compute_cost_breakdown(model, data)`:
```python
def compute_cost_breakdown(model, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Computes detailed cost breakdown from solved Pyomo model.
    
    Returns:
        {
            "production_cost": float,
            "inventory_cost": float,
            "transport_variable_cost": float,
            "trip_cost": float,
            "transport_cost": float,
            "total_cost": float,
            "cost_details": {
                "computed_total": float,
                "objective_total": float,
                "variance": float,
                "breakdown_valid": bool
            }
        }
    """
```

### Frontend Implementation

**File: `client/main.py`**

Three main changes:
1. Helper function `format_inr()` for Indian Rupee formatting
2. KPI cards use real `cost_breakdown` data
3. New "Cost Breakdown" detail tab with charts and validation

### Using the Cost Breakdown in Python

```python
import requests

response = requests.post("http://localhost:8000/optimize")
data = response.json()

if data["status"] == "success":
    breakdown = data["cost_breakdown"]
    
    # Access each component
    prod_cost = breakdown["production_cost"]
    inv_cost = breakdown["inventory_cost"]
    trans_cost = breakdown["transport_cost"]
    
    # Verify it's valid
    if data["cost_details"]["breakdown_valid"]:
        print("✅ Costs verified - breakdown matches solver objective")
    
    # Display costs
    print(f"Production: ₹{prod_cost:,.2f}")
    print(f"Inventory:  ₹{inv_cost:,.2f}")
    print(f"Transport:  ₹{trans_cost:,.2f}")
    print(f"─" * 40)
    print(f"Total:      ₹{data['total_cost']:,.2f}")
```

## Key Features

### ✅ Direct Computation
- Costs calculated from solved decision variables
- No approximations or inferences
- Full transparency

### ✅ Built-in Validation
- Breakdown total matches solver objective
- Variance reported explicitly
- `breakdown_valid` flag indicates confidence

### ✅ Real-time Display
- Frontend shows actual costs from optimization
- Not hardcoded or estimated
- Updates with each optimization run

### ✅ Audit Trail
- All cost sources documented
- Computation formulas available
- Variance explained

## Example Output

### Screen 1: Overview Tab
```
┌─ Total Cost: ₹42,50,000 (in KPI card)
├─ Cost Breakdown Cards:
│  ├─ Production: ₹25,00,000
│  ├─ Inventory: ₹7,50,000
│  └─ Transport: ₹10,00,000
└─ Other visualizations...
```

### Screen 2: Cost Breakdown Detail Tab
```
Cost Summary Metrics:
┌─────────────────────────────────┐
│ Prod: ₹25,00,000                │
│ Inv:  ₹7,50,000                 │
│ Var:  ₹9,50,000                 │
│ Trip: ₹0,50,000                 │
└─────────────────────────────────┘

Cost Distribution:
┌─────────────────────────────────┐
│        Pie Chart                 │
│   Production: 58.8%              │
│   Inventory: 17.6%               │
│   Transport: 23.5%               │
└─────────────────────────────────┘

Validation:
┌─────────────────────────────────┐
│ ✅ Cost breakdown verified       │
│ Objective: ₹42,50,000            │
│ Computed:  ₹42,50,000            │
│ Variance:  ₹0.000000             │
└─────────────────────────────────┘

Breakdown Table:
┌──────────────────┬────────────┬─────┐
│ Component        │ Amount (₹) │ %   │
├──────────────────┼────────────┼─────┤
│ Production       │ 25,00,000  │58.8%│
│ Inventory        │ 7,50,000   │17.6%│
│ Transport Var    │ 9,50,000   │22.4%│
│ Trip Fixed       │ 50,000     │ 1.2%│
├──────────────────┼────────────┼─────┤
│ TOTAL            │ 42,50,000  │100% │
└──────────────────┴────────────┴─────┘
```

## Validation Checklist

Before deploying to production:

- [ ] Backend returns `cost_breakdown` in response
- [ ] `cost_details.breakdown_valid` is `true`
- [ ] `cost_details.variance` is near 0
- [ ] production_cost + inventory_cost + transport_cost ≈ total_cost
- [ ] Frontend "Cost Breakdown" tab displays all metrics
- [ ] Cost pie chart renders correctly
- [ ] Costs displayed in Indian Rupees (₹)
- [ ] All tests pass

## Troubleshooting

### Variance is high (> 1.0)
- Check input data for errors
- Review solver logs
- Verify cost coefficients in CSVs

### Cost Breakdown tab not showing
- Ensure optimization has been run
- Check browser console for errors
- Verify API response includes `cost_breakdown`

### Costs showing as "--"
- Optimization may not have completed
- Check backend logs for errors
- Try running optimization again

## Documentation Files

Read these for more details:
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - High-level overview
- **[cost_breakdown_implementation.md](./cost_breakdown_implementation.md)** - Technical deep dive
- **[cost_equations.md](./cost_equations.md)** - Mathematical formulas
- **[api_cost_breakdown_reference.md](./api_cost_breakdown_reference.md)** - API reference
- **[architecture_diagrams.md](./architecture_diagrams.md)** - System diagrams

## Files Changed

| File | Changes |
|------|---------|
| `backend/main.py` | Added `compute_cost_breakdown()` function, modified `/optimize` endpoint |
| `client/main.py` | Added cost breakdown tab, updated KPI cards, added validation display |

## Next Steps

- [x] Backend computes cost breakdown from solved model
- [x] Frontend displays detailed cost breakdown
- [x] Validation shows breakdown matches objective
- [ ] Add cost sensitivity analysis
- [ ] Add scenario cost comparison
- [ ] Add cost allocation by demand node

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the documentation files
3. Check backend logs: `uvicorn backend.main:app --reload`
4. Check browser console for frontend errors

## Summary

The cost breakdown feature provides:
- **Transparency**: See exactly how total cost is composed
- **Auditability**: Every component is directly computed from the model
- **Validation**: Automatic verification that breakdown matches solver
- **Visibility**: Real-time display in frontend with charts and metrics

All costs are now computed directly from solved Pyomo variables, ensuring accuracy and accountability!
