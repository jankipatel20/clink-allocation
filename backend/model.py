import pandas as pd
from backend.config import get_solver   
from pyomo.environ import (
    ConcreteModel, Set, Var, Objective, Constraint,
    NonNegativeReals, NonNegativeIntegers,
    SolverFactory, TerminationCondition
)

# ==================================================
# BUILD MODEL (TEAM CAN EDIT THIS FREELY)
# ==================================================
def build_model(
    demand_df, capacity_df, prod_cost_df, logistics_df,
    constraint_df, opening_df, closing_df, type_df
):

    model = ConcreteModel()

    model.N = Set(initialize=demand_df["IUGU CODE"].unique().tolist())
    model.T = Set(initialize=sorted(demand_df["TIME PERIOD"].unique().tolist()))

    model.ARCS = Set(
        initialize=[(r["FROM IU CODE"], r["TO IUGU CODE"], r["TRANSPORT CODE"])
                    for _, r in logistics_df.iterrows()],
        dimen=3
    )

    T_first, T_last = min(model.T), max(model.T)

    # ---------------- PARAMETERS ----------------
    demand = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["DEMAND"].to_dict()
    min_fulfill = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["MIN FULFILLMENT (%)"].fillna(1).to_dict()

    prod_cap  = capacity_df.set_index(["IU CODE","TIME PERIOD"])["CAPACITY"].to_dict()
    prod_cost = prod_cost_df.set_index(["IU CODE","TIME PERIOD"])["PRODUCTION COST"].to_dict()

    inv_open  = opening_df.set_index("IUGU CODE")["OPENING STOCK"].to_dict()
    inv_close = closing_df.set_index("IUGU CODE")["CLOSING STOCK"].fillna(0).to_dict()

    inv_max = constraint_df.set_index("IUGU CODE")["MAX INVENTORY"].replace(0,1e9).fillna(1e9).to_dict()
    safety_stock = constraint_df.set_index("IUGU CODE")["SAFETY STOCK"].fillna(0).to_dict()
    node_type = type_df.set_index("IUGU CODE")["NODE TYPE"].to_dict()

    trans_cost = logistics_df.set_index(
        ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE"]
    )[["FREIGHT COST","HANDLING COST"]].sum(axis=1).to_dict()

    trip_cap = logistics_df.set_index(
        ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE"]
    )["QUANTITY MULTIPLIER"].to_dict()

    max_trips = logistics_df.set_index(
        ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE"]
    )["MAX TRIPS"].to_dict()

    # ---------------- VARIABLES ----------------
    model.Prod = Var(model.N, model.T, domain=NonNegativeReals)
    model.Inv  = Var(model.N, model.T, domain=NonNegativeReals)
    model.X    = Var(model.ARCS, model.T, domain=NonNegativeReals)
    model.Trips = Var(model.ARCS, model.T, domain=NonNegativeIntegers)

    # ---------------- OBJECTIVE ----------------
    model.OBJ = Objective(
        expr=
        sum(prod_cost.get((n,t),0)*model.Prod[n,t] for n in model.N for t in model.T)
        + sum(trans_cost.get((i,j,m),0)*model.X[i,j,m,t] for (i,j,m) in model.ARCS for t in model.T),
        sense=minimize
    )

    # ---------------- CONSTRAINTS ----------------
    model.ProdCap = Constraint(
        model.N, model.T,
        rule=lambda m,n,t: m.Prod[n,t] <= prod_cap.get((n,t),0)
    )

    model.GU_NoProd = Constraint(
        model.N, model.T,
        rule=lambda m,n,t: m.Prod[n,t]==0 if node_type[n]=="GU" else Constraint.Skip
    )

    def inv_bal(m,n,t):
        prev = inv_open.get(n,0) if t==T_first else m.Inv[n,t-1]
        inflow  = sum(m.X[i,n,m2,t] for (i,n2,m2) in m.ARCS if n2==n)
        outflow = sum(m.X[n,j,m2,t] for (n2,j,m2) in m.ARCS if n2==n)
        return prev + m.Prod[n,t] + inflow - outflow == demand[(n,t)] + m.Inv[n,t]

    model.InvBalance = Constraint(model.N, model.T, rule=inv_bal)

    model.InvCap = Constraint(
        model.N, model.T,
        rule=lambda m,n,t: m.Inv[n,t] <= inv_max[n]
    )

    model.Safety = Constraint(
        model.N, model.T,
        rule=lambda m,n,t: m.Inv[n,t] >= safety_stock[n]
    )

    model.CloseStock = Constraint(
        model.N,
        rule=lambda m,n: m.Inv[n,T_last] >= inv_close[n]
    )

    def min_fulfill_rule(m,n,t):
        served = sum(m.X[i,n,m2,t] for (i,n2,m2) in m.ARCS if n2==n)
        return served >= min_fulfill[(n,t)]*demand[(n,t)]

    model.MinFulfill = Constraint(model.N, model.T, rule=min_fulfill_rule)

    model.TripCap = Constraint(
        model.ARCS, model.T,
        rule=lambda m,i,j,m2,t: m.X[i,j,m2,t] <= trip_cap[(i,j,m2)]*m.Trips[i,j,m2,t]
    )

    model.MaxTrips = Constraint(
        model.ARCS, model.T,
        rule=lambda m,i,j,m2,t: m.Trips[i,j,m2,t] <= max_trips[(i,j,m2)]
    )

    return model


# ==================================================
# SINGLE BACKEND ENTRYPOINT (DO NOT CHANGE)
# ==================================================
def solve_model(data: dict):

    model = build_model(
        demand_df    = data["ClinkerDemand"],
        capacity_df  = data["ClinkerCapacity"],
        prod_cost_df = data["ProductionCost"],
        logistics_df = data["LogisticsIUGU"],
        constraint_df= data["IUGUConstraint"],
        opening_df   = data["IUGUOpeningStock"],
        closing_df   = data["IUGUClosingStock"],
        type_df      = data["IUGUType"]
    )

    solver = SolverFactory("glpk")  # safer default than cbc
    result = solver.solve(model, tee=False)

    # 🚫 DO NOT raise for infeasible / unbounded
    return model, result
