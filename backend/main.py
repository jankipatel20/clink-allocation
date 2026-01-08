from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
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

        # 5️⃣ Extract TOTAL COST
        total_cost = float(value(model.OBJ))

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

        # 9️⃣ FINAL JSON RESPONSE
        return {
            "status": "success",
            "total_cost": total_cost,
            "production": production_plan,
            "inventory": inventory_plan,
            "shipments": shipment_plan
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
