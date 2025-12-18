"""Convert Gen_AI Dataset.xlsx to CSV and extract training/test data"""
import pandas as pd
import os

# Read the Excel file
excel_file = "data/Gen_AI Dataset.xlsx"
print(f"Reading {excel_file}...")

# Read all sheets
xls = pd.ExcelFile(excel_file)
print(f"Found sheets: {xls.sheet_names}")

# Process each sheet
for sheet_name in xls.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"\n{sheet_name}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  First few rows:")
    print(df.head(3))
    
    # Save as CSV
    csv_filename = f"data/{sheet_name.lower().replace(' ', '_')}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"  Saved to: {csv_filename}")

print("\n✅ Conversion complete!")
