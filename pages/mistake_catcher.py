"""Real-Time Mistake Catcher page."""
import streamlit as st

from utils.theme import render_hero, render_section_header
from utils.database import save_mistake, record_progress
from utils.content import COMMON_MISTAKES, GRAMMAR_MICRODRILLS
from utils.helpers import check_text_for_mistakes, generate_corrected_text, highlight_diff


def render_mistake_catcher_page():
    """Render the Real-Time Mistake Catcher page."""
    render_hero(
        title="Mistake Catcher",
        subtitle="Real-time error detection for gender, agreement, tense, clitics, and common mistakes. Fix errors before they fossilize.",
        pills=["Gender", "Agreement", "Ser/Estar", "Prepositions", "Clitics"]
    )

    # Initialize session state
    if "mc_text" not in st.session_state:
        st.session_state.mc_text = ""
    if "mc_mistakes" not in st.session_state:
        st.session_state.mc_mistakes = []
    if "mc_corrected" not in st.session_state:
        st.session_state.mc_corrected = ""

    # Mode selection
    tabs = st.tabs(["✍️ Check Your Text", "📝 Grammar Drills", "📚 Common Mistakes Reference"])

    # Tab 1: Text Checker
    with tabs[0]:
        render_text_checker()

    # Tab 2: Grammar Drills
    with tabs[1]:
        render_grammar_drills()

    # Tab 3: Reference
    with tabs[2]:
        render_mistakes_reference()


def render_text_checker():
    """Render the text checking interface."""
    render_section_header("Check Your Spanish")

    st.markdown("""
    <div class="card-muted">
        <strong>How it works:</strong> Type or paste your Spanish text below.
        The system will flag common intermediate mistakes and offer corrections with explanations.
    </div>
    """, unsafe_allow_html=True)

    # Text input
    user_text = st.text_area(
        "Enter your Spanish text:",
        value=st.session_state.mc_text,
        height=150,
        placeholder="Escriba su texto aqui... (e.g., 'Yo dependo en mi equipo para la proyecto.')",
        key="text_input"
    )
    st.session_state.mc_text = user_text

    col1, col2 = st.columns([1, 4])

    with col1:
        check_btn = st.button("🔍 Check", type="primary", use_container_width=True)

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.mc_text = ""
            st.session_state.mc_mistakes = []
            st.session_state.mc_corrected = ""
            st.rerun()

    if check_btn and user_text.strip():
        # Perform mistake checking
        mistakes = check_text_for_mistakes(user_text)
        st.session_state.mc_mistakes = mistakes

        if mistakes:
            corrected = generate_corrected_text(user_text, mistakes)
            st.session_state.mc_corrected = corrected

    # Display results
    if st.session_state.mc_mistakes:
        st.divider()
        render_section_header("Results")

        mistakes = st.session_state.mc_mistakes

        # Summary
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid var(--warning);">
            <strong>Found {len(mistakes)} potential issue{'s' if len(mistakes) > 1 else ''}:</strong>
        </div>
        """, unsafe_allow_html=True)

        # Show diff
        if st.session_state.mc_corrected:
            st.markdown("### Corrected Version")

            diff_html = highlight_diff(st.session_state.mc_text, st.session_state.mc_corrected)
            st.markdown(f"""
            <div class="card-muted">
                <p style="font-size: 1.125rem; line-height: 1.8;">{st.session_state.mc_corrected}</p>
            </div>
            """, unsafe_allow_html=True)

        # Detailed mistakes
        st.markdown("### Detailed Corrections")

        for i, mistake in enumerate(mistakes, 1):
            error_icon = {
                "gender": "👤",
                "preposition": "📍",
                "copula": "🔄",
                "calque": "🌐",
                "false_friend": "⚠️",
            }.get(mistake.get("tag", ""), "❌")

            with st.expander(f"{error_icon} Issue {i}: {mistake['original']} → {mistake['correction']}", expanded=i == 1):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Original:** `{mistake['original']}`")
                    st.markdown(f"**Correction:** `{mistake['correction']}`")
                    st.markdown(f"**Explanation:** {mistake['explanation']}")

                    if mistake.get("examples"):
                        st.markdown("**Examples using the correct form:**")
                        for ex in mistake["examples"][:2]:
                            st.markdown(f"- _{ex}_")

                with col2:
                    st.markdown(f"""
                    <span class="pill pill-error">{mistake.get('tag', 'error')}</span>
                    """, unsafe_allow_html=True)

                    # Save to error notebook
                    if st.button("📝 Save to Notebook", key=f"save_mistake_{i}"):
                        save_mistake({
                            "user_text": st.session_state.mc_text,
                            "corrected_text": st.session_state.mc_corrected,
                            "error_type": mistake.get("tag", "unknown"),
                            "error_tag": mistake.get("tag"),
                            "pattern": mistake["original"],
                            "explanation": mistake["explanation"],
                            "examples": mistake.get("examples", []),
                        })
                        record_progress({"errors_fixed": 1})
                        st.success("Saved to your Error Notebook!")

    elif check_btn and user_text.strip():
        st.markdown("""
        <div class="feedback-box feedback-success">
            ✅ <strong>No common mistakes detected!</strong> Your text looks good.
        </div>
        """, unsafe_allow_html=True)


def render_grammar_drills():
    """Render grammar micro-drills."""
    render_section_header("Grammar Micro-Drills")

    st.markdown("""
    <div class="card-muted">
        Practice high-frequency grammar patterns: gender agreement, verb tenses, ser/estar, prepositions, and more.
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for drills
    if "gd_current" not in st.session_state:
        st.session_state.gd_current = 0
    if "gd_answered" not in st.session_state:
        st.session_state.gd_answered = {}

    # Category filter
    categories = list(set(d.get("category", "general") for d in GRAMMAR_MICRODRILLS))
    selected_category = st.selectbox(
        "Filter by category:",
        ["All"] + categories
    )

    # Filter drills
    if selected_category == "All":
        drills = GRAMMAR_MICRODRILLS
    else:
        drills = [d for d in GRAMMAR_MICRODRILLS if d.get("category") == selected_category]

    if not drills:
        st.info("No drills available for this category.")
        return

    # Current drill
    drill_idx = st.session_state.gd_current % len(drills)
    drill = drills[drill_idx]

    st.markdown(f"""
    <div class="exercise-card">
        <div class="exercise-header">
            <span class="exercise-type">{drill['focus']}</span>
            <span class="exercise-step">{drill_idx + 1}/{len(drills)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Question
    st.markdown(f"### {drill['prompt']}")

    # Options
    options = drill.get("options", [])
    answer_key = f"drill_{drill_idx}"

    selected = st.radio(
        "Select your answer:",
        options,
        key=answer_key
    )

    # Check answer
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Check Answer", type="primary"):
            correct = drill.get("answer", "")
            is_correct = selected == correct

            if is_correct:
                st.session_state.gd_answered[drill_idx] = True
                st.markdown("""
                <div class="feedback-box feedback-success">
                    ✅ <strong>Correct!</strong>
                </div>
                """, unsafe_allow_html=True)
                record_progress({"grammar_reviewed": 1})
            else:
                st.session_state.gd_answered[drill_idx] = False
                st.markdown(f"""
                <div class="feedback-box feedback-error">
                    ❌ The correct answer is: <strong>{correct}</strong>
                </div>
                """, unsafe_allow_html=True)

            # Show explanation
            st.info(f"**Why?** {drill.get('explanation', '')}")

            # Show examples
            if drill.get("examples"):
                st.markdown("**More examples:**")
                for ex in drill["examples"]:
                    st.markdown(f"- _{ex}_")

    with col2:
        if st.button("← Previous"):
            st.session_state.gd_current = max(0, st.session_state.gd_current - 1)
            st.rerun()

    with col3:
        if st.button("Next →"):
            st.session_state.gd_current += 1
            st.rerun()


def render_mistakes_reference():
    """Render reference of common mistakes."""
    render_section_header("Common Mistakes Reference")

    st.markdown("""
    <div class="card-muted">
        Review the most common mistakes made by intermediate Spanish learners.
        Understanding these patterns helps you avoid them.
    </div>
    """, unsafe_allow_html=True)

    # Group by tag
    mistakes_by_tag = {}
    for mistake in COMMON_MISTAKES:
        tag = mistake.get("tag", "other")
        if tag not in mistakes_by_tag:
            mistakes_by_tag[tag] = []
        mistakes_by_tag[tag].append(mistake)

    # Display by category
    for tag, mistakes in mistakes_by_tag.items():
        tag_icon = {
            "preposition": "📍",
            "gender": "👤",
            "calque": "🌐",
            "false_friend": "⚠️",
        }.get(tag, "❌")

        with st.expander(f"{tag_icon} {tag.replace('_', ' ').title()} ({len(mistakes)} patterns)"):
            for mistake in mistakes:
                st.markdown(f"""
                <div class="card" style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <span style="color: var(--error); text-decoration: line-through;">{mistake['pattern']}</span>
                            <span style="margin: 0 0.5rem;">→</span>
                            <span style="color: var(--success); font-weight: 600;">{mistake['correction']}</span>
                        </div>
                    </div>
                    <p style="margin-top: 0.5rem; color: var(--text-muted);">{mistake['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)

                if mistake.get("examples"):
                    st.caption("Examples: " + " | ".join(mistake["examples"][:2]))
