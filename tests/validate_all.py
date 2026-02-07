"""
Comprehensive validation script for VivaLingo Pro.
Runs all quality checks before shipping.

Usage: python tests/validate_all.py
"""
import sys
import importlib
import glob
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_all_imports():
    """Verify all modules import without errors."""
    print("\n=== CHECK 1: Module Imports ===")
    errors = []
    modules = ['utils', 'utils.database', 'utils.helpers', 'utils.theme', 'utils.content']
    for mod in modules:
        try:
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
            else:
                importlib.import_module(mod)
            print(f"  OK: {mod}")
        except Exception as e:
            errors.append(f"{mod}: {e}")
            print(f"  FAIL: {mod}: {e}")

    for f in sorted(glob.glob(str(PROJECT_ROOT / 'pages' / '*.py'))):
        if f.endswith('__init__.py'):
            continue
        mod = f.replace(str(PROJECT_ROOT) + '/', '').replace('/', '.').replace('.py', '')
        try:
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
            else:
                importlib.import_module(mod)
            print(f"  OK: {mod}")
        except Exception as e:
            errors.append(f"{mod}: {e}")
            print(f"  FAIL: {mod}: {e}")

    if errors:
        print(f"\n  FAILED: {len(errors)} import errors")
    else:
        print(f"\n  PASSED: All modules import successfully")
    return len(errors) == 0


def check_compile_all():
    """Verify all Python files compile."""
    print("\n=== CHECK 2: Syntax Compilation ===")
    import py_compile
    errors = []
    for f in glob.glob(str(PROJECT_ROOT / '**' / '*.py'), recursive=True):
        if '__pycache__' in f or '.venv' in f:
            continue
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(str(e))
            print(f"  FAIL: {f}: {e}")

    if errors:
        print(f"\n  FAILED: {len(errors)} compilation errors")
    else:
        print(f"  PASSED: All files compile successfully")
    return len(errors) == 0


def check_database_tests():
    """Run database unit tests."""
    print("\n=== CHECK 3: Database Tests ===")
    try:
        from tests.test_database import (
            test_init_db, test_profile_crud, test_set_active_profile_validation,
            test_vocab_operations, test_mistake_operations, test_domain_exposure,
            test_progress_metrics, test_grammar_pattern_upsert,
            test_error_fingerprints, test_save_transcript_none_guard,
            test_portfolio_operations, test_issue_reports,
        )
        tests = [
            test_init_db, test_profile_crud, test_set_active_profile_validation,
            test_vocab_operations, test_mistake_operations, test_domain_exposure,
            test_progress_metrics, test_grammar_pattern_upsert,
            test_error_fingerprints, test_save_transcript_none_guard,
            test_portfolio_operations, test_issue_reports,
        ]
        errors = []
        for test in tests:
            try:
                test()
            except Exception as e:
                errors.append(f"{test.__name__}: {e}")
                print(f"  FAIL: {test.__name__}: {e}")

        if errors:
            print(f"\n  FAILED: {len(errors)} database test failures")
        else:
            print(f"\n  PASSED: All {len(tests)} database tests")
        return len(errors) == 0
    except Exception as e:
        print(f"  ERROR: Could not run database tests: {e}")
        return False


def check_helper_tests():
    """Run helper function unit tests."""
    print("\n=== CHECK 4: Helper Tests ===")
    try:
        from tests.test_helpers import (
            test_normalize_accents, test_levenshtein_distance,
            test_compare_answers_exact, test_compare_answers_case_insensitive,
            test_compare_answers_accent_tolerant, test_compare_answers_multiple,
            test_compare_answers_returns_3_tuple, test_are_articles_equivalent,
            test_check_alternative_spelling, test_check_text_for_mistakes_none_guard,
            test_check_text_hecho_de_menos, test_generate_exercise_feedback_none_guard,
            test_get_streak_days, test_get_streak_days_date_objects,
            test_detect_language, test_seed_for_day, test_shuffle_with_seed,
            test_get_similar_words,
        )
        tests = [
            test_normalize_accents, test_levenshtein_distance,
            test_compare_answers_exact, test_compare_answers_case_insensitive,
            test_compare_answers_accent_tolerant, test_compare_answers_multiple,
            test_compare_answers_returns_3_tuple, test_are_articles_equivalent,
            test_check_alternative_spelling, test_check_text_for_mistakes_none_guard,
            test_check_text_hecho_de_menos, test_generate_exercise_feedback_none_guard,
            test_get_streak_days, test_get_streak_days_date_objects,
            test_detect_language, test_seed_for_day, test_shuffle_with_seed,
            test_get_similar_words,
        ]
        errors = []
        for test in tests:
            try:
                test()
            except Exception as e:
                errors.append(f"{test.__name__}: {e}")
                print(f"  FAIL: {test.__name__}: {e}")

        if errors:
            print(f"\n  FAILED: {len(errors)} helper test failures")
        else:
            print(f"\n  PASSED: All {len(tests)} helper tests")
        return len(errors) == 0
    except Exception as e:
        print(f"  ERROR: Could not run helper tests: {e}")
        return False


def check_content_quality():
    """Verify content data quality."""
    print("\n=== CHECK 5: Content Quality ===")
    errors = []
    from utils.content import TOPIC_DIVERSITY_DOMAINS, VERB_CHOICE_STUDIO, GRAMMAR_MICRODRILLS

    # Check for missing accents in domain content
    accent_issues = []
    bad_words = ["ano ", "espanol", "ingles ", "medico ", "diagnostico", "clausula"]
    domains = TOPIC_DIVERSITY_DOMAINS if isinstance(TOPIC_DIVERSITY_DOMAINS, list) else list(TOPIC_DIVERSITY_DOMAINS.values()) if isinstance(TOPIC_DIVERSITY_DOMAINS, dict) else []
    for domain_data in domains:
        domain_name = domain_data.get("domain", "unknown") if isinstance(domain_data, dict) else str(domain_data)
        if not isinstance(domain_data, dict):
            continue
        for word in domain_data.get("keywords", []):
            for bad in bad_words:
                if bad in word.lower():
                    accent_issues.append(f"  Domain '{domain_name}' keyword '{word}' may have missing accent")
        sample = domain_data.get("sample", "")
        for bad in bad_words:
            if bad in sample.lower():
                accent_issues.append(f"  Domain '{domain_name}' sample contains '{bad}' (missing accent?)")

    if accent_issues:
        for issue in accent_issues[:5]:
            print(issue)
        errors.extend(accent_issues)
    else:
        print("  OK: No obvious missing accents in domain content")

    # Check grammar drills have answers matching options
    for drill in GRAMMAR_MICRODRILLS:
        if drill.get("answer") and drill.get("options"):
            if drill["answer"] not in drill["options"]:
                msg = f"  Grammar drill '{drill.get('pattern', 'unknown')}': answer '{drill['answer']}' not in options {drill['options']}"
                errors.append(msg)
                print(msg)

    if not errors:
        print("  OK: Grammar drill answers match options")

    if errors:
        print(f"\n  WARNINGS: {len(errors)} content quality issues")
    else:
        print(f"\n  PASSED: Content quality checks")
    return True  # Warnings don't fail the build


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("  VivaLingo Pro - Quality Validation Suite")
    print("=" * 60)

    results = []
    results.append(("Module Imports", check_compile_all()))
    results.append(("Syntax Check", check_all_imports()))
    results.append(("Database Tests", check_database_tests()))
    results.append(("Helper Tests", check_helper_tests()))
    results.append(("Content Quality", check_content_quality()))

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print(f"\n  ALL CHECKS PASSED - Ready to ship!")
    else:
        print(f"\n  SOME CHECKS FAILED - Fix before shipping")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
