"""Clean Review Hub - Spaced Repetition Review System."""
import streamlit as st
import random

from utils.theme import render_hero, render_section_header, render_feedback, render_html
from utils.database import (
    get_vocab_for_review, update_vocab_review,
    get_mistakes_for_review, update_mistake_review,
    record_progress, get_user_profile
)
from utils.content import GRAMMAR_MICRODRILLS
from utils.helpers import compare_answers, get_accent_feedback


def render_review_hub_page():
    """Render the Review Hub with clean, intuitive flow."""
    # Initialize session state
    if "review_queue" not in st.session_state:
        st.session_state.review_queue = []
    if "review_index" not in st.session_state:
        st.session_state.review_index = 0
    if "review_mode" not in st.session_state:
        st.session_state.review_mode = "mixed"

    # Show active review session or start screen
    if st.session_state.review_queue and st.session_state.review_index < len(st.session_state.review_queue):
        render_review_session()
    elif st.session_state.review_queue and st.session_state.review_index >= len(st.session_state.review_queue):
        render_review_complete()
    else:
        render_review_start()


def render_review_start():
    """Render the review start screen."""
    render_hero(
        title="Review Hub",
        subtitle="Practice vocabulary and grammar with spaced repetition."
    )

    # Get items due for review
    vocab_due = get_vocab_for_review()
    grammar_items = GRAMMAR_MICRODRILLS[:8]  # Available grammar items
    errors_due = get_mistakes_for_review()

    # Show what's available
    col1, col2, col3 = st.columns(3)

    with col1:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">📚</div>
                <div class="metric-value">{len(vocab_due)}</div>
                <div class="metric-label">Vocabulary</div>
            </div>
        """)

    with col2:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">📝</div>
                <div class="metric-value">{len(grammar_items)}</div>
                <div class="metric-label">Grammar</div>
            </div>
        """)

    with col3:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">🔧</div>
                <div class="metric-value">{len(errors_due)}</div>
                <div class="metric-label">Errors to Fix</div>
            </div>
        """)

    st.divider()

    # Review mode selection
    render_section_header("Choose Review Type")

    mode = st.radio(
        "What would you like to practice?",
        options=["mixed", "vocab", "grammar", "errors"],
        format_func=lambda x: {
            "mixed": "🔄 Mixed Review (Recommended)",
            "vocab": "📚 Vocabulary Only",
            "grammar": "📝 Grammar Only",
            "errors": "🔧 Error Corrections Only"
        }.get(x, x),
        horizontal=True,
        label_visibility="collapsed"
    )

    st.session_state.review_mode = mode

    # Session length
    st.markdown("### Session Length")
    session_length = st.slider(
        "Number of items:",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        label_visibility="collapsed"
    )

    # Start button
    st.markdown("")  # Spacing

    if st.button("Start Review →", type="primary", use_container_width=True):
        build_review_queue(session_length)
        st.rerun()


def build_review_queue(length: int):
    """Build the review queue based on selected mode."""
    mode = st.session_state.review_mode
    queue = []

    if mode in ["mixed", "vocab"]:
        vocab_items = get_vocab_for_review()
        count = length // 2 if mode == "mixed" else length
        for item in vocab_items[:count]:
            queue.append({
                "type": "vocab",
                "item": item,
                "term": item.get("term", ""),
                "meaning": item.get("meaning", ""),
                "example": item.get("example", ""),
            })

    if mode in ["mixed", "grammar"]:
        grammar_items = GRAMMAR_MICRODRILLS
        count = length // 2 if mode == "mixed" else length
        for item in grammar_items[:count]:
            queue.append({
                "type": "grammar",
                "item": item,
                "prompt": item.get("prompt", ""),
                "options": item.get("options", []),
                "answer": item.get("answer", ""),
                "explanation": item.get("explanation", ""),
            })

    if mode in ["mixed", "errors"]:
        error_items = get_mistakes_for_review()
        count = length // 3 if mode == "mixed" else length
        for item in error_items[:count]:
            queue.append({
                "type": "error",
                "item": item,
                "pattern": item.get("pattern", ""),
                "correction": item.get("corrected_text", ""),
                "explanation": item.get("explanation", ""),
            })

    # Shuffle for variety
    if mode == "mixed":
        random.shuffle(queue)

    st.session_state.review_queue = queue[:length]
    st.session_state.review_index = 0


def render_review_session():
    """Render the active review session."""
    queue = st.session_state.review_queue
    index = st.session_state.review_index
    current = queue[index]

    # Header with progress
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### Card {index + 1} of {len(queue)}")

    with col2:
        if st.button("✕ End Session", use_container_width=True):
            end_review_session()
            st.rerun()

    # Progress bar
    st.progress((index + 1) / len(queue))

    # Type badge
    type_config = {
        "vocab": ("📚 VOCABULARY", "primary"),
        "grammar": ("📝 GRAMMAR", "primary"),
        "error": ("🔧 ERROR FIX", "warning")
    }
    label, variant = type_config.get(current["type"], ("📋 ITEM", "muted"))

    render_html(f'<span class="pill pill-{variant}">{label}</span>')

    st.markdown("")  # Spacing

    # Render based on type
    if current["type"] == "vocab":
        render_vocab_exercise(current)
    elif current["type"] == "grammar":
        render_grammar_exercise(current)
    elif current["type"] == "error":
        render_error_exercise(current)


def render_vocab_exercise(card: dict):
    """Render a vocabulary flashcard exercise."""
    # State keys for this card
    revealed_key = f"vocab_revealed_{st.session_state.review_index}"

    if revealed_key not in st.session_state:
        st.session_state[revealed_key] = False

    # Show the term
    render_html(f"""
        <div class="card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1rem;">
                {card['term']}
            </div>
        </div>
    """)

    if not st.session_state[revealed_key]:
        # Not yet revealed - show reveal button
        if st.button("Show Answer", type="primary", use_container_width=True):
            st.session_state[revealed_key] = True
            st.rerun()
    else:
        # Show the answer
        render_html(f"""
            <div class="card-muted" style="text-align: center;">
                <div style="font-size: 1.25rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">
                    {card['meaning']}
                </div>
                <div style="color: var(--text-muted); font-style: italic;">
                    {card.get('example', '')}
                </div>
            </div>
        """)

        # Rating buttons
        st.markdown("### How well did you know it?")

        cols = st.columns(4)

        ratings = [
            ("Again", 1, "🔴"),
            ("Hard", 2, "🟠"),
            ("Good", 4, "🟢"),
            ("Easy", 5, "⭐")
        ]

        for col, (label, quality, emoji) in zip(cols, ratings):
            with col:
                if st.button(f"{emoji} {label}", use_container_width=True, key=f"rate_{quality}"):
                    # Update SRS
                    item = card["item"]
                    if item.get("term"):
                        update_vocab_review(item["term"], quality)
                    record_progress({"vocab_reviewed": 1})

                    # Clean up and advance
                    del st.session_state[revealed_key]
                    advance_to_next()


def render_grammar_exercise(card: dict):
    """Render a grammar multiple choice exercise."""
    # State keys
    checked_key = f"grammar_checked_{st.session_state.review_index}"
    result_key = f"grammar_result_{st.session_state.review_index}"
    selected_key = f"grammar_selected_{st.session_state.review_index}"

    if checked_key not in st.session_state:
        st.session_state[checked_key] = False
        st.session_state[result_key] = None

    # Show the prompt
    render_html(f"""
        <div class="exercise-prompt">
            {card['prompt']}
        </div>
    """)

    # Answer options
    options = card.get("options", [])
    correct = card.get("answer", "")

    if not st.session_state[checked_key]:
        # Show options as radio buttons
        selected = st.radio(
            "Select your answer:",
            options=options,
            key=selected_key,
            label_visibility="collapsed"
        )

        if st.button("Check Answer", type="primary", use_container_width=True):
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
            render_feedback("success", "✅ Correct!")
            record_progress({"grammar_reviewed": 1})
        else:
            render_feedback("error", f"❌ Not quite. The correct answer is: **{result['correct']}**")

        # Show explanation
        if card.get("explanation"):
            st.info(f"**Explanation:** {card['explanation']}")

        # Next button
        if st.button("Next →", type="primary", use_container_width=True):
            # Clean up state
            del st.session_state[checked_key]
            del st.session_state[result_key]
            if selected_key in st.session_state:
                del st.session_state[selected_key]
            advance_to_next()


def render_error_exercise(card: dict):
    """Render an error correction exercise."""
    # State keys
    checked_key = f"error_checked_{st.session_state.review_index}"
    result_key = f"error_result_{st.session_state.review_index}"

    if checked_key not in st.session_state:
        st.session_state[checked_key] = False
        st.session_state[result_key] = None

    # Show the error pattern
    render_html(f"""
        <div class="exercise-prompt">
            <strong>Fix this error:</strong><br>
            {card['pattern']}
        </div>
    """)

    correct = card.get("correction", "")

    if not st.session_state[checked_key]:
        # Input for correction
        user_input = st.text_input(
            "Your correction:",
            placeholder="Type the correct form...",
            key=f"error_input_{st.session_state.review_index}"
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("Check", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning("Please enter your correction.")
                else:
                    # Get user profile for grading settings
                    profile = get_user_profile()
                    accent_tolerant = bool(profile.get("accent_tolerance", 0))

                    is_correct, _ = compare_answers(
                        user_input, correct, accent_tolerant=accent_tolerant
                    )

                    st.session_state[checked_key] = True
                    st.session_state[result_key] = {
                        "is_correct": is_correct,
                        "user_answer": user_input,
                        "correct": correct
                    }
                    st.rerun()

        with col2:
            if st.button("Skip →", use_container_width=True):
                advance_to_next()
    else:
        # Show result
        result = st.session_state[result_key]

        if result["is_correct"]:
            render_feedback("success", "✅ Correct!")
            record_progress({"errors_fixed": 1})

            item = card["item"]
            if item.get("id"):
                update_mistake_review(item["id"], 4)
        else:
            render_feedback("error", f"❌ Not quite. The correct answer is: **{result['correct']}**")

            item = card["item"]
            if item.get("id"):
                update_mistake_review(item["id"], 1)

        # Show explanation
        if card.get("explanation"):
            st.info(f"**Why:** {card['explanation']}")

        # Next button
        if st.button("Next →", type="primary", use_container_width=True):
            del st.session_state[checked_key]
            del st.session_state[result_key]
            advance_to_next()


def advance_to_next():
    """Advance to the next review item."""
    st.session_state.review_index += 1
    st.rerun()


def end_review_session():
    """End the current review session."""
    st.session_state.review_queue = []
    st.session_state.review_index = 0


def render_review_complete():
    """Render the review completion screen."""
    queue = st.session_state.review_queue
    total = len(queue)

    # Count by type
    vocab_count = sum(1 for q in queue if q["type"] == "vocab")
    grammar_count = sum(1 for q in queue if q["type"] == "grammar")
    error_count = sum(1 for q in queue if q["type"] == "error")

    # Success message
    render_html(f"""
        <div class="card" style="text-align: center; padding: 2rem; background: rgba(34, 197, 94, 0.1); border-color: rgba(34, 197, 94, 0.3);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
                Session Complete!
            </div>
            <div style="color: var(--text-secondary);">
                You reviewed {total} items
            </div>
        </div>
    """)

    # Summary
    st.markdown("### Session Summary")

    cols = st.columns(3)

    with cols[0]:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">📚</div>
                <div class="metric-value">{vocab_count}</div>
                <div class="metric-label">Vocabulary</div>
            </div>
        """)

    with cols[1]:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">📝</div>
                <div class="metric-value">{grammar_count}</div>
                <div class="metric-label">Grammar</div>
            </div>
        """)

    with cols[2]:
        render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">🔧</div>
                <div class="metric-value">{error_count}</div>
                <div class="metric-label">Errors Fixed</div>
            </div>
        """)

    # Action buttons
    st.markdown("")  # Spacing

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Review Again", type="primary", use_container_width=True):
            end_review_session()
            st.rerun()

    with col2:
        if st.button("Back to Home", use_container_width=True):
            end_review_session()
            st.session_state.current_page = "Home"
            st.rerun()
