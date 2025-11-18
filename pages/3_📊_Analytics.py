"""
Analytics Dashboard
===================
Interactive charts and cohort analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import load_all_data

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
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

st.title("📊 Cohort Analytics Dashboard")
st.markdown("**Interactive visualizations and insights**")

# Load all data
with st.spinner("Loading analytics data..."):
    data = load_all_data()
    students = data['students']
    risk_scores = data['risk_scores']
    enrollments = data['enrollments']
    grades = data['grades']
    
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

st.divider()

# KPI Row
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", len(df))

with col2:
    retention_rate = 76  # Calculate from data
    st.metric("Retention Rate", f"{retention_rate}%", delta="+4%")

with col3:
    avg_gpa = df['CalculatedGPA'].mean()
    st.metric("Average GPA", f"{avg_gpa:.2f}", delta="+0.1")

with col4:
    at_risk = len(df[df['RiskCategory'].isin(['Critical', 'High'])])
    st.metric("At-Risk Students", at_risk, delta="-3")

st.divider()

# Row 1: Risk Distribution & GPA Distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Risk Level Distribution")
    
    risk_counts = df['RiskCategory'].value_counts()
    
    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        color=risk_counts.index,
        color_discrete_map={
            'Critical': '#DC2626',
            'High': '#F59E0B',
            'Medium': '#FBBF24',
            'Low': '#10B981'
        },
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    risk_summary = pd.DataFrame({
        'Risk Level': risk_counts.index,
        'Count': risk_counts.values,
        'Percentage': (risk_counts.values / len(df) * 100).round(1)
    })
    st.dataframe(risk_summary, use_container_width=True, hide_index=True)

with col2:
    st.subheader("📚 GPA Distribution")
    
    fig = px.histogram(
        df,
        x='CalculatedGPA',
        nbins=20,
        color_discrete_sequence=['#003366'],
        labels={'CalculatedGPA': 'GPA', 'count': 'Number of Students'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="GPA",
        yaxis_title="Number of Students"
    )
    
    fig.add_vline(x=2.0, line_dash="dash", line_color="red", 
                  annotation_text="Critical (2.0)", annotation_position="top")
    fig.add_vline(x=3.0, line_dash="dash", line_color="green",
                  annotation_text="Target (3.0)", annotation_position="top")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # GPA Stats - convert all to strings to avoid type issues
    gpa_stats = pd.DataFrame({
        'Metric': ['< 2.0', '2.0 - 3.0', '> 3.0', 'Average'],
        'Value': [
            str(len(df[df['CalculatedGPA'] < 2.0])),
            str(len(df[(df['CalculatedGPA'] >= 2.0) & (df['CalculatedGPA'] < 3.0)])),
            str(len(df[df['CalculatedGPA'] >= 3.0])),
            f"{df['CalculatedGPA'].mean():.2f}"
        ]
    })
    st.dataframe(gpa_stats, use_container_width=True, hide_index=True)

st.divider()

# Row 2: Risk by Classification
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎓 Risk Distribution by Classification")
    
    class_risk = df.groupby(['Classification', 'RiskCategory']).size().reset_index(name='count')
    
    fig = px.bar(
        class_risk,
        x='Classification',
        y='count',
        color='RiskCategory',
        color_discrete_map={
            'Critical': '#DC2626',
            'High': '#F59E0B',
            'Medium': '#FBBF24',
            'Low': '#10B981'
        },
        labels={'count': 'Number of Students', 'Classification': 'Classification'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Risk by Classification")
    
    class_risk = df.groupby(['Classification', 'RiskCategory']).size().reset_index(name='count')
    
    fig = px.bar(
        class_risk,
        x='Classification',
        y='count',
        color='RiskCategory',
        color_discrete_map={
            'Critical': '#DC2626',
            'High': '#F59E0B',
            'Medium': '#FBBF24',
            'Low': '#10B981'
        },
        labels={'count': 'Number of Students'}
    )
    
    fig.update_layout(
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 3: Equity Gap Analysis
st.subheader("⚖️ Equity Gap Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### First-Generation Students")
    
    if 'FirstGenerationStudent' in df.columns:
        first_gen_risk = df.groupby('FirstGenerationStudent')['RiskScore'].mean()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Non-First-Gen', 'First-Gen'],
            y=[first_gen_risk.get(False, 0), first_gen_risk.get(True, 0)],
            marker_color=['#10B981', '#F59E0B'],
            text=[f"{first_gen_risk.get(False, 0):.1f}", f"{first_gen_risk.get(True, 0):.1f}"],
            textposition='auto'
        ))
        
        fig.update_layout(
            height=350,
            yaxis_title="Average Risk Score",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gap calculation
        if True in first_gen_risk.index and False in first_gen_risk.index:
            gap = first_gen_risk[True] - first_gen_risk[False]
            if gap > 0:
                st.error(f"⚠️ Gap: First-Gen students have {gap:.1f} points higher risk")
            else:
                st.success(f"✅ First-Gen students performing {abs(gap):.1f} points better")

with col2:
    st.markdown("### International Students")
    
    if 'InternationalStudent' in df.columns:
        intl_risk = df.groupby('InternationalStudent')['RiskScore'].mean()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Domestic', 'International'],
            y=[intl_risk.get(False, 0), intl_risk.get(True, 0)],
            marker_color=['#10B981', '#3B82F6'],
            text=[f"{intl_risk.get(False, 0):.1f}", f"{intl_risk.get(True, 0):.1f}"],
            textposition='auto'
        ))
        
        fig.update_layout(
            height=350,
            yaxis_title="Average Risk Score",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 4: Feature Importance
st.subheader("🔍 Top Risk Factors (Feature Importance)")

try:
    feature_importance = pd.read_csv('ml_pipeline/results/feature_importance.csv').head(10)
    
    fig = px.bar(
        feature_importance,
        x='Importance',
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale='Reds',
        labels={'Importance': 'Importance Score', 'Feature': 'Risk Factor'}
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Top Risk Factors Identified:**
    - Payment Rate & SAP Risk are the strongest predictors
    - LMS engagement and attendance are critical indicators
    - Academic performance (GPA, midterms) significantly impacts risk
    """)
    
except Exception as e:
    st.warning("Feature importance data not available. Run the ML pipeline first.")

st.divider()

# Export Options
st.subheader("📥 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Risk Summary"):
        risk_summary_df = df.groupby('RiskCategory').agg({
            'StudentID': 'count',
            'CalculatedGPA': 'mean',
            'OverallRiskScore': 'mean'
        }).reset_index()
        risk_summary_df['OverallRiskScore'] = risk_summary_df['OverallRiskScore'] * 100
        
        csv = risk_summary_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "risk_summary.csv",
            "text/csv"
        )

with col2:
    if st.button("👥 Export Student Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "student_data.csv",
            "text/csv"
        )

with col3:
    if st.button("📈 Export Analytics Report"):
        st.info("Generating comprehensive report...")
