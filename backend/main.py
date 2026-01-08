import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException

from backend.extract_sheets import extract_excel_to_csv
from backend.data_loader import load_data
from backend.model import solve_model
from backend import config


app = FastAPI()


# ==================================================
# OPTIMIZATION ENDPOINT
# ==================================================
@app.post("/optimize")
def optimize(file: UploadFile | None = File(default=None)):
    """
    If Excel file is provided:
        - save it
        - extract sheets → CSV
    Else:
        - use default Excel file

    Then:
        - load CSVs
        - run optimization model
        - return result
    """

    try:
        # -------------------------------
        # Step 1: Decide Excel source
        # -------------------------------
        if file:
            if not file.filename.endswith(".xlsx"):
                raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

            excel_path = os.path.join(config.UPLOAD_DIR, file.filename)
            os.makedirs(config.UPLOAD_DIR, exist_ok=True)

            with open(excel_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        else:
            excel_path = config.DEFAULT_EXCEL_PATH

            if not os.path.exists(excel_path):
                raise HTTPException(status_code=500, detail="Default Excel file not found")

        # -------------------------------
        # Step 2: Extract Excel → CSV
        # -------------------------------
        extract_excel_to_csv(
            excel_path=excel_path,
            output_dir=config.DATA_DIR
        )

        # -------------------------------
        # Step 3: Load CSVs → DataFrames
        # -------------------------------
        data = load_data(config.DATA_DIR)

        # -------------------------------
        # Step 4: Run optimization
        # -------------------------------
        result = solve_model(data)

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
