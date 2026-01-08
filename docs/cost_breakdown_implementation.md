# Cost Breakdown Implementation

## Overview

The backend now computes and returns a detailed cost breakdown directly from the solved Pyomo optimization model. This provides transparency and auditability of how the total cost is composed.

## Backend Implementation

### Function: `compute_cost_breakdown(model, data)`

Located in [backend/main.py](../backend/main.py), this function extracts cost components from the solved Pyomo model.

#### Cost Components Computed

1. **Production Cost**
   ```
   production_cost = Σ (prod_cost[i,t] × Prod[i,t])
   ```
   - Sums production costs across all nodes and periods
   - Uses solved variable values: `Prod[i,t].value`

2. **Inventory Cost**
   ```
   inventory_cost = Σ (inv_cost[i] × Inv[i,t])
   ```
   - Sums inventory holding costs across all nodes and periods
   - Uses solved variable values: `Inv[i,t].value`

3. **Transport Variable Cost**
   ```
   transport_variable_cost = Σ (trans_cost[i,j,m] × X[i,j,m,t])
   ```
   - Quantity-based transportation costs
   - Uses solved variable values: `X[i,j,m,t].value`

4. **Trip Fixed Cost**
   ```
   trip_cost = Σ (trip_fixed_cost × Trips[i,j,m,t])
   ```
   - Fixed cost per trip (currently 0.01)
   - Uses solved variable values: `Trips[i,j,m,t].value`

5. **Total Transport Cost**
   ```
   transport_cost = transport_variable_cost + trip_cost
   ```

#### Cost Validation

The function validates that the computed breakdown matches the solver's objective value:

```python
total_cost_computed = production_cost + inventory_cost + transport_cost
total_cost_objective = value(model.OBJ)
cost_variance = abs(total_cost_computed - total_cost_objective)
```

- **Variance**: Differences within solver tolerance (~1.0)
- **breakdown_valid**: Boolean flag indicating if variance is acceptable

## API Response Structure

### Request
```
POST /optimize
Content-Type: multipart/form-data
Files: [optional CSV uploads]
```

### Response (Success)
```json
{
  "status": "success",
  "total_cost": 4250000.50,
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
  },
  "production": [...],
  "inventory": [...],
  "shipments": [...]
}
```

### Response (Error)
```json
{
  "status": "error",
  "message": "Error description"
}
```

## Frontend Display

### Overview Tab
- KPI cards display:
  - Total cost in Indian Rupees
  - Backend status indicator

- Cost breakdown cards show:
  - Production cost
  - Inventory cost
  - Transport cost

### Detailed Results → Cost Breakdown Tab

New tab dedicated to cost analysis with:

1. **Cost Summary Metrics** (4 columns)
   - Production Cost
   - Inventory Cost
   - Transport Variable Cost
   - Trip Fixed Cost

2. **Cost Distribution Pie Chart**
   - Visual breakdown of cost components
   - Percentages of total cost

3. **Cost Validation Section**
   - Total (Objective): From solver
   - Total (Computed): Calculated from breakdown
   - Variance: Difference between the two
   - Validation status with checkmark or warning

4. **Detailed Breakdown Table**
   - All cost components
   - Amount in Indian Rupees
   - Percentage of total cost

## Computation Process

### Step 1: Model Solving
```python
model, result = solve_model(nodes, periods, production, demand, arcs, scenarios)
```

### Step 2: Cost Extraction
```python
cost_breakdown = compute_cost_breakdown(model, data)
```

This function:
- Extracts cost coefficients from input DataFrames
- Iterates through model sets (N, T, ARCS)
- Accesses solved variable `.value` properties
- Multiplies costs × quantities
- Sums all components

### Step 3: Validation
```python
variance = |computed_total - objective_total|
breakdown_valid = (variance < 1.0)
```

### Step 4: Response
```python
return {
    "status": "success",
    "total_cost": total_cost_objective,
    "cost_breakdown": {...},
    "cost_details": {...},
    "production": [...],
    "inventory": [...],
    "shipments": [...]
}
```

## Key Design Principles

### ✅ Direct Model Access
- Costs computed directly from solved variables
- No approximation or reverse-engineering from quantities
- Full transparency of cost sources

### ✅ No Recomputation in Frontend
- Frontend receives pre-computed costs
- No client-side cost recalculation
- JSON contains authoritative values

### ✅ Verification & Auditability
- Computed total matches solver objective
- Variance tracked and reported
- `breakdown_valid` flag indicates confidence level

### ✅ Tolerance-Aware
- Accounts for solver rounding errors
- Variance threshold: < 1.0 (configurable)
- Warnings if variance exceeds threshold

## Example Workflow

1. **User runs optimization** via frontend
2. **Backend solves model** using Pyomo + GLPK/CBC
3. **Backend computes cost breakdown** from solved variables
4. **Backend validates** computed total vs objective
5. **Backend returns full response** with:
   - Detailed cost breakdown
   - Validation details
   - Decision variables (production, inventory, shipments)
6. **Frontend displays**:
   - Cost summary in KPI cards
   - Cost breakdown pie chart
   - Validation status
   - Detailed breakdown table

## Testing & Validation

### To verify cost breakdown:

1. Check variance in `cost_details.variance`
2. Confirm `cost_details.breakdown_valid == true`
3. Validate:
   ```
   production_cost + inventory_cost + transport_cost ≈ total_cost
   ```
4. Review individual costs in detailed breakdown table

### Example validation:
```
Production Cost:        ₹25,00,000 (58.8%)
Inventory Cost:         ₹7,50,000  (17.6%)
Transport Cost:         ₹10,00,000 (23.5%)
────────────────────────────────────
Total:                  ₹42,50,000 (100%)

Variance: ₹0.000000 ✅ VALID
```

## Cost Coefficients Reference

### Production Cost Coefficient
- Source: `production.csv` → `prod_cost` column
- Unit: Cost per unit of production at node i in period t
- Example: ₹100/ton

### Inventory Cost Coefficient
- Source: `nodes.csv` → `inv_cost` column
- Unit: Cost per unit of inventory held at node i
- Example: ₹50/ton per period

### Transport Variable Cost Coefficient
- Source: `arcs.csv` → `trans_cost` column
- Unit: Cost per unit shipped on route (i,j,m)
- Example: ₹10/ton

### Trip Fixed Cost
- Hardcoded: 0.01
- Unit: Cost per trip (regardless of quantity)
- Example: ₹0.01 per trip

## Future Enhancements

- [ ] Cost breakdown by node/time period
- [ ] Cost sensitivity analysis
- [ ] Scenario comparison with cost differences
- [ ] Cost allocation to demand nodes
- [ ] Cost tracking over optimization iterations
