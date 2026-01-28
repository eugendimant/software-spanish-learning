import random
from dataclasses import dataclass
from datetime import datetime
import io
import json
import csv
import hashlib
import sqlite3
from pathlib import Path

import streamlit as st


@dataclass(frozen=True)
class VocabItem:
    spanish: str
    english: str
    level: str
    topic: str


VOCAB = [
    VocabItem("hola", "hello", "A1", "greetings"),
    VocabItem("adiós", "goodbye", "A1", "greetings"),
    VocabItem("gracias", "thank you", "A1", "greetings"),
    VocabItem("por favor", "please", "A1", "greetings"),
    VocabItem("buenos días", "good morning", "A1", "greetings"),
    VocabItem("buenas noches", "good night", "A1", "greetings"),
    VocabItem("agua", "water", "A1", "food"),
    VocabItem("pan", "bread", "A1", "food"),
    VocabItem("manzana", "apple", "A1", "food"),
    VocabItem("café", "coffee", "A1", "food"),
    VocabItem("té", "tea", "A1", "food"),
    VocabItem("pollo", "chicken", "A2", "food"),
    VocabItem("pescado", "fish", "A2", "food"),
    VocabItem("verduras", "vegetables", "A2", "food"),
    VocabItem("la cuenta", "the bill", "A2", "food"),
    VocabItem("mercado", "market", "A2", "places"),
    VocabItem("farmacia", "pharmacy", "A2", "places"),
    VocabItem("biblioteca", "library", "A2", "places"),
    VocabItem("estación", "station", "A2", "places"),
    VocabItem("aprender", "to learn", "B1", "verbs"),
    VocabItem("recordar", "to remember", "B1", "verbs"),
    VocabItem("resolver", "to solve", "B1", "verbs"),
    VocabItem("lograr", "to achieve", "B1", "verbs"),
    VocabItem("sin embargo", "however", "B2", "connectors"),
    VocabItem("aunque", "although", "B2", "connectors"),
    VocabItem("por lo tanto", "therefore", "B2", "connectors"),
    VocabItem("a pesar de", "despite", "B2", "connectors"),
    VocabItem("desempeñar", "to perform", "C1", "verbs"),
    VocabItem("aprovechar", "to take advantage", "C1", "verbs"),
]

SENTENCES = [
    {"spanish": "¿Cómo estás?", "english": "How are you?", "level": "A1", "topic": "greetings"},
    {"spanish": "Me llamo Ana.", "english": "My name is Ana.", "level": "A1", "topic": "greetings"},
    {"spanish": "Quiero un café, por favor.", "english": "I want a coffee, please.", "level": "A1", "topic": "food"},
    {"spanish": "La cuenta, por favor.", "english": "The bill, please.", "level": "A1", "topic": "food"},
    {"spanish": "¿Dónde está la estación?", "english": "Where is the station?", "level": "A2", "topic": "places"},
    {"spanish": "Voy a la biblioteca.", "english": "I am going to the library.", "level": "A2", "topic": "places"},
    {"spanish": "Necesito recordar esa palabra.", "english": "I need to remember that word.", "level": "B1", "topic": "verbs"},
    {"spanish": "Sin embargo, seguimos aprendiendo.", "english": "However, we keep learning.", "level": "B2", "topic": "connectors"},
    {"spanish": "Aprovechamos la oportunidad.", "english": "We take advantage of the opportunity.", "level": "C1", "topic": "verbs"},
]

LESSONS = [
    {
        "id": "basics",
        "title": "Starter Pack",
        "level": "A1",
        "goal": "Greet people and introduce yourself.",
        "topics": ["greetings"],
        "story": "You meet new friends at a café in Madrid.",
    },
    {
        "id": "food",
        "title": "Café Conversations",
        "level": "A1-A2",
        "goal": "Order food and handle polite requests.",
        "topics": ["food"],
        "story": "You explore tapas and order confidently.",
    },
    {
        "id": "places",
        "title": "City Explorer",
        "level": "A2",
        "goal": "Navigate the city with directions and places.",
        "topics": ["places"],
        "story": "You plan a day across Barcelona.",
    },
    {
        "id": "verbs",
        "title": "Goal Setting",
        "level": "B1",
        "goal": "Use verbs for goals and achievements.",
        "topics": ["verbs"],
        "story": "You build a study plan with milestones.",
    },
    {
        "id": "connectors",
        "title": "Connect the Ideas",
        "level": "B2",
        "goal": "Link ideas with advanced connectors.",
        "topics": ["connectors"],
        "story": "You debate a topic with nuance.",
    },
    {
        "id": "advanced_verbs",
        "title": "Professional Spanish",
        "level": "C1",
        "goal": "Speak about performance and strategy.",
        "topics": ["verbs"],
        "story": "You lead a project update meeting.",
    },
]


def set_theme() -> None:
    st.set_page_config(page_title="VivaLingo", page_icon="🇪🇸", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --primary: #ff6f61;
            --secondary: #635bff;
            --mint: #40c9a2;
            --ink: #1f1f1f;
        }
        .stApp {
            background: linear-gradient(120deg, #fff5f0, #eef2ff, #e6fff7);
            animation: gradientShift 18s ease infinite;
            background-size: 200% 200%;
        }
        @keyframes gradientShift {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .hero {
            padding: 1.5rem 2rem;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.75);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        }
        .hero h1 {
            font-size: 2.6rem;
            margin-bottom: 0.5rem;
        }
        .floating-shape {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgba(99, 91, 255, 0.15);
            position: absolute;
            top: -40px;
            right: -30px;
            animation: float 7s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% {transform: translateY(0px)}
            50% {transform: translateY(16px)}
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            background: rgba(64, 201, 162, 0.15);
            color: #0f766e;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        .lesson-card {
            padding: 1rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .lesson-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }
        .exercise-card {
            padding: 1.5rem;
            border-radius: 24px;
            background: white;
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
            animation: slideIn 0.6s ease;
        }
        @keyframes slideIn {
            0% {opacity: 0; transform: translateX(20px)}
            100% {opacity: 1; transform: translateX(0)}
        }
        .stat-card {
            padding: 1rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .progress-bar {
            height: 10px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.2);
            overflow: hidden;
        }
        .progress-bar > span {
            display: block;
            height: 100%;
            background: linear-gradient(90deg, #ff6f61, #ffb347);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@dataclass
class Exercise:
    kind: str
    prompt: str
    answer: str
    options: list[str] | None = None
    explanation: str | None = None
    extra: dict | None = None
    metadata: dict | None = None


@dataclass
class UserRecord:
    username: str
    password_hash: str
    salt: str
    data_json: str | None


DATA_DIR = Path(__file__).resolve().parent
DB_PATH = DATA_DIR / "vivalingo_users.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                data_json TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            """
        )


def hash_password(password: str, salt: str) -> str:
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 150_000)
    return hash_bytes.hex()


def register_user(username: str, password: str) -> tuple[bool, str]:
    if not username or not password:
        return False, "Username and password are required."
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "That username is already taken."
        salt = hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()[:16]
        password_hash = hash_password(password, salt)
        connection.execute(
            """
            INSERT INTO users (username, password_hash, salt, data_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password_hash, salt, None, datetime.now().isoformat()),
        )
    return True, "Account created! Please log in."


def authenticate_user(username: str, password: str) -> tuple[bool, UserRecord | None]:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "SELECT username, password_hash, salt, data_json FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
    if not row:
        return False, None
    record = UserRecord(*row)
    if hash_password(password, record.salt) != record.password_hash:
        return False, None
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (datetime.now().isoformat(), username),
        )
    return True, record


def save_user_data(username: str, data: dict) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "UPDATE users SET data_json = ?, last_login = ? WHERE username = ?",
            (json.dumps(data), datetime.now().isoformat(), username),
        )


def load_user_data(data_json: str | None) -> dict:
    if not data_json:
        return {}
    try:
        return json.loads(data_json)
    except json.JSONDecodeError:
        return {}


def init_state() -> None:
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "goal": 15,
            "level": "Adaptive",
            "streak": 3,
            "xp": 120,
            "last_login": datetime.now().strftime("%Y-%m-%d"),
        }
    if "progress" not in st.session_state:
        st.session_state.progress = {lesson["id"]: 0 for lesson in LESSONS}
    if "mastery" not in st.session_state:
        st.session_state.mastery = {item.spanish: 0 for item in VOCAB}
    if "session" not in st.session_state:
        st.session_state.session = {
            "lesson_id": None,
            "exercises": [],
            "index": 0,
            "correct": 0,
            "answered": False,
            "feedback": "",
            "last_answer": "",
        }
    if "user" not in st.session_state:
        st.session_state.user = {"username": None, "authenticated": False}
    if "last_saved" not in st.session_state:
        st.session_state.last_saved = None
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    if "goals" not in st.session_state:
        st.session_state.goals = {"weekly_minutes": 90, "weekly_target": 5}
    if "focus" not in st.session_state:
        st.session_state.focus = {"topics": [], "level": "Adaptive"}


def filter_vocab(topics: list[str], level: str) -> list[VocabItem]:
    pool = [item for item in VOCAB if item.topic in topics]
    if level == "Adaptive":
        return pool
    return [item for item in pool if item.level <= level]


def filter_sentences(topics: list[str], level: str) -> list[dict]:
    pool = [sentence for sentence in SENTENCES if sentence["topic"] in topics]
    if level == "Adaptive":
        return pool
    return [sentence for sentence in pool if sentence["level"] <= level]

def make_exercises(
    lesson_id: str,
    difficulty: str,
    variety: list[str],
    topics_override: list[str] | None = None,
) -> list[Exercise]:
    lesson = next(l for l in LESSONS if l["id"] == lesson_id)
    topics = topics_override or lesson["topics"]
    vocab_pool = filter_vocab(topics, difficulty)
    sentence_pool = filter_sentences(topics, difficulty)
    random.shuffle(vocab_pool)
    random.shuffle(sentence_pool)

    exercises: list[Exercise] = []
    for item in vocab_pool[:6]:
        if "multiple_choice" in variety:
            options = [item.english]
            options += random.sample([v.english for v in VOCAB if v.english != item.english], 3)
            random.shuffle(options)
            exercises.append(
                Exercise(
                    kind="multiple_choice",
                    prompt=f"What does **{item.spanish}** mean?",
                    answer=item.english,
                    options=options,
                    explanation=f"{item.spanish} → {item.english}",
                    metadata={"spanish": item.spanish, "english": item.english},
                )
            )
        if "fill_blank" in variety:
            exercises.append(
                Exercise(
                    kind="fill_blank",
                    prompt=f"Complete: ___ = {item.english}",
                    answer=item.spanish,
                    explanation=f"The Spanish word is **{item.spanish}**.",
                    metadata={"spanish": item.spanish, "english": item.english},
                )
            )
        if "translate" in variety:
            exercises.append(
                Exercise(
                    kind="translate",
                    prompt=f"Translate into Spanish: {item.english}",
                    answer=item.spanish,
                    explanation=f"{item.english} → {item.spanish}",
                    metadata={"spanish": item.spanish, "english": item.english},
                )
            )

    if "match" in variety:
        pair_items = vocab_pool[:4]
        if pair_items:
            pairs = {item.spanish: item.english for item in pair_items}
            exercises.append(
                Exercise(
                    kind="match",
                    prompt="Match the Spanish word with its meaning.",
                    answer=";".join([f"{k}:{v}" for k, v in pairs.items()]),
                    extra={"pairs": pairs},
                )
            )

    if "sentence_translate" in variety and sentence_pool:
        for sentence in sentence_pool[:3]:
            exercises.append(
                Exercise(
                    kind="sentence_translate",
                    prompt=f"Translate the full sentence: {sentence['english']}",
                    answer=sentence["spanish"],
                    explanation=f"Possible answer: **{sentence['spanish']}**",
                    metadata=sentence,
                )
            )

    if "sentence_fill" in variety and sentence_pool:
        sentence = sentence_pool[0]
        parts = sentence["spanish"].split(" ")
        if len(parts) > 2:
            missing = parts[1]
            prompt = " ".join([parts[0], "___", *parts[2:]])
            exercises.append(
                Exercise(
                    kind="sentence_fill",
                    prompt=f"Fill the blank: {prompt}",
                    answer=missing,
                    explanation=f"Missing word: **{missing}**",
                    metadata=sentence,
                )
            )

    if "conversation" in variety:
        exercises.append(
            Exercise(
                kind="conversation",
                prompt="You meet someone in the morning. Choose the best greeting.",
                answer="buenos días",
                options=["buenas noches", "buenos días", "adiós", "gracias"],
                explanation="In the morning you say **buenos días**.",
            )
        )

    if "word_order" in variety:
        exercises.append(
            Exercise(
                kind="word_order",
                prompt="Arrange the words to say: 'Please, the bill'.",
                answer="por favor la cuenta",
                extra={"words": ["la", "cuenta", "por", "favor"]},
                explanation="The polite phrase is **por favor, la cuenta**.",
            )
        )

    random.shuffle(exercises)
    return exercises[:10]


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def check_answer(exercise: Exercise, response: str) -> tuple[bool, str]:
    normalized = normalize_text(response)
    answer = normalize_text(exercise.answer)
    if exercise.kind == "match":
        submitted_pairs = {}
        for part in response.split(";"):
            if ":" in part:
                spanish, english = part.split(":", 1)
                submitted_pairs[spanish.strip()] = english.strip()
        expected = exercise.extra["pairs"]
        if submitted_pairs == expected:
            return True, "Perfect matches!"
        return False, "Review the pairs and try again."
    if exercise.kind == "word_order":
        normalized = normalize_text(response)
    is_correct = normalized == answer
    if is_correct:
        return True, "Correct!"
    if exercise.kind in {"sentence_translate", "sentence_fill"}:
        return False, f"Close! {exercise.explanation or ''}"
    return False, f"Not quite. {exercise.explanation or ''}"


def update_mastery(exercise: Exercise, correct: bool) -> None:
    if exercise.kind not in {"multiple_choice", "fill_blank", "translate"}:
        return
    key = exercise.answer if exercise.kind != "multiple_choice" else None
    if exercise.kind == "multiple_choice":
        for item in VOCAB:
            if item.english == exercise.answer:
                key = item.spanish
                break
    if not key:
        return
    current = st.session_state.mastery.get(key, 0)
    st.session_state.mastery[key] = max(0, current + (2 if correct else -1))


def get_user_payload() -> dict:
    return {
        "profile": st.session_state.profile,
        "progress": st.session_state.progress,
        "mastery": st.session_state.mastery,
        "activity_log": st.session_state.activity_log,
        "goals": st.session_state.goals,
        "focus": st.session_state.focus,
    }


def apply_user_payload(payload: dict) -> None:
    if not payload:
        return
    for key in ["profile", "progress", "mastery", "activity_log", "goals", "focus"]:
        if key in payload:
            st.session_state[key] = payload[key]


def persist_if_authenticated() -> None:
    user = st.session_state.user
    if not user["authenticated"]:
        return
    save_user_data(user["username"], get_user_payload())
    st.session_state.last_saved = datetime.now().strftime("%Y-%m-%d %H:%M")


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero" style="position: relative; overflow: hidden;">
            <div class="floating-shape"></div>
            <span class="pill">Personalized</span>
            <span class="pill">Adaptive</span>
            <span class="pill">Motivating</span>
            <h1>VivaLingo — Your Spanish Journey Starts Here</h1>
            <p>Micro-lessons, rich visuals, and adaptive practice that grows with you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats() -> None:
    profile = st.session_state.profile
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Streak", f"{profile['streak']} days", "+1")
    col2.metric("XP", profile["xp"], "+20")
    col3.metric("Daily Goal", f"{profile['goal']} min", "On track")
    col4.metric("Level", profile["level"], "Adaptive")


def render_lesson_cards(selected_id: str | None) -> str:
    selection = selected_id
    cols = st.columns(3)
    for index, lesson in enumerate(LESSONS):
        progress = st.session_state.progress.get(lesson["id"], 0)
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="lesson-card">
                    <h3>{lesson['title']}</h3>
                    <p><strong>{lesson['level']}</strong> • {lesson['goal']}</p>
                    <div class="progress-bar"><span style="width: {progress}%;"></span></div>
                    <p style="margin-top:0.5rem; color:#475569;">{lesson['story']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Start {lesson['title']}", key=f"start-{lesson['id']}"):
                selection = lesson["id"]
    return selection


def render_match_exercise(exercise: Exercise, key_prefix: str) -> str:
    pairs = exercise.extra["pairs"]
    st.write("Connect each Spanish word with its meaning:")
    left = list(pairs.keys())
    right = list(pairs.values())
    selections = []
    for word in left:
        selection = st.selectbox(
            f"{word}",
            options=right,
            key=f"{key_prefix}-match-{st.session_state.session['index']}-{word}",
        )
        selections.append(f"{word}:{selection}")
    return ";".join(selections)


def render_word_order(exercise: Exercise, key_prefix: str) -> str:
    st.write("Tap the words in order (type them in the box):")
    st.caption("Words: " + ", ".join(exercise.extra["words"]))
    return st.text_input(
        "Your sentence",
        key=f"{key_prefix}-word-order-{st.session_state.session['index']}",
    )


def render_exercise(exercise: Exercise, key_prefix: str) -> str:
    st.markdown(f"<div class='exercise-card'>", unsafe_allow_html=True)
    st.subheader(exercise.prompt)
    response = ""
    if exercise.kind == "multiple_choice" or exercise.kind == "conversation":
        response = st.radio(
            "Pick one",
            exercise.options,
            key=f"{key_prefix}-mc-{st.session_state.session['index']}",
        )
    elif exercise.kind in {"fill_blank", "translate", "sentence_translate", "sentence_fill"}:
        response = st.text_input(
            "Your answer",
            key=f"{key_prefix}-text-{st.session_state.session['index']}-{exercise.kind}",
        )
    elif exercise.kind == "match":
        response = render_match_exercise(exercise, key_prefix)
    elif exercise.kind == "word_order":
        response = render_word_order(exercise, key_prefix)
    st.markdown("</div>", unsafe_allow_html=True)
    return response


def render_session(selected_lesson: str, settings: dict, key_prefix: str) -> None:
    session = st.session_state.session
    if session["lesson_id"] != selected_lesson or not session["exercises"]:
        session["lesson_id"] = selected_lesson
        session["exercises"] = make_exercises(
            selected_lesson,
            settings["difficulty"],
            settings["variety"],
        )
        session["index"] = 0
        session["correct"] = 0
        session["answered"] = False
        session["feedback"] = ""

    total = len(session["exercises"])
    index = session["index"]
    progress_ratio = (index / total) if total else 0
    st.progress(progress_ratio)

    if index >= total:
        st.success("Lesson complete! Great work.")
        st.session_state.progress[selected_lesson] = min(100, st.session_state.progress[selected_lesson] + 20)
        st.session_state.profile["xp"] += 25
        st.session_state.activity_log.append(
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "lesson": selected_lesson,
                "accuracy": round(session["correct"] / total, 2) if total else 0,
                "total": total,
                "correct": session["correct"],
                "xp": st.session_state.profile["xp"],
            }
        )
        persist_if_authenticated()
        if st.button("Restart lesson"):
            session["exercises"] = []
        return

    exercise = session["exercises"][index]
    response = render_exercise(exercise, key_prefix)
    st.write("")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Check", key=f"{key_prefix}-check-answer"):
            correct, feedback = check_answer(exercise, response)
            session["answered"] = True
            session["feedback"] = feedback
            session["last_answer"] = response
            if correct:
                session["correct"] += 1
                st.session_state.profile["xp"] += 5
            update_mastery(exercise, correct)
            persist_if_authenticated()
    with col2:
        if st.button("Next", key=f"{key_prefix}-next-question"):
            if session["answered"]:
                session["index"] += 1
                session["answered"] = False
                session["feedback"] = ""
            else:
                st.warning("Check your answer before moving on.")

    if session["feedback"]:
        st.info(session["feedback"])

    st.caption(f"Accuracy so far: {session['correct']} / {index + 1}")


def render_progress() -> None:
    st.subheader("Progress Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric("Vocabulary Mastery", f"{sum(v > 0 for v in st.session_state.mastery.values())} words")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric("Lessons Completed", f"{sum(p >= 100 for p in st.session_state.progress.values())} / {len(LESSONS)}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric("Active Streak", f"{st.session_state.profile['streak']} days")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Mastery by Word")
    for word, score in sorted(st.session_state.mastery.items(), key=lambda item: item[1], reverse=True):
        if score <= 0:
            continue
        st.write(f"{word}: {'⭐' * min(score, 5)}")

    if st.session_state.activity_log:
        st.markdown("### Practice History")
        st.dataframe(st.session_state.activity_log, use_container_width=True)
        accuracy = [entry["accuracy"] for entry in st.session_state.activity_log[-10:]]
        st.line_chart(accuracy, height=220)
        xp_values = [entry["xp"] for entry in st.session_state.activity_log[-10:]]
        st.line_chart(xp_values, height=220)


def render_insights() -> None:
    st.subheader("Insights & Motivation")
    goals = st.session_state.goals
    goals["weekly_minutes"] = st.slider("Weekly minutes goal", 30, 240, goals["weekly_minutes"], step=15)
    goals["weekly_target"] = st.slider("Weekly sessions goal", 1, 7, goals["weekly_target"])
    st.markdown("### Study Rhythm")
    recent_sessions = st.session_state.activity_log[-7:]
    st.write(f"Sessions this week: **{len(recent_sessions)}**")
    if recent_sessions:
        avg_accuracy = sum(s["accuracy"] for s in recent_sessions) / len(recent_sessions)
        st.metric("Average accuracy (last 7)", f"{avg_accuracy:.0%}")
    st.info("Try mixing lesson types to reinforce vocabulary in different contexts.")
    st.markdown("### Achievements")
    xp = st.session_state.profile["xp"]
    streak = st.session_state.profile["streak"]
    badges = []
    if xp >= 100:
        badges.append("🏅 100 XP Earned")
    if xp >= 250:
        badges.append("🚀 250 XP Momentum")
    if streak >= 5:
        badges.append("🔥 5-Day Streak")
    if len(st.session_state.activity_log) >= 5:
        badges.append("📚 5 Lessons Completed")
    if badges:
        for badge in badges:
            st.success(badge)
    else:
        st.info("Complete lessons to unlock achievement badges.")
    persist_if_authenticated()


def export_activity_csv() -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["date", "lesson", "accuracy", "total", "correct", "xp"])
    writer.writeheader()
    writer.writerows(st.session_state.activity_log)
    return output.getvalue()


def render_downloads() -> None:
    st.subheader("Download Your Progress")
    if not st.session_state.activity_log:
        st.warning("Complete a lesson to unlock progress exports.")
        return
    st.download_button(
        "Download CSV",
        data=export_activity_csv(),
        file_name="vivalingo_progress.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download JSON",
        data=json.dumps(st.session_state.activity_log, indent=2),
        file_name="vivalingo_progress.json",
        mime="application/json",
    )


def render_profile() -> None:
    st.subheader("Profile & Login")
    user = st.session_state.user
    if user["authenticated"]:
        st.success(f"Logged in as **{user['username']}**")
        if st.session_state.last_saved:
            st.caption(f"Last saved: {st.session_state.last_saved}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save progress now"):
                persist_if_authenticated()
                st.success("Progress saved.")
        with col2:
            if st.button("Log out"):
                persist_if_authenticated()
                st.session_state.user = {"username": None, "authenticated": False}
                st.info("You have been logged out.")
        return

    st.markdown("### Create a new profile")
    with st.form("register-form"):
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        register_submit = st.form_submit_button("Create account")
    if register_submit:
        ok, message = register_user(new_username.strip().lower(), new_password)
        if ok:
            st.success(message)
        else:
            st.error(message)

    st.markdown("### Log in")
    with st.form("login-form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Log in")
    if login_submit:
        ok, record = authenticate_user(username.strip().lower(), password)
        if not ok or record is None:
            st.error("Invalid username or password.")
        else:
            st.session_state.user = {"username": record.username, "authenticated": True}
            payload = load_user_data(record.data_json)
            apply_user_payload(payload)
            st.success("Welcome back! Your progress has been loaded.")


def render_library() -> None:
    st.subheader("Skill Library")
    st.write("Pick a focus area or jump into a custom practice session.")
    topics = sorted({item.topic for item in VOCAB})
    selected_topics = st.multiselect("Focus topics", topics, default=topics[:2])
    level = st.selectbox("Target level", ["Adaptive", "A1", "A2", "B1", "B2", "C1"], index=1)
    if st.button("Generate custom practice"):
        st.session_state.focus["topics"] = selected_topics
        st.session_state.focus["level"] = level
        st.session_state.session["lesson_id"] = "custom"
        st.session_state.session["exercises"] = make_exercises(
            lesson_id=LESSONS[0]["id"],
            difficulty=level,
            variety=["multiple_choice", "fill_blank", "translate", "word_order"],
            topics_override=selected_topics or LESSONS[0]["topics"],
        )
        st.success("Custom practice loaded. Go to Learn tab to start.")
        persist_if_authenticated()


def render_settings() -> dict:
    st.subheader("Learning Preferences")
    profile = st.session_state.profile
    profile["name"] = st.text_input("Name", profile["name"], placeholder="Tu nombre")
    profile["goal"] = st.slider("Daily goal (minutes)", 5, 45, profile["goal"], step=5)
    profile["level"] = st.selectbox("Learning level", ["Adaptive", "A1", "A2", "B1", "B2", "C1"], index=0)
    st.markdown("### Exercise Mix")
    options = [
        "multiple_choice",
        "fill_blank",
        "translate",
        "match",
        "conversation",
        "word_order",
        "sentence_translate",
        "sentence_fill",
    ]
    default_options = [
        "multiple_choice",
        "fill_blank",
        "translate",
        "conversation",
        "word_order",
        "sentence_translate",
    ]
    variety = st.multiselect("Choose exercise types", options, default=default_options)
    st.markdown("### Coaching Tips")
    st.info("Mix practice modes daily. Short, frequent sessions help retention.")
    persist_if_authenticated()
    return {"difficulty": profile["level"], "variety": variety}


def main() -> None:
    init_db()
    set_theme()
    init_state()

    render_hero()
    st.write("")
    render_stats()

    tabs = st.tabs(["Learn", "Practice", "Progress", "Library", "Insights", "Downloads", "Profile", "Settings"])
    with tabs[0]:
        st.markdown("### Choose a lesson")
        selected = st.session_state.session.get("lesson_id")
        selected = render_lesson_cards(selected)
        if selected:
            st.session_state.session["lesson_id"] = selected
        st.markdown("---")
        if st.session_state.session.get("lesson_id"):
            settings = {
                "difficulty": st.session_state.profile["level"],
                "variety": st.session_state.get("variety", ["multiple_choice", "fill_blank", "translate"]),
            }
            render_session(st.session_state.session["lesson_id"], settings, "learn")
    with tabs[1]:
        st.markdown("### Adaptive practice")
        settings = {
            "difficulty": st.session_state.profile["level"],
            "variety": st.session_state.get("variety", ["multiple_choice", "fill_blank", "translate"]),
        }
        if st.button("Start adaptive practice"):
            st.session_state.session["lesson_id"] = LESSONS[0]["id"]
            st.session_state.session["exercises"] = make_exercises(
                lesson_id=LESSONS[0]["id"],
                difficulty=settings["difficulty"],
                variety=settings["variety"],
            )
            st.session_state.session["index"] = 0
        if st.session_state.session.get("lesson_id"):
            render_session(st.session_state.session["lesson_id"], settings, "practice")
    with tabs[2]:
        render_progress()
    with tabs[3]:
        render_library()
    with tabs[4]:
        render_insights()
    with tabs[5]:
        render_downloads()
    with tabs[6]:
        render_profile()
    with tabs[7]:
        settings = render_settings()
        st.session_state.variety = settings["variety"]


if __name__ == "__main__":
    main()
