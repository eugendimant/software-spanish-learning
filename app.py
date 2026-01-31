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

# Initialize database with error handling
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {str(e)}. Please refresh the page.")


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

        name = st.text_input("Your Name", placeholder="Enter your name...", max_chars=50)
        level = st.selectbox("Current Level", ["B2", "C1", "C2"], index=1)

        if st.button("Start Learning", type="primary", use_container_width=True):
            cleaned_name = name.strip()
            # Input validation
            if not cleaned_name:
                st.error("Please enter your name to continue.")
            elif len(cleaned_name) < 2:
                st.error("Name must be at least 2 characters long.")
            elif len(cleaned_name) > 50:
                st.error("Name must be 50 characters or less.")
            elif not cleaned_name.replace(" ", "").replace("-", "").replace("'", "").isalnum():
                st.error("Name can only contain letters, numbers, spaces, hyphens, and apostrophes.")
            else:
                try:
                    profile_id = create_profile(cleaned_name, level)
                    if profile_id:
                        st.session_state.active_profile_id = profile_id
                        st.session_state.show_create_profile = False
                        set_active_profile_id(profile_id)
                        st.rerun()
                    else:
                        st.error("Failed to create profile. Please try again.")
                except Exception as e:
                    st.error(f"Error creating profile: {str(e)}")


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

        # Check if focus mode is enabled (hide gamification)
        focus_mode = profile.get("focus_mode", 0)

        # Streak counter - only show if not in focus mode
        if not focus_mode:
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

        # Simplified navigation - clear labels, grouped logically
        st.markdown("#### Practice")
        practice_pages = [
            ("🔄 Review Due Items", "Review"),
            ("📚 Learn Vocabulary", "Topic Diversity"),
            ("🔤 Verb Studio", "Verb Studio"),
            ("💬 Conversation", "Conversation"),
            ("✍️ Writing Coach", "Writing Coach"),
        ]

        for label, page_key in practice_pages:
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("#### Tools")
        tool_pages = [
            ("✏️ Check My Writing", "Mistake Catcher"),
            ("🌎 Dialect Guide", "Dialects"),
            ("🏛️ Memory Palace", "Memory Palace"),
        ]

        for label, page_key in tool_pages:
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("#### Progress")
        progress_pages = [
            ("📖 My Spanish", "My Spanish"),
            ("📊 My Fingerprint", "Fingerprint"),
            ("📋 Error Notebook", "Error Notebook"),
        ]

        for label, page_key in progress_pages:
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        other_pages = [
            ("🏠 Home", "Home"),
            ("⚙️ Settings", "Settings"),
        ]

        for label, page_key in other_pages:
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
    """Render the home/dashboard page - calm, focused daily plan."""
    profile = get_user_profile()
    stats = get_total_stats()
    focus_mode = profile.get("focus_mode", 0)

    # Simple greeting
    name = profile.get('name', '')
    greeting = f"Welcome back, {name}!" if name else "Welcome!"

    # Check items due for review
    vocab_due = len(get_vocab_for_review())
    errors_due = len(get_mistakes_for_review())
    total_due = vocab_due + errors_due
    review_time = max(1, total_due // 2)  # Estimate ~30 sec per item

    render_hero(title=greeting, subtitle="Your daily plan", pills=[])

    # Placement test override
    if not profile.get("placement_completed"):
        st.markdown("""
        <div class="feedback-box feedback-info" style="padding: 1.5rem; text-align: center; max-width: 600px; margin: 0 auto;">
            <strong>Let's personalize your learning</strong>
            <p style="margin: 0.5rem 0; opacity: 0.9;">A quick assessment helps us recommend the right content.</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Take Assessment", type="primary", use_container_width=True):
                st.session_state.current_page = "Settings"
                st.rerun()
        with col2:
            if st.button("Skip for Now", use_container_width=True):
                st.session_state.current_page = "Topic Diversity"
                st.rerun()
        return

    # ============================================
    # TWO PRIMARY ACTIONS - Continue & Review
    # ============================================
    st.markdown("""
    <div style="max-width: 650px; margin: 0 auto;">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Continue (next lesson)
        st.markdown("""
        <div class="card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
            <strong>Continue Learning</strong>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0;">New vocabulary & skills</p>
            <span style="background: rgba(34, 197, 94, 0.15); color: #22c55e; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">~10 min</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Lesson", type="primary", use_container_width=True, key="btn_continue"):
            st.session_state.current_page = "Topic Diversity"
            st.rerun()

    with col2:
        # Review (due items)
        if total_due > 0:
            st.markdown(f"""
            <div class="card" style="text-align: center; padding: 1.5rem; border: 2px solid var(--primary);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                <strong>Review Due</strong>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0;">{total_due} items ready</p>
                <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">~{review_time} min</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Review", type="primary", use_container_width=True, key="btn_review"):
                st.session_state.current_page = "Review"
                st.rerun()
        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 1.5rem; opacity: 0.6;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                <strong>All Caught Up</strong>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0;">No reviews due</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECONDARY LINKS - Quick access, not competing
    # ============================================
    st.markdown("<br>", unsafe_allow_html=True)

    # Collapsible secondary options
    with st.expander("🎯 Quick sessions", expanded=False):
        cols = st.columns(4)
        sessions = [
            ("💬 Speak", "Conversation", "5 min"),
            ("✍️ Write", "Writing Coach", "7 min"),
            ("🔤 Verbs", "Verb Studio", "5 min"),
            ("🏛️ Memory", "Memory Palace", "10 min"),
        ]
        for col, (label, page, time) in zip(cols, sessions):
            with col:
                st.markdown(f"<div style='text-align:center;'><small>{time}</small></div>", unsafe_allow_html=True)
                if st.button(label, key=f"qs_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

    # Stats - only if not in focus mode, hidden by default
    if not focus_mode:
        with st.expander("📊 Stats", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words Learned", stats.get('total_vocab', 0))
            with col2:
                st.metric("Speaking", f"{stats.get('total_speaking', 0):.0f} min")
            with col3:
                streak = get_streak_days(get_progress_history())
                st.metric("Streak", f"🔥 {streak}" if streak > 0 else "0 days")



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
from pages.fingerprint_dashboard import render_fingerprint_dashboard
from pages.writing_coach import render_writing_coach_page
from pages.dialect_navigator import render_dialect_navigator_page
from pages.memory_palace import render_memory_palace_page
from pages.my_spanish import render_my_spanish_page


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
    elif page == "Writing Coach":
        render_writing_coach_page()
    elif page == "Dialects":
        render_dialect_navigator_page()
    elif page == "Memory Palace":
        render_memory_palace_page()
    elif page == "My Spanish":
        render_my_spanish_page()
    elif page == "Fingerprint":
        render_fingerprint_dashboard()
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
