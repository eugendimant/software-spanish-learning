import csv
import hashlib
import io
import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


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

EXTRA_DIALOGUES = [
    {
        "prompt": "You're ordering at a café. How do you politely ask for water?",
        "answer": "Quisiera agua, por favor.",
        "options": [
            "¿Dónde está la estación?",
            "Quisiera agua, por favor.",
            "Gracias, hasta luego.",
            "No entiendo.",
        ],
    },
    {
        "prompt": "A friend says: 'Buenos días'. How do you reply?",
        "answer": "Buenos días.",
        "options": ["Buenas noches.", "Buenos días.", "Adiós.", "Lo siento."],
    },
    {
        "prompt": "You need the bill. What do you say?",
        "answer": "La cuenta, por favor.",
        "options": ["¿Qué hora es?", "La cuenta, por favor.", "Estoy perdido.", "Gracias."],
    },
]

SENTENCES = [
    {
        "spanish": "Me llamo Sofía y soy de México.",
        "english": "My name is Sofia and I am from Mexico.",
        "level": "A1",
        "topic": "greetings",
    },
    {
        "spanish": "Quisiera un café con leche, por favor.",
        "english": "I would like a coffee with milk, please.",
        "level": "A1",
        "topic": "food",
    },
    {
        "spanish": "¿Dónde está la estación de metro?",
        "english": "Where is the metro station?",
        "level": "A2",
        "topic": "places",
    },
    {
        "spanish": "Estoy aprendiendo español para mi trabajo.",
        "english": "I am learning Spanish for my job.",
        "level": "B1",
        "topic": "verbs",
    },
    {
        "spanish": "Aunque hace frío, vamos a caminar por el parque.",
        "english": "Although it is cold, we are going to walk through the park.",
        "level": "B2",
        "topic": "connectors",
    },
    {
        "spanish": "Aprovechamos la reunión para presentar la estrategia.",
        "english": "We took advantage of the meeting to present the strategy.",
        "level": "C1",
        "topic": "verbs",
    },
    {
        "spanish": "Necesito comprar pan y verduras en el mercado.",
        "english": "I need to buy bread and vegetables at the market.",
        "level": "A2",
        "topic": "food",
    },
    {
        "spanish": "Siempre estudio por la mañana antes del trabajo.",
        "english": "I always study in the morning before work.",
        "level": "B1",
        "topic": "verbs",
    },
    {
        "spanish": "¿Podrías recomendarme un buen restaurante?",
        "english": "Could you recommend a good restaurant?",
        "level": "A2",
        "topic": "places",
    },
    {
        "spanish": "Por lo tanto, debemos practicar todos los días.",
        "english": "Therefore, we should practice every day.",
        "level": "B2",
        "topic": "connectors",
    },
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

DATA_DIR = Path("data")
PROFILE_PATH = DATA_DIR / "profiles.json"
DOM_ID_SAFE = "".join([str(x) for x in range(10)]) + "abcdefghijklmnopqrstuvwxyz-"


def set_theme() -> None:
    st.set_page_config(page_title="VivaLingo", page_icon="🇪🇸", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --primary: #ff6f61;
            --secondary: #4638ff;
            --mint: #2abf97;
            --ink: #0f172a;
            --muted: #475569;
            --surface: rgba(255, 255, 255, 0.92);
            --surface-strong: rgba(255, 255, 255, 0.98);
            --border: rgba(148, 163, 184, 0.25);
        }
        .stApp {
            color: var(--ink);
            background: linear-gradient(140deg, #f8fafc 0%, #eef2ff 45%, #ecfeff 100%);
            background-attachment: fixed;
            font-family: "Inter", "SF Pro Text", "Segoe UI", system-ui, -apple-system, sans-serif;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: var(--ink);
        }
        .stMarkdown p {
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
        }
        @keyframes gradientShift {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .hero {
            padding: 1.75rem 2.2rem;
            border-radius: 24px;
            background: var(--surface-strong);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
            border: 1px solid var(--border);
        }
        .hero h1 {
            font-size: 2.5rem;
            color: var(--ink);
            margin-bottom: 0.5rem;
        }
        .hero p {
            color: var(--muted);
            font-size: 1.05rem;
        }
        .floating-shape {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgba(70, 56, 255, 0.16);
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
            background: rgba(42, 191, 151, 0.18);
            color: #0f766e;
            font-weight: 600;
            margin-right: 0.5rem;
        }
        .lesson-card {
            padding: 1rem;
            border-radius: 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .lesson-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }
        .exercise-card {
            padding: 1.5rem;
            border-radius: 24px;
            background: var(--surface-strong);
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
            background: var(--surface);
            border: 1px solid var(--border);
        }
        .auth-card {
            padding: 1.5rem;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(148, 163, 184, 0.25);
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
        }
        .progress-bar {
            height: 10px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.28);
            overflow: hidden;
        }
        .progress-bar > span {
            display: block;
            height: 100%;
            background: linear-gradient(90deg, #ff6f61, #ffb347);
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--muted);
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: var(--ink);
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox div, .stRadio div {
            color: var(--ink) !important;
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #fff !important;
            border: 1px solid rgba(148, 163, 184, 0.5) !important;
            border-radius: 12px !important;
        }
        .stButton button {
            border-radius: 12px;
            font-weight: 600;
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


def default_session_state() -> dict:
    return {
        "lesson_id": None,
        "exercises": [],
        "index": 0,
        "correct": 0,
        "answered": False,
        "feedback": "",
        "last_answer": "",
        "results": {},
    }


def sanitize_dom_id(value: str) -> str:
    return "".join(char for char in value.lower() if char in DOM_ID_SAFE)


def load_profiles() -> dict:
    if not PROFILE_PATH.exists():
        return {}
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_profiles(profiles: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profiles, indent=2), encoding="utf-8")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def default_profile_state() -> dict:
    return {
        "profile": {
            "name": "",
            "goal": 15,
            "level": "Adaptive",
            "streak": 3,
            "xp": 120,
            "last_login": datetime.now().strftime("%Y-%m-%d"),
        },
        "progress": {lesson["id"]: 0 for lesson in LESSONS},
        "mastery": {item.spanish: 0 for item in VOCAB},
        "activity_log": [],
        "goals": {"weekly_minutes": 90, "weekly_target": 5},
        "focus": {"topics": [], "level": "Adaptive"},
    }


def apply_profile_state(state: dict) -> None:
    defaults = default_profile_state()
    merged = {
        "profile": {**defaults["profile"], **state.get("profile", {})},
        "progress": {**defaults["progress"], **state.get("progress", {})},
        "mastery": {**defaults["mastery"], **state.get("mastery", {})},
        "activity_log": state.get("activity_log", defaults["activity_log"]),
        "goals": {**defaults["goals"], **state.get("goals", {})},
        "focus": {**defaults["focus"], **state.get("focus", {})},
    }
    st.session_state.profile = merged["profile"]
    st.session_state.progress = merged["progress"]
    st.session_state.mastery = merged["mastery"]
    st.session_state.activity_log = merged["activity_log"]
    st.session_state.goals = merged["goals"]
    st.session_state.focus = merged["focus"]


def persist_profile_state() -> None:
    if not st.session_state.auth.get("logged_in"):
        return
    profiles = load_profiles()
    email = st.session_state.auth["email"]
    profiles[email]["state"] = {
        "profile": st.session_state.profile,
        "progress": st.session_state.progress,
        "mastery": st.session_state.mastery,
        "activity_log": st.session_state.activity_log,
        "goals": st.session_state.goals,
        "focus": st.session_state.focus,
    }
    profiles[email]["state"]["profile"]["last_login"] = datetime.now().strftime("%Y-%m-%d")
    save_profiles(profiles)


def create_profile(name: str, email: str, password: str) -> tuple[bool, str]:
    if not name or not email or not password:
        return False, "Please complete all fields."
    profiles = load_profiles()
    if email in profiles:
        return False, "Account already exists. Please log in."
    profiles[email] = {
        "name": name,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "state": default_profile_state(),
    }
    profiles[email]["state"]["profile"]["name"] = name
    save_profiles(profiles)
    return True, "Profile created. You're ready to learn!"


def authenticate(email: str, password: str) -> tuple[bool, str]:
    profiles = load_profiles()
    account = profiles.get(email)
    if not account:
        return False, "We couldn't find that account."
    if account["password"] != hash_password(password):
        return False, "Incorrect password."
    return True, "Welcome back!"


def init_state() -> None:
    if "auth" not in st.session_state:
        st.session_state.auth = {"email": "", "logged_in": False}
    if "profile" not in st.session_state:
        defaults = default_profile_state()
        apply_profile_state(defaults)
    if "sessions" not in st.session_state:
        st.session_state.sessions = {
            "learn": default_session_state(),
            "practice": default_session_state(),
        }
    if "variety" not in st.session_state:
        st.session_state.variety = [
            "multiple_choice",
            "fill_blank",
            "translate",
            "listening",
            "listening_type",
            "dialogue",
            "cloze",
            "conversation",
            "word_order",
            "sentence_build",
        ]


def filter_vocab(topics: list[str], level: str) -> list[VocabItem]:
    pool = [item for item in VOCAB if item.topic in topics]
    if level == "Adaptive":
        return pool
    rank = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}
    target = rank.get(level, 5)
    return [item for item in pool if rank.get(item.level, 5) <= target]


def filter_sentences(topics: list[str], level: str) -> list[dict]:
    pool = [sentence for sentence in SENTENCES if sentence["topic"] in topics]
    if level == "Adaptive":
        return pool
    rank = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}
    target = rank.get(level, 5)
    return [sentence for sentence in pool if rank.get(sentence["level"], 5) <= target]


def build_options(correct: str, pool: list[str], size: int = 4) -> list[str]:
    options = [correct]
    candidates = [item for item in pool if item != correct]
    random.shuffle(candidates)
    options.extend(candidates[: max(0, size - 1)])
    if len(options) < size:
        fallback = [item.english for item in VOCAB if item.english not in options]
        random.shuffle(fallback)
        options.extend(fallback[: size - len(options)])
    random.shuffle(options)
    return options


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

    exercises: list[Exercise] = []
    if difficulty == "Adaptive":
        vocab_pool.sort(key=lambda item: st.session_state.mastery.get(item.spanish, 0))

    for item in vocab_pool[:6]:
        if "multiple_choice" in variety:
            options = build_options(item.english, [v.english for v in VOCAB])
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
        if "listening" in variety:
            options = build_options(item.english, [v.english for v in VOCAB])
            exercises.append(
                Exercise(
                    kind="listening",
                    prompt="Listen and choose the correct meaning.",
                    answer=item.english,
                    options=options,
                    explanation=f"You heard **{item.spanish}**.",
                    metadata={"spanish": item.spanish, "english": item.english},
                )
            )
        if "listening_type" in variety:
            exercises.append(
                Exercise(
                    kind="listening_type",
                    prompt="Listen and type the Spanish word you hear.",
                    answer=item.spanish,
                    explanation=f"The word was **{item.spanish}**.",
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

    if "dialogue" in variety:
        dialogue = random.choice(EXTRA_DIALOGUES)
        exercises.append(
            Exercise(
                kind="dialogue",
                prompt=dialogue["prompt"],
                answer=dialogue["answer"],
                options=dialogue["options"],
                explanation=f"A natural response is **{dialogue['answer']}**.",
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

    if "sentence_build" in variety and sentence_pool:
        sentence = random.choice(sentence_pool)
        words = sentence["spanish"].replace("¿", "").replace("?", "").replace(",", "").split()
        random.shuffle(words)
        exercises.append(
            Exercise(
                kind="sentence_build",
                prompt=f"Build the sentence: '{sentence['english']}'",
                answer=sentence["spanish"],
                extra={"words": words},
                explanation=f"One correct answer is: {sentence['spanish']}",
                metadata={"spanish": sentence["spanish"], "english": sentence["english"]},
            )
        )

    if "cloze" in variety and sentence_pool:
        sentence = random.choice(sentence_pool)
        cloze = build_cloze(sentence)
        if cloze:
            exercises.append(cloze)

    random.shuffle(exercises)
    return exercises[:10]


def normalize_text(text: str) -> str:
    cleaned = text.strip().lower()
    for char in ["¿", "?", "!", ",", ".", "¡"]:
        cleaned = cleaned.replace(char, "")
    return " ".join(cleaned.split())


def check_answer(exercise: Exercise, response: str) -> tuple[bool, str]:
    if not response:
        return False, "Please enter or choose an answer before checking."
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
    return False, f"Not quite. {exercise.explanation or ''}"


def update_mastery(exercise: Exercise, correct: bool) -> None:
    if exercise.kind not in {"multiple_choice", "fill_blank", "translate", "listening", "listening_type", "cloze"}:
        return
    key = exercise.answer if exercise.kind not in {"multiple_choice", "listening"} else None
    if exercise.kind in {"multiple_choice", "listening"}:
        for item in VOCAB:
            if item.english == exercise.answer:
                key = item.spanish
                break
    if not key:
        return
    current = st.session_state.mastery.get(key, 0)
    st.session_state.mastery[key] = max(0, current + (2 if correct else -1))


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


def render_auth_panel() -> None:
    with st.container():
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        if st.session_state.auth.get("logged_in"):
            profile = st.session_state.profile
            st.subheader(f"Welcome back, {profile['name'] or 'Learner'}")
            st.caption(f"Signed in as {st.session_state.auth['email']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save progress"):
                    persist_profile_state()
                    st.success("Progress saved.")
            with col2:
                if st.button("Sign out"):
                    persist_profile_state()
                    st.session_state.auth = {"email": "", "logged_in": False}
                    apply_profile_state(default_profile_state())
                    st.success("Signed out.")
        else:
            st.subheader("Create a profile or log in")
            tab_create, tab_login = st.tabs(["Create profile", "Log in"])
            with tab_create:
                with st.form("create-profile"):
                    name = st.text_input("Name", placeholder="Your name")
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Create profile")
                if submitted:
                    success, message = create_profile(name, email, password)
                    if success:
                        profiles = load_profiles()
                        st.session_state.auth = {"email": email, "logged_in": True}
                        apply_profile_state(profiles[email]["state"])
                        st.success(message)
                    else:
                        st.error(message)
            with tab_login:
                with st.form("login-profile"):
                    email = st.text_input("Email", key="login-email")
                    password = st.text_input("Password", type="password", key="login-password")
                    submitted = st.form_submit_button("Log in")
                if submitted:
                    success, message = authenticate(email, password)
                    if success:
                        profiles = load_profiles()
                        st.session_state.auth = {"email": email, "logged_in": True}
                        apply_profile_state(profiles[email]["state"])
                        st.success(message)
                    else:
                        st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)


def render_lesson_cards(selected_id: str | None) -> str:
    selection = selected_id
    cols = st.columns(3)
    for index, lesson in enumerate(LESSONS):
        progress = st.session_state.progress.get(lesson["id"], 0)
        with cols[index % 3]:
            with st.container():
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
                if st.button(f"Start {lesson['title']}", key=f"start-{lesson['id']}", use_container_width=True):
                    selection = lesson["id"]
    return selection


def render_match_exercise(exercise: Exercise, key_prefix: str, index: int) -> str:
    pairs = exercise.extra["pairs"]
    st.write("Connect each Spanish word with its meaning:")
    left = list(pairs.keys())
    right = list(pairs.values())
    selections = []
    for word in left:
        selection = st.selectbox(
            f"{word}",
            options=right,
            key=f"{key_prefix}-match-{index}-{word}",
        )
        selections.append(f"{word}:{selection}")
    return ";".join(selections)


def render_word_order(exercise: Exercise, key_prefix: str, index: int) -> str:
    st.write("Tap the words in order (type them in the box):")
    st.caption("Words: " + ", ".join(exercise.extra["words"]))
    return st.text_input("Your sentence", key=f"{key_prefix}-word-order-{index}")

def render_sentence_build(exercise: Exercise, key_prefix: str) -> str:
    st.write("Rebuild the sentence using the words provided:")
    st.caption("Words: " + ", ".join(exercise.extra["words"]))
    return st.text_input("Your sentence", key=f"{key_prefix}-sentence-build-{st.session_state.session['index']}")


def render_voice_practice(expected: str, key_prefix: str, label: str) -> None:
    payload = json.dumps(expected)
    components.html(
        f"""
        <div style="border:1px solid #e2e8f0; padding:12px; border-radius:12px; background:#fff;">
            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                <button id="voice-btn-{key_prefix}" style="padding:8px 12px; border-radius:8px; border:1px solid #cbd5f5; background:#f8fafc;">
                    🎙️ Start voice mode
                </button>
                <span style="font-size:13px; color:#64748b;">Speak the phrase and get instant feedback.</span>
            </div>
            <div style="margin-top:10px; font-size:14px;">
                <strong>Transcript:</strong>
                <div id="voice-transcript-{key_prefix}" style="margin-top:4px; color:#0f172a;"></div>
            </div>
            <div style="margin-top:6px; font-size:13px; color:#475569;">
                <strong>Pronunciation score:</strong>
                <span id="voice-score-{key_prefix}">--</span>
            </div>
            <div style="margin-top:4px; font-size:12px; color:#94a3b8;">Target: {label}</div>
        </div>
        <script>
            const expected = {payload};
            const normalize = (text) => text
                .toLowerCase()
                .replace(/[¿?¡!.,]/g, '')
                .replace(/\\s+/g, ' ')
                .trim();
            const scorePronunciation = (spoken, target) => {{
                if (!spoken) return 0;
                const spokenWords = normalize(spoken).split(' ');
                const targetWords = normalize(target).split(' ');
                let matchCount = 0;
                targetWords.forEach((word) => {{
                    if (spokenWords.includes(word)) matchCount += 1;
                }});
                return Math.round((matchCount / Math.max(targetWords.length, 1)) * 100);
            }};
            const button = document.getElementById('voice-btn-{key_prefix}');
            const transcriptEl = document.getElementById('voice-transcript-{key_prefix}');
            const scoreEl = document.getElementById('voice-score-{key_prefix}');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                button.disabled = true;
                transcriptEl.textContent = 'Voice recognition is not supported in this browser.';
            }} else {{
                const recognition = new SpeechRecognition();
                recognition.lang = 'es-ES';
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;
                button.addEventListener('click', () => {{
                    transcriptEl.textContent = 'Listening...';
                    scoreEl.textContent = '--';
                    recognition.start();
                }});
                recognition.addEventListener('result', (event) => {{
                    const spoken = event.results[0][0].transcript;
                    transcriptEl.textContent = spoken;
                    const score = scorePronunciation(spoken, expected);
                    scoreEl.textContent = `${{score}}%`;
                }});
                recognition.addEventListener('error', () => {{
                    transcriptEl.textContent = 'We could not capture audio. Try again.';
                }});
            }}
        </script>
        """,
        height=210,
    )


def render_listening_exercise(exercise: Exercise, key_prefix: str) -> str:
    spanish = exercise.metadata["spanish"]
    payload = json.dumps(spanish)
    components.html(
        f"""
        <div style="display:flex; gap:12px; align-items:center; padding:8px 0;">
            <button id="audio-btn-{dom_id}" style="padding:8px 14px; border-radius:10px; border:1px solid #cbd5f5; background:#fff;">
                🔊 Play audio
            </button>
            <span style="color:#475569; font-size:14px;">{helper_text}</span>
        </div>
        <script>
            const button = document.getElementById('audio-btn-{dom_id}');
            if (button) {{
                button.addEventListener('click', () => {{
                    const text = {payload};
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'es-ES';
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }});
            }}
        </script>
        """,
        height=70,
    )
    return st.radio(
        "Pick the meaning",
        exercise.options,
        key=f"{key_prefix}-listen-{st.session_state.session['index']}",
    )


def render_exercise(exercise: Exercise, key_prefix: str) -> str:
    st.markdown(f"<div class='exercise-card'>", unsafe_allow_html=True)
    st.subheader(exercise.prompt)
    response = ""
    if exercise.kind == "multiple_choice" or exercise.kind == "conversation":
        response = st.radio(
            "Pick one",
            exercise.options,
            key=f"{key_prefix}-mc-{index}",
        )
    elif exercise.kind in {"fill_blank", "translate"}:
        response = st.text_input("Your answer", key=f"{key_prefix}-text-{index}")
    elif exercise.kind == "match":
        response = render_match_exercise(exercise, key_prefix, index)
    elif exercise.kind == "word_order":
        response = render_word_order(exercise, key_prefix)
    elif exercise.kind == "sentence_build":
        response = render_sentence_build(exercise, key_prefix)
    elif exercise.kind == "listening":
        response = render_listening_exercise(exercise, key_prefix)
    if exercise.kind in {"fill_blank", "translate", "word_order", "sentence_build"}:
        st.markdown("##### Voice mode")
        render_voice_practice(exercise.answer, f"{key_prefix}-voice-{st.session_state.session['index']}", exercise.answer)
    if exercise.kind == "listening":
        st.markdown("##### Voice mode")
        render_voice_practice(
            exercise.metadata["spanish"],
            f"{key_prefix}-voice-{st.session_state.session['index']}",
            exercise.metadata["spanish"],
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return response


def render_session(selected_lesson: str, settings: dict, session_label: str) -> None:
    session = st.session_state.sessions[session_label]
    if selected_lesson == "custom" and session["exercises"]:
        pass
    elif session["lesson_id"] != selected_lesson or not session["exercises"]:
        session.update(default_session_state())
        session["lesson_id"] = selected_lesson
        session["exercises"] = make_exercises(
            selected_lesson,
            settings["difficulty"],
            settings["variety"],
        )

    total = len(session["exercises"])
    index = session["index"]
    progress_ratio = (index / total) if total else 0
    st.progress(progress_ratio)

    if index >= total:
        st.success("Lesson complete! Great work.")
        if selected_lesson in st.session_state.progress:
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
        persist_profile_state()
        if st.button("Restart lesson"):
            session.update(default_session_state())
            session["lesson_id"] = selected_lesson
        return

    exercise = session["exercises"][index]
    key_prefix = f"{session_label}-{selected_lesson}"
    response = render_exercise(exercise, key_prefix, index)
    st.write("")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Check", key=f"{key_prefix}-check-answer", use_container_width=True):
            correct, feedback = check_answer(exercise, response)
            result = session["results"].get(index, {"mistake": False, "correct": False})
            if result["correct"] and not result["mistake"]:
                session["answered"] = True
                session["feedback"] = "Already marked correct. Move to the next question when you're ready."
                session["last_answer"] = response
                return
            if correct:
                if not result["mistake"] and not result["correct"]:
                    session["correct"] += 1
                    st.session_state.profile["xp"] += 5
                if result["mistake"]:
                    feedback = f"{feedback} You got it now, but accuracy won't change because of the earlier miss."
                result["correct"] = True
            else:
                result["mistake"] = True
            session["results"][index] = result
            session["answered"] = True
            session["feedback"] = feedback
            session["last_answer"] = response
            update_mastery(exercise, correct)
            persist_profile_state()
    with col2:
        if st.button("Next", key=f"{key_prefix}-next-question", use_container_width=True):
            if session["answered"]:
                session["index"] += 1
                session["answered"] = False
                session["feedback"] = ""
            else:
                st.warning("Check your answer before moving on.")

    if session["feedback"]:
        st.info(session["feedback"])

    attempted = len(session["results"])
    st.caption(f"Accuracy so far: {session['correct']} / {attempted}")


def render_pronunciation_studio() -> None:
    st.subheader("Pronunciation Studio")
    st.write("Hear the phrase, then say it out loud to practice your accent.")
    examples = [sentence["spanish"] for sentence in SENTENCES]
    chosen = st.selectbox("Choose a phrase to practice", examples)
    custom = st.text_input("Or type your own phrase")
    phrase = custom.strip() or chosen
    payload = json.dumps(phrase)
    components.html(
        f"""
        <div style="display:flex; gap:12px; align-items:center; padding:8px 0;">
            <button style="padding:8px 14px; border-radius:10px; border:1px solid #cbd5f5; background:#fff;">
                🎧 Play pronunciation
            </button>
            <span style="color:#475569; font-size:14px;">Use your microphone locally to repeat it.</span>
        </div>
        <script>
            const button = document.currentScript.previousElementSibling.querySelector('button');
            button.addEventListener('click', () => {{
                const text = {payload};
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'es-ES';
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            }});
        </script>
        """,
        height=70,
    )
    st.markdown("##### Voice mode")
    render_voice_practice(phrase, "pronunciation-studio", phrase)


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
    persist_profile_state()


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


def render_library() -> None:
    st.subheader("Skill Library")
    st.write("Pick a focus area or jump into a custom practice session.")
    topics = sorted({item.topic for item in VOCAB})
    selected_topics = st.multiselect("Focus topics", topics, default=topics[:2])
    level = st.selectbox("Target level", ["Adaptive", "A1", "A2", "B1", "B2", "C1"], index=1)
    if st.button("Generate custom practice"):
        st.session_state.focus["topics"] = selected_topics
        st.session_state.focus["level"] = level
        learn_session = st.session_state.sessions["learn"]
        learn_session.update(default_session_state())
        learn_session["lesson_id"] = "custom"
        learn_session["exercises"] = make_exercises(
            lesson_id=LESSONS[0]["id"],
            difficulty=level,
            variety=[
                "multiple_choice",
                "fill_blank",
                "translate",
                "word_order",
                "listening",
                "listening_type",
                "dialogue",
                "cloze",
            ],
            topics_override=selected_topics or LESSONS[0]["topics"],
        )
        persist_profile_state()
        st.success("Custom practice loaded. Go to Learn tab to start.")


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
        "listening",
        "listening_type",
        "match",
        "dialogue",
        "cloze",
        "conversation",
        "word_order",
        "sentence_build",
    ]
    default_options = [
        "multiple_choice",
        "fill_blank",
        "translate",
        "listening",
        "listening_type",
        "dialogue",
        "cloze",
        "conversation",
        "word_order",
    ]
    variety = st.multiselect("Choose exercise types", options, default=default_options)
    st.markdown("### Coaching Tips")
    st.info("Mix practice modes daily. Short, frequent sessions help retention.")
    persist_profile_state()
    return {"difficulty": profile["level"], "variety": variety}


def main() -> None:
    set_theme()
    init_state()

    top_left, top_right = st.columns([2.2, 1])
    with top_left:
        render_hero()
        st.write("")
        render_stats()
    with top_right:
        render_auth_panel()

    tabs = st.tabs(["Learn", "Practice", "Progress", "Library", "Insights", "Downloads", "Settings"])
    with tabs[0]:
        st.markdown("### Choose a lesson")
        learn_session = st.session_state.sessions["learn"]
        selected = learn_session.get("lesson_id")
        selected = render_lesson_cards(selected)
        if selected:
            if selected != learn_session.get("lesson_id"):
                learn_session.update(default_session_state())
                learn_session["lesson_id"] = selected
        st.markdown("---")
        if learn_session.get("lesson_id"):
            settings = {
                "difficulty": st.session_state.profile["level"],
                "variety": st.session_state.get("variety", ["multiple_choice", "fill_blank", "translate"]),
            }
            render_session(learn_session["lesson_id"], settings, "learn")
    with tabs[1]:
        st.markdown("### Adaptive practice")
        settings = {
            "difficulty": st.session_state.profile["level"],
            "variety": st.session_state.get("variety", ["multiple_choice", "fill_blank", "translate"]),
        }
        if st.button("Start adaptive practice"):
            practice_session = st.session_state.sessions["practice"]
            practice_session.update(default_session_state())
            practice_session["lesson_id"] = LESSONS[0]["id"]
            practice_session["exercises"] = make_exercises(
                lesson_id=LESSONS[0]["id"],
                difficulty=settings["difficulty"],
                variety=settings["variety"],
            )
            st.session_state.session["index"] = 0
        if st.session_state.session.get("lesson_id"):
            render_session(st.session_state.session["lesson_id"], settings, "practice")
        st.markdown("---")
        render_pronunciation_studio()
    with tabs[2]:
        render_progress()
    with tabs[3]:
        render_library()
    with tabs[4]:
        render_insights()
    with tabs[5]:
        render_downloads()
    with tabs[6]:
        settings = render_settings()
        st.session_state.variety = settings["variety"]


if __name__ == "__main__":
    main()
