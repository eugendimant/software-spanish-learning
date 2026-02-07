"""Topic-Diversity Vocabulary Engine page - Enhanced version with rich learning features."""
import streamlit as st
import random
import json
from datetime import date, datetime
from typing import Optional

from utils.theme import render_hero, render_section_header, render_progress_bar
from utils.database import (
    get_domain_exposure, record_domain_exposure, save_vocab_item,
    get_user_profile, record_progress, get_vocab_items, log_activity,
    update_vocab_review
)
from utils.content import (
    TOPIC_DIVERSITY_DOMAINS, COLLOCATIONS, FALSE_FRIENDS,
    COMMON_MISTAKES, PRAGMATICS_PATTERNS
)
from utils.helpers import (
    pick_domain_pair, seed_for_day, shuffle_with_seed, detect_language,
    compare_answers, CONFUSABLE_WORDS
)


# ============================================
# ENHANCED VOCABULARY DATA
# ============================================

# Phonetic transcriptions (IPA) for common words
PHONETIC_GUIDE = {
    # Healthcare
    "diagnostico": "/djaɣˈnos.ti.ko/",
    "sintoma": "/ˈsin.to.ma/",
    "recetar": "/re.θeˈtar/",
    "consulta": "/konˈsul.ta/",
    # Housing
    "arrendamiento": "/a.ren.da.ˈmjen.to/",
    "fianza": "/ˈfjan.θa/",
    "clausula": "/ˈklau.su.la/",
    "inquilino": "/in.ki.ˈli.no/",
    # Relationships
    "aclarar": "/a.klaˈɾaɾ/",
    "apoyo": "/aˈpo.ʝo/",
    "confianza": "/kon.ˈfjan.θa/",
    "distanciarse": "/dis.tan.ˈθjaɾ.se/",
    # Travel
    "retraso": "/reˈtɾa.so/",
    "reclamar": "/re.klaˈmaɾ/",
    "conexion": "/ko.nekˈsjon/",
    "extraviar": "/eks.tɾa.ˈβjaɾ/",
    # Workplace
    "mediar": "/meˈðjaɾ/",
    "tension": "/tenˈsjon/",
    "responsabilidad": "/res.pon.sa.βi.li.ˈðað/",
    "escalar": "/es.kaˈlaɾ/",
    # Finance
    "presupuesto": "/pɾe.su.ˈpwes.to/",
    "liquidez": "/li.kiˈðeθ/",
    "facturar": "/fak.tuˈɾaɾ/",
    "rentabilidad": "/ren.ta.βi.li.ˈðað/",
    # Cooking
    "saltear": "/sal.teˈaɾ/",
    "ingrediente": "/in.ɡɾe.ˈðjen.te/",
    "sazonar": "/sa.θoˈnaɾ/",
    "reposar": "/re.poˈsaɾ/",
    # Emotions
    "alivio": "/aˈli.βjo/",
    "frustracion": "/fɾus.tɾa.ˈθjon/",
    "serenar": "/se.ɾeˈnaɾ/",
    "agobiar": "/a.ɣo.ˈβjaɾ/",
    # Bureaucracy
    "tramitar": "/tɾa.miˈtaɾ/",
    "solicitud": "/so.li.θi.ˈtuð/",
    "plazo": "/ˈpla.θo/",
    "subsanar": "/suβ.saˈnaɾ/",
    # Slang
    "bajon": "/baˈxon/",
    "rollo": "/ˈro.ʝo/",
    "guay": "/ɡwaj/",
    "molar": "/moˈlaɾ/",
}

# Word families and derivations
WORD_FAMILIES = {
    "diagnostico": {
        "root": "diagnos-",
        "family": ["diagnosticar (v)", "diagnostico (n)", "diagnosticado (adj)"],
        "related": ["prognosis", "analisis", "evaluacion"]
    },
    "sintoma": {
        "root": "sintom-",
        "family": ["sintomatico (adj)", "asintomatico (adj)", "sintomatologia (n)"],
        "related": ["senal", "indicio", "manifestacion"]
    },
    "recetar": {
        "root": "recet-",
        "family": ["receta (n)", "recetario (n)", "recetado (adj)"],
        "related": ["prescribir", "medicar", "tratar"]
    },
    "arrendamiento": {
        "root": "arrend-",
        "family": ["arrendar (v)", "arrendatario (n)", "arrendador (n)"],
        "related": ["alquiler", "renta", "contrato"]
    },
    "fianza": {
        "root": "fi-",
        "family": ["fiar (v)", "fiador (n)", "afianzar (v)"],
        "related": ["deposito", "garantia", "aval"]
    },
    "aclarar": {
        "root": "clar-",
        "family": ["claro (adj)", "claridad (n)", "clarificacion (n)", "aclaracion (n)"],
        "related": ["explicar", "resolver", "esclarecer"]
    },
    "confianza": {
        "root": "confi-",
        "family": ["confiar (v)", "confiado (adj)", "desconfianza (n)", "desconfiar (v)"],
        "related": ["fe", "seguridad", "credibilidad"]
    },
    "retraso": {
        "root": "retras-",
        "family": ["retrasar (v)", "retrasado (adj)", "atraso (n)"],
        "related": ["demora", "tardanza", "dilacion"]
    },
    "presupuesto": {
        "root": "presupuest-",
        "family": ["presupuestar (v)", "presupuestario (adj)"],
        "related": ["cotizacion", "estimacion", "calculo"]
    },
    "tension": {
        "root": "tens-",
        "family": ["tenso (adj)", "tensar (v)", "distension (n)"],
        "related": ["estres", "presion", "ansiedad"]
    },
    "alivio": {
        "root": "alivi-",
        "family": ["aliviar (v)", "aliviado (adj)"],
        "related": ["descanso", "consuelo", "respiro"]
    },
    "tramitar": {
        "root": "tramit-",
        "family": ["tramite (n)", "tramitacion (n)"],
        "related": ["gestionar", "procesar", "diligenciar"]
    },
}

# Enhanced collocations by term
TERM_COLLOCATIONS = {
    "diagnostico": ["confirmar el diagnostico", "realizar un diagnostico", "diagnostico precoz", "diagnostico diferencial"],
    "sintoma": ["presentar sintomas", "sintomas leves/graves", "aliviar los sintomas", "sintomas clasicos"],
    "recetar": ["recetar medicamentos", "recetar reposo", "recetar tratamiento"],
    "arrendamiento": ["contrato de arrendamiento", "arrendamiento a largo plazo", "rescindir el arrendamiento"],
    "fianza": ["depositar la fianza", "devolver la fianza", "perder la fianza", "fianza de dos meses"],
    "aclarar": ["aclarar un malentendido", "aclarar dudas", "aclarar la situacion"],
    "confianza": ["ganarse la confianza", "depositar confianza", "traicionar la confianza", "confianza ciega"],
    "retraso": ["sufrir un retraso", "retraso considerable", "sin retraso", "con retraso"],
    "presupuesto": ["aprobar el presupuesto", "ajustar el presupuesto", "exceder el presupuesto", "presupuesto ajustado"],
    "tension": ["aliviar la tension", "crear tension", "tension acumulada", "subir la tension"],
    "alivio": ["sentir alivio", "suspiro de alivio", "alivio inmediato", "gran alivio"],
    "tramitar": ["tramitar un documento", "tramitar la solicitud", "tramitar el visado"],
}

# Memory tips and mnemonics
MNEMONICS = {
    "diagnostico": "Think 'dia' (through) + 'gnosis' (knowledge) - knowledge through examination",
    "sintoma": "Sounds like 'symptom' - a sign that something is wrong",
    "recetar": "Recipe for health - the doctor gives you a 'receta'",
    "arrendamiento": "Rent-amiento - renting arrangement",
    "fianza": "Fi-anza sounds like 'finance' - money you pay upfront",
    "aclarar": "A-CLAR-ar - to make CLEAR",
    "confianza": "Con-FIAR - to trust WITH someone",
    "retraso": "Re-TRAS-o - going back (tras) in time, delay",
    "presupuesto": "Pre-SUPUESTO - what you SUPPOSE you'll spend beforehand",
    "tension": "Same as English 'tension' - stress between parties",
    "alivio": "A-LIV-io - feels LIGHT (liviano) when relieved",
    "tramitar": "TRAMIT-ar - handling TRAMITes (paperwork procedures)",
    "bajon": "BAJ-on - a big DOWN (bajo) feeling",
    "guay": "GUAY sounds like 'wow' - something cool!",
}

# Register level descriptions
REGISTER_DESCRIPTIONS = {
    "formal": {
        "label": "Formal",
        "color": "#007AFF",
        "icon": "suit",
        "description": "Used in professional, academic, or official contexts. Uses 'usted' form.",
        "examples": ["business meetings", "official documents", "academic writing"]
    },
    "neutral": {
        "label": "Neutral",
        "color": "#10b981",
        "icon": "balance",
        "description": "Appropriate for most everyday situations. Neither too formal nor informal.",
        "examples": ["news articles", "general conversation", "emails to acquaintances"]
    },
    "casual": {
        "label": "Casual/Informal",
        "color": "#f59e0b",
        "icon": "chat",
        "description": "Used with friends, family, or in relaxed settings. Uses 'tu' form.",
        "examples": ["texting friends", "casual conversations", "social media"]
    }
}


def render_topic_diversity_page():
    """Render the Topic-Diversity Vocabulary Engine page."""
    render_hero(
        title="Topic-Diversity Engine",
        subtitle="Build true vocabulary breadth with domain rotation, rich word knowledge, and varied practice.",
        pills=["10 Domains", "70/30 Mix", "Word Families", "Multi-Exercise"]
    )

    # Initialize session state
    _init_session_state()

    # Get current exposure data
    exposures = get_domain_exposure()
    profile = get_user_profile()

    # Calculate familiar and stretch domains
    familiar_domain, stretch_domain = pick_domain_pair(exposures)

    # Main layout with tabs
    tab_learn, tab_practice, tab_progress = st.tabs([
        "Learn Vocabulary", "Practice Exercises", "Domain Progress"
    ])

    with tab_learn:
        _render_learning_tab(exposures, profile, familiar_domain, stretch_domain)

    with tab_practice:
        _render_practice_tab(exposures, profile)

    with tab_progress:
        _render_progress_tab(exposures)


def _init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "td_current_item": 0,
        "td_session_items": [],
        "td_learned": [],
        "td_exercise_type": "recognition",
        "td_selected_domain": None,
        "td_focus_domains": [],
        "td_confused_words": {},
        "td_practice_history": [],
        "td_current_word": None,
        "td_show_answer": False,
        "td_exercise_index": 0,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _render_learning_tab(exposures: dict, profile: dict, familiar_domain: str, stretch_domain: str):
    """Render the vocabulary learning tab."""

    # Domain selection section
    col1, col2 = st.columns([2, 1])

    with col1:
        render_section_header("Select Your Learning Focus")

        selection_mode = st.radio(
            "Choose how to explore vocabulary:",
            [
                "Surprise Me (Weighted Random)",
                "Pick a Domain",
                "70/30 Familiar/Stretch Mix",
                "Focus on Weak Domains"
            ],
            horizontal=False,
            key="td_selection_mode"
        )

        if selection_mode == "Surprise Me (Weighted Random)":
            seed = seed_for_day(date.today(), profile.get("name", "user"))
            random.seed(seed)

            weights = []
            for domain in TOPIC_DIVERSITY_DOMAINS:
                exp = exposures.get(domain["domain"], {}).get("exposure_count", 0)
                weight = max(1, 100 - exp)
                weights.append(weight)

            selected_domain = random.choices(TOPIC_DIVERSITY_DOMAINS, weights=weights, k=1)[0]
            st.info(f"Today's surprise domain: **{selected_domain['domain']}**")
            _render_domain_vocabulary_enhanced(selected_domain, exposures)

        elif selection_mode == "Pick a Domain":
            domain_names = [d["domain"] for d in TOPIC_DIVERSITY_DOMAINS]
            selected_name = st.selectbox(
                "Select a domain to explore:",
                domain_names,
                key="td_domain_select"
            )
            selected_domain = next(d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == selected_name)
            _render_domain_vocabulary_enhanced(selected_domain, exposures)

        elif selection_mode == "70/30 Familiar/Stretch Mix":
            st.markdown(f"""
            **Your personalized mix for today:**
            - **70% Familiar:** {familiar_domain} - Build confidence with known territory
            - **30% Stretch:** {stretch_domain} - Push your boundaries
            """)

            familiar_data = next((d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == familiar_domain), TOPIC_DIVERSITY_DOMAINS[0])
            stretch_data = next((d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == stretch_domain), TOPIC_DIVERSITY_DOMAINS[1])

            subtab1, subtab2 = st.tabs([f"Familiar: {familiar_domain}", f"Stretch: {stretch_domain}"])

            with subtab1:
                _render_domain_vocabulary_enhanced(familiar_data, exposures, is_stretch=False)

            with subtab2:
                _render_domain_vocabulary_enhanced(stretch_data, exposures, is_stretch=True)

        else:  # Focus on Weak Domains
            weak_domains = _get_weak_domains(exposures)
            if weak_domains:
                st.warning(f"These domains need more attention: **{', '.join(weak_domains[:3])}**")
                selected_name = st.selectbox(
                    "Focus on:",
                    weak_domains,
                    key="td_weak_domain_select"
                )
                selected_domain = next(d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == selected_name)
                _render_domain_vocabulary_enhanced(selected_domain, exposures, is_stretch=True)
            else:
                st.success("Great job! All domains are well-covered. Try 'Surprise Me' for variety!")

    with col2:
        _render_domain_sidebar(exposures)


def _get_weak_domains(exposures: dict) -> list:
    """Get domains that need more practice."""
    total_exp = sum(e.get("exposure_count", 0) for e in exposures.values()) or 1
    avg_exp = total_exp / max(len(exposures), 1)

    weak = []
    for domain_data in TOPIC_DIVERSITY_DOMAINS:
        name = domain_data["domain"]
        exp = exposures.get(name, {}).get("exposure_count", 0)
        if exp < avg_exp * 0.5:  # Less than half the average
            weak.append(name)

    return weak


def _render_domain_sidebar(exposures: dict):
    """Render the domain coverage sidebar."""
    render_section_header("Domain Coverage")

    total_exp = sum(e.get("exposure_count", 0) for e in exposures.values()) or 1
    avg_exp = total_exp / len(TOPIC_DIVERSITY_DOMAINS)

    for domain in TOPIC_DIVERSITY_DOMAINS:
        name = domain["domain"]
        exp = exposures.get(name, {}).get("exposure_count", 0)
        mastered = exposures.get(name, {}).get("mastered_items", 0)
        total_items = len(domain.get("lexicon", []))
        pct = (exp / total_exp) * 100 if total_exp > 0 else 0

        # Status indicators
        if exp > avg_exp * 1.5:
            status = "Strong"
            color = "#10b981"
        elif exp > avg_exp * 0.5:
            status = "Adequate"
            color = "#f59e0b"
        else:
            status = "Needs Work"
            color = "#ef4444"

        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500; color: #000000;">{name}</span>
                <span style="font-size: 0.75rem; color: {color};">{status}</span>
            </div>
            <div style="font-size: 0.7rem; color: #8E8E93;">
                {mastered}/{total_items} mastered | {exp} exposures
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(pct / 100, 1.0))


def _render_domain_vocabulary_enhanced(domain_data: dict, exposures: dict, is_stretch: bool = False):
    """Render enhanced vocabulary learning for a single domain."""
    if not domain_data:
        st.warning("No domain selected.")
        return

    domain_name = domain_data["domain"]
    register_tags = domain_data.get("register", ["neutral"])
    sample = domain_data.get("sample", "")
    keywords = domain_data.get("keywords", [])
    lexicon = domain_data.get("lexicon", [])

    # Domain header with badge
    badge_color = "#3b82f6" if is_stretch else "#10b981"
    badge_text = "Stretch Zone" if is_stretch else "Comfort Zone"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {badge_color}15, {badge_color}05);
                border-left: 4px solid {badge_color}; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #000000;">{domain_name}</h3>
            <span style="background: {badge_color}; color: white; padding: 4px 12px;
                         border-radius: 20px; font-size: 0.75rem;">{badge_text}</span>
        </div>
        <p style="margin: 8px 0 0 0; color: #8E8E93; font-style: italic;">"{sample}"</p>
    </div>
    """, unsafe_allow_html=True)

    # Register and keywords info
    col1, col2 = st.columns(2)
    with col1:
        register_str = ", ".join(register_tags)
        st.markdown(f"**Register:** {register_str}")
    with col2:
        st.markdown(f"**Key themes:** {', '.join(keywords[:4])}")

    st.divider()

    # Vocabulary cards with enhanced information
    if lexicon:
        for i, item in enumerate(lexicon):
            _render_vocabulary_card(item, domain_name, i, exposures)
    else:
        st.info("No vocabulary items available for this domain yet.")


def _render_vocabulary_card(item: dict, domain_name: str, index: int, exposures: dict):
    """Render an enhanced vocabulary card with all learning features."""
    term = item["term"]
    meaning = item["meaning"]
    register = item.get("register", "neutral")
    pos = item.get("pos", "word")
    contexts = item.get("contexts", [])

    # Get enhanced data
    phonetic = PHONETIC_GUIDE.get(term, "")
    word_family = WORD_FAMILIES.get(term, {})
    collocations = TERM_COLLOCATIONS.get(term, [])
    mnemonic = MNEMONICS.get(term, "")
    register_info = REGISTER_DESCRIPTIONS.get(register, REGISTER_DESCRIPTIONS["neutral"])

    with st.expander(f"{term} ({pos})", expanded=index == 0):
        # Main info row
        col1, col2 = st.columns([3, 1])

        with col1:
            # Term with phonetics
            st.markdown(f"### {term}")
            if phonetic:
                st.markdown(f"*{phonetic}*")

            # Meaning
            st.markdown(f"**Meaning:** {meaning}")

            # Register badge
            st.markdown(f"""
            <span style="background: {register_info['color']}20; color: {register_info['color']};
                         padding: 2px 10px; border-radius: 12px; font-size: 0.8rem;">
                {register_info['label']}
            </span>
            <span style="color: #8E8E93; font-size: 0.75rem; margin-left: 8px;">
                {register_info['description']}
            </span>
            """, unsafe_allow_html=True)

        with col2:
            # Action buttons
            st.markdown("**Track Progress:**")
            if st.button("I Know It", key=f"know_{domain_name}_{index}", type="primary"):
                _save_word_learned(item, domain_name, "mastered")
                st.success(f"'{term}' marked as known!")

            if st.button("Still Learning", key=f"learn_{domain_name}_{index}"):
                _save_word_learned(item, domain_name, "learning")
                st.info(f"'{term}' added to review queue!")

        st.divider()

        # Tabbed detailed information
        info_tabs = st.tabs(["Context", "Word Family", "Collocations", "Memory Tip"])

        with info_tabs[0]:
            if contexts:
                st.markdown("**Example sentences:**")
                for ctx in contexts:
                    st.markdown(f"- _{ctx}_")
            else:
                st.info("No context examples available.")

        with info_tabs[1]:
            if word_family:
                st.markdown(f"**Root:** {word_family.get('root', 'N/A')}")
                st.markdown("**Word family:**")
                for w in word_family.get("family", []):
                    st.markdown(f"- {w}")
                st.markdown("**Related words:**")
                st.markdown(", ".join(word_family.get("related", [])))
            else:
                st.info("Word family information coming soon.")

        with info_tabs[2]:
            if collocations:
                st.markdown("**Common collocations:**")
                for coll in collocations:
                    st.markdown(f"- **{coll}**")
            else:
                # Try to find in general COLLOCATIONS
                _show_general_collocations(term)

        with info_tabs[3]:
            if mnemonic:
                st.markdown(f"""
                <div style="background: #fef3c7; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <strong>Memory tip:</strong> {mnemonic}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Create your own mnemonic to remember this word!")
                user_mnemonic = st.text_input(
                    "Your memory tip:",
                    key=f"mnemonic_{domain_name}_{index}",
                    placeholder="Type a way to remember this word..."
                )


def _show_general_collocations(term: str):
    """Show collocations from the general COLLOCATIONS dictionary."""
    found = False
    for verb, chunks in COLLOCATIONS.items():
        for chunk_info in chunks:
            if term.lower() in chunk_info["chunk"].lower():
                if not found:
                    st.markdown("**Related expressions:**")
                    found = True
                st.markdown(f"- **{chunk_info['chunk']}** - {chunk_info['meaning']}")

    if not found:
        st.info("No collocations available for this term.")


def _save_word_learned(item: dict, domain_name: str, status: str):
    """Save a word as learned and update tracking."""
    save_vocab_item({
        "term": item["term"],
        "meaning": item["meaning"],
        "domain": domain_name,
        "register": item.get("register"),
        "pos": item.get("pos"),
        "contexts": item.get("contexts", []),
        "status": status,
    })
    record_domain_exposure(domain_name, 1)
    record_progress({"vocab_reviewed": 1})
    log_activity("vocab_learn", item["term"], f"Domain: {domain_name}, Status: {status}")


def _render_practice_tab(exposures: dict, profile: dict):
    """Render the practice exercises tab."""
    render_section_header("Multi-Mode Practice")

    st.markdown("""
    Practice vocabulary through different exercise types to strengthen memory from multiple angles.
    """)

    # Exercise type selection
    exercise_type = st.radio(
        "Select exercise type:",
        ["Recognition (Multiple Choice)", "Production (Fill in Blank)", "Context Match", "Word Family Quiz"],
        horizontal=True,
        key="td_exercise_type_select"
    )

    # Domain filter
    col1, col2 = st.columns([2, 1])
    with col1:
        domain_names = ["All Domains"] + [d["domain"] for d in TOPIC_DIVERSITY_DOMAINS]
        selected_domain_filter = st.selectbox(
            "Focus on domain:",
            domain_names,
            key="td_practice_domain_filter"
        )

    with col2:
        difficulty = st.select_slider(
            "Difficulty:",
            options=["Easy", "Medium", "Hard"],
            value="Medium",
            key="td_difficulty"
        )

    st.divider()

    # Get vocabulary items for practice
    if selected_domain_filter == "All Domains":
        all_items = []
        for domain in TOPIC_DIVERSITY_DOMAINS:
            for item in domain.get("lexicon", []):
                all_items.append({**item, "domain": domain["domain"]})
    else:
        domain_data = next(d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == selected_domain_filter)
        all_items = [{**item, "domain": selected_domain_filter} for item in domain_data.get("lexicon", [])]

    if not all_items:
        st.warning("No vocabulary items available for practice.")
        return

    # Initialize practice session
    practice_key = f"td_practice_item_{exercise_type}_{selected_domain_filter}"
    if practice_key not in st.session_state or st.session_state.get("td_refresh_practice", False):
        st.session_state[practice_key] = random.choice(all_items)
        st.session_state["td_practice_checked"] = False
        st.session_state["td_practice_result"] = None
        st.session_state["td_refresh_practice"] = False

    current_item = st.session_state[practice_key]

    # Render appropriate exercise type
    if exercise_type == "Recognition (Multiple Choice)":
        _render_recognition_exercise(current_item, all_items, difficulty)
    elif exercise_type == "Production (Fill in Blank)":
        _render_production_exercise(current_item, difficulty)
    elif exercise_type == "Context Match":
        _render_context_exercise(current_item, all_items, difficulty)
    else:  # Word Family Quiz
        _render_word_family_exercise(current_item, difficulty)


def _render_recognition_exercise(item: dict, all_items: list, difficulty: str):
    """Render a multiple choice recognition exercise."""
    st.markdown(f"### What does **{item['term']}** mean?")

    # Show phonetic if available
    phonetic = PHONETIC_GUIDE.get(item["term"], "")
    if phonetic:
        st.markdown(f"*Pronunciation: {phonetic}*")

    # Generate distractors based on difficulty
    num_options = {"Easy": 3, "Medium": 4, "Hard": 5}[difficulty]

    # Stabilize options across reruns using session state
    options_key = f"mcq_options_{item['term']}"
    if options_key not in st.session_state or st.session_state.get("td_refresh_practice"):
        options = _generate_mcq_options(item, all_items, num_options - 1)
        random.shuffle(options)
        st.session_state[options_key] = options
    options = st.session_state[options_key]

    # Display options
    selected = st.radio(
        "Select the correct meaning:",
        options,
        key=f"mcq_{item['term']}",
        index=None
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check Answer", type="primary", key="check_mcq"):
            if selected is None:
                st.warning("Please select an answer.")
            elif selected == item["meaning"]:
                st.session_state["td_practice_result"] = "correct"
                record_progress({"vocab_reviewed": 1})
                log_activity("vocab_practice", item["term"], "Recognition: Correct", score=5)
            else:
                st.session_state["td_practice_result"] = "incorrect"
                _track_confusion(item["term"], selected, all_items)
                log_activity("vocab_practice", item["term"], f"Recognition: Incorrect - chose '{selected}'", score=2)

    with col2:
        if st.button("Next Word", key="next_mcq"):
            st.session_state["td_refresh_practice"] = True
            st.rerun()

    # Show result and feedback
    _show_practice_feedback(item, st.session_state.get("td_practice_result"))


def _generate_mcq_options(item: dict, all_items: list, num_distractors: int) -> list:
    """Generate MCQ options including the correct answer and distractors."""
    options = [item["meaning"]]

    # Get confusable words if available
    confusables = CONFUSABLE_WORDS.get(item["term"], [])

    # Find meanings of confusable words
    for confusable in confusables:
        for other_item in all_items:
            if other_item["term"] == confusable and other_item["meaning"] not in options:
                options.append(other_item["meaning"])
                if len(options) > num_distractors:
                    break

    # Fill remaining with random distractors from same domain first
    same_domain = [i for i in all_items if i.get("domain") == item.get("domain") and i["meaning"] not in options]
    random.shuffle(same_domain)
    for other in same_domain:
        if len(options) > num_distractors:
            break
        options.append(other["meaning"])

    # Then from other domains
    other_domain = [i for i in all_items if i.get("domain") != item.get("domain") and i["meaning"] not in options]
    random.shuffle(other_domain)
    for other in other_domain:
        if len(options) > num_distractors:
            break
        options.append(other["meaning"])

    return options[:num_distractors + 1]


def _render_production_exercise(item: dict, difficulty: str):
    """Render a fill-in-the-blank production exercise."""
    contexts = item.get("contexts", [])

    if contexts:
        # Stabilize context selection across reruns
        ctx_key = f"prod_ctx_{item['term']}"
        if ctx_key not in st.session_state or st.session_state.get("td_refresh_practice"):
            st.session_state[ctx_key] = random.choice(contexts)
        context = st.session_state[ctx_key]
        blanked = context.replace(item["term"], "_____").replace(item["term"].capitalize(), "_____")
        st.markdown(f"### Fill in the blank:")
        st.markdown(f"*{blanked}*")
    else:
        st.markdown(f"### Write the Spanish word that means:")
        st.markdown(f"**{item['meaning']}**")

    # Show hint based on difficulty
    if difficulty == "Easy":
        st.info(f"Hint: The word starts with '{item['term'][0]}' and has {len(item['term'])} letters.")
    elif difficulty == "Medium":
        st.info(f"Hint: Part of speech: {item.get('pos', 'word')}")

    user_answer = st.text_input("Your answer:", key=f"prod_{item['term']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Check Answer", type="primary", key="check_prod"):
            if not user_answer.strip():
                st.warning("Please enter an answer.")
            else:
                # Use smart comparison
                is_correct, feedback_type, _ = compare_answers(
                    user_answer,
                    item["term"],
                    accent_tolerant=True,
                    grading_mode="balanced"
                )

                if is_correct:
                    st.session_state["td_practice_result"] = "correct"
                    if feedback_type == "accent_tolerance":
                        st.session_state["td_practice_feedback"] = "accent"
                    record_progress({"vocab_reviewed": 1})
                    log_activity("vocab_practice", item["term"], "Production: Correct", score=5)
                else:
                    # Check for language detection
                    lang_info = detect_language(user_answer)
                    if lang_info["language"] == "english":
                        st.session_state["td_practice_result"] = "wrong_language"
                    else:
                        st.session_state["td_practice_result"] = "incorrect"
                    log_activity("vocab_practice", item["term"], f"Production: Incorrect - wrote '{user_answer}'", score=2)

    with col2:
        if st.button("Show Hint", key="hint_prod"):
            st.info(f"**Meaning:** {item['meaning']}")
            phonetic = PHONETIC_GUIDE.get(item["term"], "")
            if phonetic:
                st.info(f"**Pronunciation:** {phonetic}")

    with col3:
        if st.button("Next Word", key="next_prod"):
            st.session_state["td_refresh_practice"] = True
            st.rerun()

    # Show result and feedback
    _show_practice_feedback(item, st.session_state.get("td_practice_result"))


def _render_context_exercise(item: dict, all_items: list, difficulty: str):
    """Render a context matching exercise."""
    contexts = item.get("contexts", [])

    if not contexts:
        st.warning("No context available for this word. Trying another exercise...")
        _render_recognition_exercise(item, all_items, difficulty)
        return

    st.markdown(f"### Which context best fits the word **{item['term']}**?")

    # Get the correct context and distractors
    correct_context = random.choice(contexts)
    distractor_contexts = []

    for other_item in all_items:
        if other_item["term"] != item["term"]:
            other_contexts = other_item.get("contexts", [])
            if other_contexts:
                distractor_contexts.append(random.choice(other_contexts))
                if len(distractor_contexts) >= 3:
                    break

    all_contexts = [correct_context] + distractor_contexts[:3]
    random.shuffle(all_contexts)

    selected = st.radio(
        "Select the correct context:",
        all_contexts,
        key=f"ctx_{item['term']}",
        index=None
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check Answer", type="primary", key="check_ctx"):
            if selected is None:
                st.warning("Please select an answer.")
            elif selected == correct_context:
                st.session_state["td_practice_result"] = "correct"
                record_progress({"vocab_reviewed": 1})
                log_activity("vocab_practice", item["term"], "Context: Correct", score=5)
            else:
                st.session_state["td_practice_result"] = "incorrect"
                log_activity("vocab_practice", item["term"], "Context: Incorrect", score=2)

    with col2:
        if st.button("Next Word", key="next_ctx"):
            st.session_state["td_refresh_practice"] = True
            st.rerun()

    _show_practice_feedback(item, st.session_state.get("td_practice_result"))


def _render_word_family_exercise(item: dict, difficulty: str):
    """Render a word family quiz."""
    term = item["term"]
    word_family = WORD_FAMILIES.get(term)

    if not word_family:
        st.info(f"Word family information not available for '{term}'. Showing general quiz...")
        st.markdown(f"### What is the root of **{term}**?")

        # Simple root guess
        possible_roots = [term[:4] + "-", term[:3] + "-", term[:5] + "-", "Unknown"]
        random.shuffle(possible_roots)

        selected = st.radio(
            "Select the likely root:",
            possible_roots,
            key=f"wf_{term}",
            index=None
        )

        if st.button("Show Answer", key="show_wf"):
            st.info(f"The word '{term}' likely derives from the root '{term[:4]}-' or similar.")

    else:
        st.markdown(f"### Word Family Quiz: **{term}**")
        st.markdown(f"Root: **{word_family['root']}**")

        # Quiz on related words
        family_words = word_family.get("family", [])
        related_words = word_family.get("related", [])

        if family_words:
            st.markdown("**Which of these belong to the same word family?**")

            # Mix correct and incorrect options
            correct_options = family_words[:2]
            incorrect_options = []
            for other_term, other_family in WORD_FAMILIES.items():
                if other_term != term:
                    incorrect_options.extend(other_family.get("family", [])[:1])
                    if len(incorrect_options) >= 2:
                        break

            all_options = correct_options + incorrect_options[:2]
            random.shuffle(all_options)

            selected = st.multiselect(
                "Select all that belong:",
                all_options,
                key=f"wf_multi_{term}"
            )

            if st.button("Check Answer", type="primary", key="check_wf"):
                correct_set = set(correct_options)
                selected_set = set(selected)

                if correct_set == selected_set:
                    st.success("Correct! You identified all the related words.")
                    record_progress({"vocab_reviewed": 1})
                elif correct_set & selected_set:
                    st.warning(f"Partially correct. The full family includes: {', '.join(correct_options)}")
                else:
                    st.error(f"Not quite. The word family includes: {', '.join(correct_options)}")

    if st.button("Next Word", key="next_wf"):
        st.session_state["td_refresh_practice"] = True
        st.rerun()


def _show_practice_feedback(item: dict, result: Optional[str]):
    """Show feedback based on practice result."""
    if result is None:
        return

    if result == "correct":
        st.markdown("""
        <div style="background: #d1fae5; padding: 16px; border-radius: 8px; border-left: 4px solid #10b981;">
            <strong style="color: #065f46;">Correct!</strong> Great job!
        </div>
        """, unsafe_allow_html=True)

        # Show additional context on success
        mnemonic = MNEMONICS.get(item["term"])
        if mnemonic:
            st.info(f"**Memory tip:** {mnemonic}")

    elif result == "incorrect":
        st.markdown(f"""
        <div style="background: #fee2e2; padding: 16px; border-radius: 8px; border-left: 4px solid #ef4444;">
            <strong style="color: #991b1b;">Not quite.</strong>
            <p style="margin: 8px 0 0 0;">The correct answer was: <strong>{item['term']}</strong></p>
            <p style="margin: 4px 0 0 0; color: #7f1d1d;">Meaning: {item['meaning']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Show helpful context
        contexts = item.get("contexts", [])
        if contexts:
            st.markdown("**Usage examples:**")
            for ctx in contexts[:2]:
                st.markdown(f"- _{ctx}_")

        # Show collocations
        collocations = TERM_COLLOCATIONS.get(item["term"], [])
        if collocations:
            st.markdown("**Common collocations:**")
            st.markdown(", ".join(collocations[:3]))

        # Suggest related vocabulary
        _suggest_related_vocabulary(item)

    elif result == "wrong_language":
        st.markdown("""
        <div style="background: #fef3c7; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
            <strong style="color: #92400e;">Please answer in Spanish!</strong>
            <p style="margin: 8px 0 0 0;">Your answer appears to be in English. Use the hint button if you need help.</p>
        </div>
        """, unsafe_allow_html=True)

    elif result == "accent":
        st.markdown("""
        <div style="background: #dbeafe; padding: 16px; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <strong style="color: #1e40af;">Almost perfect!</strong>
            <p style="margin: 8px 0 0 0;">Your answer was accepted, but pay attention to accent marks for perfect spelling.</p>
        </div>
        """, unsafe_allow_html=True)


def _suggest_related_vocabulary(item: dict):
    """Suggest related vocabulary based on the current item."""
    term = item["term"]

    # Check word families
    word_family = WORD_FAMILIES.get(term, {})
    related = word_family.get("related", [])

    if related:
        st.markdown("**You might also want to learn:**")
        for rel in related[:3]:
            st.markdown(f"- {rel}")


def _track_confusion(term: str, confused_with: str, all_items: list):
    """Track word confusion patterns."""
    if "td_confused_words" not in st.session_state:
        st.session_state["td_confused_words"] = {}

    if term not in st.session_state["td_confused_words"]:
        st.session_state["td_confused_words"][term] = {}

    confusions = st.session_state["td_confused_words"][term]
    confusions[confused_with] = confusions.get(confused_with, 0) + 1


def _render_progress_tab(exposures: dict):
    """Render the domain progress and analytics tab."""
    render_section_header("Domain Mastery Overview")

    # Summary metrics
    total_domains = len(TOPIC_DIVERSITY_DOMAINS)
    total_vocab = sum(len(d.get("lexicon", [])) for d in TOPIC_DIVERSITY_DOMAINS)
    total_exposures = sum(e.get("exposure_count", 0) for e in exposures.values())

    # Get saved vocab items
    saved_items = get_vocab_items()
    mastered_count = len([i for i in saved_items if i.get("status") == "mastered"])
    learning_count = len([i for i in saved_items if i.get("status") == "learning"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Domains", total_domains)
    with col2:
        st.metric("Total Vocabulary", total_vocab)
    with col3:
        st.metric("Words Mastered", mastered_count)
    with col4:
        st.metric("Total Exposures", total_exposures)

    st.divider()

    # Domain breakdown
    render_section_header("Domain-by-Domain Progress")

    for domain_data in TOPIC_DIVERSITY_DOMAINS:
        name = domain_data["domain"]
        lexicon = domain_data.get("lexicon", [])
        exp_data = exposures.get(name, {})

        exp_count = exp_data.get("exposure_count", 0)
        mastered = exp_data.get("mastered_items", 0)
        total_items = len(lexicon)

        # Calculate health score
        if total_items > 0:
            health = min(100, (exp_count / (total_items * 3)) * 100)  # 3 exposures per word = 100%
        else:
            health = 0

        # Status color
        if health >= 70:
            status_color = "#10b981"
            status_text = "Strong"
        elif health >= 40:
            status_color = "#f59e0b"
            status_text = "Developing"
        else:
            status_color = "#ef4444"
            status_text = "Needs Attention"

        with st.expander(f"{name} - {status_text}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.progress(health / 100)
                st.markdown(f"**Coverage:** {health:.0f}%")
                st.markdown(f"**Exposures:** {exp_count} | **Mastered:** {mastered}/{total_items}")

                # Show vocabulary in this domain
                st.markdown("**Vocabulary in this domain:**")
                for item in lexicon:
                    # Check if user has this word
                    user_item = next((i for i in saved_items if i.get("term") == item["term"]), None)
                    if user_item:
                        status = user_item.get("status", "new")
                        icon = "check" if status == "mastered" else "book" if status == "learning" else "circle"
                    else:
                        icon = "circle"

                    st.markdown(f"- {item['term']} ({item.get('pos', '')}) - {item['meaning']}")

            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 16px; background: {status_color}15;
                            border-radius: 8px; border: 1px solid {status_color}40;">
                    <div style="font-size: 2rem; font-weight: bold; color: {status_color};">{health:.0f}%</div>
                    <div style="font-size: 0.8rem; color: #8E8E93;">Domain Health</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Practice {name}", key=f"practice_btn_{name}"):
                    st.session_state["td_practice_domain_filter"] = name
                    st.info(f"Switch to the Practice tab to focus on {name}!")

    st.divider()

    # Confusion patterns
    render_section_header("Your Confusion Patterns")

    confused_words = st.session_state.get("td_confused_words", {})
    if confused_words:
        st.markdown("Words you often confuse:")
        for term, confusions in confused_words.items():
            sorted_confusions = sorted(confusions.items(), key=lambda x: x[1], reverse=True)
            st.markdown(f"- **{term}** is often confused with: {', '.join([c[0] for c in sorted_confusions[:3]])}")
    else:
        st.info("No confusion patterns recorded yet. Keep practicing!")

    # Recommendations
    render_section_header("Recommended Next Steps")

    weak_domains = _get_weak_domains(exposures)
    if weak_domains:
        st.markdown(f"**Focus on these domains:** {', '.join(weak_domains[:3])}")

    if mastered_count < 10:
        st.markdown("**Goal:** Master 10 words to build a solid foundation.")
    elif mastered_count < 30:
        st.markdown("**Goal:** Expand to 30 mastered words for conversational fluency.")
    else:
        st.markdown("**Goal:** Excellent progress! Focus on maintaining variety across all domains.")
