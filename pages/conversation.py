"""Conversation Mode with Goals page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    save_conversation, record_progress, record_conversation_outcome,
    record_pragmatics_usage, get_conversation_outcome_stats
)
from utils.content import (
    CONVERSATION_SCENARIOS, NEGOTIATION_SCENARIOS, PRAGMATICS_PATTERNS
)
from utils.helpers import analyze_constraints, check_text_for_mistakes, detect_language


def render_conversation_page():
    """Render the Conversation Mode with Goals page."""
    render_hero(
        title="Conversation Mode",
        subtitle="Goal-driven roleplay: negotiate rent, handle refunds, resolve conflicts. Real fluency shows up in task-based exchanges.",
        pills=["Task-Based", "Hidden Targets", "Repair Skills", "Outcome Scoring"]
    )

    # Initialize session state
    if "conv_scenario" not in st.session_state:
        st.session_state.conv_scenario = None
    if "conv_messages" not in st.session_state:
        st.session_state.conv_messages = []
    if "conv_turn" not in st.session_state:
        st.session_state.conv_turn = 0
    if "conv_completed" not in st.session_state:
        st.session_state.conv_completed = False
    if "conv_targets_achieved" not in st.session_state:
        st.session_state.conv_targets_achieved = []
    if "conv_mode" not in st.session_state:
        st.session_state.conv_mode = "standard"
    if "conv_objectives_met" not in st.session_state:
        st.session_state.conv_objectives_met = []
    if "conv_pragmatics_used" not in st.session_state:
        st.session_state.conv_pragmatics_used = []

    # Mode selection tabs
    tab1, tab2, tab3 = st.tabs([
        "Standard Scenarios",
        "Advanced Negotiations",
        "Repair Skills Practice"
    ])

    with tab1:
        st.session_state.conv_mode = "standard"
        if st.session_state.conv_scenario is None or st.session_state.conv_mode != "standard":
            render_scenario_selection()
        else:
            render_conversation()

    with tab2:
        st.session_state.conv_mode = "negotiation"
        render_negotiation_mode()

    with tab3:
        st.session_state.conv_mode = "repair"
        render_repair_skills_practice()


def render_scenario_selection():
    """Render scenario selection interface."""
    render_section_header("Choose a Scenario")

    st.markdown("""
    <div class="card-muted">
        Select a real-world scenario to practice. Each scenario has hidden language targets
        you'll need to achieve during the conversation. Pay attention to the formality and
        relationship context - they affect which register to use.
    </div>
    """, unsafe_allow_html=True)

    # Scenario cards
    cols = st.columns(2)

    for i, scenario in enumerate(CONVERSATION_SCENARIOS):
        with cols[i % 2]:
            # Formality badge color
            formality = scenario.get("formality", "neutral")
            formality_color = {
                "formal": "primary",
                "neutral": "warning",
                "informal": "secondary"
            }.get(formality, "muted")

            formality_icon = {
                "formal": "👔",
                "neutral": "🤝",
                "informal": "😊"
            }.get(formality, "💬")

            relationship_label = scenario.get("relationship_label", "Unknown")

            st.markdown(f"""
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">{scenario['title']}</h4>
                    <span class="pill pill-{formality_color}">{formality_icon} {formality.title()}</span>
                </div>
                <p style="color: #64748b; margin-bottom: 0.75rem;">{scenario['brief']}</p>
                <div style="background: rgba(99, 102, 241, 0.1); padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.85rem;">
                    <strong>Speaking with:</strong> {relationship_label}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Start: {scenario['title']}", key=f"start_{i}", use_container_width=True):
                st.session_state.conv_scenario = scenario
                st.session_state.conv_messages = [
                    {"role": "system", "content": scenario.get("opening", "Buenos dias...")}
                ]
                st.session_state.conv_turn = 0
                st.session_state.conv_completed = False
                st.session_state.conv_targets_achieved = []
                st.rerun()

    # Random scenario option
    st.divider()
    if st.button("🎲 Surprise Me", use_container_width=True):
        st.session_state.conv_scenario = random.choice(CONVERSATION_SCENARIOS)
        st.session_state.conv_messages = [
            {"role": "system", "content": st.session_state.conv_scenario.get("opening", "Buenos dias...")}
        ]
        st.rerun()


def render_conversation():
    """Render the active conversation interface."""
    scenario = st.session_state.conv_scenario

    # Header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### {scenario['title']}")
        st.markdown(f"*{scenario['brief']}*")

    with col2:
        if st.button("← Change Scenario"):
            st.session_state.conv_scenario = None
            st.session_state.conv_messages = []
            st.rerun()

    # Formality context banner - always visible
    formality = scenario.get("formality", "neutral")
    relationship_label = scenario.get("relationship_label", "")
    register_tips = scenario.get("register_tips", "")

    formality_icon = {"formal": "👔", "neutral": "🤝", "informal": "😊"}.get(formality, "💬")
    formality_bg = {"formal": "rgba(99, 102, 241, 0.15)", "neutral": "rgba(251, 191, 36, 0.15)", "informal": "rgba(34, 197, 94, 0.15)"}.get(formality, "rgba(100, 116, 139, 0.15)")

    st.markdown(f"""
    <div style="background: {formality_bg}; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem;">
        <span style="font-size: 1.5rem;">{formality_icon}</span>
        <div>
            <strong>{formality.title()} Register</strong> — {relationship_label}
            <br><span style="font-size: 0.85rem; opacity: 0.8;">{register_tips}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display messages
        for msg in st.session_state.conv_messages:
            role = msg["role"]
            content = msg["content"]
            corrections = msg.get("corrections", [])

            if role == "system":
                # System/partner message
                st.markdown(f"""
                <div class="chat-message">
                    <div class="chat-avatar">🧑</div>
                    <div class="chat-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # User message
                st.markdown(f"""
                <div class="chat-message user">
                    <div class="chat-avatar">👤</div>
                    <div class="chat-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)

                # Show inline corrections if any
                if corrections:
                    for corr in corrections:
                        st.caption(f"💡 *{corr}*")

    # Check if conversation should end
    if st.session_state.conv_turn >= 5 and not st.session_state.conv_completed:
        st.session_state.conv_completed = True

    # Input or completion
    if st.session_state.conv_completed:
        render_conversation_summary()
    else:
        render_conversation_input()


def render_conversation_input():
    """Render the conversation input area."""
    scenario = st.session_state.conv_scenario

    st.markdown("### Your Response")

    # Response input
    user_input = st.text_area(
        "Type your response:",
        height=100,
        placeholder="Escriba su respuesta...",
        key=f"conv_input_{st.session_state.conv_turn}"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Send", type="primary", use_container_width=True):
            if user_input.strip():
                process_user_message(user_input)
            else:
                st.warning("Please type a response.")

    with col2:
        if st.button("End Conversation", use_container_width=True):
            st.session_state.conv_completed = True
            st.rerun()

    # Hidden targets hint (revealed progressively)
    if st.session_state.conv_turn >= 2:
        with st.expander("💡 Hint: Language Targets"):
            targets = scenario.get("hidden_targets", [])
            achieved = st.session_state.conv_targets_achieved

            for i, target in enumerate(targets):
                if target in achieved:
                    st.markdown(f"✅ ~~{target}~~")
                elif i <= st.session_state.conv_turn // 2:
                    st.markdown(f"🎯 {target}")


def process_user_message(message: str):
    """Process user's conversation message."""
    scenario = st.session_state.conv_scenario

    # Check language first
    lang_info = detect_language(message)
    language_warning = None

    if lang_info["language"] == "english":
        language_warning = "🌐 Please write in Spanish to practice your conversation skills!"
    elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
        language_warning = "🔀 Mixed language detected. Try using only Spanish for better practice."

    # Check for mistakes with error handling
    corrections = []
    try:
        mistakes = check_text_for_mistakes(message)
        for mistake in mistakes[:2]:  # Show max 2 corrections
            if mistake.get("tag") != "language":  # Skip language warnings in corrections
                corrections.append(f"{mistake['original']} → {mistake['correction']}")
    except Exception:
        mistakes = []  # Gracefully handle errors in mistake checking

    # Add language warning to corrections if present
    if language_warning:
        corrections.insert(0, language_warning)

    # Check hidden targets with error handling
    targets = scenario.get("hidden_targets", [])
    try:
        constraint_results = analyze_constraints(message, targets)

        # Track achieved targets by name (not index) to properly record which ones were met
        for target, result in constraint_results.items():
            if result.get("met") and target not in st.session_state.conv_targets_achieved:
                st.session_state.conv_targets_achieved.append(target)
    except Exception:
        constraint_results = {}  # Gracefully handle errors in constraint analysis

    # Add user message
    st.session_state.conv_messages.append({
        "role": "user",
        "content": message,
        "corrections": corrections
    })

    # Generate system response
    system_response = generate_partner_response(st.session_state.conv_turn)

    st.session_state.conv_messages.append({
        "role": "system",
        "content": system_response
    })

    st.session_state.conv_turn += 1
    record_progress({"writing_words": len(message.split())})

    st.rerun()


def generate_partner_response(turn: int) -> str:
    """Generate a simulated partner response."""
    responses = [
        "Entiendo. Dejeme pensar un momento sobre lo que me dice...",
        "Tiene razon en algunos puntos. Sin embargo, me gustaria aclarar algo...",
        "Aprecio su perspectiva. Podriamos considerar otra opcion?",
        "Bueno, eso me parece razonable. Que propone exactamente?",
        "Interesante. Necesito consultar con mi equipo antes de confirmar.",
        "Perfecto, creo que estamos llegando a un acuerdo. Algo mas?",
    ]

    return responses[min(turn, len(responses) - 1)]


def render_conversation_summary():
    """Render the conversation summary and feedback."""
    scenario = st.session_state.conv_scenario

    st.divider()
    render_section_header("Conversation Complete")

    # Calculate achievements
    targets = scenario.get("hidden_targets", [])
    achieved = st.session_state.conv_targets_achieved
    achievement_rate = len(achieved) / len(targets) * 100 if targets else 100

    # Summary card
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <h3>Mission Report: {scenario['title']}</h3>
        <div class="metric-value" style="color: {'#10b981' if achievement_rate >= 70 else '#f59e0b'};">
            {achievement_rate:.0f}%
        </div>
        <div class="metric-label">Targets Achieved</div>
    </div>
    """, unsafe_allow_html=True)

    # Target breakdown
    st.markdown("### Target Analysis")

    for target in targets:
        is_achieved = target in achieved
        icon = "✅" if is_achieved else "❌"
        st.markdown(f"{icon} {target}")

    # What you did well
    st.markdown("### What You Did Well")
    positives = []

    if achievement_rate >= 50:
        positives.append("Good use of the conversation constraints")
    if st.session_state.conv_turn >= 4:
        positives.append("Maintained engagement throughout the conversation")

    all_messages = [m["content"] for m in st.session_state.conv_messages if m["role"] == "user"]
    total_words = sum(len(m.split()) for m in all_messages)

    if total_words >= 50:
        positives.append("Good output volume - you produced substantial content")

    for pos in positives:
        st.markdown(f"- {pos}")

    if not positives:
        st.markdown("- Keep practicing! Every conversation is an opportunity to improve.")

    # One thing to repeat tomorrow
    st.markdown("### Focus for Tomorrow")

    unachieved = [t for t in targets if t not in achieved]
    if unachieved:
        st.markdown(f"🎯 **Practice this:** {unachieved[0]}")
    else:
        st.markdown("🎯 **Challenge:** Try a more difficult scenario!")

    # Save conversation
    save_conversation({
        "title": scenario["title"],
        "hidden_targets": targets,
        "messages": st.session_state.conv_messages,
        "achieved_targets": achieved,
        "completed": 1,
    })
    record_progress({"missions_completed": 1})

    # Restart options
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.conv_messages = [
                {"role": "system", "content": scenario.get("opening", "Buenos dias...")}
            ]
            st.session_state.conv_turn = 0
            st.session_state.conv_completed = False
            st.session_state.conv_targets_achieved = []
            st.rerun()

    with col2:
        if st.button("📋 New Scenario", use_container_width=True):
            st.session_state.conv_scenario = None
            st.session_state.conv_messages = []
            st.session_state.conv_turn = 0
            st.session_state.conv_completed = False
            st.session_state.conv_targets_achieved = []
            st.rerun()


def render_negotiation_mode():
    """Render advanced negotiation scenarios with outcome scoring."""
    render_section_header("Advanced Negotiations")

    st.markdown("""
    <div class="card-muted">
        Practice real-world negotiations with specific objectives. Each scenario has
        measurable outcomes and a scoring rubric based on your language use.
    </div>
    """, unsafe_allow_html=True)

    # Initialize negotiation state
    if "neg_scenario" not in st.session_state:
        st.session_state.neg_scenario = None
    if "neg_messages" not in st.session_state:
        st.session_state.neg_messages = []
    if "neg_current_step" not in st.session_state:
        st.session_state.neg_current_step = 0
    if "neg_score" not in st.session_state:
        st.session_state.neg_score = {}

    if st.session_state.neg_scenario is None:
        # Scenario selection
        for i, scenario in enumerate(NEGOTIATION_SCENARIOS):
            with st.expander(f"**{scenario['title']}**", expanded=i==0):
                st.markdown(f"*{scenario['brief']}*")

                st.markdown("**Objectives:**")
                for obj in scenario.get("objectives", []):
                    st.markdown(f"- {obj['description']}")

                st.markdown("**Scoring criteria:**")
                rubric = scenario.get("scoring_rubric", {})
                for criterion, points in rubric.items():
                    st.caption(f"- {criterion.replace('_', ' ').title()}: {points} pts")

                if st.button(f"Start: {scenario['title']}", key=f"neg_start_{i}"):
                    st.session_state.neg_scenario = scenario
                    st.session_state.neg_messages = []
                    st.session_state.neg_current_step = 0
                    st.session_state.neg_score = {k: 0 for k in rubric.keys()}

                    # Add opening from partner
                    opening_response = scenario.get("partner_responses", [{}])[0]
                    st.session_state.neg_messages.append({
                        "role": "partner",
                        "content": opening_response.get("response", "Buenos dias, en que puedo ayudarle?")
                    })
                    st.rerun()
    else:
        render_negotiation_conversation()


def render_negotiation_conversation():
    """Render active negotiation conversation."""
    scenario = st.session_state.neg_scenario

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {scenario['title']}")
    with col2:
        if st.button("Reset Negotiation"):
            st.session_state.neg_scenario = None
            st.session_state.neg_messages = []
            st.rerun()

    # Objectives sidebar
    st.markdown("**Your Objectives:**")
    objectives = scenario.get("objectives", [])
    met_objectives = st.session_state.conv_objectives_met

    for obj in objectives:
        is_met = obj["target"] in met_objectives
        icon = "✅" if is_met else "🎯"
        st.markdown(f"{icon} {obj['description']}")

    st.divider()

    # Display conversation
    for msg in st.session_state.neg_messages:
        if msg["role"] == "partner":
            st.markdown(f"""
            <div class="chat-message">
                <div class="chat-avatar">🧑</div>
                <div class="chat-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-avatar">👤</div>
                <div class="chat-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            if msg.get("pragmatics"):
                st.caption(f"Pragmatics used: {', '.join(msg['pragmatics'])}")

    # Check if negotiation complete
    if len(st.session_state.neg_messages) >= 8:
        render_negotiation_summary()
        return

    # Input
    user_input = st.text_area(
        "Your response:",
        height=100,
        placeholder="Escriba su respuesta...",
        key=f"neg_input_{len(st.session_state.neg_messages)}"
    )

    # Pragmatics helper
    with st.expander("💡 Pragmatics Helper"):
        st.markdown("**Useful phrases for this negotiation:**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Requests:**")
            for pattern in PRAGMATICS_PATTERNS.get("softeners", {}).get("requests", [])[:3]:
                st.caption(f"- {pattern['phrase']}")

        with col2:
            st.markdown("**Backchanneling:**")
            for pattern in PRAGMATICS_PATTERNS.get("backchanneling", {}).get("understanding", [])[:3]:
                st.caption(f"- {pattern['phrase']}")

    if st.button("Send", type="primary", use_container_width=True):
        if user_input.strip():
            # Analyze pragmatics used
            pragmatics_found = []
            text_lower = user_input.lower()

            # Check for softeners
            for softener in PRAGMATICS_PATTERNS.get("softeners", {}).get("hedging", []):
                if softener["phrase"].lower() in text_lower:
                    pragmatics_found.append(softener["phrase"])
                    record_pragmatics_usage("softeners", softener["phrase"], is_production=True)

            # Check for backchanneling
            for backchannel in PRAGMATICS_PATTERNS.get("backchanneling", {}).get("understanding", []):
                if backchannel["phrase"].lower() in text_lower:
                    pragmatics_found.append(backchannel["phrase"])
                    record_pragmatics_usage("backchanneling", backchannel["phrase"], is_production=True)

            # Add user message
            st.session_state.neg_messages.append({
                "role": "user",
                "content": user_input,
                "pragmatics": pragmatics_found
            })

            # Update score for used politeness
            if pragmatics_found:
                st.session_state.neg_score["used_politeness"] = min(
                    st.session_state.neg_score.get("used_politeness", 0) + 5,
                    scenario.get("scoring_rubric", {}).get("used_politeness", 20)
                )

            # Check objectives
            for obj in objectives:
                trigger = obj["target"]
                if trigger not in st.session_state.conv_objectives_met:
                    # Simple keyword matching for demo
                    if any(word in text_lower for word in trigger.split("_")):
                        st.session_state.conv_objectives_met.append(trigger)

            # Generate partner response
            step = st.session_state.neg_current_step
            responses = scenario.get("partner_responses", [])
            if step < len(responses):
                partner_msg = responses[step].get("response", "Entiendo, dejeme ver...")
            else:
                partner_msg = "Muy bien, creo que estamos llegando a un acuerdo."

            st.session_state.neg_messages.append({
                "role": "partner",
                "content": partner_msg
            })

            st.session_state.neg_current_step += 1
            record_progress({"writing_words": len(user_input.split())})
            st.rerun()


def render_negotiation_summary():
    """Render negotiation outcome summary."""
    scenario = st.session_state.neg_scenario

    st.divider()
    render_section_header("Negotiation Complete")

    # Calculate total score
    rubric = scenario.get("scoring_rubric", {})
    score = st.session_state.neg_score

    # Add points for confirmed details
    met_count = len(st.session_state.conv_objectives_met)
    score["confirmed_details"] = min(met_count * 10, rubric.get("confirmed_details", 25))

    total = sum(score.values())
    max_total = sum(rubric.values())
    percentage = (total / max_total * 100) if max_total > 0 else 0

    # Display score
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <h3>{scenario['title']}</h3>
        <div class="metric-value" style="color: {'#10b981' if percentage >= 70 else '#f59e0b'};">
            {total}/{max_total} points ({percentage:.0f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    st.markdown("### Score Breakdown")
    for criterion, max_points in rubric.items():
        earned = score.get(criterion, 0)
        st.progress(earned / max_points if max_points > 0 else 0)
        st.caption(f"{criterion.replace('_', ' ').title()}: {earned}/{max_points}")

    # Record outcomes
    for obj in scenario.get("objectives", []):
        achieved = obj["target"] in st.session_state.conv_objectives_met
        record_conversation_outcome(0, obj["type"], achieved, obj["description"])

    record_progress({"missions_completed": 1})

    if st.button("New Negotiation", use_container_width=True):
        st.session_state.neg_scenario = None
        st.session_state.neg_messages = []
        st.session_state.conv_objectives_met = []
        st.session_state.neg_score = {}
        st.rerun()


def render_repair_skills_practice():
    """Render repair skills practice mode."""
    render_section_header("Repair Skills Practice")

    st.markdown("""
    Practice essential repair skills for real conversations: asking for clarification,
    self-correction, and confirming understanding. These skills are crucial for
    maintaining fluent conversations even when you don't catch everything.
    """)

    # Get repair skills patterns
    repair_skills = PRAGMATICS_PATTERNS.get("repair_skills", {})

    # Skill categories
    skill_type = st.selectbox(
        "Choose a skill to practice:",
        list(repair_skills.keys()),
        format_func=lambda x: x.replace("_", " ").title()
    )

    patterns = repair_skills.get(skill_type, [])

    if not patterns:
        st.warning("No patterns available for this skill.")
        return

    # Display patterns
    st.markdown(f"### {skill_type.replace('_', ' ').title()} Phrases")

    for i, pattern in enumerate(patterns):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{pattern['phrase']}**")
            if pattern.get("register"):
                st.caption(f"Register: {pattern['register']}")
            if pattern.get("use"):
                st.caption(f"Use: {pattern['use']}")

        with col2:
            if st.button("Practice", key=f"practice_{skill_type}_{i}"):
                record_pragmatics_usage("repair_skills", pattern["phrase"])
                st.success("Phrase practiced!")

    # Practice scenario
    st.divider()
    st.markdown("### Practice Scenario")

    scenarios = {
        "asking_clarification": {
            "prompt": "The speaker just said something too quickly. Ask them to repeat or clarify.",
            "partner": "Entonces quedamos a las siete y media en la estacion de Atocha para coger el AVE de las ocho menos cuarto.",
        },
        "self_correction": {
            "prompt": "You just made a mistake. Correct yourself using an appropriate phrase.",
            "partner": "Ya veo, entonces el proyecto empezara la proxima semana...",
        },
        "confirming_understanding": {
            "prompt": "Confirm that you understood the key points correctly.",
            "partner": "El contrato es por seis meses, con opcion de renovacion. El sueldo base es de 2500 euros mas bonus por objetivos.",
        },
    }

    if skill_type in scenarios:
        scene = scenarios[skill_type]
        st.info(f"**Situation:** {scene['prompt']}")
        st.markdown(f"**Partner says:** \"{scene['partner']}\"")

        response = st.text_area(
            "Your response (use the appropriate phrase):",
            height=100,
            placeholder="Escriba su respuesta...",
            key=f"repair_response_{skill_type}"
        )

        # Track check state
        repair_checked_key = f"repair_checked_{skill_type}"
        repair_result_key = f"repair_result_{skill_type}"

        if repair_checked_key not in st.session_state:
            st.session_state[repair_checked_key] = False
            st.session_state[repair_result_key] = None

        if not st.session_state[repair_checked_key]:
            if st.button("Check Response", type="primary"):
                if response.strip():
                    # Check if any repair phrase was used
                    response_lower = response.lower()
                    used_pattern = None

                    for pattern in patterns:
                        phrase_start = pattern["phrase"].split("...")[0].lower().strip()
                        if phrase_start and phrase_start in response_lower:
                            used_pattern = pattern["phrase"]
                            break

                    if used_pattern:
                        st.session_state[repair_result_key] = {"success": True, "pattern": used_pattern}
                        record_pragmatics_usage("repair_skills", used_pattern, is_production=True)
                        record_progress({"speaking_minutes": 0.5})
                    else:
                        st.session_state[repair_result_key] = {"success": False}

                    st.session_state[repair_checked_key] = True
                    st.rerun()
                else:
                    st.warning("Please write a response.")
        else:
            # Show result
            result = st.session_state[repair_result_key]

            if result and result["success"]:
                st.markdown(f"""
                <div class="feedback-box feedback-success">
                    ✅ <strong>Great!</strong> You used: '{result["pattern"]}'
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="feedback-box feedback-warning">
                    ⚠️ Try incorporating one of the repair phrases from above.
                </div>
                """, unsafe_allow_html=True)

            if st.button("Try Another Scenario →", type="primary"):
                st.session_state[repair_checked_key] = False
                st.session_state[repair_result_key] = None
                st.rerun()
