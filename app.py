"""
VivaLingo Pro - Advanced Spanish Learning Platform
A comprehensive, production-quality Spanish learning application for C1-C2 learners.
"""
import streamlit as st
from datetime import date
import json

# Initialize database and theme first
from utils.database import init_db, get_user_profile, update_user_profile, get_total_stats, get_domain_exposure
from utils.theme import apply_theme, render_hero, render_metric_grid, render_section_header, render_progress_bar
from utils.helpers import get_streak_days, format_time_ago, pick_domain_pair
from utils.content import TOPIC_DIVERSITY_DOMAINS

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="VivaLingo Pro",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/vivalingo/help',
        'Report a bug': 'https://github.com/vivalingo/issues',
        'About': '# VivaLingo Pro\nAdvanced Spanish Learning Platform for C1-C2 Mastery'
    }
)

# Apply custom theme
from utils.theme import get_css
st.markdown(get_css(), unsafe_allow_html=True)

# Initialize database
init_db()


def init_session_state():
    """Initialize session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = "Home"
        st.session_state.review_queue = []
        st.session_state.current_exercise = 0
        st.session_state.daily_mission_active = False
        st.session_state.conversation_messages = []
        st.session_state.placement_answers = {}
        st.session_state.quick_session_mode = False


init_session_state()


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <h1 style="font-size: 1.25rem; margin: 0; color: #0f172a;">VivaLingo Pro</h1>
            <p style="font-size: 0.75rem; color: #64748b; margin: 0;">Spanish Mastery Lab</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Quick session button
        if st.button("⚡ Quick 5-min Session", use_container_width=True, type="primary"):
            st.session_state.quick_session_mode = True
            st.session_state.current_page = "Review"
            st.rerun()

        st.divider()

        # Navigation
        st.markdown("### Navigation")

        pages = {
            "🏠 Home": "Home",
            "📚 Learn": "Learn",
            "🎯 Topic Diversity": "Topic Diversity",
            "📝 Context Units": "Context Units",
            "🔤 Verb Studio": "Verb Studio",
            "✍️ Mistake Catcher": "Mistake Catcher",
            "🎤 Daily Missions": "Daily Missions",
            "💬 Conversation": "Conversation",
            "🔄 Review Hub": "Review",
            "📊 Error Notebook": "Error Notebook",
            "📥 Content Ingest": "Content Ingest",
            "⚙️ Settings": "Settings",
        }

        for label, page_key in pages.items():
            if st.button(label, use_container_width=True,
                        type="secondary" if st.session_state.current_page != page_key else "primary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        # User profile summary
        profile = get_user_profile()
        st.markdown("### Your Profile")
        st.markdown(f"**Level:** {profile.get('level', 'C1')}")
        st.markdown(f"**Weekly Goal:** {profile.get('weekly_goal', 6)} sessions")

        # Quick stats
        stats = get_total_stats()
        if stats:
            st.markdown(f"📊 **{stats.get('total_vocab', 0)}** words reviewed")
            st.markdown(f"🎤 **{stats.get('total_speaking', 0):.0f}** min speaking")


def render_home_page():
    """Render the home/dashboard page."""
    profile = get_user_profile()
    stats = get_total_stats()
    exposures = get_domain_exposure()

    # Hero section
    render_hero(
        title=f"Welcome back{', ' + profile.get('name') if profile.get('name') else ''}!",
        subtitle="Continue your journey to Spanish mastery. Today's focus: precision and fluency.",
        pills=["C1-C2 Training", "Adaptive Learning", "Output-First"]
    )

    # Check if placement test needed
    if not profile.get("placement_completed"):
        st.warning("📋 **Complete your placement test** to personalize your learning experience.")
        if st.button("Start Placement Test", type="primary"):
            st.session_state.current_page = "Settings"
            st.rerun()
        st.divider()

    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Active Vocabulary",
            value=f"{stats.get('total_vocab', 0)}",
            delta="+12 this week" if stats.get('total_vocab', 0) > 0 else None
        )

    with col2:
        st.metric(
            label="Speaking Minutes",
            value=f"{stats.get('total_speaking', 0):.0f}",
            delta="+8 today" if stats.get('total_speaking', 0) > 0 else None
        )

    with col3:
        st.metric(
            label="Errors Fixed",
            value=f"{stats.get('total_errors', 0)}",
            delta="-3 recurring" if stats.get('total_errors', 0) > 0 else None
        )

    with col4:
        st.metric(
            label="Missions Done",
            value=f"{stats.get('total_missions', 0)}",
            delta="+1 today" if stats.get('total_missions', 0) > 0 else None
        )

    st.divider()

    # Two columns: Actions and Progress
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        render_section_header("Quick Actions")

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            st.markdown("""
            <div class="card" style="cursor: pointer;">
                <div class="card-header">
                    <div class="card-icon">📚</div>
                    <h3 class="card-title">Learn New Vocab</h3>
                </div>
                <p style="color: var(--text-muted); font-size: 0.875rem;">
                    Explore vocabulary from underexposed domains
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Learning", key="action_learn", use_container_width=True):
                st.session_state.current_page = "Topic Diversity"
                st.rerun()

        with action_col2:
            st.markdown("""
            <div class="card" style="cursor: pointer;">
                <div class="card-header">
                    <div class="card-icon">🎤</div>
                    <h3 class="card-title">Daily Mission</h3>
                </div>
                <p style="color: var(--text-muted); font-size: 0.875rem;">
                    Speaking + writing with constraints
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Mission", key="action_mission", use_container_width=True):
                st.session_state.current_page = "Daily Missions"
                st.rerun()

        action_col3, action_col4 = st.columns(2)

        with action_col3:
            st.markdown("""
            <div class="card" style="cursor: pointer;">
                <div class="card-header">
                    <div class="card-icon">🔄</div>
                    <h3 class="card-title">Review Session</h3>
                </div>
                <p style="color: var(--text-muted); font-size: 0.875rem;">
                    Vocabulary + grammar spaced repetition
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Review", key="action_review", use_container_width=True):
                st.session_state.current_page = "Review"
                st.rerun()

        with action_col4:
            st.markdown("""
            <div class="card" style="cursor: pointer;">
                <div class="card-header">
                    <div class="card-icon">💬</div>
                    <h3 class="card-title">Conversation</h3>
                </div>
                <p style="color: var(--text-muted); font-size: 0.875rem;">
                    Goal-based roleplay scenarios
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Conversation", key="action_convo", use_container_width=True):
                st.session_state.current_page = "Conversation"
                st.rerun()

    with right_col:
        render_section_header("Domain Coverage")

        if exposures:
            total_exposure = sum(e.get("exposure_count", 0) for e in exposures.values()) or 1

            for domain in TOPIC_DIVERSITY_DOMAINS[:6]:  # Show top 6
                domain_name = domain["domain"]
                exposure = exposures.get(domain_name, {}).get("exposure_count", 0)
                percent = (exposure / total_exposure) * 100

                st.markdown(f"**{domain_name}**")
                st.progress(min(percent / 100, 1.0))
                st.caption(f"{percent:.0f}% exposure")
        else:
            st.info("Start learning to see your domain coverage!")

        # Familiar vs Stretch indicator
        familiar, stretch = pick_domain_pair(exposures)
        st.markdown("---")
        st.markdown(f"🟢 **Familiar:** {familiar}")
        st.markdown(f"🔵 **Stretch:** {stretch}")

    # Today's recommendations
    st.divider()
    render_section_header("Today's Focus")

    rec_cols = st.columns(3)

    with rec_cols[0]:
        st.markdown("""
        <div class="card-muted">
            <strong>🎯 Verb Precision</strong><br>
            <span style="color: var(--text-muted);">Practice: sopesar, afrontar, plantear</span>
        </div>
        """, unsafe_allow_html=True)

    with rec_cols[1]:
        st.markdown("""
        <div class="card-muted">
            <strong>📝 Grammar Pattern</strong><br>
            <span style="color: var(--text-muted);">Review: Subjunctive with es importante que</span>
        </div>
        """, unsafe_allow_html=True)

    with rec_cols[2]:
        st.markdown("""
        <div class="card-muted">
            <strong>🔊 Error Focus</strong><br>
            <span style="color: var(--text-muted);">Common issue: preposition with depender</span>
        </div>
        """, unsafe_allow_html=True)


def render_learn_page():
    """Render the general learning hub page."""
    render_hero(
        title="Learning Hub",
        subtitle="Choose your learning path: vocabulary, verbs, grammar, or full immersion.",
        pills=["Vocabulary", "Verb Precision", "Grammar", "Context"]
    )

    # Learning paths
    paths = [
        {
            "icon": "🎯",
            "title": "Topic Diversity Engine",
            "desc": "Rotate through underexposed domains with 70/30 familiar/stretch mix",
            "page": "Topic Diversity"
        },
        {
            "icon": "📝",
            "title": "Context-First Units",
            "desc": "Learn phrases in dialogue, messages, and mini-paragraphs",
            "page": "Context Units"
        },
        {
            "icon": "🔤",
            "title": "Verb Choice Studio",
            "desc": "Master nuance, tone, and near-synonyms for advanced verbs",
            "page": "Verb Studio"
        },
        {
            "icon": "✍️",
            "title": "Mistake Catcher",
            "desc": "Real-time error detection for gender, agreement, and more",
            "page": "Mistake Catcher"
        },
    ]

    cols = st.columns(2)
    for i, path in enumerate(paths):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">{path['icon']}</div>
                    <h3 class="card-title">{path['title']}</h3>
                </div>
                <p style="color: var(--text-muted);">{path['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {path['title']}", key=f"path_{i}", use_container_width=True):
                st.session_state.current_page = path["page"]
                st.rerun()


# Import page renderers
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


def main():
    """Main application entry point."""
    render_sidebar()

    # Route to the appropriate page
    page = st.session_state.current_page

    if page == "Home":
        render_home_page()
    elif page == "Learn":
        render_learn_page()
    elif page == "Topic Diversity":
        render_topic_diversity_page()
    elif page == "Context Units":
        render_context_units_page()
    elif page == "Verb Studio":
        render_verb_studio_page()
    elif page == "Mistake Catcher":
        render_mistake_catcher_page()
    elif page == "Daily Missions":
        render_daily_missions_page()
    elif page == "Conversation":
        render_conversation_page()
    elif page == "Review":
        render_review_hub_page()
    elif page == "Error Notebook":
        render_error_notebook_page()
    elif page == "Content Ingest":
        render_content_ingest_page()
    elif page == "Settings":
        render_settings_page()
    else:
        render_home_page()


if __name__ == "__main__":
    main()
