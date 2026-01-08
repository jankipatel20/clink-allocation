import pandas as pd
from pyomo.environ import *


# ==================================================
# BUILD MODEL
# ==================================================
def build_model(demand_df, capacity_df, prod_cost_df, logistics_df,
                constraint_df, opening_df, closing_df, type_df):

    model = ConcreteModel()

    model.N = Set(initialize=demand_df["IUGU CODE"].astype(str).unique().tolist())
    model.T = Set(initialize=sorted(demand_df["TIME PERIOD"].unique().tolist()))

    model.ARCS = Set(
        initialize=[(
            str(r["FROM IU CODE"]),
            str(r["TO IUGU CODE"]),
            r["TRANSPORT CODE"],
            r["TIME PERIOD"]
        ) for _, r in logistics_df.iterrows()],
        dimen=4
    )

    T_first, T_last = min(model.T), max(model.T)

    # ---------------- PARAMETERS ----------------
        # ---------------- PARAMETERS ----------------

    # Demand + minimum fulfillment
    demand = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["DEMAND"].to_dict()

    if "MIN FULFILLMENT (%)" in demand_df.columns:
        min_fulfill = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["MIN FULFILLMENT (%)"].fillna(1).to_dict()
    else:
        min_fulfill = {(n,t):1 for (n,t) in demand}

    # Production
    prod_cap  = capacity_df.set_index(["IU CODE","TIME PERIOD"])["CAPACITY"].to_dict()
    prod_cost = prod_cost_df.set_index(["IU CODE","TIME PERIOD"])["PRODUCTION COST"].to_dict()

    # Opening stock
    inv_open = opening_df.set_index("IUGU CODE")["OPENING STOCK"].fillna(0).to_dict()

    # Closing stock (optional)
    if "CLOSING STOCK" in closing_df.columns:
        inv_close = closing_df.set_index("IUGU CODE")["CLOSING STOCK"].fillna(0).to_dict()
    else:
        inv_close = {}

    # Max inventory (optional, NULL = infinite)
    if "MAX INVENTORY" in constraint_df.columns:
        inv_max = constraint_df.set_index("IUGU CODE")["MAX INVENTORY"].to_dict()
    else:
        inv_max = {}

    # Safety stock (optional)
    if "SAFETY STOCK" in constraint_df.columns:
        safety_stock = constraint_df.set_index("IUGU CODE")["SAFETY STOCK"].fillna(0).to_dict()
    else:
        safety_stock = {}

   
    # Node type (IU / GU) — optional
    if "NODE TYPE" in type_df.columns:
        node_type = type_df.set_index("IUGU CODE")["NODE TYPE"].to_dict()
    else:
        node_type = {n: "IU" for n in model.N}   # assume all are IU


    # Transportation
    trans_cost = logistics_df.set_index(
        ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE","TIME PERIOD"]
    )["FREIGHT COST"].to_dict()

    trip_cap = logistics_df.set_index(
        ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE","TIME PERIOD"]
    )["QUANTITY MULTIPLIER"].to_dict()


    if "MAX TRIPS" in logistics_df.columns:
        max_trips = logistics_df.set_index(
            ["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE"]
        )["MAX TRIPS"].fillna(1e9).to_dict()
    else:
        max_trips = {
            (r["FROM IU CODE"], r["TO IUGU CODE"], r["TRANSPORT CODE"]): 1e9
            for _, r in logistics_df.iterrows()
        }



    # ---------------- VARIABLES ----------------
    model.Prod = Var(model.N, model.T, domain=NonNegativeReals)
    model.Inv  = Var(model.N, model.T, domain=NonNegativeReals)
    model.X = Var(model.ARCS, domain=NonNegativeReals)
    model.Trips = Var(model.ARCS, domain=NonNegativeIntegers)


    # ---------------- OBJECTIVE ----------------
    model.OBJ = Objective(
        expr=
        sum(prod_cost.get((n,t),0)*model.Prod[n,t] for n in model.N for t in model.T)
        + sum(trans_cost.get((i,j,m),0)*model.X[i,j,m,t] for (i,j,m) in model.ARCS for t in model.T),
        sense=minimize
    )

    # ---------------- CONSTRAINTS ----------------
    model.ProdCap = Constraint(model.N,model.T,
        rule=lambda m,n,t: m.Prod[n,t] <= prod_cap.get((n,t),0))

    def gu_no_prod(m,n,t):
        if node_type.get(n,"IU") == "GU":
            return m.Prod[n,t] == 0
        return Constraint.Skip

    model.GU_NoProd = Constraint(model.N, model.T, rule=gu_no_prod)


    def inv_bal(m,n,t):
        prev = inv_open.get(n,0) if t==T_first else m.Inv[n,t-1]
        inflow  = sum(m.X[i,n,m2,tt] for (i,n2,m2,tt) in m.ARCS if n2==n and tt==t)
        outflow = sum(m.X[n,j,m2,tt] for (n2,j,m2,tt) in m.ARCS if n2==n and tt==t)
        return prev + m.Prod[n,t] + inflow - outflow == demand.get((n,t),0) + m.Inv[n,t]
    model.InvBalance = Constraint(model.N,model.T,rule=inv_bal)
    def inv_cap_rule(m,n,t):
        if n not in inv_max or pd.isna(inv_max[n]):
            return Constraint.Skip     # infinite capacity
        return m.Inv[n,t] <= inv_max[n]

    model.InvCap = Constraint(model.N, model.T, rule=inv_cap_rule)



    model.Safety = Constraint(model.N,model.T,
        rule=lambda m,n,t: m.Inv[n,t] >= safety_stock.get(n,0))

    model.CloseStock = Constraint(model.N,
        rule=lambda m,n: m.Inv[n,T_last] >= inv_close.get(n,0))

    def min_fulfill_rule(m,n,t):
        served = sum(m.X[i,n,m2,tt] for (i,n2,m2,tt) in m.ARCS if n2==n and tt==t)
        return served >= min_fulfill.get((n,t),0) * demand.get((n,t),0)
    model.MinFulfill = Constraint(model.N,model.T,rule=min_fulfill_rule)

    model.TripCap = Constraint(model.ARCS,
        rule=lambda m,i,j,m2,t: m.X[i,j,m2,t] <= trip_cap.get((i,j,m2,t),0)*m.Trips[i,j,m2,t])


    model.MaxTrips = Constraint(model.ARCS,
        rule=lambda m,i,j,m2,t: m.Trips[i,j,m2,t] <= max_trips.get((i,j,m2),1e9))


    return model


# ==================================================
# SINGLE BACKEND ENTRYPOINT
# ==================================================
from pyomo.environ import SolverFactory, SolverStatus, TerminationCondition, value

from pyomo.environ import SolverFactory, TerminationCondition, value

def run_optimizer(data):

    try:
        model = build_model(**data)
        solver = SolverFactory("cbc")
        result = solver.solve(model, tee=False)

        # ❌ failure cases
        if result.solver.termination_condition != TerminationCondition.optimal:
            return {
                "success": False,
                "message": str(result.solver.termination_condition),
                "total_cost": None,
                "model_obj": None
            }

        # 🔍 DEBUG PRINTS
        print("\n================= MODEL DEBUG =================")
        print("Objective value:", value(model.OBJ))

        print("\n--- Production ---")
        for n in model.N:
            for t in model.T:
                if model.Prod[n,t].value is not None and model.Prod[n,t].value > 0:
                    print(f"Prod[{n},{t}] = {model.Prod[n,t].value}")

        print("\n--- Inventory ---")
        for n in model.N:
            for t in model.T:
                if model.Inv[n,t].value is not None and model.Inv[n,t].value > 0:
                    print(f"Inv[{n},{t}] = {model.Inv[n,t].value}")

        print("\n--- Shipments ---")
        for (i,j,m2,t) in model.ARCS:
            if model.X[i,j,m2,t].value and model.X[i,j,m2,t].value > 0:
                print(f"X[{i}->{j},{m2},{t}] = {model.X[i,j,m2,t].value}")

        print("\n=============================================\n")

        # ✅ SUCCESS RETURN
        return {
            "success": True,
            "message": "Optimal solution found",
            "total_cost": float(value(model.OBJ)),
            "model_obj": model
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "total_cost": None,
            "model_obj": None
        }


FILE = "data/dataset.xlsx"   # change path if needed

xls = pd.ExcelFile(FILE)

data = {
    "demand_df":     pd.read_excel(xls, "ClinkerDemand"),
    "capacity_df":   pd.read_excel(xls, "ClinkerCapacity"),
    "prod_cost_df":  pd.read_excel(xls, "ProductionCost"),
    "logistics_df":  pd.read_excel(xls, "LogisticsIUGU"),
    "constraint_df": pd.read_excel(xls, "IUGUConstraint"),
    "opening_df":    pd.read_excel(xls, "IUGUOpeningStock"),
    "closing_df":    pd.read_excel(xls, "IUGUClosingStock"),
    "type_df":       pd.read_excel(xls, "IUGUType"),
}


result = run_optimizer(data)

print("\n=========== RESULT ===========")
print("Success :", result["success"])
print("Message :", result["message"])
print("Total Cost :", result["total_cost"])

