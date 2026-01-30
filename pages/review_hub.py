"""Two-Layer Spaced Repetition Review Hub page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    get_vocab_for_review, update_vocab_review,
    get_grammar_for_review, get_mistakes_for_review, update_mistake_review,
    record_progress
)
from utils.content import GRAMMAR_MICRODRILLS
from utils.helpers import get_review_priority


def render_review_hub_page():
    """Render the Two-Layer Spaced Repetition Review Hub page."""
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

    if index >= len(queue):
        render_review_complete()
        return

    current = queue[index]

    # Progress bar
    progress = (index) / len(queue)
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
    """Render a vocabulary review card."""
    st.markdown(f"""
    <div class="card" style="text-align: center; padding: 2rem;">
        <h2 style="font-size: 2rem; margin-bottom: 1rem;">{card['front']}</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.review_revealed:
        if st.button("Show Answer", type="primary", use_container_width=True):
            st.session_state.review_revealed = True
            st.rerun()
    else:
        # Show answer
        st.markdown(f"""
        <div class="card-muted" style="text-align: center; margin: 1rem 0;">
            <h3>{card['back']}</h3>
            <p><em>{card.get('example', '')}</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Rating buttons
        st.markdown("### How well did you know it?")

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
                    advance_review()


def render_grammar_card(card: dict):
    """Render a grammar review card."""
    st.markdown(f"""
    <div class="card">
        <h3>{card['front']}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Options
    options = card.get("options", [])
    selected = st.radio("Select your answer:", options, key=f"grammar_{st.session_state.review_index}")

    if st.button("Check", type="primary"):
        correct = card.get("answer", "")
        is_correct = selected == correct

        if is_correct:
            st.markdown("""
            <div class="feedback-box feedback-success">
                ✅ <strong>Correct!</strong>
            </div>
            """, unsafe_allow_html=True)
            record_progress({"grammar_reviewed": 1})
        else:
            st.markdown(f"""
            <div class="feedback-box feedback-error">
                ❌ The correct answer is: <strong>{correct}</strong>
            </div>
            """, unsafe_allow_html=True)

        st.info(f"**Explanation:** {card.get('explanation', '')}")

        if st.button("Next →", key="next_grammar"):
            advance_review()


def render_error_card(card: dict):
    """Render an error review card."""
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid var(--error);">
        <h3>{card['front']}</h3>
        <p style="color: var(--text-muted);">What's the correct form?</p>
    </div>
    """, unsafe_allow_html=True)

    user_answer = st.text_input("Your correction:", key=f"error_{st.session_state.review_index}")

    if st.button("Check", type="primary"):
        correct = card.get("back", "")
        item = card["item"]

        if user_answer.lower().strip() in correct.lower():
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
            st.markdown(f"""
            <div class="feedback-box feedback-error">
                ❌ The correct form is: <strong>{correct}</strong>
            </div>
            """, unsafe_allow_html=True)

            if item.get("id"):
                update_mistake_review(item["id"], 1)

        st.info(f"**Remember:** {card.get('explanation', '')}")

        if st.button("Next →", key="next_error"):
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
