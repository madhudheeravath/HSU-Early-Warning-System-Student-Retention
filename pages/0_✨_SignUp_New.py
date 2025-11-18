"""
User Registration Page - Database Version
==========================================
Allows new users to register for the system

Author: Team Infinite - Group 6
Date: 2025
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.db_auth import register_user, validate_email, validate_password

st.set_page_config(
    page_title="Sign Up - HSU",
    page_icon="✨",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .signup-header {
        text-align: center;
        color: #003366;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    .stSelectbox > div > div > select {
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='signup-header'>✨ Create Your Account</h1>", unsafe_allow_html=True)

# Check if already logged in
if st.session_state.get("authenticated", False):
    st.success(f"✅ Already logged in as {st.session_state.get('name', 'User')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go to Dashboard", use_container_width=True):
            st.switch_page("pages/1_🏠_Dashboard.py")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            from utils.db_auth import logout
            logout()
    st.stop()

# Sign up form
with st.form("signup_form"):
    st.markdown("### Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name *", placeholder="John")
    with col2:
        last_name = st.text_input("Last Name *", placeholder="Doe")
    
    email = st.text_input("Email Address *", placeholder="john.doe@hsu.edu")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password *", type="password", placeholder="Min. 8 characters")
    with col2:
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
    
    phone_number = st.text_input("Phone Number (Optional)", placeholder="(555) 123-4567")
    
    st.markdown("### Account Type")
    
    role = st.selectbox(
        "I am a...",
        ["Student", "Advisor/Faculty", "Administrator"],
        help="Select your role in the system"
    )
    
    # Role-specific fields
    if role == "Student":
        st.markdown("### Student Information")
        
        col1, col2 = st.columns(2)
        with col1:
            classification = st.selectbox(
                "Classification",
                ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
            )
        with col2:
            date_of_birth = st.date_input(
                "Date of Birth",
                min_value=datetime(1940, 1, 1),
                max_value=datetime(2010, 12, 31),
                value=datetime(2000, 1, 1)
            )
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        with col2:
            first_gen = st.checkbox("First Generation Student")
        
        international = st.checkbox("International Student")
    
    elif role == "Advisor/Faculty":
        st.markdown("### Advisor Information")
        
        department = st.text_input("Department", placeholder="e.g., Academic Advising")
        office_location = st.text_input("Office Location (Optional)", placeholder="e.g., Building A, Room 101")
    
    # Terms and conditions
    st.markdown("---")
    agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
    
    # Submit button
    submitted = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
    
    if submitted:
        # Validation
        errors = []
        
        if not first_name or not last_name:
            errors.append("Please enter your first and last name")
        
        if not email:
            errors.append("Please enter your email address")
        elif not validate_email(email):
            errors.append("Please enter a valid email address")
        
        if not password:
            errors.append("Please enter a password")
        elif password != confirm_password:
            errors.append("Passwords do not match")
        else:
            is_valid, msg = validate_password(password)
            if not is_valid:
                errors.append(msg)
        
        if not agree_terms:
            errors.append("You must agree to the Terms of Service")
        
        # Show errors
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Register user
            with st.spinner("Creating your account..."):
                # Map role
                role_map = {
                    "Student": "student",
                    "Advisor/Faculty": "advisor",
                    "Administrator": "admin"
                }
                
                user_role = role_map[role]
                
                # Prepare additional data
                kwargs = {
                    'phone_number': phone_number if phone_number else None,
                    'is_verified': 0  # Require email verification in production
                }
                
                # Add role-specific data
                if user_role == 'student':
                    kwargs.update({
                        'classification': classification,
                        'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                        'gender': gender,
                        'first_generation_student': 1 if first_gen else 0,
                        'international_student': 1 if international else 0
                    })
                elif user_role == 'advisor':
                    kwargs.update({
                        'department': department if department else 'Academic Advising',
                        'office_location': office_location
                    })
                
                # Register
                success, message, user_id = register_user(
                    email=email,
                    password=password,
                    role=user_role,
                    first_name=first_name,
                    last_name=last_name,
                    **kwargs
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    
                    st.info("""
                    **Next Steps:**
                    1. Check your email for verification link (in production)
                    2. Log in with your credentials
                    3. Complete your profile
                    """)
                    
                    # Show login button
                    if st.button("🔐 Go to Login", type="primary", use_container_width=True):
                        st.switch_page("pages/0_🔐_Login.py")
                else:
                    st.error(f"❌ {message}")

# Additional info
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Already have an account?")
    if st.button("🔐 Sign In", use_container_width=True):
        st.switch_page("pages/0_🔐_Login.py")

with col2:
    st.markdown("### Need help?")
    if st.button("💬 Contact Support", use_container_width=True):
        st.info("📧 support@hsu.edu | 📞 (555) 123-4567")

# Footer
st.markdown("---")
st.caption("© 2025 HSU Early Warning System | Secure Registration")
st.caption("Your data is encrypted and protected according to FERPA guidelines")
