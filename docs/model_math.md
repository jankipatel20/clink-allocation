# Mathematical Formulation of the Clinker Supply Chain Optimization Model

This document presents the mathematical formulation of a **Mixed Integer Linear Programming (MILP)** model developed to optimize clinker production, transportation, and inventory management across a cement supply chain network.

The objective of the model is to minimize total operational cost while satisfying production capacity, demand fulfillment, inventory, and transportation constraints.

---

## 1. Sets and Indices

* **N** : Set of all nodes (plants), indexed by *n*  
  (Includes Integrated Units (IU) and Grinding Units (GU))

* **T** : Set of planning periods (e.g., months), indexed by *t*

* **A** : Set of transportation arcs, indexed by *(o, d, m)*  
  where *o* is origin, *d* is destination, and *m* is the transport mode

> **Note:** Integrated Units are not modeled as a separate set.  
> Production at Grinding Units is implicitly restricted by assigning zero production capacity.

---

## 2. Parameters

### Production Parameters
* **ProdCapₙₜ** : Maximum clinker production capacity at node *n* in period *t*
* **ProdCostₙₜ** : Cost per unit of clinker produced at node *n* in period *t*

### Demand Parameters
* **Demandₙₜ** : Clinker demand at node *n* in period *t*

### Inventory Parameters
* **InvInitₙ** : Initial inventory at node *n*
* **SafetyStockₙ** : Minimum safety stock required at node *n*
* **InvMaxₙ** : Maximum inventory capacity at node *n*
* **InvCostₙ** : Inventory holding cost per unit at node *n*

### Transportation Parameters
* **TransCostₒ𝒹ₘ** : Transportation cost per unit on arc *(o, d, m)*
* **TripCapₒ𝒹ₘ** : Capacity per transportation trip on arc *(o, d, m)*
* **MaxTripsₒ𝒹ₘ** : Maximum number of trips allowed on arc *(o, d, m)*

---

## 3. Decision Variables

* **Prodₙₜ ≥ 0**  
  Quantity of clinker produced at node *n* in period *t*

* **Invₙₜ ≥ 0**  
  Inventory level at node *n* at the end of period *t*

* **Xₒ𝒹ₘₜ ≥ 0**  
  Quantity of clinker transported on arc *(o, d, m)* in period *t*

* **Tripsₒ𝒹ₘₜ ∈ ℤ⁺**  
  Number of transportation trips on arc *(o, d, m)* in period *t*

---

## 4. Objective Function

The objective is to minimize the total cost across all nodes and time periods, including production, inventory holding, and transportation costs.

$$
\min \;
\sum_{n \in N} \sum_{t \in T} ProdCost_{n,t} \cdot Prod_{n,t}
+ \sum_{n \in N} \sum_{t \in T} InvCost_n \cdot Inv_{n,t}
+ \sum_{(o,d,m) \in A} \sum_{t \in T} TransCost_{o,d,m} \cdot X_{o,d,m,t}
$$

---

## 5. Constraints

### 5.1 Production Capacity Constraint

Production at each node cannot exceed its available capacity.

$$
Prod_{n,t} \leq ProdCap_{n,t}
\quad \forall n \in N,\; t \in T
$$

---

### 5.2 Inventory Balance Constraint

For each node and time period, material balance must be maintained.

**For the first period** ($t = 1$):

$$
Inv_{n,1} =
InvInit_n
+ Prod_{n,1}
+ \sum_{(o,n,m) \in A} X_{o,n,m,1}
* \sum_{(n,d,m) \in A} X_{n,d,m,1}
* Demand_{n,1}
$$

**For subsequent periods** ($t > 1$):

$$
Inv_{n,t} =
Inv_{n,t-1}
+ Prod_{n,t}
+ \sum_{(o,n,m) \in A} X_{o,n,m,t}
* \sum_{(n,d,m) \in A} X_{n,d,m,t}
* Demand_{n,t}
$$

---

### 5.3 Safety Stock Constraint

Inventory at each node must be at least the required safety stock level.

$$
Inv_{n,t} \geq SafetyStock_n
\quad \forall n \in N,\; t \in T
$$

---

### 5.4 Inventory Capacity Constraint

Inventory at each node cannot exceed its maximum storage capacity.

$$
Inv_{n,t} \leq InvMax_n
\quad \forall n \in N,\; t \in T
$$

---

### 5.5 Transportation Capacity Constraint

Shipment quantity on each arc is limited by the number of trips and per‑trip capacity.

$$
X_{o,d,m,t} \leq TripCap_{o,d,m} \cdot Trips_{o,d,m,t}
\quad \forall (o,d,m) \in A,\; t \in T
$$

---

### 5.6 Maximum Trips Constraint

The number of trips on each arc cannot exceed the allowed maximum.

$$
Trips_{o,d,m,t} \leq MaxTrips_{o,d,m}
\quad \forall (o,d,m) \in A,\; t \in T
$$

---

### 5.7 Integrality Constraint

$$
Trips_{o,d,m,t} \in \mathbb{Z}^+
\quad \forall (o,d,m) \in A,\; t \in T
$$

---

## 6. Model Notes and Assumptions

* Grinding Units do not produce clinker; this is enforced through zero production capacity.
* Integrated Units may have both production and demand.
* All costs are linear.
* Demand is deterministic for each planning run.
* Transportation routes and modes are predefined.
* The model is solved as a Mixed Integer Linear Program.

---

## 7. Conclusion

This MILP formulation enables cost‑optimal and operationally feasible clinker production and distribution decisions across the cement supply chain while respecting real‑world production, inventory, and transportation constraints.
