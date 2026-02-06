"""Settings and Profile page with placement test and data export."""
import streamlit as st
import json
from datetime import date

from utils.theme import render_hero, render_section_header, render_profile_card
from utils.database import (
    get_user_profile, update_user_profile,
    export_vocab_json, export_mistakes_json, export_progress_json,
    get_total_stats, load_portfolio, save_portfolio,
    get_all_profiles, create_profile, get_profile_stats, delete_profile,
    set_active_profile_id, get_active_profile_id, get_progress_history,
    get_activity_history
)
from utils.content import PLACEMENT_QUESTIONS, DIALECT_MODULES
from utils.helpers import get_streak_days


def render_settings_page():
    """Render the Settings page."""
    render_hero(
        title="Settings",
        subtitle="Manage your profile, take the placement test, configure preferences, and export your data.",
        pills=["Profile", "Placement", "Preferences", "Export"]
    )

    # Tabs
    tabs = st.tabs(["👤 Profile", "👥 All Profiles", "📋 Placement Test", "🌍 Preferences", "💾 Data Export"])

    with tabs[0]:
        render_profile_section()

    with tabs[1]:
        render_all_profiles()

    with tabs[2]:
        render_placement_test()

    with tabs[3]:
        render_preferences()

    with tabs[4]:
        render_data_export()


def render_all_profiles():
    """Render the all profiles management section."""
    render_section_header("Manage Profiles")

    profiles = get_all_profiles()
    current_profile_id = get_active_profile_id()

    if profiles:
        cols = st.columns(min(len(profiles), 3))

        for i, profile in enumerate(profiles):
            with cols[i % 3]:
                stats = get_profile_stats(profile["id"])
                is_active = profile["id"] == current_profile_id
                streak = get_streak_days(get_progress_history()) if is_active else 0

                st.markdown(render_profile_card(
                    profile.get("name", "Unknown"),
                    profile.get("level", "C1"),
                    stats.get("vocab_count", 0),
                    streak,
                    is_active
                ), unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(
                        "Active" if is_active else "Switch",
                        key=f"switch_{profile['id']}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                        disabled=is_active
                    ):
                        st.session_state.active_profile_id = profile["id"]
                        set_active_profile_id(profile["id"])
                        st.rerun()

                with col_b:
                    if not is_active:
                        # Prevent deletion if this is the last profile
                        if len(profiles) <= 1:
                            st.caption("Cannot delete last profile")
                        elif st.button("Delete", key=f"delete_{profile['id']}", use_container_width=True):
                            if st.session_state.get(f"confirm_delete_{profile['id']}"):
                                try:
                                    delete_profile(profile["id"])
                                    # Clear confirmation state
                                    st.session_state.pop(f"confirm_delete_{profile['id']}", None)
                                    st.success(f"Profile deleted successfully.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete profile: {str(e)}")
                            else:
                                st.session_state[f"confirm_delete_{profile['id']}"] = True
                                st.warning("Click again to confirm deletion. This action cannot be undone!")
                    else:
                        st.caption("Current profile")

    # Create new profile section
    st.divider()
    render_section_header("Create New Profile")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        new_name = st.text_input("Profile Name", placeholder="Enter a name...", key="new_profile_name", max_chars=50)

    with col2:
        new_level = st.selectbox("Level", ["B2", "C1", "C2"], index=1, key="new_profile_level")

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Profile", type="primary", use_container_width=True):
            cleaned_name = new_name.strip()
            # Input validation
            if not cleaned_name:
                st.error("Please enter a name for the profile.")
            elif len(cleaned_name) < 2:
                st.error("Name must be at least 2 characters long.")
            elif not cleaned_name.replace(" ", "").replace("-", "").replace("'", "").isalnum():
                st.error("Name can only contain letters, numbers, spaces, hyphens, and apostrophes.")
            else:
                try:
                    profile_id = create_profile(cleaned_name, new_level)
                    if profile_id:
                        st.success(f"Profile '{cleaned_name}' created!")
                        st.rerun()
                    else:
                        st.error("Failed to create profile. Please try again.")
                except Exception as e:
                    st.error(f"Error creating profile: {str(e)}")

    # Activity history for current profile
    st.divider()
    render_section_header("Recent Activity")

    activities = get_activity_history(days=7, limit=20)
    if activities:
        for activity in activities[:10]:
            activity_type = activity.get("activity_type", "Unknown")
            activity_name = activity.get("activity_name", "")
            created_at = activity.get("created_at", "")[:16]  # Truncate timestamp
            score = activity.get("score")

            icon_map = {
                "vocab_review": "📚",
                "daily_mission": "🎤",
                "conversation": "💬",
                "mistake_fixed": "✅",
                "lesson": "📝"
            }
            icon = icon_map.get(activity_type, "📌")

            score_text = f" - Score: {score:.0f}%" if score else ""
            st.markdown(f"""
            <div style="padding: 0.5rem 0; border-bottom: 1px solid #E5E5EA;">
                <span>{icon}</span>
                <strong style="color: #000000;">{activity_name or activity_type}</strong>
                <span style="color: #8E8E93; font-size: 0.8rem;">{score_text}</span>
                <span style="float: right; color: #8E8E93; font-size: 0.75rem;">{created_at}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start learning to see your activity here!")


def render_profile_section():
    """Render the profile configuration section."""
    render_section_header("Your Profile")

    profile = get_user_profile()

    col1, col2 = st.columns([2, 1])

    with col1:
        # Name
        name = st.text_input(
            "Name",
            value=profile.get("name", ""),
            placeholder="Enter your name",
            max_chars=50
        )

        # Level
        level = st.selectbox(
            "Target Level",
            ["B2", "C1", "C2"],
            index=["B2", "C1", "C2"].index(profile.get("level", "C1"))
        )

        # Weekly goal
        weekly_goal = st.slider(
            "Weekly Session Goal",
            min_value=2,
            max_value=14,
            value=profile.get("weekly_goal", 6),
            help="Number of practice sessions per week"
        )

        # Focus areas
        focus_areas = profile.get("focus_areas", [])
        if isinstance(focus_areas, str):
            try:
                focus_areas = json.loads(focus_areas)
            except:
                focus_areas = []

        new_focus = st.multiselect(
            "Focus Areas",
            ["Vocabulary", "Grammar", "Verb Precision", "Register", "Pronunciation", "Writing", "Speaking"],
            default=focus_areas
        )

    with col2:
        # Stats summary
        st.markdown("### Your Stats")
        stats = get_total_stats()

        st.metric("Total Vocab", stats.get("total_vocab", 0))
        st.metric("Speaking Minutes", f"{stats.get('total_speaking', 0):.0f}")
        st.metric("Errors Fixed", stats.get("total_errors", 0))
        st.metric("Missions Done", stats.get("total_missions", 0))

        # Placement status
        if profile.get("placement_completed"):
            st.success("✅ Placement Complete")
            if profile.get("placement_score"):
                st.caption(f"Score: {profile['placement_score']:.0f}%")
        else:
            st.warning("⚠️ Placement Pending")

    # Save button
    if st.button("Save Profile", type="primary", use_container_width=True):
        cleaned_name = name.strip()
        # Input validation
        if not cleaned_name:
            st.error("Name cannot be empty.")
        elif len(cleaned_name) < 2:
            st.error("Name must be at least 2 characters long.")
        elif not cleaned_name.replace(" ", "").replace("-", "").replace("'", "").isalnum():
            st.error("Name can only contain letters, numbers, spaces, hyphens, and apostrophes.")
        else:
            update_user_profile({
                "name": cleaned_name,
                "level": level,
                "weekly_goal": weekly_goal,
                "focus_areas": new_focus,
                "placement_completed": profile.get("placement_completed", 0),
                "placement_score": profile.get("placement_score"),
                "dialect_preference": profile.get("dialect_preference", "Spain"),
            })
            st.success("Profile saved!")
            st.rerun()


def render_placement_test():
    """Render the placement/calibration test."""
    render_section_header("Placement Test")

    profile = get_user_profile()

    if profile.get("placement_completed"):
        st.success(f"🎉 You've completed the placement test! Score: {profile.get('placement_score', 0):.0f}%")

        if st.button("Retake Placement Test"):
            update_user_profile({**profile, "placement_completed": 0, "placement_score": None})
            st.session_state.placement_answers = {}
            st.session_state.placement_index = 0
            st.rerun()
        return

    st.markdown("""
    <div class="card-muted">
        <strong>About the Placement Test:</strong>
        <p>This short adaptive test helps calibrate your learning experience. It covers grammar, vocabulary, collocations, register, and pragmatic nuance.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize state
    if "placement_index" not in st.session_state:
        st.session_state.placement_index = 0
    if "placement_answers" not in st.session_state:
        st.session_state.placement_answers = {}

    questions = PLACEMENT_QUESTIONS
    index = st.session_state.placement_index

    if index >= len(questions):
        # Test complete - calculate score
        correct = sum(1 for i, q in enumerate(questions)
                     if st.session_state.placement_answers.get(i) == q["answer"])
        score = (correct / len(questions)) * 100

        # Determine level
        if score >= 85:
            recommended_level = "C2"
        elif score >= 65:
            recommended_level = "C1"
        else:
            recommended_level = "B2"

        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 2rem;">
            <h2>Placement Test Complete!</h2>
            <div class="metric-value" style="font-size: 4rem;">{score:.0f}%</div>
            <p>Recommended level: <strong>{recommended_level}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        # Save results
        if st.button("Save Results & Continue", type="primary"):
            update_user_profile({
                **profile,
                "placement_completed": 1,
                "placement_score": score,
                "level": recommended_level
            })
            st.success("Results saved!")
            st.rerun()

        return

    # Show current question
    question = questions[index]

    # Progress
    st.progress((index) / len(questions))
    st.caption(f"Question {index + 1} of {len(questions)}")

    # Question card
    level_color = {"B2": "muted", "C1": "primary", "C2": "secondary"}.get(question.get("level", "C1"), "muted")

    st.markdown(f"""
    <div class="exercise-card">
        <div class="exercise-header">
            <span class="exercise-type">{question.get('type', 'Question').upper()}</span>
            <span class="pill pill-{level_color}">{question.get('level', 'C1')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### {question['question']}")

    # Options
    options = question.get("options", [])
    selected = st.radio(
        "Select your answer:",
        options,
        key=f"placement_q_{index}"
    )

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if index > 0:
            if st.button("← Previous"):
                st.session_state.placement_index -= 1
                st.rerun()

    with col2:
        if st.button("Next →" if index < len(questions) - 1 else "Finish", type="primary"):
            st.session_state.placement_answers[index] = selected
            st.session_state.placement_index += 1
            st.rerun()


def render_preferences():
    """Render preferences section."""
    render_section_header("Preferences")

    profile = get_user_profile()

    # Dialect preference
    st.markdown("### Regional Spanish Preference")

    dialect = st.selectbox(
        "Primary dialect exposure:",
        list(DIALECT_MODULES.keys()),
        index=list(DIALECT_MODULES.keys()).index(profile.get("dialect_preference", "Spain"))
    )

    # Show dialect info
    dialect_info = DIALECT_MODULES.get(dialect, {})
    st.markdown(f"""
    <div class="card-muted">
        <strong>Features:</strong> {', '.join(dialect_info.get('features', []))}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Learning Preferences")

    # Session settings
    col1, col2 = st.columns(2)

    with col1:
        default_session = st.select_slider(
            "Default session length:",
            options=[5, 10, 15, 20, 30],
            value=10,
            format_func=lambda x: f"{x} min"
        )

        enable_sounds = st.toggle("Enable sound effects", value=True)

    with col2:
        daily_reminder = st.toggle("Daily practice reminder", value=False)

        show_hints = st.toggle("Show hints during exercises", value=True)

    st.divider()

    # Focus Mode and Grading Options - important UX options
    st.markdown("### Display & Input Options")

    col1, col2 = st.columns(2)

    with col1:
        focus_mode = st.toggle(
            "Focus Mode",
            value=bool(profile.get("focus_mode", 0)),
            help="Hide gamification elements like streaks, XP, and achievements to reduce distractions"
        )
        st.caption("Hides streaks, XP, achievements, and leaderboards")

    with col2:
        accent_tolerance = st.toggle(
            "Accent Tolerance Mode",
            value=bool(profile.get("accent_tolerance", 0)),
            help="Accept answers even without proper accent marks (á, é, í, ó, ú, ñ)"
        )
        st.caption("Accepts 'manana' as 'mañana', 'cafe' as 'café'")

    st.markdown("### Grading Strictness")
    st.caption("Control how strictly your answers are evaluated")

    grading_mode = st.radio(
        "Grading mode:",
        ["strict", "balanced", "lenient"],
        index=["strict", "balanced", "lenient"].index(profile.get("grading_mode", "balanced")),
        horizontal=True,
        help="Strict: exact spelling required. Balanced: minor typos forgiven. Lenient: meaning-first, focus on concepts."
    )

    grading_descriptions = {
        "strict": "Exact spelling and grammar required. Best for advanced learners preparing for exams.",
        "balanced": "Minor typos forgiven (1-2 characters). Accents handled based on toggle above.",
        "lenient": "Meaning-first approach. Accepts reasonable variations and focuses on concepts over form."
    }
    st.info(grading_descriptions[grading_mode])

    # Save preferences
    if st.button("Save Preferences", type="primary"):
        update_user_profile({
            **profile,
            "dialect_preference": dialect,
            "focus_mode": 1 if focus_mode else 0,
            "accent_tolerance": 1 if accent_tolerance else 0,
            "grading_mode": grading_mode
        })
        st.success("Preferences saved!")


def render_data_export():
    """Render data export section."""
    render_section_header("Data Export")

    st.markdown("""
    <div class="card-muted">
        <strong>Export your learning data:</strong>
        <p>Download your vocabulary, mistakes, transcripts, and progress as JSON or CSV files.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Vocabulary")
        vocab_json = export_vocab_json()

        st.download_button(
            label="📥 Download Vocabulary (JSON)",
            data=vocab_json,
            file_name=f"vivalingo_vocab_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

        # CSV export
        import csv
        from io import StringIO
        vocab_data = json.loads(vocab_json)

        if vocab_data:
            csv_buffer = StringIO()
            if vocab_data:
                writer = csv.DictWriter(csv_buffer, fieldnames=vocab_data[0].keys())
                writer.writeheader()
                writer.writerows(vocab_data)
                csv_content = csv_buffer.getvalue()
            else:
                csv_content = ""

            st.download_button(
                label="📥 Download Vocabulary (CSV)",
                data=csv_content,
                file_name=f"vivalingo_vocab_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col2:
        st.markdown("### Mistakes")
        mistakes_json = export_mistakes_json()

        st.download_button(
            label="📥 Download Mistakes (JSON)",
            data=mistakes_json,
            file_name=f"vivalingo_mistakes_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Progress History")
        progress_json = export_progress_json()

        st.download_button(
            label="📥 Download Progress (JSON)",
            data=progress_json,
            file_name=f"vivalingo_progress_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

    with col4:
        st.markdown("### Portfolio")
        portfolio = load_portfolio()
        portfolio_json = json.dumps(portfolio, indent=2, ensure_ascii=False)

        st.download_button(
            label="📥 Download Portfolio (JSON)",
            data=portfolio_json,
            file_name=f"vivalingo_portfolio_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

    # Full backup
    st.divider()
    st.markdown("### Full Backup")

    if st.button("🗃️ Create Full Backup", use_container_width=True):
        backup = {
            "vocabulary": json.loads(export_vocab_json()),
            "mistakes": json.loads(export_mistakes_json()),
            "progress": json.loads(export_progress_json()),
            "portfolio": load_portfolio(),
            "profile": get_user_profile(),
            "export_date": date.today().isoformat(),
        }

        backup_json = json.dumps(backup, indent=2, ensure_ascii=False)

        st.download_button(
            label="📥 Download Full Backup",
            data=backup_json,
            file_name=f"vivalingo_backup_{date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

    # Import section
    st.divider()
    st.markdown("### Import Data")

    uploaded = st.file_uploader("Upload a backup file to restore:", type=["json"])

    if uploaded:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            st.json({"keys": list(data.keys()), "export_date": data.get("export_date", "Unknown")})

            if st.button("⚠️ Restore from Backup", type="primary"):
                # This would need implementation to restore data
                st.warning("Import functionality coming soon!")
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid backup.")
