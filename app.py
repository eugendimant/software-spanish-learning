"""
VivaLingo Pro - Advanced Spanish Learning Platform
A comprehensive, production-quality Spanish learning application for C1-C2 learners.
Features futuristic UI and multi-profile support.
"""
import streamlit as st
from datetime import date
import json

# Initialize database and theme first
from utils.database import (
    init_db, get_user_profile, update_user_profile, get_total_stats,
    get_domain_exposure, get_vocab_for_review, get_mistakes_for_review,
    get_progress_history, get_all_profiles, create_profile, get_profile,
    set_active_profile_id, get_active_profile_id, get_profile_stats,
    init_profile_domains, delete_profile
)
from utils.theme import (
    get_css, render_hero, render_section_header,
    render_streak_badge, render_profile_card
)
from utils.helpers import get_streak_days, pick_domain_pair
from utils.content import TOPIC_DIVERSITY_DOMAINS, GRAMMAR_MICRODRILLS

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="VivaLingo Pro",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/vivalingo/help',
        'Report a bug': 'https://github.com/vivalingo/issues',
        'About': '# VivaLingo Pro\nAdvanced Spanish Learning Platform for C1-C2 Mastery'
    }
)

# Apply custom theme
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
        st.session_state.show_profile_selector = False
        st.session_state.show_create_profile = False

    # Initialize active profile from database or create default
    if "active_profile_id" not in st.session_state:
        profiles = get_all_profiles()
        if profiles:
            st.session_state.active_profile_id = profiles[0]["id"]
        else:
            # No profiles exist, show profile creation
            st.session_state.active_profile_id = None
            st.session_state.show_create_profile = True

    # Sync with database module
    if st.session_state.active_profile_id:
        set_active_profile_id(st.session_state.active_profile_id)


init_session_state()


def render_profile_creation():
    """Render the profile creation screen."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
        <h1 style="margin-bottom: 0.5rem;">Welcome to VivaLingo Pro</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">
            Create your profile to start your Spanish mastery journey
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="card" style="padding: 2rem;">
            <h3 style="text-align: center; margin-bottom: 1.5rem;">Create Your Profile</h3>
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Your Name", placeholder="Enter your name...")
        level = st.selectbox("Current Level", ["B2", "C1", "C2"], index=1)

        if st.button("Start Learning", type="primary", use_container_width=True):
            if name.strip():
                profile_id = create_profile(name.strip(), level)
                st.session_state.active_profile_id = profile_id
                st.session_state.show_create_profile = False
                set_active_profile_id(profile_id)
                st.rerun()
            else:
                st.error("Please enter your name to continue.")


def render_profile_selector():
    """Render the profile selector modal."""
    profiles = get_all_profiles()

    st.markdown("### Switch Profile")

    if profiles:
        cols = st.columns(min(len(profiles) + 1, 4))

        for i, profile in enumerate(profiles):
            with cols[i % 4]:
                stats = get_profile_stats(profile["id"])
                streak = get_streak_days(get_progress_history())
                is_active = profile["id"] == st.session_state.active_profile_id

                st.markdown(render_profile_card(
                    profile.get("name", "Unknown"),
                    profile.get("level", "C1"),
                    stats.get("vocab_count", 0),
                    streak,
                    is_active
                ), unsafe_allow_html=True)

                if st.button(
                    "Active" if is_active else "Select",
                    key=f"profile_{profile['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    disabled=is_active
                ):
                    st.session_state.active_profile_id = profile["id"]
                    set_active_profile_id(profile["id"])
                    st.session_state.show_profile_selector = False
                    st.rerun()

        # Add new profile button
        with cols[min(len(profiles), 3)]:
            st.markdown("""
            <div class="profile-card" style="border-style: dashed;">
                <div class="profile-avatar" style="background: var(--bg-tertiary);">+</div>
                <div class="profile-name">New Profile</div>
                <div class="profile-stats">Create a new learner profile</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create New", key="create_new_profile", use_container_width=True):
                st.session_state.show_create_profile = True
                st.session_state.show_profile_selector = False
                st.rerun()
    else:
        st.info("No profiles found. Create your first profile!")
        if st.button("Create Profile", type="primary"):
            st.session_state.show_create_profile = True
            st.session_state.show_profile_selector = False
            st.rerun()

    if st.button("Close", use_container_width=True):
        st.session_state.show_profile_selector = False
        st.rerun()


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.5));">🚀</div>
            <h1 style="font-size: 1.4rem; margin: 0; background: linear-gradient(135deg, #f8fafc 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">VivaLingo Pro</h1>
            <p style="font-size: 0.75rem; color: #64748b; margin: 0.25rem 0 0 0;">Spanish Mastery Lab</p>
        </div>
        """, unsafe_allow_html=True)

        # Current profile display
        profile = get_user_profile()
        profile_name = profile.get("name", "")

        if profile_name:
            initial = profile_name[0].upper()
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; margin: 0.5rem 0;
                        background: rgba(99, 102, 241, 0.1); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);
                        cursor: pointer;" onclick="document.querySelector('[data-testid=stButton] button').click()">
                <div style="width: 40px; height: 40px; border-radius: 50%;
                            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                            display: flex; align-items: center; justify-content: center;
                            font-size: 1.1rem; font-weight: 700; color: white;
                            box-shadow: 0 0 16px rgba(99, 102, 241, 0.4);">{initial}</div>
                <div>
                    <div style="font-weight: 600; color: #f8fafc; font-size: 0.95rem;">{profile_name}</div>
                    <div style="font-size: 0.7rem; color: #64748b;">Level {profile.get('level', 'C1')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("👤 Switch Profile", use_container_width=True, type="secondary"):
            st.session_state.show_profile_selector = True
            st.rerun()

        # Streak counter
        streak = get_streak_days(get_progress_history())
        render_streak_badge(streak)

        # Items due badges
        vocab_due = len(get_vocab_for_review())
        errors_due = len(get_mistakes_for_review())
        total_due = vocab_due + errors_due

        if total_due > 0:
            st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; justify-content: center; margin: 0.75rem 0;">
                <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; padding: 0.3rem 0.6rem;
                            border-radius: 9999px; font-size: 0.7rem; font-weight: 600;
                            border: 1px solid rgba(99, 102, 241, 0.3);">
                    📚 {vocab_due} vocab
                </span>
                <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; padding: 0.3rem 0.6rem;
                            border-radius: 9999px; font-size: 0.7rem; font-weight: 600;
                            border: 1px solid rgba(239, 68, 68, 0.3);">
                    ✗ {errors_due} errors
                </span>
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
                         type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        # Quick stats
        stats = get_total_stats()
        if stats:
            st.markdown("### Your Stats")
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                📊 <strong style="color: var(--text-primary);">{stats.get('total_vocab', 0)}</strong> words reviewed<br>
                🎤 <strong style="color: var(--text-primary);">{stats.get('total_speaking', 0):.0f}</strong> min speaking<br>
                🎯 <strong style="color: var(--text-primary);">{stats.get('total_missions', 0)}</strong> missions done
            </div>
            """, unsafe_allow_html=True)


def render_home_page():
    """Render the home/dashboard page."""
    profile = get_user_profile()
    stats = get_total_stats()
    exposures = get_domain_exposure()

    # Hero section
    name = profile.get('name', '')
    greeting = f"Welcome back, {name}!" if name else "Welcome back!"
    render_hero(
        title=greeting,
        subtitle="Continue your journey to Spanish mastery. Today's focus: precision and fluency.",
        pills=["C1-C2 Training", "Adaptive Learning", "Output-First"]
    )

    # Check if placement test needed
    if not profile.get("placement_completed"):
        st.markdown("""
        <div class="feedback-box feedback-info" style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 1.5rem;">📋</span>
            <div>
                <strong>Complete your placement test</strong> to personalize your learning experience.
            </div>
        </div>
        """, unsafe_allow_html=True)
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
            delta="-3 recurring" if stats.get('total_errors', 0) > 0 else None,
            delta_color="inverse"
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
        if exposures:
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
            <strong style="color: var(--text-primary);">🎯 Verb Precision</strong><br>
            <span style="color: var(--text-muted);">Practice: sopesar, afrontar, plantear</span>
        </div>
        """, unsafe_allow_html=True)

    with rec_cols[1]:
        st.markdown("""
        <div class="card-muted">
            <strong style="color: var(--text-primary);">📝 Grammar Pattern</strong><br>
            <span style="color: var(--text-muted);">Review: Subjunctive with es importante que</span>
        </div>
        """, unsafe_allow_html=True)

    with rec_cols[2]:
        st.markdown("""
        <div class="card-muted">
            <strong style="color: var(--text-primary);">🔊 Error Focus</strong><br>
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
    # Check if we need to show profile creation
    if st.session_state.get("show_create_profile") or st.session_state.active_profile_id is None:
        render_profile_creation()
        return

    # Check if we need to show profile selector
    if st.session_state.get("show_profile_selector"):
        render_sidebar()
        render_profile_selector()
        return

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
