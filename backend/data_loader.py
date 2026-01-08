#For loading .csv data files from backend/data directory

# data_loader.py
# Responsibility:
# - Read CSV files from backend/data/
# - Load them into Pandas DataFrames
# - Return them as a clean dictionary
#
# NO model logic
# NO FastAPI logic
# NO validation (yet)

import os
import pandas as pd


def load_data_from_disk(base_path: str | None = None) -> dict:
    """
    Loads all required CSV files from disk and returns them as DataFrames.

    Parameters:
        base_path (str | None): Path to data directory.
                                 Defaults to backend/data/

    Returns:
        dict: {
            "nodes": DataFrame,
            "periods": DataFrame,
            "production": DataFrame,
            "demand": DataFrame,
            "arcs": DataFrame,
            "scenarios": DataFrame
        }
    """

    # Resolve default data path → backend/data/
    if base_path is None:
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(CURRENT_DIR, "data")

    # File paths
    paths = {
        "nodes": os.path.join(base_path, "nodes.csv"),
        "periods": os.path.join(base_path, "periods.csv"),
        "production": os.path.join(base_path, "production.csv"),
        "demand": os.path.join(base_path, "demand.csv"),
        "arcs": os.path.join(base_path, "arcs.csv"),
        "scenarios": os.path.join(base_path, "scenarios.csv"),
    }

    # Load CSVs into DataFrames
    data = {}
    for key, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required file: {path}")

        data[key] = pd.read_csv(path)

    return data
