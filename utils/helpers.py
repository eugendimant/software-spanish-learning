"""Helper functions for VivaLingo Pro."""
import difflib
import hashlib
import random
import re
from datetime import date, timedelta
from typing import Optional

from utils.content import COMMON_MISTAKES, REGISTER_MARKERS


def seed_for_week(week_date: date, name: str) -> int:
    """Generate a deterministic seed for weekly content."""
    base = f"{week_date.isocalendar()[1]}:{week_date.year}:{name}"
    return int(hashlib.sha256(base.encode("utf-8")).hexdigest()[:8], 16)


def seed_for_day(day_date: date, name: str) -> int:
    """Generate a deterministic seed for daily content."""
    base = f"{day_date.isoformat()}:{name}"
    return int(hashlib.sha256(base.encode("utf-8")).hexdigest()[:8], 16)


def pick_domain_pair(exposures: dict, stretch_percent: float = 0.3) -> tuple[str, str]:
    """
    Pick familiar (70%) and stretch (30%) domains based on exposure.
    Returns (familiar_domain, stretch_domain).
    """
    sorted_domains = sorted(exposures.items(), key=lambda x: x[1].get("exposure_count", 0), reverse=True)

    if len(sorted_domains) < 2:
        domains = list(exposures.keys())
        return (domains[0], domains[0]) if domains else ("Healthcare", "Healthcare")

    # Familiar = most exposed, Stretch = least exposed
    familiar = sorted_domains[0][0]
    stretch = sorted_domains[-1][0]

    return familiar, stretch


def calculate_domain_coverage(exposures: dict) -> dict:
    """Calculate coverage percentage for each domain."""
    total = sum(d.get("exposure_count", 0) for d in exposures.values()) or 1
    return {
        domain: {
            "percent": (data.get("exposure_count", 0) / total) * 100,
            "count": data.get("exposure_count", 0),
            "total_items": data.get("total_items", 0),
        }
        for domain, data in exposures.items()
    }


def check_text_for_mistakes(text: str) -> list[dict]:
    """
    Check text for common mistakes using rule-based patterns.
    Returns list of detected mistakes with corrections.
    """
    mistakes_found = []
    text_lower = text.lower()

    for mistake in COMMON_MISTAKES:
        pattern = mistake["pattern"].lower()
        if pattern in text_lower:
            # Find the position
            pos = text_lower.find(pattern)
            mistakes_found.append({
                "original": text[pos:pos + len(pattern)],
                "correction": mistake["correction"],
                "explanation": mistake["explanation"],
                "examples": mistake["examples"],
                "tag": mistake["tag"],
                "position": pos,
            })

    # Additional rule-based checks

    # Gender agreement check for common words
    gender_patterns = [
        (r"\bla problema\b", "el problema", "gender", "Problema es masculino"),
        (r"\bel tema\b.*\bbuena\b", "buen/bueno", "gender", "Tema es masculino"),
        (r"\bmucho gente\b", "mucha gente", "gender", "Gente es femenino"),
        (r"\bel agua\b.*\bfrio\b", "fria", "gender", "Agua es femenino (usa el por fonética)"),
    ]

    for pattern, correction, tag, explanation in gender_patterns:
        if re.search(pattern, text_lower):
            match = re.search(pattern, text_lower)
            if match:
                mistakes_found.append({
                    "original": match.group(),
                    "correction": correction,
                    "explanation": explanation,
                    "examples": [],
                    "tag": tag,
                    "position": match.start(),
                })

    # Ser/Estar common errors
    ser_estar_patterns = [
        (r"\bes muy cansado\b", "esta muy cansado", "copula", "Estados temporales usan estar"),
        (r"\bsoy de acuerdo\b", "estoy de acuerdo", "copula", "Estar de acuerdo es la expresion correcta"),
        (r"\besta bueno\b(?! que)", "es bueno", "copula", "Cualidades inherentes usan ser"),
    ]

    for pattern, correction, tag, explanation in ser_estar_patterns:
        if re.search(pattern, text_lower):
            match = re.search(pattern, text_lower)
            if match:
                mistakes_found.append({
                    "original": match.group(),
                    "correction": correction,
                    "explanation": explanation,
                    "examples": [],
                    "tag": tag,
                    "position": match.start(),
                })

    return mistakes_found


def generate_corrected_text(original: str, mistakes: list[dict]) -> str:
    """Generate corrected version of text based on detected mistakes."""
    if not mistakes:
        return original

    corrected = original
    # Sort by position descending to replace from end to start
    for mistake in sorted(mistakes, key=lambda x: x.get("position", 0), reverse=True):
        pos = mistake.get("position", -1)
        if pos >= 0:
            orig_len = len(mistake["original"])
            corrected = corrected[:pos] + mistake["correction"] + corrected[pos + orig_len:]

    return corrected


def highlight_diff(original: str, corrected: str) -> str:
    """Generate HTML highlighting differences between original and corrected text."""
    if original == corrected:
        return original

    diff = difflib.unified_diff(
        original.split(),
        corrected.split(),
        lineterm=""
    )

    result_parts = []
    for line in diff:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("-"):
            result_parts.append(f'<span class="diff-removed">{line[1:]}</span>')
        elif line.startswith("+"):
            result_parts.append(f'<span class="diff-added">{line[1:]}</span>')
        else:
            result_parts.append(line[1:] if line.startswith(" ") else line)

    return " ".join(result_parts) if result_parts else corrected


def score_register_response(text: str, target_register: str) -> dict:
    """Score a response for register appropriateness."""
    text_lower = text.lower()
    scores = {
        "politeness": 0,
        "hedging": 0,
        "directness": 0,
        "idiomaticity": 0,
        "audience_fit": 0,
    }

    # Count markers
    for marker in REGISTER_MARKERS["politeness"]:
        if marker in text_lower:
            scores["politeness"] += 1

    for marker in REGISTER_MARKERS["hedging"]:
        if marker in text_lower:
            scores["hedging"] += 1

    for marker in REGISTER_MARKERS["direct"]:
        if marker in text_lower:
            scores["directness"] += 1

    for marker in REGISTER_MARKERS["idiomatic"]:
        if marker in text_lower:
            scores["idiomaticity"] += 1

    # Check audience fit based on target register
    if target_register == "formal":
        scores["audience_fit"] = scores["politeness"] * 2 + scores["hedging"] - scores["directness"]
    elif target_register == "informal":
        for marker in REGISTER_MARKERS["whatsapp"]:
            if marker in text_lower:
                scores["audience_fit"] += 1
    elif target_register == "academic":
        for marker in REGISTER_MARKERS["academic"]:
            if marker in text_lower:
                scores["audience_fit"] += 1

    # Normalize scores to 1-5 scale
    max_score = 5
    for key in scores:
        scores[key] = min(max_score, max(1, scores[key] + 2))

    return scores


def analyze_constraints(text: str, constraints: list[str]) -> dict:
    """Analyze if text meets given constraints."""
    results = {}
    text_lower = text.lower()

    for constraint in constraints:
        constraint_lower = constraint.lower()

        if "mitigador" in constraint_lower or "suavizador" in constraint_lower:
            count = sum(1 for m in REGISTER_MARKERS["hedging"] if m in text_lower)
            required = 2 if "2" in constraint else 1
            results[constraint] = {"met": count >= required, "found": count, "required": required}

        elif "concesi" in constraint_lower or "aunque" in constraint_lower:
            concessive = ["aunque", "si bien", "a pesar de", "pese a"]
            found = any(c in text_lower for c in concessive)
            results[constraint] = {"met": found, "markers_found": [c for c in concessive if c in text_lower]}

        elif "verbo preciso" in constraint_lower:
            precise_verbs = ["afrontar", "plantear", "desactivar", "sopesar", "tramitar", "aportar"]
            found = [v for v in precise_verbs if v in text_lower]
            results[constraint] = {"met": len(found) > 0, "verbs_found": found}

        elif "usted" in constraint_lower or "formal" in constraint_lower:
            formal_markers = ["usted", "le ", "les ", "le agradeceria", "seria posible"]
            found = any(m in text_lower for m in formal_markers)
            results[constraint] = {"met": found, "register": "formal" if found else "informal"}

        elif "calco" in constraint_lower or "ingles" in constraint_lower:
            calques = ["aplicar para", "realizar que", "soportar (como support)"]
            found = any(c.split()[0] in text_lower for c in calques)
            results[constraint] = {"met": not found, "calques_avoided": not found}

        else:
            # Generic keyword check
            results[constraint] = {"met": True, "note": "Manual review recommended"}

    return results


def sentence_split(text: str) -> list[str]:
    """Split text into sentences."""
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_candidate_phrases(text: str, min_words: int = 2, max_words: int = 4) -> list[str]:
    """Extract candidate phrases (bigrams, trigrams) from text."""
    words = re.findall(r'\b[a-záéíóúüñ]+\b', text.lower())
    phrases = []

    for n in range(min_words, min(max_words + 1, len(words) + 1)):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i + n])
            phrases.append(phrase)

    return list(set(phrases))


def detect_domain(text: str, domain_keywords: dict) -> list[str]:
    """Detect which domains a text belongs to based on keywords."""
    text_lower = text.lower()
    detected = []

    for domain, keywords in domain_keywords.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches >= 2:
            detected.append((domain, matches))

    # Sort by match count and return domain names
    return [d[0] for d in sorted(detected, key=lambda x: x[1], reverse=True)]


def calculate_srs_interval(quality: int, current_ease: float, current_interval: int) -> tuple[int, float]:
    """
    Calculate next SRS interval using SM-2 algorithm.

    Args:
        quality: 0-5 rating of recall quality
        current_ease: current ease factor
        current_interval: current interval in days

    Returns:
        (next_interval, new_ease_factor)
    """
    if quality >= 3:  # Correct response
        if current_interval == 0:
            next_interval = 1
        elif current_interval == 1:
            next_interval = 6
        else:
            next_interval = int(current_interval * current_ease)

        new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    else:  # Incorrect response
        next_interval = 1
        new_ease = current_ease

    new_ease = max(1.3, new_ease)  # Minimum ease factor
    return next_interval, new_ease


def get_review_priority(items: list[dict], max_items: int = 20) -> list[dict]:
    """
    Prioritize items for review based on due date and ease factor.
    Lower ease = higher priority (harder items).
    """
    today = date.today().isoformat()

    # Filter overdue items
    overdue = [i for i in items if (i.get("next_review") or "9999") <= today]

    # Sort by ease factor (ascending) then by overdue days
    sorted_items = sorted(
        overdue,
        key=lambda x: (x.get("ease_factor", 2.5), x.get("next_review") or "0000")
    )

    return sorted_items[:max_items]


def format_time_ago(date_str: Optional[str]) -> str:
    """Format a date string as 'X days ago' etc."""
    if not date_str:
        return "Never"

    try:
        past_date = date.fromisoformat(date_str)
        delta = date.today() - past_date

        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    except ValueError:
        return date_str


def generate_exercise_feedback(user_answer: str, correct_answer: str, explanation: str) -> dict:
    """Generate feedback for an exercise answer."""
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

    if is_correct:
        return {
            "correct": True,
            "message": "Correcto!",
            "explanation": explanation,
            "type": "success",
        }
    else:
        return {
            "correct": False,
            "message": f"No exactamente. La respuesta correcta es: {correct_answer}",
            "explanation": explanation,
            "type": "error",
        }


def shuffle_with_seed(items: list, seed: int) -> list:
    """Shuffle a list with a specific seed for reproducibility."""
    rng = random.Random(seed)
    shuffled = items.copy()
    rng.shuffle(shuffled)
    return shuffled


def get_streak_days(history: Optional[list[dict]] = None) -> int:
    """
    Calculate current streak of consecutive days with activity.

    Args:
        history: List of dictionaries containing 'metric_date' or 'date' keys.
                 Can be None or empty.

    Returns:
        Integer representing the current streak in days.
    """
    if not history:
        return 0

    # Safely extract dates, handling various formats and None values
    dates = set()
    for h in history:
        if not isinstance(h, dict):
            continue
        date_val = h.get("metric_date") or h.get("date")
        if date_val:
            # Handle datetime strings that might include time
            if isinstance(date_val, str):
                date_val = date_val[:10]  # Take only YYYY-MM-DD portion
            dates.add(date_val)

    if not dates:
        return 0

    sorted_dates = sorted(dates, reverse=True)
    streak = 0
    expected = date.today()

    for date_str in sorted_dates:
        try:
            d = date.fromisoformat(date_str)
            if d == expected:
                streak += 1
                expected = expected - timedelta(days=1)
            elif d < expected:
                break
        except (ValueError, TypeError):
            continue

    return streak
