"""
Clean, minimal design system with high contrast and consistent surfaces.
No heavy gradients - subtle, professional appearance.
"""
import streamlit as st


# ============================================
# DESIGN TOKENS
# ============================================
COLORS = {
    # Backgrounds - 2 levels only
    "bg_page": "#09090b",
    "bg_surface": "#18181b",
    "bg_elevated": "#27272a",
    "bg_hover": "#3f3f46",

    # Text - high contrast
    "text_primary": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    "text_hint": "#52525b",

    # Accent - one primary color
    "accent": "#6366f1",
    "accent_hover": "#818cf8",
    "accent_muted": "rgba(99, 102, 241, 0.15)",

    # Semantic
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
}

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

RADII = {
    "sm": "6px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
}


def get_css() -> str:
    """Return clean, minimal CSS with high contrast."""
    return """
    <style>
    /* ============================================
       DESIGN TOKENS
       ============================================ */
    :root {
        /* Backgrounds - subtle, 2 levels */
        --bg-page: #09090b;
        --bg-surface: #18181b;
        --bg-elevated: #27272a;
        --bg-hover: #3f3f46;

        /* Text - high contrast */
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --text-hint: #52525b;

        /* Accent - single color */
        --accent: #6366f1;
        --accent-hover: #818cf8;
        --accent-muted: rgba(99, 102, 241, 0.15);

        /* Semantic colors */
        --success: #22c55e;
        --success-muted: rgba(34, 197, 94, 0.15);
        --warning: #f59e0b;
        --warning-muted: rgba(245, 158, 11, 0.15);
        --error: #ef4444;
        --error-muted: rgba(239, 68, 68, 0.15);
        --info: #3b82f6;
        --info-muted: rgba(59, 130, 246, 0.15);

        /* Borders */
        --border: #27272a;
        --border-hover: #3f3f46;

        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        --font-mono: 'SF Mono', Monaco, 'Cascadia Code', Consolas, monospace;

        /* Font sizes */
        --text-xs: 0.75rem;
        --text-sm: 0.875rem;
        --text-base: 1rem;
        --text-lg: 1.125rem;
        --text-xl: 1.25rem;
        --text-2xl: 1.5rem;
        --text-3xl: 2rem;

        /* Spacing */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;

        /* Radii */
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;

        /* Shadows - subtle */
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.4);
    }

    /* ============================================
       BASE STYLES
       ============================================ */
    .stApp {
        background: var(--bg-page) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
    }

    /* Hide Streamlit chrome */
    header[data-testid="stHeader"],
    footer,
    #MainMenu {
        display: none !important;
    }

    .main .block-container {
        padding: var(--space-6) var(--space-8) !important;
        max-width: 1200px !important;
    }

    /* ============================================
       TYPOGRAPHY
       ============================================ */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        letter-spacing: -0.01em !important;
    }

    h1, .stMarkdown h1 { font-size: var(--text-3xl) !important; }
    h2, .stMarkdown h2 { font-size: var(--text-2xl) !important; }
    h3, .stMarkdown h3 { font-size: var(--text-xl) !important; }
    h4, .stMarkdown h4 { font-size: var(--text-lg) !important; }

    p, .stMarkdown p {
        color: var(--text-secondary) !important;
        font-size: var(--text-base) !important;
        line-height: 1.6 !important;
    }

    strong, b {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ============================================
       SIDEBAR - Clean navigation
       ============================================ */
    [data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: var(--space-4) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        font-size: var(--text-xs) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--text-muted) !important;
        margin: var(--space-6) 0 var(--space-2) 0 !important;
    }

    /* ============================================
       BUTTONS
       ============================================ */

    /* Primary Button */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        font-size: var(--text-sm) !important;
        padding: 12px 24px !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: var(--accent-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="baseButton-primary"]:active {
        transform: translateY(0) !important;
    }

    /* Secondary Button */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([kind]) {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        font-size: var(--text-sm) !important;
        padding: 12px 20px !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:not([kind]):hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-hover) !important;
    }

    /* ============================================
       FORM INPUTS
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-size: var(--text-base) !important;
        padding: 12px 16px !important;
        min-height: 44px !important;
        transition: border-color 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-muted) !important;
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
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        margin-bottom: var(--space-2) !important;
    }

    /* ============================================
       RADIO BUTTONS
       ============================================ */
    .stRadio > div {
        gap: var(--space-2) !important;
    }

    .stRadio > div > label {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        color: var(--text-primary) !important;
        font-size: var(--text-sm) !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }

    .stRadio > div > label:hover {
        border-color: var(--border-hover) !important;
        background: var(--bg-elevated) !important;
    }

    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label:has(input:checked) {
        border-color: var(--accent) !important;
        background: var(--accent-muted) !important;
    }

    /* ============================================
       SELECT / DROPDOWN
       ============================================ */
    .stSelectbox > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
    }

    /* Dropdown menu */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    [data-baseweb="menu"] li,
    div[role="option"] {
        color: var(--text-primary) !important;
        background: transparent !important;
        padding: 10px 16px !important;
    }

    [data-baseweb="menu"] li:hover,
    div[role="option"]:hover {
        background: var(--bg-hover) !important;
    }

    [data-baseweb="menu"] li[aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background: var(--accent-muted) !important;
    }

    /* ============================================
       MULTISELECT
       ============================================ */
    .stMultiSelect > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: var(--accent) !important;
        border: none !important;
        color: white !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ============================================
       PROGRESS BAR
       ============================================ */
    .stProgress > div > div {
        background: var(--bg-elevated) !important;
        border-radius: var(--radius-sm) !important;
        height: 8px !important;
    }

    .stProgress > div > div > div {
        background: var(--accent) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ============================================
       CARDS
       ============================================ */
    .card {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-6) !important;
        margin-bottom: var(--space-4) !important;
        transition: border-color 0.15s ease !important;
    }

    .card:hover {
        border-color: var(--border-hover) !important;
    }

    .card-clickable {
        cursor: pointer !important;
    }

    .card-clickable:hover {
        border-color: var(--accent) !important;
    }

    /* Card variants */
    .card-accent {
        border-left: 3px solid var(--accent) !important;
    }

    .card-success {
        border-left: 3px solid var(--success) !important;
    }

    .card-warning {
        border-left: 3px solid var(--warning) !important;
    }

    /* ============================================
       TODAY DASHBOARD LAYOUT
       ============================================ */
    .dashboard-grid {
        display: grid !important;
        grid-template-columns: 1fr 340px !important;
        gap: var(--space-6) !important;
    }

    .dashboard-main {
        display: flex !important;
        flex-direction: column !important;
        gap: var(--space-4) !important;
    }

    .dashboard-rail {
        display: flex !important;
        flex-direction: column !important;
        gap: var(--space-4) !important;
    }

    @media (max-width: 1024px) {
        .dashboard-grid {
            grid-template-columns: 1fr !important;
        }
        .dashboard-rail {
            flex-direction: row !important;
            flex-wrap: wrap !important;
        }
    }

    /* ============================================
       ACTION CARDS (Continue, Review, etc.)
       ============================================ */
    .action-card {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-5) !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }

    .action-card:hover {
        border-color: var(--accent) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .action-card-primary {
        border-color: var(--accent) !important;
        background: var(--accent-muted) !important;
    }

    .action-card-title {
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: var(--space-1) !important;
    }

    .action-card-subtitle {
        font-size: var(--text-sm) !important;
        color: var(--text-secondary) !important;
    }

    .action-card-meta {
        font-size: var(--text-xs) !important;
        color: var(--text-muted) !important;
        margin-top: var(--space-2) !important;
    }

    /* ============================================
       STAT CARDS (Right rail)
       ============================================ */
    .stat-card {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-4) !important;
    }

    .stat-value {
        font-size: var(--text-2xl) !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1 !important;
    }

    .stat-label {
        font-size: var(--text-sm) !important;
        color: var(--text-muted) !important;
        margin-top: var(--space-1) !important;
    }

    /* ============================================
       EXERCISE COMPONENTS
       ============================================ */
    .exercise-container {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-6) !important;
    }

    .exercise-type-badge {
        display: inline-block !important;
        background: var(--accent-muted) !important;
        color: var(--accent) !important;
        padding: 4px 10px !important;
        border-radius: var(--radius-sm) !important;
        font-size: var(--text-xs) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: var(--space-3) !important;
    }

    .exercise-prompt {
        font-size: var(--text-xl) !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        line-height: 1.5 !important;
        margin-bottom: var(--space-4) !important;
    }

    /* Cloze blank */
    .cloze-blank {
        display: inline-block !important;
        min-width: 120px !important;
        border-bottom: 2px solid var(--accent) !important;
        margin: 0 4px !important;
        text-align: center !important;
        color: var(--accent) !important;
        font-weight: 500 !important;
    }

    .cloze-blank-input {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid var(--accent) !important;
        color: var(--text-primary) !important;
        font-size: inherit !important;
        font-weight: 500 !important;
        text-align: center !important;
        min-width: 120px !important;
        padding: 4px 8px !important;
        outline: none !important;
    }

    .cloze-blank-input:focus {
        border-bottom-color: var(--accent-hover) !important;
        background: var(--accent-muted) !important;
    }

    /* ============================================
       FEEDBACK BOXES
       ============================================ */
    .feedback-box {
        padding: var(--space-4) !important;
        border-radius: var(--radius-md) !important;
        margin: var(--space-4) 0 !important;
    }

    .feedback-success {
        background: var(--success-muted) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        color: var(--success) !important;
    }

    .feedback-error {
        background: var(--error-muted) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: var(--error) !important;
    }

    .feedback-warning {
        background: var(--warning-muted) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        color: var(--warning) !important;
    }

    .feedback-info {
        background: var(--info-muted) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: var(--info) !important;
    }

    /* ============================================
       PILLS / BADGES
       ============================================ */
    .pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        padding: 4px 10px !important;
        border-radius: var(--radius-sm) !important;
        font-size: var(--text-xs) !important;
        font-weight: 500 !important;
    }

    .pill-default {
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
    }

    .pill-accent {
        background: var(--accent-muted) !important;
        color: var(--accent) !important;
    }

    .pill-success {
        background: var(--success-muted) !important;
        color: var(--success) !important;
    }

    .pill-warning {
        background: var(--warning-muted) !important;
        color: var(--warning) !important;
    }

    .pill-error {
        background: var(--error-muted) !important;
        color: var(--error) !important;
    }

    /* ============================================
       LOADING STATES
       ============================================ */
    .skeleton {
        background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-hover) 50%, var(--bg-elevated) 75%) !important;
        background-size: 200% 100% !important;
        animation: skeleton-loading 1.5s infinite !important;
        border-radius: var(--radius-sm) !important;
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    .loading-spinner {
        display: inline-block !important;
        width: 20px !important;
        height: 20px !important;
        border: 2px solid var(--bg-elevated) !important;
        border-top-color: var(--accent) !important;
        border-radius: 50% !important;
        animation: spin 0.8s linear infinite !important;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Empty state */
    .empty-state {
        text-align: center !important;
        padding: var(--space-8) var(--space-4) !important;
        color: var(--text-muted) !important;
    }

    .empty-state-icon {
        font-size: 48px !important;
        margin-bottom: var(--space-4) !important;
        opacity: 0.5 !important;
    }

    /* Error state */
    .error-state {
        text-align: center !important;
        padding: var(--space-6) !important;
        background: var(--error-muted) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--error) !important;
    }

    /* ============================================
       TABS
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 12px 20px !important;
        font-weight: 500 !important;
        margin-bottom: -1px !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
    }

    /* ============================================
       DIVIDERS
       ============================================ */
    hr, .stDivider {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: var(--space-6) 0 !important;
    }

    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-elevated) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }

    /* ============================================
       SLIDER
       ============================================ */
    .stSlider > div > div > div {
        background: var(--bg-elevated) !important;
    }

    .stSlider > div > div > div > div {
        background: var(--accent) !important;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: white !important;
        border: 2px solid var(--accent) !important;
    }

    /* ============================================
       ALERTS
       ============================================ */
    div[data-testid="stAlert"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ============================================
       METRICS
       ============================================ */
    [data-testid="stMetric"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-4) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }

    /* ============================================
       TOAST NOTIFICATIONS
       ============================================ */
    .toast {
        position: fixed !important;
        bottom: var(--space-6) !important;
        right: var(--space-6) !important;
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-4) var(--space-5) !important;
        box-shadow: var(--shadow-lg) !important;
        z-index: 1000 !important;
        animation: slideIn 0.3s ease !important;
    }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    /* ============================================
       TOP BAR
       ============================================ */
    .top-bar {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: var(--space-4) 0 !important;
        border-bottom: 1px solid var(--border) !important;
        margin-bottom: var(--space-6) !important;
    }

    .top-bar-title {
        font-size: var(--text-xl) !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    .top-bar-actions {
        display: flex !important;
        align-items: center !important;
        gap: var(--space-3) !important;
    }

    /* ============================================
       SECTION HEADER
       ============================================ */
    .section-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin-bottom: var(--space-4) !important;
    }

    .section-title {
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    .section-link {
        font-size: var(--text-sm) !important;
        color: var(--accent) !important;
        cursor: pointer !important;
    }

    .section-link:hover {
        color: var(--accent-hover) !important;
        text-decoration: underline !important;
    }

    /* ============================================
       HINT TIERS
       ============================================ */
    .hint-tier {
        background: var(--info-muted) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-3) var(--space-4) !important;
        margin-top: var(--space-3) !important;
        font-size: var(--text-sm) !important;
        color: var(--info) !important;
    }

    .hint-tier-label {
        font-weight: 600 !important;
        margin-bottom: var(--space-1) !important;
    }

    /* ============================================
       ACCESSIBILITY
       ============================================ */
    *:focus-visible {
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """


def apply_theme() -> None:
    """Apply theme to app."""
    st.set_page_config(
        page_title="VivaLingo",
        page_icon="🇪🇸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(get_css(), unsafe_allow_html=True)


# ============================================
# COMPONENT FUNCTIONS
# ============================================

def render_hero(title: str, subtitle: str = "", pills: list = None) -> None:
    """Render page header - NOT raw HTML, proper components."""
    if pills:
        pills_html = ' '.join(f'<span class="pill pill-accent">{p}</span>' for p in pills)
        st.markdown(f'<div style="margin-bottom: 12px;">{pills_html}</div>', unsafe_allow_html=True)

    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p style='color: var(--text-secondary); margin-top: -12px;'>{subtitle}</p>", unsafe_allow_html=True)


def render_section_header(title: str, action_label: str = None, action_key: str = None) -> bool:
    """Render section header with optional action link. Returns True if action clicked."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {title}")

    clicked = False
    if action_label and action_key:
        with col2:
            clicked = st.button(action_label, key=action_key, type="secondary")

    return clicked


def render_action_card(title: str, subtitle: str, meta: str = "", primary: bool = False, icon: str = "") -> None:
    """Render an action card."""
    primary_class = "action-card-primary" if primary else ""
    icon_html = f'<span style="font-size: 24px; margin-right: 12px;">{icon}</span>' if icon else ''

    st.markdown(f"""
    <div class="action-card {primary_class}">
        <div style="display: flex; align-items: flex-start;">
            {icon_html}
            <div>
                <div class="action-card-title">{title}</div>
                <div class="action-card-subtitle">{subtitle}</div>
                {f'<div class="action-card-meta">{meta}</div>' if meta else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(value: str, label: str, icon: str = "") -> None:
    """Render a stat card for the right rail."""
    icon_html = f'<span style="font-size: 20px; margin-right: 8px;">{icon}</span>' if icon else ''
    st.markdown(f"""
    <div class="stat-card">
        <div style="display: flex; align-items: center;">
            {icon_html}
            <div>
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feedback(feedback_type: str, message: str, details: str = "") -> None:
    """Render feedback box."""
    details_html = f'<div style="margin-top: 8px; opacity: 0.9;">{details}</div>' if details else ''
    st.markdown(f"""
    <div class="feedback-box feedback-{feedback_type}">
        <strong>{message}</strong>
        {details_html}
    </div>
    """, unsafe_allow_html=True)


def render_pill(text: str, variant: str = "default") -> str:
    """Return HTML for a pill."""
    return f'<span class="pill pill-{variant}">{text}</span>'


def render_loading_skeleton(height: str = "100px") -> None:
    """Render a loading skeleton."""
    st.markdown(f'<div class="skeleton" style="height: {height};"></div>', unsafe_allow_html=True)


def render_empty_state(message: str, icon: str = "📭") -> None:
    """Render an empty state."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_error_state(message: str, retry_label: str = "Try again") -> bool:
    """Render an error state. Returns True if retry clicked."""
    st.markdown(f"""
    <div class="error-state">
        <p><strong>Something went wrong</strong></p>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(retry_label, type="primary")


def render_cloze_sentence(before: str, after: str, answer: str = "", show_answer: bool = False) -> None:
    """Render a cloze sentence with visible blank."""
    if show_answer:
        blank = f'<span class="cloze-blank" style="color: var(--success);">{answer}</span>'
    else:
        blank = '<span class="cloze-blank">_____</span>'

    st.markdown(f"""
    <div class="exercise-prompt">
        {before}{blank}{after}
    </div>
    """, unsafe_allow_html=True)


def render_exercise_feedback(correct: bool, correct_answer: str, explanation: str = "", common_mistake: str = "") -> None:
    """Render exercise feedback with teaching content."""
    if correct:
        st.markdown(f"""
        <div class="feedback-box feedback-success">
            <strong>✓ Correct!</strong>
            {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        mistake_html = f'<div style="margin-top: 8px; opacity: 0.85;"><em>Common mistake: {common_mistake}</em></div>' if common_mistake else ''
        st.markdown(f"""
        <div class="feedback-box feedback-error">
            <strong>✗ Not quite</strong>
            <div style="margin-top: 8px;">The correct answer is: <strong>{correct_answer}</strong></div>
            {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
            {mistake_html}
        </div>
        """, unsafe_allow_html=True)


def render_hint_tiers(hints: list, current_tier: int = 0) -> None:
    """Render tiered hints."""
    if current_tier < len(hints):
        hint = hints[current_tier]
        tier_labels = ["Grammar hint", "Part of speech", "First letters", "Word bank"]
        label = tier_labels[current_tier] if current_tier < len(tier_labels) else f"Hint {current_tier + 1}"

        st.markdown(f"""
        <div class="hint-tier">
            <div class="hint-tier-label">{label}</div>
            <div>{hint}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# BACKWARD COMPATIBILITY
# ============================================

def render_metric_card(value: str, label: str, icon: str = "") -> str:
    """Return HTML for metric card."""
    icon_html = f'<div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>' if icon else ''
    return f"""
    <div class="stat-card">
        {icon_html}
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def render_metric_grid(metrics: list) -> None:
    """Render grid of metrics."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(render_metric_card(
                str(m.get("value", "0")),
                m.get("label", ""),
                m.get("icon", "")
            ), unsafe_allow_html=True)


def render_card(content: str, title: str = "") -> None:
    """Render a card."""
    title_html = f'<h4 style="margin-bottom: 12px;">{title}</h4>' if title else ''
    st.markdown(f"""
    <div class="card">
        {title_html}
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_domain_coverage(domains: dict) -> None:
    """Render domain coverage."""
    for domain, coverage in domains.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(min(coverage / 100, 1.0))
        with col2:
            st.caption(f"{domain}: {coverage:.0f}%")


def render_quick_actions(actions: list) -> None:
    """Render quick actions."""
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
    """Render profile card."""
    active_class = 'border-color: var(--accent);' if is_active else ''
    active_badge = '<span class="pill pill-success">Active</span>' if is_active else ''

    return f"""
    <div class="card" style="{active_class}">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-weight: 600; font-size: 1.1rem;">{name}</div>
                <div style="color: var(--text-muted); font-size: 0.875rem;">Level: {level}</div>
            </div>
            {active_badge}
        </div>
        <div style="display: flex; gap: 24px;">
            <div>
                <div style="font-weight: 700; font-size: 1.25rem;">{vocab_count}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">Words</div>
            </div>
            <div>
                <div style="font-weight: 700; font-size: 1.25rem;">{streak}🔥</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">Streak</div>
            </div>
        </div>
    </div>
    """


def render_streak_badge(streak: int) -> None:
    """Render streak badge."""
    if streak > 0:
        st.markdown(f"""
        <div style="display: inline-flex; align-items: center; gap: 8px;
                    background: var(--warning-muted); padding: 8px 16px;
                    border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.3);">
            <span style="font-size: 1.5rem;">🔥</span>
            <span style="font-size: 1.25rem; font-weight: 700; color: var(--warning);">{streak}</span>
            <span style="color: var(--text-secondary);">day{'s' if streak != 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)


def get_design_system():
    """Return design tokens."""
    return {
        "colors": COLORS,
        "spacing": SPACING,
        "radii": RADII,
    }


# ============================================
# EXERCISE VALIDATION
# ============================================

def validate_exercise(exercise: dict) -> dict:
    """Validate exercise data. Returns {valid: bool, errors: list}."""
    errors = []
    ex_type = exercise.get("type", "")

    # Type-specific validation
    if ex_type == "cloze":
        if "before" not in exercise or "after" not in exercise:
            errors.append("Cloze exercise must have 'before' and 'after' parts")
        if not exercise.get("answer"):
            errors.append("Cloze exercise must have an answer")

    elif ex_type == "mcq":
        if not exercise.get("choices") or len(exercise.get("choices", [])) < 2:
            errors.append("MCQ must have at least 2 choices")
        if not exercise.get("correct_index") and exercise.get("correct_index") != 0:
            errors.append("MCQ must specify correct_index")

    elif ex_type == "translate":
        if not exercise.get("source"):
            errors.append("Translation must have source text")
        if not exercise.get("acceptable_answers"):
            errors.append("Translation must have acceptable answers")

    # Common validation
    if not exercise.get("type"):
        errors.append("Exercise must have a type")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def get_instruction_for_type(ex_type: str) -> str:
    """Get instruction text based on exercise type."""
    instructions = {
        "cloze": "Fill in the blank with the correct word",
        "mcq": "Choose the correct answer",
        "translate": "Translate into Spanish",
        "free_recall": "Type the missing word",
        "listening": "Listen and type what you hear",
        "speaking": "Repeat the phrase out loud",
    }
    return instructions.get(ex_type, "Complete the exercise")


def normalize_spanish_answer(text: str, strict_accents: bool = False) -> str:
    """Normalize Spanish text for comparison."""
    import unicodedata

    # Basic normalization
    text = text.strip().lower()
    text = ' '.join(text.split())  # Collapse whitespace

    # Remove punctuation (except internal apostrophes)
    import re
    text = re.sub(r'[^\w\sáéíóúüñ\']', '', text)

    # Optionally fold diacritics
    if not strict_accents:
        # Keep ñ but fold accented vowels
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')

    return text


def check_answer(user_answer: str, correct_answers: list, strict_accents: bool = False) -> dict:
    """Check user answer against correct answers.

    Returns: {result: 'correct'|'almost'|'incorrect', matched: str|None, feedback: str}
    """
    user_normalized = normalize_spanish_answer(user_answer, strict_accents=True)
    user_folded = normalize_spanish_answer(user_answer, strict_accents=False)

    for answer in correct_answers:
        answer_normalized = normalize_spanish_answer(answer, strict_accents=True)
        answer_folded = normalize_spanish_answer(answer, strict_accents=False)

        # Exact match
        if user_normalized == answer_normalized:
            return {"result": "correct", "matched": answer, "feedback": ""}

        # Match without accents
        if user_folded == answer_folded:
            return {
                "result": "almost",
                "matched": answer,
                "feedback": f"Almost! Watch the accents: {answer}"
            }

    return {
        "result": "incorrect",
        "matched": None,
        "feedback": f"The correct answer is: {correct_answers[0]}"
    }
