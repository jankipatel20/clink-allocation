# Cost Breakdown System Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
│                                                                   │
│  1. Frontend displays "Run Optimization" button                   │
│  2. User clicks button                                            │
│  3. Frontend sends POST /optimize request                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND: /optimize ENDPOINT                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. DATA LOADING                                         │    │
│  │    - Load production.csv                                │    │
│  │    - Load nodes.csv                                     │    │
│  │    - Load arcs.csv                                      │    │
│  │    - Load demand.csv, periods.csv, scenarios.csv        │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │ 2. MODEL BUILDING & SOLVING                             │    │
│  │    - build_model() creates Pyomo optimization model      │    │
│  │    - Defines decision variables:                         │    │
│  │      • Prod[i,t] - production quantities                 │    │
│  │      • Inv[n,t] - inventory quantities                   │    │
│  │      • X[i,j,m,t] - shipment quantities                  │    │
│  │      • Trips[i,j,m,t] - number of trips                 │    │
│  │    - Defines objective: minimize total cost              │    │
│  │    - solve_model() solves with GLPK/CBC solver           │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │ 3. COST BREAKDOWN COMPUTATION (NEW)                     │    │
│  │    compute_cost_breakdown(model, data):                  │    │
│  │                                                          │    │
│  │    Extract cost coefficients from data:                  │    │
│  │    • prod_cost from production.csv                       │    │
│  │    • inv_cost from nodes.csv                             │    │
│  │    • trans_cost from arcs.csv                            │    │
│  │                                                          │    │
│  │    Compute each component:                               │    │
│  │                                                          │    │
│  │    production_cost = Σ(prod_cost × Prod.value)          │    │
│  │    inventory_cost = Σ(inv_cost × Inv.value)             │    │
│  │    transport_var_cost = Σ(trans_cost × X.value)         │    │
│  │    trip_cost = Σ(0.01 × Trips.value)                    │    │
│  │    transport_cost = transport_var_cost + trip_cost       │    │
│  │                                                          │    │
│  │    Validate breakdown:                                   │    │
│  │    total_computed = prod + inv + transport               │    │
│  │    total_objective = model.OBJ().value                   │    │
│  │    variance = |total_computed - total_objective|         │    │
│  │    breakdown_valid = (variance < 1.0)                    │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │ 4. DECISION VARIABLES EXTRACTION                         │    │
│  │    - Extract production plans                            │    │
│  │    - Extract inventory plans                             │    │
│  │    - Extract shipment plans                              │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │ 5. RESPONSE ASSEMBLY                                    │    │
│  │    Return JSON with:                                     │    │
│  │    • total_cost: float                                   │    │
│  │    • cost_breakdown: {prod, inv, trans_var, trip, trans} │    │
│  │    • cost_details: {computed, objective, variance}       │    │
│  │    • production: list                                    │    │
│  │    • inventory: list                                     │    │
│  │    • shipments: list                                     │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND: DISPLAY RESULTS                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Overview Tab:                                           │    │
│  │  - KPI Cards show total_cost                            │    │
│  │  - Cost breakdown cards show production, inventory,     │    │
│  │    transport costs                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Detailed Results → Cost Breakdown Tab:                  │    │
│  │  - Display 4 metrics (production, inventory, var, trip)  │    │
│  │  - Pie chart showing cost distribution                   │    │
│  │  - Validation section with variance                      │    │
│  │  - Detailed breakdown table with percentages             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow for Cost Computation

```
INPUT DATA (CSVs)
│
├─ production.csv ────────┐
│  (prod_cost)            │
│                         │ Extract cost
├─ nodes.csv ─────────────┼─ coefficients
│  (inv_cost)             │
│                         │
├─ arcs.csv ──────────────┘
│  (trans_cost)
│
│  ┌────────────────────────────────────┐
│  │     SOLVED PYOMO MODEL             │
│  │  (decision variable values)         │
│  │                                     │
│  │  Prod[i,t].value ─────────────┐   │
│  │  Inv[n,t].value ──────────────┼─→ │ COST
│  │  X[i,j,m,t].value ────────────┼─→ │ COMP
│  │  Trips[i,j,m,t].value ────────┘   │
│  │                                     │
│  └────────────────────────────────────┘
│          │
│          │ Multiply: costs × quantities
│          │
│          ▼
│    ┌──────────────────────┐
│    │ Production Cost      │
│    │ = Σ prod_cost × Prod │
│    └──────────────────────┘
│
│    ┌──────────────────────┐
│    │ Inventory Cost       │
│    │ = Σ inv_cost × Inv   │
│    └──────────────────────┘
│
│    ┌──────────────────────┐
│    │ Transport Var Cost   │
│    │ = Σ trans_cost × X   │
│    └──────────────────────┘
│
│    ┌──────────────────────┐
│    │ Trip Cost            │
│    │ = Σ 0.01 × Trips     │
│    └──────────────────────┘
│
▼    ┌──────────────────────┐
     │ Transport Cost       │
     │ = Var + Fixed        │
     └──────────────────────┘
          │
          │ Sum all components
          │
          ▼
     ┌──────────────────────┐
     │ TOTAL COST (Computed)│
     └──────────────────────┘
          │
          │ Compare with
          │ model.OBJ().value
          │
          ▼
     ┌──────────────────────┐
     │ Variance Check       │
     │ breakdown_valid?     │
     └──────────────────────┘
          │
          ▼
     JSON Response
```

## Component Breakdown Visualization

```
TOTAL COST: ₹42,50,000
│
├─ Production Cost: ₹25,00,000 (58.8%)
│  └─ Σ(prod_cost[i,t] × Prod[i,t])
│
├─ Inventory Cost: ₹7,50,000 (17.6%)
│  └─ Σ(inv_cost[n] × Inv[n,t])
│
└─ Transport Cost: ₹10,00,000 (23.5%)
   │
   ├─ Variable: ₹9,50,000 (22.4%)
   │  └─ Σ(trans_cost[i,j,m] × X[i,j,m,t])
   │
   └─ Fixed Trips: ₹50,000 (1.2%)
      └─ Σ(0.01 × Trips[i,j,m,t])
```

## Validation Flow

```
┌──────────────────────────────┐
│   Computed Total             │
│  prod + inv + trans = ?      │
└──────────────────────┬───────┘
                       │
                       ├─ Extract ──┐
                       │            │
┌──────────────────────▼────┐      │
│   Solver Objective        │      │
│   model.OBJ().value       │◄─────┘
└──────────────────────┬────┘
                       │
                       ▼
        ┌─────────────────────────┐
        │ Calculate Variance      │
        │ |computed - objective|  │
        └────────────┬────────────┘
                     │
            ┌────────┴─────────┐
            │                  │
         (< 1.0)          (≥ 1.0)
            │                  │
            ▼                  ▼
        ✅ VALID          ⚠️ WARNING
    breakdown_valid=true  breakdown_valid=false
```

## API Response Structure

```
HTTP 200 OK
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
    {"node_id": "Plant-A", "period_id": 1, "quantity": 500},
    ...
  ],
  
  "inventory": [
    {"node_id": "Plant-A", "period_id": 1, "quantity": 150},
    ...
  ],
  
  "shipments": [
    {"origin": "Plant-A", "destination": "Warehouse-N", 
     "mode": "Rail", "period_id": 1, "quantity": 450, "trips": 2},
    ...
  ]
}
```

## Frontend Display Components

```
STREAMLIT INTERFACE
│
├─ Overview Tab
│  ├─ KPI Cards (4 columns)
│  │  └─ Total Cost from response
│  │
│  ├─ Cost Breakdown Cards (3 columns)
│  │  ├─ Production: response.cost_breakdown.production_cost
│  │  ├─ Inventory: response.cost_breakdown.inventory_cost
│  │  └─ Transport: response.cost_breakdown.transport_cost
│  │
│  └─ Charts
│     └─ Other visualizations
│
├─ Network Flow Tab
│  └─ Sankey diagram with real shipment data
│
├─ Inventory Tab
│  └─ Inventory trends chart
│
└─ Detailed Results (Tabs)
   ├─ Production Plan tab
   ├─ Inventory Levels tab
   ├─ Shipment Plan tab
   │
   └─ Cost Breakdown Tab ⭐ (NEW)
      ├─ 4 Metric cards
      │  ├─ Production Cost
      │  ├─ Inventory Cost
      │  ├─ Transport Variable Cost
      │  └─ Trip Fixed Cost
      │
      ├─ Pie Chart (Cost Distribution)
      │
      ├─ Validation Section
      │  ├─ Total (Objective)
      │  ├─ Total (Computed)
      │  ├─ Variance
      │  └─ Validation Status (✅ or ⚠️)
      │
      └─ Detailed Table
         ├─ Component names
         ├─ Amounts in ₹
         └─ % of Total
```

## Key Equations at a Glance

```
Production Cost = Σ prod_cost[i,t] × Prod[i,t]
Inventory Cost  = Σ inv_cost[i] × Inv[i,t]
Transport Cost  = Σ trans_cost[i,j,m] × X[i,j,m,t]
                + Σ trip_fixed_cost × Trips[i,j,m,t]

Total Cost = Production Cost + Inventory Cost + Transport Cost

Variance = |Computed Total - Solver Objective|
Valid = (Variance < 1.0)
```

## Performance Characteristics

```
Operation              Time Complexity    Typical Duration
─────────────────────────────────────────────────────────
Model Solving          O(solver)          1-5 minutes
Cost Computation       O(|N|×|T|+|ARCS|)  < 100 ms
Data Extraction        O(|N|×|T|+|ARCS|)  < 50 ms
Response Assembly      O(n)               < 10 ms
─────────────────────────────────────────────────────────
Total Backend Time     (dominated by solver)
Frontend Display       Real-time (< 1s)
```

## Backward Compatibility

```
Old API Response          New API Response
────────────────────      ────────────────────────
status: "success"         status: "success"
total_cost: 4250000       total_cost: 4250000 ✓
production: [...]         production: [...] ✓
inventory: [...]          inventory: [...] ✓
shipments: [...]          shipments: [...] ✓
                          
                          + cost_breakdown: {...}
                          + cost_details: {...}

✅ Old clients still work (ignore new fields)
✅ New clients get additional detail
```
