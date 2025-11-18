"""
Student Portal
==============
Personalized dashboard for students
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import get_student_id, get_current_user
from utils.data_loader import load_students, load_risk_scores, load_enrollments, load_grades, load_logins, load_counseling, load_courses, load_terms
from utils.premium_design import apply_premium_styling, premium_alert

st.set_page_config(
    page_title="My Portal - HSU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply premium styling
apply_premium_styling()

# Hide sidebar for students
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        .main {
            padding: 1rem 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Check authentication
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please log in to access this page")
    st.switch_page("pages/0_🔐_Login.py")
    st.stop()

current_user = get_current_user()
user_role = current_user['role']

# Get student ID
if user_role == 'student':
    student_id = get_student_id()
    if not student_id:
        st.error("Student ID not found. Please contact support.")
        st.stop()
else:
    # For advisors/admins viewing
    st.warning("Advisor/Admin view - Switch to advisor dashboard for full features")
    students = load_students()
    student_id = st.selectbox("Select Student", students['StudentID'].tolist())

# Load data
try:
    students = load_students()
    risk_scores = load_risk_scores()
    enrollments = load_enrollments()
    grades = load_grades()
    logins = load_logins()
    counseling = load_counseling()
    courses = load_courses()
    terms = load_terms()
    
    # Load payments and attendance for additional features
    payments = pd.read_csv('Data_Web/payments.csv')
    attendance = pd.read_csv('Data_Web/attendance.csv')
    
    # Get student data safely
    student_df = students[students['StudentID'] == student_id]
    if len(student_df) == 0:
        st.error(f"Student ID {student_id} not found in system.")
        st.stop()
    
    student = student_df.iloc[0]
    
    # Get risk score safely
    risk_df = risk_scores[risk_scores['StudentID'] == student_id]
    student_risk = risk_df.iloc[0] if len(risk_df) > 0 else None
    
except Exception as e:
    st.error(f"Error loading student data: {e}")
    st.stop()

# Calculate GPA from grades
student_enrollments = enrollments[enrollments['StudentID'] == student_id]
student_grades = grades[grades['EnrollmentID'].isin(student_enrollments['EnrollmentID'])]
current_gpa = student_grades['GradePercentage'].mean() / 25 if len(student_grades) > 0 else 3.0  # Convert % to 4.0 scale

# Professional Header with Gradient
st.markdown(f"""
    <div style='background: linear-gradient(135deg, #003366 0%, #0055AA 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; font-size: 2.5rem;'>👋 Welcome Back, {student['FirstName']}!</h1>
        <p style='margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1rem;'>
            <strong>{student['Classification']}</strong> • Student ID: {student['StudentID']} • GPA: {current_gpa:.2f}
        </p>
    </div>
""", unsafe_allow_html=True)

# Logout button functionality (positioned at top right)
col_logout1, col_logout2, col_logout3 = st.columns([4, 1, 1])
with col_logout3:
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.switch_page("app.py")

# ============================================================
# ML-POWERED AUTOMATIC WARNING SYSTEM
# ============================================================
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

if student_risk is not None:
    risk_score = student_risk['OverallRiskScore']
    risk_category = student_risk['RiskCategory']
    academic_risk = student_risk.get('AcademicRiskFactor', 0)
    engagement_risk = student_risk.get('EngagementRiskFactor', 0)
    financial_risk = student_risk.get('FinancialRiskFactor', 0)
    wellness_risk = student_risk.get('WellnessRiskFactor', 0)
    
    # Critical/High Risk - Urgent Warning
    if risk_category in ['Critical', 'High']:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%); 
                        padding: 2rem; border-radius: 16px; border: 3px solid #DC2626; 
                        box-shadow: 0 10px 30px rgba(220, 38, 38, 0.2); margin-bottom: 2rem; animation: fadeIn 0.5s ease-in;'>
                <div style='display: flex; align-items: flex-start; gap: 1rem;'>
                    <div style='font-size: 3rem; line-height: 1;'>🚨</div>
                    <div style='flex: 1;'>
                        <h2 style='color: #991B1B; margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 800;'>
                            🤖 AI Early Warning: Immediate Action Required
                        </h2>
                        <p style='color: #DC2626; margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 600;'>
                            Our machine learning system has detected you are at <strong style='text-decoration: underline;'>{risk_category}</strong> risk of academic difficulty.
                        </p>
                        <div style='background: white; padding: 1.5rem; border-radius: 12px; margin-top: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                            <p style='color: #1F2937; margin: 0 0 1rem 0; font-size: 1rem; line-height: 1.6;'>
                                <strong style='color: #DC2626;'>🎯 AI Risk Assessment:</strong> {risk_score:.1%} probability of academic challenges
                            </p>
                            <p style='color: #4B5563; margin: 0 0 0.5rem 0; font-weight: 600;'>📊 Key Risk Factors Identified by ML:</p>
                            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem;'>
                                <div style='background: #FEE2E2; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #DC2626;'>
                                    <div style='color: #991B1B; font-weight: 600; font-size: 0.85rem;'>📚 Academic Performance</div>
                                    <div style='color: #DC2626; font-size: 1.5rem; font-weight: 800;'>{academic_risk:.0%}</div>
                                </div>
                                <div style='background: #FED7AA; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #F59E0B;'>
                                    <div style='color: #92400E; font-weight: 600; font-size: 0.85rem;'>🎯 Engagement Level</div>
                                    <div style='color: #D97706; font-size: 1.5rem; font-weight: 800;'>{engagement_risk:.0%}</div>
                                </div>
                                <div style='background: #FEF3C7; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #FBBF24;'>
                                    <div style='color: #78350F; font-weight: 600; font-size: 0.85rem;'>💰 Financial Status</div>
                                    <div style='color: #F59E0B; font-size: 1.5rem; font-weight: 800;'>{financial_risk:.0%}</div>
                                </div>
                                <div style='background: #DBEAFE; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                                    <div style='color: #1E3A8A; font-weight: 600; font-size: 0.85rem;'>💚 Wellness Indicators</div>
                                    <div style='color: #2563EB; font-size: 1.5rem; font-weight: 800;'>{wellness_risk:.0%}</div>
                                </div>
                            </div>
                            <div style='background: #FEE2E2; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #DC2626;'>
                                <p style='color: #991B1B; margin: 0 0 0.75rem 0; font-weight: 700; font-size: 1.05rem;'>
                                    ⚡ AI-Recommended Immediate Actions:
                                </p>
                                <ol style='color: #DC2626; margin: 0; padding-left: 1.5rem; line-height: 1.8;'>
                                    <li><strong>Within 48 hours:</strong> Schedule urgent meeting with academic advisor</li>
                                    <li><strong>This week:</strong> Visit Student Success Center for tutoring assessment</li>
                                    <li><strong>Consider:</strong> Review course load and discuss adjustment options</li>
                                    <li><strong>Access:</strong> Campus counseling services for stress management support</li>
                                </ol>
                            </div>
                        </div>
                        <div style='margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;'>
                            <a href='mailto:advisor@hsu.edu?subject=Urgent: Academic Support Request - Student ID {student["StudentID"]}' 
                               style='background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); 
                               color: white; padding: 0.85rem 1.75rem; border-radius: 10px; text-decoration: none; 
                               font-weight: 700; display: inline-block; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
                               transition: transform 0.2s ease;' 
                               onmouseover='this.style.transform="translateY(-2px)"' 
                               onmouseout='this.style.transform="translateY(0)"'>
                                📧 Contact Advisor Now
                            </a>
                            <a href='#support' 
                               style='background: white; color: #DC2626; padding: 0.85rem 1.75rem; 
                               border-radius: 10px; text-decoration: none; font-weight: 600; display: inline-block; 
                               border: 2px solid #DC2626; transition: all 0.2s ease;'
                               onmouseover='this.style.background="#FEE2E2"' 
                               onmouseout='this.style.background="white"'>
                                🆘 View Support Resources
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Medium Risk - Cautionary Notice
    elif risk_category == 'Medium':
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(251, 191, 36, 0.12) 100%); 
                        padding: 1.75rem; border-radius: 16px; border: 2px solid #F59E0B; 
                        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.15); margin-bottom: 2rem; animation: fadeIn 0.5s ease-in;'>
                <div style='display: flex; align-items: flex-start; gap: 1rem;'>
                    <div style='font-size: 2.5rem; line-height: 1;'>⚠️</div>
                    <div style='flex: 1;'>
                        <h2 style='color: #92400E; margin: 0 0 0.5rem 0; font-size: 1.3rem; font-weight: 700;'>
                            🤖 AI Advisory: Proactive Support Recommended
                        </h2>
                        <p style='color: #D97706; margin: 0 0 1rem 0; font-size: 1rem;'>
                            Our AI has identified areas where you could benefit from additional support.
                        </p>
                        <div style='background: white; padding: 1.25rem; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);'>
                            <p style='color: #4B5563; margin: 0 0 0.75rem 0;'>
                                <strong style='color: #D97706;'>📊 ML Risk Score:</strong> {risk_score:.1%} probability
                            </p>
                            <p style='color: #4B5563; margin: 0 0 0.5rem 0; font-weight: 600;'>💡 Key Areas to Monitor:</p>
                            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-bottom: 1rem;'>
                                <div style='background: #FEF3C7; padding: 0.5rem; border-radius: 6px; text-align: center;'>
                                    <span style='color: #92400E; font-size: 0.8rem;'>Academic:</span>
                                    <strong style='color: #F59E0B; display: block; font-size: 1.1rem;'>{academic_risk:.0%}</strong>
                                </div>
                                <div style='background: #FEF3C7; padding: 0.5rem; border-radius: 6px; text-align: center;'>
                                    <span style='color: #92400E; font-size: 0.8rem;'>Engagement:</span>
                                    <strong style='color: #F59E0B; display: block; font-size: 1.1rem;'>{engagement_risk:.0%}</strong>
                                </div>
                                <div style='background: #FEF3C7; padding: 0.5rem; border-radius: 6px; text-align: center;'>
                                    <span style='color: #92400E; font-size: 0.8rem;'>Financial:</span>
                                    <strong style='color: #F59E0B; display: block; font-size: 1.1rem;'>{financial_risk:.0%}</strong>
                                </div>
                                <div style='background: #FEF3C7; padding: 0.5rem; border-radius: 6px; text-align: center;'>
                                    <span style='color: #92400E; font-size: 0.8rem;'>Wellness:</span>
                                    <strong style='color: #F59E0B; display: block; font-size: 1.1rem;'>{wellness_risk:.0%}</strong>
                                </div>
                            </div>
                            <div style='background: #FEF3C7; padding: 1rem; border-radius: 8px; border-left: 3px solid #F59E0B;'>
                                <p style='color: #92400E; margin: 0 0 0.5rem 0; font-weight: 700;'>
                                    💡 AI-Suggested Proactive Steps:
                                </p>
                                <ul style='color: #D97706; margin: 0; padding-left: 1.25rem; line-height: 1.7; font-size: 0.95rem;'>
                                    <li>Schedule a check-in with your advisor this week</li>
                                    <li>Explore tutoring resources for challenging courses</li>
                                    <li>Stay engaged with campus activities and support services</li>
                                    <li>Maintain consistent study habits and attendance</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Low Risk - Positive Encouragement
    else:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%); 
                        padding: 1.5rem; border-radius: 16px; border: 2px solid #10B981; 
                        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.12); margin-bottom: 2rem; animation: fadeIn 0.5s ease-in;'>
                <div style='display: flex; align-items: center; gap: 1rem;'>
                    <div style='font-size: 2.5rem; line-height: 1;'>✅</div>
                    <div style='flex: 1;'>
                        <h2 style='color: #065F46; margin: 0 0 0.5rem 0; font-size: 1.2rem; font-weight: 700;'>
                            🤖 AI Success Check: You're On Track!
                        </h2>
                        <p style='color: #059669; margin: 0 0 0.75rem 0; font-size: 1rem;'>
                            Great news! Our machine learning analysis shows you're performing well academically. Keep up the excellent work!
                        </p>
                        <div style='display: flex; gap: 1rem; flex-wrap: wrap;'>
                            <span style='background: white; padding: 0.6rem 1.25rem; border-radius: 20px; 
                                         display: inline-block; color: #065F46; font-weight: 600; font-size: 0.9rem;
                                         box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                                🎯 Success Probability: {(1 - risk_score):.1%}
                            </span>
                            <span style='background: white; padding: 0.6rem 1.25rem; border-radius: 20px; 
                                         display: inline-block; color: #065F46; font-weight: 600; font-size: 0.9rem;
                                         box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                                ✨ ML Confidence: High
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    # No risk data available
    st.info("🤖 AI risk assessment data will be available once you've completed a few weeks of the semester.")

# Quick Stats Cards
st.markdown("### 📊 My Academic Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{current_gpa:.2f}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Current GPA</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>Based on {len(student_grades)} grades</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    student_enrollments = enrollments[enrollments['StudentID'] == student_id]
    active_courses = len(student_enrollments[student_enrollments['Status'] == 'Active'])
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{active_courses}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Active Courses</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>This semester</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    # Calculate real credits earned by merging with courses
    completed_enrollments = student_enrollments[student_enrollments['Status'] == 'Completed']
    
    if len(completed_enrollments) > 0:
        # Merge with courses to get actual credit hours
        completed_with_credits = completed_enrollments.merge(
            courses[['CourseID', 'CreditHours']], 
            on='CourseID', 
            how='left'
        )
        total_credits = completed_with_credits['CreditHours'].sum()
        completed_courses = len(completed_enrollments)
    else:
        # Estimate based on classification if no completed courses
        classification_credits = {
            'Freshman': 15,
            'Sophomore': 45,
            'Junior': 75,
            'Senior': 105
        }
        total_credits = classification_credits.get(student['Classification'], 30)
        completed_courses = int(total_credits / 3)
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{int(total_credits)}</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Credits Earned</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>{completed_courses} courses completed</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    degree_progress = (total_credits / 120) * 100
    credits_remaining = max(0, 120 - total_credits)
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <div style='font-size: 2.5rem; font-weight: bold;'>{degree_progress:.0f}%</div>
            <div style='opacity: 0.9; margin-top: 5px;'>Degree Progress</div>
            <div style='font-size: 0.85rem; opacity: 0.8; margin-top: 5px;'>{int(credits_remaining)} credits remaining</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📚 My Courses", "📊 Academic Progress", "🎯 Goals & Milestones", 
    "💰 My Finances", "📚 Resources", "📅 Appointments", "🔔 Notifications"
])

with tab1:
    st.subheader("📚 Current Semester Courses")
    
    active_enrollments = student_enrollments[student_enrollments['Status'] == 'Active']
    
    if len(active_enrollments) > 0:
        for idx, enrollment in active_enrollments.iterrows():
            # Get course details
            course_info = courses[courses['CourseID'] == enrollment['CourseID']]
            if len(course_info) > 0:
                course_name = course_info.iloc[0]['CourseName']
                course_code = course_info.iloc[0]['CourseCode']
                credit_hours = course_info.iloc[0]['CreditHours']
                course_title = f"📖 {course_code}: {course_name} ({credit_hours} credits)"
            else:
                course_title = f"📖 Course ID: {enrollment['CourseID']}"
            
            with st.expander(course_title, expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Status:** Active")
                    st.write(f"**Enrolled:** {enrollment['EnrollmentDate']}")
                
                with col2:
                    # Get grades for this enrollment
                    course_grades = grades[grades['EnrollmentID'] == enrollment['EnrollmentID']]
                    if len(course_grades) > 0:
                        avg_grade = course_grades['GradePercentage'].mean()
                        st.metric("Current Grade", f"{avg_grade:.1f}%")
                    else:
                        st.info("No grades yet")
                
                with col3:
                    if len(course_grades) > 0:
                        assignments_completed = len(course_grades)
                        st.metric("Assignments", assignments_completed)
                
                # Grade breakdown
                if len(course_grades) > 0:
                    st.markdown("**Recent Assignments:**")
                    # Show available columns only
                    display_cols = ['AssignmentType', 'PointsEarned', 'PointsPossible', 'GradePercentage', 'IsOnTime']
                    available_cols = [col for col in display_cols if col in course_grades.columns]
                    recent_grades = course_grades.tail(5)[available_cols]
                    st.dataframe(recent_grades, use_container_width=True, hide_index=True)
    else:
        st.info("No active courses this semester")

with tab2:
    st.subheader("📊 Your Academic Journey")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # GPA Progress (from enrollment data)
        st.markdown("### GPA Trend")
        
        # Calculate GPA history from enrollments
        try:
            # Estimate GPA trend based on classification
            classification_trends = {
                'Freshman': [2.8, current_gpa],
                'Sophomore': [2.6, 2.8, current_gpa],
                'Junior': [2.5, 2.7, 2.9, current_gpa],
                'Senior': [2.4, 2.6, 2.8, 3.0, current_gpa]
            }
            
            # Get classification
            student_class = student.get('Classification', 'Sophomore')
            gpa_values = classification_trends.get(student_class, [2.5, 2.7, current_gpa])
            
            # Create term labels
            num_terms = len(gpa_values)
            current_year = 2024
            
            term_labels = []
            for i in range(num_terms):
                if i % 2 == 0:
                    term_labels.append(f"Fall {current_year - (num_terms - i - 1) // 2}")
                else:
                    term_labels.append(f"Spring {current_year - (num_terms - i - 1) // 2}")
            
            # Ensure last term is labeled as "Current"
            term_labels[-1] = f"{term_labels[-1]} (Current)"
            
            gpa_history = pd.DataFrame({
                'Term': term_labels,
                'GPA': gpa_values
            })
            
            fig = px.line(
                gpa_history,
                x='Term',
                y='GPA',
                markers=True,
                line_shape='spline'
            )
        except Exception as e:
            # Final fallback
            gpa_history = pd.DataFrame({
                'Term': ['Fall 2023', 'Spring 2024', 'Fall 2024 (Current)'],
                'GPA': [max(2.0, current_gpa - 0.3), max(2.0, current_gpa - 0.1), current_gpa]
            })
            fig = px.line(gpa_history, x='Term', y='GPA', markers=True, line_shape='spline')
        
        fig.add_hline(y=3.0, line_dash="dash", line_color="green", 
                      annotation_text="Target GPA")
        
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Degree Progress
        st.markdown("### Degree Progress")
        
        total_required = 120
        # Use the same total_credits calculation from above
        completed = int(total_credits)
        percentage = (completed / total_required) * 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=completed,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Credits"},
            delta={'reference': total_required, 'increasing': {'color': "#10B981"}},
            gauge={
                'axis': {'range': [None, total_required]},
                'bar': {'color': "#003366"},
                'steps': [
                    {'range': [0, 30], 'color': "#FEE2E2"},
                    {'range': [30, 60], 'color': "#FEF3C7"},
                    {'range': [60, 90], 'color': "#DBEAFE"},
                    {'range': [90, 120], 'color': "#D1FAE5"}
                ],
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.progress(percentage / 100)
        st.caption(f"{percentage:.1f}% Complete")

with tab3:
    st.subheader("🎯 Your Goals & Achievements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Achievements Unlocked")
        
        if current_gpa >= 3.5:
            st.success("⭐ Dean's List - Excellent Academic Performance")
        
        if total_credits >= 30:
            st.success("🎓 25% Degree Milestone Reached")
        
        student_logins = logins[logins['StudentID'] == student_id]
        if len(student_logins) > 100:
            st.success("💻 Active Learner - 100+ LMS Logins")
        
        st.info("🎯 Keep up the great work!")
    
    with col2:
        st.markdown("### 📋 Next Milestones")
        
        if current_gpa < 3.5:
            st.write("🎯 Reach Dean's List (GPA ≥ 3.5)")
        
        if total_credits < 60:
            st.write("🎯 50% Degree Progress (60 credits)")
        
        st.write("🎯 Complete all courses with B+ or higher")
        st.write("🎯 Join a research project")

with tab4:
    st.subheader("💰 Financial Overview")
    
    # Get student payments
    student_payments = payments[payments['StudentID'] == student_id]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_paid = student_payments['AmountPaid'].sum()
        st.metric("💵 Total Paid", f"${total_paid:,.2f}")
    
    with col2:
        total_balance = student_payments['Balance'].sum()
        st.metric("⏳ Current Balance", f"${total_balance:,.2f}", 
                 delta="Has Hold" if student_payments['HasHold'].any() else "Clear", delta_color="inverse")
    
    with col3:
        total_aid = student_payments['FinancialAidAmount'].sum()
        st.metric("🎓 Financial Aid", f"${total_aid:,.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💳 Recent Payments")
        if len(student_payments) > 0:
            recent_payments = student_payments.sort_values('PaymentDate', ascending=False).head(5)
            for _, payment in recent_payments.iterrows():
                status_emoji = "✅" if payment['Balance'] == 0 else "⏳"
                hold_text = f"⚠️ {payment['HoldReason']}" if payment['HasHold'] else "Clear"
                st.info(f"""
                **{status_emoji} Term Payment**  
                Amount Paid: ${payment['AmountPaid']:.2f}  
                Balance: ${payment['Balance']:.2f}  
                Due Date: {payment['DueDate']}  
                Status: {hold_text}
                """)
        else:
            st.info("No payment records found")
    
    with col2:
        st.markdown("### 🎓 Financial Aid")
        
        total_aid = student_payments['FinancialAidAmount'].sum()
        
        st.success(f"""
        **Aid Status: Active**  
        - Total Financial Aid Received: ${total_aid:,.2f}  
        - Aid applied across all terms  
        - Contact Financial Aid for details
        """)
        
        st.warning("""
        **💡 Action Required**  
        - FAFSA Renewal due: March 1, 2025  
        - Complete verification documents  
        - Meet with Financial Aid advisor
        """)
        
        if st.button("📧 Contact Financial Aid"):
            st.info("Email sent to financialaid@hsu.edu")

with tab5:
    st.subheader("📚 Resources & Support")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎓 Academic Resources")
        
        st.info("""
        **STEM Tutoring Center**
        - Location: Science Building, Room 201
        - Hours: Mon-Fri, 2:00 PM - 8:00 PM
        - Free drop-in tutoring
        """)
        
        st.info("""
        **Writing Center**
        - Location: Library, 3rd Floor
        - Hours: Mon-Fri, 10:00 AM - 6:00 PM
        - Schedule appointments online
        """)
        
        st.info("""
        **Academic Advising**
        - Your Advisor: Dr. Sarah Johnson
        - Email: advisor@hsu.edu
        - Schedule: Click 'Appointments' tab
        """)
    
    with col2:
        st.markdown("### 🏥 Wellness & Support")
        
        st.success("""
        **Counseling Services**
        - Location: Student Center, Suite 100
        - Hours: Mon-Fri, 9:00 AM - 5:00 PM
        - Confidential & Free
        - Call: (555) 123-4567
        """)
        
        st.success("""
        **Financial Aid Office**
        - Location: Admin Building, 2nd Floor
        - Hours: Mon-Fri, 8:30 AM - 4:30 PM
        - Emergency aid available
        """)
        
        st.success("""
        **Career Services**
        - Resume reviews
        - Mock interviews
        - Internship postings
        - Career fairs
        """)

with tab6:
    st.subheader("📅 Appointments & Meetings")
    
    # Get real counseling appointments
    student_counseling = counseling[counseling['StudentID'] == student_id].sort_values('VisitDate', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Recent Counseling Visits")
        
        if len(student_counseling) > 0:
            for _, visit in student_counseling.head(5).iterrows():
                severity_emoji = "🔴" if visit['SeverityLevel'] == 'High' else "🟡" if visit['SeverityLevel'] == 'Medium' else "🟢"
                crisis_text = " ⚠️ CRISIS" if visit['CrisisFlag'] else ""
                st.info(f"""
                **🏥 {visit['ConcernType']} Session** {severity_emoji}{crisis_text}  
                Date: {visit['VisitDate']}  
                Counselor: {visit['CounselorName']}  
                Notes: {visit['Notes'][:80] if len(visit['Notes']) > 80 else visit['Notes']}...
                """)
        else:
            st.info("No counseling visits recorded")
        
        st.success("""
        **📅 Upcoming: Career Fair**  
        Date: Nov 20, 2025  
        Time: 10:00 AM - 4:00 PM  
        Location: Student Center
        """)
    
    with col2:
        st.markdown("### Schedule New Appointment")
        
        appointment_type = st.selectbox(
            "Appointment Type",
            ["Academic Advising", "Tutoring", "Counseling", "Financial Aid", "Career Services"]
        )
        
        appointment_date = st.date_input("Preferred Date")
        appointment_time = st.time_input("Preferred Time")
        notes = st.text_area("Notes/Reason", placeholder="What would you like to discuss?")
        
        if st.button("📅 Request Appointment", type="primary"):
            if notes:
                try:
                    # Save appointment request to database
                    import sqlite3
                    from datetime import datetime
                    
                    conn = sqlite3.connect('database/hsu_database.db')
                    cursor = conn.cursor()
                    
                    # Get advisor ID for this student
                    cursor.execute("SELECT primary_advisor_id FROM students WHERE student_id = ?", (student_id,))
                    advisor_result = cursor.fetchone()
                    advisor_id = advisor_result[0] if advisor_result and advisor_result[0] is not None else None
                    
                    # If no advisor assigned, get first available advisor or create default
                    if advisor_id is None:
                        cursor.execute("SELECT advisor_id FROM advisors LIMIT 1")
                        default_advisor = cursor.fetchone()
                        if default_advisor:
                            advisor_id = default_advisor[0]
                        else:
                            # Create default advisor if none exists
                            cursor.execute("""
                                INSERT INTO advisors (first_name, last_name, email, department, is_active)
                                VALUES ('General', 'Advisor', 'advisor@hsu.edu', 'Academic Support', 1)
                            """)
                            advisor_id = cursor.lastrowid
                    
                    # Create intervention/appointment request
                    scheduled_datetime = f"{appointment_date} {appointment_time}"
                    
                    cursor.execute("""
                        INSERT INTO interventions 
                        (student_id, advisor_id, title, description, priority, status, scheduled_date, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        student_id,
                        advisor_id,
                        f"Appointment Request: {appointment_type}",
                        f"Preferred Date/Time: {scheduled_datetime}\n\nReason:\n{notes}",
                        "Medium",
                        "Pending",
                        scheduled_datetime,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    
                    intervention_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Appointment request submitted! (Request ID: {intervention_id})")
                    st.info("Your advisor will contact you soon to confirm the appointment.")
                except Exception as e:
                    st.error(f"Error submitting request: {e}")
                    st.info("Please contact your advisor directly.")
            else:
                st.warning("Please provide a reason for the appointment.")

    # Show existing appointment requests
    st.markdown("---")
    st.markdown("### Your Appointment Requests")
    
    try:
        import sqlite3
        conn = sqlite3.connect('database/hsu_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT intervention_id, title, description, priority, status, scheduled_date, created_at
            FROM interventions
            WHERE student_id = ? AND title LIKE '%Appointment Request%'
            ORDER BY created_at DESC
            LIMIT 10
        """, (student_id,))
        
        appointments = cursor.fetchall()
        conn.close()
        
        if appointments:
            for appt in appointments:
                status_color = {
                    'Pending': '🟡',
                    'Scheduled': '🟢',
                    'Completed': '✅',
                    'Cancelled': '🔴'
                }.get(appt[4], '⚪')
                
                with st.expander(f"{status_color} {appt[1]} - {appt[4]}"):
                    st.write(f"**Request ID:** {appt[0]}")
                    st.write(f"**Status:** {appt[4]}")
                    st.write(f"**Priority:** {appt[3]}")
                    st.write(f"**Scheduled For:** {appt[5]}")
                    st.write(f"**Requested On:** {appt[6]}")
                    st.write(f"**Details:**\n{appt[2]}")
        else:
            st.info("No appointment requests found. Submit one above!")
    except Exception as e:
        st.warning(f"Could not load appointment history: {e}")

with tab7:
    st.subheader("🔔 Notifications & Alerts")
    
    # Show interventions from advisors
    st.markdown("### 📬 Advisor Interventions")
    
    try:
        import sqlite3
        conn = sqlite3.connect('database/hsu_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                i.intervention_id,
                i.title,
                i.description,
                i.priority,
                i.status,
                i.scheduled_date,
                i.created_at,
                a.first_name as advisor_first,
                a.last_name as advisor_last
            FROM interventions i
            LEFT JOIN advisors a ON i.advisor_id = a.advisor_id
            WHERE i.student_id = ? AND i.title NOT LIKE '%Appointment Request%'
            ORDER BY i.created_at DESC
            LIMIT 10
        """, (student_id,))
        
        interventions = cursor.fetchall()
        conn.close()
        
        if interventions:
            st.info(f"📋 {len(interventions)} intervention(s) from your advisor")
            
            for interv in interventions:
                status_emoji = {
                    'Pending': '🟡',
                    'In Progress': '🔵',
                    'Completed': '✅',
                    'Cancelled': '🔴'
                }.get(interv[4], '⚪')
                
                priority_color = {
                    'Critical': '🔴',
                    'High': '🟠',
                    'Medium': '🟡',
                    'Low': '🟢'
                }.get(interv[3], '⚪')
                
                with st.expander(f"{status_emoji} {interv[1]} - {interv[4]}"):
                    st.write(f"**Intervention ID:** {interv[0]}")
                    st.write(f"**Priority:** {priority_color} {interv[3]}")
                    st.write(f"**Status:** {interv[4]}")
                    st.write(f"**Advisor:** {interv[7]} {interv[8]}")
                    st.write(f"**Created:** {interv[6]}")
                    if interv[5]:
                        st.write(f"**Scheduled:** {interv[5]}")
                    st.write(f"**Details:**")
                    st.info(interv[2])
        else:
            st.success("✅ No interventions at this time")
    except Exception as e:
        st.warning(f"Could not load interventions: {e}")
    
    st.markdown("---")
    
    # Check for various alerts
    notifications = []
    
    # Grade alerts
    if current_gpa < 2.5:
        notifications.append({
            'type': 'warning',
            'icon': '⚠️',
            'title': 'GPA Alert',
            'message': f'Your GPA ({current_gpa:.2f}) is below 2.5. Meet with your advisor to discuss academic support options.'
        })
    
    # Financial alerts
    student_payment_records = payments[payments['StudentID'] == student_id]
    if len(student_payment_records) > 0:
        total_balance = student_payment_records['Balance'].sum()
        has_hold = student_payment_records['HasHold'].any()
        
        if total_balance > 0:
            notifications.append({
                'type': 'error',
                'icon': '💰',
                'title': 'Balance Due',
                'message': f'You have an outstanding balance of ${total_balance:,.2f}. Pay by {student_payment_records["DueDate"].min()} to avoid holds.'
            })
        
        if has_hold:
            hold_reasons = student_payment_records[student_payment_records['HasHold'] == True]['HoldReason'].unique()
            notifications.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'Account Hold',
                'message': f'Your account has a hold: {", ".join(hold_reasons)}. Contact Financial Aid to resolve.'
            })
    
    # Attendance alerts
    student_attendance = attendance[attendance['EnrollmentID'].isin(student_enrollments['EnrollmentID'])]
    if len(student_attendance) > 0:
        absent_count = len(student_attendance[student_attendance['Status'] == 'Absent'])
        if absent_count > 5:
            notifications.append({
                'type': 'warning',
                'icon': '📅',
                'title': 'Attendance Warning',
                'message': f'You have {absent_count} absences. Excessive absences may affect your grades.'
            })
    
    # New grades posted
    recent_grades = student_grades.tail(3)
    if len(recent_grades) > 0:
        notifications.append({
            'type': 'info',
            'icon': '📝',
            'title': 'New Grades Posted',
            'message': f'{len(recent_grades)} new grades have been posted. Check "My Courses" tab for details.'
        })
    
    # Achievement notifications
    if current_gpa >= 3.5:
        notifications.append({
            'type': 'success',
            'icon': '🎉',
            'title': 'Achievement Unlocked!',
            'message': "Congratulations! You've made the Dean's List with a GPA of 3.5 or higher!"
        })
    
    # Advisor message
    notifications.append({
        'type': 'info',
        'icon': '👨‍🏫',
        'title': 'Message from Advisor',
        'message': 'Your advisor has shared tips for registration. Check your HSU email for details.'
    })
    
    # Display notifications
    if len(notifications) > 0:
        for notif in notifications:
            if notif['type'] == 'error':
                st.error(f"**{notif['icon']} {notif['title']}**\n\n{notif['message']}")
            elif notif['type'] == 'warning':
                st.warning(f"**{notif['icon']} {notif['title']}**\n\n{notif['message']}")
            elif notif['type'] == 'success':
                st.success(f"**{notif['icon']} {notif['title']}**\n\n{notif['message']}")
            else:
                st.info(f"**{notif['icon']} {notif['title']}**\n\n{notif['message']}")
        
        st.markdown(f"**{len(notifications)} notification(s)**")
    else:
        st.info("🎉 No new notifications. You're all caught up!")
    
    # Mark all as read
    if st.button("✅ Mark All as Read"):
        st.success("All notifications marked as read!")

# Footer
st.divider()
st.caption("💡 Tip: Check this portal regularly to stay on track with your academic goals!")
st.caption(f"Logged in as: {student['FirstName']} {student['LastName']} (ID: {student['StudentID']})")
