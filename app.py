"""
VivaLingo - Spanish Learning Platform
Clean, focused interface for C1-C2 learners.
"""
import streamlit as st
from datetime import date

# Initialize database and theme first
from utils.database import (
    init_db, get_user_profile, update_user_profile, get_total_stats,
    get_vocab_for_review, get_mistakes_for_review, get_grammar_for_review,
    get_progress_history, get_all_profiles, create_profile,
    set_active_profile_id, get_active_profile_id, get_profile_stats
)
from utils.theme import (
    get_css, render_hero, render_section_header, render_stat_card,
    render_action_card, render_feedback, render_streak_badge,
    render_empty_state, render_loading_skeleton
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
        st.markdown("""
        <div style="padding: 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 16px;">
            <div style="font-size: 24px; font-weight: 700; color: var(--text-primary);">
                🇪🇸 VivaLingo
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">Spanish Mastery</div>
        </div>
        """, unsafe_allow_html=True)

        # Profile info
        profile = get_user_profile()
        if profile.get("name"):
            streak = get_streak_days(get_progress_history())
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

        # Review due badge
        vocab_due = len(get_vocab_for_review())
        errors_due = len(get_mistakes_for_review())
        total_due = vocab_due + errors_due

        if total_due > 0:
            st.markdown(f"""
            <div style="background: var(--accent-muted); border: 1px solid rgba(99, 102, 241, 0.3);
                        border-radius: 8px; padding: 10px 12px; margin-bottom: 16px;">
                <div style="font-size: 13px; color: var(--accent);">
                    <strong>{total_due}</strong> items due for review
                </div>
            </div>
            """, unsafe_allow_html=True)

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
    """Render onboarding flow for new users."""
    step = st.session_state.onboarding_step

    # Center container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 32px 0;">
            <div style="font-size: 48px; margin-bottom: 16px;">🇪🇸</div>
            <h1 style="margin-bottom: 8px;">Welcome to VivaLingo</h1>
            <p style="color: var(--text-secondary);">Let's set up your learning profile</p>
        </div>
        """, unsafe_allow_html=True)

        if step == 0:
            # Name
            st.markdown("### What's your name?")
            name = st.text_input("Name", placeholder="Enter your name", label_visibility="collapsed")

            if st.button("Continue", type="primary", use_container_width=True, disabled=not name.strip()):
                st.session_state.onboarding_name = name.strip()
                st.session_state.onboarding_step = 1
                st.rerun()

        elif step == 1:
            # Level
            st.markdown("### What's your current Spanish level?")
            level = st.radio(
                "Level",
                ["B2 - Upper Intermediate", "C1 - Advanced", "C2 - Proficiency"],
                label_visibility="collapsed"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True):
                    st.session_state.onboarding_step = 0
                    st.rerun()
            with col_b:
                if st.button("Continue →", type="primary", use_container_width=True):
                    st.session_state.onboarding_level = level.split(" - ")[0]
                    st.session_state.onboarding_step = 2
                    st.rerun()

        elif step == 2:
            # Goal
            st.markdown("### What's your main goal?")
            goal = st.radio(
                "Goal",
                ["Professional communication", "Academic study", "Travel & culture", "General fluency"],
                label_visibility="collapsed"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True):
                    st.session_state.onboarding_step = 1
                    st.rerun()
            with col_b:
                if st.button("Start Learning", type="primary", use_container_width=True):
                    # Create profile
                    name = st.session_state.get("onboarding_name", "Learner")
                    level = st.session_state.get("onboarding_level", "C1")

                    profile_id = create_profile(name, level)
                    if profile_id:
                        st.session_state.active_profile_id = profile_id
                        set_active_profile_id(profile_id)
                        st.session_state.show_onboarding = False
                        st.session_state.onboarding_step = 0
                        st.rerun()

        # Skip option
        st.markdown("<br>", unsafe_allow_html=True)
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

        st.markdown(f"""
        <div class="action-card action-card-primary" style="margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 32px;">▶️</div>
                <div style="flex: 1;">
                    <div class="action-card-title">Continue Learning</div>
                    <div class="action-card-subtitle">Pick up where you left off</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Continue", type="primary", use_container_width=True, key="btn_continue"):
            st.session_state.current_page = last_page
            st.rerun()

        # ----------------------------------------
        # REVIEW DUE CARD
        # ----------------------------------------
        if total_due > 0:
            review_time = max(1, total_due // 2)
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

            if st.button("Start Review", use_container_width=True, key="btn_review"):
                st.session_state.current_page = "Review"
                st.rerun()

        # ----------------------------------------
        # QUICK 5 MIN SESSION
        # ----------------------------------------
        st.markdown("""
        <div class="action-card" style="margin-top: 16px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 32px;">⚡</div>
                <div style="flex: 1;">
                    <div class="action-card-title">Quick 5 min session</div>
                    <div class="action-card-subtitle">Mixed practice: vocab + grammar + listening</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
                st.markdown(f"""
                <div class="card" style="text-align: center; padding: 20px;">
                    <div style="font-size: 28px; margin-bottom: 8px;">{rec['icon']}</div>
                    <div style="font-weight: 600; margin-bottom: 4px;">{rec['title']}</div>
                    <div style="font-size: 13px; color: var(--text-muted);">{rec['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Start", key=f"rec_{i}", use_container_width=True):
                    st.session_state.current_page = rec['page']
                    st.rerun()

    # ----------------------------------------
    # RIGHT RAIL - Stats
    # ----------------------------------------
    with rail_col:
        # Streak
        streak = get_streak_days(get_progress_history())
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 12px; text-align: center;">
            <div style="font-size: 36px; margin-bottom: 4px;">🔥</div>
            <div class="stat-value">{streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

        # Weekly goal
        weekly_goal = profile.get('weekly_goal', 6)
        # TODO: Calculate actual sessions this week
        sessions_this_week = min(3, weekly_goal)  # Placeholder
        progress_pct = sessions_this_week / weekly_goal if weekly_goal > 0 else 0

        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-weight: 500;">Weekly Goal</span>
                <span style="color: var(--text-muted);">{sessions_this_week}/{weekly_goal}</span>
            </div>
            <div style="background: var(--bg-elevated); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: var(--accent); height: 100%; width: {progress_pct * 100}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Words learned
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 12px;">
            <div class="stat-value">{stats.get('total_vocab', 0)}</div>
            <div class="stat-label">Words Learned</div>
        </div>
        """, unsafe_allow_html=True)

        # Speaking time
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 12px;">
            <div class="stat-value">{stats.get('total_speaking', 0):.0f}</div>
            <div class="stat-label">Minutes Speaking</div>
        </div>
        """, unsafe_allow_html=True)

        # Weak areas
        st.markdown("### Focus Areas")
        # TODO: Get actual weak areas from analytics
        weak_areas = ["Subjunctive mood", "Ser vs Estar", "Preterite vs Imperfect"]
        for area in weak_areas[:3]:
            st.markdown(f"""
            <div style="padding: 8px 12px; background: var(--bg-surface); border-radius: 6px;
                        margin-bottom: 8px; font-size: 13px; border-left: 3px solid var(--warning);">
                {area}
            </div>
            """, unsafe_allow_html=True)


# ============================================
# LEARN PAGE
# ============================================

def render_learn_page():
    """Render Learn page with vocabulary and grammar paths."""
    st.markdown("## Learn")
    st.markdown("Build your vocabulary and grammar skills")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-size: 32px; margin-bottom: 12px;">📚</div>
            <h3>Vocabulary</h3>
            <p style="color: var(--text-muted);">Learn new words in context with the Topic Diversity Engine</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Vocabulary", type="primary", use_container_width=True, key="learn_vocab"):
            st.session_state.current_page = "Topic Diversity"
            st.session_state.last_session = "Topic Diversity"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-size: 32px; margin-bottom: 12px;">🔤</div>
            <h3>Verb Mastery</h3>
            <p style="color: var(--text-muted);">Master verb nuances, tenses, and near-synonyms</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Verbs", type="primary", use_container_width=True, key="learn_verbs"):
            st.session_state.current_page = "Verb Studio"
            st.session_state.last_session = "Verb Studio"
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
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 28px; margin-bottom: 8px;">{mode['icon']}</div>
                <h4>{mode['title']}</h4>
                <p style="color: var(--text-muted); font-size: 14px;">{mode['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
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
    """Render Progress page with stats and history."""
    st.markdown("## Progress")

    stats = get_total_stats()
    profile = get_user_profile()
    streak = get_streak_days(get_progress_history())

    # Stats grid
    cols = st.columns(4)

    with cols[0]:
        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <div style="font-size: 24px; margin-bottom: 4px;">🔥</div>
            <div class="stat-value">{streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <div style="font-size: 24px; margin-bottom: 4px;">📚</div>
            <div class="stat-value">{stats.get('total_vocab', 0)}</div>
            <div class="stat-label">Words</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <div style="font-size: 24px; margin-bottom: 4px;">🎤</div>
            <div class="stat-value">{stats.get('total_speaking', 0):.0f}</div>
            <div class="stat-label">Min Speaking</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f"""
        <div class="stat-card" style="text-align: center;">
            <div style="font-size: 24px; margin-bottom: 4px;">🎯</div>
            <div class="stat-value">{stats.get('total_missions', 0)}</div>
            <div class="stat-label">Missions</div>
        </div>
        """, unsafe_allow_html=True)

    # More details
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### My Spanish Portfolio")
        if st.button("View Full Portfolio", use_container_width=True):
            st.session_state.current_page = "My Spanish"
            st.rerun()

    with col2:
        st.markdown("### Error Patterns")
        if st.button("View Error Analysis", use_container_width=True):
            st.session_state.current_page = "Error Notebook"
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
