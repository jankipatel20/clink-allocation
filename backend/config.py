# For configuring solver paths based on environment

import os
from pyomo.environ import SolverFactory

def get_solver():
    # 1. Look for a manual path set in the terminal (For YOU)
    manual_path = os.getenv("SOLVER_PATH")
    
    if manual_path:
        # Use your manual cbc.exe
        return SolverFactory("cbc", executable=manual_path)
    
    # 2. Fallback for Team (Conda) or Docker
    # This assumes 'cbc' is in their system PATH
    return SolverFactory("cbc")

import os

BASE_DIR = os.path.dirname(__file__)

DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

DEFAULT_EXCEL_PATH = os.path.join(BASE_DIR, "dataset.xlsx")
