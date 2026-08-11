import os
import shutil
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.model import run_clinker_optimization
from backend import config


# ==================================================
# HISTORY HELPERS
# ==================================================
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "runs", "history.json")

def save_run_to_history(filename: str, response: dict):
    """Append a completed optimization run to the history JSON file"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

    # Load existing history
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    # Build the run record
    summary = response.get("summary", {})
    cost_breakdown = response.get("cost_breakdown", {})
    run = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "status": response.get("status", "unknown"),
        "objective_value": response.get("objective_value"),
        "cost_breakdown": {
            "production": cost_breakdown.get("production", 0),
            "transport": cost_breakdown.get("transport", 0),
            "inventory": cost_breakdown.get("inventory", 0),
        },
        "summary": {
            "total_production": summary.get("total_production", 0),
            "total_shipments": summary.get("total_shipments", 0),
            "total_trips": summary.get("total_trips", 0),
        }
    }

    # Prepend so newest is first, keep last 20 runs
    history.insert(0, run)
    history = history[:20]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Streamlit runs on different port)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# HEALTH CHECK ENDPOINT
# ==================================================
@app.get("/")
def home():
    return {"message": "Welcome to the Clinker Optimization API. Use /optimize to run optimization."}
@app.get("/health")
def health_check():
    """Check if backend is running"""
    return {"status": "ok", "message": "Backend is running"}


# ==================================================
# OPTIMIZATION ENDPOINT
# ==================================================
@app.post("/optimize")
def optimize(file: UploadFile = File(...)):
    """
    Load Excel file (uploaded) → Run optimization → Return results
    
    Flow:
    1. Receive uploaded Excel file (required)
    2. Run clinker optimization model from Excel
    3. Return results as JSON
    """

    try:
        # -------------------------------
        # Step 1: Validate and save file
        # -------------------------------
        # Validate file type
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(
                status_code=400, 
                detail="Only .xlsx or .xls files are supported"
            )

        # Save uploaded file
        excel_path = os.path.join(config.UPLOAD_DIR, file.filename)
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

        with open(excel_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -------------------------------
        # Step 2: Run optimization
        # -------------------------------
        try:
            result = run_clinker_optimization(excel_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Optimization failed: {str(e)}"
            )

        # -------------------------------
        # Step 3: Check result and format
        # -------------------------------
        if not result.get("success"):
            return {
                "status": "failed",
                "message": result.get("message", "Unknown error"),
                "success": False
            }

        # Extract key data from result
        response = {
            "status": "success",
            "success": True,
            "message": result.get("message", "Optimization completed"),
            "objective_value": result.get("objective_value"),
            "solver": "CBC",
            "production": [],
            "shipments": [],
            "inventory": []
        }

        # Extract production data
        model = result.get("model")
        if model:
            try:
                from pyomo.environ import value
                
                # Production
                production = []
                for i in model.IU:
                    for t in model.T:
                        qty = float(value(model.Prod[i, t]))
                        if qty > 0.01:
                            production.append({
                                "node": str(i),
                                "period": str(t),
                                "quantity": round(qty, 2)
                            })
                
                response["production"] = production
                
                # Shipments
                shipments = []
                for (i, j, m) in model.ARCS:
                    for t in model.T:
                        qty = float(value(model.X[i, j, m, t]))
                        trips = int(value(model.Trips[i, j, m, t]))
                        if qty > 0.01:
                            shipments.append({
                                "from": str(i),
                                "to": str(j),
                                "mode": str(m),
                                "period": str(t),
                                "quantity": round(qty, 2),
                                "trips": trips
                            })
                
                response["shipments"] = shipments
                
                # Inventory
                inventory = []
                for n in model.N:
                    for t in model.T:
                        qty = float(value(model.Inv[n, t]))
                        if qty > 0.01:
                            inventory.append({
                                "node": str(n),
                                "period": str(t),
                                "quantity": round(qty, 2)
                            })
                
                response["inventory"] = inventory
                
                # Summary
                response["summary"] = {
                    "total_production": sum(p["quantity"] for p in production),
                    "total_shipments": sum(s["quantity"] for s in shipments),
                    "total_trips": sum(s["trips"] for s in shipments),
                    "num_nodes": len(model.N),
                    "num_periods": len(model.T)
                }

                # Cost breakdown (computed in model.py from actual solver values)
                cost_breakdown = result.get("cost_breakdown")
                if cost_breakdown:
                    response["cost_breakdown"] = cost_breakdown
                
            except Exception as e:
                # If extraction fails, return basic result
                response["warning"] = f"Could not extract full results: {str(e)}"

        # Save run to history (best-effort — never block the response)
        try:
            save_run_to_history(file.filename, response)
        except Exception:
            pass

        return response

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )


# ==================================================
# HISTORY ENDPOINT
# ==================================================
@app.get("/history")
def get_history():
    """Return list of past optimization runs (newest first)"""
    if not os.path.exists(HISTORY_FILE):
        return {"runs": [], "message": "No runs recorded yet"}
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return {"runs": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read history: {str(e)}")


# ==================================================
# DEBUG ENDPOINTS
# ==================================================
@app.get("/debug/sheets")
def debug_sheets():
    """List all sheets in the default Excel file"""
    try:
        import pandas as pd
        
        if not os.path.exists(config.DEFAULT_EXCEL_PATH):
            raise HTTPException(status_code=404, detail="Default Excel file not found")
        
        excel_data = pd.read_excel(
            config.DEFAULT_EXCEL_PATH, 
            sheet_name=None, 
            engine='openpyxl'
        )
        
        return {
            "excel_path": config.DEFAULT_EXCEL_PATH,
            "sheets": list(excel_data.keys()),
            "sheet_info": {
                name: {"rows": df.shape[0], "columns": df.shape[1]}
                for name, df in excel_data.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/sheet-preview/{sheet_name}")
def debug_sheet_preview(sheet_name: str):
    """Preview first 5 rows of a specific sheet"""
    try:
        import pandas as pd
        
        if not os.path.exists(config.DEFAULT_EXCEL_PATH):
            raise HTTPException(status_code=404, detail="Default Excel file not found")
        
        df = pd.read_excel(
            config.DEFAULT_EXCEL_PATH, 
            sheet_name=sheet_name,
            engine='openpyxl'
        )
        
        return {
            "sheet_name": sheet_name,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))