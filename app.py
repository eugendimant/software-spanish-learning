"""
VivaLingo - Spanish Learning Platform
Clean, focused interface for C1-C2 learners.
"""
import streamlit as st
from textwrap import dedent
from datetime import date

# Initialize database and theme first
from utils.database import (
    init_db, get_user_profile, update_user_profile, get_total_stats,
    get_vocab_for_review, get_mistakes_for_review, get_grammar_for_review,
    get_progress_history, get_all_profiles, create_profile,
    set_active_profile_id, get_active_profile_id, get_profile_stats,
    get_sessions_this_week, get_weak_areas, get_learning_velocity,
    get_activity_history, get_mistake_stats, get_fingerprint_summary,
    get_vocab_items, get_active_vocab_count
)
from utils.theme import (
    get_css, render_hero, render_section_header, render_stat_card,
    render_action_card, render_feedback, render_streak_badge,
    render_empty_state, render_loading_skeleton, render_html
)
from utils.helpers import get_streak_days

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="VivaLingo",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
st.markdown(get_css(), unsafe_allow_html=True)

# Normalize HTML markdown to avoid code blocks from indentation
_original_markdown = st.markdown


def _markdown_with_html(*args, **kwargs):
    if kwargs.get("unsafe_allow_html") and args and isinstance(args[0], str):
        args = (dedent(args[0]).strip(),) + args[1:]
    return _original_markdown(*args, **kwargs)


st.markdown = _markdown_with_html

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database error: {str(e)}")


# ============================================
# SESSION STATE
# ============================================

def init_session_state():
    """Initialize session state."""
    defaults = {
        "initialized": True,
        "current_page": "Home",
        "review_queue": [],
        "active_profile_id": None,
        "show_onboarding": False,
        "onboarding_step": 0,
        "last_session": None,  # For "Continue" feature
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Load active profile
    if st.session_state.active_profile_id is None:
        profiles = get_all_profiles()
        if profiles:
            st.session_state.active_profile_id = profiles[0]["id"]
            set_active_profile_id(profiles[0]["id"])
        else:
            st.session_state.show_onboarding = True


init_session_state()


# ============================================
# NAVIGATION CONFIG
# ============================================

# Learner-facing navigation only
NAV_ITEMS = [
    {"icon": "🏠", "label": "Home", "page": "Home"},
    {"icon": "📚", "label": "Learn", "page": "Learn"},
    {"icon": "🔄", "label": "Review", "page": "Review"},
    {"icon": "🎯", "label": "Practice", "page": "Practice"},
    {"icon": "📊", "label": "Progress", "page": "Progress"},
    {"icon": "⚙️", "label": "Settings", "page": "Settings"},
]

# Sub-pages for Practice
PRACTICE_PAGES = {
    "Vocabulary": "Topic Diversity",
    "Verbs": "Verb Studio",
    "Conversation": "Conversation",
    "Writing": "Writing Coach",
}

# Tools (accessible from Practice)
TOOLS = {
    "Dialect Guide": "Dialects",
    "Memory Palace": "Memory Palace",
    "Error Patterns": "Mistake Catcher",
}


# ============================================
# SIDEBAR
# ============================================

def render_sidebar():
    """Render clean, learner-focused sidebar."""
    with st.sidebar:
        # App header
        render_html("""
            <div style="padding: 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 16px;">
                <div style="font-size: 24px; font-weight: 700; color: var(--text-primary);">
                    🇪🇸 VivaLingo
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">Spanish Mastery</div>
            </div>
        """)

        # Profile info
        profile = get_user_profile()
        if profile.get("name"):
            streak = get_streak_days(get_progress_history())
            render_html(f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 12px;
                            background: var(--bg-surface); border-radius: 8px; margin-bottom: 16px;">
                    <div style="width: 36px; height: 36px; border-radius: 50%;
                                background: var(--accent); display: flex; align-items: center;
                                justify-content: center; color: white; font-weight: 600;">
                        {profile['name'][0].upper()}
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: var(--text-primary);">{profile['name']}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">Level {profile.get('level', 'C1')}</div>
                    </div>
                    {f'<div style="font-size: 14px;">🔥 {streak}</div>' if streak > 0 else ''}
                </div>
            """)

        # Review due badge
        vocab_due = len(get_vocab_for_review())
        errors_due = len(get_mistakes_for_review())
        total_due = vocab_due + errors_due

        if total_due > 0:
            render_html(f"""
                <div style="background: var(--accent-muted); border: 1px solid rgba(99, 102, 241, 0.3);
                            border-radius: 8px; padding: 10px 12px; margin-bottom: 16px;">
                    <div style="font-size: 13px; color: var(--accent);">
                        <strong>{total_due}</strong> items due for review
                    </div>
                </div>
            """)

        # Main navigation
        st.markdown("#### Navigation")

        for item in NAV_ITEMS:
            is_active = st.session_state.current_page == item["page"]
            if st.button(
                f"{item['icon']} {item['label']}",
                key=f"nav_{item['page']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = item["page"]
                st.rerun()

        # Admin tools - only show if user has admin flag (hidden for normal users)
        profile = get_user_profile()
        if profile.get("is_admin"):
            st.divider()
            st.markdown("#### Developer")
            admin_pages = [
                ("Content Ingest", "Content Ingest"),
                ("Error Notebook", "Error Notebook"),
                ("Fingerprint", "Fingerprint"),
            ]
            for label, page in admin_pages:
                if st.button(label, key=f"admin_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()


# ============================================
# ONBOARDING
# ============================================

def render_onboarding():
    """Render onboarding flow for new users with enhanced UX."""
    step = st.session_state.onboarding_step
    total_steps = 6

    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        render_html("""
            <div style="text-align: center; padding: 32px 0;">
                <div style="font-size: 48px; margin-bottom: 16px;">🇪🇸</div>
                <h1 style="margin-bottom: 8px;">Welcome to VivaLingo</h1>
                <p style="color: var(--text-secondary);">Let's set up your learning profile</p>
            </div>
        """)

        # Progress indicator
        progress_pct = (step + 1) / total_steps
        st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 13px; color: #8E8E93;">Step {step + 1} of {total_steps}</span>
                <span style="font-size: 13px; color: #007AFF; font-weight: 500;">{int(progress_pct * 100)}%</span>
            </div>
            <div style="background: #E5E5EA; height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #007AFF, #8b5cf6);
                            height: 100%; width: {progress_pct * 100}%;
                            border-radius: 3px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ============================================
        # STEP 0: Name
        # ============================================
        if step == 0:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">👋</div>
                <h3 style="margin-bottom: 4px;">What's your name?</h3>
                <p style="color: #8E8E93; font-size: 14px;">We'll use this to personalize your experience</p>
            </div>
            """, unsafe_allow_html=True)

            name = st.text_input("Name", placeholder="Enter your name", label_visibility="collapsed")

            if st.button("Continue", type="primary", use_container_width=True, disabled=not name.strip()):
                st.session_state.onboarding_name = name.strip()
                st.session_state.onboarding_step = 1
                st.rerun()

        # ============================================
        # STEP 1: Level Selection
        # ============================================
        elif step == 1:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">📊</div>
                <h3 style="margin-bottom: 4px;">What's your current Spanish level?</h3>
                <p style="color: #8E8E93; font-size: 14px;">This helps us tailor content to your abilities</p>
            </div>
            """, unsafe_allow_html=True)

            # Level cards with descriptions
            levels = [
                {
                    "code": "B2",
                    "name": "Upper Intermediate",
                    "icon": "📗",
                    "desc": "You can handle most everyday situations and express opinions on familiar topics with some complexity."
                },
                {
                    "code": "C1",
                    "name": "Advanced",
                    "icon": "📘",
                    "desc": "You can express yourself fluently and spontaneously, using language flexibly for social, academic, and professional purposes."
                },
                {
                    "code": "C2",
                    "name": "Proficiency",
                    "icon": "📙",
                    "desc": "You can understand virtually everything and express yourself with precision, differentiating finer shades of meaning."
                }
            ]

            # Initialize selection if not set
            if "onboarding_level" not in st.session_state:
                st.session_state.onboarding_level = "C1"

            for lvl in levels:
                is_selected = st.session_state.get("onboarding_level") == lvl["code"]
                border_color = "#007AFF" if is_selected else "#E5E5EA"
                bg_color = "#eef2ff" if is_selected else "#ffffff"

                st.markdown(f"""
                <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 16px;
                            margin-bottom: 12px; background: {bg_color}; cursor: pointer;
                            transition: all 0.2s ease;">
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <div style="font-size: 24px;">{lvl['icon']}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #000000; margin-bottom: 2px;">
                                {lvl['code']} - {lvl['name']}
                            </div>
                            <div style="font-size: 13px; color: #8E8E93; line-height: 1.4;">
                                {lvl['desc']}
                            </div>
                        </div>
                        {'<div style="color: #007AFF; font-size: 20px;">✓</div>' if is_selected else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Select {lvl['code']}", key=f"level_{lvl['code']}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_level = lvl["code"]
                    st.rerun()

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_1"):
                    st.session_state.onboarding_step = 0
                    st.rerun()
            with col_b:
                if st.button("Continue →", type="primary", use_container_width=True, key="next_1"):
                    st.session_state.onboarding_step = 2
                    st.rerun()

        # ============================================
        # STEP 2: Learning Goal
        # ============================================
        elif step == 2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">🎯</div>
                <h3 style="margin-bottom: 4px;">What's your main goal?</h3>
                <p style="color: #8E8E93; font-size: 14px;">We'll prioritize content that matches your objectives</p>
            </div>
            """, unsafe_allow_html=True)

            goals = [
                {"icon": "💼", "label": "Professional communication", "desc": "Business meetings, emails, presentations"},
                {"icon": "🎓", "label": "Academic study", "desc": "University courses, research, exams"},
                {"icon": "✈️", "label": "Travel & culture", "desc": "Travel, cultural immersion, social situations"},
                {"icon": "🌟", "label": "General fluency", "desc": "Overall improvement across all skills"},
            ]

            if "onboarding_goal" not in st.session_state:
                st.session_state.onboarding_goal = "General fluency"

            for goal in goals:
                is_selected = st.session_state.get("onboarding_goal") == goal["label"]
                border_color = "#007AFF" if is_selected else "#E5E5EA"
                bg_color = "#eef2ff" if is_selected else "#ffffff"

                st.markdown(f"""
                <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 14px;
                            margin-bottom: 10px; background: {bg_color};">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 24px;">{goal['icon']}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: #000000;">{goal['label']}</div>
                            <div style="font-size: 12px; color: #8E8E93;">{goal['desc']}</div>
                        </div>
                        {'<div style="color: #007AFF; font-size: 18px;">✓</div>' if is_selected else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Select", key=f"goal_{goal['label']}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_goal = goal["label"]
                    st.rerun()

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_2"):
                    st.session_state.onboarding_step = 1
                    st.rerun()
            with col_b:
                if st.button("Continue →", type="primary", use_container_width=True, key="next_2"):
                    st.session_state.onboarding_step = 3
                    st.rerun()

        # ============================================
        # STEP 3: Dialect Preference
        # ============================================
        elif step == 3:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">🌎</div>
                <h3 style="margin-bottom: 4px;">Which Spanish dialect do you prefer?</h3>
                <p style="color: #8E8E93; font-size: 14px;">We'll adapt vocabulary and expressions to your preference</p>
            </div>
            """, unsafe_allow_html=True)

            dialects = [
                {"code": "Spain", "icon": "🇪🇸", "name": "Spain", "desc": "Castilian Spanish with vosotros"},
                {"code": "Mexico", "icon": "🇲🇽", "name": "Mexico", "desc": "Mexican Spanish, widely understood"},
                {"code": "Argentina", "icon": "🇦🇷", "name": "Argentina", "desc": "Rioplatense with vos conjugation"},
                {"code": "Colombia", "icon": "🇨🇴", "name": "Colombia", "desc": "Clear, neutral Latin American"},
                {"code": "Chile", "icon": "🇨🇱", "name": "Chile", "desc": "Chilean with unique expressions"},
            ]

            if "onboarding_dialect" not in st.session_state:
                st.session_state.onboarding_dialect = "Spain"

            # Display in 2 columns for compact layout
            cols = st.columns(2)
            for i, dialect in enumerate(dialects):
                is_selected = st.session_state.get("onboarding_dialect") == dialect["code"]
                border_color = "#007AFF" if is_selected else "#E5E5EA"
                bg_color = "#eef2ff" if is_selected else "#ffffff"

                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 12px;
                                margin-bottom: 10px; background: {bg_color}; text-align: center;">
                        <div style="font-size: 28px; margin-bottom: 4px;">{dialect['icon']}</div>
                        <div style="font-weight: 600; color: #000000;">{dialect['name']}</div>
                        <div style="font-size: 11px; color: #8E8E93;">{dialect['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"{'✓ ' if is_selected else ''}{dialect['name']}", key=f"dialect_{dialect['code']}",
                                use_container_width=True, type="primary" if is_selected else "secondary"):
                        st.session_state.onboarding_dialect = dialect["code"]
                        st.rerun()

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_3"):
                    st.session_state.onboarding_step = 2
                    st.rerun()
            with col_b:
                if st.button("Continue →", type="primary", use_container_width=True, key="next_3"):
                    st.session_state.onboarding_step = 4
                    st.rerun()

        # ============================================
        # STEP 4: Weekly Practice Goal
        # ============================================
        elif step == 4:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">📅</div>
                <h3 style="margin-bottom: 4px;">How often do you want to practice?</h3>
                <p style="color: #8E8E93; font-size: 14px;">Set a realistic weekly goal to build consistency</p>
            </div>
            """, unsafe_allow_html=True)

            weekly_options = [
                {"days": 3, "icon": "🌱", "label": "Light", "desc": "3 days/week - Great for busy schedules"},
                {"days": 4, "icon": "🌿", "label": "Moderate", "desc": "4 days/week - Steady progress"},
                {"days": 5, "icon": "🌳", "label": "Regular", "desc": "5 days/week - Recommended for best results"},
                {"days": 6, "icon": "🔥", "label": "Intensive", "desc": "6 days/week - Fast-track your learning"},
                {"days": 7, "icon": "⚡", "label": "Daily", "desc": "Every day - Maximum immersion"},
            ]

            if "onboarding_weekly_goal" not in st.session_state:
                st.session_state.onboarding_weekly_goal = 5

            for opt in weekly_options:
                is_selected = st.session_state.get("onboarding_weekly_goal") == opt["days"]
                border_color = "#007AFF" if is_selected else "#E5E5EA"
                bg_color = "#eef2ff" if is_selected else "#ffffff"

                st.markdown(f"""
                <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 14px;
                            margin-bottom: 10px; background: {bg_color};">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 24px;">{opt['icon']}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #000000;">
                                {opt['label']} <span style="color: #007AFF;">({opt['days']} days)</span>
                            </div>
                            <div style="font-size: 12px; color: #8E8E93;">{opt['desc']}</div>
                        </div>
                        {'<div style="color: #007AFF; font-size: 18px;">✓</div>' if is_selected else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Select {opt['days']} days", key=f"weekly_{opt['days']}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_weekly_goal = opt["days"]
                    st.rerun()

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_4"):
                    st.session_state.onboarding_step = 3
                    st.rerun()
            with col_b:
                if st.button("Continue →", type="primary", use_container_width=True, key="next_4"):
                    st.session_state.onboarding_step = 5
                    st.rerun()

        # ============================================
        # STEP 5: Focus Areas
        # ============================================
        elif step == 5:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 8px;">🎨</div>
                <h3 style="margin-bottom: 4px;">What do you want to focus on?</h3>
                <p style="color: #8E8E93; font-size: 14px;">Select all areas you'd like to improve (at least one)</p>
            </div>
            """, unsafe_allow_html=True)

            focus_options = [
                {"id": "Grammar", "icon": "📖", "label": "Grammar", "desc": "Verb tenses, subjunctive, sentence structure"},
                {"id": "Vocabulary", "icon": "📚", "label": "Vocabulary", "desc": "New words, idioms, collocations"},
                {"id": "Conversation", "icon": "💬", "label": "Conversation", "desc": "Speaking fluency, pronunciation, listening"},
                {"id": "Writing", "icon": "✍️", "label": "Writing", "desc": "Essays, emails, creative writing"},
            ]

            if "onboarding_focus_areas" not in st.session_state:
                st.session_state.onboarding_focus_areas = ["Grammar", "Vocabulary"]

            selected_areas = st.session_state.get("onboarding_focus_areas", [])

            cols = st.columns(2)
            for i, focus in enumerate(focus_options):
                is_selected = focus["id"] in selected_areas
                border_color = "#007AFF" if is_selected else "#E5E5EA"
                bg_color = "#eef2ff" if is_selected else "#ffffff"

                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 16px;
                                margin-bottom: 12px; background: {bg_color}; text-align: center;">
                        <div style="font-size: 32px; margin-bottom: 8px;">{focus['icon']}</div>
                        <div style="font-weight: 600; color: #000000; margin-bottom: 4px;">{focus['label']}</div>
                        <div style="font-size: 11px; color: #8E8E93; line-height: 1.3;">{focus['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = f"✓ {focus['label']}" if is_selected else focus['label']
                    if st.button(btn_label, key=f"focus_{focus['id']}", use_container_width=True,
                                type="primary" if is_selected else "secondary"):
                        current = list(st.session_state.get("onboarding_focus_areas", []))
                        if focus["id"] in current:
                            current.remove(focus["id"])
                        else:
                            current.append(focus["id"])
                        st.session_state.onboarding_focus_areas = current
                        st.rerun()

            # Show selected count
            st.markdown(f"""
            <div style="text-align: center; margin: 16px 0; color: #8E8E93; font-size: 13px;">
                {len(selected_areas)} area{'s' if len(selected_areas) != 1 else ''} selected
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_5"):
                    st.session_state.onboarding_step = 4
                    st.rerun()
            with col_b:
                can_finish = len(selected_areas) > 0
                if st.button("Start Learning 🚀", type="primary", use_container_width=True,
                            key="finish", disabled=not can_finish):
                    # Gather all onboarding data
                    name = st.session_state.get("onboarding_name", "Learner")
                    level = st.session_state.get("onboarding_level", "C1")
                    dialect = st.session_state.get("onboarding_dialect", "Spain")
                    weekly_goal = st.session_state.get("onboarding_weekly_goal", 5)
                    focus_areas = st.session_state.get("onboarding_focus_areas", ["Grammar", "Vocabulary"])

                    # Create profile with all preferences
                    profile_id = create_profile(
                        name=name,
                        level=level,
                        dialect_preference=dialect,
                        weekly_goal=weekly_goal,
                        focus_areas=focus_areas
                    )

                    if profile_id:
                        st.session_state.active_profile_id = profile_id
                        set_active_profile_id(profile_id)
                        st.session_state.show_onboarding = False
                        # Clean up onboarding state
                        for key in ["onboarding_step", "onboarding_name", "onboarding_level",
                                   "onboarding_goal", "onboarding_dialect", "onboarding_weekly_goal",
                                   "onboarding_focus_areas"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

        # Skip option
        render_html("<br>")
        if st.button("Skip setup", type="secondary"):
            profile_id = create_profile("Learner", "C1")
            if profile_id:
                st.session_state.active_profile_id = profile_id
                set_active_profile_id(profile_id)
                st.session_state.show_onboarding = False
                st.rerun()


# ============================================
# HOME / TODAY DASHBOARD
# ============================================

def render_home_page():
    """Render Today dashboard with useful modules filling the space."""
    profile = get_user_profile()
    stats = get_total_stats()

    # Get review counts
    vocab_due = len(get_vocab_for_review())
    errors_due = len(get_mistakes_for_review())
    grammar_due = len(get_grammar_for_review())
    total_due = vocab_due + errors_due + grammar_due

    # Greeting
    name = profile.get('name', 'there')
    st.markdown(f"## Good to see you, {name}")

    # ============================================
    # DASHBOARD GRID: Main (60%) + Rail (40%)
    # ============================================

    main_col, rail_col = st.columns([3, 2])

    with main_col:
        # ----------------------------------------
        # CONTINUE CARD (Primary action)
        # ----------------------------------------
        last_page = st.session_state.get("last_session", "Topic Diversity")

        render_html(f"""
            <div class="action-card action-card-primary" style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 32px;">▶️</div>
                    <div style="flex: 1;">
                        <div class="action-card-title">Continue Learning</div>
                        <div class="action-card-subtitle">Pick up where you left off</div>
                    </div>
                </div>
            </div>
        """)

        if st.button("Continue", type="primary", use_container_width=True, key="btn_continue"):
            st.session_state.current_page = last_page
            st.rerun()

        # ----------------------------------------
        # REVIEW DUE CARD
        # ----------------------------------------
        if total_due > 0:
            review_time = max(1, total_due // 2)
            render_html(f"""
                <div class="action-card" style="margin-bottom: 16px; margin-top: 16px;">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="font-size: 32px;">🔄</div>
                        <div style="flex: 1;">
                            <div class="action-card-title">Review Due</div>
                            <div class="action-card-subtitle">{total_due} items ready • ~{review_time} min</div>
                        </div>
                        <div style="text-align: right;">
                            <span class="pill pill-accent">{vocab_due} vocab</span>
                            {f'<span class="pill pill-error" style="margin-left: 4px;">{errors_due} errors</span>' if errors_due > 0 else ''}
                        </div>
                    </div>
                </div>
            """)

            if st.button("Start Review", use_container_width=True, key="btn_review"):
                st.session_state.current_page = "Review"
                st.rerun()

        # ----------------------------------------
        # QUICK 5 MIN SESSION
        # ----------------------------------------
        render_html("""
            <div class="action-card" style="margin-top: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 32px;">⚡</div>
                    <div style="flex: 1;">
                        <div class="action-card-title">Quick 5 min session</div>
                        <div class="action-card-subtitle">Mixed practice: vocab + grammar + listening</div>
                    </div>
                </div>
            </div>
        """)

        if st.button("Start Quick Session", use_container_width=True, key="btn_quick"):
            st.session_state.quick_session_mode = True
            st.session_state.current_page = "Review"
            st.rerun()

        # ----------------------------------------
        # RECOMMENDED NEXT
        # ----------------------------------------
        st.markdown("### Recommended")

        rec_cols = st.columns(2)
        recommendations = [
            {"icon": "💬", "title": "Conversation Practice", "desc": "Practice speaking scenarios", "page": "Conversation"},
            {"icon": "✍️", "title": "Writing Coach", "desc": "Get feedback on your writing", "page": "Writing Coach"},
        ]

        for i, rec in enumerate(recommendations):
            with rec_cols[i]:
                render_html(f"""
                    <div class="card" style="text-align: center; padding: 20px;">
                        <div style="font-size: 28px; margin-bottom: 8px;">{rec['icon']}</div>
                        <div style="font-weight: 600; margin-bottom: 4px;">{rec['title']}</div>
                        <div style="font-size: 13px; color: var(--text-muted);">{rec['desc']}</div>
                    </div>
                """)
                if st.button("Start", key=f"rec_{i}", use_container_width=True):
                    st.session_state.current_page = rec['page']
                    st.rerun()

    # ----------------------------------------
    # RIGHT RAIL - Stats
    # ----------------------------------------
    with rail_col:
        # Streak
        streak = get_streak_days(get_progress_history())
        render_html(f"""
            <div class="stat-card" style="margin-bottom: 12px; text-align: center;">
                <div style="font-size: 36px; margin-bottom: 4px;">🔥</div>
                <div class="stat-value">{streak}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        """)

        # Weekly goal
        weekly_goal = profile.get('weekly_goal', 6)
        sessions_this_week = get_sessions_this_week()
        progress_pct = sessions_this_week / weekly_goal if weekly_goal > 0 else 0

        render_html(f"""
            <div class="stat-card" style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 500;">Weekly Goal</span>
                    <span style="color: var(--text-muted);">{sessions_this_week}/{weekly_goal}</span>
                </div>
                <div style="background: var(--bg-elevated); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: var(--accent); height: 100%; width: {progress_pct * 100}%; border-radius: 4px;"></div>
                </div>
            </div>
        """)

        # Words learned
        render_html(f"""
            <div class="stat-card" style="margin-bottom: 12px;">
                <div class="stat-value">{stats.get('total_vocab', 0)}</div>
                <div class="stat-label">Words Learned</div>
            </div>
        """)

        # Speaking time
        render_html(f"""
            <div class="stat-card" style="margin-bottom: 12px;">
                <div class="stat-value">{stats.get('total_speaking', 0):.0f}</div>
                <div class="stat-label">Minutes Speaking</div>
            </div>
        """)

        # Weak areas
        st.markdown("### Focus Areas")
        weak_areas = get_weak_areas()
        if not weak_areas:
            weak_areas = ["Start practicing to see your focus areas"]
        for area in weak_areas[:3]:
            render_html(f"""
                <div style="padding: 8px 12px; background: var(--bg-surface); border-radius: 6px;
                            margin-bottom: 8px; font-size: 13px; border-left: 3px solid var(--warning);">
                    {area}
                </div>
            """)


# ============================================
# LEARN PAGE
# ============================================

def render_learn_page():
    """Render Learn page with vocabulary and grammar paths."""
    st.markdown("## Learn")
    st.markdown("Build your vocabulary and grammar skills")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_html("""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 12px;">📚</div>
                <h3>Vocabulary</h3>
                <p style="color: var(--text-muted);">Learn new words in context with the Topic Diversity Engine</p>
            </div>
        """)
        if st.button("Start Vocabulary", type="primary", use_container_width=True, key="learn_vocab"):
            st.session_state.current_page = "Topic Diversity"
            st.session_state.last_session = "Topic Diversity"
            st.rerun()

    with col2:
        render_html("""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 12px;">🔤</div>
                <h3>Verb Mastery</h3>
                <p style="color: var(--text-muted);">Master verb nuances, tenses, and near-synonyms</p>
            </div>
        """)
        if st.button("Start Verbs", type="primary", use_container_width=True, key="learn_verbs"):
            st.session_state.current_page = "Verb Studio"
            st.session_state.last_session = "Verb Studio"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="card">
            <div style="font-size: 32px; margin-bottom: 12px;">🧩</div>
            <h3>Context Units</h3>
            <p style="color: var(--text-muted);">Practice chunked phrases and contextual grammar patterns</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Context Units", type="primary", use_container_width=True, key="learn_context"):
            st.session_state.current_page = "Context Units"
            st.session_state.last_session = "Context Units"
            st.rerun()

    with col3:
        render_html("""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 12px;">🧩</div>
                <h3>Context Units</h3>
                <p style="color: var(--text-muted);">Practice chunked phrases and contextual grammar patterns</p>
            </div>
        """)
        if st.button("Start Context Units", type="primary", use_container_width=True, key="learn_context"):
            st.session_state.current_page = "Context Units"
            st.session_state.last_session = "Context Units"
            st.rerun()

    with col3:
        render_html("""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 12px;">🧩</div>
                <h3>Context Units</h3>
                <p style="color: var(--text-muted);">Practice chunked phrases and contextual grammar patterns</p>
            </div>
        """)
        if st.button("Start Context Units", type="primary", use_container_width=True, key="learn_context"):
            st.session_state.current_page = "Context Units"
            st.session_state.last_session = "Context Units"
            st.rerun()

    with col3:
        render_html("""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 12px;">🧩</div>
                <h3>Context Units</h3>
                <p style="color: var(--text-muted);">Practice chunked phrases and contextual grammar patterns</p>
            </div>
        """)
        if st.button("Start Context Units", type="primary", use_container_width=True, key="learn_context"):
            st.session_state.current_page = "Context Units"
            st.session_state.last_session = "Context Units"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="card">
            <div style="font-size: 32px; margin-bottom: 12px;">🧩</div>
            <h3>Context Units</h3>
            <p style="color: #8E8E93;">Practice chunked phrases and contextual grammar patterns</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Context Units", type="primary", use_container_width=True, key="learn_context_units"):
            st.session_state.current_page = "Context Units"
            st.session_state.last_session = "Context Units"
            st.rerun()


# ============================================
# PRACTICE PAGE
# ============================================

def render_practice_page():
    """Render Practice page with different skill modes."""
    st.markdown("## Practice")
    st.markdown("Apply your skills in realistic scenarios")

    # Practice modes
    modes = [
        {"icon": "💬", "title": "Conversation", "desc": "Practice speaking in real scenarios", "page": "Conversation"},
        {"icon": "✍️", "title": "Writing", "desc": "Get feedback on your written Spanish", "page": "Writing Coach"},
        {"icon": "🔤", "title": "Verbs", "desc": "Drill verb conjugations and usage", "page": "Verb Studio"},
        {"icon": "🎯", "title": "Quick Drills", "desc": "Fast-paced mixed practice", "page": "Topic Diversity"},
    ]

    cols = st.columns(2)
    for i, mode in enumerate(modes):
        with cols[i % 2]:
            render_html(f"""
                <div class="card">
                    <div style="font-size: 28px; margin-bottom: 8px;">{mode['icon']}</div>
                    <h4>{mode['title']}</h4>
                    <p style="color: var(--text-muted); font-size: 14px;">{mode['desc']}</p>
                </div>
            """)
            if st.button(f"Start {mode['title']}", key=f"practice_{i}", use_container_width=True):
                st.session_state.current_page = mode['page']
                st.session_state.last_session = mode['page']
                st.rerun()

    # Tools section
    st.divider()
    st.markdown("### Tools")

    tool_cols = st.columns(3)
    tools = [
        {"icon": "🌎", "title": "Dialect Guide", "page": "Dialects"},
        {"icon": "🏛️", "title": "Memory Palace", "page": "Memory Palace"},
        {"icon": "✏️", "title": "Error Patterns", "page": "Mistake Catcher"},
    ]

    for i, tool in enumerate(tools):
        with tool_cols[i]:
            if st.button(f"{tool['icon']} {tool['title']}", key=f"tool_{i}", use_container_width=True):
                st.session_state.current_page = tool['page']
                st.rerun()


# ============================================
# PROGRESS PAGE
# ============================================

def render_progress_page():
    """Render comprehensive Progress page with visualizations and insights."""
    st.markdown("## Your Progress")
    st.markdown("Track your Spanish learning journey")

    # Gather all data
    stats = get_total_stats()
    profile = get_user_profile()
    progress_history = get_progress_history(days=30)
    streak = get_streak_days(progress_history)
    sessions_this_week = get_sessions_this_week()
    weak_areas = get_weak_areas()
    learning_velocity = get_learning_velocity()
    activity_history = get_activity_history(days=30)
    mistake_stats = get_mistake_stats()
    vocab_items = get_vocab_items()

    # Calculate derived metrics
    mastered_vocab = len([v for v in vocab_items if v.get('status') == 'mastered'])
    learning_vocab = len([v for v in vocab_items if v.get('status') == 'learning'])
    total_vocab_count = len(vocab_items)

    # ============================================
    # TOP STATS ROW
    # ============================================
    st.markdown("### Overview")
    cols = st.columns(5)

    with cols[0]:
        render_html(f"""
            <div class="stat-card" style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">🔥</div>
                <div class="stat-value">{streak}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        """)

    with cols[1]:
        render_html(f"""
            <div class="stat-card" style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">📚</div>
                <div class="stat-value">{stats.get('total_vocab', 0)}</div>
                <div class="stat-label">Words</div>
            </div>
        """)

    with cols[2]:
        render_html(f"""
            <div class="stat-card" style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">🎤</div>
                <div class="stat-value">{stats.get('total_speaking', 0):.0f}</div>
                <div class="stat-label">Min Speaking</div>
            </div>
        """)

    with cols[3]:
        render_html(f"""
            <div class="stat-card" style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 4px;">🎯</div>
                <div class="stat-value">{stats.get('total_missions', 0)}</div>
                <div class="stat-label">Missions</div>
            </div>
        """)

    st.divider()

    # ============================================
    # WEEKLY REPORT SECTION
    # ============================================
    st.markdown("### Weekly Report")

    # Calculate weekly stats
    week_ago = date.today() - timedelta(days=7)
    weekly_history = [h for h in progress_history if h.get('metric_date', '') >= week_ago.isoformat()]

    weekly_vocab_reviewed = sum(h.get('vocab_reviewed', 0) for h in weekly_history)
    weekly_errors_fixed = sum(h.get('errors_fixed', 0) for h in weekly_history)
    weekly_speaking = sum(h.get('speaking_minutes', 0) for h in weekly_history)
    weekly_missions = sum(h.get('missions_completed', 0) for h in weekly_history)

    # New words this week (from vocab_items created this week)
    new_words_this_week = len([v for v in vocab_items
                               if v.get('created_at', '')[:10] >= week_ago.isoformat()])

    # Weekly goal progress
    weekly_goal = profile.get('weekly_goal', 6)
    goal_progress = min(100, (sessions_this_week / weekly_goal * 100)) if weekly_goal > 0 else 0

    report_col1, report_col2 = st.columns(2)

    with report_col1:
        st.markdown("""
        <div class="card" style="padding: 20px;">
            <h4 style="margin-bottom: 16px; color: #000000;">This Week's Activity</h4>
        """, unsafe_allow_html=True)

        # Weekly goal progress bar
        st.markdown(f"""
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 500; color: #3C3C43;">Weekly Goal</span>
                    <span style="color: #8E8E93;">{sessions_this_week}/{weekly_goal} days</span>
                </div>
                <div style="background: #E5E5EA; height: 10px; border-radius: 5px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #007AFF, #8b5cf6); height: 100%;
                                width: {goal_progress}%; border-radius: 5px; transition: width 0.3s;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Weekly stats grid
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="background: #F2F2F7; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #007AFF;">{weekly_vocab_reviewed}</div>
                    <div style="font-size: 12px; color: #8E8E93; text-transform: uppercase;">Items Reviewed</div>
                </div>
                <div style="background: #F2F2F7; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #10b981;">{new_words_this_week}</div>
                    <div style="font-size: 12px; color: #8E8E93; text-transform: uppercase;">New Words</div>
                </div>
                <div style="background: #F2F2F7; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #f59e0b;">{weekly_errors_fixed}</div>
                    <div style="font-size: 12px; color: #8E8E93; text-transform: uppercase;">Errors Fixed</div>
                </div>
                <div style="background: #F2F2F7; padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #3b82f6;">{weekly_speaking:.0f}</div>
                    <div style="font-size: 12px; color: #8E8E93; text-transform: uppercase;">Min Speaking</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with report_col2:
        # Streak and motivation
        st.markdown(f"""
        <div class="card" style="padding: 20px;">
            <h4 style="margin-bottom: 16px; color: #000000;">Streak & Motivation</h4>
            <div style="text-align: center; padding: 16px; background: linear-gradient(135deg, #fef3c7, #fde68a);
                        border-radius: 12px; margin-bottom: 16px;">
                <div style="font-size: 48px;">🔥</div>
                <div style="font-size: 36px; font-weight: 700; color: #b45309;">{streak}</div>
                <div style="color: #92400e; font-weight: 500;">Day Streak</div>
            </div>
        """, unsafe_allow_html=True)

        # Motivational message based on streak
        if streak == 0:
            message = "Start your streak today! Every journey begins with a single step."
            emoji = "🌱"
        elif streak < 7:
            message = "Great start! Keep going to build a strong habit."
            emoji = "💪"
        elif streak < 30:
            message = "Fantastic consistency! You're building real momentum."
            emoji = "🌟"
        elif streak < 100:
            message = "Incredible dedication! You're mastering the art of consistency."
            emoji = "🏆"
        else:
            message = "Legendary! Your commitment is truly inspiring."
            emoji = "👑"

        st.markdown(f"""
            <div style="text-align: center; padding: 12px; background: #f0fdf4; border-radius: 8px;
                        border: 1px solid #bbf7d0;">
                <span style="font-size: 24px;">{emoji}</span>
                <p style="color: #166534; margin: 8px 0 0 0; font-size: 14px;">{message}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ============================================
    # WEEKLY ACTIVITY CHART
    # ============================================
    st.markdown("### Weekly Activity")

    # Create activity data for last 7 days
    activity_by_day = {}
    for i in range(7):
        day = date.today() - timedelta(days=6-i)
        activity_by_day[day.strftime('%a')] = {'active': False, 'items': 0}

    # Mark active days from progress history
    for h in progress_history:
        try:
            h_date = datetime.strptime(h.get('metric_date', '')[:10], '%Y-%m-%d').date()
            if h_date >= week_ago:
                day_name = h_date.strftime('%a')
                if day_name in activity_by_day:
                    items = (h.get('vocab_reviewed', 0) + h.get('grammar_reviewed', 0) +
                             h.get('errors_fixed', 0))
                    if items > 0:
                        activity_by_day[day_name] = {'active': True, 'items': items}
        except (ValueError, TypeError):
            pass

    # Render activity chart
    day_cols = st.columns(7)
    for i, (day_name, data) in enumerate(activity_by_day.items()):
        with day_cols[i]:
            is_today = i == 6
            bg_color = "#10b981" if data['active'] else ("#E5E5EA" if not is_today else "#fef3c7")
            text_color = "#ffffff" if data['active'] else ("#8E8E93" if not is_today else "#b45309")
            border = "2px solid #007AFF" if is_today else "none"

            st.markdown(f"""
            <div style="text-align: center;">
                <div style="width: 48px; height: 48px; border-radius: 12px; background: {bg_color};
                            display: flex; align-items: center; justify-content: center; margin: 0 auto 8px;
                            border: {border};">
                    <span style="color: {text_color}; font-weight: 600;">
                        {"✓" if data['active'] else (day_name[0] if not is_today else "?")}
                    </span>
                </div>
                <div style="font-size: 12px; color: #8E8E93;">{day_name}</div>
                {f'<div style="font-size: 11px; color: #10b981;">{data["items"]} items</div>' if data['active'] else ''}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ============================================
    # VOCABULARY GROWTH & ERROR TRENDS
    # ============================================
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### Vocabulary Growth")

        # Group vocab by week
        vocab_by_week = defaultdict(int)
        for v in vocab_items:
            try:
                created = v.get('created_at', '')[:10]
                if created:
                    week_start = datetime.strptime(created, '%Y-%m-%d').date()
                    week_start = week_start - timedelta(days=week_start.weekday())
                    vocab_by_week[week_start.isoformat()] += 1
            except (ValueError, TypeError):
                pass

        if vocab_by_week:
            # Show last 4 weeks
            sorted_weeks = sorted(vocab_by_week.keys())[-4:]
            cumulative = 0

            st.markdown('<div class="card" style="padding: 16px;">', unsafe_allow_html=True)
            for week in sorted_weeks:
                cumulative += vocab_by_week[week]
                week_display = datetime.strptime(week, '%Y-%m-%d').strftime('%b %d')
                bar_width = min(100, (vocab_by_week[week] / max(vocab_by_week.values()) * 100)) if vocab_by_week else 0

                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 13px; color: #8E8E93;">{week_display}</span>
                        <span style="font-size: 13px; font-weight: 500; color: #000000;">+{vocab_by_week[week]} words</span>
                    </div>
                    <div style="background: #E5E5EA; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #007AFF, #8b5cf6); height: 100%;
                                    width: {bar_width}%; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="text-align: center; padding-top: 12px; border-top: 1px solid #E5E5EA;">
                    <span style="font-size: 24px; font-weight: 700; color: #007AFF;">{total_vocab_count}</span>
                    <span style="color: #8E8E93;"> total words</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            render_empty_state("Start learning to see your vocabulary growth!", "📈")

    with chart_col2:
        st.markdown("### Error Patterns")

        if mistake_stats:
            st.markdown('<div class="card" style="padding: 16px;">', unsafe_allow_html=True)

            # Sort by count
            sorted_errors = sorted(mistake_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:5]
            max_count = max(e[1].get('count', 1) for e in sorted_errors) if sorted_errors else 1

            for error_type, data in sorted_errors:
                count = data.get('count', 0)
                avg_ease = data.get('avg_ease', 2.5)
                bar_width = (count / max_count * 100) if max_count > 0 else 0

                # Color based on improvement (higher ease = more improved)
                if avg_ease >= 2.8:
                    bar_color = "#10b981"  # Green - improving
                    status = "Improving"
                elif avg_ease >= 2.2:
                    bar_color = "#f59e0b"  # Yellow - working on it
                    status = "In Progress"
                else:
                    bar_color = "#ef4444"  # Red - needs work
                    status = "Needs Focus"

                st.markdown(f"""
                <div style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 13px; color: #000000;">{error_type.replace('_', ' ').title()}</span>
                        <span style="font-size: 11px; color: {bar_color}; font-weight: 500;">{status}</span>
                    </div>
                    <div style="background: #E5E5EA; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: {bar_color}; height: 100%; width: {bar_width}%; border-radius: 4px;"></div>
                    </div>
                    <div style="font-size: 11px; color: #8E8E93; margin-top: 2px;">{count} occurrences</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            render_empty_state("Complete exercises to track your error patterns!", "🎯")

    st.divider()

    # ============================================
    # TIME SPENT BY ACTIVITY
    # ============================================
    st.markdown("### Time by Activity")

    # Aggregate time by activity type
    time_by_activity = defaultdict(int)
    for activity in activity_history:
        act_type = activity.get('activity_type', 'other')
        duration = activity.get('duration_seconds', 0)
        time_by_activity[act_type] += duration

    if time_by_activity:
        # Convert to minutes and sort
        time_minutes = {k: v / 60 for k, v in time_by_activity.items()}
        sorted_activities = sorted(time_minutes.items(), key=lambda x: x[1], reverse=True)[:6]
        total_time = sum(time_minutes.values())

        activity_icons = {
            'vocab_review': '📚',
            'conversation': '💬',
            'writing': '✍️',
            'speaking': '🎤',
            'grammar': '📝',
            'review': '🔄',
            'flashcard': '🃏',
            'exercise': '🎯',
        }

        activity_names = {
            'vocab_review': 'Vocabulary',
            'conversation': 'Conversation',
            'writing': 'Writing',
            'speaking': 'Speaking',
            'grammar': 'Grammar',
            'review': 'Review',
            'flashcard': 'Flashcards',
            'exercise': 'Exercises',
        }

        act_cols = st.columns(min(len(sorted_activities), 6))
        for i, (act_type, minutes) in enumerate(sorted_activities):
            if i < len(act_cols):
                with act_cols[i]:
                    icon = activity_icons.get(act_type, '📌')
                    name = activity_names.get(act_type, act_type.replace('_', ' ').title())
                    pct = (minutes / total_time * 100) if total_time > 0 else 0

                    st.markdown(f"""
                    <div class="stat-card" style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
                        <div style="font-size: 20px; font-weight: 700; color: #000000;">{minutes:.0f}</div>
                        <div style="font-size: 12px; color: #8E8E93;">minutes</div>
                        <div style="font-size: 11px; color: #007AFF; margin-top: 4px;">{pct:.0f}%</div>
                        <div style="font-size: 12px; color: #3C3C43; margin-top: 4px;">{name}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        render_empty_state("Activity time tracking will appear as you practice!", "⏱️")

    st.divider()

    # ============================================
    # LEARNING MILESTONES
    # ============================================
    st.markdown("### Learning Milestones")

    # Define milestones
    vocab_milestones = [
        (50, "Beginner", "🌱"),
        (100, "Getting Started", "🌿"),
        (250, "Building Foundation", "🌳"),
        (500, "Solid Progress", "⭐"),
        (1000, "Advanced Learner", "🌟"),
        (2500, "Expert Level", "💫"),
        (5000, "Master", "👑"),
    ]

    streak_milestones = [
        (7, "One Week", "🔥"),
        (30, "One Month", "🔥🔥"),
        (100, "100 Days", "🔥🔥🔥"),
        (365, "One Year", "🏆"),
    ]

    errors_fixed = stats.get('total_errors', 0)
    error_milestones = [
        (10, "First Corrections", "🔧"),
        (50, "Active Learner", "🛠️"),
        (100, "Error Hunter", "🎯"),
        (500, "Perfectionist", "💎"),
    ]

    milestone_col1, milestone_col2, milestone_col3 = st.columns(3)

    with milestone_col1:
        st.markdown("""
        <div class="card" style="padding: 16px;">
            <h4 style="margin-bottom: 12px; color: #000000;">📚 Vocabulary</h4>
        """, unsafe_allow_html=True)

        for threshold, name, emoji in vocab_milestones:
            achieved = total_vocab_count >= threshold
            opacity = "1" if achieved else "0.4"
            check = "✓" if achieved else ""

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;
                        opacity: {opacity}; border-bottom: 1px solid #F2F2F7;">
                <span style="font-size: 20px;">{emoji}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 500; color: #000000;">{threshold} words</div>
                    <div style="font-size: 12px; color: #8E8E93;">{name}</div>
                </div>
                <span style="color: #10b981; font-weight: 600;">{check}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with milestone_col2:
        st.markdown("""
        <div class="card" style="padding: 16px;">
            <h4 style="margin-bottom: 12px; color: #000000;">🔥 Streak</h4>
        """, unsafe_allow_html=True)

        for threshold, name, emoji in streak_milestones:
            achieved = streak >= threshold
            opacity = "1" if achieved else "0.4"
            check = "✓" if achieved else ""

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;
                        opacity: {opacity}; border-bottom: 1px solid #F2F2F7;">
                <span style="font-size: 20px;">{emoji}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 500; color: #000000;">{threshold} days</div>
                    <div style="font-size: 12px; color: #8E8E93;">{name}</div>
                </div>
                <span style="color: #10b981; font-weight: 600;">{check}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with milestone_col3:
        st.markdown("""
        <div class="card" style="padding: 16px;">
            <h4 style="margin-bottom: 12px; color: #000000;">🎯 Errors Fixed</h4>
        """, unsafe_allow_html=True)

        for threshold, name, emoji in error_milestones:
            achieved = errors_fixed >= threshold
            opacity = "1" if achieved else "0.4"
            check = "✓" if achieved else ""

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;
                        opacity: {opacity}; border-bottom: 1px solid #F2F2F7;">
                <span style="font-size: 20px;">{emoji}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 500; color: #000000;">{threshold} errors</div>
                    <div style="font-size: 12px; color: #8E8E93;">{name}</div>
                </div>
                <span style="color: #10b981; font-weight: 600;">{check}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ============================================
    # AREAS TO FOCUS & IMPROVED AREAS
    # ============================================
    focus_col1, focus_col2 = st.columns(2)

    with focus_col1:
        st.markdown("### Areas Needing Work")
        if weak_areas:
            for i, area in enumerate(weak_areas[:5]):
                priority_colors = ["#ef4444", "#f59e0b", "#eab308", "#84cc16", "#22c55e"]
                color = priority_colors[min(i, len(priority_colors)-1)]

                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 12px;
                            background: #ffffff; border: 1px solid #E5E5EA; border-left: 4px solid {color};
                            border-radius: 8px; margin-bottom: 8px;">
                    <div style="font-size: 18px; width: 28px; height: 28px; background: {color}20;
                                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                color: {color}; font-weight: 600;">{i+1}</div>
                    <div style="color: #000000; font-weight: 500;">{area}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 24px; background: #f0fdf4; border-radius: 12px;
                        border: 1px solid #bbf7d0;">
                <div style="font-size: 32px; margin-bottom: 8px;">🎉</div>
                <div style="color: #166534; font-weight: 500;">No weak areas identified yet!</div>
                <div style="color: #15803d; font-size: 14px;">Keep practicing to discover areas to improve.</div>
            </div>
            """, unsafe_allow_html=True)

    with focus_col2:
        st.markdown("### Strengths")

        # Analyze fingerprint summary for improved areas
        fingerprint_summary = get_fingerprint_summary()

        if fingerprint_summary:
            # Find categories with high confidence (improved areas)
            strong_areas = [
                (cat, data) for cat, data in fingerprint_summary.items()
                if data.get('avg_confidence', 0) >= 0.7 and data.get('total_correct', 0) > 5
            ]
            strong_areas.sort(key=lambda x: x[1].get('avg_confidence', 0), reverse=True)

            if strong_areas:
                for cat, data in strong_areas[:5]:
                    confidence = data.get('avg_confidence', 0) * 100
                    cat_display = cat.replace('_', ' ').title()

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px;
                                background: #f0fdf4; border: 1px solid #bbf7d0;
                                border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-size: 18px;">✓</div>
                        <div style="flex: 1;">
                            <div style="color: #166534; font-weight: 500;">{cat_display}</div>
                        </div>
                        <div style="color: #15803d; font-weight: 600;">{confidence:.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 24px; background: #F2F2F7; border-radius: 12px;
                            border: 1px solid #E5E5EA;">
                    <div style="font-size: 32px; margin-bottom: 8px;">💪</div>
                    <div style="color: #3C3C43; font-weight: 500;">Keep practicing!</div>
                    <div style="color: #8E8E93; font-size: 14px;">Your strengths will appear as you improve.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 24px; background: #F2F2F7; border-radius: 12px;
                        border: 1px solid #E5E5EA;">
                <div style="font-size: 32px; margin-bottom: 8px;">📊</div>
                <div style="color: #3C3C43; font-weight: 500;">Analysis in progress</div>
                <div style="color: #8E8E93; font-size: 14px;">Complete more exercises to see your strengths.</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ============================================
    # QUICK ACTIONS
    # ============================================
    st.markdown("### Take Action")

    action_cols = st.columns(3)

    with action_cols[0]:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
            <div style="font-weight: 600; color: #000000;">My Spanish Portfolio</div>
            <div style="font-size: 13px; color: #8E8E93; margin-bottom: 12px;">View your complete learning record</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Portfolio", use_container_width=True, key="prog_portfolio"):
            st.session_state.current_page = "My Spanish"
            st.rerun()

    with action_cols[1]:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
            <div style="font-weight: 600; color: #000000;">Error Analysis</div>
            <div style="font-size: 13px; color: #8E8E93; margin-bottom: 12px;">Deep dive into your error patterns</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Errors", use_container_width=True, key="prog_errors"):
            st.session_state.current_page = "Error Notebook"
            st.rerun()

    with action_cols[2]:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🔄</div>
            <div style="font-weight: 600; color: #000000;">Start Review</div>
            <div style="font-size: 13px; color: #8E8E93; margin-bottom: 12px;">Review items due today</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Review", type="primary", use_container_width=True, key="prog_review"):
            st.session_state.current_page = "Review"
            st.rerun()


# ============================================
# PAGE IMPORTS
# ============================================

from pages.topic_diversity import render_topic_diversity_page
from pages.context_units import render_context_units_page
from pages.verb_studio import render_verb_studio_page
from pages.mistake_catcher import render_mistake_catcher_page
from pages.daily_missions import render_daily_missions_page
from pages.conversation import render_conversation_page
from pages.review_hub import render_review_hub_page
from pages.error_notebook import render_error_notebook_page
from pages.content_ingest import render_content_ingest_page
from pages.settings import render_settings_page
from pages.fingerprint_dashboard import render_fingerprint_dashboard
from pages.writing_coach import render_writing_coach_page
from pages.dialect_navigator import render_dialect_navigator_page
from pages.memory_palace import render_memory_palace_page
from pages.my_spanish import render_my_spanish_page


# ============================================
# MAIN
# ============================================

def main():
    """Main application entry point."""
    # Show onboarding for new users
    if st.session_state.show_onboarding or st.session_state.active_profile_id is None:
        render_onboarding()
        return

    # Render sidebar
    render_sidebar()

    # Route to page
    page = st.session_state.current_page

    page_map = {
        "Home": render_home_page,
        "Learn": render_learn_page,
        "Practice": render_practice_page,
        "Progress": render_progress_page,
        "Review": render_review_hub_page,
        "Settings": render_settings_page,
        # Sub-pages
        "Topic Diversity": render_topic_diversity_page,
        "Context Units": render_context_units_page,
        "Verb Studio": render_verb_studio_page,
        "Mistake Catcher": render_mistake_catcher_page,
        "Daily Missions": render_daily_missions_page,
        "Conversation": render_conversation_page,
        "Writing Coach": render_writing_coach_page,
        "Dialects": render_dialect_navigator_page,
        "Memory Palace": render_memory_palace_page,
        "My Spanish": render_my_spanish_page,
        "Error Notebook": render_error_notebook_page,
        "Fingerprint": render_fingerprint_dashboard,
        "Content Ingest": render_content_ingest_page,
    }

    renderer = page_map.get(page, render_home_page)
    renderer()


if __name__ == "__main__":
    main()
