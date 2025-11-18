"""
Student Directory
=================
Searchable list of all students with detailed profiles
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import load_students, load_risk_scores, load_enrollments, load_logins, load_payments, load_counseling, load_grades

st.set_page_config(
    page_title="Student Directory",
    page_icon="👥",
    layout="wide"
)

# Check authentication
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please log in to access this page")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Check role
if st.session_state.get("role") not in ['advisor', 'admin']:
    st.error("🚫 Access Denied: This page is for Advisors and Admins only")
    st.stop()

# Hide public pages from sidebar (hide Admin Portal only for advisors)
admin_portal_css = """
    [data-testid="stSidebarNav"] li:has(a[href*="Admin_Portal"]) {
        display: none;
    }
""" if st.session_state.get("role") != "admin" else ""

st.markdown(f"""
    <style>
    [data-testid="stSidebarNav"] li:has(a[href*="app"]),
    [data-testid="stSidebarNav"] li:has(a[href*="SignUp"]),
    [data-testid="stSidebarNav"] li:has(a[href*="Login"]),
    [data-testid="stSidebarNav"] li:has(a[href*="Student_Portal"]) {{
        display: none;
    }}
    {admin_portal_css}
    </style>
""", unsafe_allow_html=True)

st.title("👥 Student Directory")
st.markdown("**Search, filter, and view detailed student profiles**")

# Load data
with st.spinner("Loading student data..."):
    students = load_students()
    risk_scores = load_risk_scores()
    enrollments = load_enrollments()
    grades = load_grades()

# Merge data
df = students.merge(risk_scores, on='StudentID', how='left')

# Calculate GPA for each student
gpa_dict = {}
for student_id in df['StudentID']:
    student_enr = enrollments[enrollments['StudentID'] == student_id]
    student_grd = grades[grades['EnrollmentID'].isin(student_enr['EnrollmentID'])]
    if len(student_grd) > 0:
        gpa = student_grd['GradePercentage'].mean() / 25  # Convert to 4.0 scale
        gpa_dict[student_id] = gpa
    else:
        gpa_dict[student_id] = 3.0

df['CalculatedGPA'] = df['StudentID'].map(gpa_dict)
df['RiskScore'] = df['OverallRiskScore'] * 100  # Convert to 0-100 scale

st.divider()

# Search and Filter Section
st.subheader("🔍 Search & Filter")

col1, col2, col3 = st.columns(3)

with col1:
    search_term = st.text_input(
        "Search by Name or ID",
        placeholder="Enter name or student ID..."
    )

with col2:
    risk_filter = st.selectbox(
        "Risk Level",
        ['All', 'Critical', 'High', 'Medium', 'Low']
    )

with col3:
    classification_filter = st.selectbox(
        "Classification",
        ['All'] + sorted(df['Classification'].unique().tolist())
    )

# Apply filters
filtered_df = df.copy()

# Search filter
if search_term:
    filtered_df = filtered_df[
        filtered_df['FirstName'].str.contains(search_term, case=False, na=False) |
        filtered_df['LastName'].str.contains(search_term, case=False, na=False) |
        filtered_df['StudentID'].astype(str).str.contains(search_term, na=False)
    ]

# Risk filter
if risk_filter != 'All':
    filtered_df = filtered_df[filtered_df['RiskCategory'] == risk_filter]

# Classification filter
if classification_filter != 'All':
    filtered_df = filtered_df[filtered_df['Classification'] == classification_filter]

st.divider()

# Display results count
st.markdown(f"**Showing {len(filtered_df)} of {len(df)} students**")

# Display as interactive table
st.subheader("📋 Student List")

# Prepare display columns
display_cols = ['StudentID', 'FirstName', 'LastName', 'Classification', 'Email',
                'CalculatedGPA', 'RiskScore', 'RiskCategory']

# Format the dataframe for display
display_df = filtered_df[display_cols].copy()
display_df = display_df.sort_values('RiskScore', ascending=False)

# Rename columns for display
display_df = display_df.rename(columns={'CalculatedGPA': 'GPA'})

# Round GPA to 2 decimal places
display_df['GPA'] = display_df['GPA'].round(2)
display_df['RiskScore'] = display_df['RiskScore'].round(0)

# Style the dataframe
def highlight_risk(row):
    if row['RiskCategory'] == 'Critical':
        return ['background-color: #FEE2E2'] * len(row)
    elif row['RiskCategory'] == 'High':
        return ['background-color: #FEF3C7'] * len(row)
    elif row['RiskCategory'] == 'Medium':
        return ['background-color: #FEF9E7'] * len(row)
    else:
        return ['background-color: #D1FAE5'] * len(row)

# Display styled dataframe
st.dataframe(
    display_df.style.apply(highlight_risk, axis=1),
    use_container_width=True,
    height=400
)

# Download button
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Student List (CSV)",
    data=csv,
    file_name="student_list.csv",
    mime="text/csv"
)

st.divider()

# Student Detail View
st.subheader("👤 Student Detail View")

selected_id = st.selectbox(
    "Select Student ID for Detailed View",
    options=filtered_df['StudentID'].tolist() if len(filtered_df) > 0 else [],
    format_func=lambda x: f"{x} - {filtered_df[filtered_df['StudentID']==x]['FirstName'].iloc[0]} {filtered_df[filtered_df['StudentID']==x]['LastName'].iloc[0]}" if len(filtered_df) > 0 else str(x)
)

if selected_id:
    student = df[df['StudentID'] == selected_id].iloc[0]
    
    # Student header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"## {student['FirstName']} {student['LastName']}")
        st.markdown(f"**Student ID:** {student['StudentID']}")
    
    with col2:
        risk_color = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(student['RiskCategory'], '⚪')
        
        st.markdown(f"### {risk_color} {student['RiskCategory']}")
        st.markdown(f"**Risk Score: {student['RiskScore']:.0f}/100**")
    
    st.divider()
    
    # Tabs for different information
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Academic", "📊 Engagement", "💰 Financial", "🏥 Wellness", "📈 Analytics"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Academic Information")
            # Calculate GPA
            student_enr = enrollments[enrollments['StudentID'] == selected_id]
            student_grd = grades[grades['EnrollmentID'].isin(student_enr['EnrollmentID'])]
            calc_gpa = student_grd['GradePercentage'].mean() / 25 if len(student_grd) > 0 else 3.0
            st.metric("Current GPA", f"{calc_gpa:.2f}")
            st.write(f"**Classification:** {student['Classification']}")
            st.write(f"**Email:** {student['Email']}")
            
            if 'HighSchoolGPA' in student:
                st.write(f"**High School GPA:** {student['HighSchoolGPA']:.2f}")
        
        with col2:
            st.markdown("### Enrollment Status")
            student_enrollments = enrollments[enrollments['StudentID'] == selected_id]
            
            st.metric("Current Enrollments", len(student_enrollments))
            
            active_enrollments = student_enrollments[student_enrollments['Status'] == 'Active']
            completed_enrollments = student_enrollments[student_enrollments['Status'] == 'Completed']
            withdrawn_enrollments = student_enrollments[student_enrollments['Status'] == 'Withdrawn']
            
            st.write(f"**Active:** {len(active_enrollments)}")
            st.write(f"**Completed:** {len(completed_enrollments)}")
            st.write(f"**Withdrawn:** {len(withdrawn_enrollments)}")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### LMS Activity")
            student_logins = load_logins()
            student_login_data = student_logins[student_logins['StudentID'] == selected_id]
            
            st.metric("Total Logins", len(student_login_data))
            
            if len(student_login_data) > 0:
                avg_duration = student_login_data['SessionDurationMinutes'].mean()
                st.metric("Avg Session Duration", f"{avg_duration:.0f} min")
        
        with col2:
            st.markdown("### Attendance")
            st.info("Attendance data available in full analytics")
    
    with tab3:
        st.markdown("### Financial Information")
        
        payments = load_payments()
        student_payments = payments[payments['StudentID'] == selected_id]
        
        if len(student_payments) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_paid = student_payments['AmountPaid'].sum()
                st.metric("Total Paid", f"${total_paid:,.2f}")
            
            with col2:
                total_owed = student_payments['AmountOwed'].sum()
                st.metric("Total Owed", f"${total_owed:,.2f}")
            
            with col3:
                balance = student_payments['Balance'].iloc[0] if 'Balance' in student_payments.columns else 0
                st.metric("Current Balance", f"${balance:,.2f}")
        else:
            st.info("No payment records available")
    
    with tab4:
        st.markdown("### Wellness & Support")
        
        counseling = load_counseling()
        student_counseling = counseling[counseling['StudentID'] == selected_id]
        
        if len(student_counseling) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Counseling Visits", len(student_counseling))
            
            with col2:
                if 'SeverityLevel' in student_counseling.columns:
                    max_severity = student_counseling['SeverityLevel'].max()
                    st.metric("Max Severity Level", max_severity)
            
            st.dataframe(
                student_counseling[['SessionDate', 'ConcernType', 'SeverityLevel']].head(5)
                if 'SessionDate' in student_counseling.columns else student_counseling.head(5),
                use_container_width=True
            )
        else:
            st.info("No counseling records available")
    
    with tab5:
        st.markdown("### Risk Analytics")
        
        import plotly.graph_objects as go
        
        # Risk score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=student['RiskScore'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#DC2626" if student['RiskScore'] >= 70 else "#F59E0B" if student['RiskScore'] >= 50 else "#10B981"},
                'steps': [
                    {'range': [0, 30], 'color': "#D1FAE5"},
                    {'range': [30, 50], 'color': "#FEF3C7"},
                    {'range': [50, 70], 'color': "#FED7AA"},
                    {'range': [70, 100], 'color': "#FEE2E2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk factors
        st.markdown("**Primary Risk Factors:**")
        
        # Get GPA for this student
        stud_enr = enrollments[enrollments['StudentID'] == selected_id]
        stud_grd = grades[grades['EnrollmentID'].isin(stud_enr['EnrollmentID'])]
        stud_gpa = stud_grd['GradePercentage'].mean() / 25 if len(stud_grd) > 0 else 3.0
        
        if stud_gpa < 2.5:
            st.error("⚠️ Low GPA (< 2.5)")
        
        if len(student_login_data) < 50:
            st.warning("⚠️ Low LMS Engagement (< 50 logins)")
        
        if len(withdrawn_enrollments) > 0:
            st.warning(f"⚠️ Course Withdrawals ({len(withdrawn_enrollments)})")

st.divider()

# Footer statistics
st.markdown("### 📊 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", len(filtered_df))

with col2:
    avg_gpa = filtered_df['CalculatedGPA'].mean()
    st.metric("Average GPA", f"{avg_gpa:.2f}")

with col3:
    avg_risk = filtered_df['RiskScore'].mean()
    st.metric("Average Risk Score", f"{avg_risk:.1f}")

with col4:
    at_risk = len(filtered_df[filtered_df['RiskCategory'].isin(['Critical', 'High'])])
    st.metric("At-Risk Students", at_risk)
