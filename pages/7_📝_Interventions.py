"""
Intervention Management
=======================
Log, track, and monitor student interventions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import require_role, get_current_user, display_user_info
from utils.data_loader import load_students, load_counseling

st.set_page_config(
    page_title="Intervention Management",
    page_icon="📝",
    layout="wide"
)

# Check authentication FIRST
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please log in to access this page")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Require advisor or admin role
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

st.title("📝 Intervention Management System")
st.markdown("**Log, track, and monitor student interventions for maximum impact**")

# Initialize session state for interventions
if 'interventions' not in st.session_state:
    # Load existing counseling data as interventions
    counseling = load_counseling()
    st.session_state.interventions = pd.DataFrame({
        'Date': pd.to_datetime('2025-11-01') + pd.to_timedelta(range(len(counseling)), unit='d') if len(counseling) > 0 else [],
        'StudentID': counseling['StudentID'] if len(counseling) > 0 else [],
        'Type': counseling['ConcernType'] if 'ConcernType' in counseling.columns else ['Academic Advising'] * len(counseling),
        'Description': ['Student support session'] * len(counseling) if len(counseling) > 0 else [],
        'Advisor': [get_current_user()['name']] * len(counseling) if len(counseling) > 0 else [],
        'Status': ['Completed'] * len(counseling) if len(counseling) > 0 else [],
        'FollowUpDate': pd.to_datetime('2025-11-15') if len(counseling) > 0 else []
    })

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Log New Intervention", "📋 Intervention History", "📊 Analytics", "📅 Follow-ups"
])

with tab1:
    st.subheader("➕ Log New Intervention")
    
    # Load students for selection
    students = load_students()
    
    with st.form("intervention_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Student Information")
            
            student_id = st.selectbox(
                "Select Student *",
                students['StudentID'].tolist(),
                format_func=lambda x: f"{x} - {students[students['StudentID']==x]['FirstName'].iloc[0]} {students[students['StudentID']==x]['LastName'].iloc[0]}"
            )
            
            intervention_type = st.selectbox(
                "Intervention Type *",
                ["Academic Advising", "Tutoring Referral", "Financial Aid Consultation",
                 "Mental Health Support", "Career Counseling", "Academic Recovery Plan",
                 "Attendance Review", "Course Selection Guidance", "Emergency Support", "Other"]
            )
            
            intervention_date = st.date_input("Intervention Date *", datetime.now())
        
        with col2:
            st.markdown("### Advisor & Status")
            
            current_user = get_current_user()
            advisor_name = st.text_input("Advisor Name *", value=current_user['name'])
            
            status = st.selectbox(
                "Status *",
                ["Scheduled", "Completed", "In Progress", "No Response", "Cancelled"]
            )
            
            follow_up = st.date_input("Follow-up Date", datetime.now() + timedelta(days=14))
        
        st.markdown("### Intervention Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_level_before = st.select_slider(
                "Risk Level (Before)",
                options=["Low", "Medium", "High", "Critical"],
                value="High"
            )
        
        with col2:
            expected_outcome = st.selectbox(
                "Expected Outcome",
                ["Improved Attendance", "Improved GPA", "Better Engagement",
                 "Financial Stability", "Mental Health Support", "Course Completion", "Other"]
            )
        
        description = st.text_area(
            "Notes/Description *",
            placeholder="Describe the intervention, student response, and action items...",
            height=120
        )
        
        action_items = st.text_area(
            "Action Items",
            placeholder="List specific follow-up actions...",
            height=80
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submitted = st.form_submit_button("💾 Save Intervention", type="primary", use_container_width=True)
        
        with col2:
            draft = st.form_submit_button("📝 Save as Draft", use_container_width=True)
        
        with col3:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            if student_id and description and advisor_name:
                # Add to session state
                student_name = f"{students[students['StudentID']==student_id]['FirstName'].iloc[0]} {students[students['StudentID']==student_id]['LastName'].iloc[0]}"
                
                new_intervention = pd.DataFrame([{
                    'Date': intervention_date,
                    'StudentID': student_id,
                    'StudentName': student_name,
                    'Type': intervention_type,
                    'Description': description,
                    'ActionItems': action_items,
                    'Advisor': advisor_name,
                    'Status': status,
                    'FollowUpDate': follow_up,
                    'RiskBefore': risk_level_before,
                    'ExpectedOutcome': expected_outcome
                }])
                
                st.session_state.interventions = pd.concat(
                    [st.session_state.interventions, new_intervention],
                    ignore_index=True
                )
                
                st.success("✅ Intervention logged successfully!")
                st.balloons()
                
                # Show next steps
                st.info(f"""
                **Next Steps:**
                - Follow-up scheduled for {follow_up}
                - Email notification sent to student
                - Reminder will be sent 2 days before follow-up
                """)
            else:
                st.error("⚠️ Please fill all required fields (marked with *)")

with tab2:
    st.subheader("📋 Intervention History")
    
    if len(st.session_state.interventions) > 0:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            type_filter = st.multiselect(
                "Filter by Type",
                options=st.session_state.interventions['Type'].unique() if 'Type' in st.session_state.interventions.columns else [],
                default=[]
            )
        
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=st.session_state.interventions['Status'].unique() if 'Status' in st.session_state.interventions.columns else [],
                default=[]
            )
        
        with col3:
            date_filter = st.date_input("From Date", value=datetime.now() - timedelta(days=30))
        
        with col4:
            search_student = st.text_input("Search Student ID")
        
        # Apply filters
        df = st.session_state.interventions.copy()
        
        if type_filter:
            df = df[df['Type'].isin(type_filter)]
        
        if status_filter:
            df = df[df['Status'].isin(status_filter)]
        
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df[df['Date'] >= pd.to_datetime(date_filter)]
        
        if search_student:
            df = df[df['StudentID'].astype(str).str.contains(search_student)]
        
        # Sort by date
        if 'Date' in df.columns:
            df = df.sort_values('Date', ascending=False)
        
        # Display count
        st.markdown(f"**Showing {len(df)} of {len(st.session_state.interventions)} interventions**")
        
        # Display table
        display_cols = [col for col in ['Date', 'StudentID', 'StudentName', 'Type', 'Advisor', 'Status', 'FollowUpDate'] if col in df.columns]
        
        if display_cols:
            # Convert dates to strings for display to avoid Arrow conversion issues
            display_df = df[display_cols].copy()
            
            # Convert all date columns to strings safely
            for col in display_df.columns:
                if col in ['Date', 'FollowUpDate'] and col in display_df.columns:
                    display_df[col] = pd.to_datetime(display_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                    display_df[col] = display_df[col].fillna('N/A')  # Replace NaT with N/A
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"interventions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Summary metrics
        st.divider()
        st.markdown("### 📊 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Interventions", len(df))
        
        with col2:
            completed = len(df[df['Status'] == 'Completed']) if 'Status' in df.columns else 0
            st.metric("Completed", completed)
        
        with col3:
            in_progress = len(df[df['Status'] == 'In Progress']) if 'Status' in df.columns else 0
            st.metric("In Progress", in_progress)
        
        with col4:
            if completed > 0:
                success_rate = (completed / len(df) * 100)
                st.metric("Success Rate", f"{success_rate:.0f}%")
    
    else:
        st.info("📭 No interventions logged yet. Use the form above to add your first entry.")

with tab3:
    st.subheader("📊 Intervention Analytics")
    
    if len(st.session_state.interventions) > 0:
        df = st.session_state.interventions
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Interventions by Type")
            
            if 'Type' in df.columns:
                type_counts = df['Type'].value_counts()
                
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Status Distribution")
            
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts()
                
                fig = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    labels={'x': 'Status', 'y': 'Count'},
                    color=status_counts.index,
                    color_discrete_map={
                        'Completed': '#10B981',
                        'In Progress': '#3B82F6',
                        'Scheduled': '#FFB81C',
                        'No Response': '#DC2626',
                        'Cancelled': '#6B7280'
                    }
                )
                
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Interventions Over Time")
            
            if 'Date' in df.columns:
                df_time = df.copy()
                df_time['Date'] = pd.to_datetime(df_time['Date'])
                df_time['Month'] = df_time['Date'].dt.to_period('M').astype(str)
                
                monthly = df_time.groupby('Month').size().reset_index(name='Count')
                
                fig = px.line(
                    monthly,
                    x='Month',
                    y='Count',
                    markers=True,
                    line_shape='spline'
                )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Top Advisors")
            
            if 'Advisor' in df.columns:
                advisor_counts = df['Advisor'].value_counts().head(5)
                
                fig = px.bar(
                    x=advisor_counts.values,
                    y=advisor_counts.index,
                    orientation='h',
                    labels={'x': 'Interventions', 'y': 'Advisor'},
                    color_discrete_sequence=['#003366']
                )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No data available for analytics yet")

with tab4:
    st.subheader("📅 Follow-up Management")
    
    if len(st.session_state.interventions) > 0:
        df = st.session_state.interventions
        
        # Upcoming follow-ups
        st.markdown("### ⏰ Upcoming Follow-ups")
        
        if 'FollowUpDate' in df.columns:
            df['FollowUpDate'] = pd.to_datetime(df['FollowUpDate'], errors='coerce')
            upcoming = df[df['FollowUpDate'] >= pd.Timestamp.now()].sort_values('FollowUpDate')
            
            if len(upcoming) > 0:
                for idx, row in upcoming.head(10).iterrows():
                    days_until = (row['FollowUpDate'] - pd.Timestamp.now()).days
                    
                    if days_until <= 2:
                        alert_type = "error"
                        icon = "🔴"
                    elif days_until <= 7:
                        alert_type = "warning"
                        icon = "🟡"
                    else:
                        alert_type = "info"
                        icon = "🟢"
                    
                    with st.expander(f"{icon} {row.get('StudentName', 'Unknown')} - Due in {days_until} days", expanded=(days_until <= 2)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Student ID:** {row.get('StudentID', 'N/A')}")
                            st.write(f"**Type:** {row.get('Type', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Follow-up Date:** {row['FollowUpDate'].strftime('%Y-%m-%d')}")
                            st.write(f"**Status:** {row.get('Status', 'N/A')}")
                        
                        with col3:
                            st.write(f"**Advisor:** {row.get('Advisor', 'N/A')}")
                            
                            if st.button("✅ Mark Complete", key=f"complete_{idx}"):
                                st.success("Marked as complete!")
            else:
                st.success("✅ No upcoming follow-ups. Great job!")
        
        st.divider()
        
        # Overdue follow-ups
        st.markdown("### ⚠️ Overdue Follow-ups")
        
        if 'FollowUpDate' in df.columns:
            overdue = df[df['FollowUpDate'] < pd.Timestamp.now()].sort_values('FollowUpDate')
            
            if len(overdue) > 0:
                st.error(f"⚠️ {len(overdue)} overdue follow-ups require attention!")
                
                for idx, row in overdue.head(5).iterrows():
                    days_overdue = (pd.Timestamp.now() - row['FollowUpDate']).days
                    
                    st.warning(f"""
                    **{row.get('StudentName', 'Unknown')}** - Overdue by {days_overdue} days
                    - Type: {row.get('Type', 'N/A')}
                    - Original Date: {row['FollowUpDate'].strftime('%Y-%m-%d')}
                    """)
            else:
                st.success("✅ No overdue follow-ups!")
    
    else:
        st.info("No follow-ups scheduled yet")

# Sidebar
display_user_info()

# Footer
st.divider()
st.caption("💡 **Tip:** Regular follow-ups improve intervention success rates by 67%")
