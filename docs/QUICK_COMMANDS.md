# Quick Commands - Backend Setup

## For You (Testing Backend)

### 1. Test Data Loading
```powershell
# Verify all 8 CSV files load correctly
python -c "from backend.data_loader import load_data_from_disk; data = load_data_from_disk(); print('Loaded files:', list(data.keys()))"
```

**Expected Output:**
```
Loaded 8 files:
['clinkercapacity', 'clinkerdemand', 'iuguclosingstock', 'iuguconstraint', 'iuguopeningstock', 'iugutype', 'logisticsiugu', 'productioncost']
```

---

### 2. Test Dummy Model
```powershell
python backend/model_dummy.py
```

**Expected Output:**
```
Building dummy model...
Solver Status: ok
Termination Condition: optimal
Objective Value: ₹X,XXX,XXX.XX
✅ Dummy model works! Replace with real model when ready.
```

---

### 3. Start Backend API
```powershell
uvicorn backend.main:app --reload
```

**Expected Output:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

---

### 4. Test API Endpoint
```powershell
# In another terminal
curl -X POST http://localhost:8000/optimize
```

**Expected:** JSON response with optimization results

---

## For Frontend Teammate

### File Upload Requirements

**Option 1: No Files**
- Backend uses default CSVs from `backend/data/`
- No upload needed for testing

**Option 2: Upload 8 Files**
Must include (case-insensitive):
1. ClinkerCapacity.csv
2. ClinkerDemand.csv
3. IUGUClosingStock.csv
4. IUGUConstraint.csv
5. IUGUOpeningStock.csv
6. IUGUType.csv
7. LogisticsIUGU.csv
8. ProductionCost.csv

**Naming is flexible:**
- ✅ `Clinkercapacity.csv`
- ✅ `clinkercapacity.csv`
- ✅ `CLINKERCAPACITY.CSV`

All work!

---

## When Model is Ready (For Model Teammate)

### Step 1: Keep Same Structure
```python
# In your model.py - keep these two functions:

def build_model(data: dict) -> ConcreteModel:
    """
    data contains 8 DataFrames:
    - data['clinkercapacity']
    - data['clinkerdemand']
    - data['iuguclosingstock']
    - etc.
    """
    model = ConcreteModel()
    
    # Your model logic here
    
    return model


def solve_model(data: dict):
    """
    Returns: (model, result)
    """
    model = build_model(data)
    
    # Use CBC solver from config.py
    try:
        from backend.config import get_solver_path, PREFERRED_SOLVER
        solver_name, solver_path = get_solver_path(PREFERRED_SOLVER)
    except ImportError:
        solver_name = 'cbc'
        solver_path = None
    
    if solver_path:
        solver = SolverFactory(solver_name, executable=solver_path)
    else:
        solver = SolverFactory(solver_name)
    
    result = solver.solve(model, tee=False)
    
    return model, result
```

### Step 2: Replace File
```powershell
# When ready, just replace model.py
# Backend will automatically use it
```

---

## Troubleshooting

### "Module not found"
```powershell
pip install -r backend/requirements.txt
```

### "CBC not found"
- Check: `where cbc.exe`
- Update: `backend/config.py` with CBC path

### "File not found in data/"
- Verify all 8 CSV files in `backend/data/`
- Check spelling matches expected names

### API returns error
```powershell
# Check backend logs
uvicorn backend.main:app --reload

# Check what went wrong in terminal output
```

---

## Current Setup Summary

✅ **What Works Now:**
- Backend loads CSV files from `data/` folder
- Case-insensitive file matching
- Dummy model returns mock results
- API endpoint ready for testing

🔧 **What's Being Developed:**
- Real optimization model (your teammates)
- Frontend file upload UI (other teammate)

📌 **Your Role:**
- Test backend with dummy model
- Ensure API works correctly
- Wait for teammates to complete their parts
