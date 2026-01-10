import os
import pandas as pd


# ==================================================
# CONFIG
# ==================================================
REQUIRED_CSVS = {
    "ClinkerDemand": "ClinkerDemand.csv",
    "ClinkerCapacity": "ClinkerCapacity.csv",
    "ProductionCost": "ProductionCost.csv",
    "LogisticsIUGU": "LogisticsIUGU.csv",
    "IUGUConstraint": "IUGUConstraint.csv",
    "IUGUOpeningStock": "IUGUOpeningStock.csv",
    "IUGUClosingStock": "IUGUClosingStock.csv",
    "IUGUType": "IUGUType.csv",
}


# ==================================================
# CORE FUNCTION
# ==================================================
def load_data(data_dir: str) -> dict:
    """
    Loads required CSV files into pandas DataFrames.

    Args:
        data_dir (str): Directory containing CSV files

    Returns:
        dict: DataFrames keyed exactly as model.py expects

    Raises:
        FileNotFoundError: if CSV directory or files are missing
        ValueError: if CSV files are empty
    """

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    data = {}

    for key, filename in REQUIRED_CSVS.items():
        path = os.path.join(data_dir, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required CSV: {filename}")

        df = pd.read_csv(path)

        if df.empty:
            raise ValueError(f"CSV file is empty: {filename}")

        data[key] = df

    return data


# ==================================================
# LOCAL TEST SUPPORT
# ==================================================
if __name__ == "__main__":
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    print("📦 Loading CSV data...")
    loaded_data = load_data(DATA_DIR)

    for k, v in loaded_data.items():
        print(f"{k}: {v.shape}")