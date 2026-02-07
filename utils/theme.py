"""
VivaLingo Design System
Clean, modern interface for Spanish learning.
Consistent light theme with vibrant accent colors.
"""
import re
import streamlit as st
from html import escape as _html_escape


def _esc(text) -> str:
    """HTML-escape a string for safe interpolation."""
    return _html_escape(str(text)) if text is not None else ""

# =============================================================================
# DESIGN TOKENS
# =============================================================================

COLORS = {
    # Primary palette - Vibrant green (learning/success)
    "primary": "#10B981",
    "primary_dark": "#059669",
    "primary_light": "#D1FAE5",

    # Accent palette
    "blue": "#3B82F6",
    "blue_light": "#DBEAFE",
    "purple": "#8B5CF6",
    "purple_light": "#EDE9FE",
    "orange": "#F59E0B",
    "orange_light": "#FEF3C7",
    "red": "#EF4444",
    "red_light": "#FEE2E2",
    "pink": "#EC4899",
    "pink_light": "#FCE7F3",
    "teal": "#14B8A6",
    "teal_light": "#CCFBF1",

    # Neutrals
    "white": "#FFFFFF",
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F5F9",
    "border": "#E2E8F0",
    "border_light": "#F1F5F9",

    # Text
    "text": "#0F172A",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",
}

FONTS = {
    "family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif",
    "size_xs": "0.75rem",
    "size_sm": "0.875rem",
    "size_base": "1rem",
    "size_lg": "1.125rem",
    "size_xl": "1.5rem",
    "size_2xl": "2rem",
    "size_3xl": "2.5rem",
}

SPACING = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "2xl": "3rem",
}

RADII = {
    "sm": "0.5rem",
    "md": "0.75rem",
    "lg": "1rem",
    "xl": "1.25rem",
    "full": "9999px",
}


# =============================================================================
# MAIN CSS
# =============================================================================

def get_css() -> str:
    """Return the complete CSS theme for the app."""
    return """
    <style>
    /* ============================================
       GLOBAL RESET & BASE
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --primary-light: #D1FAE5;
        --blue: #3B82F6;
        --blue-light: #DBEAFE;
        --purple: #8B5CF6;
        --purple-light: #EDE9FE;
        --orange: #F59E0B;
        --orange-light: #FEF3C7;
        --red: #EF4444;
        --red-light: #FEE2E2;
        --teal: #14B8A6;
        --teal-light: #CCFBF1;
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --surface-alt: #F1F5F9;
        --border: #E2E8F0;
        --text: #0F172A;
        --text-secondary: #64748B;
        --text-muted: #94A3B8;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
    }

    /* ============================================
       APP CONTAINER
       ============================================ */
    .stApp,
    [data-testid="stAppViewContainer"],
    .main .block-container {
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    html, body, .stApp, .stMarkdown, p, span, div, label, button, input, textarea, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    .main .block-container {
        max-width: 1200px !important;
        padding: 2rem 2rem 4rem 2rem !important;
    }

    /* ============================================
       HIDE STREAMLIT CHROME
       ============================================ */
    footer,
    #MainMenu,
    .stDeployButton,
    [data-testid="stToolbar"] {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    /* ============================================
       SIDEBAR
       ============================================ */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: var(--text) !important;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ============================================
       TYPOGRAPHY
       ============================================ */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: var(--text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    .stMarkdown p {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
    }

    /* ============================================
       BUTTONS
       ============================================ */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        border-radius: 0.75rem !important;
        padding: 0.625rem 1.25rem !important;
        min-height: 2.75rem !important;
        transition: all 0.15s ease !important;
        border: none !important;
        cursor: pointer !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3), 0 1px 2px rgba(16, 185, 129, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.35), 0 2px 4px rgba(16, 185, 129, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="baseButton-primary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 2px rgba(16, 185, 129, 0.2) !important;
    }

    /* Secondary button */
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
        background-color: var(--surface-alt) !important;
        border-color: #CBD5E1 !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* ============================================
       FORM INPUTS
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stTextArea textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 0.75rem !important;
        color: var(--text) !important;
        font-size: 0.9375rem !important;
        padding: 0.625rem 0.875rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* ============================================
       RADIO BUTTONS
       ============================================ */
    div[role="radiogroup"] label[data-baseweb="radio"] {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 0.75rem !important;
        padding: 0.5rem 0.75rem !important;
        margin-right: 0.5rem !important;
        transition: all 0.15s ease !important;
    }

    div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
        background: var(--primary-light) !important;
        border-color: var(--primary) !important;
    }

    div[role="radiogroup"] label[data-baseweb="radio"] span {
        color: var(--text) !important;
        font-weight: 500 !important;
    }

    /* ============================================
       DROPDOWNS & POPOVERS
       ============================================ */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0.75rem !important;
        box-shadow: var(--shadow-lg) !important;
    }

    [data-baseweb="menu"] li,
    div[role="option"],
    li[role="option"] {
        color: var(--text) !important;
    }

    /* ============================================
       CUSTOM COMPONENT CLASSES
       ============================================ */

    /* Hero Section */
    .vl-hero {
        background: linear-gradient(135deg, #10B981 0%, #059669 50%, #047857 100%) !important;
        border-radius: 1.25rem !important;
        padding: 2rem !important;
        margin-bottom: 1.5rem !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .vl-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
    }
    .vl-hero-title {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0 0 0.5rem 0 !important;
        position: relative !important;
    }
    .vl-hero-subtitle {
        color: rgba(255, 255, 255, 0.85) !important;
        font-size: 1rem !important;
        margin: 0 !important;
        position: relative !important;
    }

    /* Stat Card */
    .vl-stat-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        text-align: center !important;
        transition: box-shadow 0.15s ease, transform 0.15s ease !important;
    }
    .vl-stat-card:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }
    .vl-stat-icon {
        font-size: 1.75rem !important;
        margin-bottom: 0.5rem !important;
        line-height: 1 !important;
    }
    .vl-stat-value {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        line-height: 1 !important;
        margin-bottom: 0.25rem !important;
    }
    .vl-stat-label {
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
    }

    /* Action Card */
    .vl-action-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        margin-bottom: 0.75rem !important;
        transition: box-shadow 0.15s ease, transform 0.15s ease !important;
    }
    .vl-action-card:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }
    .vl-action-card-primary {
        background: linear-gradient(135deg, #10B981, #059669) !important;
        border: none !important;
    }
    .vl-action-card-title {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--text) !important;
        margin-bottom: 0.125rem !important;
    }
    .vl-action-card-primary .vl-action-card-title {
        color: #FFFFFF !important;
    }
    .vl-action-card-subtitle {
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
    }
    .vl-action-card-primary .vl-action-card-subtitle {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    /* Feature Card */
    .vl-feature-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.5rem !important;
        text-align: center !important;
        height: 100% !important;
        transition: box-shadow 0.15s ease, transform 0.15s ease !important;
    }
    .vl-feature-card:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }

    /* Card (generic) */
    .vl-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
    }

    /* Section Header */
    .vl-section-header {
        margin-bottom: 1rem !important;
    }
    .vl-section-title {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: var(--text) !important;
        margin: 0 0 0.25rem 0 !important;
    }
    .vl-section-subtitle {
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
        margin: 0 !important;
    }

    /* Progress Bar */
    .vl-progress-track {
        background: var(--surface-alt) !important;
        height: 0.5rem !important;
        border-radius: 0.25rem !important;
        overflow: hidden !important;
    }
    .vl-progress-fill {
        height: 100% !important;
        border-radius: 0.25rem !important;
        transition: width 0.3s ease !important;
    }

    /* Pill / Badge */
    .vl-pill {
        display: inline-block !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 9999px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }

    /* Feedback boxes */
    .vl-feedback {
        border-radius: 0.75rem !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    .vl-feedback-success {
        background: #D1FAE5 !important;
        color: #065F46 !important;
        border: 1px solid #A7F3D0 !important;
    }
    .vl-feedback-error {
        background: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #FECACA !important;
    }
    .vl-feedback-warning {
        background: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FDE68A !important;
    }
    .vl-feedback-info {
        background: #DBEAFE !important;
        color: #1E40AF !important;
        border: 1px solid #BFDBFE !important;
    }

    /* Empty State */
    .vl-empty-state {
        text-align: center !important;
        padding: 3rem 1.5rem !important;
        color: var(--text-muted) !important;
    }
    .vl-empty-icon {
        font-size: 3rem !important;
        margin-bottom: 1rem !important;
        opacity: 0.5 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

    /* Focus states for accessibility */
    *:focus-visible {
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }

    /* Streamlit label styling */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stRadio > label,
    .stCheckbox > label,
    .stNumberInput > label {
        color: var(--text) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* Divider */
    .stDivider {
        border-color: var(--border) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0.75rem !important;
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }

    /* Selection card style */
    .vl-selection-card {
        border: 2px solid var(--border);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background: var(--surface);
        transition: all 0.15s ease;
    }
    .vl-selection-card-active {
        border-color: var(--primary) !important;
        background: var(--primary-light) !important;
    }

    /* Streak badge */
    .vl-streak-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 700;
    }

    /* Tip card */
    .vl-tip {
        background: var(--blue-light);
        border: 1px solid #93C5FD;
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
    }

    /* ============================================
       BACKWARD-COMPATIBLE CLASSES
       Used by page files (non-vl- prefixed)
       ============================================ */

    /* Card classes */
    .card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    .card-muted {
        background: var(--surface-alt) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
        color: var(--text-secondary) !important;
    }
    .card-header {
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        margin-bottom: 0.75rem !important;
    }
    .card-icon {
        font-size: 1.5rem !important;
        line-height: 1 !important;
    }
    .card-title {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--text) !important;
    }

    /* Metric classes */
    .metric-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        text-align: center !important;
    }
    .metric-value {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        line-height: 1.2 !important;
    }
    .metric-label {
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
        margin-top: 0.25rem !important;
    }

    /* Stat classes (verb_studio) */
    .stat-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        text-align: center !important;
    }
    .stat-value {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        line-height: 1.2 !important;
    }
    .stat-label {
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
        margin-top: 0.25rem !important;
    }

    /* Feedback classes */
    .feedback-box {
        border-radius: 0.75rem !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.5 !important;
    }
    .feedback-success {
        background: #D1FAE5 !important;
        color: #065F46 !important;
        border: 1px solid #A7F3D0 !important;
    }
    .feedback-error {
        background: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #FECACA !important;
    }
    .feedback-warning {
        background: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #FDE68A !important;
    }
    .feedback-info {
        background: #DBEAFE !important;
        color: #1E40AF !important;
        border: 1px solid #BFDBFE !important;
    }

    /* Pill classes */
    .pill {
        display: inline-block !important;
        padding: 0.2rem 0.625rem !important;
        border-radius: 9999px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
    }
    .pill-primary {
        background: var(--primary-light) !important;
        color: var(--primary-dark) !important;
    }
    .pill-secondary {
        background: var(--surface-alt) !important;
        color: var(--text-secondary) !important;
    }
    .pill-accent {
        background: var(--purple-light) !important;
        color: #6D28D9 !important;
    }
    .pill-warning {
        background: var(--orange-light) !important;
        color: #B45309 !important;
    }
    .pill-error {
        background: var(--red-light) !important;
        color: #DC2626 !important;
    }
    .pill-muted {
        background: var(--surface-alt) !important;
        color: var(--text-muted) !important;
    }

    /* Exercise classes */
    .exercise-card {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1rem !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    .exercise-header {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    .exercise-type {
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--primary) !important;
        font-weight: 700 !important;
    }
    .exercise-step {
        font-size: 0.7rem !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
    }
    .exercise-prompt {
        font-size: 1.125rem !important;
        line-height: 1.7 !important;
        color: var(--text) !important;
        padding: 1rem !important;
        background: var(--surface-alt) !important;
        border-radius: 0.75rem !important;
        margin-bottom: 1rem !important;
    }

    /* Chat classes (conversation) */
    .chat-message {
        display: flex !important;
        gap: 0.75rem !important;
        margin-bottom: 1rem !important;
        align-items: flex-start !important;
    }
    .chat-message.user {
        flex-direction: row-reverse !important;
    }
    .chat-avatar {
        width: 2rem !important;
        height: 2rem !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        flex-shrink: 0 !important;
        background: var(--surface-alt) !important;
    }
    .chat-message.user .chat-avatar {
        background: var(--primary-light) !important;
    }
    .chat-bubble {
        background: var(--surface-alt) !important;
        border-radius: 1rem !important;
        padding: 0.75rem 1rem !important;
        max-width: 80% !important;
        color: var(--text) !important;
        line-height: 1.5 !important;
    }
    .chat-message.user .chat-bubble {
        background: var(--primary-light) !important;
        color: #065F46 !important;
    }

    /* Verb classes */
    .verb-option {
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    .verb-option.selected {
        border-color: var(--primary) !important;
        background: var(--primary-light) !important;
    }
    .verb-name {
        font-weight: 700 !important;
        color: var(--text) !important;
        font-size: 1rem !important;
    }
    .verb-meta {
        font-size: 0.8rem !important;
        color: var(--text-secondary) !important;
    }
    .verb-note {
        font-size: 0.8rem !important;
        color: var(--text-muted) !important;
        font-style: italic !important;
        margin-top: 0.25rem !important;
    }

    /* Hero alias (non-prefixed) */
    .hero { background: linear-gradient(135deg, #10B981, #059669, #047857) !important; border-radius: 1.25rem !important; padding: 2rem !important; margin-bottom: 1.5rem !important; overflow: hidden !important; }
    .hero-title { font-size: 1.75rem !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0 0 0.5rem 0 !important; }
    .hero-subtitle { color: rgba(255,255,255,0.85) !important; font-size: 1rem !important; margin: 0 !important; }

    /* Section header alias */
    .section-header { margin-bottom: 1rem !important; }
    .section-title { font-size: 1.25rem !important; font-weight: 700 !important; color: var(--text) !important; margin: 0 0 0.25rem 0 !important; }

    /* Diff highlighting */
    .diff-added {
        background: #D1FAE5 !important;
        color: #065F46 !important;
        padding: 0.1rem 0.3rem !important;
        border-radius: 0.2rem !important;
        text-decoration: none !important;
    }
    .diff-removed {
        background: #FEE2E2 !important;
        color: #991B1B !important;
        padding: 0.1rem 0.3rem !important;
        border-radius: 0.2rem !important;
        text-decoration: line-through !important;
    }

    /* ============================================
       FIX: Material Symbols icon text leak
       Streamlit's sidebar toggle uses Material Symbols.
       When the font fails to load, raw text like
       "keyboard_double_arrow_right" leaks through.
       ============================================ */
    [data-testid="stSidebarCollapsedControl"] {
        overflow: hidden !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        overflow: hidden !important;
        max-width: 2.75rem !important;
        max-height: 2.75rem !important;
        min-width: 2.5rem !important;
        min-height: 2.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 0.5rem !important;
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button span {
        overflow: hidden !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
        display: block !important;
        text-overflow: clip !important;
    }
    /* Hide sidebar nav collapse button text leak too */
    [data-testid="stSidebarNavCollapseButton"],
    [data-testid="stSidebarCollapseButton"] {
        overflow: hidden !important;
    }
    [data-testid="stSidebarNavCollapseButton"] button,
    [data-testid="stSidebarCollapseButton"] button {
        overflow: hidden !important;
        max-width: 2.5rem !important;
        max-height: 2.5rem !important;
    }
    [data-testid="stSidebarNavCollapseButton"] button span,
    [data-testid="stSidebarCollapseButton"] button span {
        overflow: hidden !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
        display: block !important;
    }

    /* ============================================
       MOBILE RESPONSIVE - TABLETS (max-width: 768px)
       ============================================ */
    @media (max-width: 768px) {
        /* Main container - reduce padding */
        .main .block-container {
            padding: 1rem 0.75rem 3rem 0.75rem !important;
            max-width: 100% !important;
        }

        /* Force column containers to wrap */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        /* Columns become 2-per-row on tablets */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
        }

        /* Hero sections */
        .vl-hero, .hero {
            padding: 1.25rem 1rem !important;
            border-radius: 0.75rem !important;
            margin-bottom: 1rem !important;
        }
        .vl-hero-title, .hero-title {
            font-size: 1.25rem !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        .vl-hero-subtitle, .hero-subtitle {
            font-size: 0.875rem !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
        .vl-hero::before {
            display: none !important;
        }

        /* Stat / Metric cards - compact */
        .vl-stat-card, .metric-card, .stat-card {
            padding: 0.625rem 0.5rem !important;
            border-radius: 0.75rem !important;
        }
        .vl-stat-value, .metric-value, .stat-value {
            font-size: 1.25rem !important;
        }
        .vl-stat-icon {
            font-size: 1.25rem !important;
            margin-bottom: 0.25rem !important;
        }
        .vl-stat-label, .metric-label, .stat-label {
            font-size: 0.6rem !important;
            letter-spacing: 0.04em !important;
        }

        /* Cards - reduced padding */
        .vl-card, .card, .exercise-card {
            padding: 0.875rem !important;
            margin-bottom: 0.5rem !important;
            border-radius: 0.75rem !important;
        }
        .card-muted {
            padding: 0.75rem !important;
        }
        .vl-feature-card {
            padding: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }
        .vl-action-card {
            padding: 0.75rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* Sidebar width */
        [data-testid="stSidebar"] {
            min-width: 0 !important;
            max-width: 280px !important;
        }

        /* Typography scaling */
        h1, .stMarkdown h1 { font-size: 1.5rem !important; }
        h2, .stMarkdown h2 { font-size: 1.25rem !important; }
        h3, .stMarkdown h3 { font-size: 1.1rem !important; }
        h4, .stMarkdown h4 { font-size: 1rem !important; }

        .vl-section-title, .section-title {
            font-size: 1.1rem !important;
        }

        /* Buttons - touch friendly */
        .stButton > button {
            min-height: 2.75rem !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 0.8rem !important;
        }

        /* Exercise prompt */
        .exercise-prompt {
            font-size: 1rem !important;
            padding: 0.75rem !important;
        }

        /* Chat bubbles */
        .chat-bubble {
            max-width: 90% !important;
            padding: 0.625rem 0.875rem !important;
        }

        /* Radio buttons - allow wrapping */
        div[role="radiogroup"] {
            flex-wrap: wrap !important;
        }
        div[role="radiogroup"] label[data-baseweb="radio"] {
            margin-bottom: 0.375rem !important;
            padding: 0.375rem 0.625rem !important;
            font-size: 0.8rem !important;
        }

        /* Feedback boxes */
        .vl-feedback, .feedback-box {
            padding: 0.75rem !important;
            font-size: 0.875rem !important;
        }

        /* Progress track */
        .vl-progress-track {
            height: 0.375rem !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.375rem 0.75rem !important;
            font-size: 0.8rem !important;
            white-space: nowrap !important;
        }

        /* Pill / Badge */
        .vl-pill, .pill {
            font-size: 0.65rem !important;
            padding: 0.2rem 0.5rem !important;
        }

        /* Tip card */
        .vl-tip {
            padding: 0.75rem !important;
        }

        /* Selection cards */
        .vl-selection-card {
            padding: 0.75rem !important;
        }

        /* Empty state */
        .vl-empty-state {
            padding: 2rem 1rem !important;
        }
        .vl-empty-icon {
            font-size: 2rem !important;
        }

        /* Lesson card */
        div[style*="linear-gradient"][style*="border-radius: 1rem"] {
            padding: 1rem !important;
        }

        /* Streak badge */
        .vl-streak-badge {
            padding: 0.375rem 0.75rem !important;
            font-size: 0.875rem !important;
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-size: 0.875rem !important;
            padding: 0.625rem !important;
        }

        /* Inline HTML grids - force 2 cols max */
        div[style*="grid-template-columns: 1fr 1fr 1fr"] {
            grid-template-columns: 1fr 1fr !important;
        }
        div[style*="grid-template-columns: repeat"] {
            grid-template-columns: 1fr 1fr !important;
        }

        /* Profile card in sidebar - compact */
        [data-testid="stSidebar"] .vl-card {
            padding: 0.75rem !important;
        }

        /* Scrollable containers */
        .stDataFrame {
            overflow-x: auto !important;
        }

        /* Form inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            font-size: 16px !important; /* Prevents iOS zoom on focus */
        }
    }

    /* ============================================
       MOBILE RESPONSIVE - PHONES (max-width: 480px)
       ============================================ */
    @media (max-width: 480px) {
        /* Tighter padding */
        .main .block-container {
            padding: 0.5rem 0.5rem 2rem 0.5rem !important;
        }

        /* Force single column on phones */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 0 0 100% !important;
            min-width: 100% !important;
        }

        /* Hero - even more compact */
        .vl-hero, .hero {
            padding: 1rem 0.75rem !important;
            border-radius: 0.625rem !important;
        }
        .vl-hero-title, .hero-title {
            font-size: 1.125rem !important;
        }
        .vl-hero-subtitle, .hero-subtitle {
            font-size: 0.8rem !important;
        }

        /* Stats - even more compact */
        .vl-stat-value, .metric-value, .stat-value {
            font-size: 1.125rem !important;
        }
        .vl-stat-card, .metric-card, .stat-card {
            padding: 0.5rem !important;
        }

        /* Cards */
        .vl-card, .card, .exercise-card {
            padding: 0.75rem !important;
            border-radius: 0.625rem !important;
        }
        .vl-feature-card {
            padding: 0.75rem !important;
        }

        /* Typography */
        h1, .stMarkdown h1 { font-size: 1.25rem !important; }
        h2, .stMarkdown h2 { font-size: 1.125rem !important; }
        h3, .stMarkdown h3 { font-size: 1rem !important; }

        .vl-section-title, .section-title {
            font-size: 1rem !important;
        }

        /* Buttons */
        .stButton > button {
            min-height: 2.625rem !important;
            font-size: 0.8rem !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            max-width: 260px !important;
        }

        /* Inline HTML grids - force single col */
        div[style*="grid-template-columns"] {
            grid-template-columns: 1fr !important;
        }
    }

    </style>
    """


def apply_theme():
    """Apply the theme CSS to the page."""
    st.markdown(get_css(), unsafe_allow_html=True)

    # Monkey-patch st.markdown so that ANY call with unsafe_allow_html=True
    # auto-strips leading whitespace from every line. This prevents indented
    # f-string HTML (common in Streamlit apps) from being misinterpreted as
    # Markdown code blocks (4+ leading spaces = code block).
    if not getattr(st.markdown, '_vl_patched', False):
        _original_markdown = st.markdown

        def _patched_markdown(body, *args, unsafe_allow_html=False, **kwargs):
            if unsafe_allow_html and isinstance(body, str):
                body = _clean_html(body)
            return _original_markdown(body, *args, unsafe_allow_html=unsafe_allow_html, **kwargs)

        _patched_markdown._vl_patched = True
        st.markdown = _patched_markdown


def _clean_html(markup: str) -> str:
    """Strip leading whitespace from every line so Markdown never sees 4-space indentation as a code block."""
    lines = markup.strip().splitlines()
    cleaned = "\n".join(line.strip() for line in lines)
    return cleaned


def render_html(markup: str) -> None:
    """Render HTML with consistent formatting."""
    st.markdown(_clean_html(markup), unsafe_allow_html=True)


# =============================================================================
# COMPONENT FUNCTIONS
# =============================================================================

def render_hero(title: str, subtitle: str = "", pills: list = None) -> None:
    """Render a hero section header."""
    pills_html = ""
    if pills:
        pills_html = '<div style="margin-bottom: 0.75rem; position: relative;">' + ' '.join(
            f'<span class="vl-pill" style="background: rgba(255,255,255,0.2); color: #fff;">{p}</span>'
            for p in pills
        ) + '</div>'

    render_html(f"""
        <div class="vl-hero">
            {pills_html}
            <div class="vl-hero-title">{title}</div>
            <div class="vl-hero-subtitle">{subtitle}</div>
        </div>
    """)


def render_section_header(title: str, subtitle: str = "") -> None:
    """Render a section header."""
    subtitle_html = f'<p class="vl-section-subtitle">{subtitle}</p>' if subtitle else ''
    render_html(f"""
        <div class="vl-section-header">
            <h3 class="vl-section-title">{title}</h3>
            {subtitle_html}
        </div>
    """)


def render_stat_card(value: str, label: str, icon: str = "", color: str = "") -> str:
    """Return HTML for a stat card."""
    icon_html = f'<div class="vl-stat-icon">{icon}</div>' if icon else ''
    color_style = f'color: {color} !important;' if color else ''
    return _clean_html(f"""
        <div class="vl-stat-card">
            {icon_html}
            <div class="vl-stat-value" style="{color_style}">{value}</div>
            <div class="vl-stat-label">{label}</div>
        </div>
    """)


def render_metric_card(value: str, label: str, icon: str = "", color: str = "") -> str:
    """Alias for render_stat_card."""
    return render_stat_card(value, label, icon, color)


def render_metric_grid(metrics: list) -> None:
    """Render a grid of metric cards."""
    if not metrics:
        return
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(render_stat_card(
                str(m.get("value", "0")),
                m.get("label", ""),
                m.get("icon", ""),
                m.get("color", "")
            ), unsafe_allow_html=True)


def render_action_card(title: str, subtitle: str, icon: str = "",
                       primary: bool = False, badge: str = "", meta: str = "") -> None:
    """Render an action card."""
    cls = "vl-action-card-primary" if primary else ""
    icon_html = f'<div style="font-size: 1.75rem; margin-right: 1rem; line-height: 1;">{icon}</div>' if icon else ''
    badge_html = f'<span class="vl-pill" style="background: rgba(16,185,129,0.15); color: #059669;">{badge}</span>' if badge else ''
    meta_html = f'<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">{meta}</div>' if meta else ''

    render_html(f"""
        <div class="vl-action-card {cls}">
            <div style="display: flex; align-items: center;">
                {icon_html}
                <div style="flex: 1;">
                    <div class="vl-action-card-title">{title}</div>
                    <div class="vl-action-card-subtitle">{subtitle}</div>
                    {meta_html}
                </div>
                {badge_html}
            </div>
        </div>
    """)


def render_streak_badge(streak: int) -> None:
    """Render a streak badge."""
    if streak > 0:
        render_html(f"""
            <div class="vl-streak-badge">
                <span style="font-size: 1.25rem;">&#x1F525;</span>
                <span style="font-size: 1.125rem;">{streak}</span>
                <span style="font-size: 0.8rem; opacity: 0.9;">day{"s" if streak != 1 else ""}</span>
            </div>
        """)


def render_feedback(feedback_type: str, message: str, details: str = "") -> None:
    """Render a feedback message (success, error, warning, info)."""
    icons = {"success": "&#10003;", "error": "&#10007;", "warning": "&#9888;", "info": "&#8505;"}
    icon = icons.get(feedback_type, icons["info"])
    details_html = f'<div style="margin-top: 0.5rem; opacity: 0.9;">{details}</div>' if details else ''
    render_html(f"""
        <div class="vl-feedback vl-feedback-{feedback_type}">
            <strong>{icon} {message}</strong>
            {details_html}
        </div>
    """)


def render_card(content: str, title: str = "") -> None:
    """Render a generic card."""
    title_html = f'<h4 style="margin: 0 0 0.75rem 0; color: var(--text);">{title}</h4>' if title else ''
    render_html(f"""
        <div class="vl-card">
            {title_html}
            <div style="color: var(--text-secondary);">{content}</div>
        </div>
    """)


def render_pill(text: str, variant: str = "green") -> str:
    """Return HTML for a pill/badge."""
    colors = {
        "green": ("#059669", "#D1FAE5"),
        "blue": ("#1D4ED8", "#DBEAFE"),
        "orange": ("#D97706", "#FEF3C7"),
        "red": ("#DC2626", "#FEE2E2"),
        "purple": ("#7C3AED", "#EDE9FE"),
        "gray": ("#475569", "#F1F5F9"),
    }
    fg, bg = colors.get(variant, colors["green"])
    return f'<span class="vl-pill" style="background: {bg}; color: {fg};">{text}</span>'


def render_progress_bar(value=0, max_value=100, label: str = "",
                        color: str = "var(--primary)") -> None:
    """Render a progress bar."""
    try:
        value = float(value)
        max_value = float(max_value) if max_value else 100
    except (TypeError, ValueError):
        value, max_value = 0, 100
    pct = min(100, (value / max_value * 100)) if max_value > 0 else 0
    label_html = ""
    if label:
        label_html = f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.375rem;">
                <span style="font-size: 0.8rem; font-weight: 500; color: var(--text);">{label}</span>
                <span style="font-size: 0.8rem; color: var(--text-muted);">{int(value) if value == int(value) else value}/{int(max_value) if max_value == int(max_value) else max_value}</span>
            </div>
        """
    render_html(f"""
        <div style="margin-bottom: 0.75rem;">
            {label_html}
            <div class="vl-progress-track">
                <div class="vl-progress-fill" style="width: {pct}%; background: {color};"></div>
            </div>
        </div>
    """)


def render_empty_state(message: str, icon: str = "") -> None:
    """Render an empty state placeholder."""
    icon_html = f'<div class="vl-empty-icon">{icon}</div>' if icon else ''
    render_html(f"""
        <div class="vl-empty-state">
            {icon_html}
            <p style="color: var(--text-muted); margin: 0;">{message}</p>
        </div>
    """)


def render_loading_skeleton(height: str = "100px") -> None:
    """Render a loading skeleton animation."""
    render_html(f"""
        <div style="background: linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%);
                    background-size: 200% 100%; height: {height}; border-radius: 0.75rem;
                    animation: vl-shimmer 1.5s infinite;">
        </div>
        <style>
        @keyframes vl-shimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        </style>
    """)


def render_error_state(message: str, retry_label: str = "Try again") -> bool:
    """Render error state. Returns True if retry clicked."""
    render_html(f"""
        <div class="vl-feedback vl-feedback-error" style="text-align: center;">
            <p><strong>Something went wrong</strong></p>
            <p style="opacity: 0.9;">{message}</p>
        </div>
    """)
    return st.button(retry_label, type="primary")


def render_profile_card(name: str, level: str, vocab_count: int, streak: int, is_active: bool = False) -> str:
    """Render a profile card."""
    border_style = f"border-color: var(--primary);" if is_active else ""
    badge = '<span class="vl-pill" style="background: #D1FAE5; color: #059669;">Active</span>' if is_active else ''

    return _clean_html(f"""
        <div class="vl-card" style="{border_style}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: var(--text);">{name}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Level: {level}</div>
                </div>
                {badge}
            </div>
            <div style="display: flex; gap: 1.5rem;">
                <div>
                    <div style="font-weight: 700; font-size: 1.25rem; color: var(--text);">{vocab_count}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Words</div>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.25rem; color: var(--orange);">{streak} &#x1F525;</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Streak</div>
                </div>
            </div>
        </div>
    """)


def render_exercise_feedback(correct: bool, correct_answer: str, explanation: str = "",
                            common_mistake: str = "") -> None:
    """Render exercise feedback."""
    if correct:
        render_html(f"""
            <div class="vl-feedback vl-feedback-success">
                <strong>&#10003; Correct!</strong>
                {f'<div style="margin-top: 0.5rem;">{explanation}</div>' if explanation else ''}
            </div>
        """)
    else:
        mistake_html = f'<div style="margin-top: 0.5rem; opacity: 0.85;"><em>Tip: {common_mistake}</em></div>' if common_mistake else ''
        render_html(f"""
            <div class="vl-feedback vl-feedback-error">
                <strong>&#10007; Not quite</strong>
                <div style="margin-top: 0.5rem;">Correct answer: <strong>{correct_answer}</strong></div>
                {f'<div style="margin-top: 0.5rem;">{explanation}</div>' if explanation else ''}
                {mistake_html}
            </div>
        """)


def render_domain_coverage(domains: dict) -> None:
    """Render domain coverage bars."""
    for domain, coverage in domains.items():
        try:
            coverage_val = int(coverage)
        except (TypeError, ValueError):
            coverage_val = 0
        render_progress_bar(coverage_val, 100, domain)


def render_quick_actions(actions: list) -> None:
    """Render quick action buttons in a grid."""
    if not actions:
        return
    cols = st.columns(len(actions))
    for col, action in zip(cols, actions):
        with col:
            if st.button(
                f"{action.get('icon', '')} {action.get('label', '')}",
                key=action.get('key', action.get('label', 'action')),
                use_container_width=True,
                type=action.get('type', 'secondary')
            ):
                if action.get('callback'):
                    action['callback']()


def render_lesson_card(title: str, subtitle: str, progress: int = 0, icon: str = "",
                      locked: bool = False) -> None:
    """Render a lesson card."""
    opacity = "0.5" if locked else "1"
    lock_icon = "&#x1F512; " if locked else ""
    progress_bar = ""
    if progress > 0 and not locked:
        progress_bar = f"""
        <div class="vl-progress-track" style="margin-top: 0.75rem;">
            <div class="vl-progress-fill" style="width: {progress}%; background: rgba(255,255,255,0.8);"></div>
        </div>
        """

    render_html(f"""
        <div style="background: linear-gradient(135deg, #10B981, #059669); border-radius: 1rem;
                    padding: 1.25rem; margin-bottom: 0.75rem; opacity: {opacity};">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2rem;">{icon}</div>
                <div style="flex: 1;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">{lock_icon}{title}</div>
                    <div style="font-size: 0.875rem; color: rgba(255,255,255,0.85);">{subtitle}</div>
                    {progress_bar}
                </div>
            </div>
        </div>
    """)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_design_system() -> dict:
    """Return the design system tokens."""
    return {
        "colors": COLORS,
        "fonts": FONTS,
        "spacing": SPACING,
        "radii": RADII,
    }


def normalize_spanish_answer(text: str, strict_accents: bool = False) -> str:
    """Normalize Spanish text for answer comparison."""
    import re
    text = text.strip().lower()
    text = ' '.join(text.split())
    text = re.sub(r'[^\w\s\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1]', '', text)

    if not strict_accents:
        for src, dst in [('\u00e1', 'a'), ('\u00e9', 'e'), ('\u00ed', 'i'),
                         ('\u00f3', 'o'), ('\u00fa', 'u'), ('\u00fc', 'u'),
                         ('\u00f1', 'n')]:
            text = text.replace(src, dst)

    return text


def check_answer(user_answer: str, correct_answers: list, strict_accents: bool = False) -> dict:
    """Check user answer against correct answers."""
    user_norm = normalize_spanish_answer(user_answer, strict_accents=True)
    user_fold = normalize_spanish_answer(user_answer, strict_accents=False)

    for answer in correct_answers:
        ans_norm = normalize_spanish_answer(answer, strict_accents=True)
        ans_fold = normalize_spanish_answer(answer, strict_accents=False)

        if user_norm == ans_norm:
            return {"result": "correct", "matched": answer, "feedback": ""}
        if user_fold == ans_fold:
            if not strict_accents:
                return {"result": "almost", "matched": answer, "feedback": f"Watch the accents: {answer}"}

    return {"result": "incorrect", "matched": None, "feedback": f"Correct answer: {correct_answers[0] if correct_answers else 'N/A'}"}


def validate_exercise(exercise: dict) -> dict:
    """Validate exercise structure."""
    errors = []
    ex_type = exercise.get("type", "")

    if ex_type == "cloze":
        if "before" not in exercise or "after" not in exercise:
            errors.append("Cloze must have 'before' and 'after'")
        if not exercise.get("answer"):
            errors.append("Cloze must have an answer")
    elif ex_type == "mcq":
        if not exercise.get("choices") or len(exercise.get("choices", [])) < 2:
            errors.append("MCQ must have at least 2 choices")
        if not exercise.get("answer"):
            errors.append("MCQ must have an answer")

    if not exercise.get("type"):
        errors.append("Exercise must have a type")

    return {"valid": len(errors) == 0, "errors": errors}


def get_instruction_for_type(ex_type: str) -> str:
    """Get instruction text for exercise type."""
    return {
        "cloze": "Fill in the blank with the correct word",
        "mcq": "Choose the correct answer",
        "translate": "Translate into Spanish",
        "free_recall": "Type the missing word",
    }.get(ex_type, "Complete the exercise")


def render_cloze_sentence(before: str, after: str, answer: str = "", show_answer: bool = False) -> None:
    """Render a cloze deletion sentence."""
    if show_answer:
        blank = f'<span style="background: #D1FAE5; color: #059669; padding: 0.25rem 1rem; border-radius: 0.5rem; font-weight: 700;">{answer}</span>'
    else:
        blank = '<span style="display: inline-block; width: 5rem; border-bottom: 2px dashed var(--text-muted); margin: 0 0.25rem;">&nbsp;</span>'

    render_html(f"""
        <div style="font-size: 1.125rem; line-height: 1.8; padding: 1.25rem; background: var(--surface);
                    border: 1px solid var(--border); border-radius: 0.75rem; color: var(--text);">
            {before}{blank}{after}
        </div>
    """)
