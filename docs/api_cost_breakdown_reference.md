# API Cost Breakdown Reference

## Response Format

### Successful Optimization Response

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
  "production": [
    {
      "node_id": "Plant-A",
      "period_id": 1,
      "quantity": 500.0
    }
  ],
  "inventory": [
    {
      "node_id": "Plant-A",
      "period_id": 1,
      "quantity": 150.0
    }
  ],
  "shipments": [
    {
      "origin": "Plant-A",
      "destination": "Warehouse-N",
      "mode": "Rail",
      "period_id": 1,
      "quantity": 450.0,
      "trips": 2
    }
  ]
}
```

## Cost Breakdown Fields

| Field | Type | Description |
|-------|------|-------------|
| `production_cost` | float | Σ(prod_cost[i,t] × Prod[i,t]) |
| `inventory_cost` | float | Σ(inv_cost[i] × Inv[i,t]) |
| `transport_variable_cost` | float | Σ(trans_cost[i,j,m] × X[i,j,m,t]) |
| `trip_cost` | float | Σ(trip_fixed_cost × Trips[i,j,m,t]) |
| `transport_cost` | float | transport_variable_cost + trip_cost |

## Cost Details Fields

| Field | Type | Description |
|-------|------|-------------|
| `computed_total` | float | Sum of all cost components (production + inventory + transport) |
| `objective_total` | float | Total cost from solver objective function |
| `variance` | float | \|computed_total - objective_total\| (should be near 0) |
| `breakdown_valid` | boolean | true if variance < 1.0 |

## Validation Rules

### ✅ Valid Breakdown
```
production_cost + inventory_cost + transport_cost ≈ total_cost
```
- Variance < 1.0 (within solver tolerance)
- `breakdown_valid: true`

### ⚠️ Warning Breakdown
```
|production_cost + inventory_cost + transport_cost - total_cost| ≥ 1.0
```
- Variance >= 1.0
- `breakdown_valid: false`
- Still usable but check for solver issues

## Usage Examples

### Python (Requests)
```python
import requests

response = requests.post("http://localhost:8000/optimize")
data = response.json()

if data["status"] == "success":
    # Access cost breakdown
    prod_cost = data["cost_breakdown"]["production_cost"]
    inv_cost = data["cost_breakdown"]["inventory_cost"]
    trans_cost = data["cost_breakdown"]["transport_cost"]
    total = data["total_cost"]
    
    # Verify breakdown
    if data["cost_details"]["breakdown_valid"]:
        print(f"✅ Cost breakdown verified")
    else:
        print(f"⚠️ Variance: {data['cost_details']['variance']}")
```

### JavaScript/Fetch
```javascript
const response = await fetch("http://localhost:8000/optimize", {
  method: "POST"
});

const data = await response.json();

if (data.status === "success") {
  const breakdown = data.cost_breakdown;
  const total = data.total_cost;
  
  console.log(`Production: ₹${breakdown.production_cost}`);
  console.log(`Inventory: ₹${breakdown.inventory_cost}`);
  console.log(`Transport: ₹${breakdown.transport_cost}`);
  console.log(`Total: ₹${total}`);
  
  if (data.cost_details.breakdown_valid) {
    console.log("✅ Breakdown validated");
  }
}
```

## Frontend Integration

The Streamlit frontend displays the cost breakdown in multiple places:

### 1. KPI Cards (Overview Tab)
- Shows total cost
- Extracted from `total_cost`

### 2. Cost Breakdown Cards (Overview Tab)
- Production cost from `cost_breakdown.production_cost`
- Inventory cost from `cost_breakdown.inventory_cost`
- Transport cost from `cost_breakdown.transport_cost`

### 3. Cost Breakdown Tab (Detailed Results)
- Metrics for each component
- Pie chart visualization
- Validation status with variance
- Detailed table with percentages

## Debugging

### If variance is high:
1. Check cost coefficient values in input CSVs
2. Verify solver convergence (check solver logs)
3. Confirm all decision variables have `.value` set
4. Review model objective function definition

### If breakdown_valid is false:
1. Check variance amount in `cost_details.variance`
2. Increase tolerance threshold if needed
3. Review solver solver messages for issues
4. Verify input data consistency

## Formulas

### Total Cost Equation
```
Total Cost = Production Cost + Inventory Cost + Transport Cost

Where:
  Production Cost = Σ (prod_cost[i,t] × Prod[i,t])
  Inventory Cost = Σ (inv_cost[i] × Inv[i,t])
  Transport Cost = Σ (trans_cost[i,j,m] × X[i,j,m,t]) 
                 + Σ (trip_fixed_cost × Trips[i,j,m,t])
```

### Cost Percentages
```
% of Total = (Component Cost / Total Cost) × 100
```

## Tolerance & Precision

- **Precision**: All costs rounded to 2 decimal places in JSON
- **Variance Threshold**: 1.0 (configurable in `compute_cost_breakdown`)
- **Solver Tolerance**: Depends on GLPK/CBC settings

## Audit Trail

The response provides full auditability:

1. **Raw Costs**: All component costs provided
2. **Computation**: Formulas documented above
3. **Validation**: Variance shown explicitly
4. **Objective**: Solver's objective value for verification
5. **Breakdown**: Can recalculate = objective?

## Example Calculation

Given:
- Production: 500 tons at ₹100/ton = ₹50,000
- Inventory: 150 tons at ₹50/ton = ₹7,500
- Shipments: 450 tons at ₹10/ton = ₹4,500
- Trips: 2 trips at ₹0.01 = ₹0.02

Breakdown:
```json
{
  "production_cost": 50000.00,
  "inventory_cost": 7500.00,
  "transport_variable_cost": 4500.00,
  "trip_cost": 0.02,
  "transport_cost": 4500.02,
  "total_cost": 62000.02
}
```

Verification:
```
50,000 + 7,500 + 4,500.02 = 62,000.02 ✅
```
