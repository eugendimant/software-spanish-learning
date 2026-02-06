"""Memory Palace - Interactive vocabulary scenes for memorable learning."""
import streamlit as st
import random
import json
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    get_vocab_items, save_vocab_item, record_progress, log_activity,
    get_connection, get_active_profile_id
)
from utils.helpers import seed_for_day


# Pre-defined palace locations
PALACE_LOCATIONS = {
    "home": {
        "name": "Your Home",
        "icon": "🏠",
        "rooms": [
            {"id": "entrance", "name": "Entrance Hall", "description": "The first thing you see when you walk in"},
            {"id": "living", "name": "Living Room", "description": "Cozy space with a sofa and TV"},
            {"id": "kitchen", "name": "Kitchen", "description": "Where you cook and eat"},
            {"id": "bedroom", "name": "Bedroom", "description": "Your restful sleeping space"},
            {"id": "bathroom", "name": "Bathroom", "description": "Tiles, mirror, and running water"},
        ]
    },
    "office": {
        "name": "Office Building",
        "icon": "🏢",
        "rooms": [
            {"id": "lobby", "name": "Lobby", "description": "Reception area with plants"},
            {"id": "elevator", "name": "Elevator", "description": "Small space with buttons"},
            {"id": "desk", "name": "Your Desk", "description": "Computer, papers, coffee mug"},
            {"id": "meeting", "name": "Meeting Room", "description": "Table, whiteboard, chairs"},
            {"id": "cafeteria", "name": "Cafeteria", "description": "Food, drinks, chatter"},
        ]
    },
    "city": {
        "name": "City Walk",
        "icon": "🌆",
        "rooms": [
            {"id": "plaza", "name": "Central Plaza", "description": "Fountain, benches, pigeons"},
            {"id": "cafe", "name": "Corner Café", "description": "Smell of coffee, outdoor tables"},
            {"id": "market", "name": "Market", "description": "Stalls with fruits and vegetables"},
            {"id": "park", "name": "City Park", "description": "Trees, paths, children playing"},
            {"id": "station", "name": "Train Station", "description": "Platforms, announcements, travelers"},
        ]
    },
    "beach": {
        "name": "Beach Day",
        "icon": "🏖️",
        "rooms": [
            {"id": "parking", "name": "Parking Lot", "description": "Hot asphalt, car trunks opening"},
            {"id": "boardwalk", "name": "Boardwalk", "description": "Wooden planks, ice cream stands"},
            {"id": "sand", "name": "Sandy Beach", "description": "Warm sand between toes"},
            {"id": "water", "name": "Water's Edge", "description": "Waves touching your feet"},
            {"id": "sunset", "name": "Sunset Spot", "description": "Golden light, calm water"},
        ]
    },
}

# Visualization prompts for creating mental images
VISUALIZATION_PROMPTS = [
    "Imagine the word written in giant glowing letters",
    "Picture an object representing this word in an unusual color",
    "See someone famous using this word dramatically",
    "Visualize this word causing an explosion of the meaning",
    "Imagine touching something that represents this word",
    "Hear the word being sung loudly in this location",
    "Picture this word on a huge billboard in this spot",
]


def render_memory_palace_page():
    """Render the Memory Palace page."""
    render_hero(
        title="Memory Palace",
        subtitle="Place vocabulary in memorable locations. Create vivid mental images to supercharge recall.",
        pills=["Spatial Memory", "Visualization", "Scenes", "Recall"]
    )

    # Initialize session state
    if "mp_palace" not in st.session_state:
        st.session_state.mp_palace = None
    if "mp_placements" not in st.session_state:
        st.session_state.mp_placements = {}
    if "mp_mode" not in st.session_state:
        st.session_state.mp_mode = "build"

    # Mode selection
    render_section_header("Palace Mode")

    mode = st.radio(
        "What would you like to do?",
        ["Build Palace", "Walk Through", "Recall Test", "My Palaces"],
        horizontal=True
    )

    st.divider()

    if mode == "Build Palace":
        render_build_palace()
    elif mode == "Walk Through":
        render_walk_through()
    elif mode == "Recall Test":
        render_recall_test()
    else:
        render_my_palaces()


def render_build_palace():
    """Render palace building interface."""
    render_section_header("Build Your Memory Palace")

    st.markdown("""
    Place vocabulary words in locations within your palace. Each location
    should have a vivid mental image connecting the word to the place.
    """)

    # Palace selection
    palace_options = list(PALACE_LOCATIONS.keys())
    selected_palace = st.selectbox(
        "Choose your palace setting:",
        palace_options,
        format_func=lambda x: f"{PALACE_LOCATIONS[x]['icon']} {PALACE_LOCATIONS[x]['name']}"
    )

    palace_data = PALACE_LOCATIONS[selected_palace]
    st.session_state.mp_palace = selected_palace

    # Show palace layout
    st.markdown(f"### {palace_data['icon']} {palace_data['name']}")

    # Get vocabulary items to place
    vocab_items = get_vocab_items()

    if not vocab_items:
        st.info("No vocabulary items to place yet. Learn some words first in Topic Diversity or Context Units.")
        return

    # Room selection and placement
    for room in palace_data["rooms"]:
        with st.expander(f"**{room['name']}** - {room['description']}", expanded=False):
            # Current placement
            placement_key = f"{selected_palace}_{room['id']}"
            current = st.session_state.mp_placements.get(placement_key, {})

            if current.get("term"):
                st.markdown(f"""
                <div class="card" style="background: rgba(99, 102, 241, 0.1);">
                    <strong>Currently placed:</strong> {current['term']}<br>
                    <em>Meaning:</em> {current.get('meaning', '')}
                </div>
                """, unsafe_allow_html=True)

            # Word selection
            available_terms = [v.get("term", "") for v in vocab_items if v.get("term")]
            selected_term = st.selectbox(
                f"Place a word here:",
                ["(none)"] + available_terms,
                key=f"place_{room['id']}"
            )

            if selected_term != "(none)":
                # Find the vocabulary item
                vocab = next((v for v in vocab_items if v.get("term") == selected_term), None)

                if vocab:
                    # Visualization prompt
                    seed = seed_for_day(date.today(), room['id'])
                    random.seed(seed)
                    prompt = random.choice(VISUALIZATION_PROMPTS)

                    st.info(f"**Visualization tip:** {prompt}")

                    # Custom visualization input
                    visualization = st.text_input(
                        "Describe your mental image:",
                        placeholder="e.g., A giant 'palabra' sign crashing through the door...",
                        key=f"viz_{room['id']}"
                    )

                    if st.button("Place Word", key=f"place_btn_{room['id']}", type="primary"):
                        st.session_state.mp_placements[placement_key] = {
                            "term": vocab.get("term"),
                            "meaning": vocab.get("meaning", ""),
                            "visualization": visualization,
                            "room": room["name"]
                        }
                        save_palace_placement(selected_palace, room['id'], vocab, visualization)
                        st.success(f"Placed '{selected_term}' in {room['name']}!")
                        record_progress({"vocab_reviewed": 1})

    # Summary
    st.divider()
    st.markdown("### Palace Summary")

    placed_count = sum(1 for k, v in st.session_state.mp_placements.items()
                      if k.startswith(selected_palace) and v.get("term"))

    st.markdown(f"**Words placed:** {placed_count} / {len(palace_data['rooms'])}")

    if placed_count == len(palace_data["rooms"]):
        st.success("Your palace is complete! Try the Walk Through mode to review.")


def render_walk_through():
    """Render palace walkthrough for review."""
    render_section_header("Walk Through Your Palace")

    st.markdown("""
    Take a mental journey through your palace. At each location, try to recall
    the word before revealing it. This strengthens spatial-semantic connections.
    """)

    # Load saved palaces
    placements = load_palace_placements()

    if not placements:
        st.info("No palaces built yet. Go to 'Build Palace' mode to create one.")
        return

    # Group by palace
    palaces_used = set(p.get("palace", "") for p in placements)

    selected_palace = st.selectbox(
        "Choose palace to walk through:",
        list(palaces_used),
        format_func=lambda x: f"{PALACE_LOCATIONS.get(x, {}).get('icon', '🏛️')} {PALACE_LOCATIONS.get(x, {}).get('name', x)}"
    )

    palace_placements = [p for p in placements if p.get("palace") == selected_palace]
    palace_data = PALACE_LOCATIONS.get(selected_palace, {})

    st.markdown(f"### Journey through {palace_data.get('name', selected_palace)}")

    for i, room in enumerate(palace_data.get("rooms", [])):
        placement = next((p for p in palace_placements if p.get("room_id") == room["id"]), None)

        st.markdown(f"**Stop {i+1}: {room['name']}**")
        st.caption(room["description"])

        if placement:
            # Hidden word with reveal
            if f"reveal_{room['id']}" not in st.session_state:
                st.session_state[f"reveal_{room['id']}"] = False

            if st.session_state[f"reveal_{room['id']}"]:
                st.markdown(f"""
                <div class="card" style="border-left: 4px solid #007AFF;">
                    <strong>{placement.get('term', '')}</strong>: {placement.get('meaning', '')}
                    <br><br>
                    <em>Your visualization:</em> {placement.get('visualization', 'None recorded')}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Recall challenge
                user_recall = st.text_input(
                    "What word is here?",
                    placeholder="Type the word you placed here...",
                    key=f"recall_{room['id']}"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Check", key=f"check_{room['id']}"):
                        if user_recall.lower().strip() == placement.get("term", "").lower():
                            st.success("Correct!")
                            record_progress({"vocab_reviewed": 1})
                        else:
                            st.error(f"Not quite. The word is: {placement.get('term', '')}")
                        st.session_state[f"reveal_{room['id']}"] = True

                with col2:
                    if st.button("Reveal", key=f"reveal_btn_{room['id']}"):
                        st.session_state[f"reveal_{room['id']}"] = True
                        st.rerun()
        else:
            st.caption("(No word placed here yet)")

        st.markdown("---")


def render_recall_test():
    """Render timed recall test."""
    render_section_header("Recall Test")

    st.markdown("""
    Test your memory! You'll be shown locations and need to recall
    which words are placed there. Speed and accuracy both count.
    """)

    placements = load_palace_placements()

    if not placements or len(placements) < 3:
        st.info("You need at least 3 words placed in palaces to take a test.")
        return

    # Initialize test state
    if "test_questions" not in st.session_state:
        st.session_state.test_questions = None
    if "test_score" not in st.session_state:
        st.session_state.test_score = 0
    if "test_current" not in st.session_state:
        st.session_state.test_current = 0
    if "test_answers" not in st.session_state:
        st.session_state.test_answers = {}

    if st.session_state.test_questions is None:
        # Start new test
        if st.button("Start Recall Test", type="primary", use_container_width=True):
            # Shuffle placements for test
            random.shuffle(placements)
            st.session_state.test_questions = placements[:min(10, len(placements))]
            st.session_state.test_current = 0
            st.session_state.test_score = 0
            st.session_state.test_answers = {}
            st.rerun()
    else:
        questions = st.session_state.test_questions
        current_idx = st.session_state.test_current

        if current_idx >= len(questions):
            # Test complete
            score = st.session_state.test_score
            total = len(questions)
            percentage = (score / total * 100) if total > 0 else 0

            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h3>Test Complete!</h3>
                <div class="metric-value" style="color: {'#10b981' if percentage >= 70 else '#f59e0b'};">
                    {score}/{total} ({percentage:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show answers
            st.markdown("### Review")
            for i, q in enumerate(questions):
                user_ans = st.session_state.test_answers.get(i, "")
                correct = q.get("term", "")
                icon = "✅" if user_ans.lower() == correct.lower() else "❌"
                st.markdown(f"{icon} {q.get('room_name', 'Location')}: **{correct}** (you said: {user_ans})")

            record_progress({"vocab_reviewed": score})
            log_activity("memory_palace", "recall_test", f"Score: {score}/{total}")

            if st.button("New Test", use_container_width=True):
                st.session_state.test_questions = None
                st.rerun()
        else:
            # Show current question
            q = questions[current_idx]
            palace_name = PALACE_LOCATIONS.get(q.get("palace", ""), {}).get("name", "Palace")

            st.markdown(f"### Question {current_idx + 1} of {len(questions)}")
            st.progress((current_idx + 1) / len(questions))

            st.markdown(f"""
            <div class="card">
                <strong>Location:</strong> {q.get('room_name', 'Unknown')} in {palace_name}<br>
                <em>Visualization hint:</em> {q.get('visualization', 'No hint saved')[:50]}...
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_input(
                "What word is placed here?",
                key=f"test_answer_{current_idx}"
            )

            if st.button("Submit Answer", type="primary"):
                st.session_state.test_answers[current_idx] = answer

                if answer.lower().strip() == q.get("term", "").lower():
                    st.session_state.test_score += 1

                st.session_state.test_current += 1
                st.rerun()


def render_my_palaces():
    """Render overview of user's palaces."""
    render_section_header("My Memory Palaces")

    placements = load_palace_placements()

    if not placements:
        st.info("No palaces built yet. Start by building your first palace!")
        return

    # Group by palace
    by_palace = {}
    for p in placements:
        palace = p.get("palace", "unknown")
        if palace not in by_palace:
            by_palace[palace] = []
        by_palace[palace].append(p)

    # Display palaces
    for palace_key, items in by_palace.items():
        palace_data = PALACE_LOCATIONS.get(palace_key, {"name": palace_key, "icon": "🏛️"})

        with st.expander(f"{palace_data['icon']} {palace_data['name']} ({len(items)} words)", expanded=True):
            for item in items:
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{item.get('room_name', '')}**: {item.get('term', '')}")
                    st.caption(item.get("meaning", ""))

                with col2:
                    if st.button("Remove", key=f"remove_{palace_key}_{item.get('room_id', '')}"):
                        remove_palace_placement(palace_key, item.get("room_id", ""))
                        st.rerun()


def save_palace_placement(palace: str, room_id: str, vocab: dict, visualization: str):
    """Save a palace placement to the database."""
    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            # Create table if not exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_palace (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    palace TEXT NOT NULL,
                    room_id TEXT NOT NULL,
                    room_name TEXT,
                    term TEXT NOT NULL,
                    meaning TEXT,
                    visualization TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(profile_id, palace, room_id)
                )
            """)

            # Get room name
            room_name = ""
            palace_data = PALACE_LOCATIONS.get(palace, {})
            for room in palace_data.get("rooms", []):
                if room["id"] == room_id:
                    room_name = room["name"]
                    break

            # Upsert placement
            conn.execute("""
                INSERT OR REPLACE INTO memory_palace
                (profile_id, palace, room_id, room_name, term, meaning, visualization)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (profile_id, palace, room_id, room_name, vocab.get("term", ""),
                  vocab.get("meaning", ""), visualization))
            conn.commit()
    except Exception as e:
        st.error(f"Error saving placement: {e}")


def load_palace_placements() -> list:
    """Load all palace placements for the current profile."""
    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            # Check if table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='memory_palace'
            """)
            if not cursor.fetchone():
                return []

            rows = conn.execute("""
                SELECT * FROM memory_palace
                WHERE profile_id = ?
                ORDER BY created_at DESC
            """, (profile_id,)).fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


def remove_palace_placement(palace: str, room_id: str):
    """Remove a palace placement."""
    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            conn.execute("""
                DELETE FROM memory_palace
                WHERE profile_id = ? AND palace = ? AND room_id = ?
            """, (profile_id, palace, room_id))
            conn.commit()
    except Exception as e:
        st.error(f"Error removing placement: {e}")
