"""Topic-Diversity Vocabulary Engine page."""
import streamlit as st
import random
from datetime import date

from utils.theme import render_hero, render_section_header, render_progress_bar
from utils.database import (
    get_domain_exposure, record_domain_exposure, save_vocab_item,
    get_user_profile, record_progress
)
from utils.content import TOPIC_DIVERSITY_DOMAINS
from utils.helpers import pick_domain_pair, seed_for_day, shuffle_with_seed


def render_topic_diversity_page():
    """Render the Topic-Diversity Vocabulary Engine page."""
    render_hero(
        title="Topic-Diversity Engine",
        subtitle="Break the 'same-news-same-words' loop. Rotate through underexposed domains for true vocabulary breadth.",
        pills=["10 Domains", "70/30 Mix", "Guided Variety"]
    )

    # Get current exposure data
    exposures = get_domain_exposure()
    profile = get_user_profile()

    # Calculate familiar and stretch domains
    familiar_domain, stretch_domain = pick_domain_pair(exposures)

    # Domain selection UI
    col1, col2 = st.columns([2, 1])

    with col1:
        render_section_header("Domain Selection")

        selection_mode = st.radio(
            "Choose your learning mode:",
            ["🎲 Surprise Me (Recommended)", "🎯 Pick Domain", "⚖️ 70/30 Mix Session"],
            horizontal=True
        )

        if selection_mode == "🎲 Surprise Me (Recommended)":
            # Use daily seed for consistent "surprise" within a day
            seed = seed_for_day(date.today(), profile.get("name", "user"))
            random.seed(seed)

            # Favor stretch domains
            weights = []
            for domain in TOPIC_DIVERSITY_DOMAINS:
                exp = exposures.get(domain["domain"], {}).get("exposure_count", 0)
                # Lower exposure = higher weight
                weight = max(1, 100 - exp)
                weights.append(weight)

            selected_domain = random.choices(TOPIC_DIVERSITY_DOMAINS, weights=weights, k=1)[0]
            st.info(f"🎲 Today's surprise domain: **{selected_domain['domain']}**")

        elif selection_mode == "🎯 Pick Domain":
            domain_names = [d["domain"] for d in TOPIC_DIVERSITY_DOMAINS]
            selected_name = st.selectbox("Select a domain to explore:", domain_names)
            selected_domain = next(d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == selected_name)

        else:  # 70/30 Mix
            st.markdown(f"""
            **Your 70/30 Mix for today:**
            - 🟢 **70% Familiar:** {familiar_domain} (build confidence)
            - 🔵 **30% Stretch:** {stretch_domain} (promote growth)
            """)
            selected_domain = None  # Will show both

    with col2:
        render_section_header("Domain Coverage")

        # Progress bars for all domains
        total_exp = sum(e.get("exposure_count", 0) for e in exposures.values()) or 1

        for domain in TOPIC_DIVERSITY_DOMAINS:
            name = domain["domain"]
            exp = exposures.get(name, {}).get("exposure_count", 0)
            pct = (exp / total_exp) * 100

            color = "🟢" if exp > total_exp / len(TOPIC_DIVERSITY_DOMAINS) else "🔵"
            st.markdown(f"{color} **{name}**: {pct:.0f}%")
            st.progress(min(pct / 100, 1.0))

    st.divider()

    # Session state for tracking progress
    if "td_current_item" not in st.session_state:
        st.session_state.td_current_item = 0
    if "td_session_items" not in st.session_state:
        st.session_state.td_session_items = []
    if "td_learned" not in st.session_state:
        st.session_state.td_learned = []

    # Vocabulary Learning Interface
    render_section_header("Vocabulary Session")

    if selection_mode == "⚖️ 70/30 Mix Session":
        # 70/30 mix mode
        familiar_data = next((d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == familiar_domain), TOPIC_DIVERSITY_DOMAINS[0])
        stretch_data = next((d for d in TOPIC_DIVERSITY_DOMAINS if d["domain"] == stretch_domain), TOPIC_DIVERSITY_DOMAINS[1])

        # Combine lexicons: 70% familiar, 30% stretch
        familiar_items = familiar_data.get("lexicon", [])[:3]  # 3 items = ~70%
        stretch_items = stretch_data.get("lexicon", [])[:1]    # 1 item = ~30%

        all_items = [(item, familiar_domain) for item in familiar_items] + \
                    [(item, stretch_domain) for item in stretch_items]

        tabs = st.tabs(["🟢 Familiar Domain", "🔵 Stretch Domain"])

        with tabs[0]:
            render_domain_vocabulary(familiar_data, is_stretch=False)

        with tabs[1]:
            render_domain_vocabulary(stretch_data, is_stretch=True)

    else:
        # Single domain mode
        render_domain_vocabulary(selected_domain, is_stretch=False)


def render_domain_vocabulary(domain_data: dict, is_stretch: bool = False):
    """Render vocabulary learning for a single domain."""
    if not domain_data:
        st.warning("No domain selected.")
        return

    domain_name = domain_data["domain"]
    register_tags = domain_data.get("register", ["neutral"])
    sample = domain_data.get("sample", "")
    keywords = domain_data.get("keywords", [])
    lexicon = domain_data.get("lexicon", [])

    # Domain header
    badge = "🔵 Stretch" if is_stretch else "🟢 Familiar"
    st.markdown(f"### {badge} {domain_name}")

    # Sample sentence
    st.markdown(f"""
    <div class="card-muted">
        <strong>Sample context:</strong><br>
        <em>"{sample}"</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Register:** {', '.join(register_tags)}")
    st.markdown(f"**Keywords:** {', '.join(keywords)}")

    st.divider()

    # Vocabulary items with tabs
    if lexicon:
        for i, item in enumerate(lexicon):
            with st.expander(f"📚 {item['term']} ({item.get('pos', 'word')})", expanded=i == 0):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Meaning:** {item['meaning']}")
                    st.markdown(f"**Register:** {item.get('register', 'neutral')}")

                    # Contexts if available
                    contexts = item.get("contexts", [])
                    if contexts:
                        st.markdown("**Contexts:**")
                        for ctx in contexts:
                            st.markdown(f"- _{ctx}_")

                with col2:
                    # Learning status buttons
                    st.markdown("**Mark as:**")

                    if st.button("✅ Know it", key=f"know_{domain_name}_{i}"):
                        save_vocab_item({
                            "term": item["term"],
                            "meaning": item["meaning"],
                            "domain": domain_name,
                            "register": item.get("register"),
                            "pos": item.get("pos"),
                            "contexts": contexts,
                        })
                        record_domain_exposure(domain_name, 1)
                        record_progress({"vocab_reviewed": 1})
                        st.success(f"'{item['term']}' marked as known!")

                    if st.button("📝 Learning", key=f"learn_{domain_name}_{i}"):
                        save_vocab_item({
                            "term": item["term"],
                            "meaning": item["meaning"],
                            "domain": domain_name,
                            "register": item.get("register"),
                            "pos": item.get("pos"),
                            "contexts": contexts,
                        })
                        record_domain_exposure(domain_name, 1)
                        st.info(f"'{item['term']}' added to learning queue!")

                    if st.button("⏭️ Skip", key=f"skip_{domain_name}_{i}"):
                        st.caption("Skipped")

    else:
        st.info("No vocabulary items available for this domain yet.")

    # Practice section
    st.divider()
    st.markdown("### Quick Practice")

    if lexicon:
        practice_item = random.choice(lexicon)

        st.markdown(f"**Fill in the blank with the correct word:**")
        st.markdown(f"Context: _{practice_item.get('contexts', ['Use the word in a sentence'])[0] if practice_item.get('contexts') else 'Use this word appropriately.'}_")

        user_answer = st.text_input("Your answer:", key=f"practice_{domain_name}")

        if st.button("Check Answer", key=f"check_{domain_name}"):
            if user_answer.lower().strip() == practice_item["term"].lower():
                st.success("🎉 Correct! Great job!")
                record_progress({"vocab_reviewed": 1})
            else:
                st.error(f"Not quite. The answer was: **{practice_item['term']}**")
                st.markdown(f"**Meaning:** {practice_item['meaning']}")
