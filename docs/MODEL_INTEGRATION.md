# 🔄 Model Integration Guide

## Current Setup

### File Upload Behavior
- **0 files uploaded**: Backend automatically loads CSVs from `backend/data/`
- **8 files uploaded**: Backend uses uploaded files with case-insensitive matching

### Expected CSV Files (Case-Insensitive)
1. `ClinkerCapacity.csv` → `clinkercapacity`
2. `ClinkerDemand.csv` → `clinkerdemand`
3. `IUGUClosingStock.csv` → `iuguclosingstock`
4. `IUGUConstraint.csv` → `iuguconstraint`
5. `IUGUOpeningStock.csv` → `iuguopeningstock`
6. `IUGUType.csv` → `iugutype`
7. `LogisticsIUGU.csv` → `logisticsiugu`
8. `ProductionCost.csv` → `productioncost`

### Case-Insensitive Matching
Frontend can send files with ANY case:
- ✅ `Clinkercapacity.csv`
- ✅ `clinkercapacity.csv`
- ✅ `CLINKERCAPACITY.csv`
- ✅ `ClinkerCapacity.csv`

All map to the same key: `clinkercapacity`

---

## Using Dummy Model (Current)

### What It Does
- Returns mock optimization results
- Uses CBC solver (respects config.py)
- Has dummy constraints and variables
- Works with API without real model logic

### File: `backend/model_dummy.py`
```python
# Test it standalone
python backend/model_dummy.py
```

### To Use Dummy Model
Rename files:
```bash
# Backup current model.py (teammates' work in progress)
mv backend/model.py backend/model_real.py

# Use dummy model
mv backend/model_dummy.py backend/model.py
```

---

## When Real Model is Ready

### Integration Steps

1. **Teammate completes real model.py**
   - Uses CBC solver with config.py (see template in model_dummy.py)
   - Implements `build_model(data: dict)` function
   - Implements `solve_model(data: dict)` function

2. **Required Function Signatures**
   ```python
   def build_model(data: dict) -> ConcreteModel:
       """
       data keys: clinkercapacity, clinkerdemand, etc.
       Returns: Pyomo ConcreteModel
       """
       pass

   def solve_model(data: dict) -> tuple:
       """
       Returns: (model, result)
       - model: Solved Pyomo ConcreteModel
       - result: SolverResults object
       """
       pass
   ```

3. **Replace dummy with real**
   ```bash
   # Remove dummy
   rm backend/model.py

   # Use real model
   mv backend/model_real.py backend/model.py
   ```

4. **Test**
   ```bash
   uvicorn backend.main:app --reload
   ```

---

## Data Access in Model

### Example: Extract Data from Dict
```python
def build_model(data: dict) -> ConcreteModel:
    model = ConcreteModel()
    
    # Access uploaded/loaded CSVs
    capacity_df = data.get('clinkercapacity')
    demand_df = data.get('clinkerdemand')
    opening_stock_df = data.get('iuguopeningstock')
    
    # Extract values
    if capacity_df is not None:
        # Process DataFrame
        for idx, row in capacity_df.iterrows():
            plant = row['Plant']
            period = row['Period']
            capacity = row['Capacity']
            # Use in model...
    
    return model
```

---

## Solver Configuration

### Uses config.py for CBC
```python
# In solve_model()
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
```

### Your Setup (No Conda)
- config.py detects no conda
- Uses system PATH for CBC
- Works automatically

### Teammate Setup (Conda)
- config.py detects conda environment
- Uses conda CBC path
- Works automatically

---

## Testing Checklist

### Backend Only
```bash
# Test data loader
python -c "from backend.data_loader import load_data_from_disk; print(load_data_from_disk())"

# Test dummy model
python backend/model_dummy.py

# Start backend
uvicorn backend.main:app --reload

# Test API
curl -X POST http://localhost:8000/optimize
```

### With Frontend (When Ready)
```bash
# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
streamlit run client/main.py
```

---

## Current Status

✅ **Completed**
- Case-insensitive file upload handling
- Default to backend/data/ when no files provided
- Dummy model with CBC solver
- Data loader updated for new CSV names

🔧 **In Progress by Teammates**
- Real model.py implementation
- Frontend file upload feature

📝 **Next Steps**
1. Test dummy model: `python backend/model_dummy.py`
2. Test backend API: `uvicorn backend.main:app --reload`
3. When real model ready: Replace model.py
4. Coordinate with frontend teammate for file upload integration

---

## File Structure

```
backend/
├── config.py              ← Solver configuration (your local, not in Git)
├── config.example.py      ← Template for teammates
├── data/                  ← Default CSV files
│   ├── ClinkerCapacity.csv
│   ├── ClinkerDemand.csv
│   ├── IUGUClosingStock.csv
│   ├── IUGUConstraint.csv
│   ├── IUGUOpeningStock.csv
│   ├── IUGUType.csv
│   ├── LogisticsIUGU.csv
│   └── ProductionCost.csv
├── data_loader.py         ← Updated for case-insensitive loading
├── main.py                ← Updated for 0 or 8 file handling
├── model.py               ← **Replace this when ready**
└── model_dummy.py         ← Temporary testing model
```
