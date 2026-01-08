
# model.py
# Core optimization model for clinker supply chain
# Author: Member 1 (Core Model)

import pandas as pd
from pyomo.environ import *

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
# Load CSVs manually
# nodes = pd.read_csv("data/nodes.csv")
# periods = pd.read_csv("data/periods.csv")
# production = pd.read_csv("data/production.csv")
# demand = pd.read_csv("data/demand.csv")
# arcs = pd.read_csv("data/arcs.csv")
# scenarios = pd.read_csv("data/scenarios.csv")

# --------------------------------------------------
# BUILD MODEL
# --------------------------------------------------

def build_model(nodes, periods, production, demand, arcs, scenarios):

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
    trip_fixed_cost = 0.01 
    demand_dict = demand.set_index(["node_id", "period_id"])["demand"].to_dict()

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
    model.UseRoute = Var(model.ARCS, model.T, domain=Binary)


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
        trip_cost_term = sum(
        trip_fixed_cost * model.Trips[i,j,m,t]
        for (i,j,m) in model.ARCS
        for t in model.T
        )


        return prod_cost_term + inv_cost_term + transport_cost + trip_cost_term


    model.OBJ = Objective(rule=total_cost, sense=minimize)

    # ------------------------
    # CONSTRAINTS
    # ------------------------

    # Production capacity
    def prod_limit(model, i, t):
        return model.Prod[i, t] <= prod_cap.get((i, t), 0)
    model.ProdLimit = Constraint(model.N, model.T, rule=prod_limit)
    # Explicitly forbid production at Grinding Units (GU)
    node_type = nodes.set_index("node_id")["type"].to_dict()

    def gu_no_production(model, n, t):
        if node_type[n] == "GU":
            return model.Prod[n, t] == 0
        return Constraint.Skip

    model.GU_NoProduction = Constraint(model.N, model.T, rule=gu_no_production)

    # Inventory balance
    def inventory_balance(model, n, t):
        inflow = sum(model.X[i, n, m, t] for (i, n2, m) in model.ARCS if n2 == n)
        outflow = sum(model.X[n, j, m, t] for (n2, j, m) in model.ARCS if n2 == n)

        T_sorted = sorted(model.T)
        if t == T_sorted[0]:
            prev_inv = inv_init[n]
        else:
            prev_inv = model.Inv[n, T_sorted[T_sorted.index(t)-1]]

        demand_t = demand_dict.get((n, t), 0)

        return prev_inv + model.Prod[n, t] + inflow - outflow == demand_t + model.Inv[n, t]

    model.InventoryBalance = Constraint(model.N, model.T, rule=inventory_balance)

    def inv_capacity_rule(model, n, t):
        return model.Inv[n, t] <= inv_max[n]

    model.InvCapacity = Constraint(model.N, model.T, rule=inv_capacity_rule)

    
    # Safety stock
    def safety_stock_rule(model, n, t):
        return model.Inv[n, t] >= safety_stock[n]

    model.SafetyStock = Constraint(model.N, model.T, rule=safety_stock_rule)

    # Trip capacity
    def trip_capacity(model, i, j, m, t):
        return model.X[i, j, m, t] <= trip_cap[(i, j, m)] * model.Trips[i, j, m, t]

    model.TripCap = Constraint(model.ARCS, model.T, rule=trip_capacity)

    # Maximum trips constraint (FORCES integrality relevance)
    def max_trips_rule(model, i, j, m, t):
        return model.Trips[i, j, m, t] <= max_trips[(i, j, m)]

    model.MaxTrips = Constraint(model.ARCS, model.T, rule=max_trips_rule)

    # Minimum shipment batch quantity (SBQ)
    sbq = arcs.set_index(["origin", "dest", "mode"])["sbq"].to_dict()

    def sbq_rule(model, i, j, m, t):
        return model.X[i, j, m, t] >= sbq[(i, j, m)] * model.UseRoute[i, j, m, t]

    model.SBQ = Constraint(model.ARCS, model.T, rule=sbq_rule)
    
    # Upper linking constraint (activates UseRoute)
    def use_route_upper(model, i, j, m, t):
        return model.X[i, j, m, t] <= trip_cap[(i, j, m)] * max_trips[(i, j, m)] * model.UseRoute[i, j, m, t]

    model.UseRouteUpper = Constraint(model.ARCS, model.T, rule=use_route_upper)


    return model


# --------------------------------------------------
# SOLVER
# --------------------------------------------------

# def solve_model(nodes, periods, production, demand, arcs, scenarios):
#     model = build_model(nodes, periods, production, demand, arcs, scenarios)
#     solver_path = r"C:\Users\ADMIN\Downloads\winglpk-4.65\glpk-4.65\w64\glpsol.exe"
#     solver = SolverFactory("glpk" , executable=solver_path)

#     try:
#         result = solver.solve(model, tee=True)
#     except Exception as e:
#         raise RuntimeError(f"Solver execution failed: {str(e)}")

#     # ---- STRICT VALIDATION ----
#     if result.solver.status != SolverStatus.ok:
#         raise RuntimeError(
#             f"Solver failed. Status: {result.solver.status}"
#         )

#     if result.solver.termination_condition == TerminationCondition.infeasible:
#         raise ValueError("Optimization infeasible: check demand, capacity, or safety stock.")

#     if result.solver.termination_condition == TerminationCondition.unbounded:
#         raise ValueError("Optimization unbounded: missing constraints (inventory or flow).")

#     if result.solver.termination_condition != TerminationCondition.optimal:
#         raise RuntimeError(
#             f"Solver did not find optimal solution. Termination: {result.solver.termination_condition}"
#         )
        

#     return model, result

from pyomo.environ import SolverFactory, SolverStatus, TerminationCondition


def solve_model(nodes, periods, production, demand, arcs, scenarios):
    """
    Runs the clinker optimization model.

    Parameters:
        nodes, periods, production, demand, arcs, scenarios
        → Pandas DataFrames passed from backend

    Returns:
        model  : Pyomo ConcreteModel (solved or attempted)
        result : Pyomo SolverResults (status + termination condition)
    """

    # 1️⃣ Build the optimization model
    model = build_model(
        nodes=nodes,
        periods=periods,
        production=production,
        demand=demand,
        arcs=arcs,
        scenarios=scenarios,
    )

    # 2️⃣ Configure solver (CBC with fallback to GLPK)
    try:
        from backend.config import get_solver_path, get_solver_options, PREFERRED_SOLVER
        solver_name, solver_path = get_solver_path(PREFERRED_SOLVER)
        solver_options = get_solver_options(solver_name)
    except (ImportError, FileNotFoundError):
        # Fallback if config.py doesn't exist
        solver_name = 'cbc'
        solver_path = None  # Use system PATH
        solver_options = {'tee': True}
    
    # Create solver instance
    if solver_path:
        solver = SolverFactory(solver_name, executable=solver_path)
    else:
        solver = SolverFactory(solver_name)

    # 3️⃣ Solve model
    try:
        result = solver.solve(model, tee=True)
    except Exception as e:
        # REAL execution failure (missing solver, crash, etc.)
        raise RuntimeError(f"Solver execution failed: {str(e)}")

    # 4️⃣ DO NOT crash for math outcomes
    # Backend will inspect:
    #   result.solver.status
    #   result.solver.termination_condition
    #
    # Valid outcomes:
    # - optimal       → success
    # - infeasible    → business failure (not crash)
    # - unbounded     → modeling issue (backend reports failure)
    # - other         → backend reports failure

    return model, result



def run_optimizer(data: dict):
    try:
        model = solve_model(
            data["nodes"],
            data["periods"],
            data["production"],
            data["demand"],
            data["arcs"],
            data["scenarios"]
        )
        return model

    except Exception as e:
        # Let backend catch this
        raise e


# Run model
# model = solve_model(
#     nodes,
#     periods,
#     production,
#     demand,
#     arcs,
#     scenarios
# )

# print("✅ Model solved successfully")
# print("Total cost:", model.OBJ())
