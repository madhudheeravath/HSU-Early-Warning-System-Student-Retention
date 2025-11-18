"""
Premium Design System for HSU Early Warning System
===================================================
Ultra-professional styling, animations, and UI components

Author: Rovo Dev AI Assistant
Date: November 18, 2025
"""

import streamlit as st

# =====================================================
# COLOR PALETTE - Premium HSU Brand Colors
# =====================================================

COLORS = {
    # Primary Brand Colors
    'primary': '#003366',        # Deep Navy Blue (Primary)
    'primary_light': '#0055AA',  # Lighter Blue
    'primary_dark': '#001F3F',   # Darker Navy
    
    # Secondary/Accent Colors
    'accent': '#FFB81C',         # HSU Gold
    'accent_light': '#FFD700',   # Light Gold
    'accent_dark': '#CC9500',    # Dark Gold
    
    # Status Colors
    'success': '#10B981',        # Green
    'warning': '#F59E0B',        # Orange
    'danger': '#DC2626',         # Red
    'info': '#3B82F6',           # Blue
    
    # Neutral Colors
    'white': '#FFFFFF',
    'gray_50': '#F9FAFB',
    'gray_100': '#F3F4F6',
    'gray_200': '#E5E7EB',
    'gray_300': '#D1D5DB',
    'gray_400': '#9CA3AF',
    'gray_500': '#6B7280',
    'gray_600': '#4B5563',
    'gray_700': '#374151',
    'gray_800': '#1F2937',
    'gray_900': '#111827',
    
    # Risk Level Colors
    'critical': '#DC2626',
    'high': '#F59E0B',
    'medium': '#FBBF24',
    'low': '#10B981',
}

# =====================================================
# PREMIUM CSS STYLES
# =====================================================

def get_premium_css():
    """Get comprehensive premium CSS styling"""
    return f"""
    <style>
    /* ==================== GLOBAL STYLES ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700;900&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Main Container */
    .main {{
        background: linear-gradient(135deg, {COLORS['gray_50']} 0%, {COLORS['white']} 100%);
        padding: 2rem;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        padding: 2rem 1rem;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
    }}
    
    [data-testid="stSidebar"] * {{
        color: {COLORS['white']} !important;
    }}
    
    [data-testid="stSidebar"] .stButton button {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_dark']} 100%);
        color: {COLORS['primary']} !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 184, 28, 0.3);
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 184, 28, 0.4);
    }}
    
    /* ==================== PREMIUM CARDS ==================== */
    .premium-card {{
        background: {COLORS['white']};
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid {COLORS['gray_200']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .premium-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
    }}
    
    .premium-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    }}
    
    /* ==================== HEADERS ==================== */
    .premium-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: {COLORS['white']};
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0, 51, 102, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .premium-header::after {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }}
    
    .premium-header h1 {{
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }}
    
    .premium-header p {{
        font-size: 1.2rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 400;
    }}
    
    /* ==================== BUTTONS ==================== */
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        color: {COLORS['white']};
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 51, 102, 0.3);
        cursor: pointer;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 51, 102, 0.4);
        background: linear-gradient(135deg, {COLORS['primary_light']} 0%, {COLORS['primary']} 100%);
    }}
    
    .stButton button:active {{
        transform: translateY(0px);
    }}
    
    /* Premium Button Variants */
    .premium-btn-primary {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
    }}
    
    .premium-btn-accent {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_dark']} 100%);
        color: {COLORS['primary']} !important;
    }}
    
    .premium-btn-success {{
        background: linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%);
    }}
    
    .premium-btn-danger {{
        background: linear-gradient(135deg, {COLORS['danger']} 0%, #991B1B 100%);
    }}
    
    /* ==================== METRICS/STATS ==================== */
    .premium-metric {{
        background: {COLORS['white']};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid {COLORS['gray_200']};
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .premium-metric:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    }}
    
    .premium-metric-value {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .premium-metric-label {{
        font-size: 0.9rem;
        color: {COLORS['gray_600']};
        font-weight: 500;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* ==================== TABLES ==================== */
    .dataframe {{
        border: none !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
    }}
    
    .dataframe thead tr {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        color: {COLORS['white']};
    }}
    
    .dataframe thead th {{
        padding: 1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }}
    
    .dataframe tbody tr {{
        transition: all 0.2s ease;
    }}
    
    .dataframe tbody tr:hover {{
        background-color: {COLORS['gray_50']} !important;
        transform: scale(1.01);
    }}
    
    .dataframe tbody td {{
        padding: 1rem !important;
        border-bottom: 1px solid {COLORS['gray_200']} !important;
    }}
    
    /* ==================== INPUTS ==================== */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {{
        border-radius: 12px !important;
        border: 2px solid {COLORS['gray_300']} !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: {COLORS['white']} !important;
    }}
    
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1) !important;
        outline: none !important;
    }}
    
    /* ==================== BADGES ==================== */
    .badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .badge-critical {{
        background: linear-gradient(135deg, {COLORS['critical']} 0%, #991B1B 100%);
        color: {COLORS['white']};
    }}
    
    .badge-high {{
        background: linear-gradient(135deg, {COLORS['high']} 0%, #D97706 100%);
        color: {COLORS['white']};
    }}
    
    .badge-medium {{
        background: linear-gradient(135deg, {COLORS['medium']} 0%, #F59E0B 100%);
        color: {COLORS['gray_900']};
    }}
    
    .badge-low {{
        background: linear-gradient(135deg, {COLORS['low']} 0%, #059669 100%);
        color: {COLORS['white']};
    }}
    
    /* ==================== ALERTS ==================== */
    .premium-alert {{
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }}
    
    .premium-alert-success {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left-color: {COLORS['success']};
    }}
    
    .premium-alert-warning {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left-color: {COLORS['warning']};
    }}
    
    .premium-alert-danger {{
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        border-left-color: {COLORS['danger']};
    }}
    
    .premium-alert-info {{
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-left-color: {COLORS['info']};
    }}
    
    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .animate-fadeInUp {{
        animation: fadeInUp 0.6s ease-out;
    }}
    
    .animate-fadeIn {{
        animation: fadeIn 0.4s ease-out;
    }}
    
    .animate-slideInRight {{
        animation: slideInRight 0.5s ease-out;
    }}
    
    /* ==================== EXPANDERS ==================== */
    .streamlit-expanderHeader {{
        background: linear-gradient(135deg, {COLORS['gray_50']} 0%, {COLORS['white']} 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem !important;
        font-weight: 600;
        border: 1px solid {COLORS['gray_200']};
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: linear-gradient(135deg, {COLORS['gray_100']} 0%, {COLORS['gray_50']} 100%);
        border-color: {COLORS['primary']};
    }}
    
    /* ==================== TABS ==================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: {COLORS['white']};
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        color: {COLORS['white']};
        box-shadow: 0 4px 15px rgba(0, 51, 102, 0.3);
    }}
    
    /* ==================== PROGRESS BARS ==================== */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        border-radius: 10px;
    }}
    
    /* ==================== TOOLTIPS ==================== */
    [data-testid="stTooltipIcon"] {{
        color: {COLORS['gray_500']};
        transition: color 0.3s ease;
    }}
    
    [data-testid="stTooltipIcon"]:hover {{
        color: {COLORS['primary']};
    }}
    
    /* ==================== DIVIDERS ==================== */
    hr {{
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, {COLORS['gray_300']} 50%, transparent 100%);
    }}
    
    /* ==================== SCROLLBAR ==================== */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['gray_100']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {COLORS['primary_light']} 0%, {COLORS['primary']} 100%);
    }}
    
    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {{
        .premium-header h1 {{
            font-size: 2rem;
        }}
        
        .premium-card {{
            padding: 1.5rem;
        }}
        
        .premium-metric-value {{
            font-size: 2rem;
        }}
    }}
    
    /* ==================== LOADING SPINNER ==================== */
    .stSpinner > div {{
        border-top-color: {COLORS['primary']} !important;
    }}
    
    /* ==================== SELECTBOX ==================== */
    [data-baseweb="select"] {{
        border-radius: 12px !important;
    }}
    
    /* ==================== CHECKBOX & RADIO ==================== */
    .stCheckbox, .stRadio {{
        padding: 0.5rem 0;
    }}
    
    /* ==================== FOOTER ==================== */
    .premium-footer {{
        background: linear-gradient(135deg, {COLORS['gray_900']} 0%, {COLORS['gray_800']} 100%);
        color: {COLORS['white']};
        padding: 2rem;
        border-radius: 16px;
        margin-top: 3rem;
        text-align: center;
    }}
    
    /* ==================== GLASSMORPHISM EFFECT ==================== */
    .glass-card {{
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }}
    
    /* ==================== HIDE STREAMLIT BRANDING ==================== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    </style>
    """

# =====================================================
# PREMIUM COMPONENT FUNCTIONS
# =====================================================

def premium_header(title, subtitle="", icon="🎓"):
    """Create a premium header"""
    st.markdown(f"""
        <div class="premium-header animate-fadeInUp">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def premium_metric(label, value, icon="📊", color="primary"):
    """Create a premium metric card"""
    gradient_colors = {
        'primary': f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%)",
        'success': f"linear-gradient(135deg, {COLORS['success']} 0%, #059669 100%)",
        'warning': f"linear-gradient(135deg, {COLORS['warning']} 0%, #D97706 100%)",
        'danger': f"linear-gradient(135deg, {COLORS['danger']} 0%, #991B1B 100%)",
        'info': f"linear-gradient(135deg, {COLORS['info']} 0%, #2563EB 100%)",
    }
    
    st.markdown(f"""
        <div class="premium-metric animate-fadeIn">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div class="premium-metric-value" style="background: {gradient_colors.get(color, gradient_colors['primary'])}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {value}
            </div>
            <div class="premium-metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def premium_alert(message, alert_type="info", icon=None):
    """Create a premium alert"""
    icons = {
        'success': '✅',
        'warning': '⚠️',
        'danger': '🚨',
        'info': 'ℹ️'
    }
    
    display_icon = icon or icons.get(alert_type, 'ℹ️')
    
    st.markdown(f"""
        <div class="premium-alert premium-alert-{alert_type} animate-fadeIn">
            <strong>{display_icon} {message}</strong>
        </div>
    """, unsafe_allow_html=True)

def premium_badge(text, badge_type="primary"):
    """Create a premium badge"""
    return f'<span class="badge badge-{badge_type}">{text}</span>'

def apply_premium_styling():
    """Apply all premium CSS styling"""
    st.markdown(get_premium_css(), unsafe_allow_html=True)

# =====================================================
# PREMIUM LAYOUTS
# =====================================================

def create_stat_cards(stats):
    """Create a row of premium stat cards
    
    Args:
        stats: List of dicts with 'label', 'value', 'icon', 'color'
    """
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            premium_metric(
                stat.get('label', ''),
                stat.get('value', 0),
                stat.get('icon', '📊'),
                stat.get('color', 'primary')
            )

def premium_success_message(message):
    """Show premium success message"""
    premium_alert(message, 'success', '🎉')

def premium_error_message(message):
    """Show premium error message"""
    premium_alert(message, 'danger', '❌')

def premium_warning_message(message):
    """Show premium warning message"""
    premium_alert(message, 'warning', '⚠️')

def premium_info_message(message):
    """Show premium info message"""
    premium_alert(message, 'info', 'ℹ️')
