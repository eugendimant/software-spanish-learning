"""Helper functions for VivaLingo Pro."""
import difflib
import hashlib
import random
import re
import unicodedata
from datetime import date, timedelta
from typing import Optional

from utils.content import COMMON_MISTAKES, REGISTER_MARKERS


# Accent normalization map for Spanish
ACCENT_MAP = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ü': 'u', 'ñ': 'n',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'Ü': 'U', 'Ñ': 'N'
}


def normalize_accents(text: str) -> str:
    """Remove Spanish accent marks from text for lenient comparison.

    Examples:
        normalize_accents("mañana") -> "manana"
        normalize_accents("café") -> "cafe"
        normalize_accents("así") -> "asi"
    """
    result = []
    for char in text:
        result.append(ACCENT_MAP.get(char, char))
    return ''.join(result)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def compare_answers(user_answer: str, correct_answer: str, accent_tolerant: bool = False,
                    grading_mode: str = "balanced") -> tuple:
    """Compare user answer with correct answer based on grading settings.

    Args:
        user_answer: The answer provided by the user
        correct_answer: The expected correct answer
        accent_tolerant: If True, accept answers without proper accents
        grading_mode: "strict", "balanced", or "lenient"

    Returns:
        Tuple of (is_correct: bool, feedback_type: str)
        feedback_type explains why the answer was accepted/rejected
    """
    # Normalize whitespace and case
    user_normalized = user_answer.lower().strip()
    correct_normalized = correct_answer.lower().strip()

    # Exact match - always correct
    if user_normalized == correct_normalized:
        return (True, "exact_match")

    # If accent tolerant, compare without accents
    if accent_tolerant:
        user_no_accent = normalize_accents(user_normalized)
        correct_no_accent = normalize_accents(correct_normalized)
        if user_no_accent == correct_no_accent:
            return (True, "accent_tolerance")

    # Strict mode: only exact matches (already handled above)
    if grading_mode == "strict":
        return (False, "strict_mismatch")

    # Balanced mode: allow 1-2 character typos
    if grading_mode in ["balanced", "lenient"]:
        # Calculate edit distance
        distance = levenshtein_distance(user_normalized, correct_normalized)

        # Also check with accents normalized
        user_no_accent = normalize_accents(user_normalized)
        correct_no_accent = normalize_accents(correct_normalized)
        distance_no_accent = levenshtein_distance(user_no_accent, correct_no_accent)

        # Use the smaller distance (more lenient)
        min_distance = min(distance, distance_no_accent)

        # Allow typos based on word length
        word_len = len(correct_normalized)
        if word_len <= 4:
            allowed_errors = 1 if grading_mode == "lenient" else 0
        elif word_len <= 8:
            allowed_errors = 2 if grading_mode == "lenient" else 1
        else:
            allowed_errors = 3 if grading_mode == "lenient" else 2

        if min_distance <= allowed_errors:
            return (True, f"typo_tolerance_{min_distance}")

    # Lenient mode: also accept semantic variations
    if grading_mode == "lenient":
        # Check if user answer contains important words from correct answer
        correct_words = set(correct_normalized.split())
        user_words = set(user_normalized.split())

        # Remove common articles/prepositions for comparison
        stop_words = {"el", "la", "los", "las", "un", "una", "de", "a", "en", "y", "o", "que"}
        correct_important = correct_words - stop_words
        user_important = user_words - stop_words

        if correct_important and user_important:
            overlap = len(correct_important & user_important) / len(correct_important)
            if overlap >= 0.7:  # 70% of important words match
                return (True, "semantic_match")

    return (False, "mismatch")


def get_accent_feedback(user_answer: str, correct_answer: str) -> Optional[str]:
    """If answer is correct except for accents, provide helpful feedback.

    Returns None if answers don't match even without accents,
    or a feedback string if only accents are wrong.
    """
    user_no_accent = normalize_accents(user_answer.lower().strip())
    correct_no_accent = normalize_accents(correct_answer.lower().strip())

    if user_no_accent == correct_no_accent and user_answer.lower().strip() != correct_answer.lower().strip():
        # Find which accents are missing
        missing_accents = []
        for i, (user_char, correct_char) in enumerate(zip(user_answer.lower(), correct_answer.lower())):
            if user_char != correct_char and normalize_accents(correct_char) == user_char:
                missing_accents.append(f"'{user_char}' should be '{correct_char}'")

        if missing_accents:
            return f"Close! Just needs accent marks: {', '.join(missing_accents[:3])}"
        return "Close! Check your accent marks."

    return None


def check_false_friends(text: str) -> list:
    """Check user text for potential false friend usage.

    Returns list of warnings for any false friends detected.
    """
    from utils.content import FALSE_FRIENDS

    warnings = []
    text_lower = text.lower()
    words = set(re.findall(r'\b[a-záéíóúüñ]+\b', text_lower))

    for false_friend, info in FALSE_FRIENDS.items():
        # Check if the false friend word appears in the text
        if false_friend in words:
            warnings.append({
                "word": false_friend,
                "looks_like": info["looks_like"],
                "actually_means": info["actually_means"],
                "correct_word": info["correct_word"],
                "warning": info["warning"],
                "example_right": info["example_right"]
            })

    return warnings


def get_collocation_suggestions(word: str) -> list:
    """Get common collocations for a given verb/word.

    Returns list of chunks with their meanings.
    """
    from utils.content import COLLOCATIONS

    word_lower = word.lower().strip()
    return COLLOCATIONS.get(word_lower, [])


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


def detect_language(text: str) -> dict:
    """
    Detect if text is likely Spanish, English, or mixed.
    Returns dict with language info and confidence.
    """
    text_lower = text.lower()
    words = re.findall(r'\b[a-záéíóúüñ]+\b', text_lower)

    if not words:
        return {"language": "unknown", "confidence": 0, "spanish_ratio": 0}

    # Common Spanish words (articles, prepositions, conjunctions, common verbs)
    spanish_indicators = {
        # Articles
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        # Prepositions
        "de", "en", "con", "por", "para", "sin", "sobre", "entre", "hacia", "desde", "hasta",
        # Conjunctions
        "y", "o", "pero", "sino", "aunque", "porque", "cuando", "si", "que", "como",
        # Common verbs
        "es", "está", "son", "están", "hay", "tiene", "tengo", "puede", "puedo",
        "soy", "estoy", "ser", "estar", "hacer", "hago", "hace", "quiero", "quiere",
        "voy", "va", "ir", "venir", "vengo", "viene", "decir", "digo", "dice",
        # Pronouns
        "yo", "tú", "él", "ella", "nosotros", "ellos", "ellas", "usted", "ustedes",
        "me", "te", "le", "nos", "les", "lo", "la", "se",
        # Common words
        "muy", "más", "menos", "bien", "mal", "todo", "todos", "nada", "algo",
        "este", "esta", "esto", "ese", "esa", "eso", "aquel", "aquella",
        "mi", "tu", "su", "mis", "tus", "sus", "nuestro", "nuestra",
    }

    # Common English words that would indicate English text
    english_indicators = {
        # Articles/determiners
        "the", "a", "an", "this", "that", "these", "those",
        # Prepositions
        "of", "in", "to", "for", "with", "on", "at", "from", "by", "about",
        # Conjunctions
        "and", "or", "but", "if", "when", "because", "although", "while",
        # Common verbs
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "can", "may",
        "get", "got", "go", "went", "come", "came", "make", "made", "take", "took",
        # Pronouns
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
        "my", "your", "his", "its", "our", "their", "what", "who", "which",
        # Common words
        "not", "no", "yes", "just", "only", "also", "very", "much", "many",
        "here", "there", "where", "how", "why", "all", "some", "any", "every",
        "know", "think", "want", "need", "like", "love", "work", "help",
    }

    spanish_count = sum(1 for w in words if w in spanish_indicators)
    english_count = sum(1 for w in words if w in english_indicators)

    # Check for Spanish-specific characters (accents, ñ)
    has_spanish_chars = bool(re.search(r'[áéíóúüñ¿¡]', text_lower))

    # Calculate ratios
    total_words = len(words)
    spanish_ratio = spanish_count / total_words if total_words > 0 else 0
    english_ratio = english_count / total_words if total_words > 0 else 0

    # Boost Spanish score if Spanish characters present
    if has_spanish_chars:
        spanish_ratio += 0.15

    # Determine language
    if spanish_ratio > english_ratio and spanish_ratio > 0.15:
        confidence = min(spanish_ratio * 2, 1.0)
        return {"language": "spanish", "confidence": confidence, "spanish_ratio": spanish_ratio, "english_ratio": english_ratio}
    elif english_ratio > spanish_ratio and english_ratio > 0.15:
        confidence = min(english_ratio * 2, 1.0)
        return {"language": "english", "confidence": confidence, "spanish_ratio": spanish_ratio, "english_ratio": english_ratio}
    elif spanish_ratio > 0 or english_ratio > 0:
        return {"language": "mixed", "confidence": 0.5, "spanish_ratio": spanish_ratio, "english_ratio": english_ratio}
    else:
        return {"language": "unknown", "confidence": 0, "spanish_ratio": 0, "english_ratio": 0}


def check_text_for_mistakes(text: str) -> list[dict]:
    """
    Check text for common mistakes using rule-based patterns.
    Returns list of detected mistakes with corrections.

    Now includes:
    - Language detection (warns if not Spanish)
    - Common Spanish learner mistakes
    - Gender agreement errors
    - Ser/Estar confusion
    - Preposition errors
    - False friends and calques
    """
    mistakes_found = []
    text_lower = text.lower()

    # First, check if text is actually Spanish
    lang_info = detect_language(text)

    if lang_info["language"] == "english":
        mistakes_found.append({
            "original": text[:50] + "..." if len(text) > 50 else text,
            "correction": "(Write in Spanish)",
            "explanation": f"This appears to be English text (confidence: {lang_info['confidence']:.0%}). Please write in Spanish to practice.",
            "examples": ["Intenta escribir: 'No sé qué estoy escribiendo aquí'"],
            "tag": "language",
            "position": 0,
        })
        return mistakes_found  # Return early - no point checking Spanish rules on English text

    if lang_info["language"] == "unknown" and len(text.strip()) > 10:
        mistakes_found.append({
            "original": text[:30] + "..." if len(text) > 30 else text,
            "correction": "(Unable to analyze)",
            "explanation": "Could not determine the language. Please write a longer text in Spanish.",
            "examples": [],
            "tag": "language",
            "position": 0,
        })

    if lang_info["language"] == "mixed":
        mistakes_found.append({
            "original": "Mixed language detected",
            "correction": "(Write entirely in Spanish)",
            "explanation": f"Your text appears to mix Spanish ({lang_info['spanish_ratio']:.0%}) and English ({lang_info['english_ratio']:.0%}). Try to write entirely in Spanish.",
            "examples": ["Evita mezclar idiomas en la misma oración"],
            "tag": "language",
            "position": 0,
        })

    # Check against common mistakes database
    for mistake in COMMON_MISTAKES:
        pattern = mistake["pattern"].lower()
        if pattern in text_lower:
            pos = text_lower.find(pattern)
            mistakes_found.append({
                "original": text[pos:pos + len(pattern)],
                "correction": mistake["correction"],
                "explanation": mistake["explanation"],
                "examples": mistake.get("examples", []),
                "tag": mistake["tag"],
                "position": pos,
            })

    # Gender agreement patterns (expanded)
    gender_patterns = [
        (r"\bla problema\b", "el problema", "gender", "Problema es masculino pese a terminar en -a"),
        (r"\bun problema\s+grande\b", "un problema grande", "gender", None),  # This is correct, skip
        (r"\bla tema\b", "el tema", "gender", "Tema es masculino pese a terminar en -a"),
        (r"\bla sistema\b", "el sistema", "gender", "Sistema es masculino"),
        (r"\bla programa\b", "el programa", "gender", "Programa es masculino"),
        (r"\bla idioma\b", "el idioma", "gender", "Idioma es masculino"),
        (r"\bla clima\b", "el clima", "gender", "Clima es masculino"),
        (r"\bla mapa\b", "el mapa", "gender", "Mapa es masculino"),
        (r"\bla dia\b", "el día", "gender", "Día es masculino"),
        (r"\bel mano\b", "la mano", "gender", "Mano es femenino pese a terminar en -o"),
        (r"\bel foto\b", "la foto", "gender", "Foto (fotografía) es femenino"),
        (r"\bel moto\b", "la moto", "gender", "Moto (motocicleta) es femenino"),
        (r"\bel radio\b(?!grafía)", "la radio", "gender", "Radio (emisora) es femenino en la mayoría de países"),
        (r"\bmucho gente\b", "mucha gente", "gender", "Gente es femenino"),
        (r"\bmuchos personas\b", "muchas personas", "gender", "Persona es femenino"),
        (r"\blos manos\b", "las manos", "gender", "Mano es femenino"),
    ]

    for pattern, correction, tag, explanation in gender_patterns:
        if explanation is None:  # Skip correct patterns
            continue
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

    # Ser/Estar confusion (expanded)
    ser_estar_patterns = [
        (r"\bes cansado\b", "está cansado", "copula", "Estados físicos/emocionales temporales usan estar"),
        (r"\bes enfermo\b", "está enfermo", "copula", "Estados de salud temporales usan estar"),
        (r"\bes contento\b", "está contento", "copula", "Estados emocionales usan estar"),
        (r"\bes triste\b", "está triste", "copula", "Estados emocionales temporales usan estar"),
        (r"\bes nervioso\b", "está nervioso", "copula", "Estados emocionales usan estar"),
        (r"\bsoy de acuerdo\b", "estoy de acuerdo", "copula", "'Estar de acuerdo' es la expresión correcta"),
        (r"\bsoy seguro que\b", "estoy seguro de que", "copula", "'Estar seguro de' es la expresión correcta"),
        (r"\bes listo\b(?!\s+para)", "está listo", "copula", "'Estar listo' = preparado; 'Ser listo' = inteligente"),
        (r"\bestá bueno\b(?!\s+que)", "es bueno", "copula", "Cualidades inherentes usan ser (pero 'está bueno' puede ser coloquial)"),
        (r"\bestá importante\b", "es importante", "copula", "Características esenciales usan ser"),
        (r"\bestá necesario\b", "es necesario", "copula", "Características esenciales usan ser"),
        (r"\bestá posible\b", "es posible", "copula", "Posibilidad se expresa con ser"),
    ]

    for pattern, correction, tag, explanation in ser_estar_patterns:
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

    # Preposition errors (expanded)
    preposition_patterns = [
        (r"\bpensar sobre\b", "pensar en", "preposition", "En español se dice 'pensar en' no 'pensar sobre'"),
        (r"\bsoñar sobre\b", "soñar con", "preposition", "En español se dice 'soñar con'"),
        (r"\bdepend[eo] en\b", "depender de", "preposition", "Depender siempre va con 'de'"),
        (r"\bconfiar sobre\b", "confiar en", "preposition", "Se dice 'confiar en'"),
        (r"\bcontar sobre\b", "contar con", "preposition", "Se dice 'contar con' (to count on)"),
        (r"\besperar para\b", "esperar a", "preposition", "'Esperar a' alguien/algo"),
        (r"\bllegar a casa\b", "llegar a casa", "preposition", None),  # Correct
        (r"\bllegar en casa\b", "llegar a casa", "preposition", "Se usa 'llegar a' no 'llegar en'"),
        (r"\bentrar en\b", "entrar en", "preposition", None),  # Correct
        (r"\bentrar a\b(?!\s+trabajar)", "entrar en", "preposition", "En España se prefiere 'entrar en' (en Latinoamérica 'entrar a' es común)"),
        (r"\bcasarse a\b", "casarse con", "preposition", "Se dice 'casarse con' alguien"),
        (r"\benamorarse de\b", "enamorarse de", "preposition", None),  # Correct
        (r"\benamorarse con\b", "enamorarse de", "preposition", "Se dice 'enamorarse de' no 'con'"),
    ]

    for pattern, correction, tag, explanation in preposition_patterns:
        if explanation is None:  # Skip correct patterns
            continue
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

    # Common English calques and false friends
    calque_patterns = [
        (r"\baplicar para\b", "solicitar", "calque", "Calco del inglés 'apply for'. Usa 'solicitar' o 'presentarse a'"),
        (r"\btomar lugar\b", "tener lugar", "calque", "Calco de 'take place'. Se dice 'tener lugar'"),
        (r"\bhacer sentido\b", "tener sentido", "calque", "Calco de 'make sense'. Se dice 'tener sentido'"),
        (r"\bllamar atrás\b", "devolver la llamada", "calque", "Calco de 'call back'. Se dice 'devolver la llamada'"),
        (r"\bcorrer para\b(?!\s+\w+\s+minutos)", "presentarse a", "calque", "Calco de 'run for' (candidatura). Se dice 'presentarse a'"),
        (r"\brealizar que\b", "darse cuenta de que", "false_friend", "'Realizar' = llevar a cabo; para 'realize' usa 'darse cuenta'"),
        (r"\bactualmente\b", "actualmente/en realidad", "false_friend", "'Actualmente' = ahora; para 'actually' usa 'en realidad'"),
        (r"\beventualmente\b", "eventualmente/finalmente", "false_friend", "'Eventualmente' = posiblemente; para 'eventually' usa 'finalmente'"),
        (r"\bsensible\b", "sensible/sensato", "false_friend", "'Sensible' = sensitive; para 'sensible' usa 'sensato'"),
        (r"\bexcitado\b", "emocionado", "false_friend", "'Excitado' tiene connotación sexual. Usa 'emocionado' o 'entusiasmado'"),
        (r"\bembarazada\b(?!\s+de)", "embarazada/avergonzada", "false_friend", "'Embarazada' = pregnant; para 'embarrassed' usa 'avergonzado/a'"),
    ]

    for pattern, correction, tag, explanation in calque_patterns:
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

    # Subject pronoun overuse (Spanish is a pro-drop language)
    pronoun_overuse = re.findall(r'\b(yo|tú|él|ella|nosotros|ellos|ellas)\b', text_lower)
    if len(pronoun_overuse) > 3 and len(text.split()) > 10:
        mistakes_found.append({
            "original": f"Pronoun overuse: {', '.join(pronoun_overuse[:4])}...",
            "correction": "(Consider omitting some subject pronouns)",
            "explanation": "Spanish is a pro-drop language - subject pronouns are often unnecessary and can sound repetitive. Only use them for emphasis or clarity.",
            "examples": ["'Yo quiero ir' → 'Quiero ir' (unless emphasizing 'I')"],
            "tag": "style",
            "position": 0,
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
