"""Output-First Daily Missions page."""
import streamlit as st
import streamlit.components.v1 as components
import random
import re
import json
from datetime import date
from typing import Optional

from utils.theme import render_hero, render_section_header
from utils.database import (
    save_daily_mission, get_today_mission, update_mission_response,
    record_progress, save_transcript, get_user_profile, save_mistake,
    record_error_fingerprint, log_activity
)
from utils.content import (
    DAILY_MISSION_TEMPLATES, REGISTER_MARKERS, COLLOCATIONS,
    VERB_CHOICE_STUDIO, GRAMMAR_MICRODRILLS
)
from utils.helpers import (
    seed_for_day, analyze_constraints, check_text_for_mistakes,
    detect_language, normalize_accents
)


# ============== EXTENDED MISSION TEMPLATES ==============

EXTENDED_MISSION_TEMPLATES = [
    # Speaking missions
    {
        "type": "speaking",
        "title": "Update de proyecto",
        "prompt": "Graba un update de 60-90 segundos explicando el estado de un proyecto ficticio. Menciona un obstaculo y como lo afrontaste.",
        "constraints": [
            "Usa 2 verbos del banco: sopesar, afrontar, plantear, desactivar",
            "Incluye un conector concesivo (aunque, si bien, a pesar de)",
            "Usa vocabulario del dominio profesional"
        ],
        "vocab_focus": ["sopesar", "afrontar", "plantear", "desactivar", "proyecto", "obstaculo"],
        "grammar_focus": "conectores concesivos",
        "min_words": 40,
        "target_structures": ["aunque", "si bien", "a pesar de", "pese a"],
    },
    {
        "type": "speaking",
        "title": "Explicar un problema medico",
        "prompt": "Graba 60-90 segundos explicando sintomas a un medico de forma clara y organizada.",
        "constraints": [
            "Usa vocabulario del dominio salud (sintoma, diagnostico, consulta)",
            "Organiza cronologicamente (primero, luego, despues)",
            "Incluye un subjuntivo con recomendacion (es importante que, sugiero que)"
        ],
        "vocab_focus": ["sintoma", "diagnostico", "consulta", "tratamiento", "dolor", "fiebre"],
        "grammar_focus": "subjuntivo con expresiones de consejo",
        "min_words": 40,
        "target_structures": ["es importante que", "sugiero que", "recomiendo que", "es necesario que"],
    },
    {
        "type": "speaking",
        "title": "Desacuerdo diplomatico",
        "prompt": "Graba 60-90 segundos expresando desacuerdo con una propuesta de un colega sin crear tension.",
        "constraints": [
            "Usa 2 suavizadores (quiza, me parece, tal vez, podria ser)",
            "Incluye una concesion antes del desacuerdo (entiendo que, comprendo que)",
            "Propon una alternativa concreta"
        ],
        "vocab_focus": ["plantear", "considerar", "alternativa", "propuesta", "perspectiva"],
        "grammar_focus": "hedging y mitigacion",
        "min_words": 40,
        "target_structures": ["quiza", "tal vez", "me parece", "podria ser", "entiendo que"],
    },
    {
        "type": "speaking",
        "title": "Contar una anecdota",
        "prompt": "Cuenta una anecdota interesante o divertida que te haya pasado (real o inventada). Incluye detalles y emociones.",
        "constraints": [
            "Usa preterito e imperfecto correctamente",
            "Incluye marcadores temporales (de repente, mientras, en ese momento)",
            "Expresa emociones (me sorprendio, me dio miedo, me alegro)"
        ],
        "vocab_focus": ["de repente", "mientras", "en ese momento", "entonces", "finalmente"],
        "grammar_focus": "preterito vs imperfecto",
        "min_words": 50,
        "target_structures": ["de repente", "mientras", "en ese momento", "cuando"],
    },
    {
        "type": "speaking",
        "title": "Dar instrucciones",
        "prompt": "Explica como hacer algo que sabes hacer bien (una receta, un proceso, un hobby). Se claro y usa secuenciadores.",
        "constraints": [
            "Usa imperativo o infinitivo para las instrucciones",
            "Incluye secuenciadores (primero, luego, despues, finalmente)",
            "Menciona al menos 3 pasos distintos"
        ],
        "vocab_focus": ["primero", "luego", "despues", "a continuacion", "finalmente", "por ultimo"],
        "grammar_focus": "imperativo y secuenciadores",
        "min_words": 40,
        "target_structures": ["primero", "luego", "despues", "finalmente"],
    },
    # Writing missions
    {
        "type": "writing",
        "title": "Email de negociacion",
        "prompt": "Escribe un email de 4-6 oraciones respondiendo a un cliente que pide mas alcance sin ampliar plazos.",
        "constraints": [
            "Usa 1 verbo de negociacion (pactar, ceder, plantear, negociar)",
            "Incluye una frase de mitigacion (quiza, tal vez, me parece)",
            "Evita calcos del ingles (no 'aplicar para', 'hacer sentido')"
        ],
        "vocab_focus": ["pactar", "plantear", "mitigacion", "alcance", "plazo", "priorizar"],
        "grammar_focus": "condicionales para cortesia",
        "min_words": 30,
        "target_structures": ["seria posible", "podriamos", "le agradeceria"],
    },
    {
        "type": "writing",
        "title": "Reclamacion formal",
        "prompt": "Escribe 4-6 oraciones reclamando un retraso en un envio. Se firme pero cortes.",
        "constraints": [
            "Usa registro formal con usted",
            "Incluye fechas o datos concretos (hace X dias, el dia X)",
            "Pide solucion especifica (reembolso, envio urgente, compensacion)"
        ],
        "vocab_focus": ["reclamar", "plazo", "indemnizacion", "retraso", "urgente"],
        "grammar_focus": "condicionales de cortesia",
        "min_words": 30,
        "target_structures": ["le informo", "le solicito", "le agradeceria", "seria posible"],
    },
    {
        "type": "writing",
        "title": "Mensaje a un amigo",
        "prompt": "Escribe un mensaje informal (4-6 oraciones) a un amigo contandole planes para el fin de semana e invitandolo.",
        "constraints": [
            "Usa registro informal con tu",
            "Incluye expresiones coloquiales (quedamos, mola, genial)",
            "Haz una invitacion o propuesta concreta"
        ],
        "vocab_focus": ["quedar", "plan", "genial", "apuntarse", "pasarlo bien"],
        "grammar_focus": "registro informal",
        "min_words": 25,
        "target_structures": ["te apetece", "quedamos", "que te parece si"],
    },
    {
        "type": "writing",
        "title": "Descripcion de un lugar",
        "prompt": "Describe tu lugar favorito en 4-6 oraciones. Incluye detalles sensoriales y por que te gusta.",
        "constraints": [
            "Usa adjetivos variados (no solo 'bonito' o 'grande')",
            "Incluye comparaciones o superlativos",
            "Expresa opinion personal (me encanta porque, lo que mas me gusta es)"
        ],
        "vocab_focus": ["acogedor", "tranquilo", "impresionante", "relajante", "ambiente"],
        "grammar_focus": "adjetivos y comparativos",
        "min_words": 30,
        "target_structures": ["mas... que", "el mas", "tan... como", "me encanta porque"],
    },
    {
        "type": "writing",
        "title": "Opinion argumentada",
        "prompt": "Escribe 4-6 oraciones dando tu opinion sobre un tema actual. Incluye al menos un argumento a favor y uno en contra.",
        "constraints": [
            "Usa conectores de contraste (sin embargo, por otro lado, aunque)",
            "Incluye expresiones de opinion (creo que, me parece que, en mi opinion)",
            "Concluye con tu postura final"
        ],
        "vocab_focus": ["sin embargo", "por otro lado", "en mi opinion", "considero", "concluyo"],
        "grammar_focus": "conectores de contraste",
        "min_words": 35,
        "target_structures": ["sin embargo", "por otro lado", "aunque", "creo que", "en conclusion"],
    },
    {
        "type": "writing",
        "title": "Queja formal a un servicio",
        "prompt": "Escribe 4-6 oraciones quejandote formalmente de un servicio deficiente (restaurante, tienda, transporte).",
        "constraints": [
            "Mantiene registro formal pero firme",
            "Describe el problema especifico con detalles",
            "Solicita una accion concreta (disculpa, compensacion, mejora)"
        ],
        "vocab_focus": ["inaceptable", "deficiente", "solicitar", "compensacion", "lamentar"],
        "grammar_focus": "registro formal para quejas",
        "min_words": 30,
        "target_structures": ["le escribo para", "me vi en la situacion", "le solicito"],
    },
    {
        "type": "writing",
        "title": "Resumen de una decision",
        "prompt": "Escribe 4-6 oraciones explicando una decision importante que tomaste recientemente y por que.",
        "constraints": [
            "Usa conectores causales (porque, ya que, dado que, puesto que)",
            "Incluye verbos de decision (decidir, optar por, elegir, determinar)",
            "Menciona consecuencias o resultados"
        ],
        "vocab_focus": ["decidir", "optar", "consecuencia", "resultado", "valorar", "sopesar"],
        "grammar_focus": "conectores causales",
        "min_words": 30,
        "target_structures": ["porque", "ya que", "dado que", "por lo tanto", "como resultado"],
    },
]


# ============== EVALUATION SYSTEM ==============

def evaluate_mission_response(
    response: str,
    mission: dict,
    duration: int = 0
) -> dict:
    """
    Comprehensive evaluation of a mission response.

    Checks:
    - Required vocabulary usage
    - Target grammar structures
    - Spanish language errors
    - Constraint adherence
    - Length requirements

    Returns detailed feedback with scores and suggestions.
    """
    result = {
        "overall_score": 0,
        "vocab_score": 0,
        "grammar_score": 0,
        "constraint_score": 0,
        "error_score": 100,  # Starts at 100, deducted for errors
        "length_score": 0,
        "vocab_feedback": [],
        "grammar_feedback": [],
        "constraint_feedback": [],
        "error_feedback": [],
        "suggestions": [],
        "vocab_used": [],
        "structures_used": [],
        "mistakes": [],
        "is_passing": False,
    }

    response_lower = response.lower()
    response_normalized = normalize_accents(response_lower)
    words = response.split()
    word_count = len(words)

    # ============== 1. VOCABULARY CHECK ==============
    vocab_focus = mission.get("vocab_focus", [])
    vocab_found = []
    vocab_missing = []

    for vocab in vocab_focus:
        vocab_lower = vocab.lower()
        vocab_normalized = normalize_accents(vocab_lower)

        # Check for exact match or normalized match
        if vocab_lower in response_lower or vocab_normalized in response_normalized:
            vocab_found.append(vocab)
        else:
            # Check for verb conjugations (basic stem matching)
            stem = vocab_normalized[:min(len(vocab_normalized)-2, 6)] if len(vocab_normalized) > 3 else vocab_normalized
            if len(stem) >= 3 and stem in response_normalized:
                vocab_found.append(vocab)
            else:
                vocab_missing.append(vocab)

    if vocab_focus:
        vocab_ratio = len(vocab_found) / len(vocab_focus)
        result["vocab_score"] = int(vocab_ratio * 100)
        result["vocab_used"] = vocab_found

        if vocab_found:
            result["vocab_feedback"].append({
                "type": "success",
                "message": f"Vocabulario usado: {', '.join(vocab_found)}"
            })
        if vocab_missing:
            result["vocab_feedback"].append({
                "type": "warning",
                "message": f"Vocabulario no encontrado: {', '.join(vocab_missing)}",
                "suggestion": f"Intenta incluir: {vocab_missing[0]}"
            })
    else:
        result["vocab_score"] = 100  # No vocab requirements

    # ============== 2. GRAMMAR STRUCTURE CHECK ==============
    target_structures = mission.get("target_structures", [])
    grammar_focus = mission.get("grammar_focus", "")
    structures_found = []
    structures_missing = []

    for structure in target_structures:
        structure_lower = structure.lower()
        structure_normalized = normalize_accents(structure_lower)

        if structure_lower in response_lower or structure_normalized in response_normalized:
            structures_found.append(structure)
        else:
            structures_missing.append(structure)

    if target_structures:
        # Require at least one structure to be found
        min_required = max(1, len(target_structures) // 3)
        if len(structures_found) >= min_required:
            structure_ratio = min(1.0, len(structures_found) / min_required)
            result["grammar_score"] = int(structure_ratio * 100)
        else:
            result["grammar_score"] = int((len(structures_found) / min_required) * 100)

        result["structures_used"] = structures_found

        if structures_found:
            result["grammar_feedback"].append({
                "type": "success",
                "message": f"Estructuras gramaticales usadas: {', '.join(structures_found)}"
            })
        if structures_missing and len(structures_found) < min_required:
            result["grammar_feedback"].append({
                "type": "warning",
                "message": f"Considera usar: {', '.join(structures_missing[:3])}",
                "focus": grammar_focus
            })
    else:
        result["grammar_score"] = 100  # No structure requirements

    # ============== 3. CONSTRAINT ANALYSIS ==============
    constraints = mission.get("constraints", [])
    constraints_met = 0

    for constraint in constraints:
        constraint_lower = constraint.lower()
        met = False
        feedback_item = {"constraint": constraint, "met": False, "details": ""}

        # Check for hedging/mitigation markers
        if any(term in constraint_lower for term in ["mitigador", "suavizador", "quiza", "tal vez"]):
            hedging_markers = ["quiza", "tal vez", "me parece", "podria", "seria", "a mi modo de ver", "diria que"]
            found_hedging = [m for m in hedging_markers if m in response_lower]
            required = 2 if "2" in constraint else 1
            if len(found_hedging) >= required:
                met = True
                feedback_item["details"] = f"Encontrado: {', '.join(found_hedging)}"
            else:
                feedback_item["details"] = f"Necesitas {required} mitigador(es). Encontrado: {len(found_hedging)}"

        # Check for concessive connectors
        elif any(term in constraint_lower for term in ["concesi", "aunque", "si bien", "a pesar"]):
            concessive = ["aunque", "si bien", "a pesar de", "pese a", "no obstante"]
            found_concessive = [c for c in concessive if c in response_lower]
            if found_concessive:
                met = True
                feedback_item["details"] = f"Encontrado: {', '.join(found_concessive)}"
            else:
                feedback_item["details"] = "Usa: aunque, si bien, a pesar de"

        # Check for precise verbs
        elif "verbo" in constraint_lower and any(term in constraint_lower for term in ["preciso", "negociacion", "banco"]):
            precise_verbs = ["afrontar", "plantear", "desactivar", "sopesar", "tramitar", "aportar",
                           "pactar", "ceder", "negociar", "mediar", "gestionar"]
            found_verbs = []
            for verb in precise_verbs:
                verb_stem = verb[:min(len(verb)-2, 6)]
                if verb in response_lower or verb_stem in response_normalized:
                    found_verbs.append(verb)
            required = 2 if "2" in constraint else 1
            if len(found_verbs) >= required:
                met = True
                feedback_item["details"] = f"Verbos precisos: {', '.join(found_verbs)}"
            else:
                feedback_item["details"] = f"Necesitas {required} verbo(s) preciso(s)"

        # Check for formal register (usted)
        elif "usted" in constraint_lower or "formal" in constraint_lower:
            formal_markers = ["usted", "le ", "les ", "le agradeceria", "seria posible", "le informo", "le solicito"]
            found_formal = [m for m in formal_markers if m in response_lower]
            if found_formal:
                met = True
                feedback_item["details"] = f"Registro formal detectado: {', '.join(found_formal[:3])}"
            else:
                feedback_item["details"] = "Usa 'usted' y formas de cortesia"

        # Check for informal register (tu)
        elif "informal" in constraint_lower or "coloquial" in constraint_lower:
            informal_markers = ["tu ", "te ", "quedamos", "mola", "genial", "oye", "vale"]
            found_informal = [m for m in informal_markers if m in response_lower]
            if found_informal:
                met = True
                feedback_item["details"] = f"Registro informal detectado"
            else:
                feedback_item["details"] = "Usa tuteo y expresiones coloquiales"

        # Check for temporal/sequence markers
        elif any(term in constraint_lower for term in ["temporal", "secuencia", "cronologic"]):
            temporal = ["primero", "luego", "despues", "entonces", "finalmente", "mientras", "de repente"]
            found_temporal = [t for t in temporal if t in response_lower or normalize_accents(t) in response_normalized]
            if found_temporal:
                met = True
                feedback_item["details"] = f"Marcadores: {', '.join(found_temporal)}"
            else:
                feedback_item["details"] = "Usa: primero, luego, despues, finalmente"

        # Check for subjunctive usage
        elif "subjuntivo" in constraint_lower:
            subjunctive_triggers = ["que ", "cuando ", "para que", "aunque ", "ojalá", "espero que"]
            # Look for subjunctive verb endings after triggers
            subj_patterns = [r"que\s+\w+[ae]s?\b", r"es importante que", r"sugiero que", r"recomiendo que"]
            found_subj = any(re.search(p, response_lower) for p in subj_patterns)
            if found_subj or any(t in response_lower for t in ["es importante que", "sugiero que", "recomiendo que", "es necesario que"]):
                met = True
                feedback_item["details"] = "Uso de subjuntivo detectado"
            else:
                feedback_item["details"] = "Usa: es importante que + subjuntivo"

        # Check for avoiding calques
        elif "calco" in constraint_lower or "ingles" in constraint_lower:
            calques = ["aplicar para", "hacer sentido", "tomar lugar", "llamar atras"]
            found_calques = [c for c in calques if c in response_lower]
            if not found_calques:
                met = True
                feedback_item["details"] = "No se detectaron calcos del ingles"
            else:
                feedback_item["details"] = f"Evita: {', '.join(found_calques)}"

        # Check for contrast connectors
        elif any(term in constraint_lower for term in ["contraste", "sin embargo", "por otro lado"]):
            contrast = ["sin embargo", "por otro lado", "no obstante", "en cambio", "pero"]
            found_contrast = [c for c in contrast if c in response_lower]
            if found_contrast:
                met = True
                feedback_item["details"] = f"Conectores: {', '.join(found_contrast)}"
            else:
                feedback_item["details"] = "Usa: sin embargo, por otro lado"

        # Check for causal connectors
        elif any(term in constraint_lower for term in ["causal", "porque", "ya que"]):
            causal = ["porque", "ya que", "dado que", "puesto que", "debido a"]
            found_causal = [c for c in causal if c in response_lower]
            if found_causal:
                met = True
                feedback_item["details"] = f"Conectores causales: {', '.join(found_causal)}"
            else:
                feedback_item["details"] = "Usa: porque, ya que, dado que"

        # Check for opinion expressions
        elif any(term in constraint_lower for term in ["opinion", "creo", "parece"]):
            opinion = ["creo que", "me parece", "en mi opinion", "considero", "pienso que"]
            found_opinion = [o for o in opinion if o in response_lower]
            if found_opinion:
                met = True
                feedback_item["details"] = f"Expresiones de opinion: {', '.join(found_opinion)}"
            else:
                feedback_item["details"] = "Usa: creo que, me parece que, en mi opinion"

        # Generic check - look for key words in constraint
        else:
            constraint_words = re.findall(r'\b[a-záéíóúüñ]+\b', constraint_lower)
            key_words = [w for w in constraint_words if len(w) > 4 and w not in
                        ["incluye", "incluir", "oraciones", "escribir", "menciona", "usa", "usar"]]
            if any(kw in response_lower for kw in key_words):
                met = True
                feedback_item["details"] = "Requisito cumplido"
            else:
                feedback_item["details"] = "Revision manual recomendada"
                met = True  # Give benefit of doubt for generic constraints

        feedback_item["met"] = met
        if met:
            constraints_met += 1
        result["constraint_feedback"].append(feedback_item)

    if constraints:
        result["constraint_score"] = int((constraints_met / len(constraints)) * 100)
    else:
        result["constraint_score"] = 100

    # ============== 4. ERROR CHECK ==============
    try:
        mistakes = check_text_for_mistakes(response)
        # Filter out language warnings for scoring
        grammar_mistakes = [m for m in mistakes if m.get("tag") != "language"]
        result["mistakes"] = grammar_mistakes

        # Deduct points for errors (max 50 points deduction)
        error_penalty = min(len(grammar_mistakes) * 15, 50)
        result["error_score"] = 100 - error_penalty

        for mistake in grammar_mistakes[:5]:
            result["error_feedback"].append({
                "type": "error",
                "original": mistake.get("original", ""),
                "correction": mistake.get("correction", ""),
                "explanation": mistake.get("explanation", ""),
                "tag": mistake.get("tag", "")
            })

            # Record error fingerprint for tracking
            tag = mistake.get("tag", "other")
            if tag in ["gender", "agreement"]:
                record_error_fingerprint("agreement", tag, is_error=True,
                    user_input=mistake.get("original", ""),
                    expected=mistake.get("correction", ""))
            elif tag in ["copula", "ser_estar"]:
                record_error_fingerprint("ser_estar", "usage", is_error=True,
                    user_input=mistake.get("original", ""),
                    expected=mistake.get("correction", ""))
            elif tag == "preposition":
                record_error_fingerprint("prepositions", "usage", is_error=True,
                    user_input=mistake.get("original", ""),
                    expected=mistake.get("correction", ""))
            elif tag in ["calque", "false_friend"]:
                record_error_fingerprint("vocabulary", tag, is_error=True,
                    user_input=mistake.get("original", ""),
                    expected=mistake.get("correction", ""))
    except Exception:
        result["error_score"] = 100  # Don't penalize if checker fails

    # ============== 5. LENGTH CHECK ==============
    min_words = mission.get("min_words", 25)
    if word_count >= min_words:
        result["length_score"] = 100
    elif word_count >= min_words * 0.7:
        result["length_score"] = 70
    elif word_count >= min_words * 0.5:
        result["length_score"] = 50
    else:
        result["length_score"] = max(0, int((word_count / min_words) * 50))

    if word_count < min_words:
        result["suggestions"].append(f"Escribe al menos {min_words} palabras (tienes {word_count})")

    # ============== 6. CALCULATE OVERALL SCORE ==============
    # Weighted average
    weights = {
        "vocab": 0.20,
        "grammar": 0.20,
        "constraint": 0.30,
        "error": 0.20,
        "length": 0.10
    }

    result["overall_score"] = int(
        result["vocab_score"] * weights["vocab"] +
        result["grammar_score"] * weights["grammar"] +
        result["constraint_score"] * weights["constraint"] +
        result["error_score"] * weights["error"] +
        result["length_score"] * weights["length"]
    )

    # Cap at 100
    result["overall_score"] = min(100, max(0, result["overall_score"]))

    # Passing threshold
    result["is_passing"] = result["overall_score"] >= 60

    # ============== 7. GENERATE SUGGESTIONS ==============
    if result["vocab_score"] < 70 and vocab_missing:
        result["suggestions"].append(f"Intenta usar vocabulario clave: {', '.join(vocab_missing[:2])}")

    if result["grammar_score"] < 70 and structures_missing:
        result["suggestions"].append(f"Incluye estructuras como: {structures_missing[0]}")

    if result["error_score"] < 80 and result["mistakes"]:
        result["suggestions"].append(f"Revisa: {result['mistakes'][0].get('original', '')} -> {result['mistakes'][0].get('correction', '')}")

    if not result["suggestions"]:
        if result["overall_score"] >= 90:
            result["suggestions"].append("Excelente trabajo! Respuesta muy completa.")
        elif result["overall_score"] >= 70:
            result["suggestions"].append("Buen trabajo! Sigue practicando para mejorar aun mas.")

    return result


def get_all_mission_templates() -> list:
    """Get combined mission templates (original + extended)."""
    return DAILY_MISSION_TEMPLATES + EXTENDED_MISSION_TEMPLATES


def render_daily_missions_page():
    """Render the Output-First Daily Missions page."""
    render_hero(
        title="Daily Missions",
        subtitle="Short daily tasks that force production: speaking + writing with vocabulary, grammar, and verb constraints.",
        pills=["Speaking", "Writing", "Constraints", "Feedback"]
    )

    # Initialize session state
    if "dm_mission" not in st.session_state:
        st.session_state.dm_mission = None
    if "dm_response" not in st.session_state:
        st.session_state.dm_response = ""
    if "dm_submitted" not in st.session_state:
        st.session_state.dm_submitted = False
    if "dm_feedback" not in st.session_state:
        st.session_state.dm_feedback = None
    if "dm_evaluation" not in st.session_state:
        st.session_state.dm_evaluation = None

    # Check for existing mission today
    today_mission = get_today_mission()

    # Mission selection
    col1, col2 = st.columns([2, 1])

    with col1:
        render_section_header("Today's Mission")

        if today_mission and today_mission.get("completed"):
            st.success("Mission completed! Come back tomorrow for a new challenge.")

            # Show completed mission
            st.markdown(f"""
            <div class="card">
                <h4>{today_mission.get('mission_type', 'Mission').title()}</h4>
                <p>{today_mission.get('prompt', '')}</p>
                <p><strong>Your score:</strong> {today_mission.get('score', 0):.0f}/100</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Practice Another Mission", type="primary"):
                st.session_state.dm_mission = None
                st.session_state.dm_submitted = False
                st.session_state.dm_feedback = None
                st.session_state.dm_evaluation = None
                st.rerun()

        else:
            # Generate or load mission
            if st.session_state.dm_mission is None:
                seed = seed_for_day(date.today(), "mission")
                random.seed(seed)
                all_missions = get_all_mission_templates()
                st.session_state.dm_mission = random.choice(all_missions)

            mission = st.session_state.dm_mission
            render_mission(mission)

    with col2:
        render_section_header("Mission Stats")

        # Quick stats - use profile's weekly goal setting
        profile = get_user_profile()
        weekly_goal = profile.get("weekly_goal", 6)
        st.metric("Missions Today", "1" if today_mission else "0")
        st.metric("Weekly Goal", str(weekly_goal))

        # Constraint hints
        st.markdown("### Constraint Guide")
        st.markdown("""
        - **Verbs:** Use specific, precise verbs
        - **Grammar:** Include the target structure
        - **Vocab:** Incorporate domain words
        """)


def render_mission(mission: dict):
    """Render a single mission."""
    mission_type = mission.get("type", "writing")
    title = mission.get("title", "Daily Mission")
    prompt = mission.get("prompt", "")
    constraints = mission.get("constraints", [])
    vocab_focus = mission.get("vocab_focus", [])
    grammar_focus = mission.get("grammar_focus", "")

    # Mission card
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid #6366f1;">
        <div class="card-header">
            <div class="card-icon">{'🎤' if mission_type == 'speaking' else '✍️'}</div>
            <h3 class="card-title">{title}</h3>
        </div>
        <span class="pill pill-{'primary' if mission_type == 'speaking' else 'secondary'}">
            {mission_type.upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Prompt
    st.markdown(f"""
    <div class="card-muted" style="margin: 1rem 0;">
        <strong>Your task:</strong><br>
        {prompt}
    </div>
    """, unsafe_allow_html=True)

    # Constraints
    st.markdown("### Constraints")
    for i, constraint in enumerate(constraints, 1):
        st.markdown(f"**{i}.** {constraint}")

    # Focus areas
    if vocab_focus:
        st.markdown(f"**Vocabulary focus:** {', '.join(vocab_focus)}")
    if grammar_focus:
        st.markdown(f"**Grammar focus:** {grammar_focus}")

    st.divider()

    # Input based on type
    if mission_type == "speaking":
        render_speaking_input(mission)
    else:
        render_writing_input(mission)


def render_speaking_input(mission: dict):
    """Render speaking mission input."""
    st.markdown("### Record Your Response")
    st.markdown("*60-90 seconds speaking time*")

    # Audio recorder info
    st.markdown("""
    <div class="card-muted">
        <strong>Recording Instructions:</strong>
        <ol>
            <li>Use your device's voice recorder or the browser</li>
            <li>Speak for 60-90 seconds</li>
            <li>Focus on the constraints listed above</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Web Speech API recorder
    components.html("""
    <div style="padding: 1rem; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0;">
        <div id="recorder-status" style="margin-bottom: 1rem; font-weight: 500;">Click to start recording</div>
        <button id="record-btn" onclick="toggleRecording()"
            style="padding: 0.75rem 1.5rem; background: #2563eb; color: white; border: none;
                   border-radius: 8px; cursor: pointer; font-weight: 600;">
            🎤 Start Recording
        </button>
        <div id="timer" style="margin-top: 0.5rem; font-size: 1.5rem; font-weight: 700; color: #2563eb;">0:00</div>
    </div>
    <script>
        let isRecording = false;
        let startTime;
        let timerInterval;

        function toggleRecording() {
            const btn = document.getElementById('record-btn');
            const status = document.getElementById('recorder-status');

            if (!isRecording) {
                isRecording = true;
                startTime = Date.now();
                btn.textContent = '⏹ Stop Recording';
                btn.style.background = '#dc2626';
                status.textContent = 'Recording...';

                timerInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const mins = Math.floor(elapsed / 60);
                    const secs = elapsed % 60;
                    document.getElementById('timer').textContent =
                        mins + ':' + secs.toString().padStart(2, '0');
                }, 1000);
            } else {
                isRecording = false;
                clearInterval(timerInterval);
                btn.textContent = '🎤 Start Recording';
                btn.style.background = '#2563eb';
                status.textContent = 'Recording saved! Enter transcript below.';
            }
        }
    </script>
    """, height=200)

    # Transcript input
    st.markdown("### Enter Transcript")
    st.markdown("*Type what you said (for review and feedback)*")

    transcript = st.text_area(
        "Your spoken response:",
        value=st.session_state.dm_response,
        height=150,
        key="speaking_transcript"
    )
    st.session_state.dm_response = transcript

    # Duration estimate
    duration = st.slider("Approximate speaking time (seconds):", 30, 120, 60)

    # Add hint button
    if st.button("💡 Hint in English", key="speaking_hint"):
        constraints = mission.get("constraints", [])
        st.info(f"**Hint:** Record yourself speaking in Spanish. Make sure to include: {', '.join(constraints[:3])}")

    # Submit
    if st.button("Submit Speaking Mission", type="primary", use_container_width=True):
        if transcript.strip():
            # Validate Spanish language first
            lang_info = detect_language(transcript)

            if lang_info["language"] == "english":
                st.markdown("""
                <div class="feedback-box feedback-error">
                    🌐 <strong>Please speak in Spanish!</strong> Your transcript appears to be in English.
                    Use the "Hint in English" button if you need help.
                </div>
                """, unsafe_allow_html=True)
            elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                st.markdown("""
                <div class="feedback-box feedback-warning">
                    🔀 <strong>Mixed language detected.</strong> Try speaking entirely in Spanish.
                </div>
                """, unsafe_allow_html=True)
            else:
                process_mission_response(mission, transcript, duration)
        else:
            st.warning("Please enter your transcript before submitting.")


def render_writing_input(mission: dict):
    """Render writing mission input."""
    st.markdown("### Write Your Response")
    st.markdown("*4-6 sentences recommended*")

    response = st.text_area(
        "Your written response:",
        value=st.session_state.dm_response,
        height=200,
        placeholder="Escriba su respuesta aqui...",
        key="writing_response"
    )
    st.session_state.dm_response = response

    # Word count
    word_count = len(response.split()) if response else 0
    st.caption(f"Word count: {word_count}")

    # Add hint button
    if st.button("💡 Hint in English", key="writing_hint"):
        constraints = mission.get("constraints", [])
        st.info(f"**Hint:** Write 4-6 sentences in Spanish. Make sure to include: {', '.join(constraints[:3])}")

    # Submit
    if st.button("Submit Writing Mission", type="primary", use_container_width=True):
        if response.strip():
            # Validate Spanish language first
            lang_info = detect_language(response)

            if lang_info["language"] == "english":
                st.markdown("""
                <div class="feedback-box feedback-error">
                    🌐 <strong>Please write in Spanish!</strong> Your response appears to be in English.
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
                process_mission_response(mission, response)
        else:
            st.warning("Please write your response before submitting.")


def process_mission_response(mission: dict, response: str, duration: int = 0):
    """Process and provide detailed feedback on mission response."""
    st.session_state.dm_submitted = True

    mission_type = mission.get("type", "writing")
    constraints = mission.get("constraints", [])

    # Run comprehensive evaluation
    evaluation = evaluate_mission_response(response, mission, duration)
    st.session_state.dm_evaluation = evaluation

    total_score = evaluation["overall_score"]

    # Save mission with detailed feedback
    feedback_json = json.dumps({
        "vocab_used": evaluation["vocab_used"],
        "structures_used": evaluation["structures_used"],
        "constraint_results": evaluation["constraint_feedback"],
        "errors": [e.get("original", "") for e in evaluation["error_feedback"]],
        "suggestions": evaluation["suggestions"],
    })

    mission_id = save_daily_mission({
        "date": date.today().isoformat(),
        "type": mission_type,
        "prompt": mission.get("prompt", ""),
        "constraints": constraints,
        "user_response": response,
        "feedback": feedback_json,
        "score": total_score,
        "completed": 1,
    })

    # Save transcript if speaking
    if mission_type == "speaking":
        save_transcript(response, duration, mission_id)
        record_progress({"speaking_minutes": duration / 60, "missions_completed": 1})
    else:
        record_progress({"writing_words": len(response.split()), "missions_completed": 1})

    # Log activity
    try:
        log_activity(
            activity_type="mission",
            activity_name=mission.get("title", "Daily Mission"),
            details=f"Score: {total_score}, Type: {mission_type}",
            score=total_score,
            duration_seconds=duration
        )
    except Exception:
        pass  # Activity logging is optional

    # Save individual mistakes to database for tracking
    for mistake in evaluation.get("mistakes", [])[:5]:
        try:
            save_mistake({
                "user_text": mistake.get("original", ""),
                "corrected_text": mistake.get("correction", ""),
                "error_type": mistake.get("tag", "other"),
                "error_tag": mistake.get("tag", "other"),
                "explanation": mistake.get("explanation", ""),
            })
        except Exception:
            pass

    # Display feedback
    st.divider()
    render_section_header("Mission Feedback")

    # Score display with breakdown
    score_color = "#10b981" if total_score >= 70 else "#f59e0b" if total_score >= 50 else "#ef4444"
    pass_status = "PASSED" if evaluation["is_passing"] else "NEEDS WORK"
    pass_color = "#10b981" if evaluation["is_passing"] else "#ef4444"

    st.markdown(f"""
    <div class="card" style="text-align: center; border-top: 4px solid {score_color};">
        <div class="metric-value" style="font-size: 3rem;">{total_score:.0f}</div>
        <div class="metric-label">Mission Score</div>
        <div style="margin-top: 0.5rem; color: {pass_color}; font-weight: 600;">{pass_status}</div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    st.markdown("### Score Breakdown")
    cols = st.columns(5)
    with cols[0]:
        st.metric("Vocabulary", f"{evaluation['vocab_score']}%")
    with cols[1]:
        st.metric("Grammar", f"{evaluation['grammar_score']}%")
    with cols[2]:
        st.metric("Constraints", f"{evaluation['constraint_score']}%")
    with cols[3]:
        st.metric("Accuracy", f"{evaluation['error_score']}%")
    with cols[4]:
        st.metric("Length", f"{evaluation['length_score']}%")

    # Vocabulary feedback
    if evaluation["vocab_feedback"]:
        st.markdown("### Vocabulary Check")
        for fb in evaluation["vocab_feedback"]:
            if fb["type"] == "success":
                st.markdown(f"""
                <div class="feedback-box feedback-success">
                    <strong>Found:</strong> {fb['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-box feedback-warning">
                    <strong>Missing:</strong> {fb['message']}<br>
                    <small>{fb.get('suggestion', '')}</small>
                </div>
                """, unsafe_allow_html=True)

    # Grammar feedback
    if evaluation["grammar_feedback"]:
        st.markdown("### Grammar Structures")
        for fb in evaluation["grammar_feedback"]:
            if fb["type"] == "success":
                st.markdown(f"""
                <div class="feedback-box feedback-success">
                    {fb['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-box feedback-warning">
                    {fb['message']}<br>
                    <small>Focus: {fb.get('focus', mission.get('grammar_focus', ''))}</small>
                </div>
                """, unsafe_allow_html=True)

    # Constraint results
    st.markdown("### Constraint Analysis")
    for fb in evaluation["constraint_feedback"]:
        icon = "check" if fb["met"] else "x"
        color = "#10b981" if fb["met"] else "#ef4444"
        st.markdown(f"""
        <div style="padding: 0.5rem; margin: 0.25rem 0; border-left: 3px solid {color}; background: rgba(0,0,0,0.02);">
            <strong style="color: {color};">{'[OK]' if fb['met'] else '[X]'}</strong> {fb['constraint']}<br>
            <small style="color: #666;">{fb['details']}</small>
        </div>
        """, unsafe_allow_html=True)

    # Error feedback
    if evaluation["error_feedback"]:
        st.markdown("### Corrections Needed")
        for error in evaluation["error_feedback"]:
            st.markdown(f"""
            <div class="feedback-box feedback-error">
                <strong>{error['original']}</strong> --&gt; <strong>{error['correction']}</strong><br>
                <small>{error['explanation']}</small>
                <div style="margin-top: 0.25rem;"><span class="pill pill-error">{error['tag']}</span></div>
            </div>
            """, unsafe_allow_html=True)

    # Suggestions
    if evaluation["suggestions"]:
        st.markdown("### Suggestions")
        for suggestion in evaluation["suggestions"]:
            st.info(suggestion)

    # Retry prompt
    st.markdown("### Retry Challenge")
    st.markdown("*Fix the issues above and write an improved version:*")

    retry = st.text_area(
        "Improved response:",
        height=100,
        key="retry_response"
    )

    # Get mistakes from evaluation
    original_mistakes = evaluation.get("mistakes", [])

    # Add hint button for retry
    if st.button("Hint in English", key="retry_hint"):
        if original_mistakes:
            st.info(f"**Hint:** Fix these errors: {original_mistakes[0].get('original', '')} should be {original_mistakes[0].get('correction', '')}")
        elif evaluation.get("suggestions"):
            st.info(f"**Hint:** {evaluation['suggestions'][0]}")
        else:
            st.info("**Hint:** Review the constraints above and make sure your Spanish is correct.")

    # Track retry submission state
    retry_submitted_key = "retry_submitted"
    retry_result_key = "retry_result"

    if retry_submitted_key not in st.session_state:
        st.session_state[retry_submitted_key] = False
        st.session_state[retry_result_key] = None

    if not st.session_state[retry_submitted_key]:
        if st.button("Submit Retry", type="primary"):
            if retry.strip():
                # Validate Spanish language first
                lang_info = detect_language(retry)

                if lang_info["language"] == "english":
                    st.session_state[retry_result_key] = {"type": "english"}
                elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                    st.session_state[retry_result_key] = {"type": "mixed"}
                else:
                    # Re-evaluate the retry response
                    retry_eval = evaluate_mission_response(retry, mission, 0)
                    retry_mistakes = retry_eval.get("mistakes", [])

                    if retry_eval["overall_score"] > evaluation["overall_score"]:
                        st.session_state[retry_result_key] = {
                            "type": "improved",
                            "new_score": retry_eval["overall_score"],
                            "old_score": evaluation["overall_score"]
                        }
                    elif len(retry_mistakes) < len(original_mistakes):
                        st.session_state[retry_result_key] = {
                            "type": "fewer_errors",
                            "old_errors": len(original_mistakes),
                            "new_errors": len(retry_mistakes)
                        }
                    else:
                        st.session_state[retry_result_key] = {"type": "needs_work"}

                st.session_state[retry_submitted_key] = True
                st.rerun()
            else:
                st.warning("Please enter your improved response.")
    else:
        # Show result
        result = st.session_state[retry_result_key]

        if result["type"] == "english":
            st.markdown("""
            <div class="feedback-box feedback-error">
                <strong>Please write in Spanish!</strong> Your retry appears to be in English.
            </div>
            """, unsafe_allow_html=True)
        elif result["type"] == "mixed":
            st.markdown("""
            <div class="feedback-box feedback-warning">
                <strong>Mixed language detected.</strong> Try writing entirely in Spanish.
            </div>
            """, unsafe_allow_html=True)
        elif result["type"] == "improved":
            st.markdown(f"""
            <div class="feedback-box feedback-success">
                <strong>Great improvement!</strong> Your score went from {result.get('old_score', 0):.0f} to {result.get('new_score', 0):.0f}!
            </div>
            """, unsafe_allow_html=True)
        elif result["type"] == "fewer_errors":
            st.markdown(f"""
            <div class="feedback-box feedback-success">
                <strong>Good progress!</strong> You reduced errors from {result.get('old_errors', 0)} to {result.get('new_errors', 0)}.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feedback-box feedback-info">
                Keep practicing! Review the corrections above.
            </div>
            """, unsafe_allow_html=True)

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Try Again", type="primary"):
                st.session_state[retry_submitted_key] = False
                st.session_state[retry_result_key] = None
                st.rerun()
        with col2:
            if st.button("New Mission"):
                st.session_state[retry_submitted_key] = False
                st.session_state[retry_result_key] = None
                st.session_state.dm_mission = None
                st.session_state.dm_submitted = False
                st.session_state.dm_evaluation = None
                st.rerun()
