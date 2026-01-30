# VivaLingo Pro - Spanish Mastery Lab

A comprehensive, production-quality Spanish learning application for C1-C2 learners. Built with Streamlit, featuring adaptive learning, spaced repetition, and output-first methodology.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Features

### Core Learning Modules

#### 1. Topic-Diversity Vocabulary Engine
Breaks the "same-news-same-words" loop by rotating through 10 underexposed domains:
- Healthcare, Housing, Relationships, Travel problems
- Workplace conflict, Finance, Cooking, Emotions
- Bureaucracy, Everyday slang-light

**Key features:**
- 70/30 familiar/stretch domain mix
- Domain exposure tracking with progress visualization
- "Surprise me" mode for variety

#### 2. Context-First Vocabulary Units
Every phrase arrives with 2-4 short contexts:
- Dialogue snippets
- Text messages
- Mini-paragraphs

**4-Step Exercise Flow:**
- Step A: Comprehension check
- Step B: Cloze with options
- Step C: Forced output (write a sentence)
- Step D: "Swap one word" rewrite

#### 3. Verb Choice Studio
Dedicated mode for advanced verb precision:
- Scenario-based verb selection
- Register, intensity, and implication notes
- Minimal pair contrasts
- Reference library of all verbs

#### 4. Real-Time Mistake Catcher
Rule-based error detection for:
- Gender agreement
- Ser/Estar usage
- Preposition errors
- English calques
- False friends

Includes grammar micro-drills and common mistakes reference.

#### 5. Output-First Daily Missions
Short daily tasks forcing production:
- 60-90 second speaking prompts
- 4-6 sentence writing prompts
- Vocabulary + grammar + verb constraints
- Feedback with retry prompts

#### 6. Conversation Mode with Goals
Task-based roleplay scenarios:
- Negotiate rent, handle refunds, resolve conflicts
- Hidden language targets
- Inline corrections
- End-of-conversation feedback

#### 7. Two-Layer Spaced Repetition
Separate review streams for vocabulary and grammar:
- SM-2 algorithm implementation
- Interleaved practice mode
- Mixed, vocab-only, grammar-only, or errors-only sessions

#### 8. Error Notebook
Personal "mistake memory" system:
- Track errors by category
- Trend analysis
- Spaced review by error type
- Micro-drills from your own mistakes

#### 9. Bring Your Own Content
Import and learn from your content:
- Paste articles, transcripts, notes
- Automatic phrase extraction
- Domain detection
- Optional domain vocabulary injection

### Product Features

#### Placement Test
Adaptive calibration test covering:
- Grammar (conditional, subjunctive)
- Vocabulary precision
- Collocations
- Register appropriateness
- Pragmatic nuance

#### Progress Tracking
- Active vocabulary count
- Speaking minutes
- Error-rate trends
- Mission completion
- Domain coverage visualization

#### Data Portability
Export as JSON/CSV:
- Vocabulary
- Mistakes
- Progress history
- Portfolio
- Full backup

## Architecture

```
app-spanish-learning/
├── app.py                 # Main application entry
├── requirements.txt       # Dependencies
├── data/                  # SQLite database & portfolio
│   └── vivalingo.db
├── utils/
│   ├── __init__.py
│   ├── database.py        # Database operations & SRS
│   ├── theme.py           # UI theme & components
│   ├── helpers.py         # Utility functions
│   └── content.py         # Learning content data
└── pages/
    ├── __init__.py
    ├── topic_diversity.py # Domain rotation
    ├── context_units.py   # Phrase learning
    ├── verb_studio.py     # Verb precision
    ├── mistake_catcher.py # Error detection
    ├── daily_missions.py  # Output practice
    ├── conversation.py    # Goal-based chat
    ├── review_hub.py      # Spaced repetition
    ├── error_notebook.py  # Mistake tracking
    ├── content_ingest.py  # BYOC system
    └── settings.py        # Profile & export
```

## Design Principles

1. **Output-First**: Production before passive recognition
2. **Constraint-Based**: Specific skill requirements per task
3. **Error-Driven**: Mistakes fuel personalized review
4. **Topic Diversity**: Escape vocabulary comfort zones
5. **Nuance Focus**: Register, tone, pragmatics matter

## Technology

- **Frontend**: Streamlit with custom CSS theming
- **Database**: SQLite with proper schema design
- **SRS**: SM-2 algorithm for spaced repetition
- **State**: Session state for in-memory operations

## Requirements

- Python 3.8+
- Streamlit 1.32.0+

## License

MIT
