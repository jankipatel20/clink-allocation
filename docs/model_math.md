# Mathematical Formulation of the Clinker Supply Chain Optimization Model

This document presents the mathematical formulation of a **Mixed Integer Linear Programming (MILP)** model developed to optimize clinker production, transportation, and inventory management across a cement supply chain network.

The objective of the model is to minimize total operational cost while satisfying production capacity, demand fulfillment, inventory, and transportation constraints.

---

## 1. Sets and Indices

- **N**: Set of all nodes (plants), indexed by $n$  
  (Includes Integrated Units (IU) and Grinding Units (GU))
- **T**: Set of planning periods (e.g., months), indexed by $t$
- **A**: Set of transportation arcs, indexed by $(o, d, m)$  
  where $o$ is origin, $d$ is destination, and $m$ is the transport mode

**Note:** Integrated Units are not modeled as a separate set. Production at Grinding Units is implicitly restricted by assigning zero production capacity.

---

## 2. Parameters

### Production Parameters
- $\text{ProdCap}_{n,t}$: Maximum clinker production capacity at node $n$ in period $t$
- $\text{ProdCost}_{n,t}$: Cost per unit of clinker produced at node $n$ in period $t$

### Demand Parameters
- $\text{Demand}_{n,t}$: Clinker demand at node $n$ in period $t$

### Inventory Parameters
- $\text{InvInit}_n$: Initial inventory at node $n$
- $\text{SafetyStock}_n$: Minimum safety stock required at node $n$
- $\text{InvMax}_n$: Maximum inventory capacity at node $n$
- $\text{InvCost}_n$: Inventory holding cost per unit at node $n$

### Transportation Parameters
- $\text{TransCost}_{o,d,m}$: Transportation cost per unit on arc $(o,d,m)$
- $\text{TripCap}_{o,d,m}$: Capacity per transportation trip on arc $(o,d,m)$
- $\text{MaxTrips}_{o,d,m}$: Maximum number of trips allowed on arc $(o,d,m)$

---

## 3. Decision Variables

- $\text{Prod}_{n,t} \ge 0$  
  Quantity of clinker produced at node $n$ in period $t$

- $\text{Inv}_{n,t} \ge 0$  
  Inventory level at node $n$ at the end of period $t$

- $X_{o,d,m,t} \ge 0$  
  Quantity of clinker transported on arc $(o,d,m)$ in period $t$

- $\text{Trips}_{o,d,m,t} \in \mathbb{Z}^+$  
  Number of transportation trips on arc $(o,d,m)$ in period $t$

---

## 4. Objective Function

The objective is to minimize total cost, including production, inventory holding, and transportation costs.

$$
\min \sum_{n \in N} \sum_{t \in T} \text{ProdCost}_{n,t} \cdot \text{Prod}_{n,t} + \sum_{n \in N} \sum_{t \in T} \text{InvCost}_n \cdot \text{Inv}_{n,t} + \sum_{(o,d,m) \in A} \sum_{t \in T} \text{TransCost}_{o,d,m} \cdot X_{o,d,m,t}
$$

---

## 5. Constraints

### 5.1 Production Capacity Constraint

Production at each node cannot exceed its available capacity.

$$
\text{Prod}_{n,t} \le \text{ProdCap}_{n,t} \quad \forall n \in N, t \in T
$$

---

### 5.2 Inventory Balance Constraint

For each node and time period, material balance must be maintained.

**For the first period** $(t = 1)$:

$$
\text{Inv}_{n,1} = \text{InvInit}_n + \text{Prod}_{n,1} + \sum_{(o,n,m) \in A} X_{o,n,m,1} - \sum_{(n,d,m) \in A} X_{n,d,m,1} - \text{Demand}_{n,1}
$$

**For subsequent periods** $(t > 1)$:

$$
\text{Inv}_{n,t} = \text{Inv}_{n,t-1} + \text{Prod}_{n,t} + \sum_{(o,n,m) \in A} X_{o,n,m,t} - \sum_{(n,d,m) \in A} X_{n,d,m,t} - \text{Demand}_{n,t}
$$

---

### 5.3 Safety Stock Constraint

Inventory at each node must be at least the required safety stock level.

$$
\text{Inv}_{n,t} \ge \text{SafetyStock}_n \quad \forall n \in N, t \in T
$$

---

### 5.4 Inventory Capacity Constraint

Inventory at each node cannot exceed its maximum storage capacity.

$$
\text{Inv}_{n,t} \le \text{InvMax}_n \quad \forall n \in N, t \in T
$$

---

### 5.5 Transportation Capacity Constraint

Shipment quantity on each arc is limited by the number of trips and per-trip capacity.

$$
X_{o,d,m,t} \le \text{TripCap}_{o,d,m} \cdot \text{Trips}_{o,d,m,t} \quad \forall (o,d,m) \in A, t \in T
$$

---

### 5.6 Maximum Trips Constraint

The number of trips on each arc cannot exceed the allowed maximum.

$$
\text{Trips}_{o,d,m,t} \le \text{MaxTrips}_{o,d,m} \quad \forall (o,d,m) \in A, t \in T
$$

---

### 5.7 Integrality Constraint

$$
\text{Trips}_{o,d,m,t} \in \mathbb{Z}^+ \quad \forall (o,d,m) \in A, t \in T
$$

---

## 6. Model Notes and Assumptions

- Grinding Units do not produce clinker; this is enforced through zero production capacity.
- Integrated Units may have both production and demand.
- All costs are linear.
- Demand is deterministic for each planning run.
- Transportation routes and modes are predefined.
- The model is solved as a Mixed Integer Linear Program.

---

## 7. Conclusion

This MILP formulation enables cost-optimal and operationally feasible clinker production and distribution decisions across the cement supply chain while respecting real-world production, inventory, and transportation constraints.
