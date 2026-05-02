import os
import pandas as pd
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
xlsx_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
data_files = csv_files + xlsx_files

print(f"Found {len(data_files)} datasets in the data folder.")

for file in data_files:
    print(f"\n--- Analyzing: {os.path.basename(file)} ---")
    try:
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.endswith('.xlsx'):
            df = pd.read_excel(file)
        
        print(f"Shape (Rows, Columns): {df.shape}")
        print(f"Columns: {', '.join(df.columns)}")
        print("Missing Values per Column:")
        missing = df.isnull().sum()
        print(missing[missing > 0].to_dict() if not missing[missing > 0].empty else "No missing values!")
        
    except Exception as e:
        print(f"Error reading {file}: {e}")
