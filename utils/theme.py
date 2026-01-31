"""
Modern iOS-style design system with glassmorphism, vibrant gradients, and 2026 aesthetics.
"""
import streamlit as st


# Color palette for programmatic access
COLORS = {
    "primary": "#6366f1",
    "primary_light": "#818cf8",
    "secondary": "#ec4899",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "bg_dark": "#0a0a0f",
    "bg_card": "rgba(255, 255, 255, 0.05)",
    "text_primary": "#ffffff",
    "text_secondary": "#a1a1aa",
}


def get_css() -> str:
    """Return stunning iOS-style CSS with glassmorphism and modern aesthetics."""
    return """
    <style>
    /* ============================================
       2026 iOS-STYLE DESIGN SYSTEM
       Glassmorphism • Vibrant Gradients • Fluid Motion
       ============================================ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        /* Premium Color Palette */
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-glow: rgba(99, 102, 241, 0.4);
        --secondary: #ec4899;
        --secondary-light: #f472b6;
        --accent: #06b6d4;
        --accent-light: #22d3ee;

        /* Success/Warning/Error with vibrancy */
        --success: #10b981;
        --success-light: #34d399;
        --success-glow: rgba(16, 185, 129, 0.3);
        --warning: #f59e0b;
        --warning-light: #fbbf24;
        --error: #ef4444;
        --error-light: #f87171;
        --info: #3b82f6;

        /* Dark backgrounds with depth */
        --bg-base: #0a0a0f;
        --bg-elevated: #12121a;
        --bg-card: rgba(255, 255, 255, 0.03);
        --bg-glass: rgba(255, 255, 255, 0.05);
        --bg-hover: rgba(255, 255, 255, 0.08);
        --bg-active: rgba(99, 102, 241, 0.15);

        /* Text with perfect contrast */
        --text-primary: #ffffff;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --text-hint: #52525b;

        /* Borders and dividers */
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-medium: rgba(255, 255, 255, 0.1);
        --border-focus: rgba(99, 102, 241, 0.5);

        /* Gradients */
        --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        --gradient-success: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        --gradient-card: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        --gradient-shine: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);

        /* Typography */
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;

        /* Spacing */
        --space-xs: 4px;
        --space-sm: 8px;
        --space-md: 16px;
        --space-lg: 24px;
        --space-xl: 32px;
        --space-2xl: 48px;

        /* Radii */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-2xl: 24px;
        --radius-full: 9999px;

        /* Shadows */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 40px var(--primary-glow);
        --shadow-inner: inset 0 1px 0 rgba(255, 255, 255, 0.05);

        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    /* ============================================
       BASE STYLES
       ============================================ */
    .stApp {
        background: var(--bg-base) !important;
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(6, 182, 212, 0.05) 0%, transparent 70%) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        min-height: 100vh;
    }

    /* Hide default Streamlit header/footer */
    header[data-testid="stHeader"],
    footer,
    #MainMenu {
        display: none !important;
    }

    /* Main content */
    .main .block-container {
        padding: var(--space-lg) var(--space-xl) !important;
        max-width: 1100px !important;
    }

    /* ============================================
       TYPOGRAPHY - iOS Style
       ============================================ */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }

    h1, .stMarkdown h1 {
        font-size: 2.5rem !important;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2, .stMarkdown h2 { font-size: 1.75rem !important; }
    h3, .stMarkdown h3 { font-size: 1.25rem !important; }

    p, .stMarkdown p {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
    }

    strong, b {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ============================================
       SIDEBAR - Frosted Glass
       ============================================ */
    [data-testid="stSidebar"] {
        background: rgba(18, 18, 26, 0.95) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: var(--space-md) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--text-muted) !important;
        margin: var(--space-lg) 0 var(--space-sm) 0 !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        background: none !important;
    }

    /* ============================================
       BUTTONS - iOS Style with Gradients
       ============================================ */

    /* Primary Button */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 14px 28px !important;
        min-height: 50px !important;
        box-shadow: var(--shadow-md), 0 0 20px var(--primary-glow) !important;
        transition: all var(--transition-base) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton > button[kind="primary"]::before,
    .stButton > button[data-testid="baseButton-primary"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 50% !important;
        background: linear-gradient(to bottom, rgba(255,255,255,0.2), transparent) !important;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0 !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: var(--shadow-lg), 0 0 40px var(--primary-glow) !important;
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="baseButton-primary"]:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* Secondary Button - Glass Effect */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([kind]) {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 14px 24px !important;
        min-height: 50px !important;
        transition: all var(--transition-base) !important;
        box-shadow: var(--shadow-inner) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:not([kind]):hover {
        background: var(--bg-hover) !important;
        border-color: var(--primary) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ============================================
       FORM INPUTS - Modern Glass
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 1rem !important;
        padding: 14px 16px !important;
        min-height: 50px !important;
        transition: all var(--transition-fast) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow), var(--shadow-glow) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-hint) !important;
    }

    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stRadio > label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        margin-bottom: var(--space-sm) !important;
    }

    /* ============================================
       RADIO BUTTONS - iOS Segmented Control Style
       ============================================ */
    .stRadio > div {
        gap: var(--space-sm) !important;
        flex-wrap: wrap !important;
    }

    .stRadio > div > label {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 20px !important;
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all var(--transition-fast) !important;
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
    }

    .stRadio > div > label:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-medium) !important;
        color: var(--text-primary) !important;
    }

    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label:has(input:checked) {
        background: var(--bg-active) !important;
        border-color: var(--primary) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 0 20px var(--primary-glow) !important;
    }

    /* ============================================
       SELECT / DROPDOWN - Modern Style
       ============================================ */
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
    }

    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
    }

    /* Dropdown popover */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"] {
        background: rgba(18, 18, 26, 0.98) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-lg) !important;
        overflow: hidden !important;
    }

    [data-baseweb="menu"] li,
    div[role="option"] {
        color: var(--text-primary) !important;
        background: transparent !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        transition: background var(--transition-fast) !important;
    }

    [data-baseweb="menu"] li:hover,
    div[role="option"]:hover {
        background: var(--bg-hover) !important;
    }

    [data-baseweb="menu"] li[aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background: var(--bg-active) !important;
    }

    /* ============================================
       MULTISELECT - Pills Style
       ============================================ */
    .stMultiSelect > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: var(--gradient-primary) !important;
        border: none !important;
        color: white !important;
        border-radius: var(--radius-full) !important;
        font-weight: 500 !important;
    }

    /* ============================================
       PROGRESS BAR - Animated Gradient
       ============================================ */
    .stProgress > div > div {
        background: var(--bg-glass) !important;
        border-radius: var(--radius-full) !important;
        height: 10px !important;
        overflow: hidden !important;
    }

    .stProgress > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: var(--radius-full) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stProgress > div > div > div::after {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        animation: shimmer 2s infinite !important;
    }

    @keyframes shimmer {
        100% { left: 100%; }
    }

    /* ============================================
       CARDS - Glassmorphism
       ============================================ */
    .glass-card {
        background: var(--gradient-card) !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: var(--space-lg) !important;
        box-shadow: var(--shadow-md), var(--shadow-inner) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all var(--transition-base) !important;
    }

    .glass-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent) !important;
    }

    .glass-card:hover {
        border-color: var(--border-medium) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    .card {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: var(--space-lg) !important;
        margin-bottom: var(--space-md) !important;
        transition: all var(--transition-base) !important;
    }

    .card:hover {
        border-color: var(--border-medium) !important;
    }

    /* ============================================
       HERO SECTION - Premium Header
       ============================================ */
    .hero {
        background: var(--gradient-card) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-2xl) !important;
        padding: var(--space-2xl) var(--space-xl) !important;
        margin-bottom: var(--space-xl) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .hero::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        left: -50% !important;
        width: 200% !important;
        height: 200% !important;
        background: radial-gradient(circle at 30% 30%, var(--primary-glow) 0%, transparent 50%) !important;
        opacity: 0.5 !important;
        animation: float 8s ease-in-out infinite !important;
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(20px, 20px) rotate(5deg); }
    }

    .hero-content {
        position: relative !important;
        z-index: 1 !important;
    }

    .hero-title {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: var(--gradient-primary) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: var(--space-sm) !important;
        letter-spacing: -0.02em !important;
    }

    .hero-subtitle {
        color: var(--text-secondary) !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        max-width: 600px !important;
    }

    .hero-pills {
        display: flex !important;
        gap: var(--space-sm) !important;
        flex-wrap: wrap !important;
        margin-bottom: var(--space-md) !important;
    }

    .hero-pill {
        background: var(--bg-active) !important;
        color: var(--primary-light) !important;
        padding: 6px 14px !important;
        border-radius: var(--radius-full) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
    }

    /* ============================================
       EXERCISE COMPONENTS
       ============================================ */
    .exercise-prompt {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-lg) !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        line-height: 1.6 !important;
        margin-bottom: var(--space-md) !important;
    }

    .exercise-type {
        display: inline-flex !important;
        align-items: center !important;
        background: var(--gradient-primary) !important;
        color: white !important;
        padding: 6px 14px !important;
        border-radius: var(--radius-full) !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: var(--space-md) !important;
    }

    /* ============================================
       FEEDBACK BOXES - Vibrant Colors
       ============================================ */
    .feedback-box {
        padding: var(--space-md) var(--space-lg) !important;
        border-radius: var(--radius-lg) !important;
        margin: var(--space-md) 0 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .feedback-success {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        color: var(--success-light) !important;
    }

    .feedback-success::before {
        content: '' !important;
        position: absolute !important;
        left: 0 !important;
        top: 0 !important;
        bottom: 0 !important;
        width: 4px !important;
        background: var(--gradient-success) !important;
    }

    .feedback-error {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: var(--error-light) !important;
    }

    .feedback-error::before {
        content: '' !important;
        position: absolute !important;
        left: 0 !important;
        top: 0 !important;
        bottom: 0 !important;
        width: 4px !important;
        background: linear-gradient(to bottom, var(--error), var(--secondary)) !important;
    }

    .feedback-warning {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        color: var(--warning-light) !important;
    }

    .feedback-info {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #60a5fa !important;
    }

    /* ============================================
       METRICS - Glowing Cards
       ============================================ */
    .metric-card {
        background: var(--gradient-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: var(--space-lg) !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all var(--transition-base) !important;
    }

    .metric-card:hover {
        border-color: var(--primary) !important;
        box-shadow: 0 0 30px var(--primary-glow) !important;
        transform: translateY(-4px) !important;
    }

    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: var(--gradient-primary) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        line-height: 1 !important;
        margin-bottom: var(--space-xs) !important;
    }

    .metric-label {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* ============================================
       PILLS / BADGES
       ============================================ */
    .pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        padding: 6px 14px !important;
        border-radius: var(--radius-full) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        transition: all var(--transition-fast) !important;
    }

    .pill-primary {
        background: var(--bg-active) !important;
        color: var(--primary-light) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
    }

    .pill-success {
        background: rgba(16, 185, 129, 0.15) !important;
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }

    .pill-warning {
        background: rgba(245, 158, 11, 0.15) !important;
        color: var(--warning-light) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
    }

    .pill-error {
        background: rgba(239, 68, 68, 0.15) !important;
        color: var(--error-light) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }

    /* ============================================
       ALERTS - Streamlit Native
       ============================================ */
    .stAlert {
        border-radius: var(--radius-lg) !important;
    }

    div[data-testid="stAlert"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
    }

    /* ============================================
       EXPANDER - Accordion Style
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        padding: var(--space-md) !important;
        transition: all var(--transition-fast) !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-medium) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
        padding: var(--space-md) !important;
    }

    /* ============================================
       TABS - iOS Segmented Control
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-glass) !important;
        border-radius: var(--radius-lg) !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid var(--border-subtle) !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all var(--transition-fast) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: var(--bg-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-active) !important;
        color: var(--primary-light) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Tab panel */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: var(--space-lg) !important;
    }

    /* ============================================
       DIVIDERS
       ============================================ */
    hr, .stDivider {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border-medium), transparent) !important;
        margin: var(--space-xl) 0 !important;
    }

    /* ============================================
       SECTION HEADER
       ============================================ */
    .section-header {
        display: flex !important;
        align-items: center !important;
        gap: var(--space-sm) !important;
        margin-bottom: var(--space-md) !important;
        padding-bottom: var(--space-sm) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }

    .section-header-title {
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* ============================================
       SLIDER - iOS Style
       ============================================ */
    .stSlider > div > div > div {
        background: var(--bg-glass) !important;
        height: 6px !important;
        border-radius: var(--radius-full) !important;
    }

    .stSlider > div > div > div > div {
        background: var(--gradient-primary) !important;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: white !important;
        border: 2px solid var(--primary) !important;
        box-shadow: 0 0 10px var(--primary-glow) !important;
        width: 22px !important;
        height: 22px !important;
    }

    /* ============================================
       TOGGLE/CHECKBOX
       ============================================ */
    .stCheckbox > label {
        color: var(--text-primary) !important;
    }

    /* ============================================
       FILE UPLOADER
       ============================================ */
    .stFileUploader > div {
        background: var(--bg-glass) !important;
        border: 2px dashed var(--border-medium) !important;
        border-radius: var(--radius-xl) !important;
        transition: all var(--transition-fast) !important;
    }

    .stFileUploader > div:hover {
        border-color: var(--primary) !important;
        background: var(--bg-hover) !important;
    }

    /* ============================================
       SPINNER
       ============================================ */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent !important;
    }

    /* ============================================
       COLUMNS
       ============================================ */
    [data-testid="column"] {
        padding: var(--space-sm) !important;
    }

    /* ============================================
       CHAT BUBBLES
       ============================================ */
    .chat-message {
        display: flex !important;
        gap: var(--space-md) !important;
        margin-bottom: var(--space-md) !important;
        align-items: flex-start !important;
    }

    .chat-avatar {
        width: 40px !important;
        height: 40px !important;
        border-radius: var(--radius-full) !important;
        background: var(--gradient-primary) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
        flex-shrink: 0 !important;
    }

    .chat-bubble {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-md) !important;
        max-width: 80% !important;
        color: var(--text-primary) !important;
        line-height: 1.5 !important;
    }

    .chat-message.user .chat-bubble {
        background: var(--bg-active) !important;
        border-color: var(--primary) !important;
    }

    /* ============================================
       ACCESSIBILITY
       ============================================ */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible {
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ============================================
       UTILITY CLASSES
       ============================================ */
    .text-center { text-align: center !important; }
    .text-gradient {
        background: var(--gradient-primary) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    .glow { box-shadow: var(--shadow-glow) !important; }
    .glass {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(20px) !important;
    }
    </style>
    """


def apply_theme() -> None:
    """Apply theme settings to the Streamlit app."""
    st.set_page_config(
        page_title="VivaLingo Pro",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(get_css(), unsafe_allow_html=True)


def render_hero(title: str, subtitle: str = "", pills: list = None) -> None:
    """Render a premium hero section with glassmorphism."""
    pills_html = ""
    if pills:
        pills_html = '<div class="hero-pills">' + ''.join(
            f'<span class="hero-pill">{pill}</span>' for pill in pills
        ) + '</div>'

    st.markdown(f"""
    <div class="hero">
        <div class="hero-content">
            {pills_html}
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, icon: str = "") -> None:
    """Render a section header with optional icon."""
    icon_html = f'<span style="font-size: 1.25rem;">{icon}</span>' if icon else ''
    st.markdown(f"""
    <div class="section-header">
        {icon_html}
        <span class="section-header-title">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, icon: str = "") -> str:
    """Return HTML for a glowing metric card."""
    icon_html = f'<div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>' if icon else ''
    return f"""
    <div class="metric-card">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def render_metric_grid(metrics: list) -> None:
    """Render a grid of metric cards."""
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(render_metric_card(
                metric.get("value", "0"),
                metric.get("label", ""),
                metric.get("icon", "")
            ), unsafe_allow_html=True)


def render_feedback(feedback_type: str, message: str, details: str = "") -> None:
    """Render a feedback box with vibrant styling."""
    details_html = f'<div style="margin-top: 8px; font-size: 0.9rem; opacity: 0.9;">{details}</div>' if details else ''
    st.markdown(f"""
    <div class="feedback-box feedback-{feedback_type}">
        {message}
        {details_html}
    </div>
    """, unsafe_allow_html=True)


def render_exercise_card(exercise_type: str, prompt: str) -> None:
    """Render an exercise card with type badge and prompt."""
    st.markdown(f"""
    <div class="glass-card">
        <span class="exercise-type">{exercise_type}</span>
        <div class="exercise-prompt">{prompt}</div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(current: int, total: int, label: str = "") -> None:
    """Render a progress indicator with label."""
    if label:
        st.caption(label)
    st.progress(current / total if total > 0 else 0)


def render_pill(text: str, variant: str = "primary") -> str:
    """Return HTML for a pill/badge."""
    return f'<span class="pill pill-{variant}">{text}</span>'


def render_card(content: str, title: str = "") -> None:
    """Render a glass card with optional title."""
    title_html = f'<h4 style="margin-bottom: 12px;">{title}</h4>' if title else ''
    st.markdown(f"""
    <div class="glass-card">
        {title_html}
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_domain_coverage(domains: dict) -> None:
    """Render domain coverage visualization."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    for domain, coverage in domains.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(min(coverage / 100, 1.0))
        with col2:
            st.caption(f"{domain}: {coverage:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)


def render_quick_actions(actions: list) -> None:
    """Render a row of quick action buttons."""
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


def render_profile_card(name: str, level: str, vocab_count: int, streak: int, is_active: bool = False) -> str:
    """Render a profile card with glassmorphism."""
    active_badge = '<span class="pill pill-success">Active</span>' if is_active else ''
    border_style = 'border-color: var(--primary); box-shadow: 0 0 20px var(--primary-glow);' if is_active else ''

    return f"""
    <div class="glass-card" style="{border_style}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
            <div>
                <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary);">{name}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">Level: {level}</div>
            </div>
            {active_badge}
        </div>
        <div style="display: flex; gap: 24px;">
            <div>
                <div style="font-weight: 700; font-size: 1.5rem; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{vocab_count}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Words</div>
            </div>
            <div>
                <div style="font-weight: 700; font-size: 1.5rem; color: var(--warning);">{streak}🔥</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Streak</div>
            </div>
        </div>
    </div>
    """


def render_streak_badge(streak: int) -> None:
    """Render a glowing streak badge."""
    if streak > 0:
        st.markdown(f"""
        <div style="display: inline-flex; align-items: center; gap: 10px;
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%);
                    padding: 12px 20px; border-radius: 16px;
                    border: 1px solid rgba(245, 158, 11, 0.3);
                    box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);">
            <span style="font-size: 1.75rem;">🔥</span>
            <span style="font-size: 1.5rem; font-weight: 800; color: #fbbf24;">{streak}</span>
            <span style="color: var(--text-secondary); font-weight: 500;">day{'s' if streak != 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)


# Backward compatibility
def get_design_system():
    """Return design tokens for programmatic access."""
    return {
        "colors": COLORS,
        "spacing": {
            "xs": "4px",
            "sm": "8px",
            "md": "16px",
            "lg": "24px",
            "xl": "32px",
        },
        "typography": {
            "base_size": "1rem",
            "heading_weight": 700,
            "line_height": 1.5,
        }
    }
