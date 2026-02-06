"""
VivaLingo - Spanish Learning Platform
Clean, focused interface for C1-C2 learners.
"""
import streamlit as st
import random
from datetime import date, datetime, timedelta
from collections import defaultdict

# Database imports
from utils.database import (
    init_db, get_user_profile, update_user_profile, get_total_stats,
    get_vocab_for_review, get_mistakes_for_review, get_grammar_for_review,
    get_progress_history, get_all_profiles, create_profile,
    set_active_profile_id, get_active_profile_id, get_profile_stats,
    get_sessions_this_week, get_weak_areas, get_learning_velocity,
    get_activity_history, get_mistake_stats, get_fingerprint_summary,
    get_vocab_items, get_active_vocab_count
)

# Theme imports
from utils.theme import (
    apply_theme, get_css, render_hero, render_section_header, render_stat_card,
    render_action_card, render_feedback, render_streak_badge,
    render_empty_state, render_loading_skeleton, render_html,
    render_metric_grid, render_progress_bar
)
from utils.helpers import get_streak_days

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="VivaLingo",
    page_icon="https://em-content.zobj.net/source/twitter/408/flag-spain_1f1ea-1f1f8.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme (CSS + auto-clean HTML monkey-patch)
apply_theme()

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
        "last_session": None,
        "quick_session_mode": False,
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

NAV_ITEMS = [
    {"icon": "🏠", "label": "Home", "page": "Home"},
    {"icon": "📚", "label": "Learn", "page": "Learn"},
    {"icon": "🔄", "label": "Review", "page": "Review"},
    {"icon": "🎯", "label": "Practice", "page": "Practice"},
    {"icon": "📊", "label": "Progress", "page": "Progress"},
    {"icon": "⚙️", "label": "Settings", "page": "Settings"},
]


# ============================================
# SIDEBAR
# ============================================

def render_sidebar():
    """Render clean sidebar navigation."""
    with st.sidebar:
        # App header
        render_html("""
            <div style="padding: 0.75rem 0 1rem 0; margin-bottom: 1rem;
                        border-bottom: 1px solid var(--border);">
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--text);
                            display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">&#x1F1EA;&#x1F1F8;</span> VivaLingo
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.125rem;">
                    Spanish Mastery Platform
                </div>
            </div>
        """)

        # Profile info
        profile = get_user_profile()
        if profile.get("name"):
            streak = get_streak_days(get_progress_history())
            initial = profile['name'][0].upper()
            render_html(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem;
                            background: var(--surface-alt); border-radius: 0.75rem; margin-bottom: 1rem;">
                    <div style="width: 2.25rem; height: 2.25rem; border-radius: 50%;
                                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                                display: flex; align-items: center; justify-content: center;
                                color: white; font-weight: 700; font-size: 0.875rem;">{initial}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: 600; color: var(--text); font-size: 0.875rem;
                                    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {profile['name']}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted);">
                            Level {profile.get('level', 'C1')}
                        </div>
                    </div>
                    {'<div style="font-size: 0.8rem; font-weight: 600; color: var(--orange);">🔥 ' + str(streak) + '</div>' if streak > 0 else ''}
                </div>
            """)

        # Review due notification
        vocab_due = len(get_vocab_for_review())
        errors_due = len(get_mistakes_for_review())
        total_due = vocab_due + errors_due

        if total_due > 0:
            render_html(f"""
                <div style="background: var(--primary-light); border: 1px solid #A7F3D0;
                            border-radius: 0.5rem; padding: 0.625rem 0.75rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.8rem; color: #065F46; font-weight: 600;">
                        📋 {total_due} items due for review
                    </div>
                </div>
            """)

        # Navigation label
        render_html('<div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 0.5rem; padding-left: 0.25rem;">Navigation</div>')

        # Navigation buttons
        for item in NAV_ITEMS:
            is_active = st.session_state.current_page == item["page"]
            if st.button(
                f"{item['icon']}  {item['label']}",
                key=f"nav_{item['page']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = item["page"]
                st.rerun()

        # Admin tools
        profile = get_user_profile()
        if profile.get("is_admin"):
            render_html('<hr style="margin: 1.25rem 0; border: none; border-top: 1px solid var(--border);">')
            render_html('<div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-bottom: 0.5rem; padding-left: 0.25rem;">Developer</div>')
            admin_pages = [
                ("📥 Content Ingest", "Content Ingest"),
                ("📓 Error Notebook", "Error Notebook"),
                ("🔍 Fingerprint", "Fingerprint"),
            ]
            for label, page in admin_pages:
                if st.button(label, key=f"admin_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()


# ============================================
# ONBOARDING
# ============================================

def render_onboarding():
    """Render onboarding flow for new users."""
    step = st.session_state.onboarding_step
    total_steps = 6

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        render_html("""
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <div style="font-size: 3rem; margin-bottom: 0.75rem;">&#x1F1EA;&#x1F1F8;</div>
                <h1 style="margin-bottom: 0.25rem; font-size: 2rem;">Welcome to VivaLingo</h1>
                <p style="color: var(--text-secondary); font-size: 1rem;">Let's set up your learning profile</p>
            </div>
        """)

        # Progress
        progress_pct = (step + 1) / total_steps
        render_html(f"""
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.8rem; color: var(--text-muted);">Step {step + 1} of {total_steps}</span>
                    <span style="font-size: 0.8rem; color: var(--primary); font-weight: 600;">{int(progress_pct * 100)}%</span>
                </div>
                <div class="vl-progress-track" style="height: 0.375rem;">
                    <div class="vl-progress-fill" style="width: {progress_pct * 100}%; background: linear-gradient(90deg, var(--primary), var(--teal));"></div>
                </div>
            </div>
        """)

        # STEP 0: Name
        if step == 0:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">👋</div>
                    <h3 style="margin-bottom: 0.25rem;">What's your name?</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">We'll use this to personalize your experience</p>
                </div>
            """)

            name = st.text_input("Name", placeholder="Enter your name", label_visibility="collapsed")

            if st.button("Continue", type="primary", use_container_width=True, disabled=not name.strip()):
                st.session_state.onboarding_name = name.strip()
                st.session_state.onboarding_step = 1
                st.rerun()

        # STEP 1: Level
        elif step == 1:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <h3 style="margin-bottom: 0.25rem;">Your Spanish level?</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">This helps us tailor content to your abilities</p>
                </div>
            """)

            levels = [
                ("B2", "Upper Intermediate", "Handle most situations, express opinions"),
                ("C1", "Advanced", "Express fluently for professional purposes"),
                ("C2", "Proficiency", "Understand virtually everything, near-native"),
            ]

            if "onboarding_level" not in st.session_state:
                st.session_state.onboarding_level = "C1"

            for code, name, desc in levels:
                is_selected = st.session_state.get("onboarding_level") == code
                border = "var(--primary)" if is_selected else "var(--border)"
                bg = "var(--primary-light)" if is_selected else "var(--surface)"
                check = '<span style="color: var(--primary); font-weight: 700;">✓</span>' if is_selected else ''

                render_html(f"""
                    <div style="border: 2px solid {border}; border-radius: 0.75rem; padding: 0.875rem;
                                margin-bottom: 0.5rem; background: {bg};">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: var(--text);">{code} - {name}</div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">{desc}</div>
                            </div>
                            {check}
                        </div>
                    </div>
                """)

                if st.button(f"Select {code}", key=f"level_{code}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_level = code
                    st.rerun()

            _onboarding_nav_buttons(0, 1, 2)

        # STEP 2: Goal
        elif step == 2:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <h3 style="margin-bottom: 0.25rem;">Main learning goal?</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">We'll prioritize matching content</p>
                </div>
            """)

            goals = [
                ("💼", "Professional communication", "Business, emails, presentations"),
                ("🎓", "Academic study", "University, research, exams"),
                ("✈️", "Travel & culture", "Travel, immersion, social"),
                ("🌟", "General fluency", "Overall improvement"),
            ]

            if "onboarding_goal" not in st.session_state:
                st.session_state.onboarding_goal = "General fluency"

            for icon, label, desc in goals:
                is_selected = st.session_state.get("onboarding_goal") == label
                border = "var(--primary)" if is_selected else "var(--border)"
                bg = "var(--primary-light)" if is_selected else "var(--surface)"
                check = '<span style="color: var(--primary); font-weight: 700;">✓</span>' if is_selected else ''

                render_html(f"""
                    <div style="border: 2px solid {border}; border-radius: 0.75rem; padding: 0.875rem;
                                margin-bottom: 0.5rem; background: {bg};">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <div style="flex: 1;">
                                <div style="font-weight: 500; color: var(--text);">{label}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">{desc}</div>
                            </div>
                            {check}
                        </div>
                    </div>
                """)

                if st.button(f"Select", key=f"goal_{label}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_goal = label
                    st.rerun()

            _onboarding_nav_buttons(1, 2, 3)

        # STEP 3: Dialect
        elif step == 3:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌎</div>
                    <h3 style="margin-bottom: 0.25rem;">Preferred dialect?</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">We'll adapt vocabulary and expressions</p>
                </div>
            """)

            dialects = [
                ("&#x1F1EA;&#x1F1F8;", "Spain", "Castilian with vosotros"),
                ("&#x1F1F2;&#x1F1FD;", "Mexico", "Widely understood"),
                ("&#x1F1E6;&#x1F1F7;", "Argentina", "Rioplatense with vos"),
                ("&#x1F1E8;&#x1F1F4;", "Colombia", "Clear Latin American"),
                ("&#x1F1E8;&#x1F1F1;", "Chile", "Unique expressions"),
            ]

            if "onboarding_dialect" not in st.session_state:
                st.session_state.onboarding_dialect = "Spain"

            cols = st.columns(2)
            for i, (flag, name, desc) in enumerate(dialects):
                is_selected = st.session_state.get("onboarding_dialect") == name
                border = "var(--primary)" if is_selected else "var(--border)"
                bg = "var(--primary-light)" if is_selected else "var(--surface)"

                with cols[i % 2]:
                    render_html(f"""
                        <div style="border: 2px solid {border}; border-radius: 0.75rem; padding: 0.75rem;
                                    margin-bottom: 0.5rem; background: {bg}; text-align: center;">
                            <div style="font-size: 1.75rem; margin-bottom: 0.25rem;">{flag}</div>
                            <div style="font-weight: 600; color: var(--text); font-size: 0.875rem;">{name}</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">{desc}</div>
                        </div>
                    """)
                    btn_label = f"{'✓ ' if is_selected else ''}{name}"
                    if st.button(btn_label, key=f"dialect_{name}",
                                use_container_width=True, type="primary" if is_selected else "secondary"):
                        st.session_state.onboarding_dialect = name
                        st.rerun()

            _onboarding_nav_buttons(2, 3, 4)

        # STEP 4: Weekly goal
        elif step == 4:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📅</div>
                    <h3 style="margin-bottom: 0.25rem;">How often will you practice?</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">Set a realistic weekly goal</p>
                </div>
            """)

            options = [
                (3, "🌱", "Light", "3 days/week"),
                (4, "🌿", "Moderate", "4 days/week"),
                (5, "🌳", "Regular", "5 days/week"),
                (6, "🔥", "Intensive", "6 days/week"),
                (7, "⚡", "Daily", "Every day"),
            ]

            if "onboarding_weekly_goal" not in st.session_state:
                st.session_state.onboarding_weekly_goal = 5

            for days, icon, label, desc in options:
                is_selected = st.session_state.get("onboarding_weekly_goal") == days
                border = "var(--primary)" if is_selected else "var(--border)"
                bg = "var(--primary-light)" if is_selected else "var(--surface)"
                check = '<span style="color: var(--primary); font-weight: 700;">✓</span>' if is_selected else ''

                render_html(f"""
                    <div style="border: 2px solid {border}; border-radius: 0.75rem; padding: 0.75rem;
                                margin-bottom: 0.5rem; background: {bg};">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: var(--text);">{label}
                                    <span style="color: var(--primary); font-weight: 500;">({desc})</span>
                                </div>
                            </div>
                            {check}
                        </div>
                    </div>
                """)

                if st.button(f"Select {days} days", key=f"weekly_{days}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state.onboarding_weekly_goal = days
                    st.rerun()

            _onboarding_nav_buttons(3, 4, 5)

        # STEP 5: Focus areas
        elif step == 5:
            render_html("""
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎨</div>
                    <h3 style="margin-bottom: 0.25rem;">Focus areas</h3>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">Select all you'd like to improve</p>
                </div>
            """)

            focus_options = [
                ("Grammar", "📖", "Verb tenses, subjunctive, structure"),
                ("Vocabulary", "📚", "Words, idioms, collocations"),
                ("Conversation", "💬", "Speaking fluency, listening"),
                ("Writing", "✍️", "Essays, emails, creative"),
            ]

            if "onboarding_focus_areas" not in st.session_state:
                st.session_state.onboarding_focus_areas = ["Grammar", "Vocabulary"]

            selected_areas = st.session_state.get("onboarding_focus_areas", [])

            cols = st.columns(2)
            for i, (fid, icon, desc) in enumerate(focus_options):
                is_selected = fid in selected_areas
                border = "var(--primary)" if is_selected else "var(--border)"
                bg = "var(--primary-light)" if is_selected else "var(--surface)"

                with cols[i % 2]:
                    render_html(f"""
                        <div style="border: 2px solid {border}; border-radius: 0.75rem; padding: 1rem;
                                    margin-bottom: 0.5rem; background: {bg}; text-align: center;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                            <div style="font-weight: 600; color: var(--text); margin-bottom: 0.25rem;">{fid}</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">{desc}</div>
                        </div>
                    """)

                    btn_label = f"{'✓ ' if is_selected else ''}{fid}"
                    if st.button(btn_label, key=f"focus_{fid}", use_container_width=True,
                                type="primary" if is_selected else "secondary"):
                        current = list(selected_areas)
                        if fid in current:
                            current.remove(fid)
                        else:
                            current.append(fid)
                        st.session_state.onboarding_focus_areas = current
                        st.rerun()

            render_html(f"""
                <div style="text-align: center; margin: 1rem 0; color: var(--text-muted); font-size: 0.8rem;">
                    {len(selected_areas)} area{"s" if len(selected_areas) != 1 else ""} selected
                </div>
            """)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_5"):
                    st.session_state.onboarding_step = 4
                    st.rerun()
            with col_b:
                can_finish = len(selected_areas) > 0
                if st.button("Start Learning 🚀", type="primary", use_container_width=True,
                            key="finish", disabled=not can_finish):
                    _finish_onboarding()

        # Skip option
        render_html("<br>")
        if st.button("Skip setup", type="secondary"):
            profile_id = create_profile("Learner", "C1")
            if profile_id:
                st.session_state.active_profile_id = profile_id
                set_active_profile_id(profile_id)
                st.session_state.show_onboarding = False
                st.rerun()


def _onboarding_nav_buttons(prev_step: int, current_step: int, next_step: int):
    """Render back/continue buttons for onboarding."""
    render_html('<div style="height: 1rem;"></div>')
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back", use_container_width=True, key=f"back_{current_step}"):
            st.session_state.onboarding_step = prev_step
            st.rerun()
    with col_b:
        if st.button("Continue →", type="primary", use_container_width=True, key=f"next_{current_step}"):
            st.session_state.onboarding_step = next_step
            st.rerun()


def _finish_onboarding():
    """Finish onboarding and create profile."""
    name = st.session_state.get("onboarding_name", "Learner")
    level = st.session_state.get("onboarding_level", "C1")
    dialect = st.session_state.get("onboarding_dialect", "Spain")
    weekly_goal = st.session_state.get("onboarding_weekly_goal", 5)
    focus_areas = st.session_state.get("onboarding_focus_areas", ["Grammar", "Vocabulary"])

    profile_id = create_profile(
        name=name, level=level, dialect_preference=dialect,
        weekly_goal=weekly_goal, focus_areas=focus_areas
    )

    if profile_id:
        st.session_state.active_profile_id = profile_id
        set_active_profile_id(profile_id)
        st.session_state.show_onboarding = False
        for key in ["onboarding_step", "onboarding_name", "onboarding_level",
                   "onboarding_goal", "onboarding_dialect", "onboarding_weekly_goal",
                   "onboarding_focus_areas"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ============================================
# HOME PAGE
# ============================================

def render_home_page():
    """Render the home dashboard."""
    profile = get_user_profile()
    stats = get_total_stats()

    # Review counts
    vocab_due = len(get_vocab_for_review())
    errors_due = len(get_mistakes_for_review())
    grammar_due = len(get_grammar_for_review())
    total_due = vocab_due + errors_due + grammar_due

    # Streak
    streak = get_streak_days(get_progress_history())

    # Greeting
    name = profile.get('name', 'there')
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    # Hero greeting
    render_html(f"""
        <div class="vl-hero">
            <div class="vl-hero-title">{greeting}, {name}! 👋</div>
            <div class="vl-hero-subtitle">Ready to continue your Spanish journey?</div>
        </div>
    """)

    # Stats row
    stat_cols = st.columns(4)
    stats_data = [
        ("🔥", str(streak), "Day Streak", "#F59E0B"),
        ("📚", str(stats.get('total_vocab', 0)), "Words", "#10B981"),
        ("🎯", f"{get_sessions_this_week()}/{profile.get('weekly_goal', 5)}", "Weekly Goal", "#3B82F6"),
        ("⭐", str(stats.get('total_xp', 0)), "Total XP", "#F59E0B"),
    ]

    for col, (icon, value, label, color) in zip(stat_cols, stats_data):
        with col:
            st.markdown(render_stat_card(value, label, icon, color), unsafe_allow_html=True)

    render_html('<div style="height: 1.5rem;"></div>')

    # Main content
    main_col, side_col = st.columns([3, 2])

    with main_col:
        # Continue Learning
        render_action_card("Continue Learning", "Pick up where you left off", icon="▶️", primary=True)
        last_page = st.session_state.get("last_session", "Topic Diversity")
        if st.button("CONTINUE", type="primary", use_container_width=True, key="btn_continue"):
            st.session_state.current_page = last_page
            st.session_state.last_session = last_page
            st.rerun()

        # Review Due
        if total_due > 0:
            review_time = max(1, total_due // 2)
            render_action_card(
                "Review Due",
                f"{total_due} items ready ~ {review_time} min",
                icon="🔄",
                badge=f"{vocab_due} vocab" + (f" + {errors_due} errors" if errors_due > 0 else "")
            )
            if st.button("START REVIEW", type="primary", use_container_width=True, key="btn_review"):
                st.session_state.current_page = "Review"
                st.rerun()

        # Quick Session
        render_action_card("Quick 5-min session", "Mixed practice: vocab + grammar", icon="⚡")
        if st.button("QUICK START", type="primary", use_container_width=True, key="btn_quick"):
            st.session_state.quick_session_mode = True
            st.session_state.current_page = "Review"
            st.rerun()

        # Practice Activities
        render_html('<div style="height: 1rem;"></div>')
        render_section_header("Practice Activities")

        activities = [
            {"icon": "💬", "title": "Conversation", "desc": "Practice speaking", "page": "Conversation"},
            {"icon": "✍️", "title": "Writing", "desc": "Get feedback", "page": "Writing Coach"},
            {"icon": "🔤", "title": "Vocabulary", "desc": "Learn new words", "page": "Topic Diversity"},
            {"icon": "📖", "title": "Verbs", "desc": "Master conjugations", "page": "Verb Studio"},
        ]

        activity_cols = st.columns(2)
        for i, act in enumerate(activities):
            with activity_cols[i % 2]:
                render_html(f"""
                    <div class="vl-feature-card">
                        <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">{act['icon']}</div>
                        <div style="font-weight: 600; color: var(--text); margin-bottom: 0.25rem;">{act['title']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">{act['desc']}</div>
                    </div>
                """)
                if st.button("Start", key=f"act_{i}", use_container_width=True):
                    st.session_state.current_page = act['page']
                    st.session_state.last_session = act['page']
                    st.rerun()

    # Right sidebar
    with side_col:
        # Weekly goal progress
        weekly_goal = profile.get('weekly_goal', 5)
        sessions_this_week = get_sessions_this_week()
        progress_pct = min(100, (sessions_this_week / weekly_goal * 100)) if weekly_goal > 0 else 0

        render_html(f"""
            <div class="vl-card" style="margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; font-size: 0.875rem; color: var(--text);">Weekly Goal</span>
                    <span style="color: var(--text-muted); font-size: 0.875rem;">{sessions_this_week}/{weekly_goal}</span>
                </div>
                <div class="vl-progress-track">
                    <div class="vl-progress-fill" style="width: {progress_pct}%; background: linear-gradient(90deg, var(--primary), var(--teal));"></div>
                </div>
            </div>
        """)

        # Stats
        render_html(f"""
            <div class="vl-card" style="margin-bottom: 0.75rem; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--text);">{stats.get('total_vocab', 0)}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Words Learned</div>
            </div>
        """)

        # Weak areas
        weak_areas = get_weak_areas()
        if weak_areas:
            render_html('<div style="font-size: 0.8rem; font-weight: 600; color: var(--text); margin-bottom: 0.5rem;">Areas to Focus</div>')
            for area in weak_areas[:3]:
                render_html(f"""
                    <div style="padding: 0.5rem 0.75rem; background: var(--surface); border: 1px solid var(--border);
                                border-left: 3px solid var(--orange); border-radius: 0.375rem; margin-bottom: 0.5rem;
                                font-size: 0.8rem; color: var(--text-secondary);">{area}</div>
                """)

        # Tip of the Day
        tips = [
            "Practice for just 5 minutes a day to build a habit!",
            "Review mistakes right after making them for better retention.",
            "Speaking out loud helps cement new vocabulary.",
            "Try thinking in Spanish during everyday activities.",
            "Write short journal entries to practice writing.",
        ]
        tip = random.choice(tips)

        render_html(f"""
            <div class="vl-tip" style="margin-top: 0.75rem;">
                <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                    <div style="font-size: 1.25rem;">💡</div>
                    <div>
                        <div style="font-weight: 600; color: #1D4ED8; margin-bottom: 0.25rem; font-size: 0.8rem;">Tip of the Day</div>
                        <div style="font-size: 0.8rem; color: #1E40AF; line-height: 1.4;">{tip}</div>
                    </div>
                </div>
            </div>
        """)


# ============================================
# LEARN PAGE
# ============================================

def render_learn_page():
    """Render the Learn page."""
    render_hero("Learn", "Build your vocabulary and grammar skills")

    paths = [
        {"icon": "📚", "title": "Vocabulary", "desc": "Learn new words in context with the Topic Diversity Engine",
         "page": "Topic Diversity", "color": "#10B981"},
        {"icon": "🔤", "title": "Verb Mastery", "desc": "Master verb nuances, tenses, and near-synonyms",
         "page": "Verb Studio", "color": "#F59E0B"},
        {"icon": "🧩", "title": "Context Units", "desc": "Practice chunked phrases and contextual grammar",
         "page": "Context Units", "color": "#3B82F6"},
    ]

    cols = st.columns(3)
    for i, path in enumerate(paths):
        with cols[i]:
            render_html(f"""
                <div class="vl-feature-card">
                    <div style="width: 4rem; height: 4rem; border-radius: 50%; background: {path['color']}15;
                                display: flex; align-items: center; justify-content: center; font-size: 2rem;
                                margin: 0 auto 1rem auto;">{path['icon']}</div>
                    <h4 style="color: var(--text); margin: 0 0 0.5rem 0;">{path['title']}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0; line-height: 1.5;">{path['desc']}</p>
                </div>
            """)
            if st.button("START", type="primary", use_container_width=True, key=f"learn_{i}"):
                st.session_state.current_page = path['page']
                st.session_state.last_session = path['page']
                st.rerun()


# ============================================
# PRACTICE PAGE
# ============================================

def render_practice_page():
    """Render the Practice page."""
    render_hero("Practice", "Apply your skills in realistic scenarios")

    modes = [
        {"icon": "💬", "title": "Conversation", "desc": "Practice speaking in real scenarios", "page": "Conversation"},
        {"icon": "✍️", "title": "Writing Coach", "desc": "Get feedback on your writing", "page": "Writing Coach"},
        {"icon": "🔤", "title": "Verb Drills", "desc": "Master conjugations and nuance", "page": "Verb Studio"},
        {"icon": "🎯", "title": "Quick Practice", "desc": "Fast-paced mixed exercises", "page": "Topic Diversity"},
    ]

    cols = st.columns(2)
    for i, mode in enumerate(modes):
        with cols[i % 2]:
            render_html(f"""
                <div class="vl-feature-card">
                    <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">{mode['icon']}</div>
                    <h4 style="color: var(--text); margin: 0 0 0.25rem 0;">{mode['title']}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.8rem; margin: 0;">{mode['desc']}</p>
                </div>
            """)
            if st.button(f"Start {mode['title']}", key=f"practice_{i}", use_container_width=True):
                st.session_state.current_page = mode['page']
                st.session_state.last_session = mode['page']
                st.rerun()

    # Tools section
    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')
    render_section_header("Learning Tools")

    tools = [
        {"icon": "🌎", "title": "Dialect Guide", "desc": "Regional variations", "page": "Dialects"},
        {"icon": "🏛️", "title": "Memory Palace", "desc": "Mnemonic techniques", "page": "Memory Palace"},
        {"icon": "📝", "title": "Error Analysis", "desc": "Learn from mistakes", "page": "Mistake Catcher"},
    ]

    tool_cols = st.columns(3)
    for i, tool in enumerate(tools):
        with tool_cols[i]:
            render_html(f"""
                <div style="background: var(--surface-alt); border-radius: 0.75rem; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">{tool['icon']}</div>
                    <div style="font-weight: 600; color: var(--text); font-size: 0.875rem;">{tool['title']}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">{tool['desc']}</div>
                </div>
            """)
            if st.button("Open", key=f"tool_{i}", use_container_width=True):
                st.session_state.current_page = tool['page']
                st.rerun()


# ============================================
# PROGRESS PAGE
# ============================================

def render_progress_page():
    """Render the Progress page."""
    render_hero("Your Progress", "Track your Spanish learning journey")

    # Gather data
    stats = get_total_stats()
    profile = get_user_profile()
    progress_history = get_progress_history(days=30)
    streak = get_streak_days(progress_history)
    sessions_this_week = get_sessions_this_week()
    weak_areas = get_weak_areas()
    activity_history = get_activity_history(days=30)
    mistake_stats = get_mistake_stats()
    vocab_items = get_vocab_items()

    total_vocab_count = len(vocab_items)

    # Overview stats
    render_section_header("Overview")
    overview_cols = st.columns(4)
    overview_data = [
        ("🔥", str(streak), "Day Streak", "#F59E0B"),
        ("📚", str(stats.get('total_vocab', 0)), "Words", "#10B981"),
        ("🎤", f"{stats.get('total_speaking', 0):.0f}", "Min Speaking", "#8B5CF6"),
        ("🎯", str(stats.get('total_missions', 0)), "Missions", "#3B82F6"),
    ]

    for col, (icon, value, label, color) in zip(overview_cols, overview_data):
        with col:
            st.markdown(render_stat_card(value, label, icon, color), unsafe_allow_html=True)

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Weekly Report
    render_section_header("Weekly Report")
    week_ago = date.today() - timedelta(days=7)
    weekly_history = [h for h in progress_history if h.get('metric_date', '') >= week_ago.isoformat()]

    weekly_vocab_reviewed = sum(h.get('vocab_reviewed', 0) for h in weekly_history)
    weekly_errors_fixed = sum(h.get('errors_fixed', 0) for h in weekly_history)
    weekly_speaking = sum(h.get('speaking_minutes', 0) for h in weekly_history)
    new_words_this_week = len([v for v in vocab_items if v.get('created_at', '')[:10] >= week_ago.isoformat()])

    weekly_goal = profile.get('weekly_goal', 5)
    goal_progress = min(100, (sessions_this_week / weekly_goal * 100)) if weekly_goal > 0 else 0

    report_col1, report_col2 = st.columns(2)

    with report_col1:
        render_html(f"""
            <div class="vl-card">
                <h4 style="margin: 0 0 1rem 0; color: var(--text);">This Week's Activity</h4>
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.375rem;">
                        <span style="font-weight: 500; font-size: 0.875rem; color: var(--text);">Weekly Goal</span>
                        <span style="color: var(--text-muted); font-size: 0.875rem;">{sessions_this_week}/{weekly_goal} days</span>
                    </div>
                    <div class="vl-progress-track" style="height: 0.625rem;">
                        <div class="vl-progress-fill" style="width: {goal_progress}%; background: linear-gradient(90deg, var(--primary), var(--teal));"></div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                    <div style="background: var(--surface-alt); padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--blue);">{weekly_vocab_reviewed}</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Items Reviewed</div>
                    </div>
                    <div style="background: var(--surface-alt); padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">{new_words_this_week}</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">New Words</div>
                    </div>
                    <div style="background: var(--surface-alt); padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--orange);">{weekly_errors_fixed}</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Errors Fixed</div>
                    </div>
                    <div style="background: var(--surface-alt); padding: 0.75rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--purple);">{weekly_speaking:.0f}</div>
                        <div style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Min Speaking</div>
                    </div>
                </div>
            </div>
        """)

    with report_col2:
        # Streak & motivation
        if streak == 0:
            message, emoji = "Start your streak today!", "🌱"
        elif streak < 7:
            message, emoji = "Great start! Keep building the habit.", "💪"
        elif streak < 30:
            message, emoji = "Fantastic consistency! Real momentum.", "🌟"
        elif streak < 100:
            message, emoji = "Incredible dedication!", "🏆"
        else:
            message, emoji = "Legendary commitment!", "👑"

        render_html(f"""
            <div class="vl-card">
                <h4 style="margin: 0 0 1rem 0; color: var(--text);">Streak & Motivation</h4>
                <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #FEF3C7, #FDE68A);
                            border-radius: 0.75rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">🔥</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #92400E;">{streak}</div>
                    <div style="color: #92400E; font-weight: 600; font-size: 0.875rem;">Day Streak</div>
                </div>
                <div style="text-align: center; padding: 0.75rem; background: var(--primary-light);
                            border-radius: 0.5rem; border: 1px solid #A7F3D0;">
                    <span style="font-size: 1.5rem;">{emoji}</span>
                    <p style="color: #065F46; margin: 0.5rem 0 0 0; font-size: 0.875rem;">{message}</p>
                </div>
            </div>
        """)

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Weekly Activity Chart
    render_section_header("Weekly Activity")
    activity_by_day = {}
    for i in range(7):
        day = date.today() - timedelta(days=6-i)
        activity_by_day[day.strftime('%a')] = {'active': False, 'items': 0}

    for h in progress_history:
        try:
            h_date = datetime.strptime(h.get('metric_date', '')[:10], '%Y-%m-%d').date()
            if h_date >= week_ago:
                day_name = h_date.strftime('%a')
                if day_name in activity_by_day:
                    items = (h.get('vocab_reviewed', 0) + h.get('grammar_reviewed', 0) + h.get('errors_fixed', 0))
                    if items > 0:
                        activity_by_day[day_name] = {'active': True, 'items': items}
        except (ValueError, TypeError):
            pass

    day_cols = st.columns(7)
    for i, (day_name, data) in enumerate(activity_by_day.items()):
        with day_cols[i]:
            is_today = i == 6
            if data['active']:
                bg_color = "var(--primary)"
                text_color = "#FFFFFF"
                content = "✓"
            elif is_today:
                bg_color = "var(--orange-light)"
                text_color = "#92400E"
                content = "?"
            else:
                bg_color = "var(--surface-alt)"
                text_color = "var(--text-muted)"
                content = day_name[0]

            border = "2px solid var(--primary)" if is_today else "none"
            items_html = f'<div style="font-size: 0.65rem; color: var(--primary);">{data["items"]} items</div>' if data['active'] else ''

            render_html(f"""
                <div style="text-align: center;">
                    <div style="width: 3rem; height: 3rem; border-radius: 0.75rem; background: {bg_color};
                                display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem;
                                border: {border};">
                        <span style="color: {text_color}; font-weight: 600; font-size: 0.875rem;">{content}</span>
                    </div>
                    <div style="font-size: 0.7rem; color: var(--text-muted);">{day_name}</div>
                    {items_html}
                </div>
            """)

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Vocabulary & Errors
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        render_section_header("Vocabulary Growth")
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
            sorted_weeks = sorted(vocab_by_week.keys())[-4:]
            max_val = max(vocab_by_week[w] for w in sorted_weeks) if sorted_weeks else 1

            render_html('<div class="vl-card">')
            for week in sorted_weeks:
                week_display = datetime.strptime(week, '%Y-%m-%d').strftime('%b %d')
                bar_width = min(100, (vocab_by_week[week] / max_val * 100)) if max_val > 0 else 0
                render_html(f"""
                    <div style="margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                            <span style="font-size: 0.8rem; color: var(--text-muted);">{week_display}</span>
                            <span style="font-size: 0.8rem; font-weight: 600; color: var(--text);">+{vocab_by_week[week]}</span>
                        </div>
                        <div class="vl-progress-track">
                            <div class="vl-progress-fill" style="width: {bar_width}%; background: linear-gradient(90deg, var(--primary), var(--teal));"></div>
                        </div>
                    </div>
                """)
            render_html(f"""
                <div style="text-align: center; padding-top: 0.75rem; border-top: 1px solid var(--border);">
                    <span style="font-size: 1.5rem; font-weight: 800; color: var(--primary);">{total_vocab_count}</span>
                    <span style="color: var(--text-muted); font-size: 0.875rem;"> total words</span>
                </div>
            </div>
            """)
        else:
            render_empty_state("Start learning to see vocabulary growth!", "📈")

    with chart_col2:
        render_section_header("Error Patterns")
        if mistake_stats:
            sorted_errors = sorted(mistake_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:5]
            max_count = max(e[1].get('count', 1) for e in sorted_errors) if sorted_errors else 1

            render_html('<div class="vl-card">')
            for error_type, data in sorted_errors:
                count = data.get('count', 0)
                avg_ease = data.get('avg_ease', 2.5)
                bar_width = (count / max_count * 100) if max_count > 0 else 0

                if avg_ease >= 2.8:
                    bar_color, status = "var(--primary)", "Improving"
                elif avg_ease >= 2.2:
                    bar_color, status = "var(--orange)", "In Progress"
                else:
                    bar_color, status = "var(--red)", "Needs Focus"

                render_html(f"""
                    <div style="margin-bottom: 0.875rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                            <span style="font-size: 0.8rem; color: var(--text);">{error_type.replace('_', ' ').title()}</span>
                            <span style="font-size: 0.7rem; color: {bar_color}; font-weight: 600;">{status}</span>
                        </div>
                        <div class="vl-progress-track">
                            <div class="vl-progress-fill" style="width: {bar_width}%; background: {bar_color};"></div>
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.125rem;">{count} occurrences</div>
                    </div>
                """)
            render_html('</div>')
        else:
            render_empty_state("Complete exercises to track error patterns!", "🎯")

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Milestones
    render_section_header("Learning Milestones")
    milestone_col1, milestone_col2, milestone_col3 = st.columns(3)

    def _render_milestones(milestones, current_val, title, container):
        with container:
            render_html(f'<div class="vl-card"><h4 style="margin: 0 0 0.75rem 0; color: var(--text);">{title}</h4>')
            for threshold, name, emoji in milestones:
                achieved = current_val >= threshold
                opacity = "1" if achieved else "0.35"
                check = '<span style="color: var(--primary); font-weight: 700;">✓</span>' if achieved else ''
                render_html(f"""
                    <div style="display: flex; align-items: center; gap: 0.625rem; padding: 0.5rem 0;
                                opacity: {opacity}; border-bottom: 1px solid var(--surface-alt);">
                        <span style="font-size: 1.25rem;">{emoji}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: var(--text); font-size: 0.875rem;">{threshold}</div>
                            <div style="font-size: 0.7rem; color: var(--text-muted);">{name}</div>
                        </div>
                        {check}
                    </div>
                """)
            render_html('</div>')

    _render_milestones(
        [(50, "Beginner", "🌱"), (100, "Getting Started", "🌿"), (250, "Foundation", "🌳"),
         (500, "Solid Progress", "⭐"), (1000, "Advanced", "🌟")],
        total_vocab_count, "📚 Vocabulary", milestone_col1
    )
    _render_milestones(
        [(7, "One Week", "🔥"), (30, "One Month", "🔥🔥"), (100, "100 Days", "🔥🔥🔥"), (365, "One Year", "🏆")],
        streak, "🔥 Streak", milestone_col2
    )
    _render_milestones(
        [(10, "First Fixes", "🔧"), (50, "Active Learner", "🛠️"), (100, "Error Hunter", "🎯"), (500, "Perfectionist", "💎")],
        stats.get('total_errors', 0), "🎯 Errors Fixed", milestone_col3
    )

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Focus areas and strengths
    focus_col1, focus_col2 = st.columns(2)

    with focus_col1:
        render_section_header("Areas Needing Work")
        if weak_areas:
            for i, area in enumerate(weak_areas[:5]):
                colors = ["#EF4444", "#F59E0B", "#EAB308", "#84CC16", "#22C55E"]
                color = colors[min(i, len(colors)-1)]
                render_html(f"""
                    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem;
                                background: var(--surface); border: 1px solid var(--border);
                                border-left: 3px solid {color}; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 1.5rem; height: 1.5rem; background: {color}15; border-radius: 50%;
                                    display: flex; align-items: center; justify-content: center;
                                    color: {color}; font-weight: 700; font-size: 0.75rem;">{i+1}</div>
                        <div style="color: var(--text); font-weight: 500; font-size: 0.875rem;">{area}</div>
                    </div>
                """)
        else:
            render_empty_state("Keep practicing to discover areas to improve.", "🎉")

    with focus_col2:
        render_section_header("Strengths")
        fingerprint_summary = get_fingerprint_summary()
        if fingerprint_summary:
            strong_areas = [
                (cat, data) for cat, data in fingerprint_summary.items()
                if data.get('avg_confidence', 0) >= 0.7 and data.get('total_correct', 0) > 5
            ]
            strong_areas.sort(key=lambda x: x[1].get('avg_confidence', 0), reverse=True)

            if strong_areas:
                for cat, data in strong_areas[:5]:
                    confidence = data.get('avg_confidence', 0) * 100
                    cat_display = cat.replace('_', ' ').title()
                    render_html(f"""
                        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem;
                                    background: var(--primary-light); border: 1px solid #A7F3D0;
                                    border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="color: var(--primary); font-weight: 700;">✓</span>
                            <div style="flex: 1; color: #065F46; font-weight: 500; font-size: 0.875rem;">{cat_display}</div>
                            <div style="color: #047857; font-weight: 700; font-size: 0.875rem;">{confidence:.0f}%</div>
                        </div>
                    """)
            else:
                render_empty_state("Keep practicing to discover your strengths.", "💪")
        else:
            render_empty_state("Complete more exercises to see strengths.", "📊")

    render_html('<hr style="margin: 2rem 0; border: none; border-top: 1px solid var(--border);">')

    # Quick actions
    render_section_header("Take Action")
    action_cols = st.columns(3)

    actions = [
        ("📋", "My Spanish Portfolio", "Your complete learning record", "My Spanish"),
        ("🔍", "Error Analysis", "Deep dive into error patterns", "Error Notebook"),
        ("🔄", "Start Review", "Review items due today", "Review"),
    ]

    for col, (icon, title, desc, page) in zip(action_cols, actions):
        with col:
            render_html(f"""
                <div class="vl-feature-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <div style="font-weight: 600; color: var(--text); margin-bottom: 0.25rem;">{title}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">{desc}</div>
                </div>
            """)
            btn_type = "primary" if page == "Review" else "secondary"
            if st.button(f"Open", use_container_width=True, key=f"prog_{page}", type=btn_type):
                st.session_state.current_page = page
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
    if st.session_state.show_onboarding or st.session_state.active_profile_id is None:
        render_onboarding()
        return

    render_sidebar()

    page = st.session_state.current_page

    page_map = {
        "Home": render_home_page,
        "Learn": render_learn_page,
        "Practice": render_practice_page,
        "Progress": render_progress_page,
        "Review": render_review_hub_page,
        "Settings": render_settings_page,
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
