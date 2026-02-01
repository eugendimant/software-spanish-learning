"""
Clean, modern design system - Light mode for readability.
Optimized for Streamlit with proper contrast and iOS-inspired aesthetics.
"""
import streamlit as st
from textwrap import dedent


# ============================================
# DESIGN TOKENS - Light Mode
# ============================================
COLORS = {
    # Backgrounds - clean whites and light grays
    "bg_base": "#ffffff",
    "bg_card": "#f8fafc",
    "bg_elevated": "#f1f5f9",
    "bg_hover": "#e2e8f0",

    # Text - strong contrast
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#64748b",

    # Accent colors - vibrant purple
    "accent": "#6366f1",
    "accent_light": "#818cf8",
    "accent_dark": "#4f46e5",

    # Semantic
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",

    # Borders
    "border": "#e2e8f0",
    "border_hover": "#cbd5e1",
}

SPACING = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "2xl": "48px"}
RADII = {"sm": "8px", "md": "12px", "lg": "16px", "xl": "20px", "full": "9999px"}


def get_css() -> str:
    """Return clean light-mode CSS optimized for readability."""
    return """
    <style>
    /* ============================================
       CLEAN LIGHT DESIGN SYSTEM
       High contrast • Reader-friendly • Modern
       ============================================ */

    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ============================================
       BASE STYLES - Light Mode
       ============================================ */
    :root {
        --bg-surface: rgba(255, 255, 255, 0.03);
        --bg-elevated: rgba(255, 255, 255, 0.06);
        --surface: rgba(255, 255, 255, 0.03);
        --border: rgba(255, 255, 255, 0.08);
        --primary: #6366f1;
        --accent: #6366f1;
        --accent-muted: rgba(99, 102, 241, 0.15);
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
    }
    .stApp,
    .stApp > div,
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stVerticalBlock"],
    .main .block-container {
        background: linear-gradient(180deg, #0c0c0f 0%, #111118 100%) !important;
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif, 'Apple Color Emoji',
            'Segoe UI Emoji', 'Noto Color Emoji' !important;
    }

    .main .block-container {
        padding: 2rem !important;
        max-width: 1200px !important;
    }

    /* Hide Streamlit branding */
    footer,
    #MainMenu,
    .stDeployButton,
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Keep header for sidebar toggle, but make it subtle */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        height: 2.5rem !important;
    }

    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] > button,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] > button {
        opacity: 1 !important;
        pointer-events: auto !important;
        color: #ffffff !important;
    }

    /* ============================================
       SIDEBAR - Clean with visible toggle
       ============================================ */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] {
        background: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1rem !important;
        background: transparent !important;
    }

    /* Sidebar toggle button - ALWAYS VISIBLE */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[kind="header"],
    [data-testid="stSidebar"] button[kind="header"],
    .css-1rs6os button,
    [data-testid="baseButton-header"] {
        background: #6366f1 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover,
    button[kind="header"]:hover {
        background: #4f46e5 !important;
        transform: scale(1.05) !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg,
    button[kind="header"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
    }

    /* Sidebar text styling */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #64748b !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #334155 !important;
    }

    /* Hide default Streamlit pages navigation (use custom nav) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ============================================
       TYPOGRAPHY - High contrast
       ============================================ */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.3 !important;
    }

    h1, .stMarkdown h1 { font-size: 2rem !important; font-weight: 700 !important; }
    h2, .stMarkdown h2 { font-size: 1.5rem !important; }
    h3, .stMarkdown h3 { font-size: 1.25rem !important; }
    h4, .stMarkdown h4 { font-size: 1.1rem !important; }

    p, .stMarkdown p, .stMarkdown, .stText {
        color: #334155 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    strong, b { color: #0f172a !important; font-weight: 600 !important; }
    a { color: #6366f1 !important; text-decoration: none !important; }
    a:hover { color: #4f46e5 !important; text-decoration: underline !important; }

    label, .stTextInput label, .stSelectbox label {
        color: #334155 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }

    /* ============================================
       BUTTONS - Clear, readable
       ============================================ */
    .stButton > button {
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        min-height: 46px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    /* Secondary button - light gray with dark text */
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
        background: #e2e8f0 !important;
        border-color: #cbd5e1 !important;
    }

    /* Primary button - solid purple with white text */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: #6366f1 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    .stButton > button:disabled {
        color: #cbd5f5 !important;
        opacity: 0.6 !important;
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ============================================
       FORM INPUTS - Clean with good contrast
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background: rgba(15, 15, 20, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder,
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder {
        color: #64748b !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        caret-color: #e2e8f0 !important;
    }

    /* ============================================
       SELECT / DROPDOWN
       ============================================ */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
    }

    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"] span {
        color: #0f172a !important;
    }

    /* Radio buttons - make selection obvious */
    div[role="radiogroup"] input[type="radio"] {
        accent-color: #6366f1 !important;
    }

    div[role="radiogroup"] label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        margin-right: 8px !important;
    }

    div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.6) !important;
    }

    div[role="radiogroup"] label[data-baseweb="radio"] span {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* Dropdown popover */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    [data-baseweb="menu"] li,
    div[role="option"],
    li[role="option"] {
        color: #0f172a !important;
        padding: 0.75rem 1rem !important;
    }

    [data-baseweb="menu"] li:hover,
    div[role="option"]:hover,
    li[role="option"]:hover {
        background: #f1f5f9 !important;
    }

    /* ============================================
       RADIO BUTTONS
       ============================================ */
    .stRadio > div > label {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        color: #334155 !important;
        font-weight: 500 !important;
    }

    .stRadio > div > label:hover {
        background: #f1f5f9 !important;
    }

    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label:has(input:checked) {
        background: #eef2ff !important;
        border-color: #6366f1 !important;
        color: #4f46e5 !important;
    }

    /* ============================================
       PROGRESS BAR
       ============================================ */
    .stProgress > div > div {
        background: #e2e8f0 !important;
        border-radius: 6px !important;
        height: 8px !important;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        border-radius: 6px !important;
    }

    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    .streamlit-expanderHeader:hover {
        background: #f1f5f9 !important;
    }

    .streamlit-expanderContent {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        color: #334155 !important;
    }

    /* ============================================
       TABS
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #64748b !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a !important;
    }

    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }

    /* ============================================
       ALERTS
       ============================================ */
    .stAlert, div[data-testid="stAlert"] {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #334155 !important;
    }

    /* ============================================
       DIVIDER
       ============================================ */
    hr {
        border: none !important;
        border-top: 1px solid #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }

    /* ============================================
       CUSTOM COMPONENT CLASSES
       ============================================ */

    /* Card */
    .card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.2s ease !important;
    }

    .card:hover {
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }

    .card h3, .card h4 {
        color: #0f172a !important;
        margin-bottom: 0.5rem !important;
    }

    .card p {
        color: #64748b !important;
    }

    /* Glass Card - subtle elevation */
    .glass-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    .glass-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
    }

    /* Stat Card */
    .stat-card {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        text-align: center !important;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        text-align: center !important;
    }

    .stat-value {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        line-height: 1.2 !important;
        margin-bottom: 0.25rem !important;
    }

    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1 !important;
        margin-bottom: 0.25rem !important;
    }

    .stat-label {
        font-size: 0.8rem !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 500 !important;
    }

    .metric-label {
        font-size: 0.8rem !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* Action Card */
    .action-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    .action-card:hover {
        border-color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1) !important;
    }

    .action-card-primary {
        background: #eef2ff !important;
        border-color: #c7d2fe !important;
    }

    .action-card-title {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        margin-bottom: 0.25rem !important;
    }

    .action-card-subtitle {
        font-size: 0.9rem !important;
        color: #64748b !important;
    }

    /* Pills / Badges */
    .pill {
        display: inline-flex !important;
        align-items: center !important;
        padding: 0.35rem 0.75rem !important;
        border-radius: 9999px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }

    .pill-accent {
        background: #eef2ff !important;
        color: #4f46e5 !important;
    }

    .pill-success {
        background: #d1fae5 !important;
        color: #047857 !important;
    }

    .pill-warning {
        background: #fef3c7 !important;
        color: #b45309 !important;
    }

    .pill-error {
        background: #fee2e2 !important;
        color: #b91c1c !important;
    }

    /* Feedback Boxes */
    .feedback-box {
        padding: 1rem 1.25rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
    }

    .feedback-success {
        background: #d1fae5 !important;
        border: 1px solid #6ee7b7 !important;
        color: #047857 !important;
    }

    .feedback-error {
        background: #fee2e2 !important;
        border: 1px solid #fca5a5 !important;
        color: #b91c1c !important;
    }

    .feedback-warning {
        background: #fef3c7 !important;
        border: 1px solid #fcd34d !important;
        color: #b45309 !important;
    }

    .feedback-info {
        background: #dbeafe !important;
        border: 1px solid #93c5fd !important;
        color: #1d4ed8 !important;
    }

    /* Exercise prompt */
    .exercise-prompt {
        font-size: 1.25rem !important;
        color: #0f172a !important;
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
    }

    .cloze-blank {
        display: inline-block !important;
        min-width: 100px !important;
        border-bottom: 2px solid #6366f1 !important;
        color: #6366f1 !important;
        text-align: center !important;
        margin: 0 4px !important;
        padding: 0 8px !important;
    }

    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%) !important;
        border: 1px solid #e0e7ff !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-bottom: 1.5rem !important;
    }

    .hero-title {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin-bottom: 0.5rem !important;
    }

    .hero-subtitle {
        font-size: 1rem !important;
        color: #64748b !important;
    }

    .emoji-flag {
        width: 52px;
        height: 52px;
        display: inline-block;
        margin-bottom: 16px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.25); }

    /* Focus states for accessibility */
    *:focus-visible {
        outline: 2px solid #6366f1 !important;
        outline-offset: 2px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
    """


def apply_theme():
    """Apply theme to app."""
    st.markdown(get_css(), unsafe_allow_html=True)


def _clean_html(markup: str) -> str:
    """Normalize HTML markup to avoid markdown code blocks."""
    return dedent(markup).strip()


def render_html(markup: str) -> None:
    """Render HTML with consistent formatting."""
    st.markdown(_clean_html(markup), unsafe_allow_html=True)


# ============================================
# COMPONENT FUNCTIONS
# ============================================

def render_hero(title: str, subtitle: str = "", pills: list = None) -> None:
    """Render a hero section."""
    pills_html = ""
    if pills:
        pills_html = '<div style="margin-bottom: 12px;">' + ' '.join(
            f'<span class="pill pill-accent">{p}</span>' for p in pills
        ) + '</div>'

    render_html(f"""
        <div class="hero">
            {pills_html}
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
    """)


def render_section_header(title: str, action_label: str = None, action_key: str = None) -> bool:
    """Render section header. Returns True if action clicked."""
    clicked = False
    if action_label and action_key:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            clicked = st.button(action_label, key=action_key)
    else:
        st.markdown(f"### {title}")
    return clicked


def render_metric_card(value: str, label: str, icon: str = "") -> str:
    """Return HTML for a metric card."""
    icon_html = f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''
    return _clean_html(f"""
        <div class="stat-card">
            {icon_html}
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
    """)


def render_metric_grid(metrics: list) -> None:
    """Render a grid of metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(render_metric_card(
                str(m.get("value", "0")),
                m.get("label", ""),
                m.get("icon", "")
            ), unsafe_allow_html=True)


def render_progress_bar(current: int, total: int, label: str = "") -> None:
    """Render a progress bar with optional label."""
    if label:
        st.caption(label)
    progress = current / total if total > 0 else 0
    st.progress(min(progress, 1.0))


def render_domain_coverage(domains: dict) -> None:
    """Render domain coverage visualization."""
    for domain, coverage in domains.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(min(coverage / 100, 1.0))
        with col2:
            st.caption(f"{domain}: {coverage:.0f}%")


def render_pill(text: str, variant: str = "accent") -> str:
    """Return HTML for a pill badge."""
    return f'<span class="pill pill-{variant}">{text}</span>'


def render_feedback(feedback_type: str, message: str, details: str = "") -> None:
    """Render a feedback box."""
    details_html = f'<div style="margin-top: 8px; opacity: 0.9;">{details}</div>' if details else ''
    render_html(f"""
        <div class="feedback-box feedback-{feedback_type}">
            <strong>{message}</strong>
            {details_html}
        </div>
    """)


def render_card(content: str, title: str = "") -> None:
    """Render a glass card."""
    title_html = f'<h4 style="margin-bottom: 12px; color: #ffffff;">{title}</h4>' if title else ''
    render_html(f"""
        <div class="glass-card">
            {title_html}
            <div style="color: #94a3b8;">{content}</div>
        </div>
    """)


def render_quick_actions(actions: list) -> None:
    """Render quick action buttons."""
    cols = st.columns(len(actions))
    for col, action in zip(cols, actions):
        with col:
            if st.button(
                f"{action.get('icon', '')} {action.get('label', '')}",
                key=action.get('key', action.get('label')),
                use_container_width=True,
                type=action.get('type', 'secondary')
            ):
                if action.get('callback'):
                    action['callback']()


def render_stat_card(value: str, label: str, icon: str = "") -> None:
    """Render a stat card directly."""
    st.markdown(render_metric_card(value, label, icon), unsafe_allow_html=True)


def render_action_card(title: str, subtitle: str, meta: str = "", primary: bool = False, icon: str = "") -> None:
    """Render an action card."""
    primary_class = "action-card-primary" if primary else ""
    icon_html = f'<span style="font-size: 28px; margin-right: 16px;">{icon}</span>' if icon else ''
    meta_html = f'<div style="font-size: 0.75rem; color: #64748b; margin-top: 8px;">{meta}</div>' if meta else ''

    render_html(f"""
        <div class="action-card {primary_class}">
            <div style="display: flex; align-items: flex-start;">
                {icon_html}
                <div>
                    <div class="action-card-title">{title}</div>
                    <div class="action-card-subtitle">{subtitle}</div>
                    {meta_html}
                </div>
            </div>
        </div>
    """)


def render_streak_badge(streak: int) -> None:
    """Render a streak badge."""
    if streak > 0:
        render_html(f"""
            <div style="display: inline-flex; align-items: center; gap: 10px;
                        background: rgba(245, 158, 11, 0.15); padding: 10px 18px;
                        border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.3);">
                <span style="font-size: 1.5rem;">🔥</span>
                <span style="font-size: 1.25rem; font-weight: 700; color: #fbbf24;">{streak}</span>
                <span style="color: #94a3b8; font-size: 0.9rem;">day{'s' if streak != 1 else ''}</span>
            </div>
        """)


def render_empty_state(message: str, icon: str = "📭") -> None:
    """Render an empty state."""
    render_html(f"""
        <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">{icon}</div>
            <p style="color: #64748b;">{message}</p>
        </div>
    """)


def render_loading_skeleton(height: str = "100px") -> None:
    """Render a loading skeleton."""
    render_html(f"""
        <div style="background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
                    background-size: 200% 100%; height: {height}; border-radius: 12px;
                    animation: shimmer 1.5s infinite;">
        </div>
        <style>
        @keyframes shimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        </style>
    """)


def render_error_state(message: str, retry_label: str = "Try again") -> bool:
    """Render error state. Returns True if retry clicked."""
    render_html(f"""
        <div style="text-align: center; padding: 2rem; background: rgba(239, 68, 68, 0.1);
                    border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.3);">
            <p style="color: #f87171; font-size: 1.1rem;"><strong>Something went wrong</strong></p>
            <p style="color: #f87171; opacity: 0.9;">{message}</p>
        </div>
    """)
    return st.button(retry_label, type="primary")


def render_profile_card(name: str, level: str, vocab_count: int, streak: int, is_active: bool = False) -> str:
    """Render a profile card."""
    border = 'border-color: #6366f1;' if is_active else ''
    badge = '<span class="pill pill-success">Active</span>' if is_active else ''

    return _clean_html(f"""
        <div class="glass-card" style="{border}">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <div>
                    <div style="font-weight: 600; font-size: 1.1rem; color: #ffffff;">{name}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Level: {level}</div>
                </div>
                {badge}
            </div>
            <div style="display: flex; gap: 24px;">
                <div>
                    <div style="font-weight: 700; font-size: 1.25rem; color: #ffffff;">{vocab_count}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Words</div>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.25rem; color: #fbbf24;">{streak}🔥</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Streak</div>
                </div>
            </div>
        </div>
    """)


def render_cloze_sentence(before: str, after: str, answer: str = "", show_answer: bool = False) -> None:
    """Render a cloze sentence with visible blank."""
    if show_answer:
        blank = f'<span class="cloze-blank" style="color: #047857;">{answer}</span>'
    else:
        blank = '<span class="cloze-blank">_____</span>'

    render_html(f"""
        <div class="exercise-prompt">
            {before}{blank}{after}
        </div>
    """)


def render_exercise_feedback(correct: bool, correct_answer: str, explanation: str = "", common_mistake: str = "") -> None:
    """Render exercise feedback."""
    if correct:
        render_html(f"""
            <div class="feedback-box feedback-success">
                <strong>✓ Correct!</strong>
                {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
            </div>
        """)
    else:
        mistake_html = f'<div style="margin-top: 8px; opacity: 0.85;"><em>Tip: {common_mistake}</em></div>' if common_mistake else ''
        render_html(f"""
            <div class="feedback-box feedback-error">
                <strong>✗ Not quite</strong>
                <div style="margin-top: 8px;">Correct answer: <strong>{correct_answer}</strong></div>
                {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
                {mistake_html}
            </div>
        """)


def get_design_system():
    """Return design tokens."""
    return {"colors": COLORS, "spacing": SPACING, "radii": RADII}


# ============================================
# EXERCISE HELPERS
# ============================================

def validate_exercise(exercise: dict) -> dict:
    """Validate exercise data."""
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


def normalize_spanish_answer(text: str, strict_accents: bool = False) -> str:
    """Normalize Spanish text for comparison."""
    import re
    text = text.strip().lower()
    text = ' '.join(text.split())
    text = re.sub(r'[^\w\sáéíóúüñ]', '', text)

    if not strict_accents:
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')

    return text


def check_answer(user_answer: str, correct_answers: list, strict_accents: bool = False) -> dict:
    """Check user's answer against correct answers."""
    user_norm = normalize_spanish_answer(user_answer, strict_accents=True)
    user_fold = normalize_spanish_answer(user_answer, strict_accents=False)

    for answer in correct_answers:
        ans_norm = normalize_spanish_answer(answer, strict_accents=True)
        ans_fold = normalize_spanish_answer(answer, strict_accents=False)

        if user_norm == ans_norm:
            return {"result": "correct", "matched": answer, "feedback": ""}

        if user_fold == ans_fold:
            return {"result": "almost", "matched": answer, "feedback": f"Watch the accents: {answer}"}

    return {"result": "incorrect", "matched": None, "feedback": f"Correct answer: {correct_answers[0]}"}
