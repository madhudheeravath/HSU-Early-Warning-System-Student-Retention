"""
Login Page
==========
Authentication portal for all user roles
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import authenticate_user

st.set_page_config(
    page_title="Login - HSU EWS",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for login page
st.markdown("""
    <style>
    .login-header {
        text-align: center;
        color: #003366;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .login-subtitle {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Center logo and title
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div style="text-align: center; font-size: 4rem; margin-bottom: 1rem;">🎓</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="login-header">HSU Early Warning System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Sign in to continue</p>', unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        email = st.text_input(
            "📧 Email Address",
            placeholder="yourname@hsu.edu",
            key="email_input"
        )
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            key="password_input"
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            login_button = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        with col_b:
            back_button = st.form_submit_button("← Back", use_container_width=True)
        
        if back_button:
            st.switch_page("app.py")
        
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
                    
                    # Redirect based on role
                    if user['role'] == 'student':
                        st.info("Redirecting to Student Portal...")
                        st.switch_page("pages/4_🎓_Student_Portal.py")
                    elif user['role'] == 'advisor':
                        st.info("Redirecting to Advisor Dashboard...")
                        st.switch_page("pages/1_🏠_Dashboard.py")
                    elif user['role'] == 'admin':
                        st.info("Redirecting to Admin Portal...")
                        st.switch_page("pages/5_👔_Admin_Portal.py")
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.warning("⚠️ Please enter both email and password")
    
    st.markdown("---")
    
    # Sign Up link
    st.markdown("""
        <div style='text-align: center; padding: 15px;'>
            <p style='color: #6B7280;'>Don't have an account?</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ Create New Account", use_container_width=True, key="goto_signup"):
        st.switch_page("pages/0_✨_SignUp.py")
    
    st.markdown("---")
    
    # Help section
    st.info("""
    **Need Help?**
    - Forgot password? Contact IT Support: support@hsu.edu
    - New user? Contact your department administrator
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 10px;'>
    <p>© 2025 HSU Early Warning System | Team Infinite - Group 6</p>
</div>
""", unsafe_allow_html=True)
