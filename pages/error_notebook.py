"""Personalized Error Notebook with Spaced Review page."""
import streamlit as st
from datetime import date, timedelta

from utils.theme import render_hero, render_section_header
from utils.database import (
    get_connection, get_mistakes_for_review, get_mistake_stats,
    update_mistake_review, record_progress, get_active_profile_id
)
from utils.helpers import format_time_ago, detect_language


def render_error_notebook_page():
    """Render the Error Notebook page."""
    render_hero(
        title="Error Notebook",
        subtitle="Your 'mistake memory' system. Track errors by category and review them with spaced repetition.",
        pills=["Error Tracking", "Trend Analysis", "Personal Drills"]
    )

    # Tabs for different views
    tabs = st.tabs(["📊 Dashboard", "📝 All Errors", "🎯 Practice Session"])

    with tabs[0]:
        render_error_dashboard()

    with tabs[1]:
        render_all_errors()

    with tabs[2]:
        render_error_practice()


def render_error_dashboard():
    """Render the error statistics dashboard."""
    render_section_header("Your Error Patterns")

    # Get stats
    stats = get_mistake_stats()

    if not stats:
        st.info("No errors tracked yet. Use the Mistake Catcher to log your errors!")
        return

    # Error type breakdown
    st.markdown("### Errors by Type")

    cols = st.columns(len(stats) if len(stats) <= 4 else 4)

    error_icons = {
        "preposition": "📍",
        "gender": "👤",
        "copula": "🔄",
        "calque": "🌐",
        "false_friend": "⚠️",
        "tense": "⏰",
        "agreement": "🔗",
        "unknown": "❓",
    }

    for i, (error_type, data) in enumerate(stats.items()):
        with cols[i % 4]:
            icon = error_icons.get(error_type, "❌")
            count = data.get("count", 0)
            avg_ease = data.get("avg_ease", 2.5)

            # Ease indicates difficulty: lower = harder
            difficulty = "Hard" if avg_ease < 2.0 else "Medium" if avg_ease < 2.8 else "Easy"
            diff_color = "error" if avg_ease < 2.0 else "warning" if avg_ease < 2.8 else "success"

            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">{icon}</div>
                <div class="metric-value">{count}</div>
                <div class="metric-label">{error_type.replace('_', ' ').title()}</div>
                <span class="pill pill-{diff_color}">{difficulty}</span>
            </div>
            """, unsafe_allow_html=True)

    # Top errors section
    st.markdown("### Your Top Recurring Errors")

    # Get top errors from database
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT pattern, error_type, explanation, COUNT(*) as occurrences
                FROM mistakes
                WHERE profile_id = ?
                GROUP BY pattern
                ORDER BY occurrences DESC
                LIMIT 5
            """, (profile_id,)).fetchall()
    except Exception as e:
        st.error(f"Could not load error patterns: {e}")
        rows = []

    if rows:
        for row in rows:
            st.markdown(f"""
            <div class="card" style="margin-bottom: 0.5rem; border-left: 4px solid #f59e0b;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{row['pattern']}</strong>
                    <span class="pill pill-muted">{row['occurrences']}x</span>
                </div>
                <p style="color: #64748b; margin-top: 0.25rem;">{row['explanation'] or row['error_type']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recurring patterns detected yet.")

    # Trend analysis
    st.markdown("### Error Trend (Last 30 Days)")

    # Simplified trend visualization
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM mistakes
                WHERE profile_id = ? AND created_at >= DATE('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (profile_id,)).fetchall()
    except Exception as e:
        st.error(f"Could not load error trends: {e}")
        rows = []

    if rows:
        dates = [row["date"] for row in rows]
        counts = [row["count"] for row in rows]

        # Simple bar representation
        max_count = max(counts) if counts else 1

        st.markdown("*Errors per day:*")
        for d, c in zip(dates[-7:], counts[-7:]):  # Last 7 days
            bar_width = int((c / max_count) * 100)
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span style="min-width: 80px; color: #64748b;">{d}</span>
                <div style="background: #6366f1; height: 20px; width: {bar_width}%; border-radius: 4px;"></div>
                <span>{c}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Not enough data for trend analysis yet.")


def render_all_errors():
    """Render all logged errors."""
    render_section_header("Error Log")

    # Filters
    col1, col2 = st.columns([1, 1])

    profile_id = get_active_profile_id()
    with col1:
        # Get unique error types
        try:
            with get_connection() as conn:
                types = conn.execute(
                    "SELECT DISTINCT error_type FROM mistakes WHERE profile_id = ?",
                    (profile_id,)
                ).fetchall()
                type_list = ["All"] + [t["error_type"] for t in types if t["error_type"]]
        except Exception:
            type_list = ["All"]

        filter_type = st.selectbox("Filter by type:", type_list)

    with col2:
        sort_by = st.selectbox("Sort by:", ["Most Recent", "Most Frequent", "Hardest (lowest ease)"])

    # Build query with profile filter
    query = "SELECT * FROM mistakes WHERE profile_id = ?"
    params = [profile_id]

    if filter_type != "All":
        query += " AND error_type = ?"
        params.append(filter_type)

    if sort_by == "Most Recent":
        query += " ORDER BY created_at DESC"
    elif sort_by == "Most Frequent":
        query += " ORDER BY review_count DESC"
    else:
        query += " ORDER BY ease_factor ASC"

    query += " LIMIT 50"

    try:
        with get_connection() as conn:
            errors = conn.execute(query, params).fetchall()
    except Exception:
        errors = []

    if not errors:
        st.info("No errors logged yet.")
        return

    # Display errors
    for error in errors:
        with st.expander(f"❌ {error['pattern'] or 'Error'} ({error['error_type']})", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Original:** {error['user_text']}")
                st.markdown(f"**Corrected:** {error['corrected_text']}")
                st.markdown(f"**Explanation:** {error['explanation']}")

                if error['examples']:
                    import json
                    try:
                        examples = json.loads(error['examples'])
                        st.markdown("**Examples:**")
                        for ex in examples[:2]:
                            st.markdown(f"- _{ex}_")
                    except (json.JSONDecodeError, TypeError):
                        pass

            with col2:
                st.markdown(f"**Type:** `{error['error_type']}`")
                st.markdown(f"**Reviews:** {error['review_count']}")
                st.markdown(f"**Ease:** {error['ease_factor']:.2f}")
                st.markdown(f"**Added:** {format_time_ago(error['created_at'][:10] if error['created_at'] else None)}")

                # Quick practice button
                if st.button("Practice", key=f"practice_{error['id']}"):
                    st.session_state.error_practice_id = error['id']
                    st.rerun()


def render_error_practice():
    """Render error-specific practice session."""
    render_section_header("Error Practice Session")

    # Get errors due for review
    errors = get_mistakes_for_review()

    if not errors:
        st.success("🎉 No errors due for review! Great job staying on top of your mistakes.")

        if st.button("Practice All Errors Anyway"):
            profile_id = get_active_profile_id()
            try:
                with get_connection() as conn:
                    errors = [dict(row) for row in conn.execute(
                        "SELECT * FROM mistakes WHERE profile_id = ? ORDER BY ease_factor ASC LIMIT 10",
                        (profile_id,)
                    ).fetchall()]
            except Exception:
                errors = []

        if not errors:
            st.info("Add some errors using the Mistake Catcher first!")
            return

    # Initialize session state
    if "error_practice_index" not in st.session_state:
        st.session_state.error_practice_index = 0
    if "error_practice_queue" not in st.session_state:
        st.session_state.error_practice_queue = errors

    queue = st.session_state.error_practice_queue
    index = st.session_state.error_practice_index

    if index >= len(queue):
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2rem;">
            <h2>🎉 Practice Complete!</h2>
            <p>You've reviewed all errors in the queue.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Over"):
            st.session_state.error_practice_index = 0
            st.rerun()
        return

    # Progress
    st.progress(index / len(queue))
    st.caption(f"Error {index + 1} of {len(queue)}")

    error = queue[index]

    # Error card
    st.markdown(f"""
    <div class="exercise-card">
        <div class="exercise-header">
            <span class="exercise-type">{error.get('error_type', 'Error').replace('_', ' ').upper()}</span>
        </div>
        <h3 style="margin: 1rem 0;">Fix this error:</h3>
        <div class="card-muted">
            <p style="font-size: 1.25rem;">{error.get('user_text', error.get('pattern', ''))}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User input
    user_correction = st.text_area(
        "Write the corrected version:",
        height=80,
        key=f"error_correction_{index}"
    )

    # Add hint button
    if st.button("💡 Hint in English", key=f"error_hint_{index}"):
        st.info(f"**Hint:** Fix the error in: '{error.get('user_text', error.get('pattern', ''))}'. The error type is: {error.get('error_type', 'grammar').replace('_', ' ')}")

    if st.button("Check", type="primary"):
        if not user_correction.strip():
            st.warning("Please write your correction.")
        else:
            # Validate Spanish language first
            lang_info = detect_language(user_correction)

            if lang_info["language"] == "english":
                st.markdown("""
                <div class="feedback-box feedback-error">
                    🌐 <strong>Please write in Spanish!</strong> Your correction appears to be in English.
                    Use the "Hint in English" button if you need help.
                </div>
                """, unsafe_allow_html=True)
            elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                st.markdown("""
                <div class="feedback-box feedback-warning">
                    🔀 <strong>Mixed language detected.</strong> Try writing entirely in Spanish.
                </div>
                """, unsafe_allow_html=True)
            else:
                correct = error.get('corrected_text', '')
                is_correct = user_correction.lower().strip() in correct.lower() or \
                             correct.lower() in user_correction.lower().strip()

                if is_correct:
                    st.markdown("""
                    <div class="feedback-box feedback-success">
                        ✅ <strong>Correct!</strong> You remembered this one.
                    </div>
                    """, unsafe_allow_html=True)

                    # Update SRS with good rating
                    if error.get('id'):
                        update_mistake_review(error['id'], 4)
                    record_progress({"errors_fixed": 1})
                else:
                    st.markdown(f"""
                    <div class="feedback-box feedback-error">
                        ❌ <strong>Not quite.</strong><br>
                        Correct: <strong>{correct}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    # Update SRS with poor rating
                    if error.get('id'):
                        update_mistake_review(error['id'], 1)

                st.info(f"**Remember:** {error.get('explanation', 'Review this pattern.')}")

                # Examples
                if error.get('examples'):
                    import json
                    try:
                        examples = json.loads(error['examples'])
                        st.markdown("**Examples:**")
                        for ex in examples[:2]:
                            st.markdown(f"- _{ex}_")
                    except (json.JSONDecodeError, TypeError):
                        pass

    if st.button("Next Error →"):
        st.session_state.error_practice_index += 1
        st.rerun()
