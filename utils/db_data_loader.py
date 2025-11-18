"""
Database Data Loader for HSU Early Warning System
==================================================
Replaces CSV-based data loading with database queries
Uses caching for optimal performance

Author: Team Infinite - Group 6
Date: 2025
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add database directory to path
sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import db

# =====================================================
# CACHED DATA LOADERS
# =====================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_students():
    """Load all active students"""
    try:
        students = db.get_all_students()
        df = pd.DataFrame(students)
        
        # Add computed columns for compatibility
        if not df.empty and 'student_id' in df.columns:
            df = df.rename(columns={
                'student_id': 'StudentID',
                'banner_id': 'BannerID',
                'first_name': 'FirstName',
                'last_name': 'LastName',
                'email': 'Email',
                'phone_number': 'PhoneNumber',
                'date_of_birth': 'DateOfBirth',
                'gender': 'Gender',
                'classification': 'Classification',
                'first_generation_student': 'FirstGenerationStudent',
                'international_student': 'InternationalStudent'
            })
        
        return df
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_risk_scores():
    """Load current risk scores for all students"""
    try:
        query = """
            SELECT 
                rs.student_id as StudentID,
                rs.overall_risk_score as OverallRiskScore,
                rs.academic_risk_factor as AcademicRiskFactor,
                rs.engagement_risk_factor as EngagementRiskFactor,
                rs.financial_risk_factor as FinancialRiskFactor,
                rs.wellness_risk_factor as WellnessRiskFactor,
                rs.risk_category as RiskCategory,
                rs.risk_pathway as RiskPathway,
                rs.score_calculation_date as ScoreCalculationDate
            FROM risk_scores rs
            WHERE rs.is_current = 1
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading risk scores: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_enrollments():
    """Load course enrollments"""
    try:
        query = """
            SELECT 
                e.enrollment_id as EnrollmentID,
                e.student_id as StudentID,
                e.course_id as CourseID,
                e.term_id as TermID,
                e.enrollment_date as EnrollmentDate,
                e.withdrawal_date as WithdrawalDate,
                e.status as Status,
                e.grade as Grade,
                c.course_code as CourseCode,
                c.course_name as CourseName,
                c.credit_hours as CreditHours,
                t.term_name as TermName,
                t.year as Year
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            JOIN terms t ON e.term_id = t.term_id
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading enrollments: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_grades():
    """Load grade records"""
    try:
        query = """
            SELECT 
                g.grade_event_id as GradeEventID,
                g.enrollment_id as EnrollmentID,
                e.student_id as StudentID,
                g.assignment_type as AssignmentType,
                g.assignment_name as AssignmentName,
                g.points_earned as PointsEarned,
                g.points_possible as PointsPossible,
                g.grade_percentage as GradePercentage,
                g.submission_date as SubmissionDate,
                g.is_on_time as IsOnTime
            FROM grades g
            JOIN enrollments e ON g.enrollment_id = e.enrollment_id
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading grades: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_attendance():
    """Load attendance records"""
    try:
        query = """
            SELECT 
                a.attendance_id as AttendanceID,
                e.student_id as StudentID,
                a.enrollment_id as EnrollmentID,
                a.class_date as ClassDate,
                a.status as Status,
                a.notes as Notes
            FROM attendance a
            JOIN enrollments e ON a.enrollment_id = e.enrollment_id
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading attendance: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_logins():
    """Load LMS login records"""
    try:
        query = """
            SELECT 
                login_id as LoginID,
                student_id as StudentID,
                enrollment_id as EnrollmentID,
                login_timestamp as LoginTimestamp,
                logout_timestamp as LogoutTimestamp,
                session_duration_minutes as SessionDurationMinutes,
                activity_type as ActivityType
            FROM logins
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading logins: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_payments():
    """Load payment records"""
    try:
        query = """
            SELECT 
                payment_id as PaymentID,
                student_id as StudentID,
                term_id as TermID,
                amount_owed as AmountOwed,
                amount_paid as AmountPaid,
                balance as Balance,
                has_hold as HasHold,
                hold_reason as HoldReason,
                due_date as DueDate,
                payment_date as PaymentDate
            FROM payments
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading payments: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_counseling():
    """Load counseling visit records"""
    try:
        query = """
            SELECT 
                counseling_id as CounselingID,
                student_id as StudentID,
                visit_date as VisitDate,
                counselor_name as CounselorName,
                concern_type as ConcernType,
                severity_level as SeverityLevel,
                crisis_flag as CrisisFlag,
                notes as Notes,
                follow_up_required as FollowUpRequired,
                follow_up_date as FollowUpDate,
                status as Status
            FROM counseling
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading counseling: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_courses():
    """Load course catalog"""
    try:
        query = """
            SELECT 
                course_id as CourseID,
                course_code as CourseCode,
                course_name as CourseName,
                course_description as CourseDescription,
                credit_hours as CreditHours,
                level as Level,
                department_id as DepartmentID
            FROM courses
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading courses: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_departments():
    """Load departments"""
    try:
        query = """
            SELECT 
                department_id as DepartmentID,
                department_code as DepartmentCode,
                department_name as DepartmentName,
                college as College,
                department_head as DepartmentHead,
                contact_email as ContactEmail
            FROM departments
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading departments: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_faculty():
    """Load faculty information"""
    try:
        query = """
            SELECT 
                faculty_id as FacultyID,
                first_name as FirstName,
                last_name as LastName,
                email as Email,
                phone_number as PhoneNumber,
                title as Title,
                department_id as DepartmentID,
                office_location as OfficeLocation
            FROM faculty
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading faculty: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_terms():
    """Load academic terms"""
    try:
        query = """
            SELECT 
                term_id as TermID,
                term_code as TermCode,
                term_name as TermName,
                year as Year,
                start_date as StartDate,
                end_date as EndDate,
                midterm_date as MidtermDate,
                is_current_term as IsCurrentTerm
            FROM terms
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading terms: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_interventions():
    """Load interventions with student and advisor names"""
    try:
        query = """
            SELECT 
                i.intervention_id as InterventionID,
                i.student_id as StudentID,
                i.advisor_id as AdvisorID,
                s.first_name || ' ' || s.last_name as StudentName,
                a.first_name || ' ' || a.last_name as AdvisorName,
                i.title as Title,
                i.description as Description,
                i.priority as Priority,
                i.status as Status,
                i.scheduled_date as ScheduledDate,
                i.completed_date as CompletedDate,
                i.location as Location,
                i.method as Method,
                i.duration_minutes as DurationMinutes,
                i.outcome_assessment as OutcomeAssessment,
                i.success_rating as SuccessRating,
                i.notes as Notes,
                i.created_at as CreatedAt
            FROM interventions i
            JOIN students s ON i.student_id = s.student_id
            JOIN advisors a ON i.advisor_id = a.advisor_id
            ORDER BY i.scheduled_date DESC
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading interventions: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_intervention_types():
    """Load intervention types"""
    try:
        query = """
            SELECT 
                intervention_type_id as InterventionTypeID,
                type_name as TypeName,
                category as Category,
                description as Description,
                default_priority as DefaultPriority,
                estimated_duration_minutes as EstimatedDurationMinutes
            FROM intervention_types
            WHERE is_active = 1
        """
        
        results = db.execute_query(query)
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        st.error(f"Error loading intervention types: {e}")
        return pd.DataFrame()

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def load_all_data():
    """
    Load all datasets at once
    
    Returns:
        dict: Dictionary containing all DataFrames
    """
    data = {
        'students': load_students(),
        'risk_scores': load_risk_scores(),
        'enrollments': load_enrollments(),
        'grades': load_grades(),
        'attendance': load_attendance(),
        'logins': load_logins(),
        'payments': load_payments(),
        'counseling': load_counseling(),
        'courses': load_courses(),
        'departments': load_departments(),
        'faculty': load_faculty(),
        'terms': load_terms(),
        'interventions': load_interventions(),
        'intervention_types': load_intervention_types()
    }
    
    return data

def get_student_summary():
    """
    Get summary statistics for students
    
    Returns:
        dict: Summary statistics
    """
    students = load_students()
    risk_scores = load_risk_scores()
    
    if students.empty:
        return {
            'total_students': 0,
            'avg_gpa': 0,
            'risk_counts': {},
            'first_gen_count': 0,
            'international_count': 0
        }
    
    # Merge data
    df = students.merge(risk_scores, on='StudentID', how='left')
    
    # Calculate GPA from grades
    grades_df = load_grades()
    if not grades_df.empty:
        gpa_df = grades_df.groupby('StudentID')['GradePercentage'].mean().reset_index()
        gpa_df['CurrentGPA'] = gpa_df['GradePercentage'] / 25  # Convert to 4.0 scale
        avg_gpa = gpa_df['CurrentGPA'].mean()
    else:
        avg_gpa = 0.0
    
    # Calculate summary
    summary = {
        'total_students': len(students),
        'avg_gpa': avg_gpa,
        'risk_counts': df['RiskCategory'].value_counts().to_dict() if 'RiskCategory' in df.columns else {},
        'first_gen_count': int(students['FirstGenerationStudent'].sum()) if 'FirstGenerationStudent' in students.columns else 0,
        'international_count': int(students['InternationalStudent'].sum()) if 'InternationalStudent' in students.columns else 0
    }
    
    return summary

def get_student_by_id(student_id):
    """
    Get detailed information for a specific student
    
    Args:
        student_id: StudentID to retrieve
        
    Returns:
        dict: Student information from all tables
    """
    data = load_all_data()
    
    student_info = {
        'basic': data['students'][data['students']['StudentID'] == student_id],
        'enrollments': data['enrollments'][data['enrollments']['StudentID'] == student_id],
        'risk': data['risk_scores'][data['risk_scores']['StudentID'] == student_id],
        'logins': data['logins'][data['logins']['StudentID'] == student_id],
        'payments': data['payments'][data['payments']['StudentID'] == student_id],
        'counseling': data['counseling'][data['counseling']['StudentID'] == student_id],
        'grades': data['grades'][data['grades']['StudentID'] == student_id],
        'attendance': data['attendance'][data['attendance']['StudentID'] == student_id],
        'interventions': data['interventions'][data['interventions']['StudentID'] == student_id]
    }
    
    return student_info

def clear_cache():
    """Clear all cached data - useful for refreshing data"""
    st.cache_data.clear()
    print("🔄 Cache cleared!")

def get_student_gpa(student_id):
    """Calculate current GPA for a student from grades"""
    grades_df = load_grades()
    
    if grades_df.empty:
        return 0.0
    
    student_grades = grades_df[grades_df['StudentID'] == student_id]
    
    if student_grades.empty:
        return 0.0
    
    # Calculate GPA (convert percentage to 4.0 scale)
    avg_percentage = student_grades['GradePercentage'].mean()
    gpa = avg_percentage / 25  # Simple conversion: 100% = 4.0
    
    return round(gpa, 2)

# =====================================================
# BACKWARD COMPATIBILITY
# =====================================================

# These functions maintain compatibility with existing code
# that uses the old CSV-based data loader

def get_current_term():
    """Get current academic term"""
    terms_df = load_terms()
    if not terms_df.empty:
        current = terms_df[terms_df['IsCurrentTerm'] == 1]
        if not current.empty:
            return current.iloc[0].to_dict()
    return None
