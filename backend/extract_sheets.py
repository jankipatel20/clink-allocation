import os
import pandas as pd


# ==================================================
# CONFIG
# ==================================================
REQUIRED_SHEETS = {
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
def extract_excel_to_csv(excel_path: str, output_dir: str) -> None:
    """
    Reads an Excel file and extracts required sheets as CSVs.

    Args:
        excel_path (str): Path to input Excel file
        output_dir (str): Directory to store generated CSVs

    Raises:
        FileNotFoundError: if Excel file does not exist
        ValueError: if required sheets are missing
    """

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    os.makedirs(output_dir, exist_ok=True)

    xls = pd.ExcelFile(excel_path)
    available_sheets = set(xls.sheet_names)

    missing = set(REQUIRED_SHEETS.keys()) - available_sheets
    if missing:
        raise ValueError(f"Missing required sheets: {sorted(missing)}")

    # Overwrite policy: always replace old CSVs with new ones
    for sheet_name, csv_name in REQUIRED_SHEETS.items():
        df = pd.read_excel(xls, sheet_name)

        csv_path = os.path.join(output_dir, csv_name)
        df.to_csv(csv_path, index=False)

    print("✅ Excel sheets extracted successfully.")


# ==================================================
# CLI / LOCAL TEST SUPPORT
# ==================================================
if __name__ == "__main__":
    DEFAULT_EXCEL = "dataset.xlsx"
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

    print("🚀 Extracting sheets from Excel...")
    extract_excel_to_csv(DEFAULT_EXCEL, OUTPUT_DIR)
    print(f"CSV files saved to: {OUTPUT_DIR}")