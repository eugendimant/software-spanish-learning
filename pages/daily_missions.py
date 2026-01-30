"""Output-First Daily Missions page."""
import streamlit as st
import streamlit.components.v1 as components
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    save_daily_mission, get_today_mission, update_mission_response,
    record_progress, save_transcript
)
from utils.content import DAILY_MISSION_TEMPLATES
from utils.helpers import seed_for_day, analyze_constraints, check_text_for_mistakes


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

    # Check for existing mission today
    today_mission = get_today_mission()

    # Mission selection
    col1, col2 = st.columns([2, 1])

    with col1:
        render_section_header("Today's Mission")

        if today_mission and today_mission.get("completed"):
            st.success("🎉 You've completed today's mission! Come back tomorrow for a new challenge.")

            # Show completed mission
            st.markdown(f"""
            <div class="card">
                <h4>{today_mission.get('mission_type', 'Mission').title()}</h4>
                <p>{today_mission.get('prompt', '')}</p>
                <p><strong>Your score:</strong> {today_mission.get('score', 0):.0f}/100</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Practice Another Mission"):
                st.session_state.dm_mission = None
                st.session_state.dm_submitted = False
                st.session_state.dm_feedback = None

        else:
            # Generate or load mission
            if st.session_state.dm_mission is None:
                seed = seed_for_day(date.today(), "mission")
                random.seed(seed)
                st.session_state.dm_mission = random.choice(DAILY_MISSION_TEMPLATES)

            mission = st.session_state.dm_mission
            render_mission(mission)

    with col2:
        render_section_header("Mission Stats")

        # Quick stats
        st.metric("Missions Today", "1" if today_mission else "0")
        st.metric("Weekly Goal", "6")

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
    <div class="card" style="border-left: 4px solid var(--primary);">
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

    # Submit
    if st.button("Submit Speaking Mission", type="primary", use_container_width=True):
        if transcript.strip():
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

    # Submit
    if st.button("Submit Writing Mission", type="primary", use_container_width=True):
        if response.strip():
            process_mission_response(mission, response)
        else:
            st.warning("Please write your response before submitting.")


def process_mission_response(mission: dict, response: str, duration: int = 0):
    """Process and provide feedback on mission response."""
    st.session_state.dm_submitted = True

    constraints = mission.get("constraints", [])
    mission_type = mission.get("type", "writing")

    # Analyze constraints
    constraint_results = analyze_constraints(response, constraints)

    # Check for mistakes
    mistakes = check_text_for_mistakes(response)

    # Calculate score
    constraints_met = sum(1 for c in constraint_results.values() if c.get("met", False))
    constraint_score = (constraints_met / len(constraints)) * 50 if constraints else 50
    mistake_penalty = min(len(mistakes) * 10, 30)
    length_score = min(len(response.split()) / 50 * 20, 20) if mission_type == "writing" else 20

    total_score = constraint_score + length_score - mistake_penalty + 30  # Base 30
    total_score = max(0, min(100, total_score))

    # Save mission
    mission_id = save_daily_mission({
        "date": date.today().isoformat(),
        "type": mission_type,
        "prompt": mission.get("prompt", ""),
        "constraints": constraints,
        "user_response": response,
        "score": total_score,
        "completed": 1,
    })

    # Save transcript if speaking
    if mission_type == "speaking":
        save_transcript(response, duration, mission_id)
        record_progress({"speaking_minutes": duration / 60, "missions_completed": 1})
    else:
        record_progress({"writing_words": len(response.split()), "missions_completed": 1})

    # Display feedback
    st.divider()
    render_section_header("Mission Feedback")

    # Score display
    score_color = "success" if total_score >= 70 else "warning" if total_score >= 50 else "error"
    st.markdown(f"""
    <div class="card" style="text-align: center; border-top: 4px solid var(--{score_color});">
        <div class="metric-value" style="font-size: 3rem;">{total_score:.0f}</div>
        <div class="metric-label">Mission Score</div>
    </div>
    """, unsafe_allow_html=True)

    # Constraint results
    st.markdown("### Constraint Analysis")

    for constraint, result in constraint_results.items():
        icon = "✅" if result.get("met") else "❌"
        st.markdown(f"{icon} **{constraint}**")

        if not result.get("met"):
            st.caption(f"   Tip: {result}")

    # Mistakes found
    if mistakes:
        st.markdown("### Corrections Needed")
        for mistake in mistakes[:3]:
            st.markdown(f"""
            <div class="feedback-box feedback-error">
                <strong>{mistake['original']}</strong> → <strong>{mistake['correction']}</strong><br>
                <small>{mistake['explanation']}</small>
            </div>
            """, unsafe_allow_html=True)

    # Retry prompt
    st.markdown("### Retry Challenge")
    st.markdown("*Fix the issues above and write an improved version:*")

    retry = st.text_area(
        "Improved response:",
        height=100,
        key="retry_response"
    )

    if st.button("Submit Retry"):
        if retry.strip():
            retry_mistakes = check_text_for_mistakes(retry)
            if len(retry_mistakes) < len(mistakes):
                st.success("🎉 Great improvement! You fixed some errors.")
            else:
                st.info("Keep practicing! Review the corrections above.")
