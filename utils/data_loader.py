"""
Data Loader for HSU Early Warning System
=========================================
Loads and caches all CSV data files with optimized performance

Uses Streamlit's @st.cache_data decorator for automatic caching
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import os

# Base data directory
DATA_DIR = Path("Data_Web")

@st.cache_data
def load_students():
    """Load student demographic and academic data"""
    try:
        df = pd.read_csv(DATA_DIR / "students.csv")
        print(f"✅ Loaded {len(df)} students")
        return df
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return pd.DataFrame()

@st.cache_data
def load_enrollments():
    """Load course enrollment records"""
    try:
        df = pd.read_csv(DATA_DIR / "enrollments.csv")
        print(f"✅ Loaded {len(df)} enrollments")
        return df
    except Exception as e:
        st.error(f"Error loading enrollments: {e}")
        return pd.DataFrame()

@st.cache_data
def load_grades():
    """Load grade records"""
    try:
        df = pd.read_csv(DATA_DIR / "grades.csv")
        print(f"✅ Loaded {len(df)} grade records")
        return df
    except Exception as e:
        st.error(f"Error loading grades: {e}")
        return pd.DataFrame()

@st.cache_data
def load_attendance():
    """Load attendance records"""
    try:
        df = pd.read_csv(DATA_DIR / "attendance.csv")
        print(f"✅ Loaded {len(df)} attendance records")
        return df
    except Exception as e:
        st.error(f"Error loading attendance: {e}")
        return pd.DataFrame()

@st.cache_data
def load_logins():
    """Load LMS login records"""
    try:
        df = pd.read_csv(DATA_DIR / "logins.csv")
        print(f"✅ Loaded {len(df)} login records")
        return df
    except Exception as e:
        st.error(f"Error loading logins: {e}")
        return pd.DataFrame()

@st.cache_data
def load_payments():
    """Load payment transaction records"""
    try:
        df = pd.read_csv(DATA_DIR / "payments.csv")
        print(f"✅ Loaded {len(df)} payment records")
        return df
    except Exception as e:
        st.error(f"Error loading payments: {e}")
        return pd.DataFrame()

@st.cache_data
def load_counseling():
    """Load counseling visit records"""
    try:
        df = pd.read_csv(DATA_DIR / "counseling.csv")
        print(f"✅ Loaded {len(df)} counseling records")
        return df
    except Exception as e:
        st.error(f"Error loading counseling: {e}")
        return pd.DataFrame()

@st.cache_data
def load_risk_scores():
    """Load risk score assessments"""
    try:
        df = pd.read_csv(DATA_DIR / "risk_scores.csv")
        print(f"✅ Loaded {len(df)} risk scores")
        return df
    except Exception as e:
        st.error(f"Error loading risk scores: {e}")
        return pd.DataFrame()

@st.cache_data
def load_courses():
    """Load course catalog"""
    try:
        df = pd.read_csv(DATA_DIR / "courses.csv")
        print(f"✅ Loaded {len(df)} courses")
        return df
    except Exception as e:
        st.error(f"Error loading courses: {e}")
        return pd.DataFrame()

@st.cache_data
def load_departments():
    """Load department information"""
    try:
        df = pd.read_csv(DATA_DIR / "departments.csv")
        print(f"✅ Loaded {len(df)} departments")
        return df
    except Exception as e:
        st.error(f"Error loading departments: {e}")
        return pd.DataFrame()

@st.cache_data
def load_faculty():
    """Load faculty information"""
    try:
        df = pd.read_csv(DATA_DIR / "faculty.csv")
        print(f"✅ Loaded {len(df)} faculty members")
        return df
    except Exception as e:
        st.error(f"Error loading faculty: {e}")
        return pd.DataFrame()

@st.cache_data
def load_terms():
    """Load academic term information"""
    try:
        df = pd.read_csv(DATA_DIR / "terms.csv")
        print(f"✅ Loaded {len(df)} terms")
        return df
    except Exception as e:
        st.error(f"Error loading terms: {e}")
        return pd.DataFrame()

@st.cache_data
def load_all_data():
    """
    Load all datasets at once
    
    Returns:
        dict: Dictionary containing all DataFrames
    """
    print("Loading all datasets...")
    
    data = {
        'students': load_students(),
        'enrollments': load_enrollments(),
        'grades': load_grades(),
        'attendance': load_attendance(),
        'logins': load_logins(),
        'payments': load_payments(),
        'counseling': load_counseling(),
        'risk_scores': load_risk_scores(),
        'courses': load_courses(),
        'departments': load_departments(),
        'faculty': load_faculty(),
        'terms': load_terms()
    }
    
    print("✅ All data loaded successfully!")
    return data

@st.cache_data
def get_student_summary():
    """
    Get summary statistics for students
    
    Returns:
        dict: Summary statistics
    """
    students = load_students()
    risk_scores = load_risk_scores()
    
    # Merge data
    df = students.merge(risk_scores, on='StudentID', how='left')
    
    # Calculate summary
    summary = {
        'total_students': len(students),
        'avg_gpa': df['CurrentGPA'].mean(),
        'risk_counts': df['RiskCategory'].value_counts().to_dict() if 'RiskCategory' in df.columns else {},
        'first_gen_count': students['FirstGenerationStudent'].sum() if 'FirstGenerationStudent' in students.columns else 0,
        'international_count': students['InternationalStudent'].sum() if 'InternationalStudent' in students.columns else 0
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
        'counseling': data['counseling'][data['counseling']['StudentID'] == student_id]
    }
    
    return student_info

def clear_cache():
    """Clear all cached data - useful for refreshing data"""
    st.cache_data.clear()
    print("🔄 Cache cleared!")
