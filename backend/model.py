# model.py
# Core optimization model for clinker supply chain
# Author: Member 1 (Core Model)

import pandas as pd
from pyomo.environ import *

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

import os

def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    nodes = pd.read_csv(os.path.join(DATA_DIR, "nodes.csv"))
    periods = pd.read_csv(os.path.join(DATA_DIR, "periods.csv"))
    production = pd.read_csv(os.path.join(DATA_DIR, "production.csv"))
    demand = pd.read_csv(os.path.join(DATA_DIR, "demand.csv"))
    arcs = pd.read_csv(os.path.join(DATA_DIR, "arcs.csv"))
    scenarios = pd.read_csv(os.path.join(DATA_DIR, "scenarios.csv"))

    return nodes, periods, production, demand, arcs, scenarios

# --------------------------------------------------
# BUILD MODEL
# --------------------------------------------------

def build_model():

    nodes, periods, production, demand, arcs, scenarios = load_data()

    model = ConcreteModel()

    # ------------------------
    # SETS
    # ------------------------
    model.N = Set(initialize=nodes["node_id"].tolist())
    model.T = Set(initialize=periods["period_id"].tolist())
    model.S = Set(initialize=scenarios["scenario"].tolist())

    model.ARCS = Set(
        initialize=[(r['origin'], r['dest'], r['mode']) for _, r in arcs.iterrows()],
        dimen=3
    )

    # ------------------------
    # PARAMETERS
    # ------------------------
    prod_cap = production.set_index(["node_id", "period_id"])["prod_cap"].to_dict()
    prod_cost = production.set_index(["node_id", "period_id"])["prod_cost"].to_dict()

    demand_dict = demand.set_index(["node_id", "period_id"])["demand"].to_dict()
    scenario_mult = scenarios.set_index("scenario")["demand_multiplier"].to_dict()

    inv_init = nodes.set_index("node_id")["inv_init"].to_dict()
    inv_max = nodes.set_index("node_id")["inv_max"].to_dict()
    inv_cost = nodes.set_index("node_id")["inv_cost"].to_dict()
    safety_stock = nodes.set_index("node_id")["safety_stock"].to_dict()

    trip_cap = arcs.set_index(["origin", "dest", "mode"])["trip_cap"].to_dict()
    trans_cost = arcs.set_index(["origin", "dest", "mode"])["trans_cost"].to_dict()
    max_trips = arcs.set_index(["origin", "dest", "mode"])["max_trips"].to_dict()

    # ------------------------
    # DECISION VARIABLES
    # ------------------------
    model.Prod = Var(model.N, model.T, domain=NonNegativeReals)
    model.Inv = Var(model.N, model.T, domain=NonNegativeReals)
    model.X = Var(model.ARCS, model.T, domain=NonNegativeReals)
    model.Trips = Var(model.ARCS, model.T, domain=NonNegativeIntegers)

    # ------------------------
    # OBJECTIVE FUNCTION
    # ------------------------
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
            for (i, j, m) in model.ARCS
            for t in model.T
        )

        return prod_cost_term + inv_cost_term + transport_cost

    model.OBJ = Objective(rule=total_cost, sense=minimize)

    # ------------------------
    # CONSTRAINTS
    # ------------------------

    # Production capacity
    def prod_limit(model, i, t):
        return model.Prod[i, t] <= prod_cap.get((i, t), 0)
    model.ProdLimit = Constraint(model.N, model.T, rule=prod_limit)

    # Inventory balance
    def inventory_balance(model, n, t):
        inflow = sum(model.X[i, n, m, t] for (i, n2, m) in model.ARCS if n2 == n)
        outflow = sum(model.X[n, j, m, t] for (n2, j, m) in model.ARCS if n2 == n)

        prev_inv = inv_init[n] if t == min(model.T) else model.Inv[n, t - 1]

        demand_t = demand_dict.get((n, t), 0)

        return prev_inv + model.Prod[n, t] + inflow - outflow == demand_t + model.Inv[n, t]

    model.InventoryBalance = Constraint(model.N, model.T, rule=inventory_balance)

    # Safety stock
    def safety_stock_rule(model, n, t):
        return model.Inv[n, t] >= safety_stock[n]

    model.SafetyStock = Constraint(model.N, model.T, rule=safety_stock_rule)

    # Trip capacity
    def trip_capacity(model, i, j, m, t):
        return model.X[i, j, m, t] <= trip_cap[(i, j, m)] * model.Trips[i, j, m, t]

    model.TripCap = Constraint(model.ARCS, model.T, rule=trip_capacity)

    return model


# --------------------------------------------------
# SOLVER
# --------------------------------------------------

def solve_model():
    model = build_model()
    solver = SolverFactory(
    "glpk",
    executable=r"glpsol"
)   # or cbc
    result = solver.solve(model, tee=True)

    print("Solver Status:", result.solver.status)
    print("Termination:", result.solver.termination_condition)

    # ------------------------
    # PRINT RESULTS
    # ------------------------

    print("\n================= SOLUTION SUMMARY =================")

    # Objective value
    print("\n=== TOTAL COST ===")
    print(f"Total Cost = {value(model.OBJ)}")

    # Production
    print("\n=== PRODUCTION (Prod[i,t]) ===")
    for i in model.N:
        for t in model.T:
            val = model.Prod[i, t].value
            if val is not None and val > 0:
                print(f"Prod[{i}, {t}] = {val}")

    # Inventory
    print("\n=== INVENTORY (Inv[n,t]) ===")
    for n in model.N:
        for t in model.T:
            val = model.Inv[n, t].value
            if val is not None:
                print(f"Inv[{n}, {t}] = {val}")

    # Shipments
    print("\n=== SHIPMENTS (X[o,d,m,t]) ===")
    for (i, j, m) in model.ARCS:
        for t in model.T:
            val = model.X[i, j, m, t].value
            if val is not None and val > 0:
                print(f"Ship[{i} -> {j}, {m}, {t}] = {val}")

    # Trips
    print("\n=== TRIPS (Trips[o,d,m,t]) ===")
    for (i, j, m) in model.ARCS:
        for t in model.T:
            val = model.Trips[i, j, m, t].value
            if val is not None and val > 0:
                print(f"Trips[{i} -> {j}, {m}, {t}] = {val}")

    print("\n================= END OF SOLUTION =================\n")

    return model


if __name__ == "__main__":
    solve_model()
