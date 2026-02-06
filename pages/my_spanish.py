"""My Spanish - Personal phrasebook with auto-saved phrases and searchable content."""
import streamlit as st
from datetime import datetime, date

from utils.theme import render_hero, render_section_header
from utils.database import get_user_profile, init_db


def get_phrasebook_items(filter_type: str = None, search: str = None, limit: int = 50) -> list:
    """Get phrasebook items with optional filtering."""
    from utils.database import get_connection, get_active_profile_id

    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            # Ensure table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS phrasebook (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    phrase TEXT NOT NULL,
                    translation TEXT,
                    context TEXT,
                    category TEXT DEFAULT 'general',
                    source TEXT DEFAULT 'practice',
                    difficulty TEXT DEFAULT 'intermediate',
                    practice_count INTEGER DEFAULT 0,
                    last_practiced TEXT,
                    starred INTEGER DEFAULT 0,
                    needs_review INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(profile_id, phrase)
                )
            """)
            conn.commit()

            query = """
                SELECT * FROM phrasebook
                WHERE profile_id = ?
            """
            params = [profile_id]

            if filter_type == "starred":
                query += " AND starred = 1"
            elif filter_type == "needs_review":
                query += " AND needs_review = 1"
            elif filter_type and filter_type not in ["all", "starred", "needs_review"]:
                query += " AND category = ?"
                params.append(filter_type)

            if search:
                query += " AND (phrase LIKE ? OR translation LIKE ? OR context LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])

            query += " ORDER BY starred DESC, last_practiced DESC LIMIT ?"
            params.append(limit)

            return [dict(row) for row in conn.execute(query, params).fetchall()]
    except Exception as e:
        print(f"Error getting phrasebook: {e}")
        return []


def save_phrase(phrase: str, translation: str = "", context: str = "",
                category: str = "general", source: str = "manual") -> bool:
    """Save a phrase to the phrasebook."""
    from utils.database import get_connection, get_active_profile_id

    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO phrasebook
                (profile_id, phrase, translation, context, category, source, last_practiced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (profile_id, phrase, translation, context, category, source, datetime.now().isoformat()))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving phrase: {e}")
        return False


def toggle_star(phrase_id: int) -> bool:
    """Toggle starred status for a phrase."""
    from utils.database import get_connection

    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE phrasebook SET starred = NOT starred WHERE id = ?
            """, (phrase_id,))
            conn.commit()
            return True
    except Exception:
        return False


def get_phrasebook_stats() -> dict:
    """Get stats about the phrasebook."""
    from utils.database import get_connection, get_active_profile_id

    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(starred) as starred,
                    SUM(needs_review) as needs_review,
                    COUNT(DISTINCT category) as categories
                FROM phrasebook WHERE profile_id = ?
            """, (profile_id,)).fetchone()
            return dict(row) if row else {"total": 0, "starred": 0, "needs_review": 0, "categories": 0}
    except Exception:
        return {"total": 0, "starred": 0, "needs_review": 0, "categories": 0}


def render_my_spanish_page():
    """Render the My Spanish personal phrasebook page."""
    render_hero(
        title="My Spanish",
        subtitle="Your personal phrasebook - phrases practiced, mistakes made, and expressions saved.",
        pills=["Phrases", "Mistakes", "Starred", "Search"]
    )

    stats = get_phrasebook_stats()

    # Quick stats bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Phrases", stats.get("total", 0))
    with col2:
        st.metric("Starred", stats.get("starred", 0))
    with col3:
        st.metric("Needs Review", stats.get("needs_review", 0))
    with col4:
        st.metric("Categories", stats.get("categories", 0))

    st.divider()

    # Filter and search bar
    col1, col2 = st.columns([2, 1])

    with col1:
        search = st.text_input("Search phrases...", placeholder="Type to search", key="phrase_search")

    with col2:
        filter_type = st.selectbox(
            "Filter by:",
            ["all", "starred", "needs_review", "travel", "work", "social", "grammar", "mistakes"],
            format_func=lambda x: {
                "all": "All Phrases",
                "starred": "Starred",
                "needs_review": "Needs Review",
                "travel": "Travel",
                "work": "Work",
                "social": "Social",
                "grammar": "Grammar",
                "mistakes": "From Mistakes"
            }.get(x, x.title())
        )

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Phrasebook", "Add New", "Import from Practice"])

    with tab1:
        render_phrasebook_list(filter_type if filter_type != "all" else None, search)

    with tab2:
        render_add_phrase_form()

    with tab3:
        render_import_from_practice()


def render_phrasebook_list(filter_type: str = None, search: str = None):
    """Render the list of saved phrases."""
    items = get_phrasebook_items(filter_type=filter_type, search=search)

    if not items:
        st.markdown("""
        <div class="card-muted" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
            <strong>No phrases yet</strong>
            <p style="color: #8E8E93;">
                Phrases you practice will automatically appear here.
                You can also add phrases manually.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.caption(f"Showing {len(items)} phrases")

    for item in items:
        col1, col2, col3 = st.columns([0.5, 4, 0.5])

        with col1:
            star_icon = "⭐" if item.get("starred") else "☆"
            if st.button(star_icon, key=f"star_{item['id']}", help="Toggle star"):
                toggle_star(item['id'])
                st.rerun()

        with col2:
            phrase = item.get("phrase", "")
            translation = item.get("translation", "")
            context = item.get("context", "")
            category = item.get("category", "general")

            # Category badge color
            cat_colors = {
                "travel": "success",
                "work": "primary",
                "social": "warning",
                "grammar": "secondary",
                "mistakes": "error"
            }
            cat_color = cat_colors.get(category, "muted")

            st.markdown(f"""
            <div class="card" style="padding: 1rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="font-size: 1.1rem;">{phrase}</strong>
                        <p style="color: #8E8E93; margin: 0.25rem 0;">{translation}</p>
                    </div>
                    <span class="pill pill-{cat_color}" style="font-size: 0.7rem;">{category}</span>
                </div>
                {f'<p style="font-size: 0.85rem; color: #8E8E93; margin-top: 0.5rem; font-style: italic;">{context}</p>' if context else ''}
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if item.get("needs_review"):
                st.markdown("🔄", help="Needs review")


def render_add_phrase_form():
    """Render form to add a new phrase manually."""
    render_section_header("Add a New Phrase")

    col1, col2 = st.columns(2)

    with col1:
        phrase = st.text_input("Spanish phrase", placeholder="e.g., Echar de menos")
        context = st.text_area("Context or example", placeholder="e.g., Te echo de menos mucho.", height=100)

    with col2:
        translation = st.text_input("English meaning", placeholder="e.g., To miss (someone)")
        category = st.selectbox("Category", ["general", "travel", "work", "social", "grammar", "idioms"])

    if st.button("Save Phrase", type="primary", use_container_width=True):
        if phrase.strip():
            success = save_phrase(
                phrase=phrase.strip(),
                translation=translation.strip(),
                context=context.strip(),
                category=category,
                source="manual"
            )
            if success:
                st.success(f"Saved: {phrase}")
                st.rerun()
            else:
                st.error("Failed to save phrase")
        else:
            st.warning("Please enter a phrase")


def render_import_from_practice():
    """Render section to import phrases from practice history."""
    render_section_header("Import from Your Practice")

    st.markdown("""
    <div class="card-muted">
        <strong>Auto-import phrases you've practiced</strong>
        <p>Pull in vocabulary and expressions from your learning history.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Import Vocabulary", use_container_width=True):
            import_from_vocabulary()

    with col2:
        if st.button("Import from Mistakes", use_container_width=True):
            import_from_mistakes()


def import_from_vocabulary():
    """Import recent vocabulary items to phrasebook."""
    from utils.database import get_vocab_items

    items = get_vocab_items()
    imported = 0

    for item in items[:30]:  # Limit to 30 most recent
        term = item.get("term", "")
        meaning = item.get("meaning", "")
        example = item.get("example", "")

        if term:
            success = save_phrase(
                phrase=term,
                translation=meaning,
                context=example,
                category="general",
                source="vocabulary"
            )
            if success:
                imported += 1

    if imported > 0:
        st.success(f"Imported {imported} phrases from vocabulary")
    else:
        st.info("No new phrases to import")


def import_from_mistakes():
    """Import corrected forms from mistake history."""
    from utils.database import get_connection, get_active_profile_id

    profile_id = get_active_profile_id()
    imported = 0

    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT corrected_text, explanation, error_type
                FROM mistakes WHERE profile_id = ? LIMIT 20
            """, (profile_id,)).fetchall()

            for row in rows:
                corrected = row["corrected_text"]
                explanation = row["explanation"] or ""
                error_type = row["error_type"] or "grammar"

                if corrected:
                    success = save_phrase(
                        phrase=corrected,
                        translation="",
                        context=explanation[:200],
                        category="mistakes",
                        source="mistake_correction"
                    )
                    if success:
                        imported += 1
    except Exception as e:
        print(f"Error importing mistakes: {e}")

    if imported > 0:
        st.success(f"Imported {imported} corrections from mistakes")
    else:
        st.info("No new corrections to import")
