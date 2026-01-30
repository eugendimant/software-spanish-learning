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
]

PORTFOLIO_AXES = [
    "Lexical sophistication",
    "Collocation accuracy",
    "Pragmatic appropriateness",
    "Prosody",
    "Cohesion",
]

VOCAB_DOMAINS = [
    {
        "domain": "Climate adaptation & resilience",
        "context": (
            "Las ciudades costeras están rediseñando su infraestructura para **mitigar** el "
            "**riesgo** de inundaciones, pero también para **blindar** servicios críticos y "
            "**reforzar** cadenas de suministro."
        ),
        "lexicon": [
            {
                "term": "mitigar",
                "meaning": "reducir el impacto de algo negativo",
                "example": "Se busca mitigar los efectos de las marejadas.",
                "register": "formal",
            },
            {
                "term": "blindar",
                "meaning": "proteger de forma sólida o estratégica",
                "example": "El plan pretende blindar la red eléctrica.",
                "register": "formal",
            },
            {
                "term": "reforzar",
                "meaning": "hacer más sólido o resistente",
                "example": "Hay que reforzar los diques.",
                "register": "neutral",
            },
            {
                "term": "umbral",
                "meaning": "límite crítico o punto de cambio",
                "example": "Superamos el umbral de tolerancia.",
                "register": "formal",
            },
        ],
    },
    {
        "domain": "Workplace dynamics & negotiation",
        "context": (
            "En negociaciones complejas conviene **sopesar** concesiones, "
            "**desactivar** tensiones y **pactar** un cronograma realista sin **ceder** "
            "más de lo necesario."
        ),
        "lexicon": [
            {
                "term": "sopesar",
                "meaning": "evaluar con calma varias opciones",
                "example": "Sopesó cada propuesta antes de responder.",
                "register": "formal",
            },
            {
                "term": "desactivar",
                "meaning": "reducir un conflicto o tensión",
                "example": "Buscamos desactivar la fricción con el cliente.",
                "register": "neutral",
            },
            {
                "term": "pactar",
                "meaning": "llegar a un acuerdo explícito",
                "example": "Pactaron nuevos plazos y prioridades.",
                "register": "neutral",
            },
            {
                "term": "ceder",
                "meaning": "entregar algo de forma parcial",
                "example": "Ceder demasiado puede debilitar la posición.",
                "register": "neutral",
            },
        ],
    },
    {
        "domain": "Health policy & public trust",
        "context": (
            "La estrategia debe **priorizar** la transparencia para **restablecer** "
            "la confianza pública, sin **subestimar** la fatiga informativa ni "
            "**desmentir** rumores con tono condescendiente."
        ),
        "lexicon": [
            {
                "term": "priorizar",
                "meaning": "dar prioridad a algo",
                "example": "El plan prioriza la atención primaria.",
                "register": "formal",
            },
            {
                "term": "restablecer",
                "meaning": "volver a instaurar",
                "example": "Restablecer la confianza requiere coherencia.",
                "register": "formal",
            },
            {
                "term": "subestimar",
                "meaning": "dar menos importancia de la real",
                "example": "No hay que subestimar el cansancio social.",
                "register": "neutral",
            },
            {
                "term": "desmentir",
                "meaning": "negar públicamente una información",
                "example": "El ministerio desmintió el rumor.",
                "register": "formal",
            },
        ],
    },
]

VERB_PRECISION_DRILLS = [
    {
        "scenario": "Necesitas decir que evaluaste opciones con calma antes de decidir.",
        "options": [
            {
                "verb": "sopesar",
                "nuance": "evaluación cuidadosa y estratégica",
                "example": "Sopesamos los riesgos antes de firmar.",
            },
            {
                "verb": "mirar",
                "nuance": "revisión general, poco profunda",
                "example": "Miramos los datos rápidamente.",
            },
            {
                "verb": "considerar",
                "nuance": "evaluación neutra, menos intensa",
                "example": "Consideramos varias alternativas.",
            },
        ],
        "best": "sopesar",
        "contrast": "Sopesar implica deliberación más intensa que considerar.",
    },
    {
        "scenario": "Quieres expresar que bajaste la tensión en una reunión.",
        "options": [
            {
                "verb": "desactivar",
                "nuance": "neutraliza tensión o conflicto",
                "example": "Desactivó la discusión con humor.",
            },
            {
                "verb": "parar",
                "nuance": "detener de forma brusca",
                "example": "Paró la conversación en seco.",
            },
            {
                "verb": "calmar",
                "nuance": "reducir intensidad emocional",
                "example": "Calmó a su equipo con claridad.",
            },
        ],
        "best": "desactivar",
        "contrast": "Desactivar es más táctico que calmar y menos brusco que parar.",
    },
    {
        "scenario": "Necesitas afirmar que insististe en cumplir una norma.",
        "options": [
            {
                "verb": "exigir",
                "nuance": "imponer con autoridad o firmeza",
                "example": "Exigió el cumplimiento del contrato.",
            },
            {
                "verb": "pedir",
                "nuance": "solicitud neutra",
                "example": "Pidió una actualización.",
            },
            {
                "verb": "sugerir",
                "nuance": "propuesta suave",
                "example": "Sugirió mejorar el proceso.",
            },
        ],
        "best": "exigir",
        "contrast": "Exigir es más fuerte y formal que pedir o sugerir.",
    },
]

GRAMMAR_MICRODRILLS = [
    {
        "focus": "Gender agreement",
        "prompt": "Selecciona la opción correcta: La reunión fue ___ y productiva.",
        "options": ["intenso", "intensa", "intensas"],
        "answer": "intensa",
        "explanation": "Reunión es femenino singular, por eso requiere intensa.",
        "examples": [
            "La discusión fue intensa.",
            "La agenda estuvo cargada.",
        ],
    },
    {
        "focus": "Verb tense",
        "prompt": "Completa: Si ___ más tiempo, habría terminado el informe.",
        "options": ["tengo", "tenía", "tuviera"],
        "answer": "tuviera",
        "explanation": "Condicional con si requiere imperfecto de subjuntivo.",
        "examples": [
            "Si tuviera apoyo, lo haría.",
            "Si fuera posible, lo ajustamos.",
        ],
    },
    {
        "focus": "Ser vs estar",
        "prompt": "El plan ___ listo, pero los recursos aún no.",
        "options": ["está", "es", "son"],
        "answer": "está",
        "explanation": "Estados temporales usan estar.",
        "examples": [
            "El equipo está listo.",
            "La sala está ocupada.",
        ],
    },
    {
        "focus": "Preposition choice",
        "prompt": "Depende ___ la aprobación del comité.",
        "options": ["de", "en", "por"],
        "answer": "de",
        "explanation": "El verbo depender se construye con de.",
        "examples": [
            "Depende de ti.",
            "Depende del presupuesto.",
        ],
    },
]

OUTPUT_PROMPTS = [
    {
        "title": "Operational update",
        "requirements": [
            "Usa 2 verbos precisos del banco.",
            "Incluye 1 conector concesivo (aunque/si bien).",
            "Usa 2 palabras del dominio elegido.",
        ],
        "prompt": "Escribe un update de 6-8 líneas para el equipo sobre un retraso en el proyecto.",
    },
    {
        "title": "Client negotiation note",
        "requirements": [
            "Usa 1 verbo de negociación.",
            "Incluye una frase de mitigación (quizá, tal vez, me parece).",
            "Evita calcos del inglés.",
        ],
        "prompt": "Redacta una respuesta breve a un cliente que pide más alcance sin ampliar plazos.",
    },
]

COMMON_MISTAKES = [
    {
        "pattern": "dependen en",
        "correction": "dependen de",
        "explanation": "El verbo depender siempre va con de.",
        "examples": ["Depende de la aprobación.", "Dependemos de su respuesta."],
    },
    {
        "pattern": "tomar una decisión en",
        "correction": "tomar una decisión sobre",
        "explanation": "En español, tomar una decisión sobre un tema es más natural.",
        "examples": [
            "Tomamos una decisión sobre el presupuesto.",
            "Tomó una decisión sobre el contrato.",
        ],
    },
    {
        "pattern": "la problema",
        "correction": "el problema",
        "explanation": "Problema es masculino pese a terminar en -a.",
        "examples": ["El problema fue resuelto.", "El problema persiste."],
    },
]

ADAPTIVE_QUESTION_BANK = [
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

WEEKLY_MISSIONS = [
    {
        "week": "Week 1",
        "title": "Secure a rental apartment",
        "brief": "Convince a landlord you are reliable, negotiate utilities, and clarify lease clauses.",
        "stakes": "Landlord skeptical due to high demand.",
        "skills": ["politeness", "hedging", "formal register", "negotiation"],
        "constraints": [
            "Use usted + formal greetings.",
            "Include 2 hedging phrases.",
            "Ask for clarification on a clause.",
        ],
    },
    {
        "week": "Week 2",
        "title": "Negotiate a contract clause",
        "brief": "You must push back on liability while preserving the partnership.",
        "stakes": "Legal counsel is firm on indemnity language.",
        "skills": ["diplomacy", "persuasion", "connector control", "tone"],
        "constraints": [
            "Offer a compromise with conditional language.",
            "Use 2 contrastive connectors.",
            "Avoid direct blame.",
        ],
    },
    {
        "week": "Week 3",
        "title": "Defend a thesis point",
        "brief": "Respond to committee doubts with evidence and respectful firmness.",
        "stakes": "Defense panel challenges your methodology.",
        "skills": ["academic register", "certainty control", "stance"],
        "constraints": [
            "Use 2 evidential markers.",
            "Use one concession + rebuttal.",
            "Stay in academic register.",
        ],
    },
    {
        "week": "Week 4",
        "title": "Handle a customer escalation",
        "brief": "De-escalate a frustrated client and negotiate a timeline reset.",
        "stakes": "Client threatens to cancel.",
        "skills": ["empathy", "de-escalation", "clarity", "solution framing"],
        "constraints": [
            "Acknowledge emotion explicitly.",
            "Offer 2 concrete next steps.",
            "Use softeners to reduce friction.",
        ],
    },
]

INPUT_LIBRARY = [
    {
        "title": "Investigative podcast: housing market crisis",
        "type": "Podcast",
        "level": "C1",
        "tags": ["persuasion", "interruptions", "technical vocabulary", "economics"],
    },
    {
        "title": "Debate: AI policy in higher education",
        "type": "Debate",
        "level": "C2",
        "tags": ["stance", "irony", "connectors", "academic register"],
    },
    {
        "title": "Court snippet: contract liability dispute",
        "type": "Court audio",
        "level": "C2",
        "tags": ["formal register", "precision", "hedging", "legal vocabulary"],
    },
    {
        "title": "Street interview: rent negotiations",
        "type": "Interview",
        "level": "C1",
        "tags": ["slang", "politeness", "interruptions", "negotiation"],
    },
    {
        "title": "Op-ed: customer service under pressure",
        "type": "Op-ed",
        "level": "C1",
        "tags": ["tone", "politeness", "blame control", "connectors"],
    },
    {
        "title": "Stand-up set: workplace miscommunication",
        "type": "Stand-up",
        "level": "C1",
        "tags": ["irony", "stance", "slang", "timing"],
    },
]

RELATIONSHIP_PERSONAS = [
    {
        "name": "María (Landlord)",
        "role": "Landlord",
        "relationship": "Cautiously open, wants reassurance about stability.",
        "tendencies": ["formal register", "expects concise answers", "likes polite hedging"],
    },
    {
        "name": "Sergio (Boss)",
        "role": "Boss",
        "relationship": "Direct, time-constrained, expects solutions.",
        "tendencies": ["prefers decisive tone", "low tolerance for vagueness"],
    },
    {
        "name": "Lucía (Colleague)",
        "role": "Colleague",
        "relationship": "Collaborative, values soft disagreement.",
        "tendencies": ["prefers inclusive language", "sensitive to bluntness"],
    },
]

LIVE_MODE_SCENARIOS = [
    {
        "title": "Overlapping stand-up update",
        "prompt": "Your teammate interrupts twice while you defend a timeline.",
        "focus": ["turn-taking", "speed", "assertiveness"],
    },
    {
        "title": "Angry customer call",
        "prompt": "Customer complains loudly while you propose a fix.",
        "focus": ["de-escalation", "empathy", "clarity"],
    },
    {
        "title": "Academic Q&A",
        "prompt": "Panel interrupts with rapid-fire follow-up questions.",
        "focus": ["certainty control", "evidence", "register"],
    },
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
            margin-right: 0.4rem;
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
    if "assessment" not in st.session_state:
        st.session_state.assessment = {
            "active": False,
            "last_completed": None,
        }
    if "gap_results" not in st.session_state:
        st.session_state.gap_results = []
    if "adaptive_focus" not in st.session_state:
        st.session_state.adaptive_focus = []
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = load_portfolio()
    if "writing_analysis" not in st.session_state:
        st.session_state.writing_analysis = {"draft": "", "edits": []}
    if "relationship_memory" not in st.session_state:
        st.session_state.relationship_memory = {
            persona["name"]: {"notes": [], "tendencies": persona["tendencies"]}
            for persona in RELATIONSHIP_PERSONAS
        }
    if "live_mode" not in st.session_state:
        st.session_state.live_mode = {"last_speed": 1.0, "last_complexity": 1.0}
    if "review_queue" not in st.session_state:
        st.session_state.review_queue = {}
    if "review_step" not in st.session_state:
        st.session_state.review_step = 0
    if "mistake_log" not in st.session_state:
        st.session_state.mistake_log = {}


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


def derive_adaptive_focus(scores: dict[str, int]) -> list[str]:
    focus = [area for area, score in scores.items() if score <= 3]
    return focus or ["Nuance & pragmatics", "Register & tone"]


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
    assessment = st.session_state.assessment
    profile["name"] = st.sidebar.text_input("Name", value=profile["name"], placeholder="Your name")
    profile["level"] = st.sidebar.selectbox("Target level", ["C1", "C2"], index=0)
    profile["weekly_goal"] = st.sidebar.slider("Weekly sessions", 2, 10, profile["weekly_goal"])
    assessment["active"] = st.sidebar.toggle("Activate adaptive mode", value=assessment["active"])
    if assessment["active"]:
        st.sidebar.success("Adaptive mode is on.")
    else:
        st.sidebar.info("Turn on adaptive mode to unlock weekly missions.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")

    if not assessment["active"]:
        st.sidebar.caption("Complete the activation to enable personalized missions.")

def render_gap_finder() -> None:
    st.header("Real-time gap-finder diagnostics")
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
        st.session_state.adaptive_focus = derive_adaptive_focus(scores)

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


def render_mission_control() -> None:
    st.header("Weekly mission control")
    st.write("Every week you enter a real-world mission that adapts to your slips.")

    if not st.session_state.assessment["active"]:
        st.info("Activate adaptive mode in the sidebar to unlock mission constraints.")
        return

    mission = st.selectbox("Choose your weekly mission", WEEKLY_MISSIONS, format_func=lambda m: f"{m['week']}: {m['title']}")
    st.markdown(f"**Brief:** {mission['brief']}")
    st.markdown(f"**Stakes:** {mission['stakes']}")
    st.markdown("**Core skills:** " + ", ".join(mission["skills"]))

    adaptive_constraints = {
        "Collocations": "Use 2 precise collocations from your gap list.",
        "Prepositions": "Avoid preposition mismatches (de/en/por/para).",
        "Discourse markers": "Use at least 3 discourse connectors.",
        "Register & tone": "Maintain consistent register for the whole response.",
        "Nuance & pragmatics": "Include softeners and avoid unintended blame.",
    }
    focus = st.session_state.adaptive_focus or ["Nuance & pragmatics"]
    st.markdown("**Adaptive constraints (tighten where you slipped)**")
    for area in focus:
        st.markdown(f"- {adaptive_constraints.get(area, 'Maintain clarity and precision.')}")

    st.markdown("**Mission constraints**")
    for constraint in mission["constraints"]:
        st.markdown(f"- {constraint}")

    st.text_area("Draft your mission response", height=180, key="mission-response")
    st.caption("Your mission response will be evaluated for register, hedging, and connector control.")


def render_adaptive_input_selection() -> None:
    st.header("Adaptive input selection")
    st.write("Authentic inputs are chosen based on your errors, not generic lessons.")

    tag_pool = sorted({tag for item in INPUT_LIBRARY for tag in item["tags"]})
    default_tags = []
    if st.session_state.adaptive_focus:
        focus_to_tags = {
            "Register & tone": ["formal register", "tone"],
            "Nuance & pragmatics": ["stance", "politeness", "blame control"],
            "Discourse markers": ["connectors"],
            "Collocations": ["technical vocabulary"],
            "Prepositions": ["precision"],
        }
        for focus in st.session_state.adaptive_focus:
            default_tags += focus_to_tags.get(focus, [])
    selected_tags = st.multiselect("Skills to target", tag_pool, default=list(dict.fromkeys(default_tags)))
    target_level = st.selectbox("Target input level", ["C1", "C2"])

    filtered = []
    for item in INPUT_LIBRARY:
        if item["level"] != target_level:
            continue
        overlap = len(set(item["tags"]) & set(selected_tags))
        filtered.append((overlap, item))
    filtered.sort(key=lambda x: x[0], reverse=True)

    st.markdown("**Recommended inputs at your edge**")
    for overlap, item in filtered:
        st.markdown(
            f"""
            <div class="card" style="margin-bottom:12px;">
                <h4>{item['title']}</h4>
                <p><strong>Type:</strong> {item['type']} • <strong>Level:</strong> {item['level']}</p>
                <p><strong>Skills:</strong> {", ".join(item["tags"])}</p>
                <p><strong>Match score:</strong> {overlap} skill tags</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_nuance_feedback() -> None:
    st.header("Nuance-first feedback lab")
    st.write("Compare what you intended to imply vs what you actually implied.")

    intent = st.text_area("Intended meaning", height=90, key="nuance-intent")
    message = st.text_area("Your message", height=120, key="nuance-message")
    stance = st.selectbox(
        "Target stance",
        ["Diplomatic", "Firm", "Skeptical", "Enthusiastic", "Neutral"],
    )

    if st.button("Analyze nuance"):
        lowered = message.lower()
        polite_markers = sum(marker in lowered for marker in REGISTER_MARKERS["politeness"])
        hedging_markers = sum(marker in lowered for marker in REGISTER_MARKERS["hedging"])
        blame_markers = sum(word in lowered for word in ["culpa", "fallo", "responsable"])
        certainty = "high" if "sin duda" in lowered or "claramente" in lowered else "medium"
        tone = "soft" if hedging_markers else "direct"

        st.subheader("Implication profile")
        st.write(
            [
                {"Signal": "Politeness", "Level": "high" if polite_markers else "low"},
                {"Signal": "Hedging", "Level": "present" if hedging_markers else "absent"},
                {"Signal": "Certainty", "Level": certainty},
                {"Signal": "Blame risk", "Level": "elevated" if blame_markers else "low"},
                {"Signal": "Emotional tone", "Level": tone},
            ]
        )

        st.markdown("**Mismatch check**")
        if intent and message and intent.lower() not in message.lower():
            st.warning("Your message may not reflect the intended meaning. Add explicit stance markers.")
        else:
            st.success("Message aligns with your intended meaning.")

    st.markdown("**Rephrase drill**")
    drill = st.selectbox(
        "Rephrase the same message as:",
        ["Softer", "Firmer", "More diplomatic", "More skeptical", "More enthusiastic", "More neutral"],
    )
    st.text_area("Rewrite here", height=120, key=f"nuance-drill-{drill}")
    st.caption(f"Target stance: {stance} • Drill mode: {drill}")


def render_relationship_memory() -> None:
    st.header("Relationship & persona memory")
    st.write("Stay consistent with personas across weeks and adapt to your tendencies.")

    persona_name = st.selectbox("Choose a partner", [p["name"] for p in RELATIONSHIP_PERSONAS])
    persona = next(p for p in RELATIONSHIP_PERSONAS if p["name"] == persona_name)
    memory = st.session_state.relationship_memory[persona_name]

    st.markdown(f"**Role:** {persona['role']}")
    st.markdown(f"**Relationship status:** {persona['relationship']}")
    st.markdown("**Known tendencies**")
    st.write(memory["tendencies"])

    note = st.text_area("Log a new interaction note", height=100)
    tendency_flags = st.multiselect(
        "Observed tendencies in your speech",
        ["too direct", "too formal", "over-hedging", "weak turn-taking", "awkward closings"],
    )
    if st.button("Save interaction"):
        if note.strip():
            memory["notes"].append(
                {"date": date.today().isoformat(), "note": note, "flags": tendency_flags}
            )
            st.success("Saved. Your future missions will reflect this relationship history.")
        else:
            st.info("Add a note to save the interaction.")

    if memory["notes"]:
        st.subheader("Relationship history")
        st.dataframe(memory["notes"], use_container_width=True)


def render_live_mode() -> None:
    st.header("Live mode: speed + messiness mastery")
    st.write("Real-time pace with overlaps, fillers, and timed responses.")

    scenario = st.selectbox("Scenario", [s["title"] for s in LIVE_MODE_SCENARIOS])
    selected = next(s for s in LIVE_MODE_SCENARIOS if s["title"] == scenario)
    st.markdown(f"**Prompt:** {selected['prompt']}")
    st.markdown("**Focus:** " + ", ".join(selected["focus"]))

    speed = st.slider("Audio speed multiplier", 0.8, 1.6, 1.0, 0.1)
    complexity = st.slider("Content complexity", 1, 5, 3)
    response_time = st.slider("Response time (seconds)", 10, 60, 25)

    if st.button("Start live drill"):
        st.session_state.live_mode["last_speed"] = speed
        st.session_state.live_mode["last_complexity"] = complexity
        st.info(
            f"Play the audio at {speed}× speed. Respond within {response_time}s. "
            f"Keep {complexity}/5 complexity."
        )
        st.progress(0.0, text="Timer ready — respond aloud, then debrief.")
    st.caption("Adaptive pacing: raise speed before complexity if time pressure is the issue.")


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
        choice = st.radio(task["question"], task["options"], key=f"nuance-{idx}")
        if st.button("Reveal", key=f"nuance-reveal-{idx}"):
            st.info(f"Answer: {task['answer']}")


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
                <h3>Weekly Mission Control</h3>
                <p>Real-life missions that tighten constraints where you slip and expand only after consistency.</p>
            </div>
            <div class="card">
                <h3>Adaptive Input Selection</h3>
                <p>Authentic content tagged by skills, auto-picked from your error patterns.</p>
            </div>
            <div class="card">
                <h3>Weekly Gap Finder</h3>
                <p>Adaptive C1–C2 diagnostics with ranked Error Top 20 and targeted training plan.</p>
            </div>
            <div class="card">
                <h3>Nuance Feedback Lab</h3>
                <p>Meaning vs implication feedback with rephrase drills for tone control.</p>
            </div>
            <div class="card">
                <h3>Prosody Coach</h3>
                <p>Shadowing with waveform + pitch tracks and looped playback.</p>
            </div>
            <div class="card">
                <h3>Growth Studio</h3>
                <p>Vocabulary expansion, verb precision, grammar drills, and output-first challenges.</p>
            </div>
            <div class="card">
                <h3>Relationship Memory</h3>
                <p>Track persona history, adjust to tendencies, stay consistent across weeks.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_review_items(items: list[dict]) -> None:
    for item in items:
        item_id = item["term"]
        if item_id not in st.session_state.review_queue:
            st.session_state.review_queue[item_id] = {
                "term": item["term"],
                "meaning": item["meaning"],
                "example": item["example"],
                "streak": 0,
                "next_due": 0,
            }


def log_mistake(pattern: str, correction: str) -> None:
    log = st.session_state.mistake_log
    if pattern not in log:
        log[pattern] = {"correction": correction, "count": 0}
    log[pattern]["count"] += 1


def update_review_item(item_id: str, success: bool) -> None:
    item = st.session_state.review_queue[item_id]
    if success:
        item["streak"] += 1
    else:
        item["streak"] = 0
    item["next_due"] = st.session_state.review_step + (2 ** item["streak"])


def render_growth_studio() -> None:
    st.header("Growth studio: vocabulary, verbs, grammar, output")
    st.write(
        "Push beyond repeated input with domain-specific vocabulary, precise verb choices, "
        "micro-grammar drills, and output-first practice with review."
    )

    st.subheader("1) Vocabulary expansion in context")
    domain = st.selectbox("Choose a new domain", [d["domain"] for d in VOCAB_DOMAINS])
    selected_domain = next(d for d in VOCAB_DOMAINS if d["domain"] == domain)
    st.markdown(selected_domain["context"])
    st.table(
        [
            {
                "Term": item["term"],
                "Meaning": item["meaning"],
                "Example": item["example"],
                "Register": item["register"],
            }
            for item in selected_domain["lexicon"]
        ]
    )
    chosen_terms = st.multiselect(
        "Add words to your review queue",
        [item["term"] for item in selected_domain["lexicon"]],
    )
    if st.button("Save vocab to review"):
        add_review_items(
            [item for item in selected_domain["lexicon"] if item["term"] in chosen_terms]
        )
        st.success("Added to review queue.")

    st.markdown("**Active production check**")
    vocab_response = st.text_area(
        "Write 2-3 sentences using at least 3 words from the table.",
        height=120,
        key="vocab-output",
    )
    if st.button("Check vocabulary usage"):
        used_terms = [item["term"] for item in selected_domain["lexicon"] if item["term"] in vocab_response]
        if len(used_terms) >= 3:
            st.success(f"Great—used: {', '.join(used_terms)}.")
        else:
            st.warning(
                "Try to include at least 3 target words. Detected: "
                f"{', '.join(used_terms) or 'none'}."
            )

    st.subheader("2) Verb precision lab")
    verb_drill = st.selectbox(
        "Select a scenario", [item["scenario"] for item in VERB_PRECISION_DRILLS]
    )
    drill = next(item for item in VERB_PRECISION_DRILLS if item["scenario"] == verb_drill)
    verb_choice = st.radio(
        "Choose the best verb",
        [option["verb"] for option in drill["options"]],
        key="verb-choice",
    )
    if st.button("Check verb choice"):
        if verb_choice == drill["best"]:
            st.success("Correct choice for tone and precision.")
        else:
            st.error("Close, but there is a more precise option.")
            log_mistake("verb precision", drill["best"])
        st.caption(drill["contrast"])
        st.markdown("**Quick contrasts**")
        st.write(
            [
                {
                    "Verb": option["verb"],
                    "Nuance": option["nuance"],
                    "Example": option["example"],
                }
                for option in drill["options"]
            ]
        )

    st.subheader("3) Grammar reinforcement (micro-drills)")
    drill_results = []
    for idx, drill in enumerate(GRAMMAR_MICRODRILLS):
        st.markdown(f"**{drill['focus']}**")
        choice = st.radio(drill["prompt"], drill["options"], key=f"grammar-{idx}")
        drill_results.append((drill, choice))
    if st.button("Check grammar drills"):
        for drill, choice in drill_results:
            if choice == drill["answer"]:
                st.success(f"{drill['focus']}: Correct.")
            else:
                st.error(f"{drill['focus']}: Correct answer is {drill['answer']}.")
                log_mistake(drill["prompt"], drill["answer"])
            st.caption(drill["explanation"])
            st.write("Examples: " + " • ".join(drill["examples"]))

    st.subheader("4) Output-first challenge")
    output_prompt = st.selectbox("Choose a prompt", [p["title"] for p in OUTPUT_PROMPTS])
    selected_prompt = next(p for p in OUTPUT_PROMPTS if p["title"] == output_prompt)
    st.markdown("**Prompt**: " + selected_prompt["prompt"])
    st.markdown("**Requirements**")
    for req in selected_prompt["requirements"]:
        st.markdown(f"- {req}")
    output_text = st.text_area("Your response", height=180, key="output-challenge")
    if st.button("Evaluate output"):
        feedback = []
        for mistake in COMMON_MISTAKES:
            if mistake["pattern"] in output_text.lower():
                feedback.append(mistake)
                log_mistake(mistake["pattern"], mistake["correction"])
        if feedback:
            st.error("Corrections needed")
            for item in feedback:
                st.markdown(f"- **Correction**: {item['correction']}")
                st.caption(item["explanation"])
                st.write("Examples: " + " • ".join(item["examples"]))
        else:
            st.success("Nice work! Your output avoids common errors.")

    st.subheader("5) Personalized review queue")
    st.session_state.review_step += 1
    due_items = [
        item for item in st.session_state.review_queue.values()
        if item["next_due"] <= st.session_state.review_step
    ]
    if not due_items:
        st.info("No items due. Add vocab above to start reviewing.")
    for item in due_items:
        st.markdown(f"**{item['term']}** — {item['meaning']}")
        st.caption(item["example"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Got it", key=f"review-pass-{item['term']}"):
                update_review_item(item["term"], True)
                st.success("Scheduled further out.")
        with col2:
            if st.button("Missed", key=f"review-fail-{item['term']}"):
                update_review_item(item["term"], False)
                st.warning("We'll recycle it sooner.")

    if st.session_state.mistake_log:
        st.markdown("**Mistake focus tracker**")
        sorted_mistakes = sorted(
            st.session_state.mistake_log.items(),
            key=lambda item: item[1]["count"],
            reverse=True,
        )
        st.table(
            [
                {
                    "Pattern": pattern,
                    "Correction": data["correction"],
                    "Count": data["count"],
                }
                for pattern, data in sorted_mistakes
            ]
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
            "Growth Studio",
            "Weekly Mission",
            "Adaptive Inputs",
            "Nuance Feedback",
            "Relationship Memory",
            "Live Mode",
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
    elif nav == "Growth Studio":
        render_growth_studio()
    elif nav == "Weekly Mission":
        render_mission_control()
    elif nav == "Adaptive Inputs":
        render_adaptive_input_selection()
    elif nav == "Nuance Feedback":
        render_nuance_feedback()
    elif nav == "Relationship Memory":
        render_relationship_memory()
    elif nav == "Live Mode":
        render_live_mode()
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
