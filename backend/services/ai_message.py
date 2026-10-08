# ============================================================
# RESQ-FLOW - AI MESSAGE UNDERSTANDING ENGINE
# ============================================================
#
# Purpose:
#   Convert an arbitrary victim message into a structured
#   emergency representation.
#
# Pipeline:
#
#   Victim text / speech-to-text
#           |
#           v
#   Text normalization
#           |
#           +---- Context detection
#           |
#           +---- Safety detection
#           |
#           +---- Victim information extraction
#           |
#           +---- Rule-based disaster hints
#           |
#           +---- Trained DistilBERT semantic prediction
#           |
#           v
#   Disaster fusion
#           |
#           v
#   Emergency + danger + urgency
#
# IMPORTANT:
#   This file DOES NOT train the model.
#   train_model.py trains the DistilBERT model.
#
# Expected model:
#   backend/models/disaster_model/
#
# ============================================================

import os
import re
import json
from typing import Any, Dict, List, Optional

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "disaster_model",
)


# ============================================================
# 2. MODEL SETTINGS
# ============================================================

# A semantic prediction below this confidence is not blindly
# accepted as the final disaster type.
MODEL_CONFIDENCE_THRESHOLD = 0.60

MAX_INPUT_LENGTH = 256


# ============================================================
# 3. MODEL CACHE
# ============================================================

_TOKENIZER = None
_MODEL = None
_MODEL_LABELS = None
_MODEL_ERROR = None


# ============================================================
# 4. TEXT NORMALIZATION
# ============================================================

def clean_text(message: Any) -> str:
    """
    Normalize text coming from typing or speech-to-text.

    We deliberately do NOT remove important words.
    Emergency meaning must be preserved.
    """

    if message is None:
        return ""

    text = str(message).strip().lower()

    # Normalize apostrophes.
    text = text.replace("’", "'")
    text = text.replace("‘", "'")
    text = text.replace("`", "'")

    # Common speech-to-text variations.
    replacements = {
        "couldnt": "couldn't",
        "cant": "can't",
        "wont": "won't",
        "dont": "don't",
        "doesnt": "doesn't",
        "didnt": "didn't",
        "isnt": "isn't",
        "wasnt": "wasn't",
        "werent": "weren't",
        "im": "i'm",
        "ive": "i've",
        "ill": "i'll",
        "weve": "we've",
        "youre": "you're",
        "theyre": "they're",
    }

    for old, new in replacements.items():
        text = re.sub(
            rf"\b{re.escape(old)}\b",
            new,
            text,
        )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# 5. BASIC TEXT HELPERS
# ============================================================

def contains_any(
    text: str,
    phrases: List[str],
) -> bool:

    return any(
        phrase.lower() in text
        for phrase in phrases
    )


def phrase_is_negated(
    text: str,
    phrase: str,
    window: int = 5,
) -> bool:
    """
    Basic local negation detection.

    Example:
        "there is no fire"

    should not trigger:
        fire = True
    """

    words = text.split()
    target = phrase.lower().split()

    if not target:
        return False

    for i in range(
        len(words) - len(target) + 1
    ):

        if words[
            i:i + len(target)
        ] != target:
            continue

        start = max(
            0,
            i - window,
        )

        previous = words[
            start:i
        ]

        negations = {
            "no",
            "not",
            "never",
            "without",
            "isn't",
            "wasn't",
            "weren't",
            "don't",
            "doesn't",
            "didn't",
        }

        if any(
            word in negations
            for word in previous
        ):
            return True

    return False


def positive_match(
    text: str,
    phrases: List[str],
) -> bool:

    for phrase in phrases:

        phrase = phrase.lower()

        if phrase not in text:
            continue

        if not phrase_is_negated(
            text,
            phrase,
        ):
            return True

    return False


# ============================================================
# 6. CONTEXT
# ============================================================

HYPOTHETICAL_PHRASES = [
    "what if",
    "what should i do if",
    "what should we do if",
    "what happens if",
    "if there is",
    "if there was",
    "suppose there is",
    "suppose there was",
    "imagine there is",
    "imagine there was",
    "how to prepare for",
    "how do i prepare for",
    "how can i prepare for",
]


PAST_EVENT_PHRASES = [
    "yesterday",
    "last night",
    "last week",
    "last month",
    "last year",
    "earlier",
    "earlier today",
    "previously",
    "before",
    "a few days ago",
    "last time",
    "it happened before",
]


CURRENT_EVENT_PHRASES = [
    "right now",
    "currently",
    "at the moment",
    "happening now",
    "happening right now",
    "now",
    "we are",
    "we're",
    "i am",
    "i'm",
    "inside",
    "here",
]


DIRECT_EMERGENCY_PHRASES = [
    "help",
    "help me",
    "help us",
    "please help",
    "save me",
    "save us",
    "rescue me",
    "rescue us",
    "sos",
    "emergency",
]


def detect_context(
    text: str,
) -> Dict[str, bool]:

    hypothetical = contains_any(
        text,
        HYPOTHETICAL_PHRASES,
    )

    past_event = contains_any(
        text,
        PAST_EVENT_PHRASES,
    )

    current_event = contains_any(
        text,
        CURRENT_EVENT_PHRASES,
    )

    direct_request = positive_match(
        text,
        DIRECT_EMERGENCY_PHRASES,
    )

    if direct_request:
        current_event = True

    return {
        "current_event": current_event,
        "past_event": past_event,
        "hypothetical": hypothetical,
        "direct_emergency_request": direct_request,
    }


# ============================================================
# 7. CANONICAL DISASTER CATEGORIES
# ============================================================

# These are the internal categories used by ResQ-Flow.
#
# The model can still have its own labels.
# We normalize common model labels into these categories.

CANONICAL_CATEGORIES = [
    "earthquake",
    "flood",
    "fire",
    "wildfire",
    "tsunami",
    "cyclone",
    "tornado",
    "storm",
    "landslide",
    "avalanche",
    "volcanic_eruption",
    "lightning",
    "heatwave",
    "extreme_cold",
    "drought",
    "chemical_gas",
    "structural_collapse",
    "transport_accident",
    "industrial_accident",
    "medical_emergency",
    "unknown",
]


# ============================================================
# 8. DISASTER LANGUAGE
# ============================================================

DISASTER_PATTERNS = {

    "earthquake": [
        "earthquake",
        "earthquake happened",
        "aftershock",
        "ground is shaking",
        "ground started shaking",
        "ground is moving",
        "ground started moving",
        "ground is vibrating",
        "building is shaking",
        "building started shaking",
        "building feels shaky",
        "building is shaky",
        "house is shaking",
        "house started shaking",
        "house is shaky",
        "walls are shaking",
        "walls are vibrating",
        "floor is shaking",
        "the floor is shaking",
        "room is shaking",
        "the room is shaking",
        "everything is shaking",
        "everything started shaking",
        "violent shaking",
        "strong shaking",
        "severe shaking",
        "heavy shaking",
        "continuous shaking",
        "furniture is moving",
        "furniture is falling",
        "things are falling",
        "objects are falling",
    ],

    "flood": [
        "flood",
        "flooded",
        "flooding",
        "flash flood",
        "flash flooding",
        "flood water",
        "water is entering",
        "water entered",
        "water entered the house",
        "water entering the house",
        "water is rising",
        "rising water",
        "river overflow",
        "river has overflowed",
        "strong water current",
        "sinking in water",
        "drowning",
        "swept away by water",
        "being swept away",
        "water reached my chest",
        "water reached my waist",
        "water reached the roof",
    ],

    "fire": [
        "fire",
        "flames",
        "burning",
        "burning building",
        "building burning",
        "building is burning",
        "house burning",
        "house is burning",
        "room is burning",
        "fire spreading",
        "fire is spreading",
        "flames spreading",
        "flames are spreading",
        "smoke",
        "smoke everywhere",
        "thick smoke",
        "heavy smoke",
        "smoke filling",
        "smoke filled",
        "smoke filling the room",
        "smoke filling the building",
    ],

    "wildfire": [
        "wildfire",
        "forest fire",
        "forest is burning",
        "forest burning",
        "bush fire",
        "grass fire",
        "vegetation is burning",
        "trees are burning",
    ],

    "tsunami": [
        "tsunami",
        "giant wave",
        "huge wave",
        "massive wave",
        "sea water rushing in",
        "ocean water rushing in",
        "sea suddenly rising",
        "ocean suddenly rising",
    ],

    "cyclone": [
        "cyclone",
        "hurricane",
        "typhoon",
        "cyclonic storm",
    ],

    "tornado": [
        "tornado",
        "funnel cloud",
        "twister",
    ],

    "storm": [
        "storm",
        "severe storm",
        "violent storm",
        "thunderstorm",
        "heavy rain",
        "extreme rain",
        "cloudburst",
        "very strong winds",
        "extremely strong winds",
        "high winds",
        "storm surge",
    ],

    "landslide": [
        "landslide",
        "land slide",
        "mudslide",
        "mud slide",
        "rockslide",
        "rock slide",
        "rocks falling",
        "rocks are falling",
        "hill collapsed",
        "slope collapsed",
        "slope is collapsing",
        "debris flow",
    ],

    "avalanche": [
        "avalanche",
        "snow slide",
        "snow avalanche",
        "buried in snow",
    ],

    "volcanic_eruption": [
        "volcanic eruption",
        "volcano erupted",
        "volcano is erupting",
        "lava",
        "lava flow",
        "volcanic ash",
        "ash from volcano",
    ],

    "lightning": [
        "lightning strike",
        "lightning struck",
        "struck by lightning",
        "lightning hit",
    ],

    "heatwave": [
        "heatwave",
        "heat wave",
        "extreme heat",
        "severe heat",
        "extremely hot",
        "dangerously hot",
    ],

    "extreme_cold": [
        "extreme cold",
        "cold wave",
        "freezing conditions",
        "blizzard",
        "snowstorm",
        "freezing weather",
    ],

    "drought": [
        "drought",
        "water shortage",
        "severe water shortage",
        "no water for days",
    ],

    "chemical_gas": [
        "gas leak",
        "gas leakage",
        "gas is leaking",
        "strong gas smell",
        "chemical leak",
        "chemical spill",
        "chemical explosion",
        "toxic gas",
        "toxic fumes",
        "poisonous fumes",
        "hazardous fumes",
        "chemical exposure",
        "factory leak",
        "gas spreading",
    ],

    "structural_collapse": [
        "building collapsed",
        "building is collapsing",
        "house collapsed",
        "house is collapsing",
        "roof collapsed",
        "roof is collapsing",
        "wall collapsed",
        "bridge collapsed",
        "bridge is collapsing",
        "road collapsed",
        "road has collapsed",
        "dam broke",
        "dam failure",
        "ground collapse",
        "sinkhole",
        "trapped under rubble",
    ],

    "transport_accident": [
        "car accident",
        "vehicle accident",
        "road accident",
        "bus accident",
        "train accident",
        "train crash",
        "car crash",
        "vehicle crash",
        "truck crash",
        "bike accident",
        "motorcycle accident",
        "boat accident",
        "boat capsized",
        "ship accident",
        "plane crash",
        "aircraft accident",
    ],

    "industrial_accident": [
        "factory explosion",
        "factory accident",
        "industrial accident",
        "industrial explosion",
        "factory fire",
        "chemical plant accident",
    ],

    "medical_emergency": [
        "medical emergency",
        "heart attack",
        "chest pain",
        "severe bleeding",
        "heavy bleeding",
        "unconscious",
        "not responding",
        "seizure",
        "not breathing",
        "difficulty breathing",
        "can't breathe",
        "cannot breathe",
        "couldn't breathe",
        "could not breathe",
    ],
}


# ============================================================
# 9. CRITICAL SAFETY PATTERNS
# ============================================================

CRITICAL_PATTERNS = [

    # Breathing
    "can't breathe",
    "cannot breathe",
    "couldn't breathe",
    "could not breathe",
    "unable to breathe",
    "difficulty breathing",
    "difficulty in breathing",
    "breathing difficulty",
    "struggling to breathe",
    "shortness of breath",
    "not able to breathe",
    "not breathing",
    "suffocating",
    "suffocation",
    "choking",

    # Trapped
    "trapped",
    "trapped inside",
    "trapped under rubble",
    "buried under rubble",
    "can't get out",
    "cannot get out",
    "unable to get out",
    "can't escape",
    "cannot escape",
    "unable to escape",
    "blocked inside",

    # Water
    "drowning",
    "sinking in water",
    "we are sinking",
    "i am sinking",
    "can't stay afloat",
    "cannot stay afloat",
    "unable to stay afloat",
    "being swept away",
    "swept away by water",
    "water is rising rapidly",

    # Fire
    "building is burning",
    "house is burning",
    "room is burning",
    "fire is spreading",
    "flames are spreading",
    "surrounded by fire",
    "smoke filling the room",
    "smoke filling the building",

    # Collapse
    "building collapsed",
    "building is collapsing",
    "house collapsed",
    "roof collapsed",
    "wall collapsed",
    "trapped under rubble",

    # Explosion
    "large explosion",
    "there was an explosion",
    "something exploded",

    # Medical
    "unconscious",
    "not responding",
    "severe bleeding",
    "heavy bleeding",
    "bleeding heavily",
    "not breathing",
    "heart attack",
    "having a seizure",

    # Chemical
    "toxic gas",
    "toxic fumes",
    "poisonous fumes",
    "gas leak",
    "gas leakage",
    "chemical leak",
]


# ============================================================
# 10. VULNERABLE PEOPLE / MEDICAL INFORMATION
# ============================================================

MEDICAL_PHRASES = [
    "injured",
    "injury",
    "hurt",
    "bleeding",
    "heavy bleeding",
    "bleeding heavily",
    "unconscious",
    "not responding",
    "fainted",
    "fainting",
    "seizure",
    "heart attack",
    "chest pain",
    "severe pain",
    "broken leg",
    "broken arm",
    "medical emergency",
    "medical problem",
    "seriously injured",
]


BREATHING_PHRASES = [
    "can't breathe",
    "cannot breathe",
    "couldn't breathe",
    "could not breathe",
    "can't breath",
    "cannot breath",
    "couldn't breath",
    "could not breath",
    "unable to breathe",
    "unable to breath",
    "difficulty breathing",
    "difficulty in breathing",
    "breathing difficulty",
    "having trouble breathing",
    "having trouble breathing properly",
    "hard to breathe",
    "hard to breath",
    "struggling to breathe",
    "struggling to breath",
    "shortness of breath",
    "short of breath",
    "breathless",
    "breathing problem",
    "breathing problems",
    "not able to breathe",
    "not able to breath",
    "not breathing",
    "suffocating",
    "suffocation",
    "choking",
]


ELDERLY_PHRASES = [
    "elderly",
    "elderly person",
    "old person",
    "old woman",
    "old man",
    "grandmother",
    "grandfather",
    "grandma",
    "grandpa",
    "senior citizen",
    "my grandmother",
    "my grandfather",
]


CHILD_PHRASES = [
    "child",
    "children",
    "kid",
    "kids",
    "baby",
    "infant",
    "toddler",
    "young child",
]


MOBILITY_PHRASES = [
    "can't walk",
    "cannot walk",
    "unable to walk",
    "cannot move",
    "can't move",
    "wheelchair",
    "paralyzed",
    "paralysed",
    "mobility problem",
    "mobility issue",
    "injured leg",
    "broken leg",
]


TRAPPED_PHRASES = [
    "trapped",
    "stuck",
    "can't get out",
    "cannot get out",
    "unable to get out",
    "can't escape",
    "cannot escape",
    "unable to escape",
    "blocked inside",
    "locked inside",
    "trapped inside",
    "trapped under rubble",
]


# ============================================================
# 11. PEOPLE COUNT
# ============================================================

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def extract_people_count(
    text: str,
) -> Optional[int]:

    patterns = [
        r"\b(\d+)\s+(?:people|persons|person|victims|members)\b",
        r"\b(?:there are|we are)\s+(\d+)\b",
        r"\b(\d+)\s+of us\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )

        if match:

            value = int(
                match.group(1)
            )

            if 1 <= value <= 1000:
                return value

    # "three people"
    for word, value in NUMBER_WORDS.items():

        pattern = (
            rf"\b{word}\s+"
            r"(?:people|persons|person|victims|members|of us)\b"
        )

        if re.search(
            pattern,
            text,
        ):
            return value

    # "me and 2 others"
    match = re.search(
        r"\bme and (\d+)\s+others?\b",
        text,
    )

    if match:
        return int(
            match.group(1)
        ) + 1

    # Explicitly identifiable two-person phrases.
    two_person_patterns = [
        "me and my mom",
        "me and my mother",
        "me and my dad",
        "me and my father",
        "me and my brother",
        "me and my sister",
        "me and my grandmother",
        "me and my grandfather",
    ]

    if contains_any(
        text,
        two_person_patterns,
    ):
        return 2

    return None


# ============================================================
# 12. INFORMATION EXTRACTION
# ============================================================

def extract_information(
    text: str,
) -> Dict[str, Any]:

    people = extract_people_count(
        text
    )

    elderly = (
        True
        if positive_match(
            text,
            ELDERLY_PHRASES,
        )
        else None
    )

    children = (
        True
        if positive_match(
            text,
            CHILD_PHRASES,
        )
        else None
    )

    medical = (
        True
        if positive_match(
            text,
            MEDICAL_PHRASES,
        )
        else None
    )

    breathing = (
        True
        if positive_match(
            text,
            BREATHING_PHRASES,
        )
        else None
    )

    if breathing is True:
        medical = True

    mobility = (
        True
        if positive_match(
            text,
            MOBILITY_PHRASES,
        )
        else None
    )

    trapped = (
        True
        if positive_match(
            text,
            TRAPPED_PHRASES,
        )
        else None
    )

    return {
        "people": people,
        "elderly_present": elderly,
        "children_present": children,
        "medical_emergency": medical,
        "breathing_problem": breathing,
        "mobility_issue": mobility,
        "trapped": trapped,
    }


# ============================================================
# 13. RULE-BASED DISASTER HINTS
# ============================================================

def get_rule_hints(
    text: str,
) -> List[str]:

    hints = []

    for category, phrases in DISASTER_PATTERNS.items():

        if positive_match(
            text,
            phrases,
        ):
            hints.append(
                category
            )

    return list(
        dict.fromkeys(hints)
    )


# ============================================================
# 14. SAFETY SIGNALS
# ============================================================

def get_safety_signals(
    text: str,
) -> List[str]:

    signals = []

    if positive_match(
        text,
        BREATHING_PHRASES,
    ):
        signals.append(
            "breathing_difficulty"
        )

    if positive_match(
        text,
        TRAPPED_PHRASES,
    ):
        signals.append(
            "trapped_or_unable_to_escape"
        )

    if positive_match(
        text,
        [
            "drowning",
            "sinking in water",
            "can't stay afloat",
            "cannot stay afloat",
            "being swept away",
            "swept away by water",
        ],
    ):
        signals.append(
            "immediate_water_danger"
        )

    if positive_match(
        text,
        [
            "building is burning",
            "house is burning",
            "fire is spreading",
            "flames are spreading",
            "smoke filling the room",
            "smoke filling the building",
        ],
    ):
        signals.append(
            "immediate_fire_danger"
        )

    if positive_match(
        text,
        [
            "building collapsed",
            "building is collapsing",
            "house collapsed",
            "roof collapsed",
            "wall collapsed",
            "trapped under rubble",
        ],
    ):
        signals.append(
            "structural_danger"
        )

    if positive_match(
        text,
        [
            "unconscious",
            "not responding",
            "severe bleeding",
            "heavy bleeding",
            "bleeding heavily",
            "not breathing",
            "heart attack",
            "having a seizure",
        ],
    ):
        signals.append(
            "critical_medical_condition"
        )

    if positive_match(
        text,
        [
            "toxic gas",
            "toxic fumes",
            "poisonous fumes",
            "gas leak",
            "gas leakage",
            "chemical leak",
        ],
    ):
        signals.append(
            "chemical_exposure"
        )

    return list(
        dict.fromkeys(signals)
    )


# ============================================================
# 15. LABEL MAPPING
# ============================================================

def load_label_mapping() -> Optional[Dict[int, str]]:

    possible_files = [
        "label_mapping.json",
        "label_map.json",
        "labels.json",
        "class_labels.json",
    ]

    for filename in possible_files:

        path = os.path.join(
            MODEL_PATH,
            filename,
        )

        if not os.path.exists(path):
            continue

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(
                    file
                )

            # Your train_model.py format.
            if (
                isinstance(data, dict)
                and "disaster_labels" in data
            ):

                mapping = {}

                for key, value in data[
                    "disaster_labels"
                ].items():

                    mapping[
                        int(key)
                    ] = str(value)

                return mapping

            # Simple mapping fallback.
            if isinstance(
                data,
                dict,
            ):

                mapping = {}

                for key, value in data.items():

                    try:

                        mapping[
                            int(key)
                        ] = str(value)

                    except (
                        ValueError,
                        TypeError,
                    ):
                        continue

                if mapping:
                    return mapping

        except Exception as error:

            print(
                "[ResQ-Flow] Label mapping "
                f"error: {error}"
            )

    return None


# ============================================================
# 16. NORMALIZE MODEL LABEL
# ============================================================

def normalize_model_label(
    label: Optional[str],
) -> Optional[str]:

    if not label:
        return None

    value = label.lower().strip()

    # Remove common formatting.
    value = value.replace(
        "_",
        " ",
    ).replace(
        "-",
        " ",
    )

    mappings = {

        "earthquake": "earthquake",
        "earth quake": "earthquake",

        "flood": "flood",
        "flooding": "flood",

        "fire": "fire",
        "fire smoke": "fire",
        "wildfire": "wildfire",
        "forest fire": "wildfire",

        "tsunami": "tsunami",

        "cyclone": "cyclone",
        "hurricane": "cyclone",
        "typhoon": "cyclone",

        "tornado": "tornado",

        "storm": "storm",
        "thunderstorm": "storm",

        "landslide": "landslide",
        "mudslide": "landslide",

        "avalanche": "avalanche",

        "volcano": "volcanic_eruption",
        "volcanic eruption": "volcanic_eruption",

        "lightning": "lightning",

        "heatwave": "heatwave",
        "heat wave": "heatwave",

        "drought": "drought",

        "chemical": "chemical_gas",
        "gas leak": "chemical_gas",
        "chemical leak": "chemical_gas",

        "building collapse": "structural_collapse",
        "structural collapse": "structural_collapse",

        "transport accident": "transport_accident",
        "road accident": "transport_accident",

        "industrial accident": "industrial_accident",

        "medical emergency": "medical_emergency",
    }

    if value in mappings:
        return mappings[value]

    # Partial matching for model labels.
    if "earthquake" in value:
        return "earthquake"

    if "flood" in value:
        return "flood"

    if "wildfire" in value or "forest fire" in value:
        return "wildfire"

    if "fire" in value:
        return "fire"

    if "tsunami" in value:
        return "tsunami"

    if any(
        word in value
        for word in [
            "cyclone",
            "hurricane",
            "typhoon",
        ]
    ):
        return "cyclone"

    if "tornado" in value:
        return "tornado"

    if "storm" in value:
        return "storm"

    if any(
        word in value
        for word in [
            "landslide",
            "mudslide",
        ]
    ):
        return "landslide"

    if "avalanche" in value:
        return "avalanche"

    if "volcano" in value:
        return "volcanic_eruption"

    if "lightning" in value:
        return "lightning"

    if "heat" in value:
        return "heatwave"

    if "drought" in value:
        return "drought"

    if any(
        word in value
        for word in [
            "chemical",
            "gas",
        ]
    ):
        return "chemical_gas"

    if any(
        word in value
        for word in [
            "collapse",
            "structural",
        ]
    ):
        return "structural_collapse"

    if any(
        word in value
        for word in [
            "transport",
            "vehicle",
            "road accident",
        ]
    ):
        return "transport_accident"

    return None


# ============================================================
# 17. LOAD DISTILBERT
# ============================================================

def load_semantic_model() -> bool:

    global _TOKENIZER
    global _MODEL
    global _MODEL_LABELS
    global _MODEL_ERROR

    if (
        _TOKENIZER is not None
        and _MODEL is not None
    ):
        return True

    if _MODEL_ERROR is not None:
        return False

    if not os.path.isdir(
        MODEL_PATH
    ):

        _MODEL_ERROR = (
            "Model directory not found: "
            + MODEL_PATH
        )

        return False

    try:

        print(
            "[ResQ-Flow] Loading semantic model:"
        )

        print(
            MODEL_PATH
        )

        _TOKENIZER = (
            AutoTokenizer.from_pretrained(
                MODEL_PATH
            )
        )

        _MODEL = (
            AutoModelForSequenceClassification
            .from_pretrained(
                MODEL_PATH
            )
        )

        _MODEL.eval()

        # First use model config.
        config_labels = getattr(
            _MODEL.config,
            "id2label",
            None,
        )

        if config_labels:

            _MODEL_LABELS = {
                int(key): str(value)
                for key, value
                in config_labels.items()
            }

        # If config only says LABEL_0, LABEL_1...
        # use the mapping produced by train_model.py.
        if (
            not _MODEL_LABELS
            or all(
                str(value)
                .upper()
                .startswith("LABEL_")
                for value
                in _MODEL_LABELS.values()
            )
        ):

            mapped = load_label_mapping()

            if mapped:
                _MODEL_LABELS = mapped

        print(
            "[ResQ-Flow] Semantic model loaded."
        )

        if _MODEL_LABELS:

            print(
                "[ResQ-Flow] Model labels:"
            )

            print(
                _MODEL_LABELS
            )

        else:

            print(
                "[ResQ-Flow] WARNING: "
                "No label mapping found."
            )

        return True

    except Exception as error:

        _MODEL_ERROR = str(
            error
        )

        print(
            "[ResQ-Flow] Semantic model "
            "could not be loaded:"
        )

        print(
            _MODEL_ERROR
        )

        return False


# ============================================================
# 18. SEMANTIC CLASSIFICATION
# ============================================================

def semantic_classify(
    text: str,
) -> Dict[str, Any]:

    if not text:

        return {
            "available": False,
            "label": None,
            "canonical_label": None,
            "confidence": 0.0,
            "accepted": False,
            "top_predictions": [],
            "error": "empty message",
        }

    if not load_semantic_model():

        return {
            "available": False,
            "label": None,
            "canonical_label": None,
            "confidence": 0.0,
            "accepted": False,
            "top_predictions": [],
            "error": _MODEL_ERROR,
        }

    try:

        encoded = _TOKENIZER(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_LENGTH,
        )

        with torch.no_grad():

            outputs = _MODEL(
                **encoded
            )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1,
        )[0]

        top_k = min(
            5,
            len(probabilities),
        )

        top_values, top_indices = torch.topk(
            probabilities,
            k=top_k,
        )

        top_predictions = []

        for value, index in zip(
            top_values.tolist(),
            top_indices.tolist(),
        ):

            class_id = int(
                index
            )

            raw_label = None

            if _MODEL_LABELS:

                raw_label = _MODEL_LABELS.get(
                    class_id
                )

            canonical = normalize_model_label(
                raw_label
            )

            top_predictions.append(
                {
                    "class_id": class_id,
                    "label": raw_label,
                    "canonical_label": canonical,
                    "confidence": round(
                        float(value),
                        4,
                    ),
                }
            )

        best = top_predictions[0]

        confidence = float(
            best["confidence"]
        )

        accepted = (
            best["canonical_label"]
            is not None
            and confidence
            >= MODEL_CONFIDENCE_THRESHOLD
        )

        return {
            "available": True,
            "label": best["label"],
            "canonical_label": (
                best["canonical_label"]
                if accepted
                else None
            ),
            "raw_label": best["label"],
            "confidence": round(
                confidence,
                4,
            ),
            "accepted": accepted,
            "top_predictions": top_predictions,
            "error": None,
        }

    except Exception as error:

        return {
            "available": False,
            "label": None,
            "canonical_label": None,
            "confidence": 0.0,
            "accepted": False,
            "top_predictions": [],
            "error": str(error),
        }


# ============================================================
# 19. DISASTER FUSION
# ============================================================

def choose_disaster(
    semantic: Dict[str, Any],
    rule_hints: List[str],
) -> Dict[str, Any]:

    semantic_label = semantic.get(
        "canonical_label"
    )

    semantic_confidence = float(
        semantic.get(
            "confidence",
            0.0,
        )
    )

    # --------------------------------------------------------
    # Strong semantic model prediction.
    # --------------------------------------------------------

    if (
        semantic_label is not None
        and semantic_confidence
        >= MODEL_CONFIDENCE_THRESHOLD
    ):

        return {
            "primary": semantic_label,
            "confidence": semantic_confidence,
            "source": "semantic_model",
            "rule_hints": rule_hints,
        }

    # --------------------------------------------------------
    # If the model is uncertain but rules find a meaningful
    # hazard, use the safety/rule layer.
    #
    # This prevents:
    #
    # "fire" 0.15
    #
    # from being treated as a confident semantic answer.
    # --------------------------------------------------------

    if rule_hints:

        return {
            "primary": rule_hints[0],
            "confidence": None,
            "source": "safety_fallback",
            "rule_hints": rule_hints,
        }

    # --------------------------------------------------------
    # Nothing reliable.
    # --------------------------------------------------------

    return {
        "primary": None,
        "confidence": semantic_confidence,
        "source": "unknown",
        "rule_hints": [],
    }


# ============================================================
# 20. IMMEDIATE DANGER
# ============================================================

def determine_immediate_danger(
    text: str,
    context: Dict[str, bool],
    safety_signals: List[str],
    information: Dict[str, Any],
) -> bool:

    # Hypothetical questions should not automatically
    # become active emergencies.
    #
    # Example:
    # "What should I do if there is an earthquake?"
    #
    if (
        context["hypothetical"]
        and not context["direct_emergency_request"]
    ):
        return False

    # Current critical safety signals.
    if safety_signals:
        return True

    # Breathing difficulty.
    if information[
        "breathing_problem"
    ] is True:

        return True

    # Trapped.
    if information[
        "trapped"
    ] is True:

        return True

    return False


# ============================================================
# 21. EMERGENCY DETECTION
# ============================================================

def determine_emergency(
    context: Dict[str, bool],
    disaster: Dict[str, Any],
    immediate_danger: bool,
    information: Dict[str, Any],
) -> bool:

    # Active life-threatening situation.
    if immediate_danger:
        return True

    # Hypothetical question.
    if context["hypothetical"]:
        return False

    # Past event is not necessarily an active emergency.
    if (
        context["past_event"]
        and not context["current_event"]
        and not context["direct_emergency_request"]
    ):

        return False

    # Explicit emergency request.
    if context[
        "direct_emergency_request"
    ]:
        return True

    # Medical emergency.
    if information[
        "medical_emergency"
    ] is True:

        return True

    # Reliable disaster.
    if disaster[
        "primary"
    ] is not None:

        return True

    return False


# ============================================================
# 22. URGENCY ENGINE
# ============================================================
#
# IMPORTANT CHANGE:
#
# We DO NOT give +10 merely because multiple hazards
# were detected.
#
# Urgency is based on:
#
#   immediate danger
#   breathing
#   trapped
#   severe medical condition
#   dangerous water/fire/collapse
#   vulnerable people
#   current event
#   disaster type
#   number of people
#
# Hypothetical messages = 0.
#
# Past events = greatly reduced unless they indicate
# an ongoing condition.
#
# ============================================================

def calculate_urgency(
    text: str,
    context: Dict[str, bool],
    disaster: Dict[str, Any],
    safety_signals: List[str],
    information: Dict[str, Any],
    immediate_danger: bool,
) -> int:

    # --------------------------------------------------------
    # Hypothetical = not an active rescue request.
    # --------------------------------------------------------

    if (
        context["hypothetical"]
        and not context["direct_emergency_request"]
    ):
        return 0

    score = 0

    # --------------------------------------------------------
    # ACTIVE CURRENT EVENT
    # --------------------------------------------------------

    if context["current_event"]:
        score += 10

    # --------------------------------------------------------
    # DIRECT SOS / HELP
    # --------------------------------------------------------

    if context[
        "direct_emergency_request"
    ]:
        score += 25

    # --------------------------------------------------------
    # IMMEDIATE DANGER
    # --------------------------------------------------------

    if immediate_danger:
        score += 35

    # --------------------------------------------------------
    # CRITICAL SAFETY CONDITIONS
    # --------------------------------------------------------

    if (
        "breathing_difficulty"
        in safety_signals
    ):
        score += 25

    if (
        "trapped_or_unable_to_escape"
        in safety_signals
    ):
        score += 20

    if (
        "immediate_water_danger"
        in safety_signals
    ):
        score += 25

    if (
        "immediate_fire_danger"
        in safety_signals
    ):
        score += 25

    if (
        "structural_danger"
        in safety_signals
    ):
        score += 25

    if (
        "critical_medical_condition"
        in safety_signals
    ):
        score += 30

    if (
        "chemical_exposure"
        in safety_signals
    ):
        score += 20

    # --------------------------------------------------------
    # VICTIM CONDITIONS
    # --------------------------------------------------------

    if information[
        "medical_emergency"
    ] is True:
        score += 15

    if information[
        "mobility_issue"
    ] is True:
        score += 10

    if information[
        "elderly_present"
    ] is True:
        score += 8

    if information[
        "children_present"
    ] is True:
        score += 8

    # --------------------------------------------------------
    # PEOPLE COUNT
    # --------------------------------------------------------

    people = information[
        "people"
    ]

    if people is not None:

        if people >= 10:
            score += 15

        elif people >= 5:
            score += 10

        elif people >= 2:
            score += 5

    # --------------------------------------------------------
    # DISASTER TYPE
    # --------------------------------------------------------

    disaster_type = disaster[
        "primary"
    ]

    high_risk_disasters = {
        "fire",
        "wildfire",
        "flood",
        "tsunami",
        "earthquake",
        "tornado",
        "cyclone",
        "landslide",
        "avalanche",
        "volcanic_eruption",
        "chemical_gas",
        "structural_collapse",
        "transport_accident",
        "industrial_accident",
    }

    moderate_risk_disasters = {
        "storm",
        "lightning",
        "heatwave",
        "extreme_cold",
    }

    if disaster_type in high_risk_disasters:
        score += 15

    elif disaster_type in moderate_risk_disasters:
        score += 8

    # --------------------------------------------------------
    # PAST EVENT
    #
    # Reduce urgency if clearly historical.
    # --------------------------------------------------------

    if (
        context["past_event"]
        and not context["current_event"]
        and not context["direct_emergency_request"]
    ):

        score = min(
            score,
            15,
        )

    # --------------------------------------------------------
    # FINAL RANGE
    # --------------------------------------------------------

    return max(
        0,
        min(
            int(score),
            100,
        ),
    )


# ============================================================
# 23. URGENCY LEVEL
# ============================================================

def urgency_level(
    score: int,
) -> str:

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MODERATE"

    if score > 0:
        return "LOW"

    return "NONE"


# ============================================================
# 24. MAIN ANALYSIS
# ============================================================

def analyze_message(
    message: str,
) -> Dict[str, Any]:

    cleaned = clean_text(
        message
    )

    # --------------------------------------------------------
    # Empty input.
    # --------------------------------------------------------

    if not cleaned:

        return {
            "original_message": message,
            "cleaned_message": "",
            "emergency_detected": False,
            "disaster": {
                "primary": None,
                "confidence": 0.0,
                "source": "unknown",
                "rule_hints": [],
            },
            "people": None,
            "elderly_present": None,
            "children_present": None,
            "medical_emergency": None,
            "breathing_problem": None,
            "mobility_issue": None,
            "trapped": None,
            "immediate_danger": False,
            "urgency_score": 0,
            "urgency_level": "NONE",
            "context": {
                "current_event": False,
                "past_event": False,
                "hypothetical": False,
                "direct_emergency_request": False,
            },
            "safety_signals": [],
            "model": {
                "available": False,
                "error": "empty message",
            },
        }

    # --------------------------------------------------------
    # Context.
    # --------------------------------------------------------

    context = detect_context(
        cleaned
    )

    # --------------------------------------------------------
    # Victim information.
    # --------------------------------------------------------

    information = extract_information(
        cleaned
    )

    # --------------------------------------------------------
    # Disaster hints.
    # --------------------------------------------------------

    rule_hints = get_rule_hints(
        cleaned
    )

    # --------------------------------------------------------
    # Safety signals.
    # --------------------------------------------------------

    safety_signals = get_safety_signals(
        cleaned
    )

    # --------------------------------------------------------
    # Semantic model.
    # --------------------------------------------------------

    semantic = semantic_classify(
        cleaned
    )

    # --------------------------------------------------------
    # Combine model + safety layer.
    # --------------------------------------------------------

    disaster = choose_disaster(
        semantic,
        rule_hints,
    )

    # --------------------------------------------------------
    # Immediate danger.
    # --------------------------------------------------------

    immediate_danger = (
        determine_immediate_danger(
            cleaned,
            context,
            safety_signals,
            information,
        )
    )

    # --------------------------------------------------------
    # Emergency.
    # --------------------------------------------------------

    emergency_detected = (
        determine_emergency(
            context,
            disaster,
            immediate_danger,
            information,
        )
    )

    # --------------------------------------------------------
    # Urgency.
    # --------------------------------------------------------

    urgency_score = (
        calculate_urgency(
            cleaned,
            context,
            disaster,
            safety_signals,
            information,
            immediate_danger,
        )
    )

    level = urgency_level(
        urgency_score
    )

    # --------------------------------------------------------
    # Final structured packet.
    # --------------------------------------------------------

    return {

        "original_message":
            message,

        "cleaned_message":
            cleaned,

        "emergency_detected":
            emergency_detected,

        "disaster":
            disaster,

        "people":
            information[
                "people"
            ],

        "elderly_present":
            information[
                "elderly_present"
            ],

        "children_present":
            information[
                "children_present"
            ],

        "medical_emergency":
            information[
                "medical_emergency"
            ],

        "breathing_problem":
            information[
                "breathing_problem"
            ],

        "mobility_issue":
            information[
                "mobility_issue"
            ],

        "trapped":
            information[
                "trapped"
            ],

        "immediate_danger":
            immediate_danger,

        "urgency_score":
            urgency_score,

        "urgency_level":
            level,

        "context":
            context,

        "safety_signals":
            safety_signals,

        "model":
            semantic,
    }


# ============================================================
# 25. TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("             RESQ-FLOW AI MESSAGE ENGINE")
    print("=" * 70)

    print()
    print("Model path:")
    print(MODEL_PATH)
    print()

    message = input(
        "Enter emergency message: "
    )

    result = analyze_message(
        message
    )

    print()
    print("-" * 70)
    print("ANALYSIS RESULT")
    print("-" * 70)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print("-" * 70)