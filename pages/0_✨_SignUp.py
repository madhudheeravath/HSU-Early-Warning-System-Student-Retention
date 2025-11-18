"""
Sign Up Page
============
New user registration with database integration
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.auth import register_user

st.set_page_config(
    page_title="Sign Up - HSU EWS",
    page_icon="✨",
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

# Custom CSS for signup page
st.markdown("""
    <style>
    .signup-header {
        text-align: center;
        color: #003366;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .signup-subtitle {
        text-align: center;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Center logo and title
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div style="text-align: center; font-size: 4rem; margin-bottom: 1rem;">✨</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="signup-header">Create Your Account</h1>', unsafe_allow_html=True)
    st.markdown('<p class="signup-subtitle">Join HSU Early Warning System</p>', unsafe_allow_html=True)
    
    # Sign up form
    with st.form("signup_form"):
        st.markdown("### Account Information")
        
        col_a, col_b = st.columns(2)
        with col_a:
            first_name = st.text_input("First Name *", placeholder="John")
        with col_b:
            last_name = st.text_input("Last Name *", placeholder="Doe")
        
        email = st.text_input(
            "📧 Email Address *",
            placeholder="yourname@hsu.edu",
            key="email_input"
        )
        
        password = st.text_input(
            "🔒 Password *",
            type="password",
            placeholder="Create a strong password",
            key="password_input"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirm Password *",
            type="password",
            placeholder="Re-enter your password",
            key="confirm_password_input"
        )
        
        st.markdown("### Role Selection")
        role = st.selectbox(
            "I am a... *",
            ["Select your role", "Student", "Advisor", "Administrator"]
        )
        
        if role == "Student":
            student_id = st.text_input("Student ID *", placeholder="12345678")
        elif role == "Advisor":
            department = st.text_input("Department *", placeholder="Academic Advising")
        elif role == "Administrator":
            department = st.text_input("Department *", placeholder="Student Affairs")
        
        st.markdown("---")
        
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            signup_button = st.form_submit_button("✨ Create Account", type="primary", use_container_width=True)
        
        with col_b:
            back_button = st.form_submit_button("← Back to Login", use_container_width=True)
        
        if back_button:
            st.switch_page("pages/0_🔐_Login.py")
        
        if signup_button:
            if not first_name or not last_name or not email or not password:
                st.error("⚠️ Please fill all required fields (marked with *)")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match")
            elif len(password) < 6:
                st.error("⚠️ Password must be at least 6 characters long")
            elif role == "Select your role":
                st.error("⚠️ Please select your role")
            elif not agree_terms:
                st.error("⚠️ Please agree to the Terms of Service")
            elif not email.endswith('@hsu.edu') and not email.endswith('@example.com'):
                st.error("⚠️ Please use a valid HSU email address (@hsu.edu)")
            else:
                # Register user in database
                result = register_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    role=role.lower(),
                    student_id=student_id if role == "Student" and 'student_id' in locals() else None,
                    department=department if role in ["Advisor", "Administrator"] and 'department' in locals() else None
                )
                
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.success(f"Welcome, {first_name} {last_name}!")
                    st.info("""
                    **Your account is ready!**
                    
                    ✅ Account activated immediately
                    ✅ You can now sign in with your credentials
                    
                    Click the button below to go to the login page.
                    """)
                    st.balloons()
                    
                    # Show login button
                    if st.button("🔐 Go to Login", type="primary", key="goto_login_after_signup"):
                        st.switch_page("pages/0_🔐_Login.py")
                else:
                    st.error(f"❌ {result['message']}")
                    if "already registered" in result['message']:
                        st.info("💡 Try signing in instead, or use a different email address.")
    
    st.markdown("---")
    
    # Already have account
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <p style='color: #6B7280;'>Already have an account?</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔐 Sign In Instead", use_container_width=True):
        st.switch_page("pages/0_🔐_Login.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Help section
    st.info("""
    **Need Help?**
    - Questions about registration? Contact: admissions@hsu.edu
    - Technical issues? Contact: support@hsu.edu
    - Phone: (555) 123-4567
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 10px;'>
    <p>© 2025 HSU Early Warning System | Team Infinite - Group 6</p>
</div>
""", unsafe_allow_html=True)
