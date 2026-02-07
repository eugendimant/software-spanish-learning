"""Tests for database module."""
import os
import sys
import sqlite3
import tempfile
from pathlib import Path
from datetime import date, timedelta

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import utils.database as db


def setup_test_db():
    """Create a temporary database for testing."""
    tmpdir = tempfile.mkdtemp()
    db.DATA_DIR = Path(tmpdir)
    db.DB_PATH = db.DATA_DIR / "test_vivalingo.db"
    db.PORTFOLIO_PATH = db.DATA_DIR / "test_portfolio.json"
    db.init_db()
    db.init_fingerprint_tables()
    return tmpdir


def test_init_db():
    """Test that init_db creates all required tables."""
    setup_test_db()
    conn = db.get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row["name"] for row in cursor.fetchall()}
    conn.close()

    required = {
        "profiles", "vocab_items", "mistakes", "domain_exposure",
        "grammar_patterns", "daily_missions", "transcripts",
        "conversations", "progress_metrics", "activity_log",
        "issue_reports", "user_profile"
    }
    for t in required:
        assert t in tables, f"Missing table: {t}"
    print("  PASS: test_init_db")


def test_profile_crud():
    """Test profile creation, reading, updating, and deletion."""
    setup_test_db()

    # Create
    pid = db.create_profile("Test User", level="C1", dialect_preference="Spain")
    assert pid is not None, "create_profile returned None"

    # Read
    profile = db.get_profile(pid)
    assert profile is not None
    assert profile["name"] == "Test User"
    assert profile["level"] == "C1"

    # Update
    db.update_profile(pid, {"name": "Updated User", "level": "C2"})
    profile = db.get_profile(pid)
    assert profile["name"] == "Updated User"

    # List
    profiles = db.get_all_profiles()
    assert len(profiles) >= 1

    # Delete
    db.delete_profile(pid)
    profile = db.get_profile(pid)
    assert profile is None
    print("  PASS: test_profile_crud")


def test_set_active_profile_validation():
    """Test that set_active_profile_id rejects invalid values."""
    setup_test_db()
    db.set_active_profile_id(5)
    assert db.get_active_profile_id() == 5

    # None should not change it
    db.set_active_profile_id(None)
    assert db.get_active_profile_id() == 5

    # Negative should not change it
    db.set_active_profile_id(-1)
    assert db.get_active_profile_id() == 5

    # Zero should not change it
    db.set_active_profile_id(0)
    assert db.get_active_profile_id() == 5

    # Valid should change it
    db.set_active_profile_id(1)
    assert db.get_active_profile_id() == 1
    print("  PASS: test_set_active_profile_validation")


def test_vocab_operations():
    """Test vocabulary save, retrieve, and review."""
    setup_test_db()
    pid = db.create_profile("Vocab Tester")
    db.set_active_profile_id(pid)

    # Save vocab
    db.save_vocab_item({
        "term": "hola",
        "meaning": "hello",
        "example": "Hola, como estas?",
        "domain": "Everyday slang-light",
    })

    # Get vocab
    items = db.get_vocab_items()
    assert len(items) >= 1
    assert items[0]["term"] == "hola"

    # Get for review
    review_items = db.get_vocab_for_review()
    assert len(review_items) >= 1

    # Update review
    db.update_vocab_review("hola", 4)
    items = db.get_vocab_items()
    assert items[0]["exposure_count"] >= 1

    # Upsert - should update, not duplicate
    db.save_vocab_item({
        "term": "hola",
        "meaning": "hello / hi",
        "domain": "Everyday slang-light",
    })
    items = db.get_vocab_items()
    hola_items = [i for i in items if i["term"] == "hola"]
    assert len(hola_items) == 1, "Upsert created duplicate"
    assert hola_items[0]["meaning"] == "hello / hi"
    print("  PASS: test_vocab_operations")


def test_mistake_operations():
    """Test mistake tracking and review."""
    setup_test_db()
    pid = db.create_profile("Mistake Tester")
    db.set_active_profile_id(pid)

    # Save mistake
    mid = db.save_mistake({
        "user_text": "Yo soy cansado",
        "corrected_text": "Yo estoy cansado",
        "error_type": "ser_estar",
        "explanation": "Use estar for temporary states",
    })
    assert mid is not None

    # Get for review
    mistakes = db.get_mistakes_for_review()
    assert len(mistakes) >= 1

    # Get stats
    stats = db.get_mistake_stats()
    assert "ser_estar" in stats
    assert stats["ser_estar"]["count"] == 1

    # Update review with quality clamping
    db.update_mistake_review(mid, 4)
    db.update_mistake_review(mid, 100)  # Should be clamped to 5
    print("  PASS: test_mistake_operations")


def test_domain_exposure():
    """Test domain exposure tracking."""
    setup_test_db()
    pid = db.create_profile("Domain Tester")
    db.set_active_profile_id(pid)
    db.init_profile_domains(pid)

    # Record exposure
    db.record_domain_exposure("Healthcare", 3)
    exposure = db.get_domain_exposure()
    assert "Healthcare" in exposure
    assert exposure["Healthcare"]["exposure_count"] >= 3

    # Record again - should increment
    db.record_domain_exposure("Healthcare", 2)
    exposure = db.get_domain_exposure()
    assert exposure["Healthcare"]["exposure_count"] >= 4

    # Underexposed
    underexposed = db.get_underexposed_domains(limit=3)
    assert len(underexposed) <= 3
    print("  PASS: test_domain_exposure")


def test_progress_metrics():
    """Test progress recording and retrieval."""
    setup_test_db()
    pid = db.create_profile("Progress Tester")
    db.set_active_profile_id(pid)

    # Record progress
    db.record_progress({"vocab_reviewed": 5, "grammar_reviewed": 3})
    db.record_progress({"vocab_reviewed": 2})  # Should increment

    # Get history
    history = db.get_progress_history(days=7)
    assert len(history) >= 1
    assert history[0]["vocab_reviewed"] == 7  # 5 + 2

    # Get total stats
    stats = db.get_total_stats()
    assert stats["total_vocab"] == 7
    print("  PASS: test_progress_metrics")


def test_grammar_pattern_upsert():
    """Test that grammar patterns use upsert correctly."""
    setup_test_db()
    pid = db.create_profile("Grammar Tester")
    db.set_active_profile_id(pid)

    db.save_grammar_pattern({
        "name": "subjunctive_triggers",
        "category": "mood",
        "description": "When to use subjunctive",
        "examples": ["Espero que vengas"],
    })

    # Save again - should update, not duplicate
    db.save_grammar_pattern({
        "name": "subjunctive_triggers",
        "category": "mood",
        "description": "Updated description",
        "examples": ["Espero que vengas", "Quiero que estudies"],
    })

    patterns = db.get_grammar_for_review()
    subj_patterns = [p for p in patterns if p["pattern_name"] == "subjunctive_triggers"]
    assert len(subj_patterns) == 1, "Grammar upsert created duplicate"
    assert subj_patterns[0]["description"] == "Updated description"
    print("  PASS: test_grammar_pattern_upsert")


def test_error_fingerprints():
    """Test error fingerprint recording and analysis."""
    setup_test_db()
    pid = db.create_profile("Fingerprint Tester")
    db.set_active_profile_id(pid)

    # Record errors
    db.record_error_fingerprint("ser_estar", "permanent_temporary", is_error=True,
                                 user_input="soy cansado", expected="estoy cansado")
    db.record_error_fingerprint("ser_estar", "permanent_temporary", is_error=True)
    db.record_error_fingerprint("ser_estar", "permanent_temporary", is_error=False)

    # Get fingerprints
    fps = db.get_error_fingerprints()
    assert len(fps) >= 1
    fp = fps[0]
    assert fp["error_count"] == 2
    assert fp["correct_count"] == 1

    # Get summary
    summary = db.get_fingerprint_summary()
    assert "ser_estar" in summary
    print("  PASS: test_error_fingerprints")


def test_save_transcript_none_guard():
    """Test that save_transcript handles None gracefully."""
    setup_test_db()
    # These should not crash
    db.save_transcript(None)
    db.save_transcript("")
    db.save_transcript("   ")
    db.save_transcript("Valid transcript", duration=60)
    print("  PASS: test_save_transcript_none_guard")


def test_portfolio_operations():
    """Test portfolio save/load."""
    setup_test_db()
    portfolio = {"writing_samples": [{"text": "Hola mundo"}], "recordings": []}
    db.save_portfolio(portfolio)
    loaded = db.load_portfolio()
    assert loaded["writing_samples"][0]["text"] == "Hola mundo"
    print("  PASS: test_portfolio_operations")


def test_issue_reports():
    """Test issue report CRUD."""
    setup_test_db()
    pid = db.create_profile("Report Tester")
    db.set_active_profile_id(pid)

    result = db.save_issue_report("wrong_answer", "Test context", "mi answer", "correct answer", "This is wrong")
    assert result is True

    reports = db.get_issue_reports()
    assert len(reports) >= 1
    assert reports[0]["report_type"] == "wrong_answer"
    print("  PASS: test_issue_reports")


if __name__ == "__main__":
    print("Running database tests...")
    test_init_db()
    test_profile_crud()
    test_set_active_profile_validation()
    test_vocab_operations()
    test_mistake_operations()
    test_domain_exposure()
    test_progress_metrics()
    test_grammar_pattern_upsert()
    test_error_fingerprints()
    test_save_transcript_none_guard()
    test_portfolio_operations()
    test_issue_reports()
    print("\nAll database tests passed!")
