"""
iPhone-style clean white design system.
Pure white backgrounds with colorful accents.
"""
import streamlit as st


# ============================================
# DESIGN TOKENS - iPhone Style
# ============================================
COLORS = {
    # Backgrounds - Pure white
    "bg_base": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "bg_elevated": "#F2F2F7",
    "bg_grouped": "#F2F2F7",

    # Text - iOS style
    "text_primary": "#000000",
    "text_secondary": "#3C3C43",
    "text_tertiary": "#8E8E93",

    # iOS Accent Colors
    "blue": "#007AFF",
    "green": "#34C759",
    "orange": "#FF9500",
    "red": "#FF3B30",
    "purple": "#AF52DE",
    "pink": "#FF2D55",
    "teal": "#5AC8FA",
    "indigo": "#5856D6",

    # Semantic
    "success": "#34C759",
    "warning": "#FF9500",
    "error": "#FF3B30",
    "info": "#007AFF",

    # Borders
    "separator": "#C6C6C8",
    "border": "#E5E5EA",
}

SPACING = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "20px", "xl": "32px"}
RADII = {"sm": "8px", "md": "12px", "lg": "16px", "xl": "22px", "full": "9999px"}


def get_css() -> str:
    """Return iPhone-style CSS - clean white with colorful accents."""
    return """
    <style>
    /* ============================================
       iPHONE-STYLE DESIGN SYSTEM
       Pure White • Colorful Accents • Clean
       ============================================ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ============================================
       FORCE WHITE BACKGROUND EVERYWHERE
       ============================================ */
    html, body, .stApp, .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stVerticalBlock"],
    .main .block-container,
    [data-testid="stAppViewBlockContainer"],
    .stApp > header,
    div[data-testid="stDecoration"],
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
    }

    .main .block-container {
        padding: 2rem 2rem 4rem 2rem !important;
        max-width: 1100px !important;
    }

    /* ============================================
       SIDEBAR - Clean White
       ============================================ */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] {
        background: #F2F2F7 !important;
        background-color: #F2F2F7 !important;
    }

    /* Hide sidebar collapse button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
    }

    /* Sidebar content */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #8E8E93 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }

    /* ============================================
       TYPOGRAPHY - iOS Style
       ============================================ */
    html, body, .stApp, .stMarkdown, p, span, div, label, button, input, textarea {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #000000 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }

    h1, .stMarkdown h1 { font-size: 34px !important; }
    h2, .stMarkdown h2 { font-size: 28px !important; }
    h3, .stMarkdown h3 { font-size: 22px !important; }
    h4, .stMarkdown h4 { font-size: 17px !important; font-weight: 600 !important; }

    p, .stMarkdown p, .stText {
        color: #3C3C43 !important;
        font-size: 17px !important;
        line-height: 1.5 !important;
    }

    label {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* ============================================
       BUTTONS - iOS Style
       ============================================ */
    .stButton > button {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif !important;
        font-weight: 600 !important;
        font-size: 17px !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        min-height: 50px !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }

    /* Secondary button - Light gray fill */
    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
        background: #F2F2F7 !important;
        color: #007AFF !important;
    }

    .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
        background: #E5E5EA !important;
    }

    /* Primary button - iOS Blue */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: #007AFF !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: #0056B3 !important;
    }

    /* ============================================
       FORM INPUTS - iOS Style
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #C6C6C8 !important;
        border-radius: 10px !important;
        font-size: 17px !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #C7C7CC !important;
    }

    /* ============================================
       SELECT / DROPDOWN
       ============================================ */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 1px solid #C6C6C8 !important;
        border-radius: 10px !important;
    }

    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"] span {
        color: #000000 !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12) !important;
    }

    [data-baseweb="menu"] li,
    div[role="option"] {
        color: #000000 !important;
    }

    [data-baseweb="menu"] li:hover,
    div[role="option"]:hover {
        background: #F2F2F7 !important;
    }

    /* ============================================
       RADIO BUTTONS - iOS Segmented Style
       ============================================ */
    .stRadio > div > label {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }

    .stRadio > div > label:hover {
        background: #F2F2F7 !important;
    }

    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label:has(input:checked) {
        background: #007AFF !important;
        border-color: #007AFF !important;
        color: #FFFFFF !important;
    }

    /* ============================================
       PROGRESS BAR - iOS Style
       ============================================ */
    .stProgress > div > div {
        background: #E5E5EA !important;
        border-radius: 4px !important;
        height: 8px !important;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #007AFF, #5AC8FA) !important;
        border-radius: 4px !important;
    }

    /* ============================================
       TABS - iOS Segmented Control
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        background: #F2F2F7 !important;
        border-radius: 10px !important;
        padding: 2px !important;
        gap: 2px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #8E8E93 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #000000 !important;
    }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 12px !important;
        color: #000000 !important;
    }

    .streamlit-expanderContent {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* ============================================
       ALERTS
       ============================================ */
    .stAlert, div[data-testid="stAlert"] {
        background: #F2F2F7 !important;
        border: none !important;
        border-radius: 12px !important;
        color: #000000 !important;
    }

    /* ============================================
       DIVIDER
       ============================================ */
    hr {
        border: none !important;
        border-top: 1px solid #E5E5EA !important;
        margin: 20px 0 !important;
    }

    /* ============================================
       CUSTOM CARD CLASSES - iOS Style
       ============================================ */
    .card {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    .card h3, .card h4 {
        color: #000000 !important;
        margin-bottom: 8px !important;
    }

    .card p {
        color: #8E8E93 !important;
        margin: 0 !important;
        font-size: 15px !important;
    }

    .glass-card {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    /* Stat cards */
    .stat-card {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 16px !important;
        padding: 16px !important;
        text-align: center !important;
    }

    .stat-value {
        font-size: 34px !important;
        font-weight: 700 !important;
        color: #000000 !important;
    }

    .stat-label {
        font-size: 13px !important;
        color: #8E8E93 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-weight: 600 !important;
    }

    /* Action cards */
    .action-card {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 16px !important;
        padding: 16px !important;
    }

    .action-card-title {
        font-weight: 600 !important;
        color: #000000 !important;
        font-size: 17px !important;
    }

    .action-card-subtitle {
        color: #8E8E93 !important;
        font-size: 15px !important;
    }

    /* Pills/badges - Colorful */
    .pill {
        display: inline-block !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    .pill-accent, .pill-blue {
        background: rgba(0, 122, 255, 0.12) !important;
        color: #007AFF !important;
    }

    .pill-success, .pill-green {
        background: rgba(52, 199, 89, 0.12) !important;
        color: #34C759 !important;
    }

    .pill-warning, .pill-orange {
        background: rgba(255, 149, 0, 0.12) !important;
        color: #FF9500 !important;
    }

    .pill-error, .pill-red {
        background: rgba(255, 59, 48, 0.12) !important;
        color: #FF3B30 !important;
    }

    .pill-purple {
        background: rgba(175, 82, 222, 0.12) !important;
        color: #AF52DE !important;
    }

    /* Feedback boxes */
    .feedback-box {
        padding: 16px !important;
        border-radius: 12px !important;
        margin: 12px 0 !important;
    }

    .feedback-success {
        background: rgba(52, 199, 89, 0.12) !important;
        color: #248A3D !important;
    }

    .feedback-error {
        background: rgba(255, 59, 48, 0.12) !important;
        color: #D70015 !important;
    }

    .feedback-warning {
        background: rgba(255, 149, 0, 0.12) !important;
        color: #C93400 !important;
    }

    .feedback-info {
        background: rgba(0, 122, 255, 0.12) !important;
        color: #0040DD !important;
    }

    /* Hero section */
    .hero {
        background: linear-gradient(135deg, rgba(0, 122, 255, 0.08), rgba(90, 200, 250, 0.08)) !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }

    .hero-title {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #000000 !important;
    }

    .hero-subtitle {
        color: #8E8E93 !important;
        font-size: 17px !important;
    }

    /* Exercise elements */
    .exercise-prompt {
        font-size: 20px !important;
        color: #000000 !important;
        line-height: 1.5 !important;
    }

    .cloze-blank {
        display: inline-block !important;
        min-width: 80px !important;
        border-bottom: 2px solid #007AFF !important;
        color: #007AFF !important;
        text-align: center !important;
        margin: 0 4px !important;
    }

    /* Hide Streamlit elements */
    #MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* Scrollbar - minimal */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #C6C6C8; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #8E8E93; }
    </style>
    """


def apply_theme():
    """Apply theme to app."""
    st.markdown(get_css(), unsafe_allow_html=True)


# ============================================
# COMPONENT FUNCTIONS
# ============================================

def render_hero(title: str, subtitle: str = "", pills: list = None) -> None:
    """Render a hero section."""
    pills_html = ""
    if pills:
        pills_html = '<div style="margin-bottom: 12px;">' + ' '.join(
            f'<span class="pill pill-blue">{p}</span>' for p in pills
        ) + '</div>'

    st.markdown(f"""
    <div class="hero">
        {pills_html}
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


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


def render_metric_card(value: str, label: str, icon: str = "", color: str = "#007AFF") -> str:
    """Return HTML for a metric card."""
    icon_html = f'<div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>' if icon else ''
    return f"""
    <div class="stat-card">
        {icon_html}
        <div class="stat-value" style="color: {color};">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def render_metric_grid(metrics: list) -> None:
    """Render a grid of metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(render_metric_card(
                str(m.get("value", "0")),
                m.get("label", ""),
                m.get("icon", ""),
                m.get("color", "#007AFF")
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


def render_pill(text: str, variant: str = "blue") -> str:
    """Return HTML for a pill badge."""
    return f'<span class="pill pill-{variant}">{text}</span>'


def render_feedback(feedback_type: str, message: str, details: str = "") -> None:
    """Render a feedback box."""
    details_html = f'<div style="margin-top: 8px;">{details}</div>' if details else ''
    st.markdown(f"""
    <div class="feedback-box feedback-{feedback_type}">
        <strong>{message}</strong>
        {details_html}
    </div>
    """, unsafe_allow_html=True)


def render_card(content: str, title: str = "") -> None:
    """Render a card."""
    title_html = f'<h4 style="margin-bottom: 10px; color: #000000;">{title}</h4>' if title else ''
    st.markdown(f"""
    <div class="glass-card">
        {title_html}
        <div style="color: #8E8E93;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


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


def render_stat_card(value: str, label: str, icon: str = "", color: str = "#007AFF") -> None:
    """Render a stat card directly."""
    st.markdown(render_metric_card(value, label, icon, color), unsafe_allow_html=True)


def render_action_card(title: str, subtitle: str, meta: str = "", primary: bool = False, icon: str = "") -> None:
    """Render an action card."""
    bg_color = "rgba(0, 122, 255, 0.08)" if primary else "#FFFFFF"
    border_color = "#007AFF" if primary else "#E5E5EA"
    icon_html = f'<span style="font-size: 32px; margin-right: 16px;">{icon}</span>' if icon else ''
    meta_html = f'<div style="font-size: 13px; color: #8E8E93; margin-top: 4px;">{meta}</div>' if meta else ''

    st.markdown(f"""
    <div style="background: {bg_color}; border: 1px solid {border_color};
                border-radius: 16px; padding: 16px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center;">
            {icon_html}
            <div>
                <div style="font-weight: 600; color: #000000; font-size: 17px;">{title}</div>
                <div style="color: #8E8E93; font-size: 15px;">{subtitle}</div>
                {meta_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_streak_badge(streak: int) -> None:
    """Render a streak badge."""
    if streak > 0:
        st.markdown(f"""
        <div style="display: inline-flex; align-items: center; gap: 8px;
                    background: rgba(255, 149, 0, 0.12); padding: 10px 16px;
                    border-radius: 12px;">
            <span style="font-size: 24px;">🔥</span>
            <span style="font-size: 22px; font-weight: 700; color: #FF9500;">{streak}</span>
            <span style="color: #8E8E93; font-size: 15px;">day{'s' if streak != 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)


def render_empty_state(message: str, icon: str = "📭") -> None:
    """Render an empty state."""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px;">
        <div style="font-size: 48px; margin-bottom: 12px;">{icon}</div>
        <p style="color: #8E8E93; font-size: 17px;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_loading_skeleton(height: str = "100px") -> None:
    """Render a loading skeleton."""
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #F2F2F7 25%, #E5E5EA 50%, #F2F2F7 75%);
                background-size: 200% 100%; height: {height}; border-radius: 12px;
                animation: shimmer 1.5s infinite;">
    </div>
    <style>
    @keyframes shimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
    </style>
    """, unsafe_allow_html=True)


def render_error_state(message: str, retry_label: str = "Try again") -> bool:
    """Render error state. Returns True if retry clicked."""
    st.markdown(f"""
    <div style="text-align: center; padding: 24px; background: rgba(255, 59, 48, 0.12);
                border-radius: 16px;">
        <p style="color: #FF3B30; font-size: 17px;"><strong>Something went wrong</strong></p>
        <p style="color: #8E8E93;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(retry_label, type="primary")


def render_profile_card(name: str, level: str, vocab_count: int, streak: int, is_active: bool = False) -> str:
    """Render a profile card."""
    border_color = "#007AFF" if is_active else "#E5E5EA"
    badge = '<span class="pill pill-green">Active</span>' if is_active else ''

    return f"""
    <div class="glass-card" style="border-color: {border_color};">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div style="font-weight: 600; color: #000000; font-size: 17px;">{name}</div>
                <div style="font-size: 15px; color: #8E8E93;">Level: {level}</div>
            </div>
            {badge}
        </div>
        <div style="display: flex; gap: 24px;">
            <div>
                <div style="font-weight: 700; color: #007AFF; font-size: 20px;">{vocab_count}</div>
                <div style="font-size: 13px; color: #8E8E93;">Words</div>
            </div>
            <div>
                <div style="font-weight: 700; color: #FF9500; font-size: 20px;">{streak}🔥</div>
                <div style="font-size: 13px; color: #8E8E93;">Streak</div>
            </div>
        </div>
    </div>
    """


def render_cloze_sentence(before: str, after: str, answer: str = "", show_answer: bool = False) -> None:
    """Render a cloze sentence with visible blank."""
    if show_answer:
        blank = f'<span class="cloze-blank" style="color: #34C759;">{answer}</span>'
    else:
        blank = '<span class="cloze-blank">_____</span>'

    st.markdown(f"""
    <div class="exercise-prompt">
        {before}{blank}{after}
    </div>
    """, unsafe_allow_html=True)


def render_exercise_feedback(correct: bool, correct_answer: str, explanation: str = "", common_mistake: str = "") -> None:
    """Render exercise feedback."""
    if correct:
        st.markdown(f"""
        <div class="feedback-box feedback-success">
            <strong>✓ Correct!</strong>
            {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        mistake_html = f'<div style="margin-top: 8px;"><em>Tip: {common_mistake}</em></div>' if common_mistake else ''
        st.markdown(f"""
        <div class="feedback-box feedback-error">
            <strong>✗ Not quite</strong>
            <div style="margin-top: 8px;">Correct answer: <strong>{correct_answer}</strong></div>
            {f'<div style="margin-top: 8px;">{explanation}</div>' if explanation else ''}
            {mistake_html}
        </div>
        """, unsafe_allow_html=True)


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
