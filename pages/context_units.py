"""Context-First Vocabulary Units page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import save_vocab_item, record_progress
from utils.content import VOCAB_CONTEXT_UNITS
from utils.helpers import seed_for_day, generate_exercise_feedback, detect_language


def render_context_units_page():
    """Render the Context-First Vocabulary Units page."""
    render_hero(
        title="Context-First Vocabulary",
        subtitle="Learn phrases inside real contexts: dialogue, messages, and mini-paragraphs. Usage patterns, not dictionary entries.",
        pills=["Phrases", "Collocations", "Mini-stories", "4-Step Practice"]
    )

    # Initialize session state
    if "cu_current_unit" not in st.session_state:
        st.session_state.cu_current_unit = 0
    if "cu_step" not in st.session_state:
        st.session_state.cu_step = "context"
    if "cu_answers" not in st.session_state:
        st.session_state.cu_answers = {}

    # Unit selection
    render_section_header("Select a Vocabulary Unit")

    unit_names = [u["term"] for u in VOCAB_CONTEXT_UNITS]
    selected_unit_name = st.selectbox(
        "Choose a phrase to learn:",
        unit_names,
        index=st.session_state.cu_current_unit
    )

    unit = next((u for u in VOCAB_CONTEXT_UNITS if u["term"] == selected_unit_name), VOCAB_CONTEXT_UNITS[0])
    st.session_state.cu_current_unit = unit_names.index(unit["term"])

    st.divider()

    # Main learning card
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <div class="card-icon">📚</div>
            <h3 class="card-title">{unit['term']}</h3>
        </div>
        <p><strong>Collocations:</strong> {', '.join(unit.get('collocations', []))}</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabbed interface for the 4 steps
    tabs = st.tabs(["📖 Context", "✏️ Practice", "💬 Your Sentence", "🔄 Review"])

    # Step A: Context (Comprehension)
    with tabs[0]:
        st.markdown("### Step A: See it in Context")
        st.markdown("*Read these examples to understand how the phrase is used:*")

        for i, context in enumerate(unit.get("contexts", []), 1):
            context_type = "Dialogue" if i == 1 else "Message" if i == 2 else "Paragraph"
            st.markdown(f"""
            <div class="card-muted" style="margin-bottom: 0.5rem;">
                <strong>{context_type}:</strong><br>
                {context}
            </div>
            """, unsafe_allow_html=True)

        # Comprehension question
        st.markdown("---")
        st.markdown(f"**Comprehension Check:** {unit.get('question', 'What does this phrase express?')}")

        comp_answer = st.text_input("Your answer:", key="comprehension_answer")

        # Add hint button
        if st.button("💡 Hint in English", key="comp_hint"):
            st.info(f"**Hint:** The phrase '{unit['term']}' is commonly used to express: {unit.get('hint', unit.get('collocations', ['a specific concept'])[0])}")

        if st.button("Check Comprehension", key="check_comp"):
            if comp_answer.strip():
                # Validate Spanish language
                lang_info = detect_language(comp_answer)

                if lang_info["language"] == "english":
                    st.markdown("""
                    <div class="feedback-box feedback-error">
                        🌐 <strong>Please answer in Spanish!</strong> This is a Spanish learning app.
                        Use the "Hint in English" button if you need help.
                    </div>
                    """, unsafe_allow_html=True)
                elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                    st.markdown("""
                    <div class="feedback-box feedback-warning">
                        🔀 <strong>Mixed language detected.</strong> Try answering entirely in Spanish.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("Good reflection! The key is understanding how context shapes meaning.")
                    record_progress({"vocab_reviewed": 1})
            else:
                st.warning("Try to answer the question based on the contexts above.")

    # Step B: Cloze with a twist
    with tabs[1]:
        st.markdown("### Step B: Cloze Exercise")
        st.markdown("*Choose the best option to complete the sentence:*")

        cloze = unit.get("cloze", {})
        if cloze:
            st.markdown(f"""
            <div class="exercise-card">
                <div class="exercise-header">
                    <span class="exercise-type">Fill in the blank</span>
                    <span class="exercise-step">B</span>
                </div>
                <p style="font-size: 1.125rem; margin: 1rem 0;">{cloze.get('sentence', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            options = cloze.get("options", [])
            selected = st.radio(
                "Select the best option:",
                options,
                key="cloze_answer"
            )

            if st.button("Check Answer", key="check_cloze"):
                correct = cloze.get("answer", "")
                if selected == correct:
                    st.markdown("""
                    <div class="feedback-box feedback-success">
                        ✅ <strong>Correct!</strong> Great choice.
                    </div>
                    """, unsafe_allow_html=True)
                    record_progress({"vocab_reviewed": 1})
                else:
                    st.markdown(f"""
                    <div class="feedback-box feedback-error">
                        ❌ <strong>Not quite.</strong> The best answer is: <strong>{correct}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                st.info(f"**Why?** {cloze.get('explanation', '')}")

    # Step C: Forced output
    with tabs[2]:
        st.markdown("### Step C: Write Your Own Sentence")
        st.markdown("*Use the phrase in a sentence that fits this scenario:*")

        scenario = unit.get("scenario", "Write a sentence using this phrase.")
        st.markdown(f"""
        <div class="card-muted">
            <strong>Scenario:</strong> {scenario}
        </div>
        """, unsafe_allow_html=True)

        user_sentence = st.text_area(
            f"Write a sentence using '{unit['term']}':",
            height=100,
            key="user_sentence"
        )

        # Add hint button
        if st.button("💡 Hint in English", key="sentence_hint"):
            st.info(f"**Hint:** Write a sentence in Spanish that includes '{unit['term']}'. Example context: {scenario}")

        if st.button("Submit Sentence", key="submit_sentence"):
            if user_sentence.strip():
                # First check if the sentence is in Spanish
                lang_info = detect_language(user_sentence)

                if lang_info["language"] == "english":
                    st.markdown("""
                    <div class="feedback-box feedback-error">
                        🌐 <strong>Please write in Spanish!</strong> Your sentence appears to be in English.
                    </div>
                    """, unsafe_allow_html=True)
                elif lang_info["language"] == "mixed":
                    st.markdown("""
                    <div class="feedback-box feedback-warning">
                        🔀 <strong>Mixed language detected.</strong> Try to write entirely in Spanish.
                    </div>
                    """, unsafe_allow_html=True)
                # Check if the phrase is used (only if language is OK)
                elif unit["term"].lower() in user_sentence.lower():
                    st.markdown("""
                    <div class="feedback-box feedback-success">
                        ✅ <strong>Great!</strong> You've used the phrase correctly in context.
                    </div>
                    """, unsafe_allow_html=True)
                    record_progress({"writing_words": len(user_sentence.split())})

                    # Save to vocabulary
                    save_vocab_item({
                        "term": unit["term"],
                        "meaning": "Learned through context",
                        "example": user_sentence,
                        "domain": "Context Units",
                        "contexts": unit.get("contexts", []),
                        "collocations": unit.get("collocations", []),
                    })
                else:
                    st.markdown(f"""
                    <div class="feedback-box feedback-info">
                        💡 <strong>Tip:</strong> Try to include the exact phrase "<em>{unit['term']}</em>" in your sentence.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Please write a sentence to continue.")

    # Step D: Swap one word
    with tabs[3]:
        st.markdown("### Step D: Swap One Word")
        st.markdown("*Keep the grammar stable while changing the meaning:*")

        swap = unit.get("swap", {})
        if swap:
            base = swap.get("base", "")
            choices = swap.get("choices", [])

            st.markdown(f"""
            <div class="card-muted">
                <strong>Original:</strong> {base}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Rewrite the sentence by swapping one key word with one of these options:**")

            for choice in choices:
                st.markdown(f"- `{choice}`")

            rewrite = st.text_area(
                "Your rewritten sentence:",
                height=80,
                key="swap_rewrite"
            )

            # Add hint button for rewrite
            if st.button("💡 Hint in English", key="rewrite_hint"):
                st.info(f"**Hint:** Replace one word in '{base}' with one of: {', '.join(choices)}")

            if st.button("Check Rewrite", key="check_rewrite"):
                if rewrite.strip():
                    # Validate Spanish language first
                    lang_info = detect_language(rewrite)

                    if lang_info["language"] == "english":
                        st.markdown("""
                        <div class="feedback-box feedback-error">
                            🌐 <strong>Please write in Spanish!</strong> Your sentence appears to be in English.
                        </div>
                        """, unsafe_allow_html=True)
                    elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                        st.markdown("""
                        <div class="feedback-box feedback-warning">
                            🔀 <strong>Mixed language detected.</strong> Try writing entirely in Spanish.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Check if any of the choices is used
                        used_choice = any(c.lower() in rewrite.lower() for c in choices)
                        if used_choice:
                            st.markdown("""
                            <div class="feedback-box feedback-success">
                                ✅ <strong>Excellent!</strong> You've successfully modified the sentence while maintaining the structure.
                            </div>
                            """, unsafe_allow_html=True)
                            record_progress({"vocab_reviewed": 1})
                        else:
                            st.markdown(f"""
                            <div class="feedback-box feedback-info">
                                💡 Try using one of the suggested words: {', '.join(choices)}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("Please write your rewritten sentence.")

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.cu_current_unit > 0:
            if st.button("← Previous Unit", key="key_previous_unit"):
                st.session_state.cu_current_unit -= 1
                st.rerun()

    with col2:
        st.markdown(f"**Unit {st.session_state.cu_current_unit + 1} of {len(VOCAB_CONTEXT_UNITS)}**",
                   unsafe_allow_html=True)

    with col3:
        if st.session_state.cu_current_unit < len(VOCAB_CONTEXT_UNITS) - 1:
            if st.button("Next Unit →", key="key_next_unit"):
                st.session_state.cu_current_unit += 1
                st.rerun()
