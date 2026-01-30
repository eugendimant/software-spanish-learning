"""Conversation Mode with Goals page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import save_conversation, record_progress
from utils.content import CONVERSATION_SCENARIOS
from utils.helpers import analyze_constraints, check_text_for_mistakes


def render_conversation_page():
    """Render the Conversation Mode with Goals page."""
    render_hero(
        title="Conversation Mode",
        subtitle="Goal-driven roleplay: negotiate rent, handle refunds, resolve conflicts. Real fluency shows up in task-based exchanges.",
        pills=["Task-Based", "Hidden Targets", "Inline Corrections"]
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

    # Scenario selection
    if st.session_state.conv_scenario is None:
        render_scenario_selection()
    else:
        render_conversation()


def render_scenario_selection():
    """Render scenario selection interface."""
    render_section_header("Choose a Scenario")

    st.markdown("""
    <div class="card-muted">
        Select a real-world scenario to practice. Each scenario has hidden language targets
        you'll need to achieve during the conversation.
    </div>
    """, unsafe_allow_html=True)

    # Scenario cards
    cols = st.columns(2)

    for i, scenario in enumerate(CONVERSATION_SCENARIOS):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card" style="margin-bottom: 1rem;">
                <h4>{scenario['title']}</h4>
                <p style="color: var(--text-muted);">{scenario['brief']}</p>
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
                if i < len(achieved) and achieved[i]:
                    st.markdown(f"✅ ~~{target}~~")
                elif i <= st.session_state.conv_turn // 2:
                    st.markdown(f"🎯 {target}")


def process_user_message(message: str):
    """Process user's conversation message."""
    scenario = st.session_state.conv_scenario

    # Check for mistakes
    mistakes = check_text_for_mistakes(message)
    corrections = []

    for mistake in mistakes[:2]:  # Show max 2 corrections
        corrections.append(f"{mistake['original']} → {mistake['correction']}")

    # Check hidden targets
    targets = scenario.get("hidden_targets", [])
    constraint_results = analyze_constraints(message, targets)

    for i, (target, result) in enumerate(constraint_results.items()):
        if result.get("met") and len(st.session_state.conv_targets_achieved) <= i:
            st.session_state.conv_targets_achieved.append(True)

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
        <div class="metric-value" style="color: {'var(--success)' if achievement_rate >= 70 else 'var(--warning)'};">
            {achievement_rate:.0f}%
        </div>
        <div class="metric-label">Targets Achieved</div>
    </div>
    """, unsafe_allow_html=True)

    # Target breakdown
    st.markdown("### Target Analysis")

    for i, target in enumerate(targets):
        is_achieved = i < len(achieved) and achieved[i]
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

    unachieved = [t for i, t in enumerate(targets) if i >= len(achieved) or not achieved[i]]
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
