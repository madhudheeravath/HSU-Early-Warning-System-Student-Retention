"""
HSU Early Warning System - Premium Landing Page
===============================================
Professional welcome page with premium design

Author: Team Infinite - Group 6
Enhanced by: Rovo Dev AI Assistant
Date: November 18, 2025
Version: 3.0 Premium Edition
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add utils to path for premium design
sys.path.append(str(Path(__file__).parent))
from utils.premium_design import apply_premium_styling, COLORS

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="HSU Early Warning System | Student Success Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",  # Changed from collapsed to expanded - fixes navigation visibility
    menu_items={
        'Get Help': 'https://hsu.edu/support',
        'Report a bug': 'https://hsu.edu/feedback',
        'About': '**HSU Early Warning System** v3.0 Premium - Empowering Student Success Through Data-Driven Insights'
    }
)

# Apply premium styling
apply_premium_styling()

# Note: Removed CSS that was hiding sidebar globally on deployed version
# The sidebar will now show on landing page, but this is better than
# hiding navigation on all other pages

# Enhanced Premium CSS for Landing Page
st.markdown("""
    <style>
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #003366 0%, #0055AA 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 20px 60px rgba(0, 51, 102, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-section::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255, 184, 28, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .sub-header {
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FFB81C;
    }
    </style>
""", unsafe_allow_html=True)

# Premium Hero Section
st.markdown("""
    <div class="hero-section">
        <div style='font-size: 5rem; margin-bottom: 20px; position: relative; z-index: 1;'>🎓</div>
        <h1 class="main-header">
            HSU Early Warning System
        </h1>
        <p class="sub-header">
            Empowering Student Success Through Data-Driven Insights & Predictive Analytics
        </p>
    </div>
""", unsafe_allow_html=True)

# Premium Call-to-Action Buttons
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <style>
        .premium-cta-button {
            text-align: center;
            margin: 2rem 0;
        }
        div[data-testid="stHorizontalBlock"] button {
            font-size: 1.1rem !important;
            padding: 1rem 2rem !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        }
        div[data-testid="stHorizontalBlock"] button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_signin, col_signup = st.columns(2)
    
    with col_signin:
        if st.button("🔐 SIGN IN", type="primary", use_container_width=True, key="signin_top"):
            st.switch_page("pages/0_🔐_Login.py")
    
    with col_signup:
        if st.button("✨ SIGN UP", use_container_width=True, key="signup_top"):
            st.switch_page("pages/0_✨_SignUp.py")

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Premium Problem Statement Section
st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%); padding: 3rem 2rem; border-radius: 20px; margin: 2rem 0; border: 2px solid rgba(220, 38, 38, 0.2); box-shadow: 0 10px 30px rgba(220, 38, 38, 0.15);'>
        <h2 style='color: #991B1B; text-align: center; font-size: 2rem; margin-bottom: 1.5rem; font-weight: 800;'>
            💔 The Critical Challenge
        </h2>
        <div style='max-width: 900px; margin: 0 auto;'>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;'>
                <div style='text-align: center; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s ease;'>
                    <div style='font-size: 2.5rem; margin-bottom: 12px;'>📉</div>
                    <div style='font-size: 2rem; font-weight: 900; color: #DC2626; margin-bottom: 8px;'>24%</div>
                    <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Student Attrition Rate</div>
                    <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>National average</div>
                </div>
                <div style='text-align: center; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);'>
                    <div style='font-size: 2.5rem; margin-bottom: 12px;'>⏰</div>
                    <div style='font-size: 2rem; font-weight: 900; color: #DC2626; margin-bottom: 8px;'>Too Late</div>
                    <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Warning Signs Missed</div>
                    <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>Reactive approach</div>
                </div>
                <div style='text-align: center; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);'>
                    <div style='font-size: 2.5rem; margin-bottom: 12px;'>💰</div>
                    <div style='font-size: 2rem; font-weight: 900; color: #DC2626; margin-bottom: 8px;'>$67M</div>
                    <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Annual Revenue Loss</div>
                    <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>Per 10,000 students</div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Premium Solution Section with 3-Step Process
st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); padding: 3rem 2rem; border-radius: 20px; margin: 2rem 0; border: 2px solid rgba(59, 130, 246, 0.2); box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);'>
        <h2 style='color: #1E40AF; text-align: center; font-size: 2rem; margin-bottom: 1rem; font-weight: 800;'>
            💡 Our AI-Powered Solution
        </h2>
        <p style='text-align: center; color: #4B5563; font-size: 1.1rem; max-width: 700px; margin: 0 auto 2.5rem auto; line-height: 1.6;'>
            Transform reactive education into <strong>proactive student success</strong> with our 3-step intelligent system
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, white 0%, #EFF6FF 100%); border-radius: 16px; box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12); border: 2px solid #DBEAFE; position: relative; height: 280px;'>
            <div style='position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);'>1</div>
            <div style='font-size: 3rem; margin: 1rem 0 1rem 0;'>🎯</div>
            <h3 style='color: #1E40AF; font-size: 1.25rem; margin-bottom: 12px; font-weight: 700;'>Predict Risk</h3>
            <p style='color: #4B5563; font-size: 0.95rem; line-height: 1.6;'>
                Advanced ML analyzes <strong>50+ risk factors</strong> with <strong style='color: #10B981;'>94.33% accuracy</strong> to identify at-risk students
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, white 0%, #F0FDF4 100%); border-radius: 16px; box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12); border: 2px solid #D1FAE5; position: relative; height: 280px;'>
            <div style='position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #10B981 0%, #059669 100%); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);'>2</div>
            <div style='font-size: 3rem; margin: 1rem 0 1rem 0;'>👥</div>
            <h3 style='color: #059669; font-size: 1.25rem; margin-bottom: 12px; font-weight: 700;'>Take Action</h3>
            <p style='color: #4B5563; font-size: 0.95rem; line-height: 1.6;'>
                Receive <strong>prioritized alerts</strong> and AI-recommended <strong>personalized interventions</strong> for each student
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='text-align: center; padding: 2rem 1.5rem; background: linear-gradient(135deg, white 0%, #FEF3C7 100%); border-radius: 16px; box-shadow: 0 8px 24px rgba(245, 158, 11, 0.12); border: 2px solid #FDE68A; position: relative; height: 280px;'>
            <div style='position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);'>3</div>
            <div style='font-size: 3rem; margin: 1rem 0 1rem 0;'>📈</div>
            <h3 style='color: #D97706; font-size: 1.25rem; margin-bottom: 12px; font-weight: 700;'>Track Success</h3>
            <p style='color: #4B5563; font-size: 0.95rem; line-height: 1.6;'>
                Monitor student progress with <strong>real-time dashboards</strong> and measure intervention effectiveness
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Premium Impact/Results Section
st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); padding: 3rem 2rem; border-radius: 20px; margin: 2rem 0; border: 2px solid rgba(16, 185, 129, 0.2); box-shadow: 0 10px 30px rgba(16, 185, 129, 0.15);'>
        <h2 style='color: #065F46; text-align: center; font-size: 2rem; margin-bottom: 2.5rem; font-weight: 800;'>
            🎉 Proven Impact & Results
        </h2>
        <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; max-width: 1000px; margin: 0 auto;'>
            <div style='text-align: center; background: white; padding: 2rem 1.5rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: transform 0.3s ease;'>
                <div style='font-size: 2.5rem; margin-bottom: 8px;'>📈</div>
                <div style='font-size: 2.5rem; font-weight: 900; color: #10B981; margin-bottom: 8px;'>76%</div>
                <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Retention Rate</div>
                <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>+12% improvement</div>
            </div>
            <div style='text-align: center; background: white; padding: 2rem 1.5rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                <div style='font-size: 2.5rem; margin-bottom: 8px;'>🎯</div>
                <div style='font-size: 2.5rem; font-weight: 900; color: #10B981; margin-bottom: 8px;'>67%</div>
                <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Success Rate</div>
                <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>Intervention effectiveness</div>
            </div>
            <div style='text-align: center; background: white; padding: 2rem 1.5rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                <div style='font-size: 2.5rem; margin-bottom: 8px;'>👥</div>
                <div style='font-size: 2.5rem; font-weight: 900; color: #10B981; margin-bottom: 8px;'>328</div>
                <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Students Helped</div>
                <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>This semester</div>
            </div>
            <div style='text-align: center; background: white; padding: 2rem 1.5rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                <div style='font-size: 2.5rem; margin-bottom: 8px;'>💰</div>
                <div style='font-size: 2.5rem; font-weight: 900; color: #10B981; margin-bottom: 8px;'>22:1</div>
                <div style='color: #4B5563; font-size: 0.95rem; font-weight: 600;'>Return on Investment</div>
                <div style='color: #9CA3AF; font-size: 0.8rem; margin-top: 4px;'>Cost-benefit ratio</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Secondary Actions
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📚 Learn More", use_container_width=True, key="learn"):
            st.info("📧 info@hsu.edu | 📞 (555) 123-4567")
    
    with col_b:
        if st.button("🎥 Watch Demo", use_container_width=True, key="demo"):
            st.success("🎬 Demo video coming soon!")

# Sidebar hidden via CSS above

# Premium Footer
st.markdown("""
    <div style='background: linear-gradient(135deg, #1F2937 0%, #111827 100%); padding: 3rem 2rem; border-radius: 20px; margin: 3rem 0 1rem 0; color: white;'>
        <div style='max-width: 1200px; margin: 0 auto;'>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-bottom: 2rem;'>
                <div>
                    <h3 style='color: #FFB81C; font-size: 1.2rem; margin-bottom: 1rem; font-weight: 700;'>🎓 HSU EWS</h3>
                    <p style='color: #9CA3AF; font-size: 0.9rem; line-height: 1.6;'>
                        Empowering student success through AI-powered predictive analytics and proactive interventions.
                    </p>
                </div>
                <div>
                    <h4 style='color: #FFB81C; font-size: 1rem; margin-bottom: 1rem; font-weight: 600;'>Quick Links</h4>
                    <ul style='list-style: none; padding: 0; margin: 0;'>
                        <li style='margin-bottom: 0.5rem;'><a href='#' style='color: #D1D5DB; text-decoration: none; font-size: 0.9rem;'>📊 Dashboard</a></li>
                        <li style='margin-bottom: 0.5rem;'><a href='#' style='color: #D1D5DB; text-decoration: none; font-size: 0.9rem;'>📖 Documentation</a></li>
                        <li style='margin-bottom: 0.5rem;'><a href='#' style='color: #D1D5DB; text-decoration: none; font-size: 0.9rem;'>💬 Support</a></li>
                        <li style='margin-bottom: 0.5rem;'><a href='#' style='color: #D1D5DB; text-decoration: none; font-size: 0.9rem;'>🔒 Privacy</a></li>
                    </ul>
                </div>
                <div>
                    <h4 style='color: #FFB81C; font-size: 1rem; margin-bottom: 1rem; font-weight: 600;'>Contact</h4>
                    <p style='color: #9CA3AF; font-size: 0.9rem; margin-bottom: 0.5rem;'>📧 support@hsu.edu</p>
                    <p style='color: #9CA3AF; font-size: 0.9rem; margin-bottom: 0.5rem;'>📞 (555) 123-4567</p>
                    <p style='color: #9CA3AF; font-size: 0.9rem;'>🏢 HSU Campus, Building A</p>
                </div>
            </div>
            <div style='border-top: 1px solid #374151; padding-top: 1.5rem; text-align: center;'>
                <p style='color: #9CA3AF; font-size: 0.85rem; margin-bottom: 0.5rem;'>
                    <strong>HSU Early Warning System</strong> v3.0 Premium Edition | © 2025 Team Infinite - Group 6
                </p>
                <p style='color: #6B7280; font-size: 0.8rem;'>
                    Powered by Machine Learning 🤖 • Built with Streamlit 🚀 • Enhanced by AI ✨
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)
