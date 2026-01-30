"""Database management for VivaLingo Pro."""
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
import json

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "vivalingo.db"
PORTFOLIO_PATH = DATA_DIR / "portfolio.json"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database with all required tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        # Vocabulary items with domain tagging
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocab_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT UNIQUE NOT NULL,
                meaning TEXT,
                example TEXT,
                domain TEXT,
                register TEXT,
                part_of_speech TEXT,
                contexts TEXT,
                collocations TEXT,
                exposure_count INTEGER DEFAULT 0,
                last_reviewed TEXT,
                next_review TEXT,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Mistakes with detailed tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_text TEXT NOT NULL,
                corrected_text TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_tag TEXT,
                pattern TEXT,
                explanation TEXT,
                examples TEXT,
                confidence REAL DEFAULT 0.5,
                review_count INTEGER DEFAULT 0,
                last_reviewed TEXT,
                next_review TEXT,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Domain exposure tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domain_exposure (
                domain TEXT PRIMARY KEY,
                exposure_count INTEGER DEFAULT 0,
                last_exposure TEXT,
                total_items INTEGER DEFAULT 0,
                mastered_items INTEGER DEFAULT 0
            )
        """)

        # Grammar patterns for SRS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS grammar_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                examples TEXT,
                exposure_count INTEGER DEFAULT 0,
                last_reviewed TEXT,
                next_review TEXT,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Daily missions history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_date TEXT NOT NULL,
                mission_type TEXT NOT NULL,
                prompt TEXT,
                constraints TEXT,
                user_response TEXT,
                feedback TEXT,
                score REAL,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Transcripts for speaking practice
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcript TEXT NOT NULL,
                mission_id INTEGER,
                duration_seconds INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mission_id) REFERENCES daily_missions(id)
            )
        """)

        # Conversation sessions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_title TEXT NOT NULL,
                hidden_targets TEXT,
                messages TEXT,
                achieved_targets TEXT,
                feedback TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User progress metrics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date TEXT NOT NULL,
                speaking_minutes REAL DEFAULT 0,
                writing_words INTEGER DEFAULT 0,
                vocab_reviewed INTEGER DEFAULT 0,
                grammar_reviewed INTEGER DEFAULT 0,
                errors_fixed INTEGER DEFAULT 0,
                missions_completed INTEGER DEFAULT 0,
                active_vocab_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User profile and settings
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT DEFAULT '',
                level TEXT DEFAULT 'C1',
                weekly_goal INTEGER DEFAULT 6,
                placement_completed INTEGER DEFAULT 0,
                placement_score REAL,
                focus_areas TEXT,
                dialect_preference TEXT DEFAULT 'Spain',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Initialize default domains
        domains = [
            "Healthcare", "Housing", "Relationships", "Travel problems",
            "Workplace conflict", "Finance", "Cooking", "Emotions",
            "Bureaucracy", "Everyday slang-light"
        ]
        for domain in domains:
            conn.execute("""
                INSERT OR IGNORE INTO domain_exposure (domain, exposure_count)
                VALUES (?, 0)
            """, (domain,))

        # Initialize user profile if not exists
        conn.execute("""
            INSERT OR IGNORE INTO user_profile (id) VALUES (1)
        """)

        conn.commit()


# ============== Vocabulary Operations ==============

def save_vocab_item(item: dict) -> None:
    """Save or update a vocabulary item."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO vocab_items
            (term, meaning, example, domain, register, part_of_speech, contexts, collocations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(term) DO UPDATE SET
                meaning = excluded.meaning,
                example = excluded.example,
                domain = excluded.domain,
                register = excluded.register,
                part_of_speech = excluded.part_of_speech,
                contexts = excluded.contexts,
                collocations = excluded.collocations
        """, (
            item["term"],
            item.get("meaning"),
            item.get("example"),
            item.get("domain"),
            item.get("register"),
            item.get("pos") or item.get("part_of_speech"),
            json.dumps(item.get("contexts", [])),
            json.dumps(item.get("collocations", []))
        ))
        conn.commit()


def get_vocab_items(domain: Optional[str] = None, status: Optional[str] = None) -> list:
    """Get vocabulary items, optionally filtered."""
    with get_connection() as conn:
        query = "SELECT * FROM vocab_items WHERE 1=1"
        params = []
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_vocab_for_review() -> list:
    """Get vocabulary items due for review."""
    today = date.today().isoformat()
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT * FROM vocab_items
            WHERE next_review IS NULL OR next_review <= ?
            ORDER BY next_review ASC, ease_factor ASC
            LIMIT 20
        """, (today,)).fetchall()]


def update_vocab_review(term: str, quality: int) -> None:
    """Update vocabulary item after review using SM-2 algorithm."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM vocab_items WHERE term = ?", (term,)
        ).fetchone()
        if not row:
            return

        ease_factor = row["ease_factor"]
        interval = row["interval_days"]

        # SM-2 algorithm
        if quality >= 3:
            if interval == 1:
                interval = 6
            else:
                interval = int(interval * ease_factor)
            ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            interval = 1

        ease_factor = max(1.3, ease_factor)
        next_review = (date.today() + timedelta(days=interval)).isoformat()
        status = "learning" if quality < 4 else "mastered" if interval > 21 else "learning"

        conn.execute("""
            UPDATE vocab_items SET
                exposure_count = exposure_count + 1,
                last_reviewed = ?,
                next_review = ?,
                ease_factor = ?,
                interval_days = ?,
                status = ?
            WHERE term = ?
        """, (date.today().isoformat(), next_review, ease_factor, interval, status, term))
        conn.commit()


# ============== Mistake Operations ==============

def save_mistake(entry: dict) -> int:
    """Save a mistake entry and return its ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO mistakes
            (user_text, corrected_text, error_type, error_tag, pattern, explanation, examples, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry["user_text"],
            entry["corrected_text"],
            entry["error_type"],
            entry.get("error_tag"),
            entry.get("pattern"),
            entry.get("explanation"),
            json.dumps(entry.get("examples", [])),
            entry.get("confidence", 0.5)
        ))
        conn.commit()
        return cursor.lastrowid


def get_mistakes_for_review() -> list:
    """Get mistakes due for review."""
    today = date.today().isoformat()
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT * FROM mistakes
            WHERE next_review IS NULL OR next_review <= ?
            ORDER BY next_review ASC, ease_factor ASC
            LIMIT 15
        """, (today,)).fetchall()]


def get_mistake_stats() -> dict:
    """Get statistics about mistakes by type."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT error_type, COUNT(*) as count,
                   AVG(ease_factor) as avg_ease
            FROM mistakes
            GROUP BY error_type
            ORDER BY count DESC
        """).fetchall()
        return {row["error_type"]: {"count": row["count"], "avg_ease": row["avg_ease"]}
                for row in rows}


def update_mistake_review(mistake_id: int, quality: int) -> None:
    """Update mistake after review using SM-2 algorithm."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM mistakes WHERE id = ?", (mistake_id,)
        ).fetchone()
        if not row:
            return

        ease_factor = row["ease_factor"]
        interval = row["interval_days"]

        if quality >= 3:
            if interval == 1:
                interval = 6
            else:
                interval = int(interval * ease_factor)
            ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            interval = 1

        ease_factor = max(1.3, ease_factor)
        next_review = (date.today() + timedelta(days=interval)).isoformat()

        conn.execute("""
            UPDATE mistakes SET
                review_count = review_count + 1,
                last_reviewed = ?,
                next_review = ?,
                ease_factor = ?,
                interval_days = ?
            WHERE id = ?
        """, (date.today().isoformat(), next_review, ease_factor, interval, mistake_id))
        conn.commit()


# ============== Domain Exposure Operations ==============

def record_domain_exposure(domain: str, items_count: int = 1) -> None:
    """Record exposure to a domain."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO domain_exposure (domain, exposure_count, last_exposure, total_items)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
                exposure_count = exposure_count + ?,
                last_exposure = ?,
                total_items = total_items + ?
        """, (domain, items_count, date.today().isoformat(), items_count,
              items_count, date.today().isoformat(), items_count))
        conn.commit()


def get_domain_exposure() -> dict:
    """Get exposure data for all domains."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM domain_exposure").fetchall()
        return {row["domain"]: dict(row) for row in rows}


def get_underexposed_domains(limit: int = 3) -> list:
    """Get domains with lowest exposure."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT domain, exposure_count FROM domain_exposure
            ORDER BY exposure_count ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return [row["domain"] for row in rows]


# ============== Grammar Pattern Operations ==============

def save_grammar_pattern(pattern: dict) -> None:
    """Save a grammar pattern."""
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO grammar_patterns
            (pattern_name, category, description, examples)
            VALUES (?, ?, ?, ?)
        """, (
            pattern["name"],
            pattern["category"],
            pattern.get("description"),
            json.dumps(pattern.get("examples", []))
        ))
        conn.commit()


def get_grammar_for_review() -> list:
    """Get grammar patterns due for review."""
    today = date.today().isoformat()
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT * FROM grammar_patterns
            WHERE next_review IS NULL OR next_review <= ?
            ORDER BY next_review ASC, ease_factor ASC
            LIMIT 10
        """, (today,)).fetchall()]


# ============== Daily Mission Operations ==============

def save_daily_mission(mission: dict) -> int:
    """Save a daily mission and return its ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO daily_missions
            (mission_date, mission_type, prompt, constraints, user_response, feedback, score, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mission.get("date", date.today().isoformat()),
            mission["type"],
            mission.get("prompt"),
            json.dumps(mission.get("constraints", [])),
            mission.get("user_response"),
            mission.get("feedback"),
            mission.get("score"),
            mission.get("completed", 0)
        ))
        conn.commit()
        return cursor.lastrowid


def get_today_mission() -> Optional[dict]:
    """Get today's mission if exists."""
    today = date.today().isoformat()
    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM daily_missions WHERE mission_date = ?
            ORDER BY id DESC LIMIT 1
        """, (today,)).fetchone()
        return dict(row) if row else None


def update_mission_response(mission_id: int, response: str, feedback: str, score: float) -> None:
    """Update mission with user's response."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE daily_missions SET
                user_response = ?,
                feedback = ?,
                score = ?,
                completed = 1
            WHERE id = ?
        """, (response, feedback, score, mission_id))
        conn.commit()


# ============== Conversation Operations ==============

def save_conversation(conv: dict) -> int:
    """Save a conversation session."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO conversations
            (scenario_title, hidden_targets, messages, achieved_targets, feedback, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conv["title"],
            json.dumps(conv.get("hidden_targets", [])),
            json.dumps(conv.get("messages", [])),
            json.dumps(conv.get("achieved_targets", [])),
            conv.get("feedback"),
            conv.get("completed", 0)
        ))
        conn.commit()
        return cursor.lastrowid


# ============== Progress Metrics Operations ==============

def record_progress(metrics: dict) -> None:
    """Record daily progress metrics."""
    today = date.today().isoformat()
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM progress_metrics WHERE metric_date = ?", (today,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE progress_metrics SET
                    speaking_minutes = speaking_minutes + ?,
                    writing_words = writing_words + ?,
                    vocab_reviewed = vocab_reviewed + ?,
                    grammar_reviewed = grammar_reviewed + ?,
                    errors_fixed = errors_fixed + ?,
                    missions_completed = missions_completed + ?
                WHERE metric_date = ?
            """, (
                metrics.get("speaking_minutes", 0),
                metrics.get("writing_words", 0),
                metrics.get("vocab_reviewed", 0),
                metrics.get("grammar_reviewed", 0),
                metrics.get("errors_fixed", 0),
                metrics.get("missions_completed", 0),
                today
            ))
        else:
            conn.execute("""
                INSERT INTO progress_metrics
                (metric_date, speaking_minutes, writing_words, vocab_reviewed,
                 grammar_reviewed, errors_fixed, missions_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                metrics.get("speaking_minutes", 0),
                metrics.get("writing_words", 0),
                metrics.get("vocab_reviewed", 0),
                metrics.get("grammar_reviewed", 0),
                metrics.get("errors_fixed", 0),
                metrics.get("missions_completed", 0)
            ))
        conn.commit()


def get_progress_history(days: int = 30) -> list:
    """Get progress history for the last N days."""
    start_date = (date.today() - timedelta(days=days)).isoformat()
    with get_connection() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT * FROM progress_metrics
            WHERE metric_date >= ?
            ORDER BY metric_date ASC
        """, (start_date,)).fetchall()]


def get_total_stats() -> dict:
    """Get total statistics across all time."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(speaking_minutes), 0) as total_speaking,
                COALESCE(SUM(writing_words), 0) as total_writing,
                COALESCE(SUM(vocab_reviewed), 0) as total_vocab,
                COALESCE(SUM(grammar_reviewed), 0) as total_grammar,
                COALESCE(SUM(errors_fixed), 0) as total_errors,
                COALESCE(SUM(missions_completed), 0) as total_missions
            FROM progress_metrics
        """).fetchone()
        return dict(row) if row else {}


# ============== User Profile Operations ==============

def get_user_profile() -> dict:
    """Get user profile."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
        return dict(row) if row else {}


def update_user_profile(profile: dict) -> None:
    """Update user profile."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE user_profile SET
                name = ?,
                level = ?,
                weekly_goal = ?,
                placement_completed = ?,
                placement_score = ?,
                focus_areas = ?,
                dialect_preference = ?,
                updated_at = ?
            WHERE id = 1
        """, (
            profile.get("name", ""),
            profile.get("level", "C1"),
            profile.get("weekly_goal", 6),
            profile.get("placement_completed", 0),
            profile.get("placement_score"),
            json.dumps(profile.get("focus_areas", [])),
            profile.get("dialect_preference", "Spain"),
            datetime.now().isoformat()
        ))
        conn.commit()


# ============== Portfolio Operations ==============

def load_portfolio() -> dict:
    """Load portfolio from JSON file."""
    if not PORTFOLIO_PATH.exists():
        return {
            "writing_samples": [],
            "recordings": [],
            "transcripts": [],
            "benchmarks": [],
        }
    return json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))


def save_portfolio(portfolio: dict) -> None:
    """Save portfolio to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_PATH.write_text(json.dumps(portfolio, indent=2), encoding="utf-8")


# ============== Export Operations ==============

def export_vocab_json() -> str:
    """Export vocabulary as JSON."""
    items = get_vocab_items()
    return json.dumps(items, indent=2, ensure_ascii=False)


def export_mistakes_json() -> str:
    """Export mistakes as JSON."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM mistakes ORDER BY created_at DESC").fetchall()
        return json.dumps([dict(row) for row in rows], indent=2, ensure_ascii=False)


def export_progress_json() -> str:
    """Export progress as JSON."""
    history = get_progress_history(365)
    stats = get_total_stats()
    return json.dumps({"history": history, "totals": stats}, indent=2, ensure_ascii=False)


def get_active_vocab_count() -> int:
    """Get count of vocabulary items that have been produced (used in output)."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT COUNT(*) as count FROM vocab_items
            WHERE status IN ('learning', 'mastered') AND exposure_count > 0
        """).fetchone()
        return row["count"] if row else 0


def save_transcript(text: str, duration: int = 0, mission_id: Optional[int] = None) -> None:
    """Save a transcript."""
    if not text.strip():
        return
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transcripts (transcript, duration_seconds, mission_id)
            VALUES (?, ?, ?)
        """, (text, duration, mission_id))
        conn.commit()
