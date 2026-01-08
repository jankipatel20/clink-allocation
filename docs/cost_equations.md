# Cost Breakdown Equations

This document specifies the exact mathematical equations used to compute each cost component from the solved Pyomo model.

## Cost Components

### 1. Production Cost

**Equation:**
$$\text{Production Cost} = \sum_{i \in N} \sum_{t \in T} \text{prod\_cost}[i,t] \times \text{Prod}[i,t]$$

**Description:**
- Sum over all nodes (i) and time periods (t)
- Multiplies unit production cost by quantity produced
- For each (node, period) pair where production occurs

**Implementation:**
```python
production_cost = sum(
    prod_cost.get((i, t), 0) * value(model.Prod[i, t])
    for i in model.N 
    for t in model.T
    if value(model.Prod[i, t]) > 0
)
```

**Data Source:** `production.csv` column `prod_cost`

**Units:** ₹/unit × units = ₹

---

### 2. Inventory Cost

**Equation:**
$$\text{Inventory Cost} = \sum_{n \in N} \sum_{t \in T} \text{inv\_cost}[n] \times \text{Inv}[n,t]$$

**Description:**
- Sum over all nodes (n) and time periods (t)
- Multiplies unit inventory holding cost by quantity held
- Inventory cost per node is constant across periods

**Implementation:**
```python
inventory_cost = sum(
    inv_cost.get(n, 0) * value(model.Inv[n, t])
    for n in model.N 
    for t in model.T
    if value(model.Inv[n, t]) > 0
)
```

**Data Source:** `nodes.csv` column `inv_cost`

**Units:** ₹/unit × units = ₹

---

### 3. Transport Variable Cost

**Equation:**
$$\text{Transport Variable Cost} = \sum_{(i,j,m) \in \text{ARCS}} \sum_{t \in T} \text{trans\_cost}[i,j,m] \times X[i,j,m,t]$$

**Description:**
- Sum over all routes/modes (i,j,m) and time periods (t)
- Multiplies unit transport cost by quantity shipped
- Cost varies by origin-destination-mode combination

**Implementation:**
```python
transport_variable_cost = sum(
    trans_cost.get((i, j, m), 0) * value(model.X[i, j, m, t])
    for (i, j, m) in model.ARCS 
    for t in model.T
    if value(model.X[i, j, m, t]) > 0
)
```

**Data Source:** `arcs.csv` column `trans_cost`

**Units:** ₹/unit × units = ₹

---

### 4. Trip Fixed Cost

**Equation:**
$$\text{Trip Fixed Cost} = \sum_{(i,j,m) \in \text{ARCS}} \sum_{t \in T} \text{trip\_fixed\_cost} \times \text{Trips}[i,j,m,t]$$

**Description:**
- Sum over all routes/modes (i,j,m) and time periods (t)
- Fixed cost per trip regardless of quantity
- Currently hardcoded at 0.01 per trip

**Implementation:**
```python
trip_cost = sum(
    0.01 * value(model.Trips[i, j, m, t])
    for (i, j, m) in model.ARCS 
    for t in model.T
    if value(model.Trips[i, j, m, t]) > 0
)
```

**Constant:** 0.01 (configurable)

**Units:** ₹/trip × trips = ₹

---

### 5. Total Transport Cost

**Equation:**
$$\text{Transport Cost} = \text{Transport Variable Cost} + \text{Trip Fixed Cost}$$

**Implementation:**
```python
transport_cost = transport_variable_cost + trip_cost
```

---

## Total Cost

### Aggregated Total

**Equation:**
$$\text{Total Cost} = \text{Production Cost} + \text{Inventory Cost} + \text{Transport Cost}$$

**Implementation:**
```python
total_cost_computed = production_cost + inventory_cost + transport_cost
```

### Solver Objective

**Equation:**
$$\text{Total Cost (Objective)} = \text{value}(\text{model.OBJ})$$

**Implementation:**
```python
total_cost_objective = float(value(model.OBJ))
```

---

## Validation

### Variance Calculation

**Equation:**
$$\text{Variance} = |\text{Total Cost (Computed)} - \text{Total Cost (Objective)}|$$

**Implementation:**
```python
cost_variance = abs(total_cost_computed - total_cost_objective)
```

### Validity Check

**Equation:**
$$\text{breakdown\_valid} = \begin{cases} 
\text{true} & \text{if Variance} < 1.0 \\
\text{false} & \text{otherwise}
\end{cases}$$

**Implementation:**
```python
breakdown_valid = (cost_variance < 1.0)
```

---

## Cost Percentages

### Percentage of Total

**Equation:**
$$\text{Component \%} = \frac{\text{Component Cost}}{\text{Total Cost}} \times 100\%$$

**Examples:**
```
Production %   = (2,500,000 / 4,250,000) × 100 = 58.82%
Inventory %    = (750,000 / 4,250,000) × 100 = 17.65%
Transport %    = (1,000,000 / 4,250,000) × 100 = 23.53%
```

---

## Key Variables

### Decision Variables (from Pyomo model)

| Variable | Domain | Description |
|----------|--------|-------------|
| Prod[i,t] | NonNegativeReals | Production quantity at node i in period t |
| Inv[n,t] | NonNegativeReals | Inventory quantity at node n in period t |
| X[i,j,m,t] | NonNegativeReals | Quantity shipped from i to j via mode m in period t |
| Trips[i,j,m,t] | NonNegativeIntegers | Number of trips from i to j via mode m in period t |

### Cost Parameters (from input data)

| Parameter | Source | Description |
|-----------|--------|-------------|
| prod_cost[i,t] | production.csv | Cost per unit to produce at node i in period t |
| inv_cost[n] | nodes.csv | Cost per unit to hold inventory at node n |
| trans_cost[i,j,m] | arcs.csv | Cost per unit to ship via route (i,j,m) |
| trip_fixed_cost | Constant (0.01) | Fixed cost per trip |

---

## Mathematical Notation

| Symbol | Meaning |
|--------|---------|
| N | Set of nodes |
| T | Set of time periods |
| ARCS | Set of (origin, destination, mode) tuples |
| i, j | Node indices |
| m | Transportation mode |
| t | Time period |
| Σ | Summation operator |
| × | Multiplication |
| value() | Pyomo function to extract solved value |

---

## Properties

### 1. Linearity
All cost components are linear in the decision variables:
- No quadratic or nonlinear terms
- Suitable for MILP solver

### 2. Additivity
Total cost is strictly additive:
```
Total = Production + Inventory + Transport
```

### 3. Decomposability
Each component can be computed independently:
```python
production_cost = f(Prod, prod_cost)
inventory_cost = f(Inv, inv_cost)
transport_cost = f(X, Trips, trans_cost, trip_fixed_cost)
```

### 4. Verifiability
Computed total must match solver objective (within tolerance):
```
|computed_total - objective_total| < 1.0 ✓
```

---

## Example Calculation

### Given Data

**Production:**
- Plant A, Period 1: prod_cost = ₹100/unit, Prod = 500 units

**Inventory:**
- Plant A, Period 1: inv_cost = ₹50/unit, Inv = 150 units

**Transport:**
- Route (Plant-A, Warehouse-N, Rail): 
  - trans_cost = ₹10/unit, X = 450 units
  - Trips = 2, trip_fixed_cost = ₹0.01

### Calculation

**Production Cost:**
```
= 100 × 500 = ₹50,000
```

**Inventory Cost:**
```
= 50 × 150 = ₹7,500
```

**Transport Variable Cost:**
```
= 10 × 450 = ₹4,500
```

**Trip Cost:**
```
= 0.01 × 2 = ₹0.02
```

**Transport Cost:**
```
= 4,500 + 0.02 = ₹4,500.02
```

**Total Cost:**
```
= 50,000 + 7,500 + 4,500.02
= ₹62,000.02
```

### Verification

**Solver Objective:** ₹62,000.02 (from model.OBJ)

**Computed Total:** ₹62,000.02

**Variance:** |62,000.02 - 62,000.02| = ₹0.00 ✅

**Valid:** ₹0.00 < ₹1.0 → TRUE ✅

---

## Solver Objective Function

The Pyomo model defines the objective as:

```python
def total_cost(model):
    prod_cost_term = sum(
        prod_cost.get((i, t), 0) * model.Prod[i, t]
        for i in model.N for t in model.T
    )
    inv_cost_term = sum(
        inv_cost[i] * model.Inv[i, t]
        for i in model.N for t in model.T
    )
    transport_cost = sum(
        trans_cost[(i, j, m)] * model.X[i, j, m, t]
        for (i, j, m) in model.ARCS for t in model.T
    )
    trip_cost_term = sum(
        trip_fixed_cost * model.Trips[i, j, m, t]
        for (i, j, m) in model.ARCS for t in model.T
    )
    return prod_cost_term + inv_cost_term + transport_cost + trip_cost_term

model.OBJ = Objective(rule=total_cost, sense=minimize)
```

This exactly matches the cost breakdown computation, ensuring perfect alignment.

---

## Notes

1. **Rounding**: All costs rounded to 2 decimal places in JSON response
2. **Precision**: Internal computation uses full floating-point precision
3. **Tolerance**: Variance threshold of 1.0 accounts for solver rounding errors
4. **Optimization**: Sum only over non-zero quantities for computational efficiency
