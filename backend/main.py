from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pandas as pd
import io

from pyomo.environ import value, TerminationCondition
from backend.data_loader import load_data_from_disk

app = FastAPI(title="Clinker Optimization API")

# Allow frontend (Streamlit) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def compute_cost_breakdown(model, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Compute detailed cost breakdown from solved Pyomo model.
    
    Returns:
        {
            "production_cost": float,
            "inventory_cost": float,
            "transport_cost": float,
            "trip_cost": float,
            "total_cost": float,
            "cost_details": {...}  # For transparency/debugging
        }
    """
    # Extract data dictionaries
    production_df = data["production"]
    nodes_df = data["nodes"]
    arcs_df = data["arcs"]
    
    prod_cost = production_df.set_index(["node_id", "period_id"])["prod_cost"].to_dict()
    inv_cost = nodes_df.set_index("node_id")["inv_cost"].to_dict()
    trans_cost = arcs_df.set_index(["origin", "dest", "mode"])["trans_cost"].to_dict()
    trip_fixed_cost = 0.01
    
    # ===== PRODUCTION COST =====
    production_cost = 0.0
    for i in model.N:
        for t in model.T:
            prod_val = value(model.Prod[i, t])
            if prod_val is not None and prod_val > 0:
                cost_coeff = prod_cost.get((i, t), 0)
                production_cost += cost_coeff * prod_val
    
    # ===== INVENTORY COST =====
    inventory_cost = 0.0
    for n in model.N:
        for t in model.T:
            inv_val = value(model.Inv[n, t])
            if inv_val is not None and inv_val > 0:
                cost_coeff = inv_cost.get(n, 0)
                inventory_cost += cost_coeff * inv_val
    
    # ===== TRANSPORT COST =====
    # Variable transport cost (quantity-based)
    transport_variable_cost = 0.0
    for (i, j, m) in model.ARCS:
        for t in model.T:
            qty_val = value(model.X[i, j, m, t])
            if qty_val is not None and qty_val > 0:
                cost_coeff = trans_cost.get((i, j, m), 0)
                transport_variable_cost += cost_coeff * qty_val
    
    # Fixed trip cost
    trip_cost = 0.0
    for (i, j, m) in model.ARCS:
        for t in model.T:
            trips_val = value(model.Trips[i, j, m, t])
            if trips_val is not None and trips_val > 0:
                trip_cost += trip_fixed_cost * trips_val
    
    transport_cost = transport_variable_cost + trip_cost
    
    # ===== TOTALS =====
    total_cost_computed = production_cost + inventory_cost + transport_cost
    total_cost_objective = float(value(model.OBJ))
    
    # Cost variance (should be negligible, within solver tolerance)
    cost_variance = abs(total_cost_computed - total_cost_objective)
    
    return {
        "production_cost": round(float(production_cost), 2),
        "inventory_cost": round(float(inventory_cost), 2),
        "transport_variable_cost": round(float(transport_variable_cost), 2),
        "trip_cost": round(float(trip_cost), 2),
        "transport_cost": round(float(transport_cost), 2),
        "total_cost": round(float(total_cost_objective), 2),
        "cost_details": {
            "computed_total": round(float(total_cost_computed), 2),
            "objective_total": round(float(total_cost_objective), 2),
            "variance": round(cost_variance, 6),
            "breakdown_valid": cost_variance < 1.0  # Within solver tolerance
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/optimize")
async def run_optimization(files: List[UploadFile] = File(None)):
    from backend.model import solve_model  # lazy import

    try:
        # 1️⃣ Load data
        if files:
            data = {}
            for file in files:
                content = await file.read()
                df = pd.read_csv(io.BytesIO(content))
                key = file.filename.replace(".csv", "").lower()
                data[key] = df
        else:
            data = load_data_from_disk()

        # 2️⃣ Validate required datasets
        required_keys = {
            "nodes", "periods", "production",
            "demand", "arcs", "scenarios"
        }
        missing = required_keys - data.keys()
        if missing:
            return {
                "status": "error",
                "message": f"Missing required CSV files: {list(missing)}"
            }

        # 3️⃣ Run optimization model
        model, result = solve_model(
            data["nodes"],
            data["periods"],
            data["production"],
            data["demand"],
            data["arcs"],
            data["scenarios"],
        )

        # 4️⃣ Check solver outcome
        if result.solver.termination_condition != TerminationCondition.optimal:
            return {
                "status": "failed",
                "solver_status": str(result.solver.termination_condition),
                "message": "Optimization infeasible or solver failed"
            }

        # 5️⃣ Compute cost breakdown
        cost_breakdown = compute_cost_breakdown(model, data)

        # 6️⃣ Extract PRODUCTION
        production_plan = []
        for i in model.N:
            for t in model.T:
                qty = model.Prod[i, t].value
                if qty is not None and qty > 0:
                    production_plan.append({
                        "node_id": i,
                        "period_id": int(t),
                        "quantity": float(qty)
                    })

        # 7️⃣ Extract INVENTORY
        inventory_plan = []
        for n in model.N:
            for t in model.T:
                qty = model.Inv[n, t].value
                if qty is not None:
                    inventory_plan.append({
                        "node_id": n,
                        "period_id": int(t),
                        "quantity": float(qty)
                    })

        # 8️⃣ Extract SHIPMENTS + TRIPS
        shipment_plan = []
        for (o, d, m) in model.ARCS:
            for t in model.T:
                qty = model.X[o, d, m, t].value
                trips = model.Trips[o, d, m, t].value

                if qty is not None and qty > 0:
                    shipment_plan.append({
                        "origin": o,
                        "destination": d,
                        "mode": m,
                        "period_id": int(t),
                        "quantity": float(qty),
                        "trips": int(trips) if trips is not None else 0
                    })

        # 9️⃣ FINAL JSON RESPONSE with cost breakdown
        return {
            "status": "success",
            "total_cost": cost_breakdown["total_cost"],
            "cost_breakdown": {
                "production_cost": cost_breakdown["production_cost"],
                "inventory_cost": cost_breakdown["inventory_cost"],
                "transport_variable_cost": cost_breakdown["transport_variable_cost"],
                "trip_cost": cost_breakdown["trip_cost"],
                "transport_cost": cost_breakdown["transport_cost"]
            },
            "cost_details": cost_breakdown["cost_details"],
            "production": production_plan,
            "inventory": inventory_plan,
            "shipments": shipment_plan
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
