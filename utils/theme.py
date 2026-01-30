"""Professional theme and styling for VivaLingo Pro."""
import streamlit as st

# Color palette - Modern, professional, accessible
COLORS = {
    "primary": "#2563eb",       # Royal blue
    "primary_dark": "#1d4ed8",  # Darker blue
    "secondary": "#0891b2",     # Cyan
    "accent": "#f59e0b",        # Amber
    "success": "#059669",       # Emerald
    "warning": "#d97706",       # Orange
    "error": "#dc2626",         # Red
    "surface": "#ffffff",       # White
    "surface_dim": "#f8fafc",   # Slate 50
    "surface_muted": "#f1f5f9", # Slate 100
    "border": "#e2e8f0",        # Slate 200
    "border_strong": "#cbd5e1", # Slate 300
    "text": "#0f172a",          # Slate 900
    "text_muted": "#475569",    # Slate 600
    "text_light": "#94a3b8",    # Slate 400
}


def get_css() -> str:
    """Get the complete CSS stylesheet."""
    return f"""
    <style>
    /* === IMPORTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* === ROOT VARIABLES === */
    :root {{
        --primary: {COLORS["primary"]};
        --primary-dark: {COLORS["primary_dark"]};
        --secondary: {COLORS["secondary"]};
        --accent: {COLORS["accent"]};
        --success: {COLORS["success"]};
        --warning: {COLORS["warning"]};
        --error: {COLORS["error"]};
        --surface: {COLORS["surface"]};
        --surface-dim: {COLORS["surface_dim"]};
        --surface-muted: {COLORS["surface_muted"]};
        --border: {COLORS["border"]};
        --border-strong: {COLORS["border_strong"]};
        --text: {COLORS["text"]};
        --text-muted: {COLORS["text_muted"]};
        --text-light: {COLORS["text_light"]};
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }}

    /* === GLOBAL STYLES === */
    .stApp {{
        background: linear-gradient(180deg, var(--surface-dim) 0%, var(--surface) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    .stApp > header {{
        background: transparent;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        color: var(--text);
        letter-spacing: -0.025em;
    }}

    h1 {{ font-size: 2rem; font-weight: 700; }}
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.25rem; }}

    p, li, span {{
        color: var(--text-muted);
        line-height: 1.6;
    }}

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {{
        background: var(--surface);
        border-right: 1px solid var(--border);
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}

    /* === HERO COMPONENT === */
    .hero {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: var(--radius-xl);
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
    }}

    .hero::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }}

    .hero h1 {{
        color: white;
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}

    .hero p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 0;
    }}

    .hero-pills {{
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }}

    .hero-pill {{
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
    }}

    /* === CARDS === */
    .card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}

    .card:hover {{
        box-shadow: var(--shadow-lg);
    }}

    .card-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }}

    .card-icon {{
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }}

    .card-title {{
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text);
        margin: 0;
    }}

    .card-muted {{
        background: var(--surface-muted);
        border: 1px dashed var(--border-strong);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
    }}

    /* === METRICS === */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
    }}

    .metric-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        text-align: center;
        transition: all 0.2s ease;
    }}

    .metric-card:hover {{
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
    }}

    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.2;
    }}

    .metric-label {{
        font-size: 0.875rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
    }}

    .metric-delta {{
        font-size: 0.75rem;
        margin-top: 0.5rem;
        padding: 0.125rem 0.5rem;
        border-radius: 9999px;
        display: inline-block;
    }}

    .metric-delta.positive {{
        background: rgba(5, 150, 105, 0.1);
        color: var(--success);
    }}

    .metric-delta.negative {{
        background: rgba(220, 38, 38, 0.1);
        color: var(--error);
    }}

    /* === PILLS & BADGES === */
    .pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        gap: 0.375rem;
    }}

    .pill-primary {{
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary);
    }}

    .pill-secondary {{
        background: rgba(8, 145, 178, 0.1);
        color: var(--secondary);
    }}

    .pill-success {{
        background: rgba(5, 150, 105, 0.1);
        color: var(--success);
    }}

    .pill-warning {{
        background: rgba(217, 119, 6, 0.1);
        color: var(--warning);
    }}

    .pill-error {{
        background: rgba(220, 38, 38, 0.1);
        color: var(--error);
    }}

    .pill-muted {{
        background: var(--surface-muted);
        color: var(--text-muted);
    }}

    /* === PROGRESS BARS === */
    .progress-container {{
        background: var(--surface-muted);
        border-radius: 9999px;
        height: 8px;
        overflow: hidden;
        position: relative;
    }}

    .progress-bar {{
        height: 100%;
        border-radius: 9999px;
        transition: width 0.5s ease;
    }}

    .progress-bar.primary {{
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    }}

    .progress-bar.success {{
        background: var(--success);
    }}

    .progress-bar.warning {{
        background: var(--warning);
    }}

    /* === DOMAIN COVERAGE === */
    .domain-item {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }}

    .domain-item:hover {{
        border-color: var(--primary);
        background: var(--surface-dim);
    }}

    .domain-name {{
        font-weight: 500;
        color: var(--text);
        min-width: 140px;
    }}

    .domain-progress {{
        flex: 1;
    }}

    .domain-percent {{
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--primary);
        min-width: 50px;
        text-align: right;
    }}

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        padding: 0.75rem 1.25rem;
        font-weight: 500;
        color: var(--text-muted);
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text);
        background: var(--surface-muted);
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
        background: transparent !important;
    }}

    /* === BUTTONS === */
    /* Primary button (default) */
    .stButton > button,
    .stButton > button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }}

    .stButton > button:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        filter: brightness(1.05);
    }}

    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Secondary button style */
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none;
    }}

    .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
        background: var(--background) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        transform: translateY(-1px);
    }}

    /* === SIDEBAR NAVIGATION BUTTONS === */
    /* Sidebar secondary buttons (unselected nav items) */
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"] {{
        background: transparent !important;
        color: #475569 !important;
        border: 1px solid transparent !important;
        text-align: left;
        justify-content: flex-start;
        padding: 0.5rem 0.75rem;
        font-weight: 500;
    }}

    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
        background: rgba(37, 99, 235, 0.08) !important;
        color: var(--primary) !important;
        border-color: transparent !important;
    }}

    /* Sidebar primary buttons (selected nav items) */
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        text-align: left;
        justify-content: flex-start;
        padding: 0.5rem 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
    }}

    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        filter: brightness(1.08);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }}

    /* Quick session button special styling */
    [data-testid="stSidebar"] .stButton:first-of-type > button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }}

    [data-testid="stSidebar"] .stButton:first-of-type > button[data-testid="stBaseButton-primary"]:hover {{
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }}

    /* === TEXT INPUTS === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}

    /* === SELECT BOXES === */
    .stSelectbox > div > div {{
        border-radius: var(--radius-md);
    }}

    /* === RADIO BUTTONS === */
    .stRadio > div {{
        gap: 0.5rem;
    }}

    .stRadio > div > label {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }}

    .stRadio > div > label:hover {{
        border-color: var(--primary);
        background: var(--surface-dim);
    }}

    /* === EXERCISE CARDS === */
    .exercise-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}

    .exercise-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }}

    .exercise-type {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--primary);
    }}

    .exercise-step {{
        background: var(--primary);
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    /* === FEEDBACK === */
    .feedback-box {{
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }}

    .feedback-success {{
        background: rgba(5, 150, 105, 0.1);
        border: 1px solid rgba(5, 150, 105, 0.2);
        color: var(--success);
    }}

    .feedback-error {{
        background: rgba(220, 38, 38, 0.1);
        border: 1px solid rgba(220, 38, 38, 0.2);
        color: var(--error);
    }}

    .feedback-info {{
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.2);
        color: var(--primary);
    }}

    /* === DIFF HIGHLIGHT === */
    .diff-added {{
        background: rgba(5, 150, 105, 0.2);
        color: var(--success);
        padding: 0.125rem 0.25rem;
        border-radius: 3px;
    }}

    .diff-removed {{
        background: rgba(220, 38, 38, 0.2);
        color: var(--error);
        padding: 0.125rem 0.25rem;
        border-radius: 3px;
        text-decoration: line-through;
    }}

    /* === VERB STUDIO OPTION === */
    .verb-option {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }}

    .verb-option:hover {{
        border-color: var(--primary);
        background: var(--surface-dim);
    }}

    .verb-option.selected {{
        border-color: var(--primary);
        background: rgba(37, 99, 235, 0.05);
    }}

    .verb-name {{
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.5rem;
    }}

    .verb-meta {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }}

    .verb-note {{
        font-size: 0.875rem;
        color: var(--text-muted);
    }}

    /* === CONVERSATION === */
    .chat-message {{
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease;
    }}

    .chat-message.user {{
        flex-direction: row-reverse;
    }}

    .chat-avatar {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--surface-muted);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }}

    .chat-message.user .chat-avatar {{
        background: var(--primary);
        color: white;
    }}

    .chat-bubble {{
        max-width: 70%;
        padding: 0.875rem 1.125rem;
        border-radius: var(--radius-lg);
        background: var(--surface-muted);
        color: var(--text);
    }}

    .chat-message.user .chat-bubble {{
        background: var(--primary);
        color: white;
    }}

    /* === QUICK ACTIONS === */
    .quick-actions {{
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin: 1.5rem 0;
    }}

    .quick-action {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        color: var(--text);
    }}

    .quick-action:hover {{
        border-color: var(--primary);
        background: var(--surface-dim);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }}

    .quick-action-icon {{
        font-size: 1.5rem;
    }}

    .quick-action-text {{
        font-weight: 500;
    }}

    .quick-action-desc {{
        font-size: 0.75rem;
        color: var(--text-muted);
    }}

    /* === ANIMATIONS === */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    .animate-fade-in {{
        animation: fadeIn 0.3s ease;
    }}

    .animate-pulse {{
        animation: pulse 2s infinite;
    }}

    /* === DATAFRAMES === */
    .stDataFrame {{
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        overflow: hidden;
    }}

    /* === EXPANDERS === */
    .streamlit-expanderHeader {{
        background: var(--surface-dim);
        border-radius: var(--radius-md);
        font-weight: 500;
    }}

    /* === DIVIDERS === */
    hr {{
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }}

    /* === SECTION HEADERS === */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
    }}

    .section-header h2 {{
        margin: 0;
    }}

    .section-line {{
        flex: 1;
        height: 1px;
        background: var(--border);
    }}

    /* === STATUS INDICATORS === */
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }}

    .status-dot.active {{
        background: var(--success);
    }}

    .status-dot.pending {{
        background: var(--warning);
    }}

    .status-dot.inactive {{
        background: var(--text-light);
    }}

    /* === HIDE STREAMLIT ELEMENTS === */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    </style>
    """


def apply_theme() -> None:
    """Apply the theme to the Streamlit app."""
    st.set_page_config(
        page_title="VivaLingo Pro",
        page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(get_css(), unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, pills: list[str] = None) -> None:
    """Render a hero section."""
    pills_html = ""
    if pills:
        pills_html = '<div class="hero-pills">' + ''.join(
            f'<span class="hero-pill">{pill}</span>' for pill in pills
        ) + '</div>'

    st.markdown(f"""
    <div class="hero">
        {pills_html}
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, delta: str = None, delta_type: str = "positive") -> str:
    """Return HTML for a metric card."""
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_type}">{delta}</div>'

    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """


def render_metric_grid(metrics: list[dict]) -> None:
    """Render a grid of metric cards."""
    cards_html = ''.join(
        render_metric_card(
            m["value"],
            m["label"],
            m.get("delta"),
            m.get("delta_type", "positive")
        )
        for m in metrics
    )
    st.markdown(f'<div class="metric-grid">{cards_html}</div>', unsafe_allow_html=True)


def render_progress_bar(value: float, max_value: float = 100, variant: str = "primary") -> str:
    """Return HTML for a progress bar."""
    percent = min(100, (value / max_value) * 100) if max_value > 0 else 0
    return f"""
    <div class="progress-container">
        <div class="progress-bar {variant}" style="width: {percent}%"></div>
    </div>
    """


def render_domain_coverage(domains: dict) -> None:
    """Render domain coverage visualization."""
    total = sum(d.get("exposure_count", 0) for d in domains.values()) or 1

    items_html = ""
    for name, data in sorted(domains.items(), key=lambda x: x[1].get("exposure_count", 0), reverse=True):
        count = data.get("exposure_count", 0)
        percent = (count / total) * 100
        items_html += f"""
        <div class="domain-item">
            <span class="domain-name">{name}</span>
            <div class="domain-progress">
                {render_progress_bar(percent)}
            </div>
            <span class="domain-percent">{percent:.0f}%</span>
        </div>
        """

    st.markdown(items_html, unsafe_allow_html=True)


def render_pill(text: str, variant: str = "primary") -> str:
    """Return HTML for a pill badge."""
    return f'<span class="pill pill-{variant}">{text}</span>'


def render_feedback(message: str, feedback_type: str = "info") -> None:
    """Render a feedback box."""
    st.markdown(f"""
    <div class="feedback-box feedback-{feedback_type}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_card(title: str, content: str, icon: str = None) -> None:
    """Render a card component."""
    icon_html = ""
    if icon:
        icon_html = f'<div class="card-icon">{icon}</div>'

    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            {icon_html}
            <h3 class="card-title">{title}</h3>
        </div>
        <div class="card-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str) -> None:
    """Render a section header with line."""
    st.markdown(f"""
    <div class="section-header">
        <h2>{title}</h2>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)


def render_quick_actions(actions: list[dict]) -> None:
    """Render quick action buttons."""
    actions_html = ""
    for action in actions:
        actions_html += f"""
        <div class="quick-action" onclick="window.location.href='{action.get('href', '#')}'">
            <span class="quick-action-icon">{action['icon']}</span>
            <div>
                <div class="quick-action-text">{action['text']}</div>
                <div class="quick-action-desc">{action.get('desc', '')}</div>
            </div>
        </div>
        """

    st.markdown(f'<div class="quick-actions">{actions_html}</div>', unsafe_allow_html=True)
