import difflib
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


DATA_DIR = Path("data")
PORTFOLIO_PATH = DATA_DIR / "portfolio.json"


@dataclass(frozen=True)
class DiagnosticIssue:
    area: str
    pattern: str
    impact: str
    example: str
    fix: str


DIAGNOSTIC_AREAS = [
    "Collocations",
    "Prepositions",
    "Discourse markers",
    "Register & tone",
    "Nuance & pragmatics",
]

DIAGNOSTIC_ISSUES = [
    DiagnosticIssue(
        "Collocations",
        "hacer una decisión",
        "Sounds literal; native usage prefers a different verb.",
        "Tomamos una decisión informada después del informe.",
        "Swap to 'tomar una decisión'.",
    ),
    DiagnosticIssue(
        "Collocations",
        "gran cantidad de gente",
        "Natural but heavy; try more precise nouns.",
        "Había una multitud en la plaza.",
        "Use 'multitud' or 'afluencia'.",
    ),
    DiagnosticIssue(
        "Prepositions",
        "depender en",
        "Preposition mismatch; register error.",
        "Depende de la disponibilidad del equipo.",
        "Use 'depender de'.",
    ),
    DiagnosticIssue(
        "Prepositions",
        "casarse con vs casarse de",
        "Regional mismatch.",
        "Se casó con su pareja en junio.",
        "Use 'casarse con'.",
    ),
    DiagnosticIssue(
        "Discourse markers",
        "por otro lado (without contrast)",
        "Connector doesn't match logic.",
        "Por otro lado, los datos confirman la tendencia.",
        "Use 'además' if additive.",
    ),
    DiagnosticIssue(
        "Discourse markers",
        "sin embargo + clause without contrast",
        "Creates incoherence.",
        "Sin embargo, los resultados fueron positivos.",
        "Use only with contrastive content.",
    ),
    DiagnosticIssue(
        "Register & tone",
        "tú in formal email",
        "Inappropriate level of formality.",
        "Le agradecería una respuesta antes del viernes.",
        "Maintain 'usted' and honorifics.",
    ),
    DiagnosticIssue(
        "Register & tone",
        "overly direct request",
        "Politeness strategies missing.",
        "¿Sería posible ajustar la fecha?",
        "Add hedging and modal verbs.",
    ),
    DiagnosticIssue(
        "Nuance & pragmatics",
        "literal translation of idioms",
        "Feels calqued and non-native.",
        "Me dio la impresión de que no estaban listos.",
        "Replace with natural phraseology.",
    ),
    DiagnosticIssue(
        "Nuance & pragmatics",
        "missing mitigation",
        "Sounds abrupt or face-threatening.",
        "Quizá podríamos revisar otra opción.",
        "Add softeners + hedging.",
    ),
]

TRAINING_PLAN = {
    "Collocations": [
        "Daily collocation micro-drills (verb-noun & adjective-noun).",
        "Shadow 10 native corpus sentences and rewrite with variants.",
    ],
    "Prepositions": [
        "Contrastive pairs drill (a/de/en/por/para).",
        "Record yourself using 5 preposition-dependent verbs.",
    ],
    "Discourse markers": [
        "Map argument flow with connectors per paragraph.",
        "Swap connectors to test semantic alignment.",
    ],
    "Register & tone": [
        "Rewrite the same prompt in 5 registers weekly.",
        "Score politeness strategies and hedging density.",
    ],
    "Nuance & pragmatics": [
        "Collect 3 softeners per week and use them in dialogue.",
        "Track irony/contrast markers in listening samples.",
    ],
}

REGISTER_STYLES = [
    "Informal WhatsApp",
    "Workplace email",
    "Academic abstract",
    "Polite complaint",
    "Persuasive pitch",
]

RUBRIC_DIMENSIONS = [
    "Politeness strategies",
    "Hedging",
    "Directness",
    "Idiomaticity",
    "Audience fit",
]

REGISTER_MARKERS = {
    "politeness": ["por favor", "le agradecería", "quisiera", "sería posible", "disculpe"],
    "hedging": ["quizá", "tal vez", "podría", "sería", "me parece"],
    "direct": ["necesito", "exijo", "debe", "quiero"],
    "idiomatic": ["me da la impresión", "en pocas palabras", "a fin de cuentas", "de hecho"],
    "academic": ["objetivo", "metodología", "resultados", "conclusión", "se analiza"],
    "whatsapp": ["jaja", "qué tal", "oye", "vale", "👍"],
    "pitch": ["propuesta", "impacto", "beneficio", "valor", "oportunidad"],
}

PRONUNCIATION_TARGETS = [
    {
        "phrase": "Me da la impresión de que podríamos ajustar el plan.",
        "focus": ["stress placement", "linking", "intonation (contrast)"],
        "notes": "Focus on rising-falling contour across the contrastive clause.",
    },
    {
        "phrase": "¿Te parece si lo revisamos mañana por la tarde?",
        "focus": ["rhythm", "question contour", "softening"],
        "notes": "Keep the rhythm even; lift pitch on the final question.",
    },
    {
        "phrase": "No es que no quiera, es que no llego a tiempo.",
        "focus": ["stress", "contrast", "intonation (irony)"],
        "notes": "Contrast the clauses with a clear pause and pitch reset.",
    },
]

COLLOCATION_SETS = [
    {
        "pair": "tomar una decisión",
        "type": "verb-noun",
        "frame": "Después de analizar los datos, ___ una decisión.",
        "options": ["tomamos", "hacemos"],
        "native": "tomamos",
        "rewrite": "Tomamos una decisión informada tras el informe.",
    },
    {
        "pair": "alto nivel de",
        "type": "adjective-noun",
        "frame": "El proyecto exige un ___ compromiso.",
        "options": ["alto", "elevado"],
        "native": "alto",
        "rewrite": "El proyecto exige un alto nivel de compromiso.",
    },
    {
        "pair": "me da la impresión de que",
        "type": "fixed phrase",
        "frame": "___ no estaban listos para el cambio.",
        "options": ["Me da la impresión de que", "Me hace pensar que"],
        "native": "Me da la impresión de que",
        "rewrite": "Me da la impresión de que el equipo necesita más tiempo.",
    },
]

CONVERSATION_SCENARIOS = [
    {
        "title": "Negotiating scope creep",
        "roles": "You are a product lead; the client wants more features without timeline changes.",
        "constraints": [
            "Use 3 concessive structures (aunque, si bien, a pesar de).",
            "Maintain formal usted throughout.",
            "Avoid English-like calques.",
        ],
    },
    {
        "title": "Soft disagreement in a meeting",
        "roles": "You disagree with a peer but need to keep collaboration.",
        "constraints": [
            "Include 2 softeners (quizá, me parece, tal vez).",
            "Use one redirecting phrase (en todo caso, de todos modos).",
        ],
    },
]

WRITING_GUIDE = [
    {
        "pattern": "muy importante",
        "replacement": "crucial",
        "category": "lexical choice",
        "reason": "Increase lexical sophistication.",
    },
    {
        "pattern": "pienso que",
        "replacement": "considero que",
        "category": "register",
        "reason": "More formal stance marker.",
    },
    {
        "pattern": "pero",
        "replacement": "sin embargo",
        "category": "cohesion",
        "reason": "Stronger discourse connector.",
    },
]

ARGUMENTATION_TOPICS = [
    "La inteligencia artificial en la educación superior",
    "Teletrabajo y productividad en empresas globales",
    "Políticas de movilidad urbana sostenible",
]

DIALECT_MODULES = {
    "Spain": {
        "features": ["distinción /θ/ vs /s/", "leísmo moderado", "tú predominante"],
        "lexicon": {"ordenador": "computer", "coger": "to take", "vale": "okay"},
        "sample": "Vale, luego te llamo para concretar los detalles.",
        "trap": {
            "question": "¿Qué matiz tiene 'vale' aquí?",
            "options": ["confirmación informal", "desacuerdo", "sorpresa"],
            "answer": "confirmación informal",
        },
    },
    "Mexico": {
        "features": ["seseo", "ustedes generalizado", "diminutivos frecuentes"],
        "lexicon": {"computadora": "computer", "platicar": "to chat", "ahorita": "soon-ish"},
        "sample": "Ahorita lo revisamos y te aviso.",
        "trap": {
            "question": "¿Qué implica 'ahorita' en este contexto?",
            "options": ["inmediatamente", "pronto, pero flexible", "mañana"],
            "answer": "pronto, pero flexible",
        },
    },
    "River Plate": {
        "features": ["voseo", "entonación rioplatense", "yeísmo rehilado"],
        "lexicon": {"vos": "you", "laburo": "work", "che": "hey"},
        "sample": "Che, ¿vos venís a la reunión o laburás desde casa?",
        "trap": {
            "question": "¿Qué marca el uso de 'vos'?",
            "options": ["voseo", "formalidad", "plural"],
            "answer": "voseo",
        },
    },
    "Caribbean": {
        "features": ["aspiration of /s/", "fast rhythm", "tuteo predominante"],
        "lexicon": {"guagua": "bus", "china": "orange", "chévere": "cool"},
        "sample": "La guagua viene llena, pero está chévere el plan.",
        "trap": {
            "question": "¿Qué significa 'chévere' aquí?",
            "options": ["molesto", "agradable", "lento"],
            "answer": "agradable",
        },
    },
    "Andes": {
        "features": ["intonation rise", "use of 'pues'", "leísmo parcial"],
        "lexicon": {"chompa": "sweater", "anticucho": "street food", "pues": "emphasis"},
        "sample": "Sí, pues, mañana nos vemos temprano.",
        "trap": {
            "question": "¿Qué función cumple 'pues'?",
            "options": ["énfasis", "negación", "finalizar"],
            "answer": "énfasis",
        },
    },
}

LISTENING_SCENARIOS = [
    {
        "title": "Fast overlap meeting",
        "audio": "Bueno, sí, pero—no, espera, lo que digo es que el cliente quiere otra cosa.",
        "tasks": [
            {
                "question": "¿Qué cambió de postura la persona?",
                "options": [
                    "Se contradijo y reformuló.",
                    "Aceptó la propuesta sin reservas.",
                    "Se negó a hablar.",
                ],
                "answer": "Se contradijo y reformuló.",
            },
            {
                "question": "Identifica un suavizador.",
                "options": ["bueno", "espera", "cliente"],
                "answer": "bueno",
            },
        ],
    },
    {
        "title": "Street interview",
        "audio": "Pues, la verdad, no sé, como que al final me convencieron.",
        "tasks": [
            {
                "question": "¿Qué implica 'como que'?",
                "options": ["hedging", "certeza", "ironía"],
                "answer": "hedging",
            }
        ],
    },
]

PORTFOLIO_AXES = [
    "Lexical sophistication",
    "Collocation accuracy",
    "Pragmatic appropriateness",
    "Prosody",
    "Cohesion",
]


def set_theme() -> None:
    st.set_page_config(page_title="VivaLingo Pro", page_icon="🗣️", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --primary: #1f3a8a;
            --secondary: #38bdf8;
            --accent: #f97316;
            --surface: #ffffff;
            --surface-muted: #f8fafc;
            --ink: #0f172a;
            --muted: #64748b;
            --border: rgba(148, 163, 184, 0.3);
        }
        .stApp {
            background: radial-gradient(circle at top left, #e0f2fe 0%, #f8fafc 45%, #ecfeff 100%);
            color: var(--ink);
            font-family: "Inter", "SF Pro Text", "Segoe UI", system-ui, -apple-system, sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--ink);
        }
        .hero {
            padding: 2.2rem;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(31, 58, 138, 0.92), rgba(56, 189, 248, 0.9));
            color: #fff;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.16);
        }
        .hero p {
            color: rgba(255, 255, 255, 0.85);
            font-size: 1.05rem;
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            font-weight: 600;
            margin-right: 0.4rem;
        }
        .card {
            padding: 1.4rem;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
        }
        .card-muted {
            padding: 1.2rem;
            border-radius: 18px;
            border: 1px dashed rgba(148, 163, 184, 0.6);
            background: var(--surface-muted);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .wave-box {
            border-radius: 18px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1rem;
        }
        .shadow-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.2);
            color: #0c4a6e;
            font-weight: 600;
            margin-right: 0.4rem;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "level": "C1",
            "weekly_goal": 6,
            "last_gap_week": None,
        }
    if "gap_results" not in st.session_state:
        st.session_state.gap_results = []
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = load_portfolio()
    if "writing_analysis" not in st.session_state:
        st.session_state.writing_analysis = {"draft": "", "edits": []}


def load_portfolio() -> dict:
    if not PORTFOLIO_PATH.exists():
        return {
            "writing_samples": [],
            "recordings": [],
            "transcripts": [],
            "benchmarks": [],
        }
    return json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))


def save_portfolio() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_PATH.write_text(json.dumps(st.session_state.portfolio, indent=2), encoding="utf-8")


def seed_for_week(week: date, name: str) -> int:
    base = f"{week.isoformat()}:{name}"
    return int(hashlib.sha256(base.encode("utf-8")).hexdigest()[:8], 16)


def generate_gap_results(scores: dict[str, int]) -> list[DiagnosticIssue]:
    weights = {
        issue: (6 - scores.get(issue.area, 3)) * random.uniform(0.8, 1.2)
        for issue in DIAGNOSTIC_ISSUES
    }
    ranked = sorted(DIAGNOSTIC_ISSUES, key=lambda issue: weights[issue], reverse=True)
    return ranked[:20]


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div>
                <span class="pill">C1–C2 Diagnostics</span>
                <span class="pill">Prosody Coach</span>
                <span class="pill">Native Corpus</span>
            </div>
            <h1>VivaLingo Pro: Spanish Mastery Lab</h1>
            <p>Train nuance, register, collocation accuracy, and real-world fluency with adaptive diagnostics and
            portfolio-ready evidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile_sidebar() -> None:
    st.sidebar.header("Learner Profile")
    profile = st.session_state.profile
    profile["name"] = st.sidebar.text_input("Name", value=profile["name"], placeholder="Your name")
    profile["level"] = st.sidebar.selectbox("Target level", ["C1", "C2"], index=0)
    profile["weekly_goal"] = st.sidebar.slider("Weekly sessions", 2, 10, profile["weekly_goal"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")


def render_gap_finder() -> None:
    st.header("1. Real-time gap-finder diagnostics")
    st.write("Weekly adaptive tests targeting collocations, prepositions, discourse markers, register, and nuance.")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        week = st.date_input("Week of", value=date.today())
        st.caption("Diagnostics adapt weekly to C1–C2 micro-skills.")
        scores = {}
        for area in DIAGNOSTIC_AREAS:
            scores[area] = st.slider(f"Self-assess {area}", 1, 5, 3)
    with col2:
        st.markdown("#### Diagnostic Focus")
        st.markdown("- Collocation strength\n- Preposition precision\n- Discourse cohesion\n- Register control\n- Pragmatic nuance")
        run = st.button("Run adaptive diagnostics")

    if run:
        random.seed(seed_for_week(week, st.session_state.profile["name"]))
        st.session_state.gap_results = generate_gap_results(scores)
        st.session_state.profile["last_gap_week"] = week.isoformat()

    if st.session_state.gap_results:
        st.subheader("Error Top 20")
        table = [
            {
                "Rank": idx + 1,
                "Area": issue.area,
                "Pattern": issue.pattern,
                "Impact": issue.impact,
                "Native corpus example": issue.example,
                "Fix": issue.fix,
            }
            for idx, issue in enumerate(st.session_state.gap_results)
        ]
        st.dataframe(table, use_container_width=True)

        st.subheader("Personalized training plan")
        for area in DIAGNOSTIC_AREAS:
            st.markdown(f"**{area}**")
            for item in TRAINING_PLAN[area]:
                st.markdown(f"- {item}")


def score_register_response(text: str, style: str) -> dict[str, int]:
    lowered = text.lower()
    scores = {dim: 2 for dim in RUBRIC_DIMENSIONS}
    if any(marker in lowered for marker in REGISTER_MARKERS["politeness"]):
        scores["Politeness strategies"] += 2
    if any(marker in lowered for marker in REGISTER_MARKERS["hedging"]):
        scores["Hedging"] += 2
    if any(marker in lowered for marker in REGISTER_MARKERS["direct"]):
        scores["Directness"] += 1
    if any(marker in lowered for marker in REGISTER_MARKERS["idiomatic"]):
        scores["Idiomaticity"] += 2
    if style == "Academic abstract" and any(marker in lowered for marker in REGISTER_MARKERS["academic"]):
        scores["Audience fit"] += 3
    if style == "Informal WhatsApp" and any(marker in lowered for marker in REGISTER_MARKERS["whatsapp"]):
        scores["Audience fit"] += 3
    if style == "Persuasive pitch" and any(marker in lowered for marker in REGISTER_MARKERS["pitch"]):
        scores["Audience fit"] += 3
    if len(text.split()) > 55:
        scores["Directness"] += 1
    return {k: min(v, 5) for k, v in scores.items()}


def render_register_simulator() -> None:
    st.header("2. Register & tone mastery simulator")
    prompt = st.text_area(
        "Scenario prompt",
        value="You need to convince a skeptical team to adopt a new workflow.",
        height=90,
    )

    responses = {}
    for style in REGISTER_STYLES:
        responses[style] = st.text_area(f"{style} response", key=f"register-{style}")

    if st.button("Score responses"):
        rows = []
        for style, text in responses.items():
            scores = score_register_response(text, style)
            rows.append({"Register": style, **scores})
        st.dataframe(rows, use_container_width=True)
        st.markdown("**Rubric guidance**")
        st.markdown(
            "- *Politeness strategies*: modals, gratitude, deference.\n"
            "- *Hedging*: quizá, tal vez, me parece.\n"
            "- *Directness*: strong imperatives lower score in formal contexts.\n"
            "- *Idiomaticity*: natural phraseology and discourse frames.\n"
            "- *Audience fit*: match lexical density and formality to register."
        )


def render_pronunciation_coach() -> None:
    st.header("3. High-precision pronunciation & prosody coach")
    target = st.selectbox("Shadowing prompt", [item["phrase"] for item in PRONUNCIATION_TARGETS])
    details = next(item for item in PRONUNCIATION_TARGETS if item["phrase"] == target)
    st.markdown("**Focus areas:** " + ", ".join(details["focus"]))
    st.info(details["notes"])

    phrase_chunks = [chunk.strip() for chunk in target.split(",") if chunk.strip()]
    st.markdown("#### Shadowing mode")
    loop_count = st.slider("Replay loops", 1, 5, 2)

    components.html(
        f"""
        <div class="wave-box">
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
                {''.join([f'<span class="shadow-pill">{chunk}</span>' for chunk in phrase_chunks])}
            </div>
            <svg width="100%" height="120" viewBox="0 0 600 120" preserveAspectRatio="none">
                <polyline fill="none" stroke="#38bdf8" stroke-width="3"
                    points="0,60 40,55 80,70 120,40 160,60 200,30 240,65 280,50 320,80 360,55 400,65 440,35 480,60 520,45 560,70 600,50" />
                <polyline fill="none" stroke="#f97316" stroke-width="2" stroke-dasharray="6 4"
                    points="0,90 40,85 80,95 120,70 160,85 200,65 240,92 280,75 320,100 360,80 400,88 440,70 480,85 520,78 560,92 600,80" />
            </svg>
            <div style="font-size:12px; color:#64748b;">Waveform (blue) & pitch track (orange)</div>
            <button id="shadow-play" style="margin-top:8px; padding:8px 12px; border-radius:8px; border:1px solid #cbd5f5;">▶️ Play & loop</button>
            <div id="shadow-status" style="margin-top:6px; font-size:13px; color:#0f172a;"></div>
        </div>
        <script>
            const button = document.getElementById('shadow-play');
            const status = document.getElementById('shadow-status');
            const utteranceText = {json.dumps(target)};
            const loops = {loop_count};
            button.onclick = () => {{
                let count = 0;
                status.textContent = `Loop 1 / ${loops}`;
                const speakOnce = () => {{
                    const utterance = new SpeechSynthesisUtterance(utteranceText);
                    utterance.lang = 'es-ES';
                    utterance.onend = () => {{
                        count += 1;
                        if (count < loops) {{
                            status.textContent = `Loop ${count + 1} / ${loops}`;
                            speakOnce();
                        }} else {{
                            status.textContent = 'Done. Replay to continue shadowing.';
                        }}
                    }};
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }};
                speakOnce();
            }};
        </script>
        """,
        height=280,
    )


def render_collocation_engine() -> None:
    st.header("4. Native-corpus collocation engine")
    tabs = st.tabs(["Choose-the-more-native", "Rewrite to sound native", "Collocation completion"])

    with tabs[0]:
        item = random.choice(COLLOCATION_SETS)
        st.markdown(f"**{item['pair']}** ({item['type']})")
        choice = st.radio("Which is more native?", item["options"], key="collocation-choice")
        if st.button("Check", key="collocation-check"):
            st.success("Correct!" if choice == item["native"] else "Not quite.")
            st.caption(f"Native choice: {item['native']} • Example: {item['rewrite']}")

    with tabs[1]:
        item = random.choice(COLLOCATION_SETS)
        st.markdown(f"Rewrite using: **{item['pair']}**")
        rewrite = st.text_area("Your rewrite", value="", key="rewrite-native")
        if st.button("Show model", key="rewrite-show"):
            st.info(item["rewrite"])
            st.caption("Compare rhythm, verb choice, and fixed frames.")

    with tabs[2]:
        item = random.choice(COLLOCATION_SETS)
        st.markdown(item["frame"])
        completion = st.text_input("Fill in the blank", key="collocation-fill")
        if st.button("Reveal", key="collocation-reveal"):
            st.success(f"Suggested: {item['native']}")
            st.caption(f"Full example: {item['rewrite']}")


def analyze_constraints(response: str, constraints: list[str]) -> dict[str, bool]:
    lowered = response.lower()
    results = {}
    concessives = ["aunque", "si bien", "a pesar de", "no obstante"]
    softeners = ["quizá", "tal vez", "me parece", "podría"]
    redirect = ["en todo caso", "de todos modos", "en cualquier caso"]

    for constraint in constraints:
        if "concessive" in constraint.lower():
            results[constraint] = sum(phrase in lowered for phrase in concessives) >= 3
        elif "softeners" in constraint.lower():
            results[constraint] = sum(phrase in lowered for phrase in softeners) >= 2
        elif "redirecting" in constraint.lower():
            results[constraint] = any(phrase in lowered for phrase in redirect)
        elif "formal usted" in constraint.lower():
            results[constraint] = "usted" in lowered or "su " in lowered
        elif "Avoid English-like calques" in constraint:
            results[constraint] = "aplicar para" not in lowered
        else:
            results[constraint] = False
    return results


def render_conversation_lab() -> None:
    st.header("5. Advanced conversation lab with constraints")
    scenario = st.selectbox("Choose a roleplay", [s["title"] for s in CONVERSATION_SCENARIOS])
    selected = next(s for s in CONVERSATION_SCENARIOS if s["title"] == scenario)

    st.markdown("**Roleplay brief**")
    st.write(selected["roles"])
    st.markdown("**Constraints**")
    for constraint in selected["constraints"]:
        st.markdown(f"- {constraint}")

    response = st.text_area("Your response", height=160, key="conversation-response")
    if st.button("Evaluate constraints"):
        checks = analyze_constraints(response, selected["constraints"])
        for constraint, passed in checks.items():
            st.write(f"{'✅' if passed else '❌'} {constraint}")
        score = sum(checks.values()) / max(len(checks), 1)
        st.metric("Constraint completion", f"{score:.0%}")
        st.caption("Improve by weaving softeners, concessions, and register markers.")


def generate_edit_trail(text: str) -> list[dict]:
    edits = []
    for guide in WRITING_GUIDE:
        if guide["pattern"] in text:
            edited = text.replace(guide["pattern"], guide["replacement"])
            edits.append(
                {
                    "before": guide["pattern"],
                    "after": guide["replacement"],
                    "category": guide["category"],
                    "reason": guide["reason"],
                    "preview": edited,
                }
            )
    if not edits and text:
        edits.append(
            {
                "before": "(sentence cohesion)",
                "after": "Add connector: sin embargo",
                "category": "cohesion",
                "reason": "Improve logical flow between sentences.",
                "preview": text,
            }
        )
    return edits


def render_writing_studio() -> None:
    st.header("6. Error-aware writing studio with edit trails")
    st.write("Write 300–1000 words and receive line edits with reasoning categories.")
    draft = st.text_area("Your draft", height=220, key="writing-draft")

    if st.button("Analyze writing"):
        st.session_state.writing_analysis = {
            "draft": draft,
            "edits": generate_edit_trail(draft),
        }

    if st.session_state.writing_analysis["draft"]:
        edits = st.session_state.writing_analysis["edits"]
        st.subheader("Line edits")
        st.dataframe(
            [
                {
                    "Before": edit["before"],
                    "After": edit["after"],
                    "Category": edit["category"],
                    "Reason": edit["reason"],
                }
                for edit in edits
            ],
            use_container_width=True,
        )
        if edits:
            diff = "\n".join(
                difflib.unified_diff(
                    st.session_state.writing_analysis["draft"].splitlines(),
                    edits[0]["preview"].splitlines(),
                    fromfile="before",
                    tofile="after",
                    lineterm="",
                )
            )
            st.subheader("Before/after diff")
            st.code(diff or "(No diff produced)")

        deck = {}
        for edit in edits:
            deck[edit["category"]] = deck.get(edit["category"], 0) + 1
        st.subheader("Spaced repetition deck")
        st.write(
            [
                {"Category": category, "Cards": count}
                for category, count in deck.items()
            ]
        )

        if st.session_state.writing_analysis["draft"].strip():
            if st.button("Save to portfolio"):
                st.session_state.portfolio["writing_samples"].append(
                    {
                        "date": date.today().isoformat(),
                        "text": st.session_state.writing_analysis["draft"],
                    }
                )
                save_portfolio()
                st.success("Saved to portfolio.")


def render_argumentation_drills() -> None:
    st.header("7. Argumentation & rhetoric drills")
    topic = st.selectbox("Choose a topic", ARGUMENTATION_TOPICS)
    st.write("Build a thesis, counterargument, concession, and conclusion using discourse connectors.")

    thesis = st.text_input("Thesis")
    counter = st.text_input("Counterargument")
    concession = st.text_input("Concession")
    conclusion = st.text_input("Conclusion")

    if st.button("Evaluate structure"):
        connector_count = sum(
            phrase in " ".join([thesis, counter, concession, conclusion]).lower()
            for phrase in ["por lo tanto", "sin embargo", "no obstante", "además", "en conclusión"]
        )
        length_score = sum(len(part.split()) > 6 for part in [thesis, counter, concession, conclusion])
        score = (connector_count + length_score) / 10
        st.metric("Argumentation score", f"{score:.0%}")
        st.caption("Improve cohesion by adding explicit stance markers and connectors.")


def render_dialect_tuning() -> None:
    st.header("8. Dialect & regional Spanish tuning")
    dialect = st.selectbox("Select region", list(DIALECT_MODULES.keys()))
    data = DIALECT_MODULES[dialect]

    st.markdown("**Core features**")
    st.write(", ".join(data["features"]))
    st.markdown("**Key lexicon**")
    st.table([{"Term": k, "Meaning": v} for k, v in data["lexicon"].items()])

    st.markdown("**Listening: same content across dialects**")
    for name, variant in DIALECT_MODULES.items():
        with st.expander(f"{name} variant"):
            st.write(variant["sample"])
            components.html(
                f"""
                <button id="dialect-{name}" style="padding:6px 10px; border-radius:8px; border:1px solid #cbd5f5;">🔊 Play</button>
                <script>
                    const btn = document.getElementById('dialect-{name}');
                    btn.onclick = () => {{
                        const utterance = new SpeechSynthesisUtterance({json.dumps(variant['sample'])});
                        utterance.lang = 'es-ES';
                        window.speechSynthesis.cancel();
                        window.speechSynthesis.speak(utterance);
                    }};
                </script>
                """,
                height=60,
            )

    st.markdown("**Comprehension trap**")
    trap = data["trap"]
    answer = st.radio(trap["question"], trap["options"], key="dialect-trap")
    if st.button("Check trap"):
        st.success("Correct!" if answer == trap["answer"] else "Try again.")


def render_listening_nuance() -> None:
    st.header("9. Listening for nuance: fast, messy, real")
    scenario_title = st.selectbox("Choose a scenario", [s["title"] for s in LISTENING_SCENARIOS])
    scenario = next(s for s in LISTENING_SCENARIOS if s["title"] == scenario_title)
    st.write(scenario["audio"])

    components.html(
        f"""
        <button id="nuance-audio" style="padding:6px 10px; border-radius:8px; border:1px solid #cbd5f5;">🔊 Play sample</button>
        <script>
            const btn = document.getElementById('nuance-audio');
            btn.onclick = () => {{
                const utterance = new SpeechSynthesisUtterance({json.dumps(scenario['audio'])});
                utterance.lang = 'es-ES';
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            }};
        </script>
        """,
        height=60,
    )

    for idx, task in enumerate(scenario["tasks"]):
        choice = st.radio(task["question"], task["options"], key=f"nuance-{idx}")
        if st.button("Reveal", key=f"nuance-reveal-{idx}"):
            st.info(f"Answer: {task['answer']}")


def render_portfolio() -> None:
    st.header("10. Native-likeness benchmark & portfolio")
    st.write("Track progress across measurable axes and export your evidence.")

    axis_scores = {}
    for axis in PORTFOLIO_AXES:
        axis_scores[axis] = st.slider(axis, 1, 10, 6)

    if st.button("Save benchmark"):
        st.session_state.portfolio["benchmarks"].append(
            {"date": date.today().isoformat(), "scores": axis_scores}
        )
        save_portfolio()
        st.success("Benchmark saved.")

    if st.session_state.portfolio["benchmarks"]:
        st.subheader("Benchmark history")
        st.dataframe(st.session_state.portfolio["benchmarks"], use_container_width=True)

    st.subheader("Portfolio artifacts")
    st.write(f"Writing samples: {len(st.session_state.portfolio['writing_samples'])}")
    st.write(f"Recordings: {len(st.session_state.portfolio['recordings'])}")
    st.write(f"Conversation transcripts: {len(st.session_state.portfolio['transcripts'])}")

    if st.session_state.portfolio["writing_samples"]:
        st.markdown("**Latest writing sample**")
        st.text_area(
            "",
            value=st.session_state.portfolio["writing_samples"][-1]["text"],
            height=160,
            disabled=True,
        )

    export = json.dumps(st.session_state.portfolio, indent=2)
    st.download_button("Download portfolio JSON", data=export, file_name="vivalingo_portfolio.json")


def render_overview() -> None:
    st.header("Program Overview")
    st.write(
        "This lab integrates diagnostics, register calibration, prosody coaching, collocation accuracy,"
        " and portfolio-grade evidence for advanced Spanish learners."
    )

    st.markdown(
        """
        <div class="metric-grid">
            <div class="card">
                <h3>Weekly Gap Finder</h3>
                <p>Adaptive C1–C2 diagnostics with ranked Error Top 20 and targeted training plan.</p>
            </div>
            <div class="card">
                <h3>Register Simulator</h3>
                <p>One prompt, five registers. Score politeness, hedging, directness, idiomaticity.</p>
            </div>
            <div class="card">
                <h3>Prosody Coach</h3>
                <p>Shadowing with waveform + pitch tracks and looped playback.</p>
            </div>
            <div class="card">
                <h3>Native Collocation Engine</h3>
                <p>Verb-noun pairs, fixed phrases, and corpus-based frames.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    set_theme()
    init_state()
    render_profile_sidebar()

    render_hero()
    st.write("")

    nav = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "Gap Finder",
            "Register Simulator",
            "Prosody Coach",
            "Collocation Engine",
            "Conversation Lab",
            "Writing Studio",
            "Argumentation",
            "Dialect Tuning",
            "Listening for Nuance",
            "Portfolio",
        ],
    )

    if nav == "Overview":
        render_overview()
    elif nav == "Gap Finder":
        render_gap_finder()
    elif nav == "Register Simulator":
        render_register_simulator()
    elif nav == "Prosody Coach":
        render_pronunciation_coach()
    elif nav == "Collocation Engine":
        render_collocation_engine()
    elif nav == "Conversation Lab":
        render_conversation_lab()
    elif nav == "Writing Studio":
        render_writing_studio()
    elif nav == "Argumentation":
        render_argumentation_drills()
    elif nav == "Dialect Tuning":
        render_dialect_tuning()
    elif nav == "Listening for Nuance":
        render_listening_nuance()
    elif nav == "Portfolio":
        render_portfolio()


if __name__ == "__main__":
    main()
