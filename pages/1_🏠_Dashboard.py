"""
Advisor Dashboard - Action Queue
=================================
Priority view of at-risk students requiring intervention
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import database version first, fallback to CSV version
try:
    from utils.db_data_loader import (
        load_students, load_risk_scores, load_enrollments, 
        load_logins, load_grades, load_counseling, load_attendance
    )
    from utils.intervention_manager import intervention_manager
    from database.db_manager import db
    DATABASE_MODE = True
except ImportError:
    from utils.data_loader import (
        load_students, load_risk_scores, load_enrollments, 
        load_logins, load_grades, load_counseling, load_attendance
    )
    DATABASE_MODE = False

import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Advisor Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"  # Ensure sidebar is visible by default
)

# Check authentication FIRST
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please log in to access this page")
    st.info("Redirecting to login page...")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Check role
if st.session_state.get("role") not in ['advisor', 'admin']:
    st.error("🚫 Access Denied: This page is for Advisors and Admins only")
    st.stop()

# Custom CSS - Hide unnecessary sidebar pages (hide Admin Portal only for advisors)
admin_portal_css = """
    [data-testid="stSidebarNav"] li:has(a[href*="Admin_Portal"]) {
        display: none;
    }
""" if st.session_state.get("role") != "admin" else ""

st.markdown(f"""
    <style>
    /* Hide public pages and Student Portal */
    [data-testid="stSidebarNav"] li:has(a[href*="app"]),
    [data-testid="stSidebarNav"] li:has(a[href*="SignUp"]),
    [data-testid="stSidebarNav"] li:has(a[href*="Login"]),
    [data-testid="stSidebarNav"] li:has(a[href*="Student_Portal"]) {{
        display: none;
    }}
    {admin_portal_css}
    
    .risk-critical {{
        border-left: 5px solid #DC2626;
        padding: 15px;
        background-color: #FEE2E2;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .risk-high {{
        border-left: 5px solid #F59E0B;
        padding: 15px;
        background-color: #FEF3C7;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .risk-medium {{
        border-left: 5px solid #FBBF24;
        padding: 15px;
        background-color: #FEF3C7;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .risk-low {{
        border-left: 5px solid #10B981;
        padding: 15px;
        background-color: #D1FAE5;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# Professional Header with Gradient
mode_badge = "🗄️ Database Mode" if DATABASE_MODE else "📁 CSV Mode"
st.markdown(f"""
    <div style='background: linear-gradient(135deg, #003366 0%, #0055AA 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; font-size: 2.5rem; font-weight: 800;'>🏠 Advisor Action Queue</h1>
        <p style='margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1rem;'>
            Prioritized dashboard for student interventions • Logged in as: <strong>{st.session_state.get('name', 'Advisor')}</strong> • {mode_badge}
        </p>
    </div>
""", unsafe_allow_html=True)

# Quick Action Buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📧 Email All At-Risk", use_container_width=True):
        if DATABASE_MODE:
            # Real implementation: Queue emails for high-risk students
            try:
                high_risk = df[df['RiskCategory'].isin(['Critical', 'High'])]
                count = 0
                for _, student in high_risk.iterrows():
                    # Queue email notification
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO email_queue (
                                to_email, subject, body_html, body_text, email_type, priority
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            student['Email'],
                            f"Important: Academic Support Available - HSU",
                            f"<p>Dear {student['FirstName']},</p><p>Your advisor has identified you as needing additional support. Please schedule a meeting.</p>",
                            f"Dear {student['FirstName']}, Your advisor has identified you as needing additional support. Please schedule a meeting.",
                            'high_risk_alert',
                            5
                        ))
                    count += 1
                st.success(f"✅ {count} emails queued for delivery to at-risk students!")
            except Exception as e:
                st.error(f"Error queueing emails: {e}")
        else:
            # CSV mode - show what would be sent
            email_list = filtered_df['Email'].tolist()
            st.success(f"✅ Would send bulk email to {len(email_list)} at-risk students!")
            with st.expander("View email recipients"):
                st.write(filtered_df[['FirstName', 'LastName', 'Email', 'RiskCategory']])

with col2:
    if st.button("📊 Export Report", use_container_width=True):
        # Real export functionality
        try:
            export_df = filtered_df[['StudentID', 'FirstName', 'LastName', 'Email', 
                                     'Classification', 'CalculatedGPA', 'RiskCategory', 'OverallRiskScore']]
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"advisor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error exporting: {e}")

with col3:
    if st.button("🔔 Create Alert", use_container_width=True):
        if DATABASE_MODE:
            with st.form("create_alert_form"):
                st.markdown("### Create System Alert")
                alert_title = st.text_input("Alert Title", placeholder="e.g., Midterm Check-in Required")
                alert_message = st.text_area("Alert Message", placeholder="Enter alert message...")
                alert_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                alert_target = st.multiselect("Send to", ["All Students", "High Risk", "Medium Risk", "Critical Risk"])
                
                if st.form_submit_button("📤 Send Alert"):
                    if alert_title and alert_message:
                        try:
                            with db.get_connection() as conn:
                                cursor = conn.cursor()
                                # Create notification for targeted students
                                target_students = filtered_df if alert_target else pd.DataFrame()
                                for _, student in target_students.iterrows():
                                    cursor.execute("""
                                        INSERT INTO notifications (
                                            user_id, notification_type, title, message, priority
                                        ) VALUES (?, ?, ?, ?, ?)
                                    """, (student['StudentID'], 'alert', alert_title, alert_message, alert_priority))
                            st.success(f"✅ Alert sent to {len(target_students)} students!")
                        except Exception as e:
                            st.error(f"Error creating alert: {e}")
                    else:
                        st.warning("Please fill in all fields")
        else:
            st.info("🔔 Alert system available in database mode")

with col4:
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        if DATABASE_MODE:
            # Log logout action
            try:
                user_id = st.session_state.get('user_id')
                if user_id:
                    db.log_action(user_id, 'USER_LOGOUT')
            except:
                pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")

st.divider()

# Load data
with st.spinner("Loading student data..."):
    students = load_students()
    risk_scores = load_risk_scores()
    enrollments = load_enrollments()
    grades = load_grades()
    counseling = load_counseling()
    attendance_data = load_attendance()
    logins = load_logins()  # Add logins here

# Merge data
df = students.merge(risk_scores, on='StudentID', how='left')

# Calculate GPA for each student from grades
gpa_dict = {}
for student_id in df['StudentID']:
    student_enr = enrollments[enrollments['StudentID'] == student_id]
    student_grd = grades[grades['EnrollmentID'].isin(student_enr['EnrollmentID'])]
    if len(student_grd) > 0:
        gpa = student_grd['GradePercentage'].mean() / 25  # Convert to 4.0 scale
        gpa_dict[student_id] = gpa
    else:
        gpa_dict[student_id] = 3.0  # Default

df['CalculatedGPA'] = df['StudentID'].map(gpa_dict)

# Add search functionality
st.markdown("### 🔍 Search Students")
search_term = st.text_input("Search by name or student ID", placeholder="Enter name or ID...")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Risk level filter
risk_levels = ['Critical', 'High', 'Medium', 'Low']
selected_risks = st.sidebar.multiselect(
    "Risk Level",
    options=risk_levels,
    default=['Critical', 'High']
)

# Classification filter removed major since it doesn't exist in students table

# Classification filter
if 'Classification' in df.columns:
    classifications = ['All'] + sorted(df['Classification'].unique().tolist())
    selected_class = st.sidebar.selectbox("Classification", classifications)
else:
    selected_class = 'All'

# First-Gen filter
show_first_gen = st.sidebar.checkbox("First-Generation Only", value=False)

# Sort options
sort_by = st.sidebar.selectbox(
    "Sort By",
    ["Risk Score (High to Low)", "Risk Score (Low to High)", "GPA (Low to High)", "GPA (High to Low)", "Name (A-Z)"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Apply filters
filtered_df = df.copy()

# Apply search
if search_term:
    search_term_lower = search_term.lower()
    filtered_df = filtered_df[
        filtered_df['FirstName'].str.lower().str.contains(search_term_lower, na=False) |
        filtered_df['LastName'].str.lower().str.contains(search_term_lower, na=False) |
        filtered_df['StudentID'].astype(str).str.contains(search_term, na=False)
    ]

if selected_risks:
    filtered_df = filtered_df[filtered_df['RiskCategory'].isin(selected_risks)]

if selected_class != 'All':
    filtered_df = filtered_df[filtered_df['Classification'] == selected_class]

if show_first_gen and 'FirstGenerationStudent' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['FirstGenerationStudent'] == True]

# Apply sorting
if sort_by == "Risk Score (High to Low)":
    filtered_df = filtered_df.sort_values('OverallRiskScore', ascending=False)
elif sort_by == "Risk Score (Low to High)":
    filtered_df = filtered_df.sort_values('OverallRiskScore', ascending=True)
elif sort_by == "GPA (Low to High)":
    filtered_df = filtered_df.sort_values('CalculatedGPA', ascending=True)
elif sort_by == "GPA (High to Low)":
    filtered_df = filtered_df.sort_values('CalculatedGPA', ascending=False)
elif sort_by == "Name (A-Z)":
    filtered_df = filtered_df.sort_values('LastName', ascending=True)

# Show Pending Appointment Requests
st.markdown("### 📅 Pending Appointment Requests")

try:
    import sqlite3
    conn = sqlite3.connect('database/hsu_database.db')
    
    pending_requests_query = """
        SELECT 
            i.intervention_id,
            i.student_id,
            s.first_name,
            s.last_name,
            i.title,
            i.description,
            i.scheduled_date,
            i.created_at,
            i.priority
        FROM interventions i
        JOIN students s ON i.student_id = s.student_id
        WHERE i.status = 'Pending' AND i.title LIKE '%Appointment Request%'
        ORDER BY i.created_at DESC
        LIMIT 10
    """
    
    pending_requests = pd.read_sql_query(pending_requests_query, conn)
    conn.close()
    
    if not pending_requests.empty:
        st.info(f"📬 {len(pending_requests)} new appointment request(s) awaiting response")
        
        for idx, req in pending_requests.iterrows():
            with st.expander(f"🟡 {req['first_name']} {req['last_name']} - {req['title']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Student:** {req['first_name']} {req['last_name']} (ID: {req['student_id']})")
                    st.write(f"**Request Type:** {req['title']}")
                    st.write(f"**Requested:** {req['created_at']}")
                    st.write(f"**Preferred Time:** {req['scheduled_date']}")
                    st.write(f"**Details:**")
                    st.text(req['description'])
                
                with col2:
                    if st.button(f"✅ Approve", key=f"approve_{req['intervention_id']}"):
                        try:
                            conn = sqlite3.connect('database/hsu_database.db')
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE interventions 
                                SET status = 'Scheduled'
                                WHERE intervention_id = ?
                            """, (req['intervention_id'],))
                            conn.commit()
                            conn.close()
                            st.success("✅ Approved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    if st.button(f"❌ Decline", key=f"decline_{req['intervention_id']}"):
                        try:
                            conn = sqlite3.connect('database/hsu_database.db')
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE interventions 
                                SET status = 'Cancelled'
                                WHERE intervention_id = ?
                            """, (req['intervention_id'],))
                            conn.commit()
                            conn.close()
                            st.warning("Declined")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    else:
        st.success("✅ No pending appointment requests")
except Exception as e:
    st.warning(f"Could not load appointment requests: {e}")

st.markdown("---")

# Summary metrics with gradient cards
st.markdown("### 📊 At-A-Glance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    critical_count = len(df[df['RiskCategory'] == 'Critical'])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{critical_count}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>🔴 Critical Risk</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>Immediate action needed</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    high_count = len(df[df['RiskCategory'] == 'High'])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{high_count}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>🟠 High Risk</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>Needs intervention</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    medium_count = len(df[df['RiskCategory'] == 'Medium'])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{medium_count}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>🟡 Medium Risk</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>Monitor closely</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    low_count = len(df[df['RiskCategory'] == 'Low'])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{low_count}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>🟢 Low Risk</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>On track</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Student cards
st.subheader(f"📋 Action Queue ({len(filtered_df)} students)")

if len(filtered_df) == 0:
    st.info("No students match the selected filters.")
else:
    # Display student cards
    for idx, student in filtered_df.iterrows():
        # Determine risk emoji and color
        risk_emoji = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(student['RiskCategory'], '⚪')
        
        # Create expander for each student
        risk_score = student.get('OverallRiskScore', 0) * 100  # Convert to 0-100 scale
        gpa = student.get('CalculatedGPA', 3.0)
        
        with st.expander(
            f"{risk_emoji} {student['FirstName']} {student['LastName']} - "
            f"Risk: {risk_score:.0f}/100 - GPA: {gpa:.2f}",
            expanded=(student['RiskCategory'] == 'Critical')
        ):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("**📚 Academic Information**")
                st.write(f"**Student ID:** {student['StudentID']}")
                st.write(f"**GPA:** {gpa:.2f}")
                st.write(f"**Classification:** {student['Classification']}")
                st.write(f"**Email:** {student['Email']}")
                
                if 'FirstGenerationStudent' in student and student['FirstGenerationStudent']:
                    st.write("**First-Generation:** ✓ Yes")
                
                if 'InternationalStudent' in student and student['InternationalStudent']:
                    st.write("**International:** ✓ Yes")
            
            with col2:
                st.markdown("**⚠️ Risk Assessment**")
                st.write(f"**Risk Score:** {risk_score:.0f}/100")
                st.write(f"**Category:** {risk_emoji} {student['RiskCategory']}")
                
                # Progress bar for risk score
                st.progress(risk_score / 100)
                
                st.markdown("**📊 Key Indicators:**")
                
                # Get login count
                student_logins = logins[logins['StudentID'] == student['StudentID']]
                login_count = len(student_logins)
                st.write(f"• LMS Logins: {login_count}")
                
                # Get enrollment count
                student_enrollments = enrollments[enrollments['StudentID'] == student['StudentID']]
                active_enrollments = len(student_enrollments[student_enrollments['Status'] == 'Active'])
                st.write(f"• Active Courses: {active_enrollments}")
                
                # Get counseling visits
                student_counseling = counseling[counseling['StudentID'] == student['StudentID']]
                st.write(f"• Counseling Visits: {len(student_counseling)}")
            
            with col3:
                st.markdown("**🎯 Actions**")
                
                if st.button(f"📅 Schedule Meeting", key=f"meet_{student['StudentID']}"):
                    if DATABASE_MODE:
                        try:
                            # Create appointment in database
                            advisor_id = st.session_state.get('advisor_id', 1)
                            meeting_date = datetime.now() + timedelta(days=2)
                            
                            with db.get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO appointments (
                                        student_id, advisor_id, appointment_date, 
                                        duration_minutes, location, method, purpose, status
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    student['StudentID'],
                                    advisor_id,
                                    meeting_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    30,
                                    'Office Hours',
                                    'In-person',
                                    'Academic advising check-in',
                                    'Scheduled'
                                ))
                            
                            st.success(f"✅ Meeting scheduled for {meeting_date.strftime('%B %d, %Y at %I:%M %p')}!")
                            st.info("📧 Calendar invite queued for student")
                            
                            # Log action
                            db.log_action(st.session_state.get('user_id'), 'APPOINTMENT_CREATED', 'appointments', cursor.lastrowid)
                        except Exception as e:
                            st.error(f"Error scheduling meeting: {e}")
                    else:
                        # CSV mode - show confirmation
                        st.success(f"✅ Would schedule meeting with {student['FirstName']} {student['LastName']}")
                        st.info(f"📅 {meeting_date} at {meeting_time} via {meeting_method}")
                
                if st.button(f"📧 Send Email", key=f"email_{student['StudentID']}"):
                    if DATABASE_MODE:
                        try:
                            # Queue email in database
                            with db.get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO email_queue (
                                        to_email, subject, body_html, body_text, email_type, priority
                                    ) VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    student['Email'],
                                    f"Check-in from Your Advisor - HSU",
                                    f"<p>Dear {student['FirstName']},</p><p>I wanted to check in with you regarding your academic progress. Please let me know if you need any support.</p><p>Best regards,<br>{st.session_state.get('name', 'Your Advisor')}</p>",
                                    f"Dear {student['FirstName']}, I wanted to check in with you regarding your academic progress. Please let me know if you need any support. Best regards, {st.session_state.get('name', 'Your Advisor')}",
                                    'advisor_checkin',
                                    3
                                ))
                            
                            st.success(f"✅ Email queued to {student['Email']}!")
                            
                            # Log action
                            db.log_action(st.session_state.get('user_id'), 'EMAIL_SENT', 'students', student['StudentID'])
                        except Exception as e:
                            st.error(f"Error sending email: {e}")
                    else:
                        # CSV mode - show what would be sent
                        st.success(f"✅ Would send email to {student['Email']}")
                        st.info(f"Subject: Check-in from Your Advisor")
                
                if st.button(f"🎯 Create Intervention", key=f"interv_{student['StudentID']}"):
                    if DATABASE_MODE:
                        try:
                            # Create intervention in database
                            import sqlite3
                            from datetime import datetime
                            
                            conn = sqlite3.connect('database/hsu_database.db')
                            cursor = conn.cursor()
                            
                            # Get advisor ID
                            advisor_id = st.session_state.get('user_id', 1)
                            
                            # Create intervention
                            intervention_title = f"Academic Support for {student['FirstName']} {student['LastName']}"
                            intervention_desc = f"Risk Level: {student['RiskCategory']}\nGPA: {student['CalculatedGPA']:.2f}\nAction Required: Follow-up and support"
                            
                            cursor.execute("""
                                INSERT INTO interventions 
                                (student_id, advisor_id, title, description, priority, status, scheduled_date, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                student['StudentID'],
                                advisor_id,
                                intervention_title,
                                intervention_desc,
                                'High' if student['RiskCategory'] in ['Critical', 'High'] else 'Medium',
                                'In Progress',
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            ))
                            
                            intervention_id = cursor.lastrowid
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Intervention created! (ID: {intervention_id})")
                            st.info("Student will be notified")
                        except Exception as e:
                            st.error(f"Error creating intervention: {e}")
                    else:
                        st.success(f"✅ Would create intervention for {student['FirstName']} {student['LastName']}")
                
                if st.button(f"📝 Log Note", key=f"note_{student['StudentID']}"):
                    if DATABASE_MODE:
                        # Create a form for note entry
                        with st.form(key=f"note_form_{student['StudentID']}"):
                            note_subject = st.text_input("Subject", placeholder="e.g., Academic concerns")
                            note_content = st.text_area("Note", placeholder="Enter your note here...")
                            note_type = st.selectbox("Type", ["General", "Academic", "Behavioral", "Financial", "Personal"])
                            is_private = st.checkbox("Private note (only you can see)")
                            
                            if st.form_submit_button("💾 Save Note"):
                                if note_content:
                                    try:
                                        advisor_id = st.session_state.get('advisor_id', 1)
                                        with db.get_connection() as conn:
                                            cursor = conn.cursor()
                                            cursor.execute("""
                                                INSERT INTO student_notes (
                                                    student_id, advisor_id, note_type, 
                                                    subject, content, is_private
                                                ) VALUES (?, ?, ?, ?, ?, ?)
                                            """, (
                                                student['StudentID'],
                                                advisor_id,
                                                note_type,
                                                note_subject,
                                                note_content,
                                                1 if is_private else 0
                                            ))
                                        
                                        st.success("✅ Note saved successfully!")
                                        
                                        # Log action
                                        db.log_action(st.session_state.get('user_id'), 'NOTE_CREATED', 'student_notes', cursor.lastrowid)
                                    except Exception as e:
                                        st.error(f"Error saving note: {e}")
                                else:
                                    st.warning("Please enter note content")
                    else:
                        # CSV mode - show note form anyway
                        with st.form(key=f"note_form_{student['StudentID']}"):
                            st.markdown("### Add Note (View Only)")
                            note_subject = st.text_input("Subject", placeholder="e.g., Academic concerns")
                            note_content = st.text_area("Note", placeholder="Note taking available in database mode...")
                            note_type = st.selectbox("Type", ["General", "Academic", "Behavioral", "Financial", "Personal"])
                            
                            if st.form_submit_button("💾 Save Note"):
                                st.info("📝 Note saving available in database mode")
            
            # Recommended interventions
            st.markdown("**💡 Recommended Interventions:**")
            
            if student['RiskCategory'] == 'Critical':
                st.error("""
                🚨 **Immediate Action Required:**
                - Schedule urgent advising meeting (within 24 hours)
                - Academic recovery plan development
                - Financial aid emergency review
                - Mental health resource referral
                """)
            elif student['RiskCategory'] == 'High':
                st.warning("""
                ⚠️ **High Priority (within 1 week):**
                - Schedule advising meeting
                - Tutoring center referral
                - Attendance monitoring
                - Financial aid consultation
                """)
            elif student['RiskCategory'] == 'Medium':
                st.info("""
                📋 **Monitor Closely:**
                - Check-in within 2 weeks
                - Academic resources recommendation
                - Engagement activity invitation
                """)
            else:
                st.success("""
                ✅ **On Track:**
                - Regular check-in (monthly)
                - Encourage continued success
                """)

# Footer with enhanced statistics
st.divider()
st.markdown("### 📈 Detailed Analytics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_risk = filtered_df['OverallRiskScore'].mean() * 100
    st.markdown(f"""
        <div style='background: #F3F4F6; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold; color: #374151;'>{avg_risk:.1f}</div>
            <div style='color: #6B7280; font-size: 0.9rem;'>Avg Risk Score</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    avg_gpa = filtered_df['CalculatedGPA'].mean()
    st.markdown(f"""
        <div style='background: #F3F4F6; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold; color: #374151;'>{avg_gpa:.2f}</div>
            <div style='color: #6B7280; font-size: 0.9rem;'>Average GPA</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    action_needed = len(filtered_df[filtered_df['RiskCategory'].isin(['Critical', 'High'])])
    st.markdown(f"""
        <div style='background: #FEE2E2; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold; color: #DC2626;'>{action_needed}</div>
            <div style='color: #991B1B; font-size: 0.9rem;'>Actions Needed</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    first_gen_count = len(filtered_df[filtered_df['FirstGenerationStudent'] == True])
    st.markdown(f"""
        <div style='background: #DBEAFE; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold; color: #1E40AF;'>{first_gen_count}</div>
            <div style='color: #1E3A8A; font-size: 0.9rem;'>First-Gen Students</div>
        </div>
    """, unsafe_allow_html=True)

# Advanced Professional Visualizations
st.markdown("### 📊 Advanced Risk Analytics & Visualizations")

# Create three columns for multiple charts
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    # Enhanced Donut Chart with Gradient Effects
    st.markdown("#### 🎯 Risk Distribution Overview")
    risk_dist_data = filtered_df['RiskCategory'].value_counts()
    
    # Calculate percentages
    total_students = len(filtered_df)
    risk_percentages = (risk_dist_data / total_students * 100).round(1)
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=risk_dist_data.index,
        values=risk_dist_data.values,
        hole=0.6,
        marker=dict(
            colors=['#DC2626', '#F59E0B', '#FBBF24', '#10B981'],
            line=dict(color='white', width=3)
        ),
        textposition='outside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Students: %{value}<br>Percentage: %{percent}<extra></extra>',
        pull=[0.1 if cat == 'Critical' else 0.05 if cat == 'High' else 0 for cat in risk_dist_data.index]
    )])
    
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        height=400,
        margin=dict(t=30, b=80, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=12),
        annotations=[dict(
            text=f'<b>{total_students}</b><br>Total<br>Students',
            x=0.5, y=0.5,
            font=dict(size=20, color='#1F2937'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)

with viz_col2:
    # 3D Funnel Chart showing risk progression
    st.markdown("#### 📉 Risk Level Funnel")
    
    # Sort by severity for funnel
    risk_order = ['Critical', 'High', 'Medium', 'Low']
    risk_counts = [risk_dist_data.get(cat, 0) for cat in risk_order]
    
    fig_funnel = go.Figure(go.Funnel(
        y=risk_order,
        x=risk_counts,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=['#DC2626', '#F59E0B', '#FBBF24', '#10B981'],
            line=dict(width=2, color='white')
        ),
        connector=dict(line=dict(color='#E5E7EB', width=2)),
        hovertemplate='<b>%{y}</b><br>Students: %{x}<br>Of Total: %{percentInitial}<extra></extra>'
    ))
    
    fig_funnel.update_layout(
        height=400,
        margin=dict(t=30, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)

# Full-width advanced visualizations
st.markdown("---")

viz_col3, viz_col4 = st.columns(2)

with viz_col3:
    # Gauge Chart for Average Risk Score
    st.markdown("#### 🎚️ Average Risk Score Gauge")
    avg_risk_score = filtered_df['OverallRiskScore'].mean() * 100
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Risk Level", 'font': {'size': 18}},
        delta={'reference': 50, 'increasing': {'color': "#DC2626"}, 'decreasing': {'color': "#10B981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#6B7280"},
            'bar': {'color': "#3B82F6", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, 25], 'color': '#D1FAE5'},
                {'range': [25, 50], 'color': '#FEF3C7'},
                {'range': [50, 75], 'color': '#FED7AA'},
                {'range': [75, 100], 'color': '#FEE2E2'}
            ],
            'threshold': {
                'line': {'color': "#DC2626", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=350,
        margin=dict(t=60, b=20, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial, sans-serif", 'size': 14, 'color': "#1F2937"}
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)

with viz_col4:
    # Bar Chart with Risk Factor Breakdown
    st.markdown("#### 📊 Risk Factor Analysis")
    
    risk_factors = {
        'Academic': filtered_df['AcademicRiskFactor'].mean() * 100,
        'Engagement': filtered_df['EngagementRiskFactor'].mean() * 100,
        'Financial': filtered_df['FinancialRiskFactor'].mean() * 100,
        'Wellness': filtered_df['WellnessRiskFactor'].mean() * 100
    }
    
    fig_factors = go.Figure(data=[
        go.Bar(
            x=list(risk_factors.keys()),
            y=list(risk_factors.values()),
            marker=dict(
                color=list(risk_factors.values()),
                colorscale=[
                    [0, '#10B981'],
                    [0.5, '#FBBF24'],
                    [1, '#DC2626']
                ],
                line=dict(color='white', width=2),
                showscale=False  # Changed from True to False to avoid colorbar issues
            ),
            text=[f'{v:.1f}%' for v in risk_factors.values()],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Risk Level: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig_factors.update_layout(
        yaxis=dict(
            title='Risk Level (%)',
            range=[0, 100],
            gridcolor='#E5E7EB',
            gridwidth=1
        ),
        xaxis=dict(title='Risk Category', tickfont=dict(size=11)),
        height=350,
        margin=dict(t=30, b=40, l=60, r=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        showlegend=False
    )
    
    st.plotly_chart(fig_factors, use_container_width=True)

# Heatmap for Risk Distribution by Classification
st.markdown("#### 🔥 Risk Heatmap by Classification")

if 'Classification' in filtered_df.columns and len(filtered_df) > 0:
    # Create pivot table
    heatmap_data = pd.crosstab(
        filtered_df['Classification'],
        filtered_df['RiskCategory']
    )
    
    # Reorder columns
    col_order = ['Critical', 'High', 'Medium', 'Low']
    heatmap_data = heatmap_data.reindex(columns=[col for col in col_order if col in heatmap_data.columns])
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0, '#D1FAE5'],
            [0.33, '#FEF3C7'],
            [0.66, '#FED7AA'],
            [1, '#FEE2E2']
        ],
        text=heatmap_data.values,
        texttemplate='<b>%{text}</b>',
        textfont={"size": 14},
        hovertemplate='<b>%{y}</b><br>Risk: %{x}<br>Students: %{z}<extra></extra>',
        showscale=False  # Disabled colorbar to avoid Python 3.13 compatibility issues
    ))
    
    fig_heatmap.update_layout(
        xaxis=dict(title='Risk Category', side='bottom', tickfont=dict(size=12)),
        yaxis=dict(title='Classification', tickfont=dict(size=12)),
        height=300,
        margin=dict(t=20, b=60, l=100, r=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Advanced Summary Statistics
st.markdown("#### 📈 Statistical Insights")
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    median_risk = filtered_df['OverallRiskScore'].median() * 100
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold;'>{median_risk:.1f}</div>
            <div style='opacity: 0.9; margin-top: 5px; font-size: 0.9rem;'>Median Risk Score</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col2:
    std_dev = filtered_df['OverallRiskScore'].std() * 100
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold;'>{std_dev:.1f}</div>
            <div style='opacity: 0.9; margin-top: 5px; font-size: 0.9rem;'>Std Deviation</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col3:
    high_risk_pct = len(filtered_df[filtered_df['RiskCategory'].isin(['Critical', 'High'])]) / len(filtered_df) * 100
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold;'>{high_risk_pct:.1f}%</div>
            <div style='opacity: 0.9; margin-top: 5px; font-size: 0.9rem;'>High Risk Students</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col4:
    intervention_needed = len(filtered_df[filtered_df['OverallRiskScore'] > 0.7])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2rem; font-weight: bold;'>{intervention_needed}</div>
            <div style='opacity: 0.9; margin-top: 5px; font-size: 0.9rem;'>Need Intervention</div>
        </div>
    """, unsafe_allow_html=True)
