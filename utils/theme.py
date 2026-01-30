"""
Futuristic 2040-style theme for VivaLingo Pro.
Glass morphism, neon accents, animated gradients, and modern aesthetics.
"""
import streamlit as st

# Color palette - Futuristic neon with deep backgrounds
COLORS = {
    # Primary gradient colors
    "primary": "#6366f1",           # Indigo
    "primary_light": "#818cf8",     # Light indigo
    "primary_dark": "#4f46e5",      # Dark indigo
    "secondary": "#06b6d4",         # Cyan
    "secondary_light": "#22d3ee",   # Light cyan
    "accent": "#f472b6",            # Pink
    "accent_alt": "#a855f7",        # Purple

    # Status colors
    "success": "#10b981",           # Emerald
    "success_light": "#34d399",     # Light emerald
    "warning": "#f59e0b",           # Amber
    "error": "#ef4444",             # Red
    "error_light": "#f87171",       # Light red

    # Backgrounds - Dark theme with depth
    "bg_primary": "#0a0a0f",        # Deep dark
    "bg_secondary": "#12121a",      # Card background
    "bg_tertiary": "#1a1a25",       # Elevated surface
    "bg_glass": "rgba(255, 255, 255, 0.03)",  # Glass effect

    # Text colors
    "text_primary": "#f8fafc",      # Pure white-ish
    "text_secondary": "#94a3b8",    # Muted text
    "text_muted": "#64748b",        # Very muted

    # Border and dividers
    "border": "rgba(255, 255, 255, 0.08)",
    "border_glow": "rgba(99, 102, 241, 0.3)",
    "divider": "rgba(255, 255, 255, 0.05)",
}


def get_css() -> str:
    """Get the complete CSS stylesheet with futuristic 2040 aesthetics."""
    return """
    <style>
    /* === IMPORTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* === ROOT VARIABLES === */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #06b6d4;
        --secondary-light: #22d3ee;
        --accent: #f472b6;
        --accent-alt: #a855f7;

        --success: #10b981;
        --success-light: #34d399;
        --warning: #f59e0b;
        --error: #ef4444;

        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a25;
        --bg-glass: rgba(255, 255, 255, 0.03);

        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;

        --border: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(99, 102, 241, 0.3);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-2xl: 32px;

        --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4), 0 0 1px rgba(255, 255, 255, 0.1);
        --shadow-elevated: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 1px rgba(255, 255, 255, 0.1);
        --shadow-neon: 0 0 20px rgba(99, 102, 241, 0.4), 0 0 40px rgba(99, 102, 241, 0.2);
    }

    /* === GLOBAL STYLES === */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, #0d0d14 50%, var(--bg-primary) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Animated background gradient */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(ellipse 80% 50% at 20% 40%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse 60% 40% at 80% 20%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse 50% 50% at 50% 80%, rgba(168, 85, 247, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    .stApp > header {
        background: transparent !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: var(--text-primary) !important;
        letter-spacing: -0.03em;
    }

    h1 {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary-light) 50%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    h2 { font-size: 1.75rem !important; }
    h3 { font-size: 1.25rem !important; }

    p, li, span {
        color: var(--text-secondary) !important;
        line-height: 1.7;
    }

    /* Form labels should be clearly visible */
    label, .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* Make sure label text is visible */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #94a3b8 !important;
    }

    /* === SIDEBAR - Glass Morphism === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(18, 18, 26, 0.95) 0%, rgba(10, 10, 15, 0.98) 100%) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(20px);
    }

    section[data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%);
        pointer-events: none;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.75rem;
    }

    /* Sidebar divider */
    section[data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 1rem 0;
    }

    /* === HERO COMPONENT - Futuristic === */
    .hero {
        background: linear-gradient(135deg,
            rgba(99, 102, 241, 0.15) 0%,
            rgba(6, 182, 212, 0.1) 50%,
            rgba(168, 85, 247, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-2xl);
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-glow);
    }

    .hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.02) 100%),
            radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.2) 0%, transparent 40%),
            radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.15) 0%, transparent 40%);
        pointer-events: none;
    }

    .hero::after {
        content: '';
        position: absolute;
        top: -2px;
        left: 20%;
        right: 20%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
        border-radius: 2px;
    }

    .hero h1 {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.75rem !important;
        position: relative;
        z-index: 1;
        -webkit-text-fill-color: var(--text-primary);
        background: none;
    }

    .hero p {
        color: var(--text-secondary) !important;
        font-size: 1.05rem !important;
        margin: 0 !important;
        position: relative;
        z-index: 1;
        max-width: 600px;
    }

    .hero-pills {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }

    .hero-pill {
        background: rgba(255, 255, 255, 0.08) !important;
        color: var(--text-primary) !important;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .hero-pill:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: var(--primary);
        transform: translateY(-1px);
    }

    /* === CARDS - Glass Morphism === */
    .card {
        background: linear-gradient(135deg, rgba(26, 26, 37, 0.8) 0%, rgba(18, 18, 26, 0.9) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.75rem;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-card);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    }

    .card:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-elevated), var(--shadow-glow);
        transform: translateY(-4px);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-alt) 100%);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        position: relative;
    }

    .card-icon::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        z-index: -1;
        opacity: 0.5;
        filter: blur(8px);
    }

    .card-title {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }

    .card-muted {
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
    }

    /* === METRICS - Futuristic Dashboard === */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.25rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(26, 26, 37, 0.6) 0%, rgba(18, 18, 26, 0.8) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-neon);
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--text-muted) !important;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }

    .metric-delta {
        font-size: 0.75rem;
        margin-top: 0.75rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-weight: 600;
    }

    .metric-delta.positive {
        background: rgba(16, 185, 129, 0.15);
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .metric-delta.negative {
        background: rgba(239, 68, 68, 0.15);
        color: var(--error-light) !important;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* === PILLS & BADGES === */
    .pill {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        gap: 0.375rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .pill-primary {
        background: rgba(99, 102, 241, 0.15);
        color: var(--primary-light) !important;
        border-color: rgba(99, 102, 241, 0.3);
    }

    .pill-secondary {
        background: rgba(6, 182, 212, 0.15);
        color: var(--secondary-light) !important;
        border-color: rgba(6, 182, 212, 0.3);
    }

    .pill-success {
        background: rgba(16, 185, 129, 0.15);
        color: var(--success-light) !important;
        border-color: rgba(16, 185, 129, 0.3);
    }

    .pill-warning {
        background: rgba(245, 158, 11, 0.15);
        color: var(--warning) !important;
        border-color: rgba(245, 158, 11, 0.3);
    }

    .pill-error {
        background: rgba(239, 68, 68, 0.15);
        color: var(--error-light) !important;
        border-color: rgba(239, 68, 68, 0.3);
    }

    .pill-muted {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-muted) !important;
        border-color: var(--border);
    }

    /* === PROGRESS BARS - Animated Neon === */
    .progress-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 9999px;
        height: 8px;
        overflow: hidden;
        position: relative;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .progress-bar {
        height: 100%;
        border-radius: 9999px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }

    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 2s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .progress-bar.primary {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.5);
    }

    .progress-bar.success {
        background: linear-gradient(90deg, var(--success) 0%, var(--success-light) 100%);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.5);
    }

    .progress-bar.warning {
        background: linear-gradient(90deg, var(--warning) 0%, #fbbf24 100%);
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
    }

    /* === DOMAIN COVERAGE === */
    .domain-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.25rem;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }

    .domain-item:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
        transform: translateX(4px);
    }

    .domain-name {
        font-weight: 600;
        color: var(--text-primary) !important;
        min-width: 140px;
    }

    .domain-progress {
        flex: 1;
    }

    .domain-percent {
        font-size: 0.875rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        min-width: 50px;
        text-align: right;
    }

    /* === TABS - Modern === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        padding: 0.875rem 1.5rem;
        font-weight: 600;
        color: var(--text-muted) !important;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: rgba(255, 255, 255, 0.02);
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary-light) !important;
        border-bottom-color: var(--primary) !important;
        background: rgba(99, 102, 241, 0.05) !important;
    }

    /* === BUTTONS - Futuristic === */
    .stButton > button,
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 600 !important;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button p,
    .stButton > button span,
    button[data-testid="stBaseButton-primary"] p,
    button[data-testid="stBaseButton-primary"] span {
        color: white !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4), var(--shadow-neon);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary button */
    .stButton > button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none;
    }

    .stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: var(--primary) !important;
        color: var(--primary-light) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }

    /* === SIDEBAR NAVIGATION === */
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 1px solid transparent !important;
        text-align: left;
        justify-content: flex-start;
        padding: 0.75rem 1rem;
        font-weight: 500;
        border-radius: var(--radius-md);
    }

    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        color: var(--primary-light) !important;
        border-color: transparent !important;
        transform: translateX(4px);
    }

    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        text-align: left;
        justify-content: flex-start;
        padding: 0.75rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    }

    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }

    /* Quick session button - Neon accent */
    [data-testid="stSidebar"] .stButton:first-of-type > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-alt) 100%) !important;
        box-shadow: 0 4px 16px rgba(244, 114, 182, 0.3);
    }

    [data-testid="stSidebar"] .stButton:first-of-type > button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 8px 24px rgba(244, 114, 182, 0.4), 0 0 30px rgba(244, 114, 182, 0.3);
    }

    /* === TEXT INPUTS - Glass Style with high contrast === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(18, 18, 26, 0.95) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md);
        padding: 0.875rem 1.125rem;
        font-size: 0.95rem;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        transition: all 0.3s ease;
        caret-color: #f8fafc !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15), var(--shadow-glow);
        background: rgba(26, 26, 37, 0.98) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* Ensure input text is always visible */
    .stTextInput input[type="text"],
    .stTextInput input[type="number"],
    .stTextInput input[type="email"],
    .stTextInput input[type="password"] {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    /* === SELECT BOXES === */
    .stSelectbox > div > div {
        background: rgba(18, 18, 26, 0.95) !important;
        border-radius: var(--radius-md);
        border: 1px solid var(--border) !important;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--primary) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(18, 18, 26, 0.95) !important;
        color: #f8fafc !important;
    }

    .stSelectbox [data-baseweb="select"] span {
        color: #f8fafc !important;
    }

    /* === RADIO BUTTONS === */
    .stRadio > div {
        gap: 0.75rem;
    }

    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .stRadio > div > label:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
    }

    /* === EXERCISE CARDS === */
    .exercise-card {
        background: linear-gradient(135deg, rgba(26, 26, 37, 0.8) 0%, rgba(18, 18, 26, 0.9) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(20px);
    }

    .exercise-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.25rem;
    }

    .exercise-type {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--primary-light) !important;
        background: rgba(99, 102, 241, 0.1);
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }

    .exercise-step {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-alt) 100%);
        color: white !important;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
    }

    /* === FEEDBACK BOXES === */
    .feedback-box {
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        margin: 1.25rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid;
    }

    .feedback-success {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: var(--success-light) !important;
    }

    .feedback-error {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.3);
        color: var(--error-light) !important;
    }

    .feedback-info {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
        color: var(--primary-light) !important;
    }

    /* === DIFF HIGHLIGHTING === */
    .diff-added {
        background: rgba(16, 185, 129, 0.2);
        color: var(--success-light) !important;
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .diff-removed {
        background: rgba(239, 68, 68, 0.2);
        color: var(--error-light) !important;
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
        text-decoration: line-through;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* === VERB STUDIO OPTIONS === */
    .verb-option {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .verb-option:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
        transform: translateX(4px);
    }

    .verb-option.selected {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.1);
        box-shadow: var(--shadow-neon);
    }

    .verb-name {
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }

    .verb-meta {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }

    .verb-note {
        font-size: 0.875rem;
        color: var(--text-muted) !important;
    }

    /* === CONVERSATION - Chat Interface === */
    .chat-message {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.25rem;
        animation: messageSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .chat-message.user {
        flex-direction: row-reverse;
    }

    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.125rem;
        flex-shrink: 0;
        border: 1px solid var(--border);
    }

    .chat-message.user .chat-avatar {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-alt) 100%);
        color: white !important;
        border: none;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.3);
    }

    .chat-bubble {
        max-width: 70%;
        padding: 1rem 1.25rem;
        border-radius: var(--radius-xl);
        background: rgba(255, 255, 255, 0.03);
        color: var(--text-primary) !important;
        border: 1px solid var(--border);
    }

    .chat-message.user .chat-bubble {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        border: none;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    }

    /* === QUICK ACTIONS === */
    .quick-actions {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1.5rem 0;
    }

    .quick-action {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.25rem 1.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        color: var(--text-primary) !important;
    }

    .quick-action:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow);
    }

    .quick-action-icon {
        font-size: 1.75rem;
        filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
    }

    .quick-action-text {
        font-weight: 600;
        color: var(--text-primary) !important;
    }

    .quick-action-desc {
        font-size: 0.8rem;
        color: var(--text-muted) !important;
        margin-top: 0.25rem;
    }

    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.5); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .animate-fade-in {
        animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .animate-pulse {
        animation: pulse 2s infinite;
    }

    .animate-glow {
        animation: glow 3s infinite;
    }

    .animate-float {
        animation: float 4s ease-in-out infinite;
    }

    /* === DATAFRAMES === */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }

    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: var(--radius-md);
        font-weight: 600;
        color: var(--text-primary) !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(99, 102, 241, 0.05) !important;
    }

    /* === DIVIDERS === */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 2rem 0;
    }

    /* === SECTION HEADERS === */
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 2.5rem 0 1.25rem 0;
    }

    .section-header h2 {
        margin: 0 !important;
        white-space: nowrap;
    }

    .section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border), transparent);
    }

    /* === STATUS INDICATORS === */
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
        box-shadow: 0 0 8px currentColor;
    }

    .status-dot.active {
        background: var(--success);
        box-shadow: 0 0 12px var(--success);
    }

    .status-dot.pending {
        background: var(--warning);
        box-shadow: 0 0 12px var(--warning);
    }

    .status-dot.inactive {
        background: var(--text-muted);
    }

    /* === PROFILE SELECTOR - Futuristic === */
    .profile-card {
        background: linear-gradient(135deg, rgba(26, 26, 37, 0.8) 0%, rgba(18, 18, 26, 0.9) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .profile-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-neon);
        transform: translateY(-4px);
    }

    .profile-card.active {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.1);
        box-shadow: var(--shadow-neon);
    }

    .profile-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-alt) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        margin: 0 auto 1rem;
        box-shadow: 0 0 24px rgba(99, 102, 241, 0.4);
    }

    .profile-name {
        font-weight: 700;
        color: var(--text-primary) !important;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }

    .profile-stats {
        font-size: 0.8rem;
        color: var(--text-muted) !important;
    }

    /* === STREAK BADGE - Neon Effect === */
    .streak-badge {
        background: linear-gradient(135deg, rgba(244, 114, 182, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(244, 114, 182, 0.3);
        border-radius: var(--radius-lg);
        padding: 0.75rem 1rem;
        text-align: center;
        margin: 0.75rem 0;
    }

    .streak-badge .streak-number {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-alt) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* === HIDE STREAMLIT ELEMENTS === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* === STREAMLIT METRIC STYLING === */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(26, 26, 37, 0.6) 0%, rgba(18, 18, 26, 0.8) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.25rem !important;
        backdrop-filter: blur(20px);
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-neon);
    }

    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* Warning/Info boxes */
    .stAlert {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
    }

    /* Progress bar streamlit native */
    .stProgress > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 9999px;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
        border-radius: 9999px;
    }
    </style>
    """


def apply_theme() -> None:
    """Apply the theme to the Streamlit app."""
    st.set_page_config(
        page_title="VivaLingo Pro",
        page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(get_css(), unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, pills: list[str] = None) -> None:
    """Render a hero section with futuristic styling."""
    pills_html = ""
    if pills:
        pills_html = '<div class="hero-pills">' + ''.join(
            f'<span class="hero-pill">{pill}</span>' for pill in pills
        ) + '</div>'

    st.markdown(f"""
    <div class="hero animate-fade-in">
        {pills_html}
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, delta: str = None, delta_type: str = "positive") -> str:
    """Return HTML for a metric card."""
    delta_html = ""
    if delta:
        icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="metric-delta {delta_type}">{icon} {delta}</div>'

    return f"""
    <div class="metric-card animate-fade-in">
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
    """Return HTML for a progress bar with animation."""
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
    <div class="feedback-box feedback-{feedback_type} animate-fade-in">
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_card(title: str, content: str, icon: str = None) -> None:
    """Render a card component."""
    icon_html = ""
    if icon:
        icon_html = f'<div class="card-icon">{icon}</div>'

    st.markdown(f"""
    <div class="card animate-fade-in">
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


def render_profile_card(name: str, level: str, vocab_count: int, streak: int, is_active: bool = False) -> str:
    """Render a profile card."""
    active_class = "active" if is_active else ""
    initial = name[0].upper() if name else "?"

    return f"""
    <div class="profile-card {active_class}">
        <div class="profile-avatar">{initial}</div>
        <div class="profile-name">{name or 'New Profile'}</div>
        <div class="profile-stats">
            Level {level} • {vocab_count} words • {streak} day streak
        </div>
    </div>
    """


def render_streak_badge(streak: int) -> None:
    """Render a streak badge with neon effect."""
    flame = "🔥" if streak > 0 else "💤"
    st.markdown(f"""
    <div class="streak-badge">
        <span style="font-size: 1.5rem;">{flame}</span>
        <span class="streak-number">{streak}</span>
        <span style="color: var(--text-secondary); font-size: 0.85rem;"> day{'s' if streak != 1 else ''} streak</span>
    </div>
    """, unsafe_allow_html=True)
