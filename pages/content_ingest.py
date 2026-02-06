"""Bring Your Own Content Ingest page."""
import streamlit as st
import re
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import save_vocab_item, record_domain_exposure, record_progress
from utils.content import TOPIC_DIVERSITY_DOMAINS
from utils.helpers import sentence_split, extract_candidate_phrases, detect_domain, detect_language


def render_content_ingest_page():
    """Render the Bring Your Own Content Ingest page."""
    render_hero(
        title="Content Ingest",
        subtitle="Paste articles, transcripts, or notes. Extract useful phrases, identify what's new, and build practice around your content.",
        pills=["Articles", "Podcasts", "Notes", "Targeted Extraction"]
    )

    # Initialize session state
    if "ci_text" not in st.session_state:
        st.session_state.ci_text = ""
    if "ci_extracted" not in st.session_state:
        st.session_state.ci_extracted = []
    if "ci_domains" not in st.session_state:
        st.session_state.ci_domains = []

    # Tabs
    tabs = st.tabs(["📥 Upload Content", "📋 Extracted Phrases", "🎯 Practice"])

    with tabs[0]:
        render_upload_section()

    with tabs[1]:
        render_extracted_phrases()

    with tabs[2]:
        render_practice_section()


def render_upload_section():
    """Render the content upload section."""
    render_section_header("Upload or Paste Content")

    st.markdown("""
    <div class="card-muted">
        <strong>Supported content types:</strong>
        <ul>
            <li>News articles</li>
            <li>Podcast transcripts</li>
            <li>Personal notes</li>
            <li>Book excerpts</li>
            <li>Social media posts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Input methods
    input_method = st.radio(
        "Input method:",
        ["Paste text", "Upload file"],
        horizontal=True
    )

    if input_method == "Paste text":
        text = st.text_area(
            "Paste your Spanish text here:",
            value=st.session_state.ci_text,
            height=250,
            placeholder="Pegue su texto en espanol aqui...",
            key="content_input"
        )
        st.session_state.ci_text = text

    else:
        # File size limit: 1MB
        MAX_FILE_SIZE_MB = 1
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

        uploaded_file = st.file_uploader(
            f"Upload a text file (max {MAX_FILE_SIZE_MB}MB):",
            type=["txt", "md"],
            key="file_upload"
        )

        if uploaded_file:
            # Check file size
            file_size = uploaded_file.size
            if file_size > MAX_FILE_SIZE_BYTES:
                st.error(f"File is too large ({file_size / 1024 / 1024:.2f}MB). Maximum size is {MAX_FILE_SIZE_MB}MB.")
                text = ""
            else:
                try:
                    text = uploaded_file.read().decode("utf-8")
                    # Additional content length check
                    if len(text) > 500000:  # ~500K characters max
                        st.warning("File content is very long. Only the first 500,000 characters will be processed.")
                        text = text[:500000]
                except UnicodeDecodeError:
                    st.error("File encoding error. Please upload a UTF-8 encoded text file.")
                    text = ""
            st.session_state.ci_text = text
            if text:
                st.text_area("File content:", value=text[:500] + "..." if len(text) > 500 else text, height=150, disabled=True)
        else:
            text = ""

    # Domain injection option
    st.markdown("### Domain Injection")
    st.markdown("*Optionally inject vocabulary from underexposed domains:*")

    inject_domains = st.multiselect(
        "Add vocabulary from these domains:",
        [d["domain"] for d in TOPIC_DIVERSITY_DOMAINS],
        default=[]
    )

    # Extract button
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔍 Extract Phrases", type="primary", use_container_width=True):
            if st.session_state.ci_text.strip():
                with st.spinner("Extracting phrases from your content..."):
                    extract_phrases(st.session_state.ci_text, inject_domains)
                st.success(f"Extracted {len(st.session_state.ci_extracted)} phrases!")
            else:
                st.warning("Please paste or upload some text first.")

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.ci_text = ""
            st.session_state.ci_extracted = []
            st.session_state.ci_domains = []
            st.rerun()


def extract_phrases(text: str, inject_domains: list = None):
    """Extract candidate phrases from text."""
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into sentences
    sentences = sentence_split(text)

    # Extract candidate phrases (bigrams, trigrams)
    all_phrases = []
    for sentence in sentences:
        phrases = extract_candidate_phrases(sentence, min_words=2, max_words=4)
        all_phrases.extend(phrases)

    # Remove duplicates and common words
    common_words = {"de la", "en el", "que el", "para el", "con el", "por el", "de los", "en los"}
    unique_phrases = list(set(all_phrases) - common_words)

    # Score phrases by potential usefulness
    scored_phrases = []
    for phrase in unique_phrases:
        # Higher score for longer phrases
        length_score = len(phrase.split()) * 2

        # Bonus for certain patterns
        if any(word in phrase for word in ["cion", "miento", "idad", "izar"]):
            length_score += 3

        scored_phrases.append((phrase, length_score))

    # Sort by score and take top 20
    scored_phrases.sort(key=lambda x: x[1], reverse=True)
    top_phrases = [p[0] for p in scored_phrases[:20]]

    # Detect domains in the text
    domain_keywords = {d["domain"]: d["keywords"] for d in TOPIC_DIVERSITY_DOMAINS}
    detected_domains = detect_domain(text, domain_keywords)
    st.session_state.ci_domains = detected_domains[:3]

    # Add domain vocabulary if injection requested
    injected_items = []
    if inject_domains:
        for domain_name in inject_domains:
            domain = next((d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == domain_name), None)
            if domain:
                for item in domain.get("lexicon", [])[:2]:
                    injected_items.append({
                        "phrase": item["term"],
                        "meaning": item["meaning"],
                        "domain": domain_name,
                        "register": item.get("register", "neutral"),
                        "injected": True
                    })

    # Build extracted list
    extracted = []
    for phrase in top_phrases:
        extracted.append({
            "phrase": phrase,
            "meaning": "",  # To be filled by user
            "domain": detected_domains[0] if detected_domains else "General",
            "register": "neutral",
            "injected": False
        })

    # Add injected items
    extracted.extend(injected_items)

    st.session_state.ci_extracted = extracted


def render_extracted_phrases():
    """Render the extracted phrases review."""
    render_section_header("Review Extracted Phrases")

    extracted = st.session_state.ci_extracted
    detected_domains = st.session_state.ci_domains

    if not extracted:
        st.info("No phrases extracted yet. Go to 'Upload Content' to start.")
        return

    # Domain detection display
    if detected_domains:
        st.markdown(f"**Detected domains:** {', '.join(detected_domains)}")

    st.markdown(f"**Total phrases:** {len(extracted)}")

    st.divider()

    # Initialize selection state
    if "ci_selected" not in st.session_state:
        st.session_state.ci_selected = {i: True for i in range(len(extracted))}

    # Phrase review list
    for i, item in enumerate(extracted):
        col1, col2, col3 = st.columns([0.5, 3, 1])

        with col1:
            selected = st.checkbox(
                "",
                value=st.session_state.ci_selected.get(i, True),
                key=f"select_{i}"
            )
            st.session_state.ci_selected[i] = selected

        with col2:
            # Phrase display
            badge = "🔵 Injected" if item.get("injected") else ""
            st.markdown(f"**{item['phrase']}** {badge}")

            if item.get("meaning"):
                st.caption(f"Meaning: {item['meaning']}")
            elif item.get("injected"):
                st.caption(f"Meaning: {item.get('meaning', 'See lexicon')}")

        with col3:
            status = st.selectbox(
                "",
                ["Learn", "Skip", "Know"],
                key=f"status_{i}",
                label_visibility="collapsed"
            )

    st.divider()

    # Bulk actions
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state.ci_selected = {i: True for i in range(len(extracted))}
            st.rerun()

    with col2:
        if st.button("❌ Deselect All", use_container_width=True):
            st.session_state.ci_selected = {i: False for i in range(len(extracted))}
            st.rerun()

    with col3:
        if st.button("💾 Save Selected", type="primary", use_container_width=True):
            with st.spinner("Saving selected phrases..."):
                save_selected_phrases()


def save_selected_phrases():
    """Save selected phrases to vocabulary."""
    extracted = st.session_state.ci_extracted
    selected = st.session_state.ci_selected

    saved_count = 0
    for i, item in enumerate(extracted):
        if selected.get(i, False):
            save_vocab_item({
                "term": item["phrase"],
                "meaning": item.get("meaning", "From content ingest"),
                "domain": item.get("domain", "Imported"),
                "register": item.get("register", "neutral"),
                "pos": "phrase",
            })

            # Record domain exposure
            if item.get("domain"):
                record_domain_exposure(item["domain"], 1)

            saved_count += 1

    record_progress({"vocab_reviewed": saved_count})
    st.success(f"Saved {saved_count} phrases to your vocabulary!")


def render_practice_section():
    """Render practice exercises from extracted content."""
    render_section_header("Practice with Your Content")

    extracted = st.session_state.ci_extracted

    if not extracted:
        st.info("Extract some phrases first to practice with them.")
        return

    # Filter to selected phrases
    selected = st.session_state.get("ci_selected", {})
    practice_items = [item for i, item in enumerate(extracted) if selected.get(i, True)]

    if not practice_items:
        st.info("Select some phrases to practice.")
        return

    # Practice mode selection
    practice_mode = st.radio(
        "Practice mode:",
        ["Flashcards", "Fill in the blank", "Write a sentence"],
        horizontal=True
    )

    st.divider()

    # Initialize practice state
    if "ci_practice_index" not in st.session_state:
        st.session_state.ci_practice_index = 0

    index = st.session_state.ci_practice_index % len(practice_items)
    current = practice_items[index]

    # Progress
    st.progress((index + 1) / len(practice_items))
    st.caption(f"Item {index + 1} of {len(practice_items)}")

    if practice_mode == "Flashcards":
        render_flashcard_practice(current, index)
    elif practice_mode == "Fill in the blank":
        render_cloze_practice(current, index)
    else:
        render_sentence_practice(current, index)


def render_flashcard_practice(item: dict, index: int):
    """Render flashcard practice."""
    if "ci_revealed" not in st.session_state:
        st.session_state.ci_revealed = False

    st.markdown(f"""
    <div class="card" style="text-align: center; padding: 2rem;">
        <h2 style="font-size: 1.75rem;">{item['phrase']}</h2>
        <span class="pill pill-muted">{item.get('domain', 'General')}</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.ci_revealed:
        if st.button("Show Meaning", type="primary", use_container_width=True):
            st.session_state.ci_revealed = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="card-muted" style="text-align: center; margin-top: 1rem;">
            <h3>{item.get('meaning', 'Practice using this phrase in context')}</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Previous"):
                st.session_state.ci_practice_index = max(0, index - 1)
                st.session_state.ci_revealed = False
                st.rerun()

        with col2:
            if st.button("Next →"):
                st.session_state.ci_practice_index = index + 1
                st.session_state.ci_revealed = False
                st.rerun()


def render_cloze_practice(item: dict, index: int):
    """Render cloze/fill-in-the-blank practice."""
    phrase = item['phrase']
    words = phrase.split()

    if len(words) > 1:
        # Hide a random word
        import random
        hidden_idx = random.randint(0, len(words) - 1)
        hidden_word = words[hidden_idx]
        display_phrase = " ".join(["___" if i == hidden_idx else w for i, w in enumerate(words)])
    else:
        display_phrase = "___"
        hidden_word = phrase

    st.markdown(f"""
    <div class="card">
        <h3>Complete the phrase:</h3>
        <p style="font-size: 1.5rem; margin: 1rem 0;">{display_phrase}</p>
    </div>
    """, unsafe_allow_html=True)

    user_answer = st.text_input("Fill in the blank:", key=f"cloze_{index}")

    # Add hint button
    if st.button("💡 Hint in English", key=f"cloze_hint_{index}"):
        st.info(f"**Hint:** The missing word is a Spanish word from the phrase you're learning.")

    if st.button("Check", type="primary"):
        if not user_answer.strip():
            st.warning("Please enter your answer.")
        else:
            # Validate Spanish (only for longer answers)
            if len(user_answer.split()) > 1:
                lang_info = detect_language(user_answer)
                if lang_info["language"] == "english":
                    st.markdown("""
                    <div class="feedback-box feedback-error">
                        🌐 <strong>Please answer in Spanish!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    return

            if user_answer.lower().strip() == hidden_word.lower():
                st.success("Correct!")
                record_progress({"vocab_reviewed": 1})
            else:
                st.error(f"The answer was: {hidden_word}")

    if st.button("Next →"):
        st.session_state.ci_practice_index = index + 1
        st.rerun()


def render_sentence_practice(item: dict, index: int):
    """Render write-a-sentence practice."""
    st.markdown(f"""
    <div class="card">
        <h3>Write a sentence using:</h3>
        <p style="font-size: 1.5rem; margin: 1rem 0;"><strong>{item['phrase']}</strong></p>
        <p style="color: #8E8E93;">Domain: {item.get('domain', 'General')}</p>
    </div>
    """, unsafe_allow_html=True)

    user_sentence = st.text_area("Your sentence:", height=80, key=f"sentence_{index}")

    # Add hint button
    if st.button("💡 Hint in English", key=f"sentence_hint_{index}"):
        st.info(f"**Hint:** Write a sentence in Spanish using '{item['phrase']}'. Domain: {item.get('domain', 'General')}")

    if st.button("Submit", type="primary"):
        if user_sentence.strip():
            # Validate Spanish language first
            lang_info = detect_language(user_sentence)

            if lang_info["language"] == "english":
                st.markdown("""
                <div class="feedback-box feedback-error">
                    🌐 <strong>Please write in Spanish!</strong> Your sentence appears to be in English.
                    Use the "Hint in English" button if you need help.
                </div>
                """, unsafe_allow_html=True)
            elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
                st.markdown("""
                <div class="feedback-box feedback-warning">
                    🔀 <strong>Mixed language detected.</strong> Try writing entirely in Spanish.
                </div>
                """, unsafe_allow_html=True)
            elif item['phrase'].lower() in user_sentence.lower():
                st.success("Great! You've used the phrase in context.")
                record_progress({"writing_words": len(user_sentence.split())})
            else:
                st.warning(f"Try to include '{item['phrase']}' in your sentence.")
        else:
            st.warning("Please write a sentence.")

    if st.button("Next →"):
        st.session_state.ci_practice_index = index + 1
        st.rerun()
