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

DATA_DIR = Path(__file__).parent.parent / "data"
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
    if profile_id is None or profile_id < 1:
        logger.warning(f"Invalid profile_id: {profile_id}, keeping current: {_active_profile_id}")
        return
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
                focus_mode INTEGER DEFAULT 0,
                accent_tolerance INTEGER DEFAULT 0,
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_id, pattern_name)
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

        # Transcripts for speaking practice - with profile_id for data isolation
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
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

        # Issue reports for user feedback on corrections
        conn.execute("""
            CREATE TABLE IF NOT EXISTS issue_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT 1,
                report_type TEXT NOT NULL,
                context TEXT,
                user_answer TEXT,
                expected_answer TEXT,
                user_comment TEXT,
                status TEXT DEFAULT 'pending',
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

        # Performance indexes for frequently queried columns
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vocab_profile_status ON vocab_items(profile_id, status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_vocab_next_review ON vocab_items(profile_id, next_review)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mistakes_next_review ON mistakes(profile_id, next_review)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_profile_date ON activity_log(profile_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_progress_profile_date ON progress_metrics(profile_id, metric_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_grammar_next_review ON grammar_patterns(profile_id, next_review)")

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


def create_profile(name: str, level: str = "C1", dialect_preference: str = "Spain",
                   weekly_goal: int = 6, focus_areas: Optional[list] = None) -> Optional[int]:
    """Create a new profile and return its ID.

    Args:
        name: User's display name
        level: Spanish proficiency level (B2, C1, C2)
        dialect_preference: Preferred Spanish dialect (Spain, Mexico, Argentina, Colombia, Chile)
        weekly_goal: Target practice sessions per week (3-7)
        focus_areas: List of focus areas (Grammar, Vocabulary, Conversation, Writing)

    Returns:
        Profile ID if created successfully, None otherwise
    """
    profile_id = None
    focus_areas_json = json.dumps(focus_areas) if focus_areas else json.dumps([])
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO profiles (name, level, dialect_preference, weekly_goal, focus_areas,
                                      is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, level, dialect_preference, weekly_goal, focus_areas_json,
                  0, datetime.now().isoformat(), datetime.now().isoformat()))
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
            # Try to update with new columns first
            try:
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
                        focus_mode = ?,
                        accent_tolerance = ?,
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
                    profile.get("focus_mode", 0),
                    profile.get("accent_tolerance", 0),
                    datetime.now().isoformat(),
                    profile_id
                ))
            except sqlite3.OperationalError:
                # Fall back to old columns if new ones don't exist
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
            # Delete child tables first to respect foreign key constraints
            # near_misses and personal_syllabus reference error_fingerprints
            conn.execute("DELETE FROM near_misses WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM personal_syllabus WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM error_fingerprints WHERE profile_id = ?", (profile_id,))
            # transcripts references daily_missions
            conn.execute("DELETE FROM transcripts WHERE profile_id = ?", (profile_id,))
            # conversation_outcomes references conversations
            conn.execute("DELETE FROM conversation_outcomes WHERE profile_id = ?", (profile_id,))
            # Now delete remaining tables
            conn.execute("DELETE FROM vocab_items WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM mistakes WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM domain_exposure WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM grammar_patterns WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM daily_missions WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM conversations WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM progress_metrics WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM activity_log WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM issue_reports WHERE profile_id = ?", (profile_id,))
            conn.execute("DELETE FROM pragmatics_exposure WHERE profile_id = ?", (profile_id,))
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
    quality = max(0, min(5, quality))  # Clamp to valid range
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
            exposure = row["exposure_count"] or 0

            # SM-2 algorithm with proper initial steps
            if quality >= 3:
                if exposure == 0 or interval <= 1:
                    interval = 1
                elif interval < 6:
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
    quality = max(0, min(5, quality))  # Clamp to valid range
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM mistakes WHERE id = ? AND profile_id = ?", (mistake_id, profile_id)
            ).fetchone()
            if not row:
                return

            ease_factor = row["ease_factor"]
            interval = row["interval_days"]
            review_count = row["review_count"] or 0

            if quality >= 3:
                if review_count == 0 or interval <= 1:
                    interval = 1
                elif interval < 6:
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
                WHERE id = ? AND profile_id = ?
            """, (date.today().isoformat(), next_review, ease_factor, interval, mistake_id, profile_id))
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
                    exposure_count = domain_exposure.exposure_count + excluded.exposure_count,
                    last_exposure = excluded.last_exposure,
                    total_items = domain_exposure.total_items + excluded.total_items
            """, (profile_id, domain, items_count, date.today().isoformat(), items_count))
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
                INSERT INTO grammar_patterns
                (profile_id, pattern_name, category, description, examples)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(profile_id, pattern_name) DO UPDATE SET
                    category = excluded.category,
                    description = excluded.description,
                    examples = excluded.examples
            """, (
                profile_id,
                pattern.get("name", ""),
                pattern.get("category", ""),
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
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE daily_missions SET
                    user_response = ?,
                    feedback = ?,
                    score = ?,
                    completed = 1
                WHERE id = ? AND profile_id = ?
            """, (response, feedback, score, mission_id, profile_id))
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
    """Save a transcript for the active profile."""
    if not text or not text.strip():
        return
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO transcripts (profile_id, transcript, duration_seconds, mission_id)
                VALUES (?, ?, ?, ?)
            """, (profile_id, text, duration, mission_id))
            conn.commit()
    except Exception as e:
        logger.warning(f"Transcript save failed: {e}")


# ============== Error Fingerprint Operations ==============

# Error taxonomy for granular tracking
ERROR_TAXONOMY = {
    "verb_tense": {
        "preterito_imperfecto": "Pretérito vs Imperfecto confusion",
        "subjunctive_triggers": "Subjunctive trigger words (cuando, aunque, ojalá)",
        "conditional_usage": "Conditional mood usage",
        "future_ir_a": "Future tense vs ir a + infinitive",
    },
    "ser_estar": {
        "permanent_temporary": "Ser vs estar for states",
        "location_event": "Estar for location, ser for events",
        "passive_voice": "Passive voice with ser vs estar",
    },
    "prepositions": {
        "por_para": "Por vs para distinction",
        "a_personal": "Personal 'a' before direct objects",
        "en_a_location": "En vs a for location/direction",
        "de_possession": "De for possession and origin",
    },
    "pronouns": {
        "clitic_placement": "Clitic pronoun placement (me lo, se lo)",
        "leismo": "Leísmo patterns (le vs lo)",
        "reflexive_usage": "Reflexive pronoun usage",
        "indirect_object": "Indirect object pronouns",
    },
    "agreement": {
        "gender_noun": "Gender agreement with nouns",
        "gender_adjective": "Gender agreement with adjectives",
        "number_agreement": "Number (singular/plural) agreement",
    },
    "vocabulary": {
        "false_friends": "False cognates (embarazada, sensible)",
        "calques": "Literal translations from English",
        "register_mismatch": "Formal/informal register mismatch",
    },
    "word_order": {
        "adjective_position": "Adjective placement",
        "adverb_position": "Adverb placement",
        "question_formation": "Question word order",
    },
}


def init_fingerprint_tables() -> None:
    """Initialize error fingerprint tracking tables."""
    try:
        with get_connection() as conn:
            # Error fingerprints table - tracks error patterns per user
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    error_count INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    last_correct TEXT,
                    confidence REAL DEFAULT 0.5,
                    priority_score REAL DEFAULT 0.0,
                    rule_boundary TEXT,
                    examples TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(profile_id, category, subcategory)
                )
            """)

            # Near-miss tracking for "almost correct" answers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS near_misses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    fingerprint_id INTEGER,
                    user_input TEXT NOT NULL,
                    expected TEXT NOT NULL,
                    rule_explanation TEXT,
                    contrast_example TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fingerprint_id) REFERENCES error_fingerprints(id)
                )
            """)

            # Personal syllabus - prioritized learning items
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_syllabus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    fingerprint_id INTEGER,
                    week_start TEXT NOT NULL,
                    priority_rank INTEGER DEFAULT 0,
                    target_practice_count INTEGER DEFAULT 5,
                    actual_practice_count INTEGER DEFAULT 0,
                    improvement_score REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fingerprint_id) REFERENCES error_fingerprints(id)
                )
            """)

            # Pragmatics and culture patterns
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pragmatics_exposure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    dialect TEXT DEFAULT 'neutral',
                    exposure_count INTEGER DEFAULT 0,
                    production_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    UNIQUE(profile_id, pattern_type, pattern_name, dialect)
                )
            """)

            # Conversation outcomes for turn-taking practice
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    conversation_id INTEGER,
                    outcome_type TEXT NOT NULL,
                    achieved INTEGER DEFAULT 0,
                    details TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)

            conn.commit()
    except Exception as e:
        logger.warning(f"Fingerprint tables initialization failed: {e}")


def record_error_fingerprint(category: str, subcategory: str, is_error: bool = True,
                             user_input: str = "", expected: str = "",
                             rule_explanation: str = "", contrast_example: str = "") -> None:
    """Record an error or correct usage in the fingerprint system."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            # Upsert the fingerprint record
            if is_error:
                conn.execute("""
                    INSERT INTO error_fingerprints
                    (profile_id, category, subcategory, error_count, last_error, updated_at)
                    VALUES (?, ?, ?, 1, ?, ?)
                    ON CONFLICT(profile_id, category, subcategory) DO UPDATE SET
                        error_count = error_count + 1,
                        last_error = excluded.last_error,
                        updated_at = excluded.updated_at
                """, (profile_id, category, subcategory, datetime.now().isoformat(),
                      datetime.now().isoformat()))
            else:
                conn.execute("""
                    INSERT INTO error_fingerprints
                    (profile_id, category, subcategory, correct_count, last_correct, updated_at)
                    VALUES (?, ?, ?, 1, ?, ?)
                    ON CONFLICT(profile_id, category, subcategory) DO UPDATE SET
                        correct_count = correct_count + 1,
                        last_correct = excluded.last_correct,
                        updated_at = excluded.updated_at
                """, (profile_id, category, subcategory, datetime.now().isoformat(),
                      datetime.now().isoformat()))

            # Update confidence and priority scores
            row = conn.execute("""
                SELECT * FROM error_fingerprints
                WHERE profile_id = ? AND category = ? AND subcategory = ?
            """, (profile_id, category, subcategory)).fetchone()

            if row:
                total = row["error_count"] + row["correct_count"]
                confidence = row["correct_count"] / total if total > 0 else 0.5
                # Priority: more errors + lower confidence = higher priority
                priority = (row["error_count"] * 2) * (1 - confidence) if total > 0 else 0

                conn.execute("""
                    UPDATE error_fingerprints SET
                        confidence = ?, priority_score = ?
                    WHERE id = ?
                """, (confidence, priority, row["id"]))

                # Record near-miss if applicable
                if is_error and user_input and expected:
                    conn.execute("""
                        INSERT INTO near_misses
                        (profile_id, fingerprint_id, user_input, expected,
                         rule_explanation, contrast_example)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (profile_id, row["id"], user_input, expected,
                          rule_explanation, contrast_example))

            conn.commit()
    except Exception as e:
        logger.warning(f"Error fingerprint recording failed: {e}")


def get_error_fingerprints(limit: int = 20) -> list:
    """Get error fingerprints for the active profile, sorted by priority."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM error_fingerprints
                WHERE profile_id = ?
                ORDER BY priority_score DESC, error_count DESC
                LIMIT ?
            """, (profile_id, limit)).fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


def get_fingerprint_summary() -> dict:
    """Get a summary of error fingerprints by category."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT category,
                       SUM(error_count) as total_errors,
                       SUM(correct_count) as total_correct,
                       AVG(confidence) as avg_confidence,
                       MAX(priority_score) as max_priority
                FROM error_fingerprints
                WHERE profile_id = ?
                GROUP BY category
                ORDER BY total_errors DESC
            """, (profile_id,)).fetchall()
            return {row["category"]: dict(row) for row in rows}
    except Exception:
        return {}


def generate_personal_syllabus() -> list:
    """Generate a personal syllabus for the next 7-14 days based on fingerprints."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            # Get top priority fingerprints
            fingerprints = conn.execute("""
                SELECT * FROM error_fingerprints
                WHERE profile_id = ? AND error_count > 0
                ORDER BY priority_score DESC
                LIMIT 5
            """, (profile_id,)).fetchall()

            week_start = date.today().isoformat()
            syllabus = []

            for i, fp in enumerate(fingerprints):
                # Check if already in current syllabus
                existing = conn.execute("""
                    SELECT * FROM personal_syllabus
                    WHERE profile_id = ? AND fingerprint_id = ? AND status = 'active'
                """, (profile_id, fp["id"])).fetchone()

                if not existing:
                    conn.execute("""
                        INSERT INTO personal_syllabus
                        (profile_id, fingerprint_id, week_start, priority_rank, target_practice_count)
                        VALUES (?, ?, ?, ?, ?)
                    """, (profile_id, fp["id"], week_start, i + 1, 5 + (5 - i)))

                syllabus.append({
                    "fingerprint": dict(fp),
                    "rank": i + 1,
                    "target": 5 + (5 - i)
                })

            conn.commit()
            return syllabus
    except Exception:
        return []


def get_active_syllabus() -> list:
    """Get the active personal syllabus items."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT ps.*, ef.category, ef.subcategory, ef.error_count,
                       ef.correct_count, ef.confidence
                FROM personal_syllabus ps
                JOIN error_fingerprints ef ON ps.fingerprint_id = ef.id
                WHERE ps.profile_id = ? AND ps.status = 'active'
                ORDER BY ps.priority_rank ASC
            """, (profile_id,)).fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


def record_syllabus_practice(fingerprint_id: int) -> None:
    """Record a practice attempt for a syllabus item."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE personal_syllabus SET
                    actual_practice_count = actual_practice_count + 1
                WHERE profile_id = ? AND fingerprint_id = ? AND status = 'active'
            """, (profile_id, fingerprint_id))
            conn.commit()
    except Exception as e:
        logger.warning(f"Syllabus practice recording failed: {e}")


# ============== Pragmatics Operations ==============

def record_pragmatics_usage(pattern_type: str, pattern_name: str,
                            dialect: str = "neutral", is_production: bool = False) -> None:
    """Record exposure or production of a pragmatic pattern."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            if is_production:
                conn.execute("""
                    INSERT INTO pragmatics_exposure
                    (profile_id, pattern_type, pattern_name, dialect, production_count, last_used)
                    VALUES (?, ?, ?, ?, 1, ?)
                    ON CONFLICT(profile_id, pattern_type, pattern_name, dialect) DO UPDATE SET
                        production_count = production_count + 1,
                        last_used = excluded.last_used
                """, (profile_id, pattern_type, pattern_name, dialect, datetime.now().isoformat()))
            else:
                conn.execute("""
                    INSERT INTO pragmatics_exposure
                    (profile_id, pattern_type, pattern_name, dialect, exposure_count, last_used)
                    VALUES (?, ?, ?, ?, 1, ?)
                    ON CONFLICT(profile_id, pattern_type, pattern_name, dialect) DO UPDATE SET
                        exposure_count = exposure_count + 1,
                        last_used = excluded.last_used
                """, (profile_id, pattern_type, pattern_name, dialect, datetime.now().isoformat()))
            conn.commit()
    except Exception as e:
        logger.warning(f"Pragmatics recording failed: {e}")


def get_pragmatics_stats() -> dict:
    """Get pragmatics usage statistics."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT pattern_type,
                       SUM(exposure_count) as total_exposure,
                       SUM(production_count) as total_production
                FROM pragmatics_exposure
                WHERE profile_id = ?
                GROUP BY pattern_type
            """, (profile_id,)).fetchall()
            return {row["pattern_type"]: dict(row) for row in rows}
    except Exception:
        return {}


# ============== Conversation Outcome Operations ==============

def record_conversation_outcome(conversation_id: int, outcome_type: str,
                                achieved: bool, details: str = "") -> None:
    """Record an outcome from a conversation (confirmation, clarification, etc.)."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO conversation_outcomes
                (profile_id, conversation_id, outcome_type, achieved, details)
                VALUES (?, ?, ?, ?, ?)
            """, (profile_id, conversation_id, outcome_type, 1 if achieved else 0, details))
            conn.commit()
    except Exception as e:
        logger.warning(f"Conversation outcome recording failed: {e}")


def get_conversation_outcome_stats() -> dict:
    """Get statistics on conversation outcomes."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT outcome_type,
                       COUNT(*) as total_attempts,
                       SUM(achieved) as successful
                FROM conversation_outcomes
                WHERE profile_id = ?
                GROUP BY outcome_type
            """, (profile_id,)).fetchall()
            return {row["outcome_type"]: {
                "total": row["total_attempts"],
                "successful": row["successful"],
                "rate": row["successful"] / row["total_attempts"] if row["total_attempts"] > 0 else 0
            } for row in rows}
    except Exception:
        return {}


# ============== Issue Report Operations ==============

def save_issue_report(report_type: str, context: str, user_answer: str = "",
                      expected_answer: str = "", user_comment: str = "") -> bool:
    """Save an issue report from user feedback.

    Args:
        report_type: Type of issue (wrong_answer, unfair_marking, content_error, etc.)
        context: The question or card content
        user_answer: What the user answered (if applicable)
        expected_answer: What the system expected (if applicable)
        user_comment: User's explanation of the issue

    Returns:
        True if saved successfully, False otherwise
    """
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO issue_reports
                (profile_id, report_type, context, user_answer, expected_answer, user_comment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (profile_id, report_type, context, user_answer, expected_answer, user_comment))
            conn.commit()
            return True
    except Exception as e:
        logger.warning(f"Issue report save failed: {e}")
        return False


def get_issue_reports(status: str = None) -> list:
    """Get issue reports, optionally filtered by status."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            if status:
                rows = conn.execute("""
                    SELECT * FROM issue_reports
                    WHERE profile_id = ? AND status = ?
                    ORDER BY created_at DESC
                """, (profile_id, status)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM issue_reports
                    WHERE profile_id = ?
                    ORDER BY created_at DESC
                """, (profile_id,)).fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []


# ============== Analytics Operations ==============

def get_sessions_this_week() -> int:
    """Count unique days with activity in the last 7 days for the active profile.

    Returns:
        Number of unique days with recorded activity (0-7).
    """
    profile_id = get_active_profile_id()
    try:
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        with get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(DISTINCT DATE(created_at)) as active_days
                FROM activity_log
                WHERE profile_id = ? AND DATE(created_at) >= ?
            """, (profile_id, week_ago)).fetchone()
            return row["active_days"] if row and row["active_days"] else 0
    except Exception as e:
        logger.warning(f"Failed to get sessions this week: {e}")
        return 0


def get_weak_areas() -> list:
    """Analyze mistakes and errors to identify the top 3 weakness areas.

    Returns:
        List of up to 3 human-readable weakness area strings
        (e.g., ["Subjunctive mood", "Ser vs Estar", "Gender agreement"]).
    """
    profile_id = get_active_profile_id()

    # Mapping of error types to human-readable names
    error_type_labels = {
        "verb_tense": "Verb tenses",
        "preterito_imperfecto": "Preterite vs Imperfect",
        "subjunctive": "Subjunctive mood",
        "subjunctive_triggers": "Subjunctive triggers",
        "conditional": "Conditional mood",
        "ser_estar": "Ser vs Estar",
        "preposition": "Prepositions",
        "prepositions": "Prepositions",
        "por_para": "Por vs Para",
        "pronoun": "Pronouns",
        "pronouns": "Pronouns",
        "clitic": "Clitic placement",
        "agreement": "Agreement",
        "gender": "Gender agreement",
        "gender_noun": "Gender agreement",
        "gender_adjective": "Adjective agreement",
        "number": "Number agreement",
        "vocabulary": "Vocabulary",
        "false_friends": "False cognates",
        "word_order": "Word order",
        "spelling": "Spelling",
        "accent": "Accent marks",
        "punctuation": "Punctuation",
        "article": "Articles",
        "conjugation": "Verb conjugation",
    }

    try:
        with get_connection() as conn:
            # First try error_fingerprints table for detailed tracking
            rows = conn.execute("""
                SELECT category, subcategory, error_count
                FROM error_fingerprints
                WHERE profile_id = ? AND error_count > 0
                ORDER BY error_count DESC, priority_score DESC
                LIMIT 3
            """, (profile_id,)).fetchall()

            if rows:
                result = []
                for row in rows:
                    # Use subcategory label if available, otherwise category
                    label = error_type_labels.get(
                        row["subcategory"],
                        error_type_labels.get(row["category"], row["category"].replace("_", " ").title())
                    )
                    result.append(label)
                return result

            # Fallback to mistakes table
            rows = conn.execute("""
                SELECT error_type, COUNT(*) as count
                FROM mistakes
                WHERE profile_id = ?
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 3
            """, (profile_id,)).fetchall()

            result = []
            for row in rows:
                error_type = row["error_type"] or "unknown"
                label = error_type_labels.get(
                    error_type.lower(),
                    error_type.replace("_", " ").title()
                )
                result.append(label)
            return result
    except Exception as e:
        logger.warning(f"Failed to get weak areas: {e}")
        return []


def get_learning_velocity() -> float:
    """Calculate vocabulary items mastered per week for the active profile.

    Returns:
        Average number of vocab items mastered per week (float).
        Returns 0.0 if no data available.
    """
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            # Get mastered items with their mastery dates
            rows = conn.execute("""
                SELECT last_reviewed
                FROM vocab_items
                WHERE profile_id = ? AND status = 'mastered' AND last_reviewed IS NOT NULL
            """, (profile_id,)).fetchall()

            if not rows:
                return 0.0

            # Find date range
            dates = [row["last_reviewed"][:10] for row in rows if row["last_reviewed"]]
            if not dates:
                return 0.0

            dates.sort()
            first_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
            last_date = date.today()

            # Calculate weeks elapsed (minimum 1 to avoid division by zero)
            days_elapsed = (last_date - first_date).days
            weeks_elapsed = max(1, days_elapsed / 7)

            # Items per week
            return round(len(rows) / weeks_elapsed, 1)
    except Exception as e:
        logger.warning(f"Failed to calculate learning velocity: {e}")
        return 0.0


def get_review_performance() -> float:
    """Get average quality score from recent reviews for the active profile.

    Analyzes activity_log entries with scores and vocab/mistake reviews.

    Returns:
        Average quality score as a percentage (0-100).
        Returns 0.0 if no review data available.
    """
    profile_id = get_active_profile_id()
    try:
        thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
        with get_connection() as conn:
            # Get average score from activity_log for review-type activities
            row = conn.execute("""
                SELECT AVG(score) as avg_score, COUNT(*) as count
                FROM activity_log
                WHERE profile_id = ?
                    AND score IS NOT NULL
                    AND DATE(created_at) >= ?
                    AND activity_type IN ('vocab_review', 'mistake_review', 'grammar_review', 'review', 'flashcard')
            """, (profile_id, thirty_days_ago)).fetchone()

            if row and row["avg_score"] is not None and row["count"] > 0:
                # Assuming scores are 0-5 scale (SM-2), convert to percentage
                avg = row["avg_score"]
                if avg <= 5:
                    return round((avg / 5) * 100, 1)
                return round(min(avg, 100), 1)

            # Fallback: calculate from vocab items ease_factor
            # Higher ease_factor = better performance
            row = conn.execute("""
                SELECT AVG(ease_factor) as avg_ease, COUNT(*) as count
                FROM vocab_items
                WHERE profile_id = ?
                    AND status IN ('learning', 'mastered')
                    AND exposure_count > 0
            """, (profile_id,)).fetchone()

            if row and row["avg_ease"] is not None and row["count"] > 0:
                # Ease factor ranges from 1.3 to ~3.0, normalize to percentage
                # 1.3 = poor (0%), 2.5 = good (75%), 3.0+ = excellent (100%)
                ease = row["avg_ease"]
                normalized = min(100, max(0, (ease - 1.3) / (3.0 - 1.3) * 100))
                return round(normalized, 1)

            return 0.0
    except Exception as e:
        logger.warning(f"Failed to get review performance: {e}")
        return 0.0


def get_daily_activity_summary() -> dict:
    """Get today's activity statistics for the active profile.

    Returns:
        Dict with keys:
        - items_reviewed: int (vocab + grammar items reviewed today)
        - errors_fixed: int (mistakes addressed today)
        - time_spent: int (total seconds spent on activities today)
    """
    profile_id = get_active_profile_id()
    default_result = {"items_reviewed": 0, "errors_fixed": 0, "time_spent": 0}

    try:
        today = date.today().isoformat()
        with get_connection() as conn:
            # Get from progress_metrics for today
            metrics_row = conn.execute("""
                SELECT vocab_reviewed, grammar_reviewed, errors_fixed
                FROM progress_metrics
                WHERE profile_id = ? AND metric_date = ?
            """, (profile_id, today)).fetchone()

            items_reviewed = 0
            errors_fixed = 0

            if metrics_row:
                items_reviewed = (metrics_row["vocab_reviewed"] or 0) + (metrics_row["grammar_reviewed"] or 0)
                errors_fixed = metrics_row["errors_fixed"] or 0

            # Get time spent from activity_log
            time_row = conn.execute("""
                SELECT COALESCE(SUM(duration_seconds), 0) as total_time
                FROM activity_log
                WHERE profile_id = ? AND DATE(created_at) = ?
            """, (profile_id, today)).fetchone()

            time_spent = time_row["total_time"] if time_row else 0

            # If no metrics, try counting from activity_log
            if items_reviewed == 0:
                count_row = conn.execute("""
                    SELECT COUNT(*) as count
                    FROM activity_log
                    WHERE profile_id = ?
                        AND DATE(created_at) = ?
                        AND activity_type IN ('vocab_review', 'grammar_review', 'review', 'flashcard')
                """, (profile_id, today)).fetchone()
                if count_row:
                    items_reviewed = count_row["count"] or 0

            return {
                "items_reviewed": items_reviewed,
                "errors_fixed": errors_fixed,
                "time_spent": time_spent
            }
    except Exception as e:
        logger.warning(f"Failed to get daily activity summary: {e}")
        return default_result
