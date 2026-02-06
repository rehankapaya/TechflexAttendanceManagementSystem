import pandas as pd

try:
    df = pd.read_excel('Student_Status_Report.xlsx', sheet_name='Student Records')
    unique_courses = df['Course Name'].unique().tolist()
    print(f"Unique Courses: {unique_courses}")
    
    # Also check if there are other sheets that might contain schedule info
    xl = pd.ExcelFile('Student_Status_Report.xlsx')
    if len(xl.sheet_names) > 1:
        print(f"Other sheets: {xl.sheet_names[1:]}")

except Exception as e:
    print(f"Error: {e}")
