"""Writing Coach with error feedback and forced re-production."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    record_progress, record_error_fingerprint, save_mistake, log_activity
)
from utils.content import (
    WRITING_COACH_TEMPLATES, PRAGMATICS_WARNINGS, RULE_BOUNDARIES
)
from utils.helpers import detect_language, seed_for_day


def render_writing_coach_page():
    """Render the Writing Coach page."""
    render_hero(
        title="Writing Coach",
        subtitle="Develop precision through constrained writing, error feedback, and forced re-production.",
        pills=["Error Type", "Rule", "Examples", "Rewrite"]
    )

    # Initialize session state
    if "wc_mode" not in st.session_state:
        st.session_state.wc_mode = "free_writing"
    if "wc_text" not in st.session_state:
        st.session_state.wc_text = ""
    if "wc_feedback" not in st.session_state:
        st.session_state.wc_feedback = None
    if "wc_rewrite_required" not in st.session_state:
        st.session_state.wc_rewrite_required = False
    if "wc_constraint" not in st.session_state:
        st.session_state.wc_constraint = None
    if "wc_original_errors" not in st.session_state:
        st.session_state.wc_original_errors = []

    # Mode selection
    render_section_header("Practice Mode")

    mode = st.radio(
        "Choose your practice mode:",
        [
            "Free Writing + Feedback",
            "Tone Transformation",
            "Constraint Rewrites",
            "Error Pattern Drills"
        ],
        horizontal=True
    )

    st.divider()

    if mode == "Free Writing + Feedback":
        render_free_writing()
    elif mode == "Tone Transformation":
        render_tone_transformation()
    elif mode == "Constraint Rewrites":
        render_constraint_rewrites()
    else:
        render_error_pattern_drills()


def render_free_writing():
    """Render free writing mode with detailed feedback."""
    render_section_header("Write and Get Feedback")

    st.markdown("""
    Write in Spanish about any topic. You'll receive detailed feedback on:
    - Grammar patterns (ser/estar, por/para, subjunctive)
    - Pragmatic appropriateness (too direct, register mismatch)
    - Common errors and calques
    """)

    # Text input
    text = st.text_area(
        "Write in Spanish:",
        value=st.session_state.wc_text,
        height=150,
        placeholder="Escriba su texto aquí...",
        key="free_writing_input"
    )
    st.session_state.wc_text = text

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Analyze My Writing", type="primary", use_container_width=True):
            if text.strip():
                # Validate Spanish
                lang_info = detect_language(text)
                if lang_info["language"] == "english":
                    st.warning("Please write in Spanish for feedback.")
                else:
                    feedback = analyze_writing(text)
                    st.session_state.wc_feedback = feedback
                    st.session_state.wc_original_errors = feedback.get("errors", [])

                    if feedback.get("errors"):
                        st.session_state.wc_rewrite_required = True
            else:
                st.warning("Please write something first.")

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.wc_text = ""
            st.session_state.wc_feedback = None
            st.session_state.wc_rewrite_required = False
            st.rerun()

    # Display feedback
    if st.session_state.wc_feedback:
        render_writing_feedback(st.session_state.wc_feedback)

        # Forced re-production section
        if st.session_state.wc_rewrite_required and st.session_state.wc_original_errors:
            st.divider()
            render_section_header("Forced Re-Production")

            st.markdown("""
            <div class="feedback-box feedback-warning">
                <strong>Practice makes permanent!</strong> Rewrite your text, correcting the errors identified above.
            </div>
            """, unsafe_allow_html=True)

            rewrite = st.text_area(
                "Rewrite your text with corrections:",
                height=150,
                placeholder="Escriba su texto corregido aquí...",
                key="rewrite_input"
            )

            if st.button("Check Rewrite", type="primary"):
                if rewrite.strip():
                    # Check if original errors are fixed
                    new_feedback = analyze_writing(rewrite)
                    new_errors = new_feedback.get("errors", [])

                    # Compare error types
                    original_types = {e["type"] for e in st.session_state.wc_original_errors}
                    new_types = {e["type"] for e in new_errors}

                    fixed_errors = original_types - new_types
                    remaining_errors = original_types & new_types

                    if not remaining_errors:
                        st.markdown("""
                        <div class="feedback-box feedback-success">
                            Excellent! You've corrected all the identified errors. Great practice!
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.wc_rewrite_required = False
                        record_progress({"errors_fixed": len(fixed_errors)})
                        log_activity("writing_coach", "rewrite_complete",
                                   f"Fixed {len(fixed_errors)} errors")
                    else:
                        st.markdown(f"""
                        <div class="feedback-box feedback-warning">
                            You fixed {len(fixed_errors)} error(s), but {len(remaining_errors)} type(s) remain.
                            Check the feedback above and try again.
                        </div>
                        """, unsafe_allow_html=True)

                    # Show new feedback
                    if new_errors:
                        render_writing_feedback(new_feedback)


def analyze_writing(text: str) -> dict:
    """Analyze writing for errors and provide detailed feedback."""
    feedback = {
        "errors": [],
        "pragmatics": [],
        "strengths": [],
        "suggestions": []
    }

    text_lower = text.lower()

    # Comprehensive error patterns for Spanish learners
    error_patterns = [
        # ============== GENDER AGREEMENT ERRORS ==============
        {
            "pattern": "la problema",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "greek_origin_ma",
            "correction": "el problema",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas: el problema, el tema, el sistema, el programa, el idioma.",
            "examples": ["el problema grave", "el tema interesante"],
        },
        {
            "pattern": "la sistema",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "greek_origin_ma",
            "correction": "el sistema",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas: el problema, el tema, el sistema, el programa, el idioma.",
            "examples": ["el sistema operativo", "el sistema nervioso"],
        },
        {
            "pattern": "la tema",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "greek_origin_ma",
            "correction": "el tema",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas: el problema, el tema, el sistema, el programa, el idioma.",
            "examples": ["el tema principal", "el tema de la reunión"],
        },
        {
            "pattern": "la programa",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "greek_origin_ma",
            "correction": "el programa",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas: el problema, el tema, el sistema, el programa, el idioma.",
            "examples": ["el programa de televisión", "el programa informático"],
        },
        {
            "pattern": "la idioma",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "greek_origin_ma",
            "correction": "el idioma",
            "rule": "Palabras terminadas en -ma de origen griego son masculinas: el problema, el tema, el sistema, el programa, el idioma.",
            "examples": ["el idioma español", "el idioma oficial"],
        },
        {
            "pattern": "el agua fría",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "feminine_el",
            "correction": "el agua fría (correcto - pero el adjetivo es femenino)",
            "rule": "Sustantivos femeninos que empiezan con 'a' tónica usan 'el' pero siguen siendo femeninos: el agua fría, el alma buena, el águila majestuosa.",
            "examples": ["el agua está fría", "el alma es eterna"],
        },
        {
            "pattern": "el agua frío",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "feminine_el",
            "correction": "el agua fría",
            "rule": "Aunque usamos 'el' antes de 'agua' (por empezar con 'a' tónica), agua sigue siendo femenino. Los adjetivos deben concordar en femenino: el agua fría, NO el agua frío.",
            "examples": ["el agua fría", "las aguas cristalinas", "el agua está contaminada"],
        },
        {
            "pattern": "la mano pequeño",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "irregular_gender",
            "correction": "la mano pequeña",
            "rule": "'Mano' es femenino aunque termine en -o. Siempre: la mano, las manos. Similar: la foto, la moto, la radio.",
            "examples": ["la mano derecha", "las manos limpias"],
        },
        {
            "pattern": "el mano",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "irregular_gender",
            "correction": "la mano",
            "rule": "'Mano' es femenino aunque termine en -o. Es una excepción importante. Similar: la foto, la moto, la radio.",
            "examples": ["la mano izquierda", "dame la mano"],
        },
        {
            "pattern": "el foto",
            "type": "gender_agreement",
            "category": "agreement",
            "subcategory": "irregular_gender",
            "correction": "la foto",
            "rule": "'Foto' es femenino (abreviatura de 'fotografía'). También: la moto (motocicleta), la radio (radiodifusión).",
            "examples": ["la foto borrosa", "las fotos del viaje"],
        },

        # ============== SER/ESTAR CONFUSION ==============
        {
            "pattern": "soy aburrido",
            "type": "ser_estar",
            "category": "copula",
            "subcategory": "adjective_meaning_change",
            "correction": "estoy aburrido (si te aburres) / soy aburrido (si eres una persona aburrida)",
            "rule": "Muchos adjetivos cambian de significado con ser/estar. 'Soy aburrido' = I'm a boring person. 'Estoy aburrido' = I'm bored right now.",
            "examples": ["Estoy aburrido en clase (feeling)", "Es una persona aburrida (characteristic)"],
        },
        {
            "pattern": "estoy listo para",
            "type": "ser_estar",
            "category": "copula",
            "subcategory": "adjective_meaning_change",
            "correction": "estoy listo (ready) - correcto / soy listo (clever)",
            "rule": "'Ser listo' = to be clever/smart. 'Estar listo' = to be ready. Contexto: 'Estoy listo para el examen' (ready) vs 'Soy muy listo' (clever).",
            "examples": ["Estoy listo para salir", "Mi hermano es muy listo"],
        },
        {
            "pattern": "soy enfermo",
            "type": "ser_estar",
            "category": "copula",
            "subcategory": "temporary_states",
            "correction": "estoy enfermo",
            "rule": "Estados temporales como enfermedad usan 'estar'. 'Soy enfermo' implicaría una condición permanente o que eres una persona enferma por naturaleza.",
            "examples": ["Estoy enfermo hoy", "Está cansada", "Estamos contentos"],
        },
        {
            "pattern": "es en",
            "type": "ser_estar",
            "category": "copula",
            "subcategory": "location_event",
            "correction": "está en (para ubicación) / es en (para eventos)",
            "rule": "Ubicación física = estar. Eventos = ser. 'La oficina está en el centro' (location). 'La fiesta es en mi casa' (event).",
            "examples": ["El libro está en la mesa", "La reunión es en la sala 3"],
        },

        # ============== FALSE FRIENDS ==============
        {
            "pattern": "estoy excitado",
            "type": "false_friend",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "estoy emocionado/entusiasmado",
            "rule": "'Excitado' tiene connotación sexual en español. Para expresar entusiasmo, usa 'emocionado', 'entusiasmado', o 'ilusionado'.",
            "examples": ["Estoy muy emocionado por el viaje", "Estoy entusiasmado con el proyecto"],
        },
        {
            "pattern": "realizar que",
            "type": "false_friend",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "darse cuenta de que",
            "rule": "'Realizar' significa 'llevar a cabo' o 'cumplir'. Para 'realize' (entender), usa 'darse cuenta de'.",
            "examples": ["Me di cuenta de que era tarde", "Realizamos el proyecto (we carried out)"],
        },
        {
            "pattern": "estoy embarazada",
            "type": "false_friend",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "estoy avergonzada/avergonzado (si significa 'embarrassed')",
            "rule": "'Embarazada' significa 'pregnant'. Para 'embarrassed', usa 'avergonzado/a' o 'me da vergüenza'.",
            "examples": ["Estoy avergonzada por mi error", "Me dio mucha vergüenza"],
        },
        {
            "pattern": "la librería",
            "type": "false_friend_context",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "la biblioteca (para estudiar) / la librería (para comprar libros)",
            "rule": "'Librería' = bookstore (donde compras libros). 'Biblioteca' = library (donde estudias o tomas libros prestados).",
            "examples": ["Fui a la biblioteca a estudiar", "Compré el libro en la librería"],
        },
        {
            "pattern": "sensible",
            "type": "false_friend_context",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "sensato/a (para 'sensible') / sensible (para 'sensitive')",
            "rule": "'Sensible' = sensitive (emotionally). Para 'sensible' (razonable), usa 'sensato/a' o 'razonable'.",
            "examples": ["Es una persona muy sensible (sensitive)", "Esa es una decisión sensata (sensible)"],
        },
        {
            "pattern": "soportar",
            "type": "false_friend_context",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "apoyar (para 'support') / soportar (para 'tolerate')",
            "rule": "'Soportar' = to tolerate/endure. Para 'support', usa 'apoyar' (ayudar) o 'mantener' (financially).",
            "examples": ["Te apoyo en tu decisión (I support)", "No soporto el ruido (I can't stand)"],
        },
        {
            "pattern": "actualmente",
            "type": "false_friend_context",
            "category": "vocabulary",
            "subcategory": "false_friends",
            "correction": "en realidad/de hecho (para 'actually') / actualmente (para 'currently')",
            "rule": "'Actualmente' = currently/nowadays. Para 'actually', usa 'en realidad', 'de hecho', o 'la verdad es que'.",
            "examples": ["Actualmente vivo en Madrid (currently)", "En realidad, no estoy de acuerdo (actually)"],
        },

        # ============== PREPOSITION ERRORS ==============
        {
            "pattern": "estudio por",
            "type": "por_para",
            "category": "prepositions",
            "subcategory": "por_para",
            "correction": "estudio para",
            "rule": "'Para' indica propósito/objetivo. 'Por' indica causa/razón. 'Estudio para aprobar' (purpose). 'Lo hago por ti' (because of you).",
            "examples": ["Estudio para ser médico", "Trabajo para vivir"],
        },
        {
            "pattern": "depende en",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "verb_preposition",
            "correction": "depende de",
            "rule": "El verbo 'depender' siempre se construye con 'de'. Es un error común por influencia del inglés 'depend on'.",
            "examples": ["Depende de la situación", "Dependemos de tu respuesta"],
        },
        {
            "pattern": "pensar sobre",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "verb_preposition",
            "correction": "pensar en",
            "rule": "'Pensar' + en (to think about). 'Pensar sobre' es un calco del inglés 'think about'.",
            "examples": ["Pienso en ti", "Estoy pensando en el problema"],
        },
        {
            "pattern": "soñar sobre",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "verb_preposition",
            "correction": "soñar con",
            "rule": "'Soñar' + con (to dream about). Es el régimen preposicional correcto en español.",
            "examples": ["Soñé contigo anoche", "Sueño con viajar"],
        },
        {
            "pattern": "casarse a",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "verb_preposition",
            "correction": "casarse con",
            "rule": "'Casarse' + con (to marry). 'Se casó con María' = He married María.",
            "examples": ["Me casé con mi mejor amigo", "Van a casarse con ceremonia civil"],
        },
        {
            "pattern": "consistir de",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "verb_preposition",
            "correction": "consistir en",
            "rule": "'Consistir' + en (to consist of). Calco del inglés 'consist of'.",
            "examples": ["El examen consiste en tres partes", "El trabajo consiste en revisar documentos"],
        },
        {
            "pattern": "en el mañana",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "time_expressions",
            "correction": "por la mañana",
            "rule": "Partes del día: 'por la mañana', 'por la tarde', 'por la noche'. NO 'en la mañana' (aunque se usa en algunas regiones).",
            "examples": ["Trabajo por la mañana", "Estudio por la noche"],
        },
        {
            "pattern": "en la noche",
            "type": "preposition",
            "category": "prepositions",
            "subcategory": "time_expressions",
            "correction": "por la noche (o 'de noche' para generalizar)",
            "rule": "En español peninsular estándar: 'por la noche' (at night). 'De noche' = nighttime in general.",
            "examples": ["Salimos por la noche", "De noche hace frío"],
        },

        # ============== SUBJUNCTIVE TRIGGERS ==============
        {
            "pattern": "quiero que vienes",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "quiero que vengas",
            "rule": "Expresiones de deseo + que + subjuntivo. 'Querer que', 'desear que', 'esperar que' siempre llevan subjuntivo.",
            "examples": ["Quiero que vengas", "Espero que estés bien", "Deseo que tengas suerte"],
        },
        {
            "pattern": "cuando llega",
            "type": "subjunctive_future",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "cuando llegue",
            "rule": "'Cuando' + acción futura requiere subjuntivo. 'Cuando llegue' (when he/she arrives - future). Pero: 'Cuando llega, siempre...' (habitual - indicativo).",
            "examples": ["Cuando llegues, llámame", "Cuando termine, te aviso"],
        },
        {
            "pattern": "ojalá viene",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "ojalá venga / ojalá viniera",
            "rule": "'Ojalá' SIEMPRE lleva subjuntivo. 'Ojalá + presente subjuntivo' (esperanza posible). 'Ojalá + imperfecto subjuntivo' (deseo menos probable).",
            "examples": ["Ojalá venga mañana", "Ojalá tuviera más tiempo"],
        },
        {
            "pattern": "es necesario que tienes",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "es necesario que tengas",
            "rule": "Expresiones impersonales de necesidad/duda/emoción + que + subjuntivo: 'es necesario que', 'es importante que', 'es posible que'.",
            "examples": ["Es necesario que vengas", "Es importante que lo sepas"],
        },
        {
            "pattern": "dudo que es",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "dudo que sea",
            "rule": "Verbos de duda + que + subjuntivo. 'Dudar que', 'no creer que', 'no pensar que' llevan subjuntivo.",
            "examples": ["Dudo que sea verdad", "No creo que venga"],
        },
        {
            "pattern": "antes de que llega",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "antes de que llegue",
            "rule": "'Antes de que' SIEMPRE lleva subjuntivo, incluso para acciones pasadas.",
            "examples": ["Antes de que llegue", "Antes de que te vayas"],
        },
        {
            "pattern": "para que puedes",
            "type": "subjunctive",
            "category": "verb_tense",
            "subcategory": "subjunctive_triggers",
            "correction": "para que puedas",
            "rule": "'Para que' (so that) SIEMPRE lleva subjuntivo porque expresa propósito.",
            "examples": ["Te lo digo para que sepas", "Lo hago para que puedas entender"],
        },

        # ============== ACCENT ERRORS ==============
        {
            "pattern": " si ",
            "type": "accent_check",
            "category": "orthography",
            "subcategory": "accent_meaning",
            "correction": "si (if) vs sí (yes)",
            "rule": "'Si' (sin tilde) = if. 'Sí' (con tilde) = yes. Contexto: 'Si vienes, te veo' (if) vs 'Sí, vengo' (yes).",
            "examples": ["Si quieres, vamos (if)", "Sí, claro que sí (yes)"],
        },
        {
            "pattern": " tu ",
            "type": "accent_check",
            "category": "orthography",
            "subcategory": "accent_meaning",
            "correction": "tu (your) vs tú (you)",
            "rule": "'Tu' (sin tilde) = your. 'Tú' (con tilde) = you. 'Tu casa' (your house) vs 'Tú vienes' (you come).",
            "examples": ["Tu libro (your)", "Tú sabes (you)"],
        },
        {
            "pattern": " el ",
            "type": "accent_check",
            "category": "orthography",
            "subcategory": "accent_meaning",
            "correction": "el (the) vs él (he)",
            "rule": "'El' (sin tilde) = the. 'Él' (con tilde) = he. 'El libro' (the book) vs 'Él viene' (he comes).",
            "examples": ["El coche es rojo (the)", "Él es mi amigo (he)"],
        },
        {
            "pattern": "que bueno",
            "type": "accent_exclamation",
            "category": "orthography",
            "subcategory": "accent_meaning",
            "correction": "¡qué bueno!",
            "rule": "'Qué' lleva tilde en exclamaciones e interrogaciones. 'Que' sin tilde es conjunción: 'Creo que sí' vs '¡Qué bien!'",
            "examples": ["¡Qué interesante!", "¿Qué hora es?", "Creo que viene (no tilde)"],
        },
        {
            "pattern": "como estas",
            "type": "accent_interrogative",
            "category": "orthography",
            "subcategory": "accent_meaning",
            "correction": "¿cómo estás?",
            "rule": "'Cómo' lleva tilde en preguntas. 'Como' sin tilde = as/like. '¿Cómo estás?' vs 'Como siempre'.",
            "examples": ["¿Cómo te llamas?", "Lo hice como me dijiste (no tilde)"],
        },

        # ============== COMMON ANGLICISMS AND CALQUES ==============
        {
            "pattern": "aplicar para",
            "type": "calque",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "solicitar / presentarse a",
            "rule": "'Aplicar para' es un calco del inglés 'apply for'. En español: 'solicitar un puesto', 'presentarse a una convocatoria'.",
            "examples": ["Solicité el puesto", "Me presenté a la beca"],
        },
        {
            "pattern": "llamar para atrás",
            "type": "calque",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "devolver la llamada",
            "rule": "'Llamar para atrás' es un calco de 'call back'. Usa 'devolver la llamada' o 'volver a llamar'.",
            "examples": ["Te devuelvo la llamada", "Vuelvo a llamarte luego"],
        },
        {
            "pattern": "tener sentido",
            "type": "calque_context",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "tener sentido (correcto) - pero ojo con 'hacer sentido' (incorrecto)",
            "rule": "'Tener sentido' es correcto. 'Hacer sentido' es un calco del inglés 'make sense'. Siempre: 'tiene sentido', nunca 'hace sentido'.",
            "examples": ["Esto tiene sentido", "No tiene ningún sentido"],
        },
        {
            "pattern": "hacer sentido",
            "type": "calque",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "tener sentido",
            "rule": "'Hacer sentido' es un calco del inglés 'make sense'. En español correcto: 'tener sentido'.",
            "examples": ["Esto tiene sentido", "¿Tiene sentido lo que digo?"],
        },
        {
            "pattern": "en orden a",
            "type": "calque",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "para / con el fin de",
            "rule": "'En orden a' es un calco de 'in order to'. Usa 'para' o 'con el fin de'.",
            "examples": ["Estudio para aprobar", "Lo hago con el fin de mejorar"],
        },
        {
            "pattern": "asumir que",
            "type": "calque_context",
            "category": "vocabulary",
            "subcategory": "anglicisms",
            "correction": "suponer que / dar por hecho que",
            "rule": "'Asumir' en español significa 'aceptar responsabilidad'. Para 'assume' (suponer), usa 'suponer', 'dar por hecho', o 'presumir'.",
            "examples": ["Supongo que vendrá", "Doy por hecho que lo sabe"],
        },

        # ============== OTHER COMMON ERRORS ==============
        {
            "pattern": "más mejor",
            "type": "redundancy",
            "category": "grammar",
            "subcategory": "comparative",
            "correction": "mejor",
            "rule": "'Mejor' ya es comparativo. No se dice 'más mejor' ni 'más peor'. Similarmente: mayor, menor, superior, inferior.",
            "examples": ["Este es mejor", "Es el mayor de los hermanos"],
        },
        {
            "pattern": "más peor",
            "type": "redundancy",
            "category": "grammar",
            "subcategory": "comparative",
            "correction": "peor",
            "rule": "'Peor' ya es comparativo. No necesita 'más'. Lo mismo aplica a mejor, mayor, menor.",
            "examples": ["La situación es peor", "Este resultado es peor que el anterior"],
        },
        {
            "pattern": "hubieron muchos",
            "type": "verb_agreement",
            "category": "grammar",
            "subcategory": "haber_impersonal",
            "correction": "hubo muchos",
            "rule": "El verbo 'haber' impersonal es siempre singular: 'Hay problemas', 'Hubo problemas', 'Había problemas'. NUNCA 'Habían problemas'.",
            "examples": ["Hubo muchos invitados", "Hay varias opciones", "Había muchos coches"],
        },
        {
            "pattern": "habían muchos",
            "type": "verb_agreement",
            "category": "grammar",
            "subcategory": "haber_impersonal",
            "correction": "había muchos",
            "rule": "El verbo 'haber' impersonal es siempre singular. 'Había muchos' (there were many), NO 'habían muchos'.",
            "examples": ["Había muchas personas", "Hay que estudiar más"],
        },
        {
            "pattern": "la gente son",
            "type": "verb_agreement",
            "category": "grammar",
            "subcategory": "collective_nouns",
            "correction": "la gente es",
            "rule": "'Gente' es singular gramaticalmente aunque se refiera a muchas personas. 'La gente es amable', NO 'la gente son amables'.",
            "examples": ["La gente es muy simpática", "La gente aquí habla español"],
        },
    ]

    for pattern_data in error_patterns:
        if pattern_data["pattern"] in text_lower:
            error = {
                "type": pattern_data["type"],
                "category": pattern_data["category"],
                "subcategory": pattern_data["subcategory"],
                "found": pattern_data["pattern"],
                "correction": pattern_data["correction"],
                "rule": pattern_data["rule"],
                "examples": pattern_data.get("examples", []),
            }
            feedback["errors"].append(error)

            # Record in fingerprint system
            record_error_fingerprint(
                pattern_data["category"],
                pattern_data["subcategory"],
                is_error=True,
                user_input=pattern_data["pattern"],
                expected=pattern_data["correction"],
                rule_explanation=pattern_data["rule"]
            )

    # Check pragmatics issues
    for warning in PRAGMATICS_WARNINGS:
        if warning["pattern"].lower() in text_lower:
            feedback["pragmatics"].append({
                "pattern": warning["pattern"],
                "issue": warning["issue"],
                "explanation": warning["explanation"],
                "alternatives": warning["alternatives"],
            })

    # Check for strengths with more detailed feedback
    strength_markers = [
        ("me parece que", "Good use of hedging! 'Me parece que' softens opinions nicely."),
        ("tal vez", "Nice use of softening language with 'tal vez'."),
        ("sin embargo", "Great use of contrast marker 'sin embargo' - more formal than 'pero'."),
        ("aunque", "Good concessive construction with 'aunque'."),
        ("le agradecería", "Excellent formal politeness marker! Perfect for professional contexts."),
        ("quisiera", "Great use of polite conditional 'quisiera'."),
        ("sería posible", "Excellent politeness strategy with conditional questions."),
        ("a mi modo de ver", "Sophisticated hedging expression!"),
        ("no obstante", "Excellent formal connector - shows advanced writing."),
        ("cabe destacar", "Very professional and academic expression."),
        ("en cuanto a", "Good topic organizer for structured writing."),
        ("por un lado", "Great for presenting balanced arguments."),
        ("hubiera", "Good use of subjunctive - shows grammar sophistication."),
        ("haya", "Correct present perfect subjunctive usage."),
    ]

    for marker, msg in strength_markers:
        if marker in text_lower:
            feedback["strengths"].append(msg)

    # Add suggestions based on text length and content
    word_count = len(text.split())
    if word_count < 20:
        feedback["suggestions"].append("Try writing longer texts (20+ words) for more comprehensive practice.")

    if "pero" in text_lower and "sin embargo" not in text_lower:
        feedback["suggestions"].append("Consider using 'sin embargo' or 'no obstante' for more formal contrast.")

    if "pienso que" in text_lower and "me parece que" not in text_lower:
        feedback["suggestions"].append("Try 'me parece que' or 'a mi modo de ver' for softer opinion expression.")

    if "quiero" in text_lower and "quisiera" not in text_lower and "me gustaría" not in text_lower:
        feedback["suggestions"].append("For politeness, consider 'quisiera' or 'me gustaría' instead of 'quiero'.")

    # Check for text complexity and provide encouragement
    if word_count >= 50:
        feedback["suggestions"].append("Great effort with a longer text! Keep practicing extended writing.")

    # Check for variety in sentence starters
    sentences = text.split('.')
    if len(sentences) > 3:
        first_words = [s.strip().split()[0].lower() if s.strip() else '' for s in sentences if s.strip()]
        if len(set(first_words)) < len(first_words) * 0.6:
            feedback["suggestions"].append("Try varying your sentence starters for more engaging writing.")

    return feedback


def render_writing_feedback(feedback: dict):
    """Render detailed feedback for writing with educational explanations."""
    st.divider()
    render_section_header("Feedback")

    # Calculate overall score for motivation
    total_errors = len(feedback.get("errors", []))
    total_strengths = len(feedback.get("strengths", []))

    # Show summary metrics
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        if total_errors == 0:
            st.metric("Areas to Review", "None found", delta="Excellent!")
        else:
            st.metric("Areas to Review", total_errors)
    with col_metric2:
        st.metric("Strengths Detected", total_strengths)
    with col_metric3:
        pragmatic_count = len(feedback.get("pragmatics", []))
        st.metric("Pragmatic Notes", pragmatic_count)

    st.divider()

    # Errors section with enhanced educational feedback
    if feedback.get("errors"):
        st.markdown("### Areas to Polish")
        st.markdown("Review these patterns to strengthen your Spanish writing:")

        for i, error in enumerate(feedback["errors"], 1):
            # Create a clear, educational expander title
            error_type_display = error['type'].replace('_', ' ').title()
            category_icon = _get_category_icon(error['category'])

            with st.expander(
                f"{category_icon} **{error_type_display}**: `{error['found']}`",
                expanded=(i <= 2)  # Auto-expand first two errors
            ):
                # Side-by-side comparison
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**What you wrote:**")
                    st.markdown(
                        f"<div style='background-color: #fff3cd; padding: 12px; "
                        f"border-radius: 8px; border-left: 4px solid #ffc107; "
                        f"font-family: monospace;'>{error['found']}</div>",
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown("**Suggested correction:**")
                    st.markdown(
                        f"<div style='background-color: #d4edda; padding: 12px; "
                        f"border-radius: 8px; border-left: 4px solid #28a745; "
                        f"font-family: monospace;'>{error['correction']}</div>",
                        unsafe_allow_html=True
                    )

                # Rule explanation in a highlighted box
                if error.get("rule"):
                    st.markdown("---")
                    st.markdown("**The Rule:**")
                    st.info(error['rule'])

                # Show examples if available
                examples = error.get("examples", [])
                if examples:
                    st.markdown("**Correct Examples:**")
                    example_html = "<ul style='margin: 0; padding-left: 20px;'>"
                    for ex in examples[:3]:  # Show up to 3 examples
                        example_html += f"<li><code>{ex}</code></li>"
                    example_html += "</ul>"
                    st.markdown(example_html, unsafe_allow_html=True)

                # Show related boundary cases if available
                boundary = RULE_BOUNDARIES.get(error["type"])
                if boundary:
                    st.markdown("---")
                    st.markdown("**Nuances to Remember:**")
                    for case in boundary.get("boundary_cases", [])[:2]:
                        st.markdown(
                            f"<div style='background-color: #e7f3ff; padding: 10px; "
                            f"border-radius: 6px; margin-bottom: 8px;'>"
                            f"<strong>{case['case']}</strong>: {case['explanation']}"
                            f"<br><em>Example: {case.get('example', '')}</em></div>",
                            unsafe_allow_html=True
                        )

                # Category tag for reference
                st.caption(f"Category: {error['category'].title()} > {error['subcategory'].replace('_', ' ').title()}")
    else:
        st.markdown("""
        <div style="background-color: #d4edda; padding: 20px; border-radius: 10px;
                    border-left: 5px solid #28a745; text-align: center;">
            <h4 style="color: #155724; margin: 0;">Excellent Work!</h4>
            <p style="color: #155724; margin: 10px 0 0 0;">
                No major grammatical issues detected in your writing.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Pragmatics section with detailed explanations
    if feedback.get("pragmatics"):
        st.markdown("### Pragmatic Considerations")
        st.markdown("These are cultural and communicative nuances to be aware of:")

        for pragma in feedback["pragmatics"]:
            issue_title = pragma['issue'].replace('_', ' ').title()

            st.markdown(
                f"""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px;
                            border-left: 5px solid #ffc107; margin-bottom: 15px;">
                    <h5 style="color: #856404; margin: 0 0 10px 0;">{issue_title}</h5>
                    <p style="color: #856404; margin: 0 0 10px 0;">
                        <strong>Pattern found:</strong> <code>{pragma['pattern']}</code>
                    </p>
                    <p style="color: #856404; margin: 0 0 10px 0;">
                        {pragma['explanation']}
                    </p>
                    <p style="color: #856404; margin: 0;">
                        <strong>Native-like alternatives:</strong><br>
                        {' / '.join(pragma['alternatives'][:4])}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Strengths section with encouragement
    if feedback.get("strengths"):
        st.markdown("### What You Did Well")
        st.markdown("These elements show strong Spanish writing skills:")

        strength_html = "<div style='background-color: #d4edda; padding: 15px; border-radius: 10px;'><ul style='margin: 0; padding-left: 20px;'>"
        for strength in feedback["strengths"]:
            strength_html += f"<li style='color: #155724; margin-bottom: 5px;'>{strength}</li>"
        strength_html += "</ul></div>"
        st.markdown(strength_html, unsafe_allow_html=True)

    # Suggestions section
    if feedback.get("suggestions"):
        st.markdown("### Tips for Improvement")
        for suggestion in feedback["suggestions"]:
            st.markdown(
                f"<div style='padding: 8px 12px; background-color: #e7f3ff; "
                f"border-radius: 6px; margin-bottom: 8px;'>"
                f"<span style='margin-right: 8px;'>Tip:</span> {suggestion}</div>",
                unsafe_allow_html=True
            )


def _get_category_icon(category: str) -> str:
    """Return an appropriate text indicator for error category."""
    icons = {
        "agreement": "[Gender]",
        "copula": "[Ser/Estar]",
        "vocabulary": "[Vocab]",
        "prepositions": "[Prep]",
        "verb_tense": "[Tense]",
        "orthography": "[Spelling]",
        "grammar": "[Grammar]",
    }
    return icons.get(category, "[Note]")


def render_tone_transformation():
    """Render tone transformation exercises with educational guidance."""
    render_section_header("Tone Transformation")

    st.markdown("""
    Practice adjusting register and tone - a crucial skill for effective Spanish communication.
    You'll transform sentences between formal/informal registers and direct/polite tones.
    """)

    # Educational sidebar about register markers
    with st.expander("Register Transformation Guide", expanded=False):
        st.markdown("""
        **Key Markers for Register Transformation:**

        **Formal to Informal:**
        - Change `usted` to `tu`
        - Replace `Le agradeceria` with `¿Podrías...?`
        - Use contractions and casual expressions
        - Add informal closings: `Saludos`, `Un abrazo`

        **Informal to Formal:**
        - Change `tu` to `usted`
        - Use conditional: `quisiera`, `podría`, `sería posible`
        - Add politeness markers: `por favor`, `si no es molestia`
        - Formal closings: `Atentamente`, `Cordialmente`

        **Direct to Polite:**
        - Add hedging: `quizá`, `tal vez`, `me parece que`
        - Use questions instead of commands
        - Add appreciation: `Te lo agradecería mucho`
        - Soften with conditionals: `¿Podrías...?` vs `Hazlo`
        """)

    templates = WRITING_COACH_TEMPLATES.get("tone_rewrites", {})

    # Select transformation type with better descriptions
    transform_descriptions = {
        "formal_to_informal": "Formal to Informal - Make it casual and friendly",
        "informal_to_formal": "Informal to Formal - Make it professional",
        "direct_to_polite": "Direct to Polite - Soften the request"
    }

    transform_type = st.selectbox(
        "Choose transformation type:",
        list(templates.keys()),
        format_func=lambda x: transform_descriptions.get(x, x.replace("_", " ").title())
    )

    template = templates.get(transform_type, {})

    if template:
        # Show instruction with context
        st.markdown(
            f"<div style='background-color: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>"
            f"<strong>Your Task:</strong> {template.get('instruction', '')}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Determine which example to show based on the transformation
        if "informal" in transform_type.lower() and "to_informal" in transform_type.lower():
            source = template.get("example_formal", "")
            target = template.get("example_informal", "")
            source_label = "Formal Version (Transform this)"
            target_label = "Informal Version"
            tips = [
                "Change 'usted' pronouns to 'tu'",
                "Use more casual greetings like 'Oye' or 'Hola'",
                "Replace formal phrases with everyday equivalents",
                "Consider adding colloquial expressions"
            ]
        elif "formal" in transform_type.lower():
            source = template.get("example_informal", "")
            target = template.get("example_formal", "")
            source_label = "Informal Version (Transform this)"
            target_label = "Formal Version"
            tips = [
                "Change 'tu' to 'usted' throughout",
                "Use conditional verbs: 'quisiera', 'podria'",
                "Add politeness phrases: 'Le agradeceria...'",
                "Use formal vocabulary and complete sentences"
            ]
        else:
            source = template.get("example_direct", "")
            target = template.get("example_polite", "")
            source_label = "Direct Version (Transform this)"
            target_label = "Polite Version"
            tips = [
                "Convert commands to questions",
                "Add 'por favor' or 'si es posible'",
                "Use hedging: 'tal vez', 'quiza'",
                "Express appreciation: 'Te lo agradeceria'"
            ]

        # Source sentence display
        st.markdown(f"**{source_label}:**")
        st.markdown(
            f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; "
            f"border: 2px solid #dee2e6; font-size: 1.1em;'>{source}</div>",
            unsafe_allow_html=True
        )

        # Tips for this transformation
        st.markdown("**Transformation Tips:**")
        tips_html = "<ul style='margin: 5px 0;'>"
        for tip in tips:
            tips_html += f"<li>{tip}</li>"
        tips_html += "</ul>"
        st.markdown(tips_html, unsafe_allow_html=True)

        # User attempt with helpful placeholder
        user_attempt = st.text_area(
            f"Write your {target_label.split(' ')[0].lower()} version:",
            height=120,
            placeholder=f"Reescribe el texto de forma {'informal' if 'informal' in target_label.lower() else 'formal' if 'formal' in target_label.lower() else 'cortés'}...",
            key="tone_transform_input"
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Check My Version", type="primary", use_container_width=True):
                if user_attempt.strip():
                    # Validate Spanish
                    lang_info = detect_language(user_attempt)
                    if lang_info["language"] == "english":
                        st.warning("Please write in Spanish.")
                    else:
                        st.markdown("---")
                        st.markdown("**Model Answer:**")
                        st.markdown(
                            f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; "
                            f"border: 2px solid #28a745; font-size: 1.1em;'>{target}</div>",
                            unsafe_allow_html=True
                        )

                        # Provide comparison feedback
                        st.markdown("---")
                        st.markdown("**Self-Assessment Checklist:**")
                        _render_tone_checklist(transform_type, user_attempt, target)

                        record_progress({"writing_words": len(user_attempt.split())})
                        log_activity("writing_coach", "tone_transformation", transform_type)
                else:
                    st.warning("Please write your transformation first.")

        with col2:
            if st.button("Show Model Answer", use_container_width=True):
                st.markdown(f"**{target_label}:**")
                st.markdown(
                    f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; "
                    f"font-size: 1.1em;'>{target}</div>",
                    unsafe_allow_html=True
                )


def _render_tone_checklist(transform_type: str, user_text: str, model_text: str):
    """Render a self-assessment checklist for tone transformation."""
    user_lower = user_text.lower()

    checks = []

    if "formal" in transform_type and "to_formal" in transform_type:
        checks = [
            ("Used 'usted' forms", "usted" in user_lower or "le " in user_lower),
            ("Used conditional verbs", any(w in user_lower for w in ["ría", "quisiera", "podría", "sería"])),
            ("Added politeness markers", any(w in user_lower for w in ["por favor", "agradecería", "si es posible"])),
            ("Formal vocabulary", any(w in user_lower for w in ["informo", "solicito", "atentamente"])),
        ]
    elif "informal" in transform_type:
        checks = [
            ("Used 'tu' forms", any(w in user_lower for w in ["tu ", "tú ", "puedes", "tienes", "quieres"])),
            ("Casual greeting/tone", any(w in user_lower for w in ["oye", "hola", "vale", "genial"])),
            ("Shortened expressions", len(user_text) <= len(model_text) * 1.2),
            ("Natural flow", True),  # Always positive for encouragement
        ]
    else:  # direct to polite
        checks = [
            ("Used question form", "?" in user_text),
            ("Added softening words", any(w in user_lower for w in ["tal vez", "quizá", "podría", "sería posible"])),
            ("Expressed appreciation", any(w in user_lower for w in ["gracias", "agradecería", "agradezco"])),
            ("Used conditional", any(w in user_lower for w in ["ría", "podría", "sería"])),
        ]

    for label, passed in checks:
        icon = "[OK]" if passed else "[ ]"
        color = "#28a745" if passed else "#6c757d"
        st.markdown(
            f"<span style='color: {color}; font-family: monospace;'>{icon}</span> {label}",
            unsafe_allow_html=True
        )


def render_constraint_rewrites():
    """Render constraint-based rewrite exercises with educational guidance."""
    render_section_header("Constraint Rewrites")

    st.markdown("""
    Rewrite sentences with specific grammatical constraints. This powerful exercise builds
    flexibility and helps you internalize grammar patterns through active practice.
    """)

    # Constraint type explanations
    constraint_guides = {
        "imperfecto": {
            "name": "Imperfect Tense",
            "explanation": "The imperfect tense describes ongoing or habitual past actions.",
            "markers": ["siempre", "antes", "cuando era", "de niño", "todos los días"],
            "pattern": "Transform completed actions into habitual/ongoing ones"
        },
        "conditional": {
            "name": "Conditional Mood",
            "explanation": "The conditional softens requests and expresses hypotheticals.",
            "markers": ["ría", "rías", "ría", "ríamos", "rían"],
            "pattern": "Transform direct statements into polite/hypothetical ones"
        },
        "passive": {
            "name": "Passive Voice",
            "explanation": "Passive voice emphasizes the action rather than the actor.",
            "markers": ["fue/fueron + participle", "es/son + participle", "se + verb"],
            "pattern": "Transform active sentences to focus on what happened, not who did it"
        },
        "subjunctive": {
            "name": "Subjunctive Mood",
            "explanation": "The subjunctive expresses wishes, doubts, and emotions.",
            "markers": ["que + subjunctive", "ojalá", "espero que", "dudo que"],
            "pattern": "Transform indicative statements to express desire or uncertainty"
        },
    }

    constraints = WRITING_COACH_TEMPLATES.get("constraint_rewrites", [])

    if not constraints:
        st.warning("No constraint exercises available.")
        return

    # Allow user to select constraint type or get random
    constraint_types = list(set(c.get("constraint", "other") for c in constraints))

    col_select1, col_select2 = st.columns([2, 1])
    with col_select1:
        selected_constraint = st.selectbox(
            "Focus on specific constraint:",
            ["Random"] + constraint_types,
            format_func=lambda x: x.title() if x != "Random" else "Random Selection"
        )

    with col_select2:
        if st.button("Get New Exercise", use_container_width=True):
            st.session_state.constraint_seed = random.randint(1, 10000)
            st.rerun()

    # Get exercise based on selection
    if "constraint_seed" not in st.session_state:
        st.session_state.constraint_seed = seed_for_day(date.today())

    random.seed(st.session_state.constraint_seed)

    if selected_constraint == "Random":
        exercise = random.choice(constraints)
    else:
        filtered = [c for c in constraints if c.get("constraint") == selected_constraint]
        exercise = random.choice(filtered) if filtered else random.choice(constraints)

    constraint_type = exercise.get("constraint", "")

    # Show constraint guide if available
    guide = constraint_guides.get(constraint_type, {})
    if guide:
        with st.expander(f"Guide: {guide.get('name', constraint_type.title())}", expanded=False):
            st.markdown(f"**What it is:** {guide.get('explanation', '')}")
            st.markdown(f"**Pattern:** {guide.get('pattern', '')}")
            st.markdown("**Key markers:**")
            markers_html = ", ".join([f"`{m}`" for m in guide.get("markers", [])])
            st.markdown(markers_html)

    # Exercise display
    st.markdown(
        f"<div style='background-color: #e7f3ff; padding: 15px; border-radius: 8px; margin: 15px 0;'>"
        f"<strong>Constraint:</strong> {exercise.get('instruction', '')}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("**Original Sentence:**")
    st.markdown(
        f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; "
        f"border: 2px solid #dee2e6; font-size: 1.1em;'>{exercise.get('original', '')}</div>",
        unsafe_allow_html=True
    )

    # Hint system
    if st.checkbox("Show hint", key="constraint_hint"):
        hint = _generate_constraint_hint(constraint_type, exercise.get("original", ""))
        st.markdown(
            f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 6px; font-style: italic;'>"
            f"Hint: {hint}</div>",
            unsafe_allow_html=True
        )

    user_attempt = st.text_area(
        "Your rewrite:",
        height=120,
        placeholder="Reescribe la oración aplicando la restricción...",
        key="constraint_rewrite_input"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Check My Answer", type="primary", use_container_width=True):
            if user_attempt.strip():
                lang_info = detect_language(user_attempt)
                if lang_info["language"] == "english":
                    st.warning("Please write in Spanish.")
                else:
                    st.markdown("---")
                    st.markdown("**Model Answer:**")
                    st.markdown(
                        f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; "
                        f"border: 2px solid #28a745; font-size: 1.1em;'>{exercise.get('example', '')}</div>",
                        unsafe_allow_html=True
                    )

                    # Analyze the user's attempt
                    st.markdown("---")
                    st.markdown("**Analysis:**")
                    _analyze_constraint_attempt(constraint_type, user_attempt, exercise.get("example", ""))

                    record_progress({"writing_words": len(user_attempt.split())})
                    log_activity("writing_coach", "constraint_rewrite", constraint_type)
            else:
                st.warning("Please write your rewrite first.")

    with col2:
        if st.button("Show Model Answer", use_container_width=True):
            st.markdown(
                f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; "
                f"font-size: 1.1em;'>{exercise.get('example', '')}</div>",
                unsafe_allow_html=True
            )

    # Additional practice section
    st.markdown("---")
    with st.expander("Try Another Variation", expanded=False):
        st.markdown("**Create your own sentence using this constraint:**")
        custom_attempt = st.text_area(
            "Write an original sentence:",
            height=80,
            placeholder="Escribe tu propia oración original aplicando esta restricción...",
            key="custom_constraint_input"
        )
        if custom_attempt:
            st.markdown("Good practice! Compare your sentence structure with the model above.")


def _generate_constraint_hint(constraint_type: str, original: str) -> str:
    """Generate a helpful hint for the constraint exercise."""
    hints = {
        "imperfecto": "Think about what was happening regularly or was in progress. Change action verbs to their imperfect forms (-aba, -ía).",
        "conditional": "Make it hypothetical or more polite. Conditional endings: -ría, -rías, -ría, -ríamos, -rían.",
        "passive": "Focus on WHAT happened rather than WHO did it. Use 'fue/fueron + participle' or 'se + verb'.",
        "subjunctive": "Express this as a wish, doubt, or emotional reaction. The subjunctive often follows 'que'.",
    }
    return hints.get(constraint_type, "Apply the grammatical transformation while keeping the same meaning.")


def _analyze_constraint_attempt(constraint_type: str, user_text: str, model_text: str):
    """Analyze the user's constraint rewrite attempt."""
    user_lower = user_text.lower()
    model_lower = model_text.lower()

    feedback_items = []

    if constraint_type == "imperfecto":
        has_imperfect = any(ending in user_lower for ending in ["aba", "ía", "íamos", "aban", "ían"])
        feedback_items.append(("Uses imperfect tense markers", has_imperfect))
        has_preterite = any(ending in user_lower for ending in ["ó ", "é ", "ieron", "aron"])
        if has_preterite:
            feedback_items.append(("Avoid preterite (should be imperfect)", False))

    elif constraint_type == "conditional":
        has_conditional = any(ending in user_lower for ending in ["ría", "rías", "ríamos", "rían"])
        feedback_items.append(("Uses conditional mood", has_conditional))

    elif constraint_type == "passive":
        has_passive_ser = any(phrase in user_lower for phrase in ["fue ", "fueron ", "es ", "son ", "era ", "eran "])
        has_passive_se = " se " in user_lower or user_lower.startswith("se ")
        feedback_items.append(("Uses passive construction", has_passive_ser or has_passive_se))

    elif constraint_type == "subjunctive":
        subjunctive_markers = ["que ", "ojalá", "espero", "dudo", "quiero que"]
        has_trigger = any(m in user_lower for m in subjunctive_markers)
        feedback_items.append(("Includes subjunctive trigger", has_trigger))

    # Length comparison
    length_similar = 0.5 <= len(user_text) / max(len(model_text), 1) <= 1.5
    feedback_items.append(("Appropriate length", length_similar))

    # Meaning preservation (basic check)
    original_words = set(model_lower.split())
    user_words = set(user_lower.split())
    overlap = len(original_words & user_words) / max(len(original_words), 1)
    feedback_items.append(("Preserves core meaning", overlap > 0.3))

    for label, passed in feedback_items:
        icon = "[OK]" if passed else "[--]"
        color = "#28a745" if passed else "#dc3545"
        st.markdown(
            f"<span style='color: {color}; font-family: monospace;'>{icon}</span> {label}",
            unsafe_allow_html=True
        )


def render_error_pattern_drills():
    """Render drills focused on specific error patterns."""
    render_section_header("Error Pattern Drills")

    st.markdown("""
    Practice the grammar patterns that cause the most confusion for Spanish learners.
    Each drill focuses on a specific error type with rule explanations and examples.
    """)

    # Select error category
    error_templates = WRITING_COACH_TEMPLATES.get("error_feedback", {})
    categories = list(error_templates.keys())

    if not categories:
        st.warning("No error pattern drills available.")
        return

    selected = st.selectbox(
        "Focus on:",
        categories,
        format_func=lambda x: x.replace("_", " ").title()
    )

    template = error_templates.get(selected, {})

    if template:
        # Rule display
        st.markdown("### Rule")
        st.info(template.get("rule", ""))

        # Examples
        st.markdown("### Examples")
        for example in template.get("examples", []):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Incorrect:** ~~{example.get('wrong', '')}~~")
            with col2:
                st.markdown(f"**Correct:** {example.get('correct', '')}")

        # Practice prompts
        st.markdown("### Practice")
        prompts = template.get("practice_prompts", [])

        for i, prompt in enumerate(prompts):
            st.markdown(f"**{i+1}.** {prompt}")

            user_response = st.text_input(
                f"Your answer for prompt {i+1}:",
                key=f"drill_{selected}_{i}",
                placeholder="Escriba su respuesta..."
            )

            if user_response:
                # Validate Spanish
                lang_info = detect_language(user_response)
                if lang_info["language"] == "english":
                    st.caption("Please write in Spanish.")
                else:
                    st.caption("Submitted. Check that your answer follows the rule above.")

        # Track drill completion state
        drill_submitted_key = f"drill_submitted_{selected}"
        if drill_submitted_key not in st.session_state:
            st.session_state[drill_submitted_key] = False

        if not st.session_state[drill_submitted_key]:
            if st.button("Submit All", type="primary"):
                record_progress({"grammar_reviewed": 1})
                log_activity("writing_coach", "error_drill", selected)
                st.session_state[drill_submitted_key] = True
                st.rerun()
        else:
            st.markdown("""
            <div class="feedback-box feedback-success">
                ✅ <strong>Great practice!</strong> Keep working on this pattern.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Try Another Drill →", type="primary"):
                    st.session_state[drill_submitted_key] = False
                    st.rerun()
            with col2:
                if st.button("Back to Writing Coach"):
                    st.session_state[drill_submitted_key] = False
                    st.session_state.writing_mode = None
                    st.rerun()
