import pandas as pd

try:
    # Load the Excel file
    xl = pd.ExcelFile('Student_Status_Report.xlsx')
    
    print(f"Sheet names: {xl.sheet_names}")
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel('Student_Status_Report.xlsx', sheet_name=sheet_name)
        print(f"\n--- Sheet: {sheet_name} ---")
        print(f"Columns: {df.columns.tolist()}")
        print("First few rows:")
        print(df.head())
        print(f"Data types:\n{df.dtypes}")

except Exception as e:
    print(f"Error: {e}")
