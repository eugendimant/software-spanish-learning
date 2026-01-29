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

ADAPTIVE_QUESTION_BANK = [
    {
        "id": "c1-coll-1",
        "level": "C1",
        "skill": "Collocations",
        "prompt": "Elige la opción más natural: \"___ una decisión informada\"",
        "options": ["Hacer", "Tomar", "Crear"],
        "answer": "Tomar",
        "explanation": "En español es más natural 'tomar una decisión'.",
    },
    {
        "id": "c1-discourse-1",
        "level": "C1",
        "skill": "Discourse markers",
        "prompt": "Completa con un conector adecuado: \"___, los datos sugieren un cambio estructural.\"",
        "options": ["Además", "Sin embargo", "Por eso"],
        "answer": "Además",
        "explanation": "El contexto es aditivo, no contrastivo.",
    },
    {
        "id": "c1-prep-1",
        "level": "C1",
        "skill": "Prepositions",
        "prompt": "Selecciona la preposición correcta: \"Depende ___ la estrategia.\"",
        "options": ["de", "en", "a"],
        "answer": "de",
        "explanation": "El verbo es 'depender de'.",
    },
    {
        "id": "c2-register-1",
        "level": "C2",
        "skill": "Register & tone",
        "prompt": "En un correo formal, ¿qué opción suena más adecuada?",
        "options": [
            "¿Puedes mandarme eso hoy?",
            "Le agradecería que me enviara el documento hoy.",
            "Mándame eso ya.",
        ],
        "answer": "Le agradecería que me enviara el documento hoy.",
        "explanation": "Incluye tratamiento formal y mitigación.",
    },
    {
        "id": "c2-nuance-1",
        "level": "C2",
        "skill": "Nuance & pragmatics",
        "prompt": "¿Qué reformulación suena más natural?",
        "options": [
            "Me dio la impresión de que no estaban listos.",
            "Me dio la sensación de que no estaban listos.",
            "Me dio el parecer de que no estaban listos.",
        ],
        "answer": "Me dio la impresión de que no estaban listos.",
        "explanation": "La fórmula 'me dio la impresión de que' es idiomática.",
    },
    {
        "id": "c2-discourse-2",
        "level": "C2",
        "skill": "Discourse markers",
        "prompt": "Selecciona el conector correcto: \"___, conviene matizar la hipótesis.\"",
        "options": ["No obstante", "Por ejemplo", "Mientras tanto"],
        "answer": "No obstante",
        "explanation": "Marca contraste o matización.",
    },
]

FOSSILIZED_ERRORS = [
    {
        "pattern": "aplicar para",
        "correction": "solicitar",
        "explanation": "Evita el calco 'aplicar para' en español formal.",
        "minimal_pairs": [
            ("Solicité el puesto ayer.", "Apliqué para el puesto ayer."),
            ("¿Has solicitado la beca?", "¿Has aplicado para la beca?"),
        ],
    },
    {
        "pattern": "realizar una decisión",
        "correction": "tomar una decisión",
        "explanation": "La colocación correcta es 'tomar una decisión'.",
        "minimal_pairs": [
            ("Tomamos una decisión informada.", "Realizamos una decisión informada."),
            ("Necesitamos tomar una decisión hoy.", "Necesitamos realizar una decisión hoy."),
        ],
    },
    {
        "pattern": "por otro lado" ,
        "correction": "además",
        "explanation": "Usa 'por otro lado' solo con contraste claro.",
        "minimal_pairs": [
            ("Además, el equipo ya validó el plan.", "Por otro lado, el equipo ya validó el plan."),
            ("Además, aumentó la demanda.", "Por otro lado, aumentó la demanda."),
        ],
    },
]

IDIOM_LIBRARY = [
    {
        "idiom": "estar en las nubes",
        "meaning": "estar distraído",
        "register": "informal",
        "safe_alternative": "estar distraído",
        "note": "Evita usarlo en contextos académicos muy formales.",
    },
    {
        "idiom": "poner el grito en el cielo",
        "meaning": "quejarse fuertemente",
        "register": "neutral",
        "safe_alternative": "quejarse con fuerza",
        "note": "Úsalo en contextos narrativos o coloquiales.",
    },
    {
        "idiom": "a grandes rasgos",
        "meaning": "en términos generales",
        "register": "formal",
        "safe_alternative": "en términos generales",
        "note": "Funciona bien en informes y presentaciones.",
    },
]

PRAGMATIC_SCENARIOS = [
    {
        "region": "Mexico",
        "situation": "Pedir un favor a un colega senior.",
        "prompt": "Selecciona la versión socialmente más adecuada:",
        "options": [
            "Oye, pásame el informe ya.",
            "¿Te molestaría compartirme el informe cuando tengas un momento?",
            "Mándame el informe ahora mismo.",
        ],
        "answer": "¿Te molestaría compartirme el informe cuando tengas un momento?",
        "feedback": "En México se valora la mitigación y los suavizadores en peticiones laborales.",
    },
    {
        "region": "Spain",
        "situation": "Rechazar una invitación informal.",
        "prompt": "Selecciona la versión más natural:",
        "options": [
            "No voy.",
            "Me encantaría, pero se me complica esta vez.",
            "No puedo asistir.",
        ],
        "answer": "Me encantaría, pero se me complica esta vez.",
        "feedback": "El rechazo suave con una razón breve es más natural en contexto informal.",
    },
]

DOMAIN_MODULES = {
    "Finance": {
        "collocations": ["gestionar riesgos", "flujo de caja", "rentabilidad ajustada"],
        "templates": ["Según el análisis, la liquidez se mantiene estable."],
        "false_friend": {
            "prompt": "¿Cuál es la traducción correcta de 'actual' en finanzas?",
            "options": ["actual", "real", "corriente"],
            "answer": "actual",
            "note": "En español financiero, 'actual' suele equivaler a current/present.",
        },
    },
    "Law": {
        "collocations": ["interponer un recurso", "marco normativo", "jurisprudencia vigente"],
        "templates": ["Conforme al marco normativo, procede la revisión del contrato."],
        "false_friend": {
            "prompt": "¿Cómo se traduce correctamente 'eventually' en textos jurídicos?",
            "options": ["eventualmente", "finalmente", "posiblemente"],
            "answer": "finalmente",
            "note": "\"Eventualmente\" en español significa \"ocasionalmente\".",
        },
    },
    "Medicine": {
        "collocations": ["presentar síntomas", "historia clínica", "alta médica"],
        "templates": ["La historia clínica indica antecedentes relevantes."],
        "false_friend": {
            "prompt": "¿Cuál es la traducción correcta de 'intoxication' en medicina?",
            "options": ["intoxicación", "embriaguez", "toxicidad"],
            "answer": "intoxicación",
            "note": "\"Intoxicación\" es el término estándar para poisoning.",
        },
    },
    "Academia": {
        "collocations": ["marco teórico", "diseño metodológico", "hallazgos clave"],
        "templates": ["El estudio se apoya en un marco teórico robusto."],
        "false_friend": {
            "prompt": "¿Cómo se traduce 'evidence' en un paper?",
            "options": ["evidencia", "prueba", "testimonio"],
            "answer": "evidencia",
            "note": "\"Evidencia\" es aceptado en academia, con matices según disciplina.",
        },
    },
    "Tech": {
        "collocations": ["escalabilidad del sistema", "arquitectura modular", "rendimiento óptimo"],
        "templates": ["La arquitectura modular facilita la escalabilidad."],
        "false_friend": {
            "prompt": "¿Cómo se traduce 'library' en software?",
            "options": ["biblioteca", "librería", "libro"],
            "answer": "librería",
            "note": "\"Librería\" es el uso estándar en tecnología.",
        },
    },
    "HR": {
        "collocations": ["gestión del talento", "clima laboral", "plan de carrera"],
        "templates": ["El plan de carrera mejora la retención del talento."],
        "false_friend": {
            "prompt": "¿Cómo se traduce correctamente 'actually' en una revisión?",
            "options": ["actualmente", "en realidad", "realmente"],
            "answer": "en realidad",
            "note": "\"Actually\" suele equivaler a \"en realidad\".",
        },
    },
}

IMMERSION_MODES = [
    {
        "label": "20-minute sprint",
        "duration": 20,
        "steps": [
            "Read a 300-word article and annotate discourse markers.",
            "Listen to a short debate clip and note stance markers.",
            "Summarize in 5 sentences using formal register.",
            "Rewrite in a stricter register with hedging.",
        ],
    },
    {
        "label": "40-minute deep dive",
        "duration": 40,
        "steps": [
            "Read a 600-word report and list 10 collocations.",
            "Listen to a panel discussion and identify softeners.",
            "Write a 150-word argument with concessions.",
            "Rewrite for a different audience (email vs abstract).",
        ],
    },
    {
        "label": "60-minute immersion",
        "duration": 60,
        "steps": [
            "Read a 900-word essay and map its rhetorical structure.",
            "Listen to a fast interview and capture implied meaning.",
            "Write a 250-word response with 5 discourse connectors.",
            "Rewrite into a formal complaint and then a pitch.",
        ],
    },
]

NAV_ITEMS = [
    "Overview",
    "Adaptive Assessment",
    "Gap Finder",
    "Register Simulator",
    "Prosody Coach",
    "Collocation Engine",
    "Conversation Lab",
    "Writing Studio",
    "Argumentation",
    "Dialect Tuning",
    "Listening for Nuance",
    "Fossilized Errors",
    "Idioms & Metaphor",
    "Cultural Pragmatics",
    "Domain Precision",
    "Immersion Mode",
    "Portfolio",
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
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
        .quick-card {
            border-radius: 18px;
            border: 1px solid var(--border);
            padding: 1rem;
            background: #fff;
        }
        .sidebar-header {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-top: 0.5rem;
        }
        section[data-testid="stSidebar"] .stButton button {
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, 0.4);
            background: #fff;
            font-weight: 600;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            border-color: rgba(56, 189, 248, 0.6);
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
    if "nav" not in st.session_state:
        st.session_state.nav = "Overview"
    if "assessment" not in st.session_state:
        st.session_state.assessment = {
            "active": False,
            "questions": [],
            "index": 0,
            "score": 0,
            "level": "C1",
            "missed_skills": {},
            "complete": False,
        }
    if "fossil_log" not in st.session_state:
        st.session_state.fossil_log = []
    if "fossil_stats" not in st.session_state:
        st.session_state.fossil_stats = {"attempts": 0, "correct": 0}
    if "immersion_notes" not in st.session_state:
        st.session_state.immersion_notes = ""


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


def set_nav(page: str) -> None:
    if page in NAV_ITEMS:
        st.session_state.nav = page


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
    st.sidebar.markdown("<div class='sidebar-header'>Navigation</div>", unsafe_allow_html=True)
    st.sidebar.caption(f"Current: {st.session_state.nav}")
    for item in NAV_ITEMS:
        if st.sidebar.button(item, key=f"nav-{item}", use_container_width=True):
            set_nav(item)


def render_adaptive_assessment() -> None:
    st.header("Adaptive placement test")
    st.write("Calibrate your level and generate a personalized plan based on real-time performance.")

    assessment = st.session_state.assessment

    if not assessment["active"]:
        if st.button("Start adaptive assessment"):
            assessment.update(
                {
                    "active": True,
                    "questions": [],
                    "index": 0,
                    "score": 0,
                    "level": st.session_state.profile["level"],
                    "missed_skills": {},
                    "complete": False,
                }
            )

    if not assessment["active"]:
        st.info("Start the assessment to begin adaptive questions.")
        return

    if assessment["complete"]:
        st.subheader("Placement result")
        estimated = assessment["level"]
        st.metric("Estimated level", estimated)
        missed = assessment["missed_skills"]
        if missed:
            sorted_skills = sorted(missed.items(), key=lambda item: item[1], reverse=True)
            st.markdown("**Top gaps to address next**")
            for skill, count in sorted_skills[:3]:
                st.write(f"- {skill} (missed {count} items)")
                for tip in TRAINING_PLAN.get(skill, []):
                    st.write(f"  - {tip}")
        st.success("Your personalized plan is ready. Use Gap Finder for weekly refinement.")
        if st.button("Restart assessment"):
            assessment["active"] = False
        return

    current_level = assessment["level"]
    candidates = [q for q in ADAPTIVE_QUESTION_BANK if q["level"] == current_level]
    if len(assessment["questions"]) < 8:
        remaining = [q for q in candidates if q["id"] not in assessment["questions"]]
        if not remaining:
            remaining = candidates
        chosen = random.choice(remaining)
        assessment["questions"].append(chosen["id"])
        question = chosen
    else:
        question_id = assessment["questions"][assessment["index"]]
        question = next(q for q in ADAPTIVE_QUESTION_BANK if q["id"] == question_id)

    st.subheader(f"Question {assessment['index'] + 1} of 8")
    st.write(question["prompt"])
    response = st.radio("Choose an answer", question["options"], key=f"adaptive-{assessment['index']}")

    if st.button("Submit answer"):
        correct = response == question["answer"]
        if correct:
            assessment["score"] += 1
            if current_level == "C1":
                assessment["level"] = "C2"
            st.success("Correct!")
        else:
            assessment["missed_skills"][question["skill"]] = assessment["missed_skills"].get(question["skill"], 0) + 1
            if current_level == "C2":
                assessment["level"] = "C1"
            st.error(f"Incorrect. {question['explanation']}")

        assessment["index"] += 1
        if assessment["index"] >= 8:
            assessment["complete"] = True
            assessment["active"] = True
            st.session_state.assessment = assessment
            st.experimental_rerun()


def render_gap_finder() -> None:
    st.header("Weekly gap-finder diagnostics")
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
    st.header("Register & tone mastery simulator")
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
    st.header("High-precision pronunciation & prosody coach")
    target = st.selectbox("Shadowing prompt", [item["phrase"] for item in PRONUNCIATION_TARGETS])
    details = next(item for item in PRONUNCIATION_TARGETS if item["phrase"] == target)
    st.markdown("**Focus areas:** " + ", ".join(details["focus"]))
    st.info(details["notes"])

    phrase_chunks = [chunk.strip() for chunk in target.split(",") if chunk.strip()]
    st.markdown("#### Shadowing mode")
    loop_count = st.slider("Replay loops", 1, 5, 2)

    loop_text = f"Loop 1 / {loop_count}"
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
            <div id="shadow-status" style="margin-top:6px; font-size:13px; color:#0f172a;">{loop_text}</div>
        </div>
        <script>
            const button = document.getElementById('shadow-play');
            const status = document.getElementById('shadow-status');
            const utteranceText = {json.dumps(target)};
            const loops = {loop_count};
            button.onclick = () => {{
                let count = 0;
                status.textContent = 'Loop 1 / ' + loops;
                const speakOnce = () => {{
                    const utterance = new SpeechSynthesisUtterance(utteranceText);
                    utterance.lang = 'es-ES';
                    utterance.onend = () => {{
                        count += 1;
                        if (count < loops) {{
                            status.textContent = 'Loop ' + (count + 1) + ' / ' + loops;
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
    st.header("Native-corpus collocation engine")
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
        st.text_area("Your rewrite", value="", key="rewrite-native")
        if st.button("Show model", key="rewrite-show"):
            st.info(item["rewrite"])
            st.caption("Compare rhythm, verb choice, and fixed frames.")

    with tabs[2]:
        item = random.choice(COLLOCATION_SETS)
        st.markdown(item["frame"])
        st.text_input("Fill in the blank", key="collocation-fill")
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
    st.header("Advanced conversation lab with constraints")
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
    st.header("Error-aware writing studio with edit trails")
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
    st.header("Argumentation & rhetoric drills")
    st.selectbox("Choose a topic", ARGUMENTATION_TOPICS)
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
    st.header("Dialect & regional Spanish tuning")
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
    st.header("Listening for nuance: fast, messy, real")
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
        st.radio(task["question"], task["options"], key=f"nuance-{idx}")
        if st.button("Reveal", key=f"nuance-reveal-{idx}"):
            st.info(f"Answer: {task['answer']}")


def render_fossilized_practice() -> None:
    st.header("Deliberate practice on fossilized errors")
    st.write("Detect repeated near-correct patterns and drill minimal pairs until accuracy improves.")

    log = st.text_area("Paste recent errors or draft snippets")
    if st.button("Analyze errors"):
        st.session_state.fossil_log.append(log)

    combined = " ".join(st.session_state.fossil_log).lower()
    st.subheader("Detected patterns")
    matches = []
    for item in FOSSILIZED_ERRORS:
        if item["pattern"] in combined:
            matches.append(item)
            st.markdown(f"- **{item['pattern']}** → {item['correction']} ({item['explanation']})")

    if not matches:
        st.info("No repeated patterns detected yet. Add more writing samples or errors.")
        return

    st.subheader("Contrast drill")
    selected = matches[0]
    pair = random.choice(selected["minimal_pairs"])
    choice = st.radio("Which sentence is correct?", pair, key="fossil-drill")
    if st.button("Submit drill"):
        st.session_state.fossil_stats["attempts"] += 1
        if choice == pair[0]:
            st.session_state.fossil_stats["correct"] += 1
            st.success("Correct! Keep reinforcing the accurate pattern.")
        else:
            st.error("Not quite. Focus on the corrected pattern above.")

    attempts = st.session_state.fossil_stats["attempts"]
    correct = st.session_state.fossil_stats["correct"]
    if attempts:
        st.metric("Drill accuracy", f"{(correct / attempts):.0%}")


def render_idioms_metaphor() -> None:
    st.header("Idioms, set phrases, and metaphor control")
    idiom = st.selectbox("Choose an idiom", [item["idiom"] for item in IDIOM_LIBRARY])
    selected = next(item for item in IDIOM_LIBRARY if item["idiom"] == idiom)

    st.markdown(f"**Meaning:** {selected['meaning']}")
    st.markdown(f"**Register:** {selected['register']}")
    st.markdown(f"**Safer alternative:** {selected['safe_alternative']}")
    st.info(selected["note"])

    register = st.selectbox("Required register", ["informal", "neutral", "formal"])
    response = st.text_area("Use it in context", height=120)
    if st.button("Evaluate usage"):
        has_idiom = selected["idiom"] in response.lower()
        register_match = selected["register"] == register or selected["register"] == "neutral"
        if has_idiom and register_match:
            st.success("Good usage. Sounds natural in the chosen register.")
        elif has_idiom:
            st.warning("Idiom used, but register may be off. Try the safer alternative.")
        else:
            st.error("Idiom missing. Try incorporating it naturally.")


def render_cultural_pragmatics() -> None:
    st.header("Cultural pragmatics and etiquette")
    region = st.selectbox("Region focus", sorted({s["region"] for s in PRAGMATIC_SCENARIOS}))
    scenarios = [s for s in PRAGMATIC_SCENARIOS if s["region"] == region]
    scenario = random.choice(scenarios)

    st.markdown(f"**Scenario:** {scenario['situation']}")
    st.write(scenario["prompt"])
    choice = st.radio("Select the best option", scenario["options"], key="pragmatics-choice")
    if st.button("Check pragmatics"):
        if choice == scenario["answer"]:
            st.success("Correct. Socially aligned response.")
        else:
            st.error("Grammatically possible, but socially off.")
        st.caption(scenario["feedback"])


def render_domain_precision() -> None:
    st.header("Precision vocabulary by domains")
    domain = st.selectbox("Select a domain", list(DOMAIN_MODULES.keys()))
    data = DOMAIN_MODULES[domain]

    st.subheader("Collocations & templates")
    st.write(", ".join(data["collocations"]))
    for template in data["templates"]:
        st.markdown(f"- {template}")

    st.subheader("False-friend trap")
    trap = data["false_friend"]
    choice = st.radio(trap["prompt"], trap["options"], key="domain-trap")
    if st.button("Check domain trap"):
        st.success("Correct!" if choice == trap["answer"] else "Try again.")
        st.caption(trap["note"])


def render_immersion_mode() -> None:
    st.header("Long-session immersion modes")
    mode_label = st.selectbox("Choose a session length", [mode["label"] for mode in IMMERSION_MODES])
    mode = next(item for item in IMMERSION_MODES if item["label"] == mode_label)

    st.markdown(f"**Duration:** {mode['duration']} minutes")
    st.markdown("#### Guided steps")
    for idx, step in enumerate(mode["steps"], start=1):
        st.checkbox(f"Step {idx}: {step}", key=f"immersion-step-{mode_label}-{idx}")

    st.subheader("Personal checklist")
    st.session_state.immersion_notes = st.text_area(
        "What do you personally need next?",
        value=st.session_state.immersion_notes,
        height=120,
    )
    if st.button("Save immersion notes"):
        st.success("Saved. Revisit after each session to track progress.")


def render_portfolio() -> None:
    st.header("Native-likeness benchmark & portfolio")
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
                <h3>Adaptive Assessment</h3>
                <p>Level placement + plan generation based on real-time performance.</p>
            </div>
            <div class="card">
                <h3>Weekly Gap Finder</h3>
                <p>Adaptive C1–C2 diagnostics with ranked Error Top 20 and targeted training plan.</p>
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

    st.subheader("Quick start exercises")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='quick-card'>Adaptive Assessment</div>", unsafe_allow_html=True)
        if st.button("Start assessment", key="quick-assessment"):
            set_nav("Adaptive Assessment")
    with col2:
        st.markdown("<div class='quick-card'>Fossilized Errors Drill</div>", unsafe_allow_html=True)
        if st.button("Start drill", key="quick-fossil"):
            set_nav("Fossilized Errors")
    with col3:
        st.markdown("<div class='quick-card'>Immersion Session</div>", unsafe_allow_html=True)
        if st.button("Start immersion", key="quick-immersion"):
            set_nav("Immersion Mode")


def main() -> None:
    set_theme()
    init_state()
    render_profile_sidebar()

    render_hero()
    st.write("")

    nav = st.session_state.nav
    if nav == "Overview":
        render_overview()
    elif nav == "Adaptive Assessment":
        render_adaptive_assessment()
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
    elif nav == "Fossilized Errors":
        render_fossilized_practice()
    elif nav == "Idioms & Metaphor":
        render_idioms_metaphor()
    elif nav == "Cultural Pragmatics":
        render_cultural_pragmatics()
    elif nav == "Domain Precision":
        render_domain_precision()
    elif nav == "Immersion Mode":
        render_immersion_mode()
    elif nav == "Portfolio":
        render_portfolio()


if __name__ == "__main__":
    main()
