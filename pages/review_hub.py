"""Two-Layer Spaced Repetition Review Hub page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    get_vocab_for_review, update_vocab_review,
    get_grammar_for_review, get_mistakes_for_review, update_mistake_review,
    record_progress, save_issue_report, get_user_profile
)
from utils.content import GRAMMAR_MICRODRILLS
from utils.helpers import get_review_priority, detect_language, compare_answers, get_accent_feedback


def render_review_hub_page():
    """Render the Two-Layer Spaced Repetition Review Hub page."""
    # Check if micro-drill is active
    if st.session_state.get("microdrill_active"):
        render_microdrill()
        return

    render_hero(
        title="Review Hub",
        subtitle="Two-layer spaced repetition: vocabulary and grammar as separate streams, each with its own forgetting curve.",
        pills=["Vocabulary SRS", "Grammar SRS", "Interleaved Practice"]
    )

    # Initialize session state
    if "review_mode" not in st.session_state:
        st.session_state.review_mode = "mixed"
    if "review_queue" not in st.session_state:
        st.session_state.review_queue = []
    if "review_index" not in st.session_state:
        st.session_state.review_index = 0
    if "review_revealed" not in st.session_state:
        st.session_state.review_revealed = False

    # Mode selection
    col1, col2 = st.columns([2, 1])

    with col1:
        render_section_header("Review Session")

        mode = st.radio(
            "Choose review mode:",
            ["🔄 Mixed (Interleaved)", "📚 Vocabulary Only", "📝 Grammar Only", "❌ Errors Only"],
            horizontal=True,
            key="review_mode_select"
        )

        st.session_state.review_mode = {
            "🔄 Mixed (Interleaved)": "mixed",
            "📚 Vocabulary Only": "vocab",
            "📝 Grammar Only": "grammar",
            "❌ Errors Only": "errors"
        }.get(mode, "mixed")

    with col2:
        # Queue stats
        vocab_due = len(get_vocab_for_review())
        grammar_due = len(GRAMMAR_MICRODRILLS)  # Simplified for now
        errors_due = len(get_mistakes_for_review())

        st.markdown("### Items Due")
        st.markdown(f"📚 **Vocabulary:** {vocab_due}")
        st.markdown(f"📝 **Grammar:** {grammar_due}")
        st.markdown(f"❌ **Errors:** {errors_due}")

    st.divider()

    # Start or continue review
    if not st.session_state.review_queue:
        render_start_review()
    else:
        render_review_session()


def render_microdrill():
    """Render a 90-second micro-drill for a specific error pattern."""
    pattern = st.session_state.get("microdrill_pattern", {})

    render_hero(
        title="🔧 Fix It Now - Micro Drill",
        subtitle=f"90-second focused practice for: {pattern.get('error_type', 'grammar')} errors",
        pills=["Quick Fix", "Pattern Practice", "Reinforce"]
    )

    # Initialize drill state
    if "microdrill_step" not in st.session_state:
        st.session_state.microdrill_step = 0
    if "microdrill_correct" not in st.session_state:
        st.session_state.microdrill_correct = 0

    step = st.session_state.microdrill_step
    correct_answer = pattern.get("correct", "")
    explanation = pattern.get("explanation", "")
    original_pattern = pattern.get("pattern", "")

    # Progress indicator
    st.progress((step + 1) / 4)
    st.caption(f"Step {step + 1} of 4")

    if step == 0:
        # Step 1: Show the rule and explain
        st.markdown("### Step 1: Understand the Rule")
        st.markdown(f"""
        <div class="feedback-box feedback-info">
            <strong>Original error:</strong> {original_pattern}
            <br><strong>Correct form:</strong> {correct_answer}
        </div>
        """, unsafe_allow_html=True)
        st.info(f"**Why?** {explanation}")

        st.markdown("**Read and understand the rule above, then continue.**")
        if st.button("I understand → Continue", type="primary", use_container_width=True):
            st.session_state.microdrill_step = 1
            st.rerun()

    elif step == 1:
        # Step 2: Type the correct answer from memory
        st.markdown("### Step 2: Write It Yourself")
        st.markdown("Now type the **correct form** from memory:")

        user_input = st.text_input("Your answer:", key="microdrill_input_1")

        if st.button("Check", type="primary"):
            if user_input.strip().lower() == correct_answer.lower():
                st.success("Correct! You've got it.")
                st.session_state.microdrill_correct += 1
                st.session_state.microdrill_step = 2
                st.rerun()
            else:
                st.warning(f"Not quite. The correct answer is: **{correct_answer}**")
                st.caption("Try again or continue to the next step.")
                if st.button("Continue anyway →"):
                    st.session_state.microdrill_step = 2
                    st.rerun()

    elif step == 2:
        # Step 3: Explain why in your own words
        st.markdown("### Step 3: Explain It")
        st.markdown("In your own words, why is the following correct?")
        st.markdown(f"**{correct_answer}**")

        user_explanation = st.text_area("Your explanation:", key="microdrill_explain",
                                         placeholder="e.g., 'Because after prepositions we use...'")

        if st.button("Submit & Continue", type="primary"):
            if user_explanation.strip():
                st.success("Good reflection! Teaching yourself helps reinforce learning.")
                st.session_state.microdrill_correct += 1
            st.session_state.microdrill_step = 3
            st.rerun()

    elif step == 3:
        # Step 4: Final quick recall
        st.markdown("### Step 4: Quick Recall")
        st.markdown("One more time - type the **correct form**:")

        user_final = st.text_input("Final answer:", key="microdrill_final")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check & Finish", type="primary", use_container_width=True):
                if user_final.strip().lower() == correct_answer.lower():
                    st.session_state.microdrill_correct += 1
                    st.balloons()
                    st.success(f"Excellent! You got {st.session_state.microdrill_correct}/3 correct.")
                else:
                    st.warning(f"The correct answer was: **{correct_answer}**")
                    st.info(f"You got {st.session_state.microdrill_correct}/3 in this drill.")

                # Show completion
                st.markdown("---")
                st.markdown("### Micro-drill complete!")
                st.caption("This pattern has been reinforced. You'll see it again in review.")

                if st.button("Return to Review", use_container_width=True):
                    # Clean up
                    st.session_state.microdrill_active = False
                    st.session_state.microdrill_pattern = None
                    st.session_state.microdrill_step = 0
                    st.session_state.microdrill_correct = 0
                    st.rerun()

        with col2:
            if st.button("Skip & Return", use_container_width=True):
                st.session_state.microdrill_active = False
                st.session_state.microdrill_pattern = None
                st.session_state.microdrill_step = 0
                st.session_state.microdrill_correct = 0
                st.rerun()


def render_start_review():
    """Render the start review interface."""
    st.markdown("### Start a Review Session")

    # Session length selection
    session_length = st.select_slider(
        "Session length:",
        options=[5, 10, 15, 20, 30],
        value=10,
        format_func=lambda x: f"{x} items"
    )

    # Quick session option
    if st.session_state.get("quick_session_mode"):
        session_length = 10
        st.info("⚡ Quick session mode: 10 items")

    if st.button("Start Review", type="primary", use_container_width=True):
        build_review_queue(session_length)
        st.rerun()


def build_review_queue(length: int):
    """Build the review queue based on selected mode."""
    mode = st.session_state.review_mode
    queue = []

    if mode in ["mixed", "vocab"]:
        vocab_items = get_vocab_for_review()
        for item in vocab_items[:length // 2 if mode == "mixed" else length]:
            queue.append({
                "type": "vocab",
                "item": item,
                "front": item.get("term", ""),
                "back": item.get("meaning", ""),
                "example": item.get("example", ""),
            })

    if mode in ["mixed", "grammar"]:
        grammar_items = GRAMMAR_MICRODRILLS[:length // 2 if mode == "mixed" else length]
        for item in grammar_items:
            queue.append({
                "type": "grammar",
                "item": item,
                "front": item.get("prompt", ""),
                "options": item.get("options", []),
                "answer": item.get("answer", ""),
                "explanation": item.get("explanation", ""),
            })

    if mode in ["mixed", "errors"]:
        error_items = get_mistakes_for_review()
        for item in error_items[:length // 3 if mode == "mixed" else length]:
            queue.append({
                "type": "error",
                "item": item,
                "front": f"Fix: {item.get('pattern', '')}",
                "back": item.get('corrected_text', ''),
                "explanation": item.get("explanation", ""),
            })

    # Shuffle for interleaving
    if mode == "mixed":
        random.shuffle(queue)

    st.session_state.review_queue = queue[:length]
    st.session_state.review_index = 0
    st.session_state.review_revealed = False


def render_review_session():
    """Render the active review session."""
    queue = st.session_state.review_queue
    index = st.session_state.review_index

    if not queue or index >= len(queue):
        render_review_complete()
        return

    current = queue[index]

    # Progress bar
    progress = (index + 1) / len(queue)  # +1 for 1-based progress display
    st.progress(progress)
    st.caption(f"Card {index + 1} of {len(queue)}")

    # Card type indicator
    type_colors = {"vocab": "primary", "grammar": "secondary", "error": "error"}
    type_icons = {"vocab": "📚", "grammar": "📝", "error": "❌"}

    st.markdown(f"""
    <span class="pill pill-{type_colors.get(current['type'], 'muted')}">
        {type_icons.get(current['type'], '📋')} {current['type'].upper()}
    </span>
    """, unsafe_allow_html=True)

    # Render based on type
    if current["type"] == "vocab":
        render_vocab_card(current)
    elif current["type"] == "grammar":
        render_grammar_card(current)
    else:
        render_error_card(current)


def render_vocab_card(card: dict):
    """Render a vocabulary review card with tiered hints."""
    # Initialize hint level in session state
    hint_key = f"hint_level_{st.session_state.review_index}"
    if hint_key not in st.session_state:
        st.session_state[hint_key] = 0

    hint_level = st.session_state[hint_key]
    term = card['front']
    meaning = card['back']
    example = card.get('example', '')

    st.markdown(f"""
    <div class="card" style="text-align: center; padding: 2rem;">
        <h2 style="font-size: 2rem; margin-bottom: 1rem;">{term}</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.review_revealed:
        # Tiered hints system
        # Level 0: No hints
        # Level 1: First letter of meaning
        # Level 2: Category/part of speech hint
        # Level 3: Example sentence (with blank)
        # Level 4: Full reveal

        if hint_level >= 1:
            first_letter = meaning[0].upper() if meaning else "?"
            st.markdown(f"""
            <div class="feedback-box feedback-info" style="text-align: center;">
                <strong>Hint 1:</strong> Starts with "{first_letter}..."
            </div>
            """, unsafe_allow_html=True)

        if hint_level >= 2:
            # Try to detect part of speech from the term or meaning
            pos_hint = "noun/verb/adjective"
            if meaning:
                lower_meaning = meaning.lower()
                if lower_meaning.startswith("to "):
                    pos_hint = "verb (action)"
                elif lower_meaning.endswith("ly"):
                    pos_hint = "adverb"
                elif lower_meaning.endswith(("ness", "tion", "ment")):
                    pos_hint = "noun (concept)"
                elif lower_meaning.startswith(("a ", "an ", "the ")):
                    pos_hint = "noun (thing)"

            st.markdown(f"""
            <div class="feedback-box feedback-warning" style="text-align: center;">
                <strong>Hint 2:</strong> This is likely a {pos_hint}
            </div>
            """, unsafe_allow_html=True)

        if hint_level >= 3 and example:
            # Show example with the term blanked out
            blanked_example = example.replace(term, "______").replace(term.lower(), "______")
            st.markdown(f"""
            <div class="feedback-box feedback-success" style="text-align: center;">
                <strong>Hint 3 (Example):</strong> <em>"{blanked_example}"</em>
            </div>
            """, unsafe_allow_html=True)

        # Hint progression buttons
        col1, col2 = st.columns(2)

        with col1:
            if hint_level < 3:
                if st.button("💡 Get Hint", use_container_width=True):
                    st.session_state[hint_key] = hint_level + 1
                    st.rerun()
            else:
                st.caption("All hints used")

        with col2:
            if st.button("Show Answer", type="primary", use_container_width=True):
                st.session_state.review_revealed = True
                st.rerun()

        # Hint progress indicator
        st.caption(f"Hints used: {hint_level}/3 — Using hints is OK! They help build connections.")

    else:
        # Show answer
        st.markdown(f"""
        <div class="card-muted" style="text-align: center; margin: 1rem 0;">
            <h3>{meaning}</h3>
            <p><em>{example}</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Rating buttons - adjust based on hints used
        if hint_level == 0:
            st.markdown("### How well did you know it?")
        else:
            st.caption(f"You used {hint_level} hint(s) - that's fine for learning!")
            st.markdown("### Rate your recall (hints don't penalize you)")

        cols = st.columns(4)

        ratings = [
            ("Again", 1, "error"),
            ("Hard", 2, "warning"),
            ("Good", 4, "success"),
            ("Easy", 5, "primary")
        ]

        for col, (label, quality, color) in zip(cols, ratings):
            with col:
                if st.button(label, key=f"rate_{quality}", use_container_width=True):
                    # Update SRS
                    item = card["item"]
                    if item.get("term"):
                        update_vocab_review(item["term"], quality)
                    record_progress({"vocab_reviewed": 1})
                    # Clean up hint state
                    if hint_key in st.session_state:
                        del st.session_state[hint_key]
                    advance_review()


def render_report_issue(context: str, user_answer: str = "", expected_answer: str = "", key_prefix: str = ""):
    """Render a report issue button with modal-like UI."""
    report_key = f"show_report_{key_prefix}_{st.session_state.review_index}"

    if report_key not in st.session_state:
        st.session_state[report_key] = False

    if not st.session_state[report_key]:
        if st.button("⚠️ Report Issue", key=f"report_btn_{key_prefix}"):
            st.session_state[report_key] = True
            st.rerun()
    else:
        st.markdown("---")
        st.markdown("### Report an Issue")
        st.caption("Automated grading isn't perfect. If you think this answer was marked incorrectly, let us know.")

        report_type = st.selectbox(
            "Issue type:",
            ["My answer should be accepted", "The expected answer seems wrong", "The explanation is unclear", "Other"],
            key=f"report_type_{key_prefix}"
        )

        comment = st.text_area(
            "Please explain (optional):",
            placeholder="Why do you think your answer should be correct?",
            key=f"report_comment_{key_prefix}"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Report", type="primary", key=f"submit_report_{key_prefix}"):
                type_map = {
                    "My answer should be accepted": "unfair_marking",
                    "The expected answer seems wrong": "wrong_answer",
                    "The explanation is unclear": "unclear_explanation",
                    "Other": "other"
                }
                success = save_issue_report(
                    report_type=type_map.get(report_type, "other"),
                    context=context,
                    user_answer=user_answer,
                    expected_answer=expected_answer,
                    user_comment=comment
                )
                if success:
                    st.success("Thank you! Your feedback helps improve the app.")
                    st.session_state[report_key] = False
                else:
                    st.error("Failed to save report. Please try again.")

        with col2:
            if st.button("Cancel", key=f"cancel_report_{key_prefix}"):
                st.session_state[report_key] = False
                st.rerun()


def render_grammar_card(card: dict):
    """Render a grammar review card."""
    # Initialize answer checked state for this card
    checked_key = f"grammar_checked_{st.session_state.review_index}"
    result_key = f"grammar_result_{st.session_state.review_index}"

    if checked_key not in st.session_state:
        st.session_state[checked_key] = False
        st.session_state[result_key] = None

    st.markdown(f"""
    <div class="card">
        <div class="exercise-prompt">{card['front']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Options
    options = card.get("options", [])
    correct = card.get("answer", "")

    st.markdown("Select your answer:")
    selected = st.radio(
        "Select your answer:",
        options,
        key=f"grammar_{st.session_state.review_index}",
        label_visibility="collapsed"
    )

    # Show Check button if not yet checked
    if not st.session_state[checked_key]:
        if st.button("Check", type="primary", key=f"check_grammar_{st.session_state.review_index}"):
            is_correct = selected == correct
            st.session_state[checked_key] = True
            st.session_state[result_key] = {
                "is_correct": is_correct,
                "selected": selected,
                "correct": correct
            }
            st.rerun()
    else:
        # Show result
        result = st.session_state[result_key]

        if result["is_correct"]:
            st.markdown("""
            <div class="feedback-box feedback-success">
                ✅ <strong>Correct!</strong>
            </div>
            """, unsafe_allow_html=True)
            record_progress({"grammar_reviewed": 1})
        else:
            st.markdown(f"""
            <div class="feedback-box feedback-info">
                <strong>Not quite.</strong> The correct answer is: <strong>{result['correct']}</strong>
            </div>
            """, unsafe_allow_html=True)

            # Show report issue option for wrong answers
            render_report_issue(
                context=card['front'],
                user_answer=result['selected'],
                expected_answer=result['correct'],
                key_prefix="grammar"
            )

        st.info(f"**Explanation:** {card.get('explanation', '')}")

        if st.button("Next →", type="primary", key=f"next_grammar_{st.session_state.review_index}"):
            # Clean up state for this card
            del st.session_state[checked_key]
            del st.session_state[result_key]
            advance_review()


def render_error_card(card: dict):
    """Render an error review card with tiered hints."""
    # Initialize hint level
    hint_key = f"error_hint_level_{st.session_state.review_index}"
    if hint_key not in st.session_state:
        st.session_state[hint_key] = 0

    hint_level = st.session_state[hint_key]
    correct = card.get("back", "")
    explanation = card.get('explanation', 'grammar error')

    st.markdown(f"""
    <div class="card" style="border-left: 4px solid var(--error);">
        <h3>{card['front']}</h3>
        <p style="color: var(--text-muted);">What's the correct form?</p>
    </div>
    """, unsafe_allow_html=True)

    # Tiered hints for error cards
    # Level 1: Error category (gender, preposition, etc.)
    # Level 2: Grammar rule hint
    # Level 3: First few letters of correction
    # Level 4: Full answer

    if hint_level >= 1:
        # Extract error type from explanation or tag
        error_type = card.get("item", {}).get("error_type", "grammar")
        st.markdown(f"""
        <div class="feedback-box feedback-info">
            <strong>Hint 1 (Error Type):</strong> This is a <em>{error_type}</em> error.
        </div>
        """, unsafe_allow_html=True)

    if hint_level >= 2:
        # Show grammar rule hint (first part of explanation)
        rule_hint = explanation.split(".")[0] if "." in explanation else explanation[:80]
        st.markdown(f"""
        <div class="feedback-box feedback-warning">
            <strong>Hint 2 (Rule):</strong> {rule_hint}...
        </div>
        """, unsafe_allow_html=True)

    if hint_level >= 3 and correct:
        # Show first few characters
        preview_len = min(len(correct) // 2, 8)
        preview = correct[:preview_len] if preview_len > 0 else correct[0]
        st.markdown(f"""
        <div class="feedback-box feedback-success">
            <strong>Hint 3 (Preview):</strong> The correct form starts with: "{preview}..."
        </div>
        """, unsafe_allow_html=True)

    # Hint buttons
    col1, col2 = st.columns([1, 2])

    with col1:
        if hint_level < 3:
            if st.button("💡 Get Hint", key=f"error_get_hint_{st.session_state.review_index}", use_container_width=True):
                st.session_state[hint_key] = hint_level + 1
                st.rerun()
        else:
            st.caption("All hints used")

    st.caption(f"Hints: {hint_level}/3")

    user_answer = st.text_input("Your correction:", key=f"error_{st.session_state.review_index}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check", type="primary", use_container_width=True):
            if not user_answer.strip():
                st.warning("Please enter your correction.")
            else:
                # Validate Spanish language first
                lang_info = detect_language(user_answer)

                if lang_info["language"] == "english":
                    st.markdown("""
                    <div class="feedback-box feedback-error">
                        🌐 <strong>Please write in Spanish!</strong> Your correction appears to be in English.
                        Use the hints if you need help.
                    </div>
                    """, unsafe_allow_html=True)
                elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                    st.markdown("""
                    <div class="feedback-box feedback-warning">
                        🔀 <strong>Mixed language detected.</strong> Try writing entirely in Spanish.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    item = card["item"]

                    # Get user profile for grading settings
                    profile = get_user_profile()
                    accent_tolerant = bool(profile.get("accent_tolerance", 0))
                    grading_mode = profile.get("grading_mode", "balanced")

                    # Use smart answer comparison with grading mode
                    is_correct, match_type = compare_answers(
                        user_answer, correct,
                        accent_tolerant=accent_tolerant,
                        grading_mode=grading_mode
                    )

                    # Also check for alternative correct forms (with →, /)
                    if not is_correct:
                        correct_normalized = correct.lower().strip()
                        user_normalized = user_answer.lower().strip()
                        if (user_normalized == correct_normalized.replace("→", "").strip() or
                            user_normalized == correct_normalized.split("/")[0].strip()):
                            is_correct = True
                            match_type = "alternative_form"

                    if is_correct:
                        st.markdown("""
                        <div class="feedback-box feedback-success">
                            ✅ <strong>Correct!</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        record_progress({"errors_fixed": 1})

                        # Update SRS for error
                        if item.get("id"):
                            update_mistake_review(item["id"], 4)
                    else:
                        # Check if it's an accent issue
                        accent_feedback = get_accent_feedback(user_answer, correct)

                        if accent_feedback and not accent_tolerant:
                            # Almost correct - just accents wrong
                            st.markdown(f"""
                            <div class="feedback-box feedback-warning">
                                <strong>Almost!</strong> {accent_feedback}
                                <br>The correct form is: <strong>{correct}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                            st.caption("Tip: Enable 'Accent Tolerance' in Settings if you can't type accents easily.")
                            # Give partial credit
                            if item.get("id"):
                                update_mistake_review(item["id"], 2)
                        else:
                            st.markdown(f"""
                            <div class="feedback-box feedback-info">
                                <strong>Not quite.</strong> The correct form is: <strong>{correct}</strong>
                            </div>
                            """, unsafe_allow_html=True)

                            if item.get("id"):
                                update_mistake_review(item["id"], 1)

                            # "Fix it now" micro-drill option
                            st.markdown("---")
                            col_fix, col_report = st.columns(2)
                            with col_fix:
                                if st.button("🔧 Fix It Now", key="fix_now", help="90-second micro-drill for this pattern"):
                                    # Store error pattern for micro-drill
                                    st.session_state.microdrill_pattern = {
                                        "pattern": card['front'],
                                        "correct": correct,
                                        "explanation": explanation,
                                        "error_type": item.get("error_type", "grammar")
                                    }
                                    st.session_state.microdrill_active = True
                                    st.rerun()
                            with col_report:
                                # Show report issue option
                                render_report_issue(
                                    context=card['front'],
                                    user_answer=user_answer,
                                    expected_answer=correct,
                                    key_prefix="error"
                                )

                    st.info(f"**Why?** {explanation}")

                    # Clean up hint state
                    if hint_key in st.session_state:
                        del st.session_state[hint_key]

    with col2:
        if st.button("Skip →", key="next_error", use_container_width=True):
            # Clean up hint state
            if hint_key in st.session_state:
                del st.session_state[hint_key]
            advance_review()


def advance_review():
    """Advance to the next review item."""
    st.session_state.review_index += 1
    st.session_state.review_revealed = False
    st.rerun()


def render_review_complete():
    """Render the review complete screen with achievements."""
    queue = st.session_state.review_queue
    vocab_count = sum(1 for q in queue if q["type"] == "vocab")
    grammar_count = sum(1 for q in queue if q["type"] == "grammar")
    error_count = sum(1 for q in queue if q["type"] == "error")
    total_items = len(queue)

    # Determine achievements earned
    achievements = []
    if total_items >= 20:
        achievements.append(("🏆", "Marathon Learner", "Reviewed 20+ items in one session"))
    elif total_items >= 10:
        achievements.append(("⭐", "Dedicated Student", "Reviewed 10+ items in one session"))

    if error_count >= 5:
        achievements.append(("🔧", "Error Crusher", "Tackled 5+ error corrections"))

    if vocab_count >= 10:
        achievements.append(("📚", "Vocab Champion", "Reviewed 10+ vocabulary items"))

    if grammar_count >= 5:
        achievements.append(("📝", "Grammar Guru", "Practiced 5+ grammar patterns"))

    if vocab_count > 0 and grammar_count > 0 and error_count > 0:
        achievements.append(("🌈", "Well-Rounded", "Practiced all three categories"))

    # Main completion card
    st.markdown(f"""
    <div class="card" style="text-align: center; padding: 2rem;
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 2px solid #10b981;">
        <h1 style="font-size: 4rem; margin-bottom: 0.5rem;">🎉</h1>
        <h2 style="color: #065f46; margin-bottom: 0.5rem;">Session Complete!</h2>
        <p style="color: #047857; font-size: 1.25rem; font-weight: 600;">
            You reviewed <strong>{total_items}</strong> items
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Session stats
    st.markdown("### Session Summary")

    cols = st.columns(3)

    with cols[0]:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem;">📚</div>
            <div class="metric-value">{vocab_count}</div>
            <div class="metric-label">Vocabulary</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem;">📝</div>
            <div class="metric-value">{grammar_count}</div>
            <div class="metric-label">Grammar</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem;">❌</div>
            <div class="metric-value">{error_count}</div>
            <div class="metric-label">Errors Fixed</div>
        </div>
        """, unsafe_allow_html=True)

    # Achievements section
    if achievements:
        st.markdown("### Achievements Earned")

        achievement_cols = st.columns(min(len(achievements), 3))
        for i, (icon, title, desc) in enumerate(achievements):
            with achievement_cols[i % 3]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;
                            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                            border-radius: 12px; border: 2px solid #f59e0b;
                            margin-bottom: 0.5rem;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="font-weight: 700; color: #92400e; font-size: 0.9rem;">{title}</div>
                    <div style="color: #a16207; font-size: 0.7rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # Encouragement based on performance
    st.markdown("---")
    if total_items >= 15:
        st.success("🌟 Outstanding effort! You're making excellent progress toward mastery.")
    elif total_items >= 8:
        st.info("💪 Great session! Consistent practice like this builds lasting fluency.")
    else:
        st.info("👍 Good start! Every review session strengthens your memory.")

    # Action buttons
    st.markdown("### What's Next?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Review Again", use_container_width=True):
            st.session_state.review_queue = []
            st.session_state.review_index = 0
            st.rerun()

    with col2:
        if st.button("🎤 Daily Mission", use_container_width=True):
            st.session_state.review_queue = []
            st.session_state.current_page = "Daily Missions"
            st.session_state.quick_session_mode = False
            st.rerun()

    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.review_queue = []
            st.session_state.current_page = "Home"
            st.session_state.quick_session_mode = False
            st.rerun()
