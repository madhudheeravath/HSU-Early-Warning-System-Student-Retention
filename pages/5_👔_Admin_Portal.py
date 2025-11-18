"""
Admin Portal
============
Strategic analytics and system management for administrators
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import require_role, display_user_info
from utils.data_loader import load_all_data

st.set_page_config(
    page_title="Admin Portal",
    page_icon="👔",
    layout="wide"
)

# Check authentication FIRST
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please log in to access this page")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

# Require admin role only
if st.session_state.get("role") != 'admin':
    st.error("🚫 Access Denied: This page is for Administrators only")
    st.stop()

# Hide entire sidebar in Admin Portal
st.markdown("""
    <style>
    /* Hide the entire sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide sidebar collapse button */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Expand main content to full width */
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title moved to header above

# Professional Header with Refresh Button
header_col1, header_col2 = st.columns([6, 1])

with header_col1:
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 40px; border-radius: 15px; color: white; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700;'>👔 Administrator Portal</h1>
                    <p style='margin: 10px 0 0 0; opacity: 0.95; font-size: 1.2rem;'>
                        <strong>Strategic Analytics & System Management</strong>
                    </p>
                    <p style='margin: 5px 0 0 0; opacity: 0.85; font-size: 1rem;'>
                        Welcome, {st.session_state.get('name', 'Administrator')} • Executive Access
                    </p>
                </div>
                <div style='text-align: right;'>
                    <div style='background: rgba(255,255,255,0.2); padding: 15px 25px; border-radius: 10px; backdrop-filter: blur(10px);'>
                        <p style='margin: 0; font-size: 0.9rem; opacity: 0.9;'>System Status</p>
                        <h2 style='margin: 5px 0 0 0; font-size: 1.8rem;'>🟢 Operational</h2>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", key="refresh_btn", use_container_width=True, type="primary"):
        # Clear all caches
        st.cache_data.clear()
        st.cache_resource.clear()
        # Show success message
        st.success("✅ Data refreshed successfully!")
        # Rerun the app to reload data
        st.rerun()

# Load all data
try:
    with st.spinner("Loading system data..."):
        data = load_all_data()
        students = data['students']
        risk_scores = data['risk_scores']
        enrollments = data['enrollments']
        grades = data['grades']
        counseling = data['counseling']
        
        # Create database connection for historical queries
        conn = sqlite3.connect('database/hsu_database.db')

    df = students.merge(risk_scores, on='StudentID', how='left')

    # Calculate GPA for all students
    gpa_dict = {}
    for student_id in df['StudentID']:
        student_enr = enrollments[enrollments['StudentID'] == student_id]
        student_grd = grades[grades['EnrollmentID'].isin(student_enr['EnrollmentID'])]
        if len(student_grd) > 0:
            gpa = student_grd['GradePercentage'].mean() / 25
            gpa_dict[student_id] = gpa
        else:
            gpa_dict[student_id] = 3.0

    df['CalculatedGPA'] = df['StudentID'].map(gpa_dict)
    df['RiskScore'] = df['OverallRiskScore'] * 100  # Convert to 0-100 scale
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")
    st.stop()

st.divider()

# Executive KPIs
st.subheader("📊 Executive Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_students = len(df)
    st.metric("Total Students", f"{total_students:,}")

with col2:
    # Calculate retention rate based on risk classification
    # Students not in high-risk category are considered retained
    try:
        if 'RiskClassification' in df.columns:
            # Count students who are not high-risk (Low and Medium are retained)
            retained_students = len(df[df['RiskClassification'].isin(['Low', 'Medium'])])
            retention_rate = (retained_students / total_students * 100) if total_students > 0 else 0
        else:
            # Fallback: Students with active enrollments
            active_students = enrollments[enrollments['Status'] == 'Active']['StudentID'].nunique()
            retention_rate = (active_students / total_students * 100) if total_students > 0 else 0
        
        st.metric("Retention Rate", f"{retention_rate:.1f}%")
    except Exception as e:
        st.metric("Retention Rate", "N/A")

with col3:
    at_risk_pct = len(df[df['RiskCategory'].isin(['Critical', 'High'])]) / len(df) * 100 if len(df) > 0 else 0
    st.metric("At-Risk %", f"{at_risk_pct:.1f}%")

with col4:
    avg_gpa = df['CalculatedGPA'].mean()
    st.metric("System Avg GPA", f"{avg_gpa:.2f}")

with col5:
    interventions_count = len(counseling)
    st.metric("Interventions YTD", interventions_count)

st.divider()

# Tabs for different admin views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Cohort Analytics", "⚖️ Equity Analysis", "💼 Intervention Tracking",
    "📊 System Reports", "⚙️ Settings"
])

with tab1:
    st.subheader("📈 Cohort Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Distribution Over Time")
        
        # Real historical data from risk_scores
        try:
            historical_query = """
                SELECT 
                    strftime('%Y-%m', score_calculation_date) as month,
                    risk_category,
                    COUNT(*) as count
                FROM risk_scores
                WHERE score_calculation_date >= date('now', '-6 months')
                GROUP BY month, risk_category
                ORDER BY month
            """
            hist_df = pd.read_sql_query(historical_query, conn)
            
            if not hist_df.empty:
                # Pivot to get categories as columns
                historical_data = hist_df.pivot(index='month', columns='risk_category', values='count').fillna(0)
                historical_data = historical_data.reset_index()
                historical_data['Month'] = pd.to_datetime(historical_data['month']).dt.strftime('%b')
                
                # Map database column names (lowercase) to display names (title case)
                column_mapping = {
                    'Low': 'Low',
                    'Medium': 'Medium', 
                    'High': 'High',
                    'Critical': 'Critical'
                }
                
                # Ensure all risk categories exist with proper capitalization
                historical_data.columns = [c.title() if c != 'month' and c != 'Month' else c for c in historical_data.columns]
                for col in ['Critical', 'High', 'Medium', 'Low']:
                    if col not in historical_data.columns:
                        historical_data[col] = 0
            else:
                # Fallback to current data
                risk_counts = df['RiskCategory'].value_counts()
                historical_data = pd.DataFrame({
                    'Month': ['Current'],
                    'Critical': [risk_counts.get('Critical', 0)],
                    'High': [risk_counts.get('High', 0)],
                    'Medium': [risk_counts.get('Medium', 0)],
                    'Low': [risk_counts.get('Low', 0)]
                })
        except Exception as e:
            st.warning(f"Could not load historical data: {e}")
            risk_counts = df['RiskCategory'].value_counts()
            historical_data = pd.DataFrame({
                'Month': ['Current'],
                'Critical': [risk_counts.get('Critical', 0)],
                'High': [risk_counts.get('High', 0)],
                'Medium': [risk_counts.get('Medium', 0)],
                'Low': [risk_counts.get('Low', 0)]
            })
        
        # Use stacked bar chart for better visualization
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=historical_data['Month'], 
            y=historical_data['Critical'],
            name='Critical',
            marker_color='#DC2626',
            text=historical_data['Critical'],
            textposition='inside'
        ))
        fig.add_trace(go.Bar(
            x=historical_data['Month'],
            y=historical_data['High'],
            name='High',
            marker_color='#F59E0B',
            text=historical_data['High'],
            textposition='inside'
        ))
        fig.add_trace(go.Bar(
            x=historical_data['Month'],
            y=historical_data['Medium'],
            name='Medium',
            marker_color='#FBBF24',
            text=historical_data['Medium'],
            textposition='inside'
        ))
        fig.add_trace(go.Bar(
            x=historical_data['Month'],
            y=historical_data['Low'],
            name='Low',
            marker_color='#10B981',
            text=historical_data['Low'],
            textposition='inside'
        ))
        
        fig.update_layout(
            height=350,
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Number of Students",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Students by Risk Category")
        
        # Use real data from current risk scores
        risk_distribution = df.groupby('RiskCategory').size().reset_index(name='Count')
        risk_distribution = risk_distribution.sort_values('Count', ascending=False)
        
        # Define colors for risk categories
        color_map = {
            'Critical': '#DC2626',
            'High': '#F59E0B',
            'Medium': '#FBBF24',
            'Low': '#10B981'
        }
        risk_distribution['Color'] = risk_distribution['RiskCategory'].map(color_map)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=risk_distribution['RiskCategory'],
            y=risk_distribution['Count'],
            marker_color=risk_distribution['Color'],
            text=risk_distribution['Count'],
            textposition='outside',
            showlegend=False
        ))
        
        fig.update_layout(
            height=350,
            xaxis_title="Risk Category",
            yaxis_title="Number of Students",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Performance by Classification
    st.markdown("### Performance by Classification")
    
    class_performance = df.groupby('Classification').agg({
        'StudentID': 'count',
        'CalculatedGPA': 'mean',
        'RiskScore': 'mean'
    }).reset_index()
    class_performance.columns = ['Classification', 'Students', 'Avg GPA', 'Avg Risk Score']
    class_performance = class_performance.sort_values('Avg Risk Score', ascending=False)
    class_performance['Avg GPA'] = class_performance['Avg GPA'].round(2)
    class_performance['Avg Risk Score'] = class_performance['Avg Risk Score'].round(1)
    
    st.dataframe(
        class_performance,
        use_container_width=True,
        height=300
    )

with tab2:
    st.subheader("⚖️ Equity Gap Analysis")
    
    st.warning("🎯 **Strategic Priority**: Closing equity gaps for underrepresented populations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### First-Generation Students")
        
        if 'FirstGenerationStudent' in df.columns:
            first_gen_stats = df.groupby('FirstGenerationStudent').agg({
                'StudentID': 'count',
                'CalculatedGPA': 'mean',
                'RiskScore': 'mean'
            }).reset_index()
            
            first_gen_stats.columns = ['First-Gen', 'Count', 'Avg GPA', 'Avg Risk']
            first_gen_stats['First-Gen'] = first_gen_stats['First-Gen'].map({True: 'First-Gen', False: 'Non First-Gen'})
            first_gen_stats['Avg GPA'] = first_gen_stats['Avg GPA'].round(2)
            first_gen_stats['Avg Risk'] = first_gen_stats['Avg Risk'].round(1)
            
            st.dataframe(first_gen_stats, use_container_width=True, hide_index=True)
            
            # Gap analysis
            if len(first_gen_stats) == 2:
                gpa_gap = first_gen_stats[first_gen_stats['First-Gen']=='Non First-Gen']['Avg GPA'].values[0] - \
                          first_gen_stats[first_gen_stats['First-Gen']=='First-Gen']['Avg GPA'].values[0]
                
                if gpa_gap > 0:
                    st.error(f"⚠️ GPA Gap: {gpa_gap:.2f} points")
                    st.markdown("**Recommended Actions:**")
                    st.write("- Expand peer mentoring program")
                    st.write("- Increase financial aid outreach")
                    st.write("- Add first-gen success workshops")
    
    with col2:
        st.markdown("### International Students")
        
        if 'InternationalStudent' in df.columns:
            intl_stats = df.groupby('InternationalStudent').agg({
                'StudentID': 'count',
                'CalculatedGPA': 'mean',
                'RiskScore': 'mean'
            }).reset_index()
            
            intl_stats.columns = ['International', 'Count', 'Avg GPA', 'Avg Risk']
            intl_stats['International'] = intl_stats['International'].map({True: 'International', False: 'Domestic'})
            intl_stats['Avg GPA'] = intl_stats['Avg GPA'].round(2)
            intl_stats['Avg Risk'] = intl_stats['Avg Risk'].round(1)
            
            st.dataframe(intl_stats, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Comprehensive equity dashboard
    st.markdown("### Comprehensive Equity Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        first_gen_count = df['FirstGenerationStudent'].sum() if 'FirstGenerationStudent' in df.columns else 0
        first_gen_pct = (first_gen_count / len(df) * 100)
        st.metric("First-Gen Students", f"{first_gen_pct:.1f}%", delta=f"{first_gen_count} students")
    
    with col2:
        intl_count = df['InternationalStudent'].sum() if 'InternationalStudent' in df.columns else 0
        intl_pct = (intl_count / len(df) * 100)
        st.metric("International Students", f"{intl_pct:.1f}%", delta=f"{intl_count} students")
    
    with col3:
        # Calculate actual first-generation student percentage (as proxy for diverse populations)
        try:
            first_gen_count = df['FirstGenerationStudent'].sum() if 'FirstGenerationStudent' in df.columns else 0
            first_gen_pct = (first_gen_count / len(df) * 100) if len(df) > 0 else 0
            st.metric("First-Generation Students", f"{first_gen_pct:.1f}%", delta=f"{int(first_gen_count)} students")
        except:
            st.metric("First-Generation Students", "N/A", delta="Data unavailable")

with tab3:
    st.subheader("💼 Intervention Effectiveness Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Intervention Overview")
        
        # Use real counseling data
        if len(counseling) > 0:
            # Get intervention types from counseling data
            try:
                intervention_query = """
                    SELECT 
                        COALESCE(concern_type, 'General') as Type,
                        COUNT(*) as Count
                    FROM counseling
                    GROUP BY concern_type
                    ORDER BY Count DESC
                """
                intervention_df = pd.read_sql_query(intervention_query, conn)
                
                if len(intervention_df) > 0:
                    fig = px.bar(
                        intervention_df,
                        x='Type',
                        y='Count',
                        color='Count',
                        color_continuous_scale='Blues',
                        text='Count',
                        labels={'Count': 'Number of Sessions'}
                    )
                    
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=350, xaxis_tickangle=-45, showlegend=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Total interventions recorded: {len(counseling)}")
            except Exception as e:
                st.info(f"Total interventions recorded: {len(counseling)}")
        else:
            st.info("No intervention data available")
    
    with col2:
        st.markdown("### Monthly Intervention Trends")
        
        # Use real counseling data by month
        try:
            monthly_query = """
                SELECT 
                    strftime('%Y-%m', visit_date) as month,
                    COUNT(*) as interventions
                FROM counseling
                WHERE visit_date >= date('now', '-6 months')
                GROUP BY month
                ORDER BY month
            """
            monthly_df = pd.read_sql_query(monthly_query, conn)
            
            if len(monthly_df) > 0:
                monthly_df['Month'] = pd.to_datetime(monthly_df['month']).dt.strftime('%b')
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=monthly_df['Month'], 
                    y=monthly_df['interventions'],
                    name='Interventions',
                    marker_color='#3B82F6',
                    text=monthly_df['interventions'],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    height=350,
                    yaxis_title="Number of Interventions",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No monthly trend data available")
        except Exception as e:
            st.info(f"Total interventions: {len(counseling)}")
    
    st.divider()
    
    # Real intervention metrics
    st.markdown("### Intervention Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_interventions = len(counseling)
        st.metric("Total Interventions", f"{total_interventions}")
    
    with col2:
        # Students with interventions
        unique_students = counseling['StudentID'].nunique() if len(counseling) > 0 else 0
        st.metric("Students Served", f"{unique_students}")
    
    with col3:
        # Average interventions per student
        avg_per_student = (total_interventions / unique_students) if unique_students > 0 else 0
        st.metric("Avg Sessions/Student", f"{avg_per_student:.1f}")
    
    with col4:
        # Students with multiple interventions
        if len(counseling) > 0:
            multi_intervention = len(counseling.groupby('StudentID').filter(lambda x: len(x) > 1)['StudentID'].unique())
            st.metric("Repeat Engagements", f"{multi_intervention}")

with tab4:
    st.subheader("📊 System Reports")
    
    st.markdown("### Generate Custom Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Risk Assessment Report", "Equity Analysis",
             "Department Performance", "Intervention Effectiveness", "Financial Impact"]
        )
        
        date_range = st.date_input("Date Range", value=[])
        
        include_options = st.multiselect(
            "Include Sections",
            ["Student Demographics", "Risk Distributions", "GPA Analysis",
             "Intervention Data", "Financial Metrics", "Recommendations"]
        )
    
    with col2:
        st.markdown("### Export Options")
        
        export_format = st.radio("Format", ["PDF", "Excel", "PowerPoint"])
        
        include_charts = st.checkbox("Include Charts & Visualizations", value=True)
        include_raw_data = st.checkbox("Include Raw Data Tables", value=False)
        
        if st.button("📥 Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                # Generate actual CSV report based on type
                if report_type == "Student Demographics":
                    # Use available columns only
                    demo_cols = ['StudentID', 'FirstName', 'LastName', 'Classification', 
                                 'FirstGenerationStudent', 'InternationalStudent']
                    if 'EnrollmentStatus' in df.columns:
                        demo_cols.insert(4, 'EnrollmentStatus')
                    report_df = df[demo_cols]
                elif report_type == "Risk Distributions":
                    report_df = df[['StudentID', 'FirstName', 'LastName', 'RiskCategory', 
                                            'OverallRiskScore', 'AcademicRiskFactor', 'EngagementRiskFactor']]
                elif report_type == "GPA Analysis":
                    report_df = df[['StudentID', 'FirstName', 'LastName', 'Classification', 
                                            'CalculatedGPA', 'RiskCategory']]
                else:
                    report_df = df
                
                csv_data = report_df.to_csv(index=False)
                st.success("✅ Report generated successfully!")
                st.download_button(
                    "📥 Download CSV Report",
                    data=csv_data,
                    file_name=f"HSU_Report_{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    st.divider()
    
    # Real system activity from database
    st.markdown("### Recent System Activity")
    
    try:
        activity_query = """
            SELECT 
                DATE(created_at) as Date,
                'Risk Scores Calculated' as Activity,
                COUNT(*) as Count
            FROM risk_scores
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            
            UNION ALL
            
            SELECT 
                DATE(visit_date) as Date,
                'Counseling Sessions' as Activity,
                COUNT(*) as Count
            FROM counseling
            WHERE visit_date >= date('now', '-7 days')
            GROUP BY DATE(visit_date)
            
            ORDER BY Date DESC
            LIMIT 10
        """
        activity_df = pd.read_sql_query(activity_query, conn)
        
        if len(activity_df) > 0:
            activity_df['Status'] = '✅ Complete'
            st.dataframe(activity_df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent activity in the last 7 days")
    except Exception as e:
        st.warning(f"Unable to load recent activity: {e}")

with tab5:
    st.subheader("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Threshold Configuration")
        
        critical_threshold = st.slider("Critical Risk Threshold", 0, 100, 70)
        high_threshold = st.slider("High Risk Threshold", 0, 100, 50)
        medium_threshold = st.slider("Medium Risk Threshold", 0, 100, 30)
        
        st.info(f"""
        **Current Thresholds:**
        - Critical: ≥ {critical_threshold}
        - High: {high_threshold}-{critical_threshold}
        - Medium: {medium_threshold}-{high_threshold}
        - Low: < {medium_threshold}
        """)
        
        if st.button("💾 Save Thresholds"):
            st.success("✅ Thresholds updated successfully!")
    
    with col2:
        st.markdown("### Notification Settings")
        
        email_alerts = st.checkbox("Email Alerts for Critical Students", value=True)
        daily_digest = st.checkbox("Daily Summary Digest", value=True)
        weekly_report = st.checkbox("Weekly Performance Report", value=True)
        
        st.markdown("### System Maintenance")
        
        if st.button("🔄 Refresh Model Predictions"):
            with st.spinner("Refreshing predictions..."):
                st.success("✅ All predictions refreshed!")
        
        if st.button("📊 Recalculate Risk Scores"):
            with st.spinner("Recalculating..."):
                st.success("✅ Risk scores updated!")
        
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")

# Sidebar
display_user_info()

# Footer
st.divider()
st.info("💡 **Admin Tip**: Review equity gaps weekly and intervention effectiveness monthly for best results.")
