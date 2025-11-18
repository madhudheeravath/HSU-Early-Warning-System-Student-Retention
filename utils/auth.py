"""
Authentication System for HSU Early Warning System
==================================================
Role-based authentication with session management

Roles:
- Student: View own data only
- Advisor: Access student data, log interventions
- Admin: Full access to all features
"""

import streamlit as st
import hashlib
import pandas as pd
import sqlite3
from datetime import datetime
from utils.data_loader import load_students

DEMO_USERS = {
    # Advisors
    'advisor@hsu.edu': {
        'password': hashlib.sha256('advisor123'.encode()).hexdigest(),
        'role': 'advisor',
        'name': 'Dr. Sarah Johnson',
        'department': 'Academic Advising'
    },
    'advisor2@hsu.edu': {
        'password': hashlib.sha256('advisor123'.encode()).hexdigest(),
        'role': 'advisor',
        'name': 'Dr. Michael Chen',
        'department': 'STEM Advising'
    },
    
    # Admin
    'admin@hsu.edu': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'name': 'Dean Patricia Martinez',
        'department': 'Student Affairs'
    },
    
    # Students (using actual StudentIDs from data)
    'student1@hsu.edu': {
        'password': hashlib.sha256('student123'.encode()).hexdigest(),
        'role': 'student',
        'name': 'Amy Phillips',
        'student_id': 9457
    },
    'student2@hsu.edu': {
        'password': hashlib.sha256('student123'.encode()).hexdigest(),
        'role': 'student',
        'name': 'Student User 2',
        'student_id': 8868
    },
    'student3@hsu.edu': {
        'password': hashlib.sha256('student123'.encode()).hexdigest(),
        'role': 'student',
        'name': 'Student User 3',
        'student_id': 9360
    }
}

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_student_user_from_email(email):
    """
    Get student user info from CSV data
    This allows all students in the CSV to login with password: password123
    """
    students = load_students()
    if students.empty or 'Email' not in students.columns:
        return None
    email_norm = email.lower().strip()
    matches = students[students['Email'].str.lower() == email_norm]
    if matches.empty:
        return None
    row = matches.iloc[0]
    name = f"{row['FirstName']} {row['LastName']}"
    return {
        'password': hash_password('password123'),
        'role': 'student',
        'name': name,
        'student_id': int(row['StudentID']),
        'first_name': row['FirstName'],
        'last_name': row['LastName'],
        'email': email_norm
    }

def register_user(first_name, last_name, email, password, role, student_id=None, department=None):
    """
    Register a new user in the database
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email: User's email (will be lowercased)
        password: Plain text password (will be hashed)
        role: User role (student, advisor, admin)
        student_id: Student ID (optional, for students)
        department: Department (optional, for advisors/admins)
    
    Returns:
        dict: Success status and message
    """
    try:
        email = email.lower().strip()
        hashed_password = hash_password(password)
        
        conn = sqlite3.connect('database/hsu_database.db')
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "message": "Email already registered"}
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash, role, is_active, is_verified, created_at)
            VALUES (?, ?, ?, ?, ?, 1, 1, ?)
        """, (first_name, last_name, email, hashed_password, role.lower(), datetime.now()))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "message": "Account created successfully!",
            "user_id": user_id
        }
    
    except Exception as e:
        return {"success": False, "message": f"Registration error: {str(e)}"}

def authenticate_user(email, password):
    """
    Authenticate user credentials - checks database first, then demo users
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        dict: User info if authenticated, None otherwise
    """
    email = email.lower().strip()
    hashed_password = hash_password(password)
    
    # First, check database for registered users
    try:
        conn = sqlite3.connect('database/hsu_database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, password_hash, role, is_active
            FROM users
            WHERE email = ? AND is_active = 1
        """, (email,))
        
        user_row = cursor.fetchone()
        
        if user_row:
            user_id, first_name, last_name, db_email, db_password_hash, role, is_active = user_row
            
            if db_password_hash == hashed_password:
                # Update last login
                cursor.execute("UPDATE users SET last_login = ? WHERE user_id = ?", 
                             (datetime.now(), user_id))
                conn.commit()
                
                # For students, try to get student_id from CSV data
                student_id = None
                if role == 'student':
                    try:
                        students = load_students()
                        student_match = students[students['Email'].str.lower() == db_email.lower()]
                        if not student_match.empty:
                            student_id = int(student_match.iloc[0]['StudentID'])
                    except Exception as e:
                        print(f"Could not load student_id: {e}")
                
                conn.close()
                
                result = {
                    'user_id': user_id,
                    'email': db_email,
                    'role': role,
                    'name': f"{first_name} {last_name}",
                    'first_name': first_name,
                    'last_name': last_name
                }
                
                # Add student_id if found
                if student_id:
                    result['student_id'] = student_id
                
                return result
        
        conn.close()
    
    except Exception as e:
        print(f"Database authentication error: {e}")
    
    # Fallback to demo users
    if email in DEMO_USERS:
        if DEMO_USERS[email]['password'] == hashed_password:
            return DEMO_USERS[email]
    
    # Fallback to student email lookup from CSV
    student_user = get_student_user_from_email(email)
    if student_user and hashed_password == student_user['password']:
        # Add additional fields for consistency
        student_user['email'] = email
        return student_user
    
    return None

def login():
    """
    Display login form and handle authentication
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # Check if already logged in
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        return True
    
    # Display login form
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 HSU Login")
        st.markdown("---")
        
        email = st.text_input("📧 Email", placeholder="yourname@hsu.edu", key="login_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_password")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            login_button = st.button("🚀 Sign In", type="primary", use_container_width=True)
        
        with col_b:
            demo_button = st.button("👁️ Demo Login", use_container_width=True)
        
        if login_button:
            if email and password:
                user = authenticate_user(email, password)
                
                if user:
                    # Set session state
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.session_state["email"] = email
                    st.session_state["role"] = user['role']
                    st.session_state["name"] = user['name']
                    
                    st.success(f"✅ Welcome, {user['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.warning("⚠️ Please enter both email and password")
        
        if demo_button:
            st.info("""
            **Demo Credentials:**
            
            **👨‍🏫 Advisor:**
            - Email: advisor@hsu.edu
            - Password: advisor123
            
            **👔 Admin:**
            - Email: admin@hsu.edu
            - Password: admin123
            
            **🎓 Student:**
            - Email: student1@hsu.edu
            - Password: student123
            """)
        
        st.markdown("---")
        st.caption("© 2025 HSU Early Warning System | Team Infinite")
    
    return False

def logout():
    """Logout current user and clear session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("✅ Logged out successfully!")
    st.rerun()

def require_authentication():
    """
    Require authentication to access page
    Call this at the top of each protected page
    
    Returns:
        bool: True if authenticated
    """
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.warning("🔒 Please log in to access this page")
        login()
        st.stop()
        return False
    return True

def require_role(allowed_roles):
    """
    Require specific role(s) to access page
    
    Args:
        allowed_roles: List of allowed roles or single role string
    """
    require_authentication()
    
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    user_role = st.session_state.get("role", "")
    
    if user_role not in allowed_roles:
        st.error(f"🚫 Access Denied: This page requires {', '.join(allowed_roles)} role")
        st.info(f"Your role: {user_role}")
        st.stop()

def get_current_user():
    """
    Get current logged-in user info
    
    Returns:
        dict: User information or None
    """
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        return st.session_state.get("user", None)
    return None

def get_user_role():
    """Get current user's role"""
    return st.session_state.get("role", None)

def is_student():
    """Check if current user is a student"""
    return get_user_role() == "student"

def is_advisor():
    """Check if current user is an advisor"""
    return get_user_role() == "advisor"

def is_admin():
    """Check if current user is an admin"""
    return get_user_role() == "admin"

def get_student_id():
    """Get student ID for student users"""
    user = get_current_user()
    if user and user.get('role') == 'student':
        return user.get('student_id')
    return None

def display_user_info():
    """Display current user info in sidebar"""
    user = get_current_user()
    
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Profile")
        st.sidebar.write(f"**Name:** {user['name']}")
        st.sidebar.write(f"**Role:** {user['role'].title()}")
        
        if user['role'] in ['advisor', 'admin']:
            st.sidebar.write(f"**Dept:** {user.get('department', 'N/A')}")
        
        if user['role'] == 'student':
            st.sidebar.write(f"**Student ID:** {user.get('student_id', 'N/A')}")
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
