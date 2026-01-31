"""Writing Coach with error feedback and forced re-production."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    record_progress, record_error_fingerprint, save_mistake, log_activity
)
from utils.content import (
    WRITING_COACH_TEMPLATES, PRAGMATICS_WARNINGS, RULE_BOUNDARIES
)
from utils.helpers import detect_language, seed_for_day


def render_writing_coach_page():
    """Render the Writing Coach page."""
    render_hero(
        title="Writing Coach",
        subtitle="Develop precision through constrained writing, error feedback, and forced re-production.",
        pills=["Error Type", "Rule", "Examples", "Rewrite"]
    )

    # Initialize session state
    if "wc_mode" not in st.session_state:
        st.session_state.wc_mode = "free_writing"
    if "wc_text" not in st.session_state:
        st.session_state.wc_text = ""
    if "wc_feedback" not in st.session_state:
        st.session_state.wc_feedback = None
    if "wc_rewrite_required" not in st.session_state:
        st.session_state.wc_rewrite_required = False
    if "wc_constraint" not in st.session_state:
        st.session_state.wc_constraint = None
    if "wc_original_errors" not in st.session_state:
        st.session_state.wc_original_errors = []

    # Mode selection
    render_section_header("Practice Mode")

    mode = st.radio(
        "Choose your practice mode:",
        [
            "Free Writing + Feedback",
            "Tone Transformation",
            "Constraint Rewrites",
            "Error Pattern Drills"
        ],
        horizontal=True
    )

    st.divider()

    if mode == "Free Writing + Feedback":
        render_free_writing()
    elif mode == "Tone Transformation":
        render_tone_transformation()
    elif mode == "Constraint Rewrites":
        render_constraint_rewrites()
    else:
        render_error_pattern_drills()


def render_free_writing():
    """Render free writing mode with detailed feedback."""
    render_section_header("Write and Get Feedback")

    st.markdown("""
    Write in Spanish about any topic. You'll receive detailed feedback on:
    - Grammar patterns (ser/estar, por/para, subjunctive)
    - Pragmatic appropriateness (too direct, register mismatch)
    - Common errors and calques
    """)

    # Text input
    text = st.text_area(
        "Write in Spanish:",
        value=st.session_state.wc_text,
        height=150,
        placeholder="Escriba su texto aquí...",
        key="free_writing_input"
    )
    st.session_state.wc_text = text

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Analyze My Writing", type="primary", use_container_width=True):
            if text.strip():
                # Validate Spanish
                lang_info = detect_language(text)
                if lang_info["language"] == "english":
                    st.warning("Please write in Spanish for feedback.")
                else:
                    feedback = analyze_writing(text)
                    st.session_state.wc_feedback = feedback
                    st.session_state.wc_original_errors = feedback.get("errors", [])

                    if feedback.get("errors"):
                        st.session_state.wc_rewrite_required = True
            else:
                st.warning("Please write something first.")

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.wc_text = ""
            st.session_state.wc_feedback = None
            st.session_state.wc_rewrite_required = False
            st.rerun()

    # Display feedback
    if st.session_state.wc_feedback:
        render_writing_feedback(st.session_state.wc_feedback)

        # Forced re-production section
        if st.session_state.wc_rewrite_required and st.session_state.wc_original_errors:
            st.divider()
            render_section_header("Forced Re-Production")

            st.markdown("""
            <div class="feedback-box feedback-warning">
                <strong>Practice makes permanent!</strong> Rewrite your text, correcting the errors identified above.
            </div>
            """, unsafe_allow_html=True)

            rewrite = st.text_area(
                "Rewrite your text with corrections:",
                height=150,
                placeholder="Escriba su texto corregido aquí...",
                key="rewrite_input"
            )

            if st.button("Check Rewrite", type="primary"):
                if rewrite.strip():
                    # Check if original errors are fixed
                    new_feedback = analyze_writing(rewrite)
                    new_errors = new_feedback.get("errors", [])

                    # Compare error types
                    original_types = {e["type"] for e in st.session_state.wc_original_errors}
                    new_types = {e["type"] for e in new_errors}

                    fixed_errors = original_types - new_types
                    remaining_errors = original_types & new_types

                    if not remaining_errors:
                        st.markdown("""
                        <div class="feedback-box feedback-success">
                            Excellent! You've corrected all the identified errors. Great practice!
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.wc_rewrite_required = False
                        record_progress({"errors_fixed": len(fixed_errors)})
                        log_activity("writing_coach", "rewrite_complete",
                                   f"Fixed {len(fixed_errors)} errors")
                    else:
                        st.markdown(f"""
                        <div class="feedback-box feedback-warning">
                            You fixed {len(fixed_errors)} error(s), but {len(remaining_errors)} type(s) remain.
                            Check the feedback above and try again.
                        </div>
                        """, unsafe_allow_html=True)

                    # Show new feedback
                    if new_errors:
                        render_writing_feedback(new_feedback)


def analyze_writing(text: str) -> dict:
    """Analyze writing for errors and provide detailed feedback."""
    feedback = {
        "errors": [],
        "pragmatics": [],
        "strengths": [],
        "suggestions": []
    }

    text_lower = text.lower()

    # Check for common grammar errors
    error_patterns = [
        {
            "pattern": "la problema",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "gender_noun",
            "correction": "el problema",
            "rule": WRITING_COACH_TEMPLATES["error_feedback"].get("gender_agreement", {}).get("rule", ""),
        },
        {
            "pattern": "la sistema",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "gender_noun",
            "correction": "el sistema",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas.",
        },
        {
            "pattern": "estudio por",
            "type": "por_para",
            "category": "prepositions",
            "subcategory": "por_para",
            "correction": "estudio para",
            "rule": WRITING_COACH_TEMPLATES["error_feedback"].get("por_para", {}).get("rule", ""),
        },
        {
            "pattern": "depende en",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "en_a_location",
            "correction": "depende de",
            "rule": "El verbo 'depender' siempre se construye con la preposición 'de'.",
        },
        {
            "pattern": "quiero que vienes",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "quiero que vengas",
            "rule": WRITING_COACH_TEMPLATES["error_feedback"].get("subjunctive_triggers", {}).get("rule", ""),
        },
        {
            "pattern": "cuando llega",
            "type": "subjunctive_future",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "cuando llegue",
            "rule": "Cuando + futuro temporal requiere subjuntivo.",
        },
        {
            "pattern": "estoy excitado",
            "type": "false_friend",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "estoy emocionado/entusiasmado",
            "rule": "'Excitado' tiene connotación sexual en español. Usa 'emocionado' o 'entusiasmado'.",
        },
        {
            "pattern": "realizar que",
            "type": "false_friend",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "darse cuenta de que",
            "rule": "'Realizar' significa 'llevar a cabo', no 'darse cuenta' (realize).",
        },
    ]

    for pattern_data in error_patterns:
        if pattern_data["pattern"] in text_lower:
            error = {
                "type": pattern_data["type"],
                "category": pattern_data["category"],
                "subcategory": pattern_data["subcategory"],
                "found": pattern_data["pattern"],
                "correction": pattern_data["correction"],
                "rule": pattern_data["rule"],
            }
            feedback["errors"].append(error)

            # Record in fingerprint system
            record_error_fingerprint(
                pattern_data["category"],
                pattern_data["subcategory"],
                is_error=True,
                user_input=pattern_data["pattern"],
                expected=pattern_data["correction"],
                rule_explanation=pattern_data["rule"]
            )

    # Check pragmatics issues
    for warning in PRAGMATICS_WARNINGS:
        if warning["pattern"].lower() in text_lower:
            feedback["pragmatics"].append({
                "pattern": warning["pattern"],
                "issue": warning["issue"],
                "explanation": warning["explanation"],
                "alternatives": warning["alternatives"],
            })

    # Check for strengths
    strength_markers = [
        ("me parece que", "Good use of hedging!"),
        ("tal vez", "Nice use of softening language."),
        ("sin embargo", "Great use of contrast markers."),
        ("aunque", "Good concessive construction."),
        ("le agradecería", "Excellent formal politeness marker."),
    ]

    for marker, msg in strength_markers:
        if marker in text_lower:
            feedback["strengths"].append(msg)

    # Add suggestions based on text length and content
    word_count = len(text.split())
    if word_count < 20:
        feedback["suggestions"].append("Try writing longer texts for more practice.")

    if "pero" in text_lower and "sin embargo" not in text_lower:
        feedback["suggestions"].append("Consider using 'sin embargo' for more formal contrast.")

    return feedback


def render_writing_feedback(feedback: dict):
    """Render detailed feedback for writing."""
    st.divider()
    render_section_header("Feedback")

    # Suggestions section (renamed from "Errors")
    if feedback.get("errors"):
        st.markdown("### Areas to Polish")

        for error in feedback["errors"]:
            with st.expander(f"**{error['type'].replace('_', ' ').title()}**: `{error['found']}`", expanded=True):
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**What you wrote:**")
                    st.markdown(f"<div class='feedback-box feedback-warning'>{error['found']}</div>",
                              unsafe_allow_html=True)

                with col2:
                    st.markdown("**Try this instead:**")
                    st.markdown(f"<div class='feedback-box feedback-success'>{error['correction']}</div>",
                              unsafe_allow_html=True)

                if error.get("rule"):
                    st.info(f"**Why?** {error['rule']}")

                # Show related boundary cases if available
                boundary = RULE_BOUNDARIES.get(error["type"])
                if boundary:
                    st.markdown("**Good to know:**")
                    for case in boundary.get("boundary_cases", [])[:2]:
                        st.caption(f"- {case['case']}: {case['explanation']}")
    else:
        st.markdown("""
        <div class="feedback-box feedback-success">
            Looking good! No major issues detected in your writing.
        </div>
        """, unsafe_allow_html=True)

    # Pragmatics section
    if feedback.get("pragmatics"):
        st.markdown("### Pragmatic Issues")

        for pragma in feedback["pragmatics"]:
            st.markdown(f"""
            <div class="feedback-box feedback-warning">
                <strong>{pragma['issue'].replace('_', ' ').title()}</strong><br>
                {pragma['explanation']}
                <br><br>
                <strong>Try instead:</strong> {', '.join(pragma['alternatives'][:3])}
            </div>
            """, unsafe_allow_html=True)

    # Strengths section
    if feedback.get("strengths"):
        st.markdown("### What You Did Well")
        for strength in feedback["strengths"]:
            st.markdown(f"- {strength}")

    # Suggestions
    if feedback.get("suggestions"):
        st.markdown("### Suggestions")
        for suggestion in feedback["suggestions"]:
            st.caption(f"💡 {suggestion}")


def render_tone_transformation():
    """Render tone transformation exercises."""
    render_section_header("Tone Transformation")

    st.markdown("""
    Practice adjusting register and tone. You'll be given a sentence and asked to rewrite it
    in a different register (formal/informal) or tone (polite/direct).
    """)

    templates = WRITING_COACH_TEMPLATES.get("tone_rewrites", {})

    # Select transformation type
    transform_type = st.selectbox(
        "Transformation type:",
        list(templates.keys()),
        format_func=lambda x: x.replace("_", " ").title()
    )

    template = templates.get(transform_type, {})

    if template:
        st.markdown(f"**Instruction:** {template.get('instruction', '')}")

        # Determine which example to show based on the transformation
        if "informal" in transform_type.lower():
            source = template.get("example_formal", "")
            target = template.get("example_informal", "")
            source_label = "Formal version"
            target_label = "Informal version"
        elif "formal" in transform_type.lower():
            source = template.get("example_informal", "")
            target = template.get("example_formal", "")
            source_label = "Informal version"
            target_label = "Formal version"
        else:
            source = template.get("example_direct", "")
            target = template.get("example_polite", "")
            source_label = "Direct version"
            target_label = "Polite version"

        st.markdown(f"**{source_label}:**")
        st.info(source)

        # User attempt
        user_attempt = st.text_area(
            f"Rewrite it ({target_label}):",
            height=100,
            placeholder="Escriba su versión aquí..."
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Check My Version", type="primary", use_container_width=True):
                if user_attempt.strip():
                    # Validate Spanish
                    lang_info = detect_language(user_attempt)
                    if lang_info["language"] == "english":
                        st.warning("Please write in Spanish.")
                    else:
                        st.markdown("**Example answer:**")
                        st.success(target)
                        st.markdown("""
                        <div class="feedback-box feedback-info">
                            Compare your version with the example. Key markers to look for:
                            politeness phrases, formal pronouns (usted), conditional verbs, etc.
                        </div>
                        """, unsafe_allow_html=True)

                        record_progress({"writing_words": len(user_attempt.split())})
                        log_activity("writing_coach", "tone_transformation", transform_type)

        with col2:
            if st.button("Show Answer", use_container_width=True):
                st.markdown(f"**{target_label}:**")
                st.success(target)


def render_constraint_rewrites():
    """Render constraint-based rewrite exercises."""
    render_section_header("Constraint Rewrites")

    st.markdown("""
    Rewrite sentences with specific grammatical constraints. This builds flexibility
    and helps you internalize patterns.
    """)

    constraints = WRITING_COACH_TEMPLATES.get("constraint_rewrites", [])

    if not constraints:
        st.warning("No constraint exercises available.")
        return

    # Daily seed for variety
    seed = seed_for_day(date.today())
    random.seed(seed)
    exercise = random.choice(constraints)

    st.markdown(f"**Constraint:** {exercise.get('instruction', '')}")

    st.markdown("**Original sentence:**")
    st.info(exercise.get("original", ""))

    user_attempt = st.text_area(
        "Your rewrite:",
        height=100,
        placeholder="Escriba su versión aquí..."
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Check", type="primary", use_container_width=True):
            if user_attempt.strip():
                lang_info = detect_language(user_attempt)
                if lang_info["language"] == "english":
                    st.warning("Please write in Spanish.")
                else:
                    st.markdown("**Example answer:**")
                    st.success(exercise.get("example", ""))

                    record_progress({"writing_words": len(user_attempt.split())})
                    log_activity("writing_coach", "constraint_rewrite", exercise.get("constraint", ""))

    with col2:
        if st.button("Show Answer", use_container_width=True):
            st.success(exercise.get("example", ""))

    with col3:
        if st.button("New Exercise", use_container_width=True):
            st.rerun()


def render_error_pattern_drills():
    """Render drills focused on specific error patterns."""
    render_section_header("Error Pattern Drills")

    st.markdown("""
    Practice the grammar patterns that cause the most confusion for Spanish learners.
    Each drill focuses on a specific error type with rule explanations and examples.
    """)

    # Select error category
    error_templates = WRITING_COACH_TEMPLATES.get("error_feedback", {})
    categories = list(error_templates.keys())

    if not categories:
        st.warning("No error pattern drills available.")
        return

    selected = st.selectbox(
        "Focus on:",
        categories,
        format_func=lambda x: x.replace("_", " ").title()
    )

    template = error_templates.get(selected, {})

    if template:
        # Rule display
        st.markdown("### Rule")
        st.info(template.get("rule", ""))

        # Examples
        st.markdown("### Examples")
        for example in template.get("examples", []):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Incorrect:** ~~{example.get('wrong', '')}~~")
            with col2:
                st.markdown(f"**Correct:** {example.get('correct', '')}")

        # Practice prompts
        st.markdown("### Practice")
        prompts = template.get("practice_prompts", [])

        for i, prompt in enumerate(prompts):
            st.markdown(f"**{i+1}.** {prompt}")

            user_response = st.text_input(
                f"Your answer for prompt {i+1}:",
                key=f"drill_{selected}_{i}",
                placeholder="Escriba su respuesta..."
            )

            if user_response:
                # Validate Spanish
                lang_info = detect_language(user_response)
                if lang_info["language"] == "english":
                    st.caption("Please write in Spanish.")
                else:
                    st.caption("Submitted. Check that your answer follows the rule above.")

        if st.button("Submit All", type="primary"):
            record_progress({"grammar_reviewed": 1})
            log_activity("writing_coach", "error_drill", selected)
            st.success("Great practice! Keep working on this pattern.")
