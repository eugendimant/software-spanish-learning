"""Dialect Navigator - Compare and learn Spanish varieties."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header, render_html
from utils.database import record_progress, log_activity, get_user_profile
from utils.content import DIALECT_MODULES, DIALECT_CONVERTER
from utils.helpers import seed_for_day


def render_dialect_navigator_page():
    """Render the Dialect Navigator page."""
    render_hero(
        title="Dialect Navigator",
        subtitle="Navigate Spanish varieties: Spain, Mexico, Argentina, Colombia, Chile. Learn regional vocabulary, pronunciation markers, and cultural nuances.",
        pills=["Spain", "Mexico", "Argentina", "Colombia", "Chile"]
    )

    # Get user's dialect preference
    profile = get_user_profile()
    preferred_dialect = profile.get("dialect_preference", "Spain")

    # Initialize session state
    if "dn_dialect" not in st.session_state:
        st.session_state.dn_dialect = preferred_dialect
    if "dn_mode" not in st.session_state:
        st.session_state.dn_mode = "explore"

    # Mode selection
    render_section_header("Navigation Mode")

    mode = st.radio(
        "Choose how to explore:",
        [
            "Explore Dialects",
            "Compare Phrases",
            "Dialect Quiz",
            "Your Preference Settings"
        ],
        horizontal=True
    )

    st.divider()

    if mode == "Explore Dialects":
        render_dialect_exploration()
    elif mode == "Compare Phrases":
        render_phrase_comparison()
    elif mode == "Dialect Quiz":
        render_dialect_quiz()
    else:
        render_preference_settings()


def render_dialect_exploration():
    """Render dialect exploration mode."""
    render_section_header("Explore a Dialect")

    # Dialect selector
    dialects = list(DIALECT_MODULES.keys())
    selected = st.selectbox(
        "Select a dialect to explore:",
        dialects,
        index=dialects.index(st.session_state.dn_dialect) if st.session_state.dn_dialect in dialects else 0
    )

    st.session_state.dn_dialect = selected
    dialect_data = DIALECT_MODULES.get(selected, {})

    if not dialect_data:
        st.warning("No data available for this dialect.")
        return

    # Display dialect information
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### {selected} Spanish")

        # Features
        st.markdown("**Key Features:**")
        for feature in dialect_data.get("features", []):
            st.markdown(f"- {feature}")

        # Sample sentence
        st.markdown("**Sample:**")
        st.info(dialect_data.get("sample", ""))

    with col2:
        st.markdown("### Quick Reference")

        # Lexicon
        lexicon = dialect_data.get("lexicon", {})
        if lexicon:
            st.markdown("**Local vocabulary:**")
            for term, meaning in lexicon.items():
                st.markdown(f"- **{term}**: {meaning}")

    # Dialect trap (quiz element)
    st.divider()
    st.markdown("### Test Your Understanding")

    trap = dialect_data.get("trap", {})
    if trap:
        st.markdown(f"**Question:** {trap.get('question', '')}")

        options = trap.get("options", [])
        answer = trap.get("answer", "")

        user_answer = st.radio(
            "Select your answer:",
            options,
            key=f"trap_{selected}"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Check Answer", type="primary", key="key_check_dialect_answer"):
                if user_answer == answer:
                    st.success("Correct! You understand this dialect nuance.")
                    record_progress({"vocab_reviewed": 1})
                    log_activity("dialect_navigator", "trap_correct", selected)
                else:
                    st.error(f"Not quite. The answer is: {answer}")
                    log_activity("dialect_navigator", "trap_incorrect", selected)


def render_phrase_comparison():
    """Render phrase comparison across dialects."""
    render_section_header("Compare Phrases Across Dialects")

    st.markdown("""
    See how the same concept is expressed differently across Spanish-speaking regions.
    This helps you recognize and adapt to different varieties.
    """)

    # Category selection
    categories = list(DIALECT_CONVERTER.keys())
    selected_category = st.selectbox(
        "Choose a phrase category:",
        categories,
        format_func=lambda x: x.replace("_", " ").title()
    )

    phrases = DIALECT_CONVERTER.get(selected_category, {})

    if not phrases:
        st.warning("No phrases available for this category.")
        return

    # Display comparison table
    st.markdown(f"### {selected_category.replace('_', ' ').title()}")

    # Create comparison cards
    cols = st.columns(len(phrases))

    for col, (dialect, phrase) in zip(cols, phrases.items()):
        with col:
            is_neutral = dialect == "neutral"

            st.markdown(f"""
            <div class="card" style="{'background: rgba(99, 102, 241, 0.1); border-color: rgba(99, 102, 241, 0.3);' if is_neutral else ''}">
                <div style="font-weight: 600; color: {'#007AFF' if is_neutral else '#000000'};">
                    {dialect}
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.95rem;">
                    {phrase}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Practice section
    st.divider()
    st.markdown("### Practice")

    st.markdown(f"**Neutral form:** {phrases.get('neutral', '')}")

    target_dialect = st.selectbox(
        "Convert to:",
        [d for d in phrases.keys() if d != "neutral"]
    )

    user_attempt = st.text_input(
        f"Write the {target_dialect} version:",
        placeholder="Escriba su versión..."
    )

    if st.button("Check", type="primary", key="key_check_phrase_comparison"):
        if user_attempt.strip():
            correct = phrases.get(target_dialect, "")

            # Simple similarity check
            if user_attempt.lower().strip() in correct.lower() or correct.lower() in user_attempt.lower().strip():
                st.success(f"Great! The {target_dialect} version is: {correct}")
                record_progress({"vocab_reviewed": 1})
            else:
                st.info(f"The {target_dialect} version is: {correct}")
                st.caption("Compare your answer with the correct form.")


def render_dialect_quiz():
    """Render dialect identification quiz."""
    render_section_header("Dialect Identification Quiz")

    st.markdown("""
    Test your ability to identify which Spanish-speaking region a phrase comes from.
    This builds your ear for regional differences.
    """)

    # Generate quiz questions from dialect modules
    questions = []
    for dialect, data in DIALECT_MODULES.items():
        lexicon = data.get("lexicon", {})
        for term, meaning in lexicon.items():
            questions.append({
                "term": term,
                "meaning": meaning,
                "dialect": dialect,
                "sample": data.get("sample", "")
            })

    if not questions:
        st.warning("No quiz questions available.")
        return

    # Daily seed for consistent questions
    seed = seed_for_day(date.today())
    random.seed(seed)

    # Select questions for today
    daily_questions = random.sample(questions, min(5, len(questions)))

    # Quiz state
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    dialects = list(DIALECT_MODULES.keys())

    for i, q in enumerate(daily_questions):
        st.markdown(f"**Question {i+1}:** What dialect uses the word **'{q['term']}'** (meaning: {q['meaning']})?")

        answer = st.radio(
            f"Select dialect for question {i+1}:",
            dialects,
            key=f"quiz_q_{i}",
            horizontal=True
        )

        st.session_state.quiz_answers[i] = {
            "selected": answer,
            "correct": q["dialect"]
        }

        st.markdown("---")

    if st.button("Submit Quiz", type="primary", use_container_width=True, key="key_submit_dialect_quiz"):
        st.session_state.quiz_submitted = True

        # Calculate score
        correct_count = sum(
            1 for a in st.session_state.quiz_answers.values()
            if a["selected"] == a["correct"]
        )

        total = len(daily_questions)
        percentage = (correct_count / total * 100) if total > 0 else 0

        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3>Quiz Results</h3>
            <div class="metric-value" style="color: {'#10b981' if percentage >= 60 else '#f59e0b'};">
                {correct_count}/{total} ({percentage:.0f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show correct answers
        st.markdown("### Answers:")
        for i, q in enumerate(daily_questions):
            user = st.session_state.quiz_answers.get(i, {}).get("selected", "")
            correct = q["dialect"]
            icon = "✅" if user == correct else "❌"
            st.markdown(f"{icon} **{q['term']}** is from **{correct}** (you chose: {user})")

        record_progress({"vocab_reviewed": correct_count})
        log_activity("dialect_navigator", "quiz_complete", f"Score: {correct_count}/{total}")

    # Reset button
    if st.session_state.quiz_submitted:
        if st.button("Try Again Tomorrow", key="key_try_quiz_again"):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()


def render_preference_settings():
    """Render dialect preference settings."""
    render_section_header("Your Dialect Preferences")

    st.markdown("""
    Set your primary dialect focus. This affects which vocabulary and expressions
    are emphasized throughout the app.
    """)

    profile = get_user_profile()
    current_preference = profile.get("dialect_preference", "Spain")

    dialects = list(DIALECT_MODULES.keys())

    # Display dialect cards
    cols = st.columns(len(dialects))

    for col, dialect in zip(cols, dialects):
        with col:
            data = DIALECT_MODULES.get(dialect, {})
            is_selected = dialect == current_preference

            flag_map = {'Spain': '&#x1F1EA;&#x1F1F8;', 'Mexico': '&#x1F1F2;&#x1F1FD;', 'Argentina': '&#x1F1E6;&#x1F1F7;', 'Colombia': '&#x1F1E8;&#x1F1F4;', 'Chile': '&#x1F1E8;&#x1F1F1;'}
            flag = flag_map.get(dialect, '')
            feature = data.get('features', [''])[0] if data.get('features') else ''
            border_style = 'border: 2px solid #007AFF; background: rgba(99, 102, 241, 0.05);' if is_selected else ''
            render_html(f"""
                <div class="card" style="text-align: center; {border_style}">
                    <div style="font-size: 2rem;">{flag}</div>
                    <div style="font-weight: 600; margin-top: 0.5rem;">{dialect}</div>
                    <div style="font-size: 0.8rem; color: #8E8E93; margin-top: 0.25rem;">{feature}</div>
                </div>
            """)

            if st.button(
                "Selected" if is_selected else "Select",
                key=f"pref_{dialect}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                disabled=is_selected
            ):
                from utils.database import update_user_profile
                profile["dialect_preference"] = dialect
                update_user_profile(profile)
                st.success(f"Preference updated to {dialect} Spanish!")
                st.rerun()

    # Dialect comparison info
    st.divider()
    st.markdown("### Why This Matters")

    st.markdown("""
    Spanish varies significantly across regions. Your dialect preference affects:

    - **Vocabulary suggestions**: Regional terms vs. neutral alternatives
    - **Pronunciation notes**: Local sound patterns
    - **Cultural contexts**: Region-specific expressions and customs
    - **Conversation practice**: Partner responses match regional patterns

    You can always explore other dialects in the comparison tools above.
    """)
