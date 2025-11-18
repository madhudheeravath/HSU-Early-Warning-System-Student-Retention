"""
Database-Backed Authentication System for HSU Early Warning System
===================================================================
Secure authentication with database storage, session management, and user registration

Author: Team Infinite - Group 6
Date: 2025
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

# Add database directory to path
sys.path.append(str(Path(__file__).parent.parent))
from database.db_manager import db

# =====================================================
# AUTHENTICATION FUNCTIONS
# =====================================================

def authenticate_user(email, password):
    """
    Authenticate user credentials against database
    
    Args:
        email: User email
        password: Plain text password (will be hashed)
        
    Returns:
        dict: User info if authenticated, None otherwise
    """
    user = db.authenticate_user(email, password)
    
    if user:
        # Get additional info based on role
        if user['role'] == 'student':
            student = db.execute_query(
                "SELECT student_id, banner_id FROM students WHERE user_id = ?", 
                [user['user_id']]
            )
            if student:
                user['student_id'] = student[0]['student_id']
                user['banner_id'] = student[0]['banner_id']
        
        elif user['role'] == 'advisor':
            advisor = db.execute_query(
                "SELECT advisor_id, department, office_location FROM advisors WHERE user_id = ?",
                [user['user_id']]
            )
            if advisor:
                user['advisor_id'] = advisor[0]['advisor_id']
                user['department'] = advisor[0]['department']
                user['office_location'] = advisor[0]['office_location']
        
        return user
    
    return None

def register_user(email, password, role, first_name, last_name, **kwargs):
    """
    Register a new user account
    
    Args:
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        role: User role (student, advisor, admin)
        first_name: First name
        last_name: Last name
        **kwargs: Additional fields based on role
        
    Returns:
        tuple: (success: bool, message: str, user_id: int)
    """
    # Validate email format
    if not validate_email(email):
        return False, "Invalid email format", None
    
    # Validate password strength
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, msg, None
    
    # Check if email already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return False, "Email already registered", None
    
    try:
        # Create user account
        user_id = db.create_user(
            email=email,
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name,
            phone_number=kwargs.get('phone_number'),
            is_verified=kwargs.get('is_verified', 0)
        )
        
        # Create role-specific record
        if role == 'student':
            # Generate banner ID
            banner_id = f"A{1000000 + user_id}"
            
            student_id = db.create_student(
                user_id=user_id,
                banner_id=banner_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=kwargs.get('phone_number'),
                date_of_birth=kwargs.get('date_of_birth', '2000-01-01'),
                gender=kwargs.get('gender'),
                classification=kwargs.get('classification', 'Freshman'),
                first_generation_student=kwargs.get('first_generation_student', 0),
                international_student=kwargs.get('international_student', 0)
            )
            
            # Log action
            db.log_action(user_id, 'USER_REGISTERED', 'students', student_id)
            
            return True, "Student account created successfully!", user_id
        
        elif role == 'advisor':
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO advisors (
                        user_id, first_name, last_name, email, phone_number,
                        department, office_location
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    first_name,
                    last_name,
                    email,
                    kwargs.get('phone_number'),
                    kwargs.get('department', 'Academic Advising'),
                    kwargs.get('office_location')
                ))
                advisor_id = cursor.lastrowid
            
            # Log action
            db.log_action(user_id, 'USER_REGISTERED', 'advisors', advisor_id)
            
            return True, "Advisor account created successfully!", user_id
        
        elif role == 'admin':
            # Admin users don't need additional records
            db.log_action(user_id, 'USER_REGISTERED', 'users', user_id)
            return True, "Admin account created successfully!", user_id
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}", None

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
                    st.session_state["user_id"] = user['user_id']
                    st.session_state["email"] = email
                    st.session_state["role"] = user['role']
                    st.session_state["name"] = f"{user['first_name']} {user['last_name']}"
                    st.session_state["first_name"] = user['first_name']
                    st.session_state["last_name"] = user['last_name']
                    
                    # Role-specific session data
                    if user['role'] == 'student':
                        st.session_state["student_id"] = user.get('student_id')
                    elif user['role'] == 'advisor':
                        st.session_state["advisor_id"] = user.get('advisor_id')
                    
                    st.success(f"✅ Welcome, {user['first_name']}!")
                    
                    # Log action
                    db.log_action(user['user_id'], 'USER_LOGIN')
                    
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
        
        # Link to sign up
        if st.button("✨ Don't have an account? Sign Up", use_container_width=True):
            st.switch_page("pages/0_✨_SignUp.py")
        
        st.caption("© 2025 HSU Early Warning System | Team Infinite")
    
    return False

def logout():
    """Logout current user and clear session"""
    if "user_id" in st.session_state:
        db.log_action(st.session_state["user_id"], 'USER_LOGOUT')
    
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

# =====================================================
# USER INFORMATION
# =====================================================

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
    if is_student():
        return st.session_state.get('student_id')
    return None

def get_advisor_id():
    """Get advisor ID for advisor users"""
    if is_advisor():
        return st.session_state.get('advisor_id')
    return None

def get_user_id():
    """Get current user's ID"""
    return st.session_state.get('user_id')

def display_user_info():
    """Display current user info in sidebar"""
    user = get_current_user()
    
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Profile")
        st.sidebar.write(f"**Name:** {user['first_name']} {user['last_name']}")
        st.sidebar.write(f"**Role:** {user['role'].title()}")
        st.sidebar.write(f"**Email:** {user['email']}")
        
        if user['role'] == 'advisor':
            st.sidebar.write(f"**Dept:** {user.get('department', 'N/A')}")
            st.sidebar.write(f"**Office:** {user.get('office_location', 'N/A')}")
        
        if user['role'] == 'student':
            st.sidebar.write(f"**Student ID:** {user.get('student_id', 'N/A')}")
            st.sidebar.write(f"**Banner ID:** {user.get('banner_id', 'N/A')}")
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()

# =====================================================
# VALIDATION FUNCTIONS
# =====================================================

def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

# =====================================================
# PASSWORD RESET
# =====================================================

def request_password_reset(email):
    """
    Request password reset for email
    
    Args:
        email: User email
        
    Returns:
        tuple: (success: bool, message: str)
    """
    user = db.get_user_by_email(email)
    
    if not user:
        # Don't reveal if email exists for security
        return True, "If the email exists, you will receive a reset link"
    
    # In production, send email with reset token
    # For now, just log the action
    db.log_action(user['user_id'], 'PASSWORD_RESET_REQUESTED')
    
    return True, "Password reset instructions sent to your email"

def reset_password(user_id, new_password):
    """
    Reset user password
    
    Args:
        user_id: User ID
        new_password: New password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    is_valid, msg = validate_password(new_password)
    if not is_valid:
        return False, msg
    
    try:
        db.update_password(user_id, new_password)
        db.log_action(user_id, 'PASSWORD_RESET')
        return True, "Password updated successfully"
    except Exception as e:
        return False, f"Password reset failed: {str(e)}"

# =====================================================
# USER MANAGEMENT (Admin)
# =====================================================

def get_all_users():
    """Get all users (admin only)"""
    if not is_admin():
        return []
    
    query = """
        SELECT user_id, email, role, first_name, last_name, 
               phone_number, is_active, last_login, created_at
        FROM users
        ORDER BY created_at DESC
    """
    
    return db.execute_query(query)

def deactivate_user(user_id):
    """Deactivate a user account (admin only)"""
    if not is_admin():
        return False, "Unauthorized"
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
        
        db.log_action(get_user_id(), 'USER_DEACTIVATED', 'users', user_id)
        return True, "User deactivated successfully"
    except Exception as e:
        return False, f"Deactivation failed: {str(e)}"

def activate_user(user_id):
    """Activate a user account (admin only)"""
    if not is_admin():
        return False, "Unauthorized"
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
        
        db.log_action(get_user_id(), 'USER_ACTIVATED', 'users', user_id)
        return True, "User activated successfully"
    except Exception as e:
        return False, f"Activation failed: {str(e)}"

# =====================================================
# NOTIFICATIONS
# =====================================================

def get_user_notifications(user_id=None):
    """Get unread notifications for current user"""
    if user_id is None:
        user_id = get_user_id()
    
    if not user_id:
        return []
    
    return db.get_unread_notifications(user_id)

def create_notification(user_id, title, message, notification_type='info', **kwargs):
    """Create a notification for a user"""
    return db.create_notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        **kwargs
    )

def mark_notification_read(notification_id):
    """Mark notification as read"""
    db.mark_notification_read(notification_id)
    
def display_notifications():
    """Display notifications in sidebar"""
    notifications = get_user_notifications()
    
    if notifications:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### 🔔 Notifications ({len(notifications)})")
        
        for notif in notifications[:5]:  # Show top 5
            with st.sidebar.expander(notif['title'], expanded=False):
                st.write(notif['message'])
                if st.button(f"Mark as read", key=f"notif_{notif['notification_id']}"):
                    mark_notification_read(notif['notification_id'])
                    st.rerun()
