"""Error Fingerprint Dashboard - Personal learning analytics and syllabus."""
import streamlit as st
from datetime import date, timedelta

from utils.theme import render_hero, render_section_header
from utils.database import (
    get_error_fingerprints,
    get_fingerprint_summary,
    generate_personal_syllabus,
    get_active_syllabus,
    init_fingerprint_tables,
    ERROR_TAXONOMY,
    get_connection,
    get_active_profile_id,
)


def render_fingerprint_dashboard():
    """Render the error fingerprint dashboard."""
    render_hero(
        title="Your Learning Fingerprint",
        subtitle="Track your error patterns and focus on what matters most. Your personalized syllabus updates based on your mistakes.",
        pills=["Analytics", "Patterns", "Syllabus", "Progress"]
    )

    # Initialize fingerprint tables if needed
    init_fingerprint_tables()

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Error Patterns",
        "Personal Syllabus",
        "Near-Miss Gallery"
    ])

    with tab1:
        render_overview()

    with tab2:
        render_error_patterns()

    with tab3:
        render_personal_syllabus()

    with tab4:
        render_near_miss_gallery()


def render_overview():
    """Render the overview dashboard."""
    render_section_header("Your Error Profile")

    summary = get_fingerprint_summary()

    if not summary:
        st.info("Start practicing to build your error profile. Your patterns will appear here as you learn.")
        st.markdown("""
        **How it works:**
        1. Practice in any module (Mistake Catcher, Verb Studio, Grammar Drills)
        2. Your errors are automatically categorized
        3. High-priority patterns become your focus for the next week
        """)
        return

    # Display summary cards
    cols = st.columns(len(summary))

    category_icons = {
        "verb_tense": "Tense",
        "ser_estar": "Ser/Estar",
        "prepositions": "Prepositions",
        "pronouns": "Pronouns",
        "agreement": "Agreement",
        "vocabulary": "Vocabulary",
        "word_order": "Word Order",
    }

    for col, (category, data) in zip(cols, summary.items()):
        with col:
            total = data.get("total_errors", 0) + data.get("total_correct", 0)
            confidence = data.get("avg_confidence", 0.5)
            errors = data.get("total_errors", 0)

            # Color based on confidence
            if confidence >= 0.8:
                color = "#22c55e"  # green
                status = "Strong"
            elif confidence >= 0.5:
                color = "#f59e0b"  # amber
                status = "Developing"
            else:
                color = "#ef4444"  # red
                status = "Focus Area"

            st.markdown(f"""
            <div class="card" style="text-align: center; border-left: 4px solid {color};">
                <div style="font-size: 0.875rem; color: #8E8E93;">
                    {category_icons.get(category, category.replace('_', ' ').title())}
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {color};">
                    {int(confidence * 100)}%
                </div>
                <div style="font-size: 0.75rem; color: #8E8E93;">
                    {errors} errors / {total} attempts
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="pill pill-{'primary' if status == 'Strong' else 'warning' if status == 'Developing' else 'error'}">
                        {status}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Trend section
    st.divider()
    render_section_header("Focus Recommendation")

    # Get highest priority fingerprints
    fingerprints = get_error_fingerprints(limit=3)

    if fingerprints:
        st.markdown("Based on your recent practice, focus on these areas:")

        for i, fp in enumerate(fingerprints, 1):
            category = fp.get("category", "")
            subcategory = fp.get("subcategory", "")
            description = ERROR_TAXONOMY.get(category, {}).get(subcategory, subcategory.replace("_", " ").title())
            priority = fp.get("priority_score", 0)
            errors = fp.get("error_count", 0)
            correct = fp.get("correct_count", 0)

            with st.expander(f"**#{i} {description}** ({errors} errors)", expanded=i==1):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Category:** {category.replace('_', ' ').title()}")
                    st.markdown(f"**Pattern:** {subcategory.replace('_', ' ')}")
                    st.progress(correct / (errors + correct) if (errors + correct) > 0 else 0)
                    st.caption(f"{correct} correct / {errors + correct} total")

                with col2:
                    st.metric("Priority", f"{priority:.1f}")
    else:
        st.info("Keep practicing to get personalized recommendations.")


def render_error_patterns():
    """Render detailed error pattern analysis."""
    render_section_header("Error Pattern Breakdown")

    # Category filter
    categories = list(ERROR_TAXONOMY.keys())
    selected_category = st.selectbox(
        "Filter by category:",
        ["All Categories"] + [c.replace("_", " ").title() for c in categories]
    )

    fingerprints = get_error_fingerprints(limit=50)

    if not fingerprints:
        st.info("No error patterns recorded yet. Practice to see your patterns here.")
        return

    # Filter if category selected
    if selected_category != "All Categories":
        category_key = selected_category.lower().replace(" ", "_")
        fingerprints = [fp for fp in fingerprints if fp.get("category") == category_key]

    # Group by category
    by_category = {}
    for fp in fingerprints:
        cat = fp.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(fp)

    for category, items in by_category.items():
        st.markdown(f"### {category.replace('_', ' ').title()}")

        for item in items:
            subcategory = item.get("subcategory", "")
            description = ERROR_TAXONOMY.get(category, {}).get(subcategory, subcategory)
            errors = item.get("error_count", 0)
            correct = item.get("correct_count", 0)
            confidence = item.get("confidence", 0.5)
            last_error = item.get("last_error", "Never")

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{description}**")
                st.progress(confidence)

            with col2:
                st.metric("Errors", errors)

            with col3:
                st.metric("Correct", correct)

        st.divider()


def render_personal_syllabus():
    """Render the personal learning syllabus."""
    render_section_header("Your Personal Syllabus")

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("Regenerate Syllabus", type="primary"):
            generate_personal_syllabus()
            st.rerun()

    syllabus = get_active_syllabus()

    if not syllabus:
        st.info("No syllabus generated yet. Click 'Regenerate Syllabus' to create one based on your error patterns.")

        # Show what's needed
        fingerprints = get_error_fingerprints(limit=5)
        if not fingerprints:
            st.warning("You need to practice more to generate a personalized syllabus. Try the Mistake Catcher or Grammar Drills first.")
        else:
            if st.button("Generate My First Syllabus"):
                generate_personal_syllabus()
                st.rerun()
        return

    # Display syllabus items
    st.markdown("**Your focus areas for the next 7-14 days:**")

    for item in syllabus:
        rank = item.get("priority_rank", 0)
        category = item.get("category", "")
        subcategory = item.get("subcategory", "")
        description = ERROR_TAXONOMY.get(category, {}).get(subcategory, subcategory)
        target = item.get("target_practice_count", 5)
        actual = item.get("actual_practice_count", 0)
        confidence = item.get("confidence", 0.5)

        # Progress toward target
        progress = min(actual / target, 1.0) if target > 0 else 0

        with st.container():
            st.markdown(f"""
            <div class="card" style="border-left: 4px solid {'#22c55e' if progress >= 1 else '#007AFF'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="pill pill-primary">#{rank}</span>
                        <strong style="margin-left: 0.5rem;">{description}</strong>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #8E8E93;">{actual}/{target} practices</span>
                    </div>
                </div>
                <div style="margin-top: 0.75rem;">
                    <div style="background: #F2F2F7; border-radius: 4px; height: 8px; overflow: hidden;">
                        <div style="background: {'#22c55e' if progress >= 1 else '#007AFF'}; width: {progress * 100}%; height: 100%;"></div>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #8E8E93;">
                    Category: {category.replace('_', ' ').title()} | Current confidence: {int(confidence * 100)}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")

    # Practice recommendations
    st.divider()
    render_section_header("Practice Recommendations")

    st.markdown("""
    To improve your syllabus focus areas:

    - **Mistake Catcher** - Check your writing for these specific patterns
    - **Grammar Drills** - Practice the underlying rules
    - **Verb Studio** - For verb tense and conjugation issues
    - **Context Units** - See patterns used correctly in context
    """)


def render_near_miss_gallery():
    """Render gallery of near-miss examples."""
    render_section_header("Near-Miss Gallery")

    st.markdown("""
    These are cases where you almost got it right. Understanding these edge cases
    will help you avoid similar mistakes.
    """)

    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            near_misses = conn.execute("""
                SELECT nm.*, ef.category, ef.subcategory
                FROM near_misses nm
                JOIN error_fingerprints ef ON nm.fingerprint_id = ef.id
                WHERE nm.profile_id = ?
                ORDER BY nm.created_at DESC
                LIMIT 20
            """, (profile_id,)).fetchall()
            near_misses = [dict(row) for row in near_misses]
    except Exception:
        near_misses = []

    if not near_misses:
        st.info("No near-misses recorded yet. As you practice, your almost-correct attempts will appear here with explanations.")
        return

    # Filter by category
    categories = list(set(nm.get("category", "") for nm in near_misses))
    selected = st.selectbox(
        "Filter by error type:",
        ["All"] + [c.replace("_", " ").title() for c in categories if c]
    )

    for nm in near_misses:
        category = nm.get("category", "")

        # Apply filter
        if selected != "All" and category.replace("_", " ").title() != selected:
            continue

        subcategory = nm.get("subcategory", "")
        user_input = nm.get("user_input", "")
        expected = nm.get("expected", "")
        rule = nm.get("rule_explanation", "")
        contrast = nm.get("contrast_example", "")
        description = ERROR_TAXONOMY.get(category, {}).get(subcategory, subcategory)

        with st.expander(f"{description}: \"{user_input[:50]}...\"" if len(user_input) > 50 else f"{description}: \"{user_input}\""):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**What you wrote:**")
                st.markdown(f"<div class='feedback-box feedback-error'>{user_input}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("**Expected:**")
                st.markdown(f"<div class='feedback-box feedback-success'>{expected}</div>", unsafe_allow_html=True)

            if rule:
                st.markdown("**Rule:**")
                st.info(rule)

            if contrast:
                st.markdown("**Contrast example:**")
                st.caption(contrast)
