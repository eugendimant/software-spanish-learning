# VivaLingo (Spanish Learning)

A Duolingo-inspired Spanish learning experience built with Streamlit. The app offers adaptive lessons, multiple exercise modes, and a visually engaging interface.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Features

- Guided lesson paths across CEFR levels.
- Adaptive practice modes with variety settings.
- Progress dashboard, mastery tracking, and streaks.
- Custom practice library.
- Insights, goals, and downloadable progress exports (CSV/JSON).
- Profile login with secure, hashed passwords stored locally in SQLite.
- Animated, friendly UI built with Streamlit + CSS.
- Sentence-level practice (translation + fill-in) for richer fluency.
- Pronunciation Lab for uploading and reviewing audio clips.

## Data storage

User profiles and progress are stored locally in `vivalingo_users.db` (SQLite) in the app directory. Use this file for backup or migration.
