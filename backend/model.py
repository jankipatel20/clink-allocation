import pandas as pd
import math
from pyomo.environ import (
    ConcreteModel, Set, Var,
    NonNegativeReals, NonNegativeIntegers,
    Objective, Constraint, minimize,
    SolverFactory, value, TerminationCondition
)

# ==================================================
# CONFIGURATION
# ==================================================
SETTINGS = {
    "ENABLE_MIN_FULFILL": True,
    "UNMET_PENALTY": 10_000_000,
    "HOLDING_COST": 0.5,
    "DEFAULT_LEAD_TIME": 1
}

# ==================================================
# MAIN SOLVER FUNCTION (BACKEND SAFE)
# ==================================================
def run_clinker_optimization(file_path):

    try:
        # ------------------------------
        # LOAD DATA
        # ------------------------------
        xls = pd.ExcelFile(file_path)

        demand_df    = pd.read_excel(xls, "ClinkerDemand")
        capacity_df  = pd.read_excel(xls, "ClinkerCapacity")
        prod_cost_df = pd.read_excel(xls, "ProductionCost")
        logistics_df = pd.read_excel(xls, "LogisticsIUGU")
        opening_df   = pd.read_excel(xls, "IUGUOpeningStock")
        type_df      = pd.read_excel(xls, "IUGUType")

        # ------------------------------
        # CLEAN CODES
        # ------------------------------
        for df in [demand_df, capacity_df, prod_cost_df,
                   logistics_df, opening_df, type_df]:
            for c in df.columns:
                if "CODE" in c or "TYPE" in c:
                    df[c] = df[c].astype(str).str.strip()

        # ------------------------------
        # SETS
        # ------------------------------
        T = sorted(demand_df["TIME PERIOD"].unique())

        IU = type_df[type_df["PLANT TYPE"] == "IU"]["IUGU CODE"].tolist()
        GU = type_df[type_df["PLANT TYPE"] == "GU"]["IUGU CODE"].tolist()
        ALL_NODES = list(set(IU) | set(GU))

        # ------------------------------
        # REMOVE EXT / INVALID NODES
        # ------------------------------
        logistics_df = logistics_df[
            logistics_df["FROM IU CODE"].isin(IU) &
            logistics_df["TO IUGU CODE"].isin(ALL_NODES)
        ]

        ARCS = list({
            (r["FROM IU CODE"], r["TO IUGU CODE"], r["TRANSPORT CODE"])
            for _, r in logistics_df.iterrows()
            if r["FROM IU CODE"] != r["TO IUGU CODE"]
        })

        # ------------------------------
        # PARAMETERS
        # ------------------------------
        demand = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["DEMAND"].fillna(0).to_dict()
        min_fulfill = demand_df.set_index(["IUGU CODE","TIME PERIOD"])["MIN FULFILLMENT (%)"].fillna(0).to_dict()
        prod_cap = capacity_df.set_index(["IU CODE","TIME PERIOD"])["CAPACITY"].fillna(0).to_dict()
        prod_cost = prod_cost_df.set_index(["IU CODE","TIME PERIOD"])["PRODUCTION COST"].fillna(0).to_dict()
        inv_open = opening_df.set_index("IUGU CODE")["OPENING STOCK"].fillna(0).to_dict()

        log_idx = logistics_df.set_index(["FROM IU CODE","TO IUGU CODE","TRANSPORT CODE"])
        trip_cap = log_idx["QUANTITY MULTIPLIER"].fillna(0).to_dict()
        trip_cost = (log_idx["FREIGHT COST"] + log_idx["HANDLING COST"]).fillna(0).to_dict()
        lead_time = (
            log_idx["LEAD TIME"].fillna(SETTINGS["DEFAULT_LEAD_TIME"]).astype(int).to_dict()
            if "LEAD TIME" in log_idx else {}
        )

        # ------------------------------
        # MAX TRIPS
        # ------------------------------
        incoming = {(n,t):0 for n in ALL_NODES for t in T}
        for (_,j,_) in ARCS:
            for t in T:
                incoming[(j,t)] += 1

        max_trips = {}
        for (i,j,m) in ARCS:
            cap = trip_cap.get((i,j,m),0)
            for t in T:
                dem = demand.get((j,t),0)
                routes = max(incoming[(j,t)],1)
                max_trips[(i,j,m,t)] = math.ceil(dem/(routes*cap)) if cap>0 else 0

        # ==================================================
        # PYOMO MODEL
        # ==================================================
        model = ConcreteModel()

        model.T = Set(initialize=T, ordered=True)
        model.IU = Set(initialize=IU)
        model.N = Set(initialize=ALL_NODES)
        model.ARCS = Set(dimen=3, initialize=ARCS)

        model.Prod = Var(model.IU, model.T, domain=NonNegativeReals)
        model.Inv = Var(model.N, model.T, domain=NonNegativeReals)
        model.X = Var(model.ARCS, model.T, domain=NonNegativeReals)
        model.Trips = Var(model.ARCS, model.T, domain=NonNegativeIntegers)
        model.Unmet = Var(model.N, model.T, domain=NonNegativeReals)

        # ------------------------------
        # OBJECTIVE
        # ------------------------------
        model.OBJ = Objective(
            expr=
            sum(prod_cost.get((i,t),0)*model.Prod[i,t] for i in model.IU for t in model.T)
            + sum(trip_cost.get((i,j,m),0)*model.Trips[i,j,m,t]
                  for (i,j,m) in model.ARCS for t in model.T)
            + sum(SETTINGS["HOLDING_COST"]*model.Inv[n,t] for n in model.N for t in model.T)
            + sum(SETTINGS["UNMET_PENALTY"]*model.Unmet[n,t] for n in model.N for t in model.T),
            sense=minimize
        )

        # ------------------------------
        # CONSTRAINTS
        # ------------------------------
        model.ProdCap = Constraint(
            model.IU, model.T,
            rule=lambda m,i,t: m.Prod[i,t] <= prod_cap.get((i,t),0)
        )

        def inv_balance(m,n,t):
            idx = T.index(t)
            prev = inv_open.get(n,0) if idx==0 else m.Inv[n,T[idx-1]]
            inflow = sum(
                m.X[i,n,m_,T[idx-lead_time.get((i,n,m_),1)]]
                for (i,j,m_) in m.ARCS
                if j==n and idx-lead_time.get((i,n,m_),1)>=0
            )
            outflow = sum(m.X[n,j,m_,t] for (i,j,m_) in m.ARCS if i==n)
            prod = m.Prod[n,t] if n in m.IU else 0
            return prev + prod + inflow - outflow + m.Unmet[n,t] == demand.get((n,t),0) + m.Inv[n,t]

        model.InvBalance = Constraint(model.N, model.T, rule=inv_balance)

        if SETTINGS["ENABLE_MIN_FULFILL"]:
            model.MinFulfill = Constraint(
                model.N, model.T,
                rule=lambda m,n,t:
                    Constraint.Skip if demand.get((n,t),0)==0
                    else sum(m.X[i,n,m_,t] for (i,j,m_) in m.ARCS if j==n)
                         + (m.Prod[n,t] if n in m.IU else 0)
                         >= min_fulfill.get((n,t),0)/100*demand.get((n,t),0)
            )

        model.TripPhysics = Constraint(
            model.ARCS, model.T,
            rule=lambda m,i,j,m_,t: m.X[i,j,m_,t] == trip_cap.get((i,j,m_),0)*m.Trips[i,j,m_,t]
        )

        model.TripLimit = Constraint(
            model.ARCS, model.T,
            rule=lambda m,i,j,m_,t: m.Trips[i,j,m_,t] <= max_trips[(i,j,m_,t)]
        )

        # ==================================================
        # SOLVE
        # ==================================================
        solver = SolverFactory("cbc")
        result = solver.solve(model, tee=False)

        if result.solver.termination_condition == TerminationCondition.optimal:
            return {
                "success": True,
                "message": "Optimization completed successfully",
                "objective_value": value(model.OBJ),
                "model": model
            }

        return {
            "success": False,
            "message": f"Solver terminated with status: {result.solver.termination_condition}",
            "model": None
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Runtime error: {str(e)}",
            "model": None
        }


# ==================================================
# OPTIONAL LOCAL RUN
# ==================================================
# if __name__ == "__main__":
#     response = run_clinker_optimization("data/dataset.xlsx")
#     print(response["message"])