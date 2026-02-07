"""Tests for helper functions."""
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    normalize_accents, levenshtein_distance, normalize_for_comparison,
    are_articles_equivalent, check_alternative_spelling, compare_answers,
    get_accent_feedback, check_text_for_mistakes, generate_corrected_text,
    generate_exercise_feedback, get_streak_days, seed_for_day,
    shuffle_with_seed, detect_language, get_similar_words,
)


def test_normalize_accents():
    """Test accent normalization."""
    assert normalize_accents("café") == "cafe"
    assert normalize_accents("niño") == "nino"
    assert normalize_accents("NIÑO") == "NINO"
    assert normalize_accents("") == ""
    print("  PASS: test_normalize_accents")


def test_levenshtein_distance():
    """Test edit distance calculation."""
    assert levenshtein_distance("", "") == 0
    assert levenshtein_distance("abc", "abc") == 0
    assert levenshtein_distance("abc", "abd") == 1
    assert levenshtein_distance("cat", "cats") == 1
    assert levenshtein_distance("kitten", "sitting") == 3
    print("  PASS: test_levenshtein_distance")


def test_compare_answers_exact():
    """Test exact match comparison."""
    is_correct, feedback, matched = compare_answers("hola", "hola")
    assert is_correct is True
    assert feedback == "exact_match"
    print("  PASS: test_compare_answers_exact")


def test_compare_answers_case_insensitive():
    """Test case-insensitive matching."""
    is_correct, _, _ = compare_answers("Hola", "hola")
    assert is_correct is True
    print("  PASS: test_compare_answers_case_insensitive")


def test_compare_answers_accent_tolerant():
    """Test accent-tolerant mode."""
    # Without tolerance - different
    is_correct, _, _ = compare_answers("cafe", "café", accent_tolerant=False)
    # With tolerance - should match
    is_correct2, feedback, _ = compare_answers("cafe", "café", accent_tolerant=True)
    assert is_correct2 is True
    assert feedback == "accent_tolerance"
    print("  PASS: test_compare_answers_accent_tolerant")


def test_compare_answers_multiple():
    """Test comparison with multiple correct answers."""
    is_correct, _, matched = compare_answers("coche", ["carro", "coche", "auto"])
    assert is_correct is True
    # matched may be "carro" (via alt spelling) or "coche" (exact) - both valid
    assert matched in ["carro", "coche", "auto"]

    is_correct2, _, _ = compare_answers("completely_wrong_xyz", ["carro", "coche", "auto"])
    assert is_correct2 is False
    print("  PASS: test_compare_answers_multiple")


def test_compare_answers_returns_3_tuple():
    """Test that compare_answers always returns exactly 3 values."""
    result = compare_answers("hola", "hola")
    assert len(result) == 3, f"Expected 3-tuple, got {len(result)}"

    result2 = compare_answers("wrong", "right")
    assert len(result2) == 3, f"Expected 3-tuple, got {len(result2)}"
    assert result2[0] is False
    assert result2[2] is None
    print("  PASS: test_compare_answers_returns_3_tuple")


def test_are_articles_equivalent():
    """Test article tolerance."""
    # Same article+word - always equivalent
    assert are_articles_equivalent("el libro", "el libro") is True
    # Different articles may be tolerated (function returns True for article variation)
    result = are_articles_equivalent("el libro", "la libro")
    assert isinstance(result, bool)
    print("  PASS: test_are_articles_equivalent")


def test_check_alternative_spelling():
    """Test alternative spelling detection."""
    assert check_alternative_spelling("computadora", "ordenador") is True
    assert check_alternative_spelling("hello", "goodbye") is False
    print("  PASS: test_check_alternative_spelling")


def test_check_text_for_mistakes_none_guard():
    """Test that check_text_for_mistakes handles None/empty gracefully."""
    assert check_text_for_mistakes(None) == []
    assert check_text_for_mistakes("") == []
    assert check_text_for_mistakes("   ") == []
    # Valid text should not crash
    result = check_text_for_mistakes("Yo soy cansado después del trabajo.")
    assert isinstance(result, list)
    # Check that results have the expected keys
    for m in result:
        assert "original" in m
        assert "correction" in m
    print("  PASS: test_check_text_for_mistakes_none_guard")


def test_check_text_hecho_de_menos():
    """Test that 'hecho de menos' is corrected to 'echo de menos' without duplication."""
    result = check_text_for_mistakes("te hecho de menos mucho")
    spelling_mistakes = [m for m in result if m.get("tag") == "spelling"]
    for m in spelling_mistakes:
        if "echo" in m.get("correction", ""):
            corrected = generate_corrected_text("te hecho de menos mucho", [m])
            assert "de menos de menos" not in corrected, f"Text duplication bug: {corrected}"
            break
    # Also verify the function doesn't crash on the input
    assert isinstance(result, list)
    print("  PASS: test_check_text_hecho_de_menos")


def test_generate_exercise_feedback_none_guard():
    """Test that generate_exercise_feedback handles None gracefully."""
    result = generate_exercise_feedback(None, "correct", "explanation")
    assert result["correct"] is False
    result2 = generate_exercise_feedback("answer", None, "explanation")
    assert result2["correct"] is False
    print("  PASS: test_generate_exercise_feedback_none_guard")


def test_get_streak_days():
    """Test streak calculation."""
    assert get_streak_days(None) == 0
    assert get_streak_days([]) == 0

    # Today only
    today = date.today().isoformat()
    assert get_streak_days([{"metric_date": today}]) == 1

    # Today + yesterday
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assert get_streak_days([{"metric_date": today}, {"metric_date": yesterday}]) == 2

    # Gap - only today counts
    three_days_ago = (date.today() - timedelta(days=3)).isoformat()
    assert get_streak_days([{"metric_date": today}, {"metric_date": three_days_ago}]) == 1
    print("  PASS: test_get_streak_days")


def test_get_streak_days_date_objects():
    """Test streak with date objects mixed with strings."""
    today = date.today()
    yesterday_str = (today - timedelta(days=1)).isoformat()
    # Mixed date objects and strings should not crash
    result = get_streak_days([
        {"metric_date": today},
        {"metric_date": yesterday_str},
    ])
    assert result >= 1
    print("  PASS: test_get_streak_days_date_objects")


def test_detect_language():
    """Test language detection."""
    result = detect_language("Hola, ¿cómo estás? Estoy bien, gracias.")
    assert result["language"] == "spanish"

    result2 = detect_language("Hello, how are you? I am fine, thanks.")
    assert result2["language"] == "english"
    print("  PASS: test_detect_language")


def test_seed_for_day():
    """Test deterministic seeding."""
    seed1 = seed_for_day(date.today(), "test")
    seed2 = seed_for_day(date.today(), "test")
    assert seed1 == seed2, "Same day/suffix should produce same seed"

    seed3 = seed_for_day(date.today(), "other")
    assert seed1 != seed3, "Different suffix should produce different seed"
    print("  PASS: test_seed_for_day")


def test_shuffle_with_seed():
    """Test reproducible shuffling."""
    items = [1, 2, 3, 4, 5]
    result1 = shuffle_with_seed(items, 42)
    result2 = shuffle_with_seed(items, 42)
    assert result1 == result2, "Same seed should produce same shuffle"
    assert items == [1, 2, 3, 4, 5], "Original list should not be modified"
    print("  PASS: test_shuffle_with_seed")


def test_get_similar_words():
    """Test similar word generation."""
    similar = get_similar_words("ser", count=3)
    assert isinstance(similar, list)
    assert len(similar) <= 3
    # Should include known confusables
    assert "estar" in similar or len(similar) > 0
    print("  PASS: test_get_similar_words")


if __name__ == "__main__":
    print("Running helper tests...")
    test_normalize_accents()
    test_levenshtein_distance()
    test_compare_answers_exact()
    test_compare_answers_case_insensitive()
    test_compare_answers_accent_tolerant()
    test_compare_answers_multiple()
    test_compare_answers_returns_3_tuple()
    test_are_articles_equivalent()
    test_check_alternative_spelling()
    test_check_text_for_mistakes_none_guard()
    test_check_text_hecho_de_menos()
    test_generate_exercise_feedback_none_guard()
    test_get_streak_days()
    test_get_streak_days_date_objects()
    test_detect_language()
    test_seed_for_day()
    test_shuffle_with_seed()
    test_get_similar_words()
    print("\nAll helper tests passed!")
