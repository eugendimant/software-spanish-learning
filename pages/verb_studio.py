"""Verb Choice Studio page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header, render_html
from utils.database import record_progress, save_vocab_item
from utils.content import VERB_CHOICE_STUDIO
from utils.helpers import seed_for_day, detect_language


def render_verb_studio_page():
    """Render the Verb Choice Studio page."""
    render_hero(
        title="Verb Choice Studio",
        subtitle="Master nuance, tone, intensity, and near-synonyms. Advanced fluency is often verb precision.",
        pills=["Nuance", "Register", "Intensity", "Near-Synonyms"]
    )

    # Initialize session state
    if "vs_current_scenario" not in st.session_state:
        st.session_state.vs_current_scenario = 0
    if "vs_selected_verb" not in st.session_state:
        st.session_state.vs_selected_verb = None
    if "vs_explanation" not in st.session_state:
        st.session_state.vs_explanation = ""
    if "vs_revealed" not in st.session_state:
        st.session_state.vs_revealed = False

    # Mode selection
    render_section_header("Practice Mode")

    mode = st.radio(
        "Choose your practice mode:",
        ["📝 Guided Practice", "🎲 Random Challenge", "📚 Browse All Verbs"],
        horizontal=True
    )

    st.divider()

    # Check if there are any scenarios to practice
    if not VERB_CHOICE_STUDIO:
        st.warning("No verb scenarios available. Please check the content configuration.")
        return

    if mode == "📚 Browse All Verbs":
        render_verb_reference()
    elif mode == "🎲 Random Challenge":
        # Random scenario
        seed = seed_for_day(date.today(), str(st.session_state.get("vs_current_scenario", 0)))
        random.seed(seed)
        scenario = random.choice(VERB_CHOICE_STUDIO)
        render_verb_scenario(scenario, random_mode=True)
    else:
        # Guided practice - sequential
        scenario = VERB_CHOICE_STUDIO[st.session_state.vs_current_scenario % len(VERB_CHOICE_STUDIO)]
        render_verb_scenario(scenario, random_mode=False)


def render_verb_scenario(scenario: dict, random_mode: bool = False):
    """Render a single verb choice scenario."""
    st.markdown("### Scenario")

    render_html(f"""
        <div class="card">
            <p style="font-size: 1.125rem; line-height: 1.6;">
                {scenario['scenario']}
            </p>
        </div>
    """)

    st.markdown("### Choose the Best Verb")

    # Display verb options as cards
    options = scenario.get("options", [])

    if not options:
        st.warning("No verb options available for this scenario.")
        return

    cols = st.columns(len(options))

    for i, (col, opt) in enumerate(zip(cols, options)):
        with col:
            is_selected = st.session_state.vs_selected_verb == opt["verb"]

            # Card styling based on selection
            border_color = "#6366f1" if is_selected else "#e2e8f0"
            bg_color = "rgba(37, 99, 235, 0.05)" if is_selected else "#f8fafc"

            render_html(f"""
                <div class="verb-option {'selected' if is_selected else ''}" style="border-color: {border_color}; background: {bg_color};">
                    <div class="verb-name">{opt['verb']}</div>
                    <div class="verb-meta">
                        <span class="pill pill-{'primary' if opt.get('register') == 'formal' else 'secondary' if opt.get('register') == 'neutral' else 'muted'}">
                            {opt.get('register', 'neutral')}
                        </span>
                        <span class="pill pill-{'warning' if opt.get('intensity') == 'alta' else 'muted'}">
                            {opt.get('intensity', 'media')} intensity
                        </span>
                    </div>
                    <div class="verb-note">
                        <strong>Implies:</strong> {opt.get('implication', '')}
                    </div>
                    <div class="verb-note" style="margin-top: 0.5rem;">
                        <strong>Typical objects:</strong> {opt.get('objects', '')}
                    </div>
                </div>
            """)

            if st.button(f"Select '{opt['verb']}'", key=f"select_{i}", use_container_width=True):
                st.session_state.vs_selected_verb = opt["verb"]
                st.session_state.vs_revealed = False
                st.rerun()

    # Explanation input
    st.markdown("### Explain Your Choice (in Spanish)")

    explanation = st.text_area(
        "¿Por qué elegiste este verbo? (Una línea es suficiente)",
        value=st.session_state.vs_explanation,
        height=80,
        key="verb_explanation",
        placeholder="Escriba su explicación en español..."
    )
    st.session_state.vs_explanation = explanation

    # Add hint button
    if st.button("💡 Hint in English", key="verb_hint"):
        st.info("**Hint:** Explain in Spanish why you think this verb is the best choice. Consider register (formal/informal), intensity, and context.")

    # Check answer button
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Check Answer", type="primary", use_container_width=True):
            # Validate Spanish if explanation provided
            if explanation.strip():
                lang_info = detect_language(explanation)
                if lang_info["language"] == "english":
                    render_html("""
                        <div class="feedback-box feedback-warning">
                            🌐 <strong>Try explaining in Spanish!</strong> It's great practice.
                            Use the "Hint in English" button if you need help.
                        </div>
                    """)
            st.session_state.vs_revealed = True

    with col2:
        # Always show Next button - works for both modes
        next_label = "Next Scenario →" if not random_mode else "New Scenario →"
        if st.button(next_label, use_container_width=True):
            if random_mode:
                # Get a new random scenario
                import random
                st.session_state.vs_current_scenario = random.randint(0, 100)  # Random seed
            else:
                st.session_state.vs_current_scenario += 1
            st.session_state.vs_selected_verb = None
            st.session_state.vs_explanation = ""
            st.session_state.vs_revealed = False
            st.rerun()

    # Reveal answer and feedback
    if st.session_state.vs_revealed:
        st.divider()

        best = scenario.get("best", "")
        also = scenario.get("also", [])
        contrasts = scenario.get("contrast", [])

        is_correct = st.session_state.vs_selected_verb == best
        is_acceptable = st.session_state.vs_selected_verb in also

        if is_correct:
            render_html("""
                <div class="feedback-box feedback-success">
                    ✅ <strong>Perfect!</strong> You chose the best option for this context.
                </div>
            """)
            record_progress({"vocab_reviewed": 1})
        elif is_acceptable:
            render_html(f"""
                <div class="feedback-box feedback-info">
                    👍 <strong>Also acceptable!</strong> '{st.session_state.vs_selected_verb}' works here, but '{best}' is the best fit.
                </div>
            """)
            record_progress({"vocab_reviewed": 1})
        else:
            render_html(f"""
                <div class="feedback-box feedback-error">
                    ❌ <strong>Not quite.</strong> The best choice is '{best}'.
                </div>
            """)

        # Show contrasts
        st.markdown("### Why?")

        st.markdown(f"**Best fit:** `{best}`")
        if also:
            st.markdown(f"**Also possible:** {', '.join([f'`{a}`' for a in also])}")

        st.markdown("**Minimal pair contrasts:**")
        for contrast in contrasts:
            st.markdown(f"- {contrast}")

        # Save the verb to vocabulary if learned
        if is_correct or is_acceptable:
            best_option = next((o for o in options if o["verb"] == best), options[0])
            save_vocab_item({
                "term": best,
                "meaning": best_option.get("implication", ""),
                "domain": "Verb Studio",
                "register": best_option.get("register", "neutral"),
                "pos": "verb",
            })


def render_verb_reference():
    """Render a reference view of all verbs."""
    st.markdown("### Verb Reference Library")

    # Extract all unique verbs
    all_verbs = {}
    for scenario in VERB_CHOICE_STUDIO:
        for opt in scenario.get("options", []):
            verb = opt["verb"]
            if verb not in all_verbs:
                all_verbs[verb] = {
                    "verb": verb,
                    "register": opt.get("register", "neutral"),
                    "intensity": opt.get("intensity", "media"),
                    "implication": opt.get("implication", ""),
                    "objects": opt.get("objects", ""),
                    "scenarios": []
                }
            all_verbs[verb]["scenarios"].append(scenario["scenario"][:100] + "...")

    # Display in a sortable format
    sort_by = st.selectbox("Sort by:", ["Alphabetical", "Register", "Intensity"])

    verbs_list = list(all_verbs.values())

    if sort_by == "Alphabetical":
        verbs_list.sort(key=lambda x: x["verb"])
    elif sort_by == "Register":
        order = {"formal": 0, "neutral": 1, "casual": 2}
        verbs_list.sort(key=lambda x: order.get(x["register"], 1))
    else:  # Intensity
        order = {"alta": 0, "media": 1, "baja": 2}
        verbs_list.sort(key=lambda x: order.get(x["intensity"], 1))

    # Display verbs
    for verb_data in verbs_list:
        with st.expander(f"🔤 {verb_data['verb']} ({verb_data['register']})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Implication:** {verb_data['implication']}")
                st.markdown(f"**Typical objects:** {verb_data['objects']}")
                st.markdown("**Used in scenarios:**")
                for s in verb_data["scenarios"][:2]:
                    st.caption(f"- {s}")

            with col2:
                render_html(f"""
                    <div class="verb-meta" style="flex-direction: column; align-items: flex-start;">
                        <span class="pill pill-primary">{verb_data['register']}</span>
                        <span class="pill pill-warning" style="margin-top: 0.25rem;">{verb_data['intensity']}</span>
                    </div>
                """)

                if st.button("Practice this verb", key=f"practice_{verb_data['verb']}"):
                    # Find a scenario with this verb
                    for i, scenario in enumerate(VERB_CHOICE_STUDIO):
                        if any(o["verb"] == verb_data["verb"] for o in scenario.get("options", [])):
                            st.session_state.vs_current_scenario = i
                            st.session_state.vs_selected_verb = None
                            st.session_state.vs_revealed = False
                            st.rerun()
                            break
