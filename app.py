import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import glob


# --- Page Configuration ---
st.set_page_config(page_title="Attendance Pro", layout="wide", initial_sidebar_state="expanded")




# --- Constants ---
STUDENT_DATA_FILE = "Student_Status_Report.xlsx"
ATTENDANCE_FILE = "Attendance_Records.xlsx"
CONFIG_FILE = "course_config.json"

# --- Helper Functions ---

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_student_data():
    # Priority 1: Check for the exact master file
    target_file = STUDENT_DATA_FILE
    
    # Priority 2: If master file is missing, find the most recent file matching the pattern
    if not os.path.exists(target_file):
        files = glob.glob("Student_Status_Report*.xlsx")
        if files:
            # Sort by modification time (most recent first)
            files.sort(key=os.path.getmtime, reverse=True)
            target_file = files[0]
            st.info(f"💡 Found student data in: `{target_file}`")
        else:
            st.error(f"Error: No file matching `Student_Status_Report*.xlsx` found!")
            return None
            
    try:
        df = pd.read_excel(target_file, sheet_name='Student Records')
        # Clean data: trim strings
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"Error loading student data from {target_file}: {e}")
        return None


def save_attendance(records_df):
    try:
        if os.path.exists(ATTENDANCE_FILE):
            existing_df = pd.read_excel(ATTENDANCE_FILE)
            
            # Merge logic: Overwrite existing records for the same (Date, Student ID, Course)
            # We combine and then drop duplicates, keeping the 'last' (newest) record
            updated_df = pd.concat([existing_df, records_df], ignore_index=True)
            updated_df = updated_df.drop_duplicates(subset=['Date', 'Student ID', 'Course'], keep='last')
            
            updated_df.to_excel(ATTENDANCE_FILE, index=False)
        else:
            records_df.to_excel(ATTENDANCE_FILE, index=False)
        return True
    except PermissionError:
        st.error(f"❌ Cannot save attendance. Please close **{ATTENDANCE_FILE}** if it's open in Excel and try again.")
        return False
    except Exception as e:
        st.error(f"❌ An error occurred while saving: {e}")
        return False

def get_course_schedule(course_name):
    # Migration helper: default to Mon-Fri if config is missing or old format
    val = st.session_state.config.get(course_name, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    if isinstance(val, str):
        if val == "5 Days":
            return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        elif val == "3 Days":
            return ["Monday", "Wednesday", "Friday"]
    return val

# --- App State Management ---
if 'config' not in st.session_state:
    st.session_state.config = load_config()

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Header Styling */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        padding: 1.5rem 0;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }


    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background: linear-gradient(90deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        font-weight: 700;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
        color: white;
        border: none;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    
    /* Custom Status Badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid #cbd5e1;
        background: #f1f5f9;
    }
    
    /* Clean Separator Line */
    .row-divider {
        margin: 8px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">📊 Attendance Management PRO</h1>', unsafe_allow_html=True)

tabs = st.tabs(["📝 Mark Attendance", "📥 Update Students", "⚙️ Settings", "📈 Reports"])

# --- Tab 1: Update Students ---
with tabs[1]:
    st.subheader("📥 Update Student Records")
    st.info("""
        Upload a new student report (e.g., `Student_Status_Report_2_6_2026.xlsx`). 
        **Note:** The system will automatically rename it to `Student_Status_Report.xlsx` to use it as the main record.
    """)
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"], key="student_upload")

    
    if uploaded_file is not None:
        try:
            # Check if the uploaded file has the required sheet
            xl = pd.ExcelFile(uploaded_file)
            if 'Student Records' in xl.sheet_names:
                if st.button("🔥 Replace Current Records"):
                    # Save the file
                    with open(STUDENT_DATA_FILE, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("✅ Student records updated successfully!")
                    st.balloons()
                    # Optional: Rerun logic could go here but st.success is often enough
            else:
                st.error("❌ The uploaded file does not contain a sheet named **'Student Records'**. Please check the file and try again.")
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")


# --- Tab 1: Mark Attendance ---
with tabs[0]:
    st.subheader("Mark Daily Attendance")
    
    df = load_student_data()
    
    if df is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            courses = sorted(df['Course Name'].unique().tolist())
            selected_course = st.selectbox("Select Course", courses)
        
        with col2:
            selected_date = st.date_input("Select Date", datetime.now())
            day_name = selected_date.strftime("%A")
            st.info(f"📅 Today is **{day_name}**")

        # Check Schedule Logic
        course_schedule = get_course_schedule(selected_course)
        is_valid_day = True
        
        if day_name not in course_schedule:
            st.warning(f"⚠️ **{selected_course}** is not scheduled for {day_name}. Scheduled days: {', '.join(course_schedule)}")
            is_valid_day = False
        
        # Filter Students
        course_students = df[df['Course Name'] == selected_course].copy()
        
        # Add a filter for Active Students
        st.write("---")
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            show_only_active = st.checkbox("Show Only **ACTIVE** Students", value=True)
        
        if show_only_active:
            course_students = course_students[course_students['Course Status'].str.lower() == 'active']
            
        if course_students.empty:
            st.warning("No students found matching your criteria.")
        else:
            st.write(f"### Student List ({len(course_students)} Students)")
            
            # Check for existing attendance for this date/course
            existing_records = pd.DataFrame()
            if os.path.exists(ATTENDANCE_FILE):
                all_att = pd.read_excel(ATTENDANCE_FILE)
                target_date_str = selected_date.strftime("%Y-%m-%d")
                existing_records = all_att[(all_att['Date'] == target_date_str) & (all_att['Course'] == selected_course)]

            # Using a list of dictionaries to track attendance
            attendance_status = []
            
            # Create a table-like header
            h1, h2, h3, h4, h5 = st.columns([0.8, 1.5, 3.5, 2, 2])
            h1.markdown("**Mark**")
            h2.markdown("**ID**")
            h3.markdown("**Student Name**")
            h4.markdown("**Status**")
            h5.markdown("**Record**")
            st.markdown('<div class="row-divider" style="border-bottom: 2px solid #1e293b;"></div>', unsafe_allow_html=True)

            for i, row in course_students.iterrows():
                # Check if this student already has a record for today
                prev_status = None
                if not existing_records.empty and 'Student ID' in existing_records.columns:
                    existing_att = existing_records[existing_records['Student ID'] == row['Student ID']]
                    prev_status = existing_att['Status'].iloc[0] if not existing_att.empty else None
                
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([0.8, 1.5, 3.5, 2, 2])
                    status_color = "#10b981" if row['Course Status'].lower() == "active" else "#ef4444"
                    
                    with c1:
                        # If previously marked "Absent", default to unchecked, else checked
                        is_present = st.checkbox("", value=(prev_status != "Absent"), key=f"att_{row['Student ID']}_{i}")
                    with c2:
                        st.write(f"{row['Student ID']}")
                    with c3:
                        st.markdown(f"**{row['Name']}**")
                    with c4:
                        st.markdown(f'<span class="status-badge" style="background:{status_color}20; color:{status_color}; border: 1px solid {status_color}">{row['Course Status']}</span>', unsafe_allow_html=True)
                    with c5:
                        if prev_status:
                            badge_color = "#10b981" if prev_status == "Present" else "#ef4444"
                            st.markdown(f'<span style="color:{badge_color}; font-size: 0.85em; font-weight:600;">{prev_status}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown("<span style='color:gray; font-size: 0.8em;'>No record</span>", unsafe_allow_html=True)
                    
                    # Added the requested separator line
                    st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)
                    
                    attendance_status.append({
                        "Date": selected_date.strftime("%Y-%m-%d"),
                        "Student ID": row['Student ID'],
                        "Name": row['Name'],
                        "Course": selected_course,
                        "Status": "Present" if is_present else "Absent"
                    })
            
            if st.button("Submit Attendance", disabled=not is_valid_day):
                new_records = pd.DataFrame(attendance_status)
                if save_attendance(new_records):
                    st.success(f"✅ Attendance for {len(new_records)} students recorded successfully!")

# --- Tab 2: Settings ---
with tabs[2]:
    st.subheader("⚙️ Course Schedule Configuration")
    st.info("Select the specific days of the week each course is held.")
    
    if df is not None:
        all_courses = sorted(df['Course Name'].unique().tolist())
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        updated_config = {}
        for course in all_courses:
            # Get current days using helper (handles migration)
            current_days = get_course_schedule(course)
            
            st.write(f"#### {course}")
            selected_days = st.multiselect(
                f"Days for {course}", 
                options=days_of_week, 
                default=current_days, 
                key=f"cfg_{course}"
            )
            updated_config[course] = selected_days
            st.markdown("---")
        
        if st.button("Save All Configurations"):
            st.session_state.config = updated_config
            save_config(updated_config)
            st.success("✅ All course schedules updated successfully!")
            st.balloons()

# --- Tab 3: Reports ---
with tabs[3]:
    st.subheader("📊 Attendance History & Analytics")
    if os.path.exists(ATTENDANCE_FILE):
        report_df = pd.read_excel(ATTENDANCE_FILE)
        
        # Filter by course for a cleaner pivot
        all_courses = sorted(report_df['Course'].unique().tolist())
        report_course = st.selectbox("View Report for Course", all_courses, key="report_course_sel")
        
        course_data = report_df[report_df['Course'] == report_course]
        
        if not course_data.empty:
            # Create a more descriptive Date column for headers (Date + Day)
            course_data = course_data.copy()
            course_data['Date_with_Day'] = course_data['Date'].apply(
                lambda x: f"{x} ({datetime.strptime(x, '%Y-%m-%d').strftime('%a')})"
            )
            
            # Pivot the data: Rows = Student ID & Name, Columns = Date + Day
            pivot_df = course_data.pivot(index=['Student ID', 'Name'], columns='Date_with_Day', values='Status').fillna("-")
            
            # --- Added Color Coding ---
            def color_attendance(val):
                if val == 'Present':
                    return 'background-color: #d4edda; color: #155724;' # Green
                elif val == 'Absent':
                    return 'background-color: #f8d7da; color: #721c24;' # Red
                return ''

            styled_df = pivot_df.style.applymap(color_attendance)
            # --------------------------

            st.write(f"### Attendance Grid: {report_course}")
            st.dataframe(styled_df, use_container_width=True)
            
            # Simple stats for this course
            st.write("---")
            st.write("### Summary Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Classes", len(pivot_df))
            with col2:
                total_p = (course_data['Status'] == 'Present').sum()
                st.metric("Total Presents", total_p)
            with col3:
                total_a = (course_data['Status'] == 'Absent').sum()
                st.metric("Total Absents", total_a)
        
        st.write("---")
        st.write("### 🔍 Missing Attendance for Today")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Load all students
        all_students_df = load_student_data()
        active_students = all_students_df[all_students_df['Course Status'].str.lower() == 'active']
        
        # Check against the full report_df (not just filtered course)
        marked_ids = report_df[report_df['Date'] == today_str]['Student ID'].unique()
        missing_students = active_students[~active_students['Student ID'].isin(marked_ids)]
        
        if not missing_students.empty:
            st.warning(f"Note: {len(missing_students)} active students have not been marked for today yet.")
            st.dataframe(missing_students[['Student ID', 'Name', 'Course Name']], use_container_width=True)
        else:
            st.success("All active students have been marked for today! 🎉")

        # Download button
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Raw Report (Standard Format) as CSV", data=csv, file_name="attendance_report.csv", mime="text/csv")
    else:
        st.info("No attendance records found yet.")
