import pandas as pd

try:
    df = pd.read_excel('Student_Status_Report.xlsx', sheet_name='Student Records')
    print("Unique Account Statuses:", df['Account Status'].unique().tolist())
    print("Unique Course Statuses:", df['Course Status'].unique().tolist())
    
    # Check for any other interesting columns
    print("\nValue counts for Account Status:")
    print(df['Account Status'].value_counts())

except Exception as e:
    print(f"Error: {e}")
