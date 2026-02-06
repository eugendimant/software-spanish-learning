"""Verb Choice Studio page with Conjugation Drills."""
import streamlit as st
import random
from datetime import date, datetime, timedelta
from typing import Optional

from utils.theme import render_hero, render_section_header, render_html
from utils.database import record_progress, save_vocab_item
from utils.content import VERB_CHOICE_STUDIO
from utils.helpers import seed_for_day, detect_language, normalize_accents


# ============================================
# CONJUGATION DATA - Common Irregular Verbs
# ============================================

# Person/number keys: yo, tu, el, nosotros, vosotros, ellos
PERSONS = {
    "yo": "yo",
    "tu": "tu",
    "el": "el/ella/usted",
    "nosotros": "nosotros",
    "vosotros": "vosotros",
    "ellos": "ellos/ellas/ustedes"
}

PERSON_LABELS = {
    "yo": "yo",
    "tu": "tu",
    "el": "el/ella/Ud.",
    "nosotros": "nosotros/as",
    "vosotros": "vosotros/as",
    "ellos": "ellos/ellas/Uds."
}

TENSE_LABELS = {
    "presente": "Presente",
    "preterito": "Preterito Indefinido",
    "imperfecto": "Imperfecto",
    "futuro": "Futuro Simple",
    "condicional": "Condicional",
    "subjuntivo_presente": "Subjuntivo Presente",
    "subjuntivo_imperfecto": "Subjuntivo Imperfecto"
}

# Comprehensive conjugation data for irregular verbs
CONJUGATION_DATA = {
    "ser": {
        "meaning": "to be (permanent)",
        "presente": {
            "yo": "soy", "tu": "eres", "el": "es",
            "nosotros": "somos", "vosotros": "sois", "ellos": "son"
        },
        "preterito": {
            "yo": "fui", "tu": "fuiste", "el": "fue",
            "nosotros": "fuimos", "vosotros": "fuisteis", "ellos": "fueron"
        },
        "imperfecto": {
            "yo": "era", "tu": "eras", "el": "era",
            "nosotros": "eramos", "vosotros": "erais", "ellos": "eran"
        },
        "futuro": {
            "yo": "sere", "tu": "seras", "el": "sera",
            "nosotros": "seremos", "vosotros": "sereis", "ellos": "seran"
        },
        "condicional": {
            "yo": "seria", "tu": "serias", "el": "seria",
            "nosotros": "seriamos", "vosotros": "seriais", "ellos": "serian"
        },
        "subjuntivo_presente": {
            "yo": "sea", "tu": "seas", "el": "sea",
            "nosotros": "seamos", "vosotros": "seais", "ellos": "sean"
        },
        "subjuntivo_imperfecto": {
            "yo": "fuera", "tu": "fueras", "el": "fuera",
            "nosotros": "fueramos", "vosotros": "fuerais", "ellos": "fueran"
        }
    },
    "estar": {
        "meaning": "to be (temporary/location)",
        "presente": {
            "yo": "estoy", "tu": "estas", "el": "esta",
            "nosotros": "estamos", "vosotros": "estais", "ellos": "estan"
        },
        "preterito": {
            "yo": "estuve", "tu": "estuviste", "el": "estuvo",
            "nosotros": "estuvimos", "vosotros": "estuvisteis", "ellos": "estuvieron"
        },
        "imperfecto": {
            "yo": "estaba", "tu": "estabas", "el": "estaba",
            "nosotros": "estabamos", "vosotros": "estabais", "ellos": "estaban"
        },
        "futuro": {
            "yo": "estare", "tu": "estaras", "el": "estara",
            "nosotros": "estaremos", "vosotros": "estareis", "ellos": "estaran"
        },
        "condicional": {
            "yo": "estaria", "tu": "estarias", "el": "estaria",
            "nosotros": "estariamos", "vosotros": "estariais", "ellos": "estarian"
        },
        "subjuntivo_presente": {
            "yo": "este", "tu": "estes", "el": "este",
            "nosotros": "estemos", "vosotros": "esteis", "ellos": "esten"
        },
        "subjuntivo_imperfecto": {
            "yo": "estuviera", "tu": "estuvieras", "el": "estuviera",
            "nosotros": "estuvieramos", "vosotros": "estuvierais", "ellos": "estuvieran"
        }
    },
    "ir": {
        "meaning": "to go",
        "presente": {
            "yo": "voy", "tu": "vas", "el": "va",
            "nosotros": "vamos", "vosotros": "vais", "ellos": "van"
        },
        "preterito": {
            "yo": "fui", "tu": "fuiste", "el": "fue",
            "nosotros": "fuimos", "vosotros": "fuisteis", "ellos": "fueron"
        },
        "imperfecto": {
            "yo": "iba", "tu": "ibas", "el": "iba",
            "nosotros": "ibamos", "vosotros": "ibais", "ellos": "iban"
        },
        "futuro": {
            "yo": "ire", "tu": "iras", "el": "ira",
            "nosotros": "iremos", "vosotros": "ireis", "ellos": "iran"
        },
        "condicional": {
            "yo": "iria", "tu": "irias", "el": "iria",
            "nosotros": "iriamos", "vosotros": "iriais", "ellos": "irian"
        },
        "subjuntivo_presente": {
            "yo": "vaya", "tu": "vayas", "el": "vaya",
            "nosotros": "vayamos", "vosotros": "vayais", "ellos": "vayan"
        },
        "subjuntivo_imperfecto": {
            "yo": "fuera", "tu": "fueras", "el": "fuera",
            "nosotros": "fueramos", "vosotros": "fuerais", "ellos": "fueran"
        }
    },
    "haber": {
        "meaning": "to have (auxiliary)",
        "presente": {
            "yo": "he", "tu": "has", "el": "ha",
            "nosotros": "hemos", "vosotros": "habeis", "ellos": "han"
        },
        "preterito": {
            "yo": "hube", "tu": "hubiste", "el": "hubo",
            "nosotros": "hubimos", "vosotros": "hubisteis", "ellos": "hubieron"
        },
        "imperfecto": {
            "yo": "habia", "tu": "habias", "el": "habia",
            "nosotros": "habiamos", "vosotros": "habiais", "ellos": "habian"
        },
        "futuro": {
            "yo": "habre", "tu": "habras", "el": "habra",
            "nosotros": "habremos", "vosotros": "habreis", "ellos": "habran"
        },
        "condicional": {
            "yo": "habria", "tu": "habrias", "el": "habria",
            "nosotros": "habriamos", "vosotros": "habriais", "ellos": "habrian"
        },
        "subjuntivo_presente": {
            "yo": "haya", "tu": "hayas", "el": "haya",
            "nosotros": "hayamos", "vosotros": "hayais", "ellos": "hayan"
        },
        "subjuntivo_imperfecto": {
            "yo": "hubiera", "tu": "hubieras", "el": "hubiera",
            "nosotros": "hubieramos", "vosotros": "hubierais", "ellos": "hubieran"
        }
    },
    "tener": {
        "meaning": "to have (possession)",
        "presente": {
            "yo": "tengo", "tu": "tienes", "el": "tiene",
            "nosotros": "tenemos", "vosotros": "teneis", "ellos": "tienen"
        },
        "preterito": {
            "yo": "tuve", "tu": "tuviste", "el": "tuvo",
            "nosotros": "tuvimos", "vosotros": "tuvisteis", "ellos": "tuvieron"
        },
        "imperfecto": {
            "yo": "tenia", "tu": "tenias", "el": "tenia",
            "nosotros": "teniamos", "vosotros": "teniais", "ellos": "tenian"
        },
        "futuro": {
            "yo": "tendre", "tu": "tendras", "el": "tendra",
            "nosotros": "tendremos", "vosotros": "tendreis", "ellos": "tendran"
        },
        "condicional": {
            "yo": "tendria", "tu": "tendrias", "el": "tendria",
            "nosotros": "tendriamos", "vosotros": "tendriais", "ellos": "tendrian"
        },
        "subjuntivo_presente": {
            "yo": "tenga", "tu": "tengas", "el": "tenga",
            "nosotros": "tengamos", "vosotros": "tengais", "ellos": "tengan"
        },
        "subjuntivo_imperfecto": {
            "yo": "tuviera", "tu": "tuvieras", "el": "tuviera",
            "nosotros": "tuvieramos", "vosotros": "tuvierais", "ellos": "tuvieran"
        }
    },
    "hacer": {
        "meaning": "to do/make",
        "presente": {
            "yo": "hago", "tu": "haces", "el": "hace",
            "nosotros": "hacemos", "vosotros": "haceis", "ellos": "hacen"
        },
        "preterito": {
            "yo": "hice", "tu": "hiciste", "el": "hizo",
            "nosotros": "hicimos", "vosotros": "hicisteis", "ellos": "hicieron"
        },
        "imperfecto": {
            "yo": "hacia", "tu": "hacias", "el": "hacia",
            "nosotros": "haciamos", "vosotros": "haciais", "ellos": "hacian"
        },
        "futuro": {
            "yo": "hare", "tu": "haras", "el": "hara",
            "nosotros": "haremos", "vosotros": "hareis", "ellos": "haran"
        },
        "condicional": {
            "yo": "haria", "tu": "harias", "el": "haria",
            "nosotros": "hariamos", "vosotros": "hariais", "ellos": "harian"
        },
        "subjuntivo_presente": {
            "yo": "haga", "tu": "hagas", "el": "haga",
            "nosotros": "hagamos", "vosotros": "hagais", "ellos": "hagan"
        },
        "subjuntivo_imperfecto": {
            "yo": "hiciera", "tu": "hicieras", "el": "hiciera",
            "nosotros": "hicieramos", "vosotros": "hicierais", "ellos": "hicieran"
        }
    },
    "decir": {
        "meaning": "to say/tell",
        "presente": {
            "yo": "digo", "tu": "dices", "el": "dice",
            "nosotros": "decimos", "vosotros": "decis", "ellos": "dicen"
        },
        "preterito": {
            "yo": "dije", "tu": "dijiste", "el": "dijo",
            "nosotros": "dijimos", "vosotros": "dijisteis", "ellos": "dijeron"
        },
        "imperfecto": {
            "yo": "decia", "tu": "decias", "el": "decia",
            "nosotros": "deciamos", "vosotros": "deciais", "ellos": "decian"
        },
        "futuro": {
            "yo": "dire", "tu": "diras", "el": "dira",
            "nosotros": "diremos", "vosotros": "direis", "ellos": "diran"
        },
        "condicional": {
            "yo": "diria", "tu": "dirias", "el": "diria",
            "nosotros": "diriamos", "vosotros": "diriais", "ellos": "dirian"
        },
        "subjuntivo_presente": {
            "yo": "diga", "tu": "digas", "el": "diga",
            "nosotros": "digamos", "vosotros": "digais", "ellos": "digan"
        },
        "subjuntivo_imperfecto": {
            "yo": "dijera", "tu": "dijeras", "el": "dijera",
            "nosotros": "dijeramos", "vosotros": "dijerais", "ellos": "dijeran"
        }
    },
    "poder": {
        "meaning": "to be able to/can",
        "presente": {
            "yo": "puedo", "tu": "puedes", "el": "puede",
            "nosotros": "podemos", "vosotros": "podeis", "ellos": "pueden"
        },
        "preterito": {
            "yo": "pude", "tu": "pudiste", "el": "pudo",
            "nosotros": "pudimos", "vosotros": "pudisteis", "ellos": "pudieron"
        },
        "imperfecto": {
            "yo": "podia", "tu": "podias", "el": "podia",
            "nosotros": "podiamos", "vosotros": "podiais", "ellos": "podian"
        },
        "futuro": {
            "yo": "podre", "tu": "podras", "el": "podra",
            "nosotros": "podremos", "vosotros": "podreis", "ellos": "podran"
        },
        "condicional": {
            "yo": "podria", "tu": "podrias", "el": "podria",
            "nosotros": "podriamos", "vosotros": "podriais", "ellos": "podrian"
        },
        "subjuntivo_presente": {
            "yo": "pueda", "tu": "puedas", "el": "pueda",
            "nosotros": "podamos", "vosotros": "podais", "ellos": "puedan"
        },
        "subjuntivo_imperfecto": {
            "yo": "pudiera", "tu": "pudieras", "el": "pudiera",
            "nosotros": "pudieramos", "vosotros": "pudierais", "ellos": "pudieran"
        }
    },
    "querer": {
        "meaning": "to want/love",
        "presente": {
            "yo": "quiero", "tu": "quieres", "el": "quiere",
            "nosotros": "queremos", "vosotros": "quereis", "ellos": "quieren"
        },
        "preterito": {
            "yo": "quise", "tu": "quisiste", "el": "quiso",
            "nosotros": "quisimos", "vosotros": "quisisteis", "ellos": "quisieron"
        },
        "imperfecto": {
            "yo": "queria", "tu": "querias", "el": "queria",
            "nosotros": "queriamos", "vosotros": "queriais", "ellos": "querian"
        },
        "futuro": {
            "yo": "querre", "tu": "querras", "el": "querra",
            "nosotros": "querremos", "vosotros": "querreis", "ellos": "querran"
        },
        "condicional": {
            "yo": "querria", "tu": "querrias", "el": "querria",
            "nosotros": "querriamos", "vosotros": "querriais", "ellos": "querrian"
        },
        "subjuntivo_presente": {
            "yo": "quiera", "tu": "quieras", "el": "quiera",
            "nosotros": "queramos", "vosotros": "querais", "ellos": "quieran"
        },
        "subjuntivo_imperfecto": {
            "yo": "quisiera", "tu": "quisieras", "el": "quisiera",
            "nosotros": "quisieramos", "vosotros": "quisierais", "ellos": "quisieran"
        }
    },
    "saber": {
        "meaning": "to know (facts)",
        "presente": {
            "yo": "se", "tu": "sabes", "el": "sabe",
            "nosotros": "sabemos", "vosotros": "sabeis", "ellos": "saben"
        },
        "preterito": {
            "yo": "supe", "tu": "supiste", "el": "supo",
            "nosotros": "supimos", "vosotros": "supisteis", "ellos": "supieron"
        },
        "imperfecto": {
            "yo": "sabia", "tu": "sabias", "el": "sabia",
            "nosotros": "sabiamos", "vosotros": "sabiais", "ellos": "sabian"
        },
        "futuro": {
            "yo": "sabre", "tu": "sabras", "el": "sabra",
            "nosotros": "sabremos", "vosotros": "sabreis", "ellos": "sabran"
        },
        "condicional": {
            "yo": "sabria", "tu": "sabrias", "el": "sabria",
            "nosotros": "sabriamos", "vosotros": "sabriais", "ellos": "sabrian"
        },
        "subjuntivo_presente": {
            "yo": "sepa", "tu": "sepas", "el": "sepa",
            "nosotros": "sepamos", "vosotros": "sepais", "ellos": "sepan"
        },
        "subjuntivo_imperfecto": {
            "yo": "supiera", "tu": "supieras", "el": "supiera",
            "nosotros": "supieramos", "vosotros": "supierais", "ellos": "supieran"
        }
    },
    "poner": {
        "meaning": "to put/place",
        "presente": {
            "yo": "pongo", "tu": "pones", "el": "pone",
            "nosotros": "ponemos", "vosotros": "poneis", "ellos": "ponen"
        },
        "preterito": {
            "yo": "puse", "tu": "pusiste", "el": "puso",
            "nosotros": "pusimos", "vosotros": "pusisteis", "ellos": "pusieron"
        },
        "imperfecto": {
            "yo": "ponia", "tu": "ponias", "el": "ponia",
            "nosotros": "poniamos", "vosotros": "poniais", "ellos": "ponian"
        },
        "futuro": {
            "yo": "pondre", "tu": "pondras", "el": "pondra",
            "nosotros": "pondremos", "vosotros": "pondreis", "ellos": "pondran"
        },
        "condicional": {
            "yo": "pondria", "tu": "pondrias", "el": "pondria",
            "nosotros": "pondriamos", "vosotros": "pondriais", "ellos": "pondrian"
        },
        "subjuntivo_presente": {
            "yo": "ponga", "tu": "pongas", "el": "ponga",
            "nosotros": "pongamos", "vosotros": "pongais", "ellos": "pongan"
        },
        "subjuntivo_imperfecto": {
            "yo": "pusiera", "tu": "pusieras", "el": "pusiera",
            "nosotros": "pusieramos", "vosotros": "pusierais", "ellos": "pusieran"
        }
    },
    "venir": {
        "meaning": "to come",
        "presente": {
            "yo": "vengo", "tu": "vienes", "el": "viene",
            "nosotros": "venimos", "vosotros": "venis", "ellos": "vienen"
        },
        "preterito": {
            "yo": "vine", "tu": "viniste", "el": "vino",
            "nosotros": "vinimos", "vosotros": "vinisteis", "ellos": "vinieron"
        },
        "imperfecto": {
            "yo": "venia", "tu": "venias", "el": "venia",
            "nosotros": "veniamos", "vosotros": "veniais", "ellos": "venian"
        },
        "futuro": {
            "yo": "vendre", "tu": "vendras", "el": "vendra",
            "nosotros": "vendremos", "vosotros": "vendreis", "ellos": "vendran"
        },
        "condicional": {
            "yo": "vendria", "tu": "vendrias", "el": "vendria",
            "nosotros": "vendriamos", "vosotros": "vendriais", "ellos": "vendrian"
        },
        "subjuntivo_presente": {
            "yo": "venga", "tu": "vengas", "el": "venga",
            "nosotros": "vengamos", "vosotros": "vengais", "ellos": "vengan"
        },
        "subjuntivo_imperfecto": {
            "yo": "viniera", "tu": "vinieras", "el": "viniera",
            "nosotros": "vinieramos", "vosotros": "vinierais", "ellos": "vinieran"
        }
    },
    "ver": {
        "meaning": "to see",
        "presente": {
            "yo": "veo", "tu": "ves", "el": "ve",
            "nosotros": "vemos", "vosotros": "veis", "ellos": "ven"
        },
        "preterito": {
            "yo": "vi", "tu": "viste", "el": "vio",
            "nosotros": "vimos", "vosotros": "visteis", "ellos": "vieron"
        },
        "imperfecto": {
            "yo": "veia", "tu": "veias", "el": "veia",
            "nosotros": "veiamos", "vosotros": "veiais", "ellos": "veian"
        },
        "futuro": {
            "yo": "vere", "tu": "veras", "el": "vera",
            "nosotros": "veremos", "vosotros": "vereis", "ellos": "veran"
        },
        "condicional": {
            "yo": "veria", "tu": "verias", "el": "veria",
            "nosotros": "veriamos", "vosotros": "veriais", "ellos": "verian"
        },
        "subjuntivo_presente": {
            "yo": "vea", "tu": "veas", "el": "vea",
            "nosotros": "veamos", "vosotros": "veais", "ellos": "vean"
        },
        "subjuntivo_imperfecto": {
            "yo": "viera", "tu": "vieras", "el": "viera",
            "nosotros": "vieramos", "vosotros": "vierais", "ellos": "vieran"
        }
    },
    "dar": {
        "meaning": "to give",
        "presente": {
            "yo": "doy", "tu": "das", "el": "da",
            "nosotros": "damos", "vosotros": "dais", "ellos": "dan"
        },
        "preterito": {
            "yo": "di", "tu": "diste", "el": "dio",
            "nosotros": "dimos", "vosotros": "disteis", "ellos": "dieron"
        },
        "imperfecto": {
            "yo": "daba", "tu": "dabas", "el": "daba",
            "nosotros": "dabamos", "vosotros": "dabais", "ellos": "daban"
        },
        "futuro": {
            "yo": "dare", "tu": "daras", "el": "dara",
            "nosotros": "daremos", "vosotros": "dareis", "ellos": "daran"
        },
        "condicional": {
            "yo": "daria", "tu": "darias", "el": "daria",
            "nosotros": "dariamos", "vosotros": "dariais", "ellos": "darian"
        },
        "subjuntivo_presente": {
            "yo": "de", "tu": "des", "el": "de",
            "nosotros": "demos", "vosotros": "deis", "ellos": "den"
        },
        "subjuntivo_imperfecto": {
            "yo": "diera", "tu": "dieras", "el": "diera",
            "nosotros": "dieramos", "vosotros": "dierais", "ellos": "dieran"
        }
    }
}

# List of all verbs for random selection
ALL_VERBS = list(CONJUGATION_DATA.keys())
ALL_TENSES = list(TENSE_LABELS.keys())
ALL_PERSONS = list(PERSONS.keys())


# ============================================
# CONJUGATION FUNCTIONS
# ============================================

def get_conjugation(verb: str, tense: str, person: str) -> Optional[str]:
    """
    Get the correct conjugation for a verb in a specific tense and person.

    Args:
        verb: The infinitive form of the verb (e.g., "ser", "estar")
        tense: The tense (e.g., "presente", "preterito", "imperfecto")
        person: The person/number (e.g., "yo", "tu", "el", "nosotros", "vosotros", "ellos")

    Returns:
        The conjugated form, or None if not found
    """
    verb = verb.lower().strip()
    tense = tense.lower().strip()
    person = person.lower().strip()

    if verb not in CONJUGATION_DATA:
        return None

    verb_data = CONJUGATION_DATA[verb]
    if tense not in verb_data:
        return None

    tense_data = verb_data[tense]
    if person not in tense_data:
        return None

    return tense_data[person]


def check_conjugation(user_answer: str, verb: str, tense: str, person: str,
                      accent_tolerant: bool = True) -> dict:
    """
    Validate a user's conjugation answer.

    Args:
        user_answer: The user's answer
        verb: The infinitive form of the verb
        tense: The tense
        person: The person/number
        accent_tolerant: Whether to accept answers without proper accents

    Returns:
        Dict with keys:
        - correct: bool - whether the answer is correct
        - expected: str - the correct answer
        - feedback: str - feedback message
        - quality: int - SRS quality score (0-5)
    """
    correct_answer = get_conjugation(verb, tense, person)

    if correct_answer is None:
        return {
            "correct": False,
            "expected": "Unknown",
            "feedback": "This verb/tense/person combination is not in the database.",
            "quality": 0
        }

    user_normalized = user_answer.strip().lower()
    correct_normalized = correct_answer.lower()

    # Exact match
    if user_normalized == correct_normalized:
        return {
            "correct": True,
            "expected": correct_answer,
            "feedback": "Perfect!",
            "quality": 5
        }

    # Check with accent tolerance
    if accent_tolerant:
        user_no_accent = normalize_accents(user_normalized)
        correct_no_accent = normalize_accents(correct_normalized)

        if user_no_accent == correct_no_accent:
            return {
                "correct": True,
                "expected": correct_answer,
                "feedback": f"Correct! Note the proper form with accents: {correct_answer}",
                "quality": 4  # Slightly lower for missing accents
            }

    # Check for common near-misses (one character off)
    if len(user_normalized) == len(correct_normalized):
        diffs = sum(1 for a, b in zip(user_normalized, correct_normalized) if a != b)
        if diffs == 1:
            return {
                "correct": False,
                "expected": correct_answer,
                "feedback": f"Very close! The correct form is: {correct_answer}",
                "quality": 2
            }

    return {
        "correct": False,
        "expected": correct_answer,
        "feedback": f"The correct form is: {correct_answer}",
        "quality": 1
    }


def get_verb_progress(verb: str) -> dict:
    """Get progress data for a specific verb from the database."""
    profile_id = get_active_profile_id()
    try:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM conjugation_progress
                WHERE profile_id = ? AND verb = ?
            """, (profile_id, verb)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def update_verb_progress(verb: str, tense: str, person: str, quality: int) -> None:
    """Update SRS progress for a verb conjugation."""
    profile_id = get_active_profile_id()
    key = f"{verb}_{tense}_{person}"

    try:
        with get_connection() as conn:
            # Ensure table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conjugation_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    verb TEXT NOT NULL,
                    tense TEXT NOT NULL,
                    person TEXT NOT NULL,
                    correct_count INTEGER DEFAULT 0,
                    incorrect_count INTEGER DEFAULT 0,
                    ease_factor REAL DEFAULT 2.5,
                    interval_days INTEGER DEFAULT 1,
                    next_review TEXT,
                    last_reviewed TEXT,
                    UNIQUE(profile_id, verb, tense, person)
                )
            """)

            # Get existing record
            row = conn.execute("""
                SELECT * FROM conjugation_progress
                WHERE profile_id = ? AND verb = ? AND tense = ? AND person = ?
            """, (profile_id, verb, tense, person)).fetchone()

            today = date.today().isoformat()

            if row:
                # Update existing record using SM-2 algorithm
                ease_factor = row["ease_factor"]
                interval = row["interval_days"]
                correct_count = row["correct_count"]
                incorrect_count = row["incorrect_count"]

                if quality >= 3:  # Correct
                    correct_count += 1
                    if interval == 1:
                        interval = 6
                    else:
                        interval = int(interval * ease_factor)
                    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
                else:  # Incorrect
                    incorrect_count += 1
                    interval = 1

                ease_factor = max(1.3, ease_factor)
                next_review = (date.today() + timedelta(days=interval)).isoformat()

                conn.execute("""
                    UPDATE conjugation_progress SET
                        correct_count = ?,
                        incorrect_count = ?,
                        ease_factor = ?,
                        interval_days = ?,
                        next_review = ?,
                        last_reviewed = ?
                    WHERE profile_id = ? AND verb = ? AND tense = ? AND person = ?
                """, (correct_count, incorrect_count, ease_factor, interval,
                      next_review, today, profile_id, verb, tense, person))
            else:
                # Insert new record
                interval = 1 if quality < 3 else 6
                next_review = (date.today() + timedelta(days=interval)).isoformat()

                conn.execute("""
                    INSERT INTO conjugation_progress
                    (profile_id, verb, tense, person, correct_count, incorrect_count,
                     ease_factor, interval_days, next_review, last_reviewed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (profile_id, verb, tense, person,
                      1 if quality >= 3 else 0,
                      0 if quality >= 3 else 1,
                      2.5, interval, next_review, today))

            conn.commit()
    except Exception as e:
        print(f"Error updating conjugation progress: {e}")


def get_due_conjugations(limit: int = 10) -> list:
    """Get conjugations due for review based on SRS schedule."""
    profile_id = get_active_profile_id()
    today = date.today().isoformat()

    try:
        with get_connection() as conn:
            # Check if table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='conjugation_progress'
            """)
            if not cursor.fetchone():
                return []

            rows = conn.execute("""
                SELECT verb, tense, person, ease_factor, incorrect_count
                FROM conjugation_progress
                WHERE profile_id = ? AND (next_review IS NULL OR next_review <= ?)
                ORDER BY ease_factor ASC, incorrect_count DESC
                LIMIT ?
            """, (profile_id, today, limit)).fetchall()

            return [dict(row) for row in rows]
    except Exception:
        return []


def get_weak_conjugations(limit: int = 5) -> list:
    """Get the conjugations the user struggles with most."""
    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='conjugation_progress'
            """)
            if not cursor.fetchone():
                return []

            rows = conn.execute("""
                SELECT verb, tense, person, incorrect_count, correct_count, ease_factor
                FROM conjugation_progress
                WHERE profile_id = ? AND (correct_count + incorrect_count) > 0
                ORDER BY (CAST(incorrect_count AS REAL) / (correct_count + incorrect_count + 1)) DESC,
                         ease_factor ASC
                LIMIT ?
            """, (profile_id, limit)).fetchall()

            return [dict(row) for row in rows]
    except Exception:
        return []


def get_conjugation_stats() -> dict:
    """Get overall conjugation practice statistics."""
    profile_id = get_active_profile_id()

    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='conjugation_progress'
            """)
            if not cursor.fetchone():
                return {"total_practiced": 0, "total_correct": 0, "accuracy": 0, "verbs_practiced": 0}

            row = conn.execute("""
                SELECT
                    COUNT(*) as total_items,
                    SUM(correct_count) as total_correct,
                    SUM(incorrect_count) as total_incorrect,
                    COUNT(DISTINCT verb) as verbs_practiced
                FROM conjugation_progress
                WHERE profile_id = ?
            """, (profile_id,)).fetchone()

            if row:
                total = (row["total_correct"] or 0) + (row["total_incorrect"] or 0)
                accuracy = ((row["total_correct"] or 0) / total * 100) if total > 0 else 0
                return {
                    "total_practiced": total,
                    "total_correct": row["total_correct"] or 0,
                    "accuracy": round(accuracy, 1),
                    "verbs_practiced": row["verbs_practiced"] or 0
                }
    except Exception:
        pass

    return {"total_practiced": 0, "total_correct": 0, "accuracy": 0, "verbs_practiced": 0}


# ============================================
# UI RENDERING FUNCTIONS
# ============================================

def render_conjugation_drill():
    """Render the conjugation drill UI."""

    # Initialize session state for drill
    if "cd_verb" not in st.session_state:
        st.session_state.cd_verb = None
    if "cd_tense" not in st.session_state:
        st.session_state.cd_tense = None
    if "cd_person" not in st.session_state:
        st.session_state.cd_person = None
    if "cd_user_answer" not in st.session_state:
        st.session_state.cd_user_answer = ""
    if "cd_checked" not in st.session_state:
        st.session_state.cd_checked = False
    if "cd_result" not in st.session_state:
        st.session_state.cd_result = None
    if "cd_session_correct" not in st.session_state:
        st.session_state.cd_session_correct = 0
    if "cd_session_total" not in st.session_state:
        st.session_state.cd_session_total = 0
    if "cd_streak" not in st.session_state:
        st.session_state.cd_streak = 0

    # Display stats
    stats = get_conjugation_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.cd_session_correct}/{st.session_state.cd_session_total}</div>
            <div class="stat-label">This Session</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{st.session_state.cd_streak}</div>
            <div class="stat-label">Current Streak</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['accuracy']}%</div>
            <div class="stat-label">All-Time Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['verbs_practiced']}/14</div>
            <div class="stat-label">Verbs Practiced</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Drill settings
    with st.expander("Drill Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            selected_verbs = st.multiselect(
                "Focus on specific verbs:",
                ALL_VERBS,
                default=[],
                key="cd_selected_verbs"
            )
        with col2:
            selected_tenses = st.multiselect(
                "Focus on specific tenses:",
                list(TENSE_LABELS.keys()),
                default=[],
                format_func=lambda x: TENSE_LABELS.get(x, x),
                key="cd_selected_tenses"
            )

        drill_mode = st.radio(
            "Drill Mode:",
            ["Random", "SRS (Spaced Repetition)", "Focus on Weak Points"],
            horizontal=True,
            key="cd_drill_mode"
        )

    # Generate a new question if needed
    if st.session_state.cd_verb is None or st.session_state.cd_checked:
        if st.button("Start New Question", type="primary", use_container_width=True, key="cd_new_question"):
            _generate_new_question(selected_verbs, selected_tenses, drill_mode)
            st.rerun()

    # Display current question
    if st.session_state.cd_verb:
        verb = st.session_state.cd_verb
        tense = st.session_state.cd_tense
        person = st.session_state.cd_person

        verb_info = CONJUGATION_DATA.get(verb, {})
        meaning = verb_info.get("meaning", "")

        # Question card
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 0.875rem; color: #8E8E93; margin-bottom: 0.5rem;">
                Conjugate the verb
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: #000000; margin-bottom: 0.5rem;">
                {verb.upper()}
            </div>
            <div style="font-size: 0.875rem; color: #8E8E93; margin-bottom: 1rem;">
                ({meaning})
            </div>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span class="pill pill-accent">{TENSE_LABELS.get(tense, tense)}</span>
                <span class="pill pill-warning">{PERSON_LABELS.get(person, person)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Answer input
        if not st.session_state.cd_checked:
            user_answer = st.text_input(
                "Your answer:",
                value=st.session_state.cd_user_answer,
                key="cd_answer_input",
                placeholder=f"Conjugate '{verb}' for '{PERSON_LABELS.get(person, person)}' in {TENSE_LABELS.get(tense, tense)}..."
            )
            st.session_state.cd_user_answer = user_answer

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Check Answer", type="primary", use_container_width=True, key="cd_check"):
                    if user_answer.strip():
                        result = check_conjugation(user_answer, verb, tense, person)
                        st.session_state.cd_result = result
                        st.session_state.cd_checked = True
                        st.session_state.cd_session_total += 1

                        if result["correct"]:
                            st.session_state.cd_session_correct += 1
                            st.session_state.cd_streak += 1
                        else:
                            st.session_state.cd_streak = 0

                        # Update SRS progress
                        update_verb_progress(verb, tense, person, result["quality"])

                        # Log activity
                        log_activity(
                            "conjugation_drill",
                            f"{verb} - {tense} - {person}",
                            f"Answer: {user_answer}, Correct: {result['expected']}",
                            score=result["quality"]
                        )

                        # Record progress
                        record_progress({"grammar_reviewed": 1})

                        st.rerun()
                    else:
                        st.warning("Please enter your answer.")

            with col2:
                if st.button("Skip", use_container_width=True, key="cd_skip"):
                    st.session_state.cd_streak = 0
                    _generate_new_question(selected_verbs, selected_tenses, drill_mode)
                    st.rerun()

            # Hint button
            if st.button("Show Hint", key="cd_hint"):
                correct = get_conjugation(verb, tense, person)
                if correct:
                    hint = correct[0] + "_" * (len(correct) - 2) + correct[-1] if len(correct) > 2 else "_" * len(correct)
                    st.info(f"Hint: {hint} ({len(correct)} letters)")

        else:
            # Show result
            result = st.session_state.cd_result

            if result["correct"]:
                st.markdown(f"""
                <div class="feedback-box feedback-success">
                    <strong>Correct!</strong> {result['feedback']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feedback-box feedback-error">
                    <strong>Not quite.</strong> {result['feedback']}
                    <div style="margin-top: 0.5rem;">
                        Your answer: <strong>{st.session_state.cd_user_answer}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Show full conjugation table for this verb/tense
            with st.expander("View Full Conjugation Table", expanded=False):
                _render_conjugation_table(verb, tense)

            # Next question button
            if st.button("Next Question", type="primary", use_container_width=True, key="cd_next"):
                _generate_new_question(selected_verbs, selected_tenses, drill_mode)
                st.rerun()

    # Show weak points section
    weak_points = get_weak_conjugations(5)
    if weak_points:
        st.divider()
        st.markdown("### Areas to Focus On")

        for wp in weak_points:
            accuracy = (wp["correct_count"] / (wp["correct_count"] + wp["incorrect_count"]) * 100) if (wp["correct_count"] + wp["incorrect_count"]) > 0 else 0

            st.markdown(f"""
            <div class="card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{wp['verb']}</strong> - {TENSE_LABELS.get(wp['tense'], wp['tense'])} - {PERSON_LABELS.get(wp['person'], wp['person'])}
                    </div>
                    <div>
                        <span class="pill pill-{'error' if accuracy < 50 else 'warning' if accuracy < 75 else 'success'}">
                            {accuracy:.0f}% accuracy
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _generate_new_question(selected_verbs: list, selected_tenses: list, drill_mode: str):
    """Generate a new conjugation question."""

    # Determine verb pool
    verb_pool = selected_verbs if selected_verbs else ALL_VERBS

    # Determine tense pool
    tense_pool = selected_tenses if selected_tenses else ALL_TENSES

    if drill_mode == "SRS (Spaced Repetition)":
        # Try to get due conjugations first
        due = get_due_conjugations(10)
        if due:
            # Filter by selected verbs/tenses if any
            filtered = [d for d in due
                       if (not selected_verbs or d["verb"] in selected_verbs)
                       and (not selected_tenses or d["tense"] in selected_tenses)]
            if filtered:
                item = random.choice(filtered)
                st.session_state.cd_verb = item["verb"]
                st.session_state.cd_tense = item["tense"]
                st.session_state.cd_person = item["person"]
                st.session_state.cd_user_answer = ""
                st.session_state.cd_checked = False
                st.session_state.cd_result = None
                return

    elif drill_mode == "Focus on Weak Points":
        weak = get_weak_conjugations(10)
        if weak:
            filtered = [w for w in weak
                       if (not selected_verbs or w["verb"] in selected_verbs)
                       and (not selected_tenses or w["tense"] in selected_tenses)]
            if filtered:
                item = random.choice(filtered)
                st.session_state.cd_verb = item["verb"]
                st.session_state.cd_tense = item["tense"]
                st.session_state.cd_person = item["person"]
                st.session_state.cd_user_answer = ""
                st.session_state.cd_checked = False
                st.session_state.cd_result = None
                return

    # Random selection (default)
    st.session_state.cd_verb = random.choice(verb_pool)
    st.session_state.cd_tense = random.choice(tense_pool)
    st.session_state.cd_person = random.choice(ALL_PERSONS)
    st.session_state.cd_user_answer = ""
    st.session_state.cd_checked = False
    st.session_state.cd_result = None


def _render_conjugation_table(verb: str, highlight_tense: str = None):
    """Render a conjugation table for a verb."""
    verb_data = CONJUGATION_DATA.get(verb, {})

    if not verb_data:
        st.warning(f"No conjugation data for '{verb}'")
        return

    # Create table for the highlighted tense or all tenses
    tenses_to_show = [highlight_tense] if highlight_tense else ALL_TENSES

    for tense in tenses_to_show:
        if tense not in verb_data:
            continue

        st.markdown(f"**{TENSE_LABELS.get(tense, tense)}**")

        tense_data = verb_data[tense]

        # Create a 2-column layout for the conjugations
        col1, col2 = st.columns(2)

        with col1:
            for person in ["yo", "tu", "el"]:
                if person in tense_data:
                    st.markdown(f"- **{PERSON_LABELS.get(person, person)}**: {tense_data[person]}")

        with col2:
            for person in ["nosotros", "vosotros", "ellos"]:
                if person in tense_data:
                    st.markdown(f"- **{PERSON_LABELS.get(person, person)}**: {tense_data[person]}")


def render_conjugation_reference():
    """Render a reference view of all verb conjugations."""
    st.markdown("### Conjugation Reference")

    # Verb selector
    selected_verb = st.selectbox(
        "Select a verb:",
        ALL_VERBS,
        format_func=lambda v: f"{v} - {CONJUGATION_DATA.get(v, {}).get('meaning', '')}",
        key="ref_verb_select"
    )

    # Tense selector
    selected_tenses = st.multiselect(
        "Show tenses:",
        ALL_TENSES,
        default=["presente", "preterito"],
        format_func=lambda t: TENSE_LABELS.get(t, t),
        key="ref_tense_select"
    )

    if selected_verb and selected_tenses:
        verb_data = CONJUGATION_DATA.get(selected_verb, {})

        st.markdown(f"### {selected_verb.upper()} ({verb_data.get('meaning', '')})")

        # Create columns for each tense
        cols = st.columns(min(len(selected_tenses), 3))

        for i, tense in enumerate(selected_tenses):
            if tense not in verb_data:
                continue

            with cols[i % len(cols)]:
                st.markdown(f"**{TENSE_LABELS.get(tense, tense)}**")

                tense_data = verb_data[tense]

                table_html = "<table style='width: 100%; border-collapse: collapse; font-size: 0.875rem;'>"
                for person in ALL_PERSONS:
                    if person in tense_data:
                        plabel = PERSON_LABELS.get(person, person)
                        table_html += (
                            f"<tr><td style='padding: 4px 8px; border-bottom: 1px solid #E5E5EA; color: #8E8E93;'>{plabel}</td>"
                            f"<td style='padding: 4px 8px; border-bottom: 1px solid #E5E5EA; font-weight: 500;'>{tense_data[person]}</td></tr>"
                        )
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)


# ============================================
# MAIN PAGE RENDERING
# ============================================

def render_verb_studio_page():
    """Render the Verb Choice Studio page."""
    render_hero(
        title="Verb Studio",
        subtitle="Master verb conjugations and nuance. From irregular verb drills to precision in register and tone.",
        pills=["Conjugation", "Nuance", "Register", "Irregular Verbs"]
    )

    # Mode selection
    render_section_header("Practice Mode")

    mode = st.radio(
        "Choose your practice mode:",
        [
            "Conjugation Drill",
            "Verb Choice Practice",
            "Conjugation Reference",
            "Browse All Verbs"
        ],
        horizontal=True,
        key="vs_mode_select"
    )

    st.divider()

    if mode == "Conjugation Drill":
        render_conjugation_drill()

    elif mode == "Conjugation Reference":
        render_conjugation_reference()

    elif mode == "Browse All Verbs":
        render_verb_reference()

    else:  # Verb Choice Practice
        # Initialize session state for verb choice
        if "vs_current_scenario" not in st.session_state:
            st.session_state.vs_current_scenario = 0
        if "vs_selected_verb" not in st.session_state:
            st.session_state.vs_selected_verb = None
        if "vs_explanation" not in st.session_state:
            st.session_state.vs_explanation = ""
        if "vs_revealed" not in st.session_state:
            st.session_state.vs_revealed = False

        # Check if there are any scenarios to practice
        if not VERB_CHOICE_STUDIO:
            st.warning("No verb scenarios available. Please check the content configuration.")
            return

        # Sub-mode selection for verb choice
        sub_mode = st.radio(
            "Verb Choice Mode:",
            ["Guided Practice", "Random Challenge"],
            horizontal=True,
            key="vs_sub_mode"
        )

        if sub_mode == "Random Challenge":
            # Random scenario
            seed = seed_for_day(date.today(), str(st.session_state.get("vs_current_scenario", 0)))
            random.seed(seed)
            scenario = random.choice(VERB_CHOICE_STUDIO)
            render_verb_scenario(scenario, random_mode=True)
        else:
            # Guided practice - sequential
            scenario = VERB_CHOICE_STUDIO[st.session_state.vs_current_scenario % len(VERB_CHOICE_STUDIO)]
            render_verb_scenario(scenario, random_mode=False)


def render_verb_scenario(scenario: dict, random_mode: bool = False):
    """Render a single verb choice scenario."""
    st.markdown("### Scenario")

    render_html(f"""
        <div class="card">
            <p style="font-size: 1.125rem; line-height: 1.6;">
                {scenario['scenario']}
            </p>
        </div>
    """)

    st.markdown("### Choose the Best Verb")

    # Display verb options as cards
    options = scenario.get("options", [])

    if not options:
        st.warning("No verb options available for this scenario.")
        return

    cols = st.columns(len(options))

    for i, (col, opt) in enumerate(zip(cols, options)):
        with col:
            is_selected = st.session_state.vs_selected_verb == opt["verb"]

            # Card styling based on selection
            border_color = "#007AFF" if is_selected else "#E5E5EA"
            bg_color = "rgba(37, 99, 235, 0.05)" if is_selected else "#F2F2F7"

            render_html(f"""
                <div class="verb-option {'selected' if is_selected else ''}" style="border-color: {border_color}; background: {bg_color};">
                    <div class="verb-name">{opt['verb']}</div>
                    <div class="verb-meta">
                        <span class="pill pill-{'primary' if opt.get('register') == 'formal' else 'secondary' if opt.get('register') == 'neutral' else 'muted'}">
                            {opt.get('register', 'neutral')}
                        </span>
                        <span class="pill pill-{'warning' if opt.get('intensity') == 'alta' else 'muted'}">
                            {opt.get('intensity', 'media')} intensity
                        </span>
                    </div>
                    <div class="verb-note">
                        <strong>Implies:</strong> {opt.get('implication', '')}
                    </div>
                    <div class="verb-note" style="margin-top: 0.5rem;">
                        <strong>Typical objects:</strong> {opt.get('objects', '')}
                    </div>
                </div>
            """)

            if st.button(f"Select '{opt['verb']}'", key=f"select_{i}", use_container_width=True):
                st.session_state.vs_selected_verb = opt["verb"]
                st.session_state.vs_revealed = False
                st.rerun()

    # Explanation input
    st.markdown("### Explain Your Choice (in Spanish)")

    explanation = st.text_area(
        "Por que elegiste este verbo? (Una linea es suficiente)",
        value=st.session_state.vs_explanation,
        height=80,
        key="verb_explanation",
        placeholder="Escriba su explicacion en espanol..."
    )
    st.session_state.vs_explanation = explanation

    # Add hint button
    if st.button("Hint in English", key="verb_hint"):
        st.info("**Hint:** Explain in Spanish why you think this verb is the best choice. Consider register (formal/informal), intensity, and context.")

    # Check answer button
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Check Answer", type="primary", use_container_width=True, key="vs_check_answer"):
            # Validate Spanish if explanation provided
            if explanation.strip():
                lang_info = detect_language(explanation)
                if lang_info["language"] == "english":
                    render_html("""
                        <div class="feedback-box feedback-warning">
                            🌐 <strong>Try explaining in Spanish!</strong> It's great practice.
                            Use the "Hint in English" button if you need help.
                        </div>
                    """)
            st.session_state.vs_revealed = True

    with col2:
        # Always show Next button - works for both modes
        next_label = "Next Scenario" if not random_mode else "New Scenario"
        if st.button(next_label, use_container_width=True, key="vs_next_scenario"):
            if random_mode:
                # Get a new random scenario
                st.session_state.vs_current_scenario = random.randint(0, 100)  # Random seed
            else:
                st.session_state.vs_current_scenario += 1
            st.session_state.vs_selected_verb = None
            st.session_state.vs_explanation = ""
            st.session_state.vs_revealed = False
            st.rerun()

    # Reveal answer and feedback
    if st.session_state.vs_revealed:
        st.divider()

        best = scenario.get("best", "")
        also = scenario.get("also", [])
        contrasts = scenario.get("contrast", [])

        is_correct = st.session_state.vs_selected_verb == best
        is_acceptable = st.session_state.vs_selected_verb in also

        if is_correct:
            render_html("""
                <div class="feedback-box feedback-success">
                    ✅ <strong>Perfect!</strong> You chose the best option for this context.
                </div>
            """)
            record_progress({"vocab_reviewed": 1})
        elif is_acceptable:
            render_html(f"""
                <div class="feedback-box feedback-info">
                    👍 <strong>Also acceptable!</strong> '{st.session_state.vs_selected_verb}' works here, but '{best}' is the best fit.
                </div>
            """)
            record_progress({"vocab_reviewed": 1})
        else:
            render_html(f"""
                <div class="feedback-box feedback-error">
                    ❌ <strong>Not quite.</strong> The best choice is '{best}'.
                </div>
            """)

        # Show contrasts
        st.markdown("### Why?")

        st.markdown(f"**Best fit:** `{best}`")
        if also:
            st.markdown(f"**Also possible:** {', '.join([f'`{a}`' for a in also])}")

        st.markdown("**Minimal pair contrasts:**")
        for contrast in contrasts:
            st.markdown(f"- {contrast}")

        # Save the verb to vocabulary if learned
        if is_correct or is_acceptable:
            best_option = next((o for o in options if o["verb"] == best), options[0])
            save_vocab_item({
                "term": best,
                "meaning": best_option.get("implication", ""),
                "domain": "Verb Studio",
                "register": best_option.get("register", "neutral"),
                "pos": "verb",
            })


def render_verb_reference():
    """Render a reference view of all verbs."""
    st.markdown("### Verb Reference Library")

    # Extract all unique verbs
    all_verbs = {}
    for scenario in VERB_CHOICE_STUDIO:
        for opt in scenario.get("options", []):
            verb = opt["verb"]
            if verb not in all_verbs:
                all_verbs[verb] = {
                    "verb": verb,
                    "register": opt.get("register", "neutral"),
                    "intensity": opt.get("intensity", "media"),
                    "implication": opt.get("implication", ""),
                    "objects": opt.get("objects", ""),
                    "scenarios": []
                }
            all_verbs[verb]["scenarios"].append(scenario["scenario"][:100] + "...")

    # Display in a sortable format
    sort_by = st.selectbox("Sort by:", ["Alphabetical", "Register", "Intensity"])

    verbs_list = list(all_verbs.values())

    if sort_by == "Alphabetical":
        verbs_list.sort(key=lambda x: x["verb"])
    elif sort_by == "Register":
        order = {"formal": 0, "neutral": 1, "casual": 2}
        verbs_list.sort(key=lambda x: order.get(x["register"], 1))
    else:  # Intensity
        order = {"alta": 0, "media": 1, "baja": 2}
        verbs_list.sort(key=lambda x: order.get(x["intensity"], 1))

    # Display verbs
    for verb_data in verbs_list:
        with st.expander(f"{verb_data['verb']} ({verb_data['register']})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Implication:** {verb_data['implication']}")
                st.markdown(f"**Typical objects:** {verb_data['objects']}")
                st.markdown("**Used in scenarios:**")
                for s in verb_data["scenarios"][:2]:
                    st.caption(f"- {s}")

            with col2:
                render_html(f"""
                    <div class="verb-meta" style="flex-direction: column; align-items: flex-start;">
                        <span class="pill pill-primary">{verb_data['register']}</span>
                        <span class="pill pill-warning" style="margin-top: 0.25rem;">{verb_data['intensity']}</span>
                    </div>
                """)

                if st.button("Practice this verb", key=f"practice_{verb_data['verb']}"):
                    # Find a scenario with this verb
                    for i, scenario in enumerate(VERB_CHOICE_STUDIO):
                        if any(o["verb"] == verb_data["verb"] for o in scenario.get("options", [])):
                            st.session_state.vs_current_scenario = i
                            st.session_state.vs_selected_verb = None
                            st.session_state.vs_revealed = False
                            st.rerun()
                            break
