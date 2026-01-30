"""Database management for VivaLingo Pro with multi-profile support."""
import sqlite3
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
import json

# Configure logging for database operations
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "vivalingo.db"
PORTFOLIO_PATH = DATA_DIR / "portfolio.json"

# Global active profile ID (defaults to 1)
_active_profile_id: int = 1


def get_active_profile_id() -> int:
    """Get the currently active profile ID."""
    return _active_profile_id


def set_active_profile_id(profile_id: int) -> None:
    """Set the active profile ID."""
    global _active_profile_id
    _active_profile_id = profile_id


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_tables_exist() -> None:
    """Ensure all required tables exist (call after init_db)."""
    try:
        with get_connection() as conn:
            # Check if domain_exposure table exists and has correct structure
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='domain_exposure'
            """)
            if not cursor.fetchone():
                # Table doesn't exist, create it
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS domain_exposure (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_id INTEGER DEFAULT 1,
                        domain TEXT NOT NULL,
                        exposure_count INTEGER DEFAULT 0,
                        last_exposure TEXT,
                        total_items INTEGER DEFAULT 0,
                        mastered_items INTEGER DEFAULT 0,
                        UNIQUE(profile_id, domain)
                    )
                """)
                conn.commit()
    except Exception as e:
        print(f"Warning: Could not ensure tables exist: {e}")


def init_db() -> None:
    """Initialize the database with all required tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        # Profiles table for multi-user support
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT DEFAULT 'C1',
                weekly_goal INTEGER DEFAULT 6,
                placement_completed INTEGER DEFAULT 0,
                placement_score REAL,
                focus_areas TEXT,
                dialect_preference TEXT DEFAULT 'Spain',
                avatar_color TEXT DEFAULT '#6366f1',
                is_active INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Vocabulary items with domain tagging - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vocab_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
                term TEXT NOT NULL,
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_id, term)
            )
        """)

        # Mistakes with detailed tracking - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
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

        # Domain exposure tracking - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domain_exposure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
                domain TEXT NOT NULL,
                exposure_count INTEGER DEFAULT 0,
                last_exposure TEXT,
                total_items INTEGER DEFAULT 0,
                mastered_items INTEGER DEFAULT 0,
                UNIQUE(profile_id, domain)
            )
        """)

        # Grammar patterns for SRS - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS grammar_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
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

        # Daily missions history - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
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

        # Conversation sessions - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
                scenario_title TEXT NOT NULL,
                hidden_targets TEXT,
                messages TEXT,
                achieved_targets TEXT,
                feedback TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User progress metrics - now with profile_id
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
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

        # Activity log for detailed exercise history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
                activity_type TEXT NOT NULL,
                activity_name TEXT,
                details TEXT,
                score REAL,
                duration_seconds INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Legacy user_profile table (kept for backwards compatibility)
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

        # Initialize legacy user profile if not exists
        conn.execute("""
            INSERT OR IGNORE INTO user_profile (id) VALUES (1)
        """)

        conn.commit()

    # Ensure all tables exist after init
    ensure_tables_exist()


def init_profile_domains(profile_id: int) -> None:
    """Initialize default domains for a profile."""
    if profile_id is None:
        return

    domains = [
        "Healthcare", "Housing", "Relationships", "Travel problems",
        "Workplace conflict", "Finance", "Cooking", "Emotions",
        "Bureaucracy", "Everyday slang-light"
    ]
    try:
        with get_connection() as conn:
            # Ensure table exists with all required columns
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domain_exposure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER DEFAULT 1,
                    domain TEXT NOT NULL,
                    exposure_count INTEGER DEFAULT 0,
                    last_exposure TEXT,
                    total_items INTEGER DEFAULT 0,
                    mastered_items INTEGER DEFAULT 0,
                    UNIQUE(profile_id, domain)
                )
            """)
            # Insert domains one by one
            for domain in domains:
                conn.execute("""
                    INSERT OR IGNORE INTO domain_exposure
                    (profile_id, domain, exposure_count, total_items, mastered_items)
                    VALUES (?, ?, ?, ?, ?)
                """, (profile_id, domain, 0, 0, 0))
            conn.commit()
    except Exception as e:
        # Log error but don't crash - domains can be initialized later
        print(f"Warning: Could not initialize profile domains: {e}")


# ============== Profile Operations ==============

def get_all_profiles() -> list:
    """Get all profiles."""
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM profiles ORDER BY created_at ASC
            """).fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


def create_profile(name: str, level: str = "C1") -> Optional[int]:
    """Create a new profile and return its ID."""
    profile_id = None
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO profiles (name, level, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (name, level, 0, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            profile_id = cursor.lastrowid

        # Initialize domains for this profile (with error handling)
        if profile_id is not None:
            try:
                init_profile_domains(profile_id)
            except Exception as e:
                print(f"Warning: Could not initialize domains for profile {profile_id}: {e}")
                # Don't fail profile creation if domains can't be initialized

        return profile_id
    except Exception as e:
        print(f"Error creating profile: {e}")
        return None


def get_profile(profile_id: int) -> Optional[dict]:
    """Get a specific profile by ID."""
    try:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM profiles WHERE id = ?
            """, (profile_id,)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def update_profile(profile_id: int, profile: dict) -> None:
    """Update a profile."""
    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE profiles SET
                    name = ?,
                    level = ?,
                    weekly_goal = ?,
                    placement_completed = ?,
                    placement_score = ?,
                    focus_areas = ?,
                    dialect_preference = ?,
                    avatar_color = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                profile.get("name", ""),
                profile.get("level", "C1"),
                profile.get("weekly_goal", 6),
                profile.get("placement_completed", 0),
                profile.get("placement_score"),
                json.dumps(profile.get("focus_areas", [])),
                profile.get("dialect_preference", "Spain"),
                profile.get("avatar_color", "#6366f1"),
                datetime.now().isoformat(),
                profile_id
            ))
            conn.commit()
    except Exception as e:
        logger.warning(f"Profile update failed for ID {profile_id}: {e}")


def delete_profile(profile_id: int) -> None:
    """Delete a profile and all associated data."""
    try:
        with get_connection() as conn:
            # Delete all associated data
            conn.execute("DELETE FROM vocab_items WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM mistakes WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM domain_exposure WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM grammar_patterns WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM daily_missions WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM conversations WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM progress_metrics WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM activity_log WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Profile deletion failed for ID {profile_id}: {e}")
        raise  # Re-raise since deletion failure is critical


def get_profile_stats(profile_id: int) -> dict:
    """Get stats for a specific profile."""
    try:
        with get_connection() as conn:
            # Total vocab
            vocab_row = conn.execute("""
                SELECT COUNT(*) as count FROM vocab_items
                WHERE profile_id = ? AND status IN ('learning', 'mastered')
            """, (profile_id,)).fetchone()

            # Total progress
            progress_row = conn.execute("""
                SELECT
                    COALESCE(SUM(speaking_minutes), 0) as total_speaking,
                    COALESCE(SUM(vocab_reviewed), 0) as total_vocab,
                    COALESCE(SUM(missions_completed), 0) as total_missions,
                    COALESCE(SUM(errors_fixed), 0) as total_errors
                FROM progress_metrics WHERE profile_id = ?
            """, (profile_id,)).fetchone()

            return {
                "vocab_count": vocab_row["count"] if vocab_row else 0,
                "total_speaking": progress_row["total_speaking"] if progress_row else 0,
                "total_vocab": progress_row["total_vocab"] if progress_row else 0,
                "total_missions": progress_row["total_missions"] if progress_row else 0,
                "total_errors": progress_row["total_errors"] if progress_row else 0,
            }
    except Exception:
        return {"vocab_count": 0, "total_speaking": 0, "total_vocab": 0, "total_missions": 0, "total_errors": 0}


# ============== Activity Log Operations ==============

def log_activity(activity_type: str, activity_name: str = "", details: str = "",
                 score: float = None, duration_seconds: int = 0) -> None:
    """Log an activity for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO activity_log
                (profile_id, activity_type, activity_name, details, score, duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (profile_id, activity_type, activity_name, details, score, duration_seconds,
                  datetime.now().isoformat()))
            conn.commit()
    except Exception as e:
        logger.warning(f"Activity logging failed: {e}")


def get_activity_history(days: int = 30, limit: int = 100) -> list:
    """Get activity history for the active profile."""
    profile_id = get_active_profile_id()
    try:
        start_date = (date.today() - timedelta(days=days)).isoformat()
        with get_connection() as conn:
            return [dict(row) for row in conn.execute("""
                SELECT * FROM activity_log
                WHERE profile_id = ? AND created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (profile_id, start_date, limit)).fetchall()]
    except Exception:
        return []


# ============== Vocabulary Operations ==============

def save_vocab_item(item: dict) -> None:
    """Save or update a vocabulary item for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO vocab_items
                (profile_id, term, meaning, example, domain, register, part_of_speech, contexts, collocations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(profile_id, term) DO UPDATE SET
                    meaning = excluded.meaning,
                    example = excluded.example,
                    domain = excluded.domain,
                    register = excluded.register,
                    part_of_speech = excluded.part_of_speech,
                    contexts = excluded.contexts,
                    collocations = excluded.collocations
            """, (
                profile_id,
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
    except Exception as e:
        logger.warning(f"Vocab save failed for '{item.get('term', 'unknown')}': {e}")


def get_vocab_items(domain: Optional[str] = None, status: Optional[str] = None) -> list:
    """Get vocabulary items for the active profile, optionally filtered."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            query = "SELECT * FROM vocab_items WHERE profile_id = ?"
            params = [profile_id]
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC"
            return [dict(row) for row in conn.execute(query, params).fetchall()]
    except Exception:
        return []


def get_vocab_for_review() -> list:
    """Get vocabulary items due for review for the active profile."""
    profile_id = get_active_profile_id()
    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            return [dict(row) for row in conn.execute("""
                SELECT * FROM vocab_items
                WHERE profile_id = ? AND (next_review IS NULL OR next_review <= ?)
                ORDER BY next_review ASC, ease_factor ASC
                LIMIT 20
            """, (profile_id, today)).fetchall()]
    except Exception:
        return []


def update_vocab_review(term: str, quality: int) -> None:
    """Update vocabulary item after review using SM-2 algorithm."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM vocab_items WHERE profile_id = ? AND term = ?", (profile_id, term)
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
                WHERE profile_id = ? AND term = ?
            """, (date.today().isoformat(), next_review, ease_factor, interval, status, profile_id, term))
            conn.commit()
    except Exception as e:
        logger.warning(f"Vocab review update failed for '{term}': {e}")


# ============== Mistake Operations ==============

def save_mistake(entry: dict) -> Optional[int]:
    """Save a mistake entry for the active profile and return its ID."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO mistakes
                (profile_id, user_text, corrected_text, error_type, error_tag, pattern, explanation, examples, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
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
    except Exception:
        return None


def get_mistakes_for_review() -> list:
    """Get mistakes due for review for the active profile."""
    profile_id = get_active_profile_id()
    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            return [dict(row) for row in conn.execute("""
                SELECT * FROM mistakes
                WHERE profile_id = ? AND (next_review IS NULL OR next_review <= ?)
                ORDER BY next_review ASC, ease_factor ASC
                LIMIT 15
            """, (profile_id, today)).fetchall()]
    except Exception:
        return []


def get_mistake_stats() -> dict:
    """Get statistics about mistakes by type for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT error_type, COUNT(*) as count,
                       AVG(ease_factor) as avg_ease
                FROM mistakes
                WHERE profile_id = ?
                GROUP BY error_type
                ORDER BY count DESC
            """, (profile_id,)).fetchall()
            return {row["error_type"]: {"count": row["count"], "avg_ease": row["avg_ease"]}
                    for row in rows}
    except Exception:
        return {}


def update_mistake_review(mistake_id: int, quality: int) -> None:
    """Update mistake after review using SM-2 algorithm."""
    try:
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
    except Exception as e:
        logger.warning(f"Mistake review update failed for ID {mistake_id}: {e}")


# ============== Domain Exposure Operations ==============

def record_domain_exposure(domain: str, items_count: int = 1) -> None:
    """Record exposure to a domain for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO domain_exposure (profile_id, domain, exposure_count, last_exposure, total_items)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(profile_id, domain) DO UPDATE SET
                    exposure_count = exposure_count + ?,
                    last_exposure = ?,
                    total_items = total_items + ?
            """, (profile_id, domain, items_count, date.today().isoformat(), items_count,
                  items_count, date.today().isoformat(), items_count))
            conn.commit()
    except Exception as e:
        logger.warning(f"Domain exposure recording failed for '{domain}': {e}")


def get_domain_exposure() -> dict:
    """Get exposure data for all domains for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM domain_exposure WHERE profile_id = ?",
                (profile_id,)
            ).fetchall()
            return {row["domain"]: dict(row) for row in rows}
    except Exception:
        return {}


def get_underexposed_domains(limit: int = 3) -> list:
    """Get domains with lowest exposure for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT domain, exposure_count FROM domain_exposure
                WHERE profile_id = ?
                ORDER BY exposure_count ASC
                LIMIT ?
            """, (profile_id, limit)).fetchall()
            return [row["domain"] for row in rows]
    except Exception:
        return []


# ============== Grammar Pattern Operations ==============

def save_grammar_pattern(pattern: dict) -> None:
    """Save a grammar pattern for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO grammar_patterns
                (profile_id, pattern_name, category, description, examples)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile_id,
                pattern["name"],
                pattern["category"],
                pattern.get("description"),
                json.dumps(pattern.get("examples", []))
            ))
            conn.commit()
    except Exception as e:
        logger.warning(f"Grammar pattern save failed for '{pattern.get('name', 'unknown')}': {e}")


def get_grammar_for_review() -> list:
    """Get grammar patterns due for review for the active profile."""
    profile_id = get_active_profile_id()
    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            return [dict(row) for row in conn.execute("""
                SELECT * FROM grammar_patterns
                WHERE profile_id = ? AND (next_review IS NULL OR next_review <= ?)
                ORDER BY next_review ASC, ease_factor ASC
                LIMIT 10
            """, (profile_id, today)).fetchall()]
    except Exception:
        return []


# ============== Daily Mission Operations ==============

def save_daily_mission(mission: dict) -> Optional[int]:
    """Save a daily mission for the active profile and return its ID."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO daily_missions
                (profile_id, mission_date, mission_type, prompt, constraints, user_response, feedback, score, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
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
    except Exception:
        return None


def get_today_mission() -> Optional[dict]:
    """Get today's mission for the active profile if exists."""
    profile_id = get_active_profile_id()
    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM daily_missions WHERE profile_id = ? AND mission_date = ?
                ORDER BY id DESC LIMIT 1
            """, (profile_id, today)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def update_mission_response(mission_id: int, response: str, feedback: str, score: float) -> None:
    """Update mission with user's response."""
    try:
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
    except Exception as e:
        logger.warning(f"Mission response update failed for ID {mission_id}: {e}")


# ============== Conversation Operations ==============

def save_conversation(conv: dict) -> Optional[int]:
    """Save a conversation session for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO conversations
                (profile_id, scenario_title, hidden_targets, messages, achieved_targets, feedback, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                conv["title"],
                json.dumps(conv.get("hidden_targets", [])),
                json.dumps(conv.get("messages", [])),
                json.dumps(conv.get("achieved_targets", [])),
                conv.get("feedback"),
                conv.get("completed", 0)
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception:
        return None


# ============== Progress Metrics Operations ==============

def record_progress(metrics: dict) -> None:
    """Record daily progress metrics for the active profile."""
    profile_id = get_active_profile_id()
    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM progress_metrics WHERE profile_id = ? AND metric_date = ?",
                (profile_id, today)
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
                    WHERE profile_id = ? AND metric_date = ?
                """, (
                    metrics.get("speaking_minutes", 0),
                    metrics.get("writing_words", 0),
                    metrics.get("vocab_reviewed", 0),
                    metrics.get("grammar_reviewed", 0),
                    metrics.get("errors_fixed", 0),
                    metrics.get("missions_completed", 0),
                    profile_id,
                    today
                ))
            else:
                conn.execute("""
                    INSERT INTO progress_metrics
                    (profile_id, metric_date, speaking_minutes, writing_words, vocab_reviewed,
                     grammar_reviewed, errors_fixed, missions_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_id,
                    today,
                    metrics.get("speaking_minutes", 0),
                    metrics.get("writing_words", 0),
                    metrics.get("vocab_reviewed", 0),
                    metrics.get("grammar_reviewed", 0),
                    metrics.get("errors_fixed", 0),
                    metrics.get("missions_completed", 0)
                ))
            conn.commit()
    except Exception as e:
        logger.warning(f"Progress recording failed: {e}")


def get_progress_history(days: int = 30) -> list:
    """Get progress history for the last N days for the active profile."""
    profile_id = get_active_profile_id()
    try:
        start_date = (date.today() - timedelta(days=days)).isoformat()
        with get_connection() as conn:
            return [dict(row) for row in conn.execute("""
                SELECT * FROM progress_metrics
                WHERE profile_id = ? AND metric_date >= ?
                ORDER BY metric_date ASC
            """, (profile_id, start_date)).fetchall()]
    except Exception:
        return []


def get_total_stats() -> dict:
    """Get total statistics across all time for the active profile."""
    profile_id = get_active_profile_id()
    try:
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
                WHERE profile_id = ?
            """, (profile_id,)).fetchone()
            return dict(row) if row else {
                "total_speaking": 0,
                "total_writing": 0,
                "total_vocab": 0,
                "total_grammar": 0,
                "total_errors": 0,
                "total_missions": 0
            }
    except Exception:
        return {
            "total_speaking": 0,
            "total_writing": 0,
            "total_vocab": 0,
            "total_grammar": 0,
            "total_errors": 0,
            "total_missions": 0
        }


# ============== User Profile Operations ==============

def get_user_profile() -> dict:
    """Get user profile for the active profile (uses new profiles table)."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            # Try new profiles table first
            row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
            if row:
                return dict(row)
            # Fall back to legacy table
            row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
            return dict(row) if row else {
                "id": 1,
                "name": "",
                "level": "C1",
                "weekly_goal": 6,
                "placement_completed": 0,
                "dialect_preference": "Spain"
            }
    except Exception:
        return {
            "id": 1,
            "name": "",
            "level": "C1",
            "weekly_goal": 6,
            "placement_completed": 0,
            "dialect_preference": "Spain"
        }


def update_user_profile(profile: dict) -> None:
    """Update user profile for the active profile."""
    try:
        profile_id = get_active_profile_id()

        # Try to update in new profiles table first
        existing = get_profile(profile_id)
        if existing:
            update_profile(profile_id, profile)
        else:
            # Fall back to legacy table
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
    except Exception as e:
        logger.warning(f"User profile update failed: {e}")


# ============== Portfolio Operations ==============

def load_portfolio() -> dict:
    """Load portfolio from JSON file."""
    try:
        if not PORTFOLIO_PATH.exists():
            return {
                "writing_samples": [],
                "recordings": [],
                "transcripts": [],
                "benchmarks": [],
            }
        return json.loads(PORTFOLIO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "writing_samples": [],
            "recordings": [],
            "transcripts": [],
            "benchmarks": [],
        }


def save_portfolio(portfolio: dict) -> None:
    """Save portfolio to JSON file."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PORTFOLIO_PATH.write_text(json.dumps(portfolio, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Portfolio save failed: {e}")


# ============== Export Operations ==============

def export_vocab_json() -> str:
    """Export vocabulary as JSON."""
    items = get_vocab_items()
    return json.dumps(items, indent=2, ensure_ascii=False)


def export_mistakes_json() -> str:
    """Export mistakes as JSON for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM mistakes WHERE profile_id = ? ORDER BY created_at DESC",
                (profile_id,)
            ).fetchall()
            return json.dumps([dict(row) for row in rows], indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error exporting mistakes: {e}")
        return "[]"


def export_progress_json() -> str:
    """Export progress as JSON."""
    history = get_progress_history(365)
    stats = get_total_stats()
    return json.dumps({"history": history, "totals": stats}, indent=2, ensure_ascii=False)


def get_active_vocab_count() -> int:
    """Get count of vocabulary items that have been produced (used in output) for the active profile."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) as count FROM vocab_items
                WHERE profile_id = ? AND status IN ('learning', 'mastered') AND exposure_count > 0
            """, (profile_id,)).fetchone()
            return row["count"] if row else 0
    except Exception:
        return 0


def save_transcript(text: str, duration: int = 0, mission_id: Optional[int] = None) -> None:
    """Save a transcript."""
    if not text.strip():
        return
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO transcripts (transcript, duration_seconds, mission_id)
                VALUES (?, ?, ?)
            """, (text, duration, mission_id))
            conn.commit()
    except Exception as e:
        logger.warning(f"Transcript save failed: {e}")
