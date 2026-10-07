# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI MESSAGE ANALYSIS
# ============================================================
#
# Purpose:
# Convert an unstructured emergency message into
# structured emergency information.
#
# Example:
#
# Input:
# "Water has entered our house. My grandmother cannot walk.
#  There are 5 people inside and one has breathing difficulty."
#
# Output:
# {
#     "people": 5,
#     "elderly_present": True,
#     "mobility_issue": True,
#     "medical_emergency": True,
#     "breathing_problem": True,
#     "children_present": False,
#     "trapped": False
# }
#
# ============================================================

import re


# ============================================================
# KEYWORD GROUPS
# ============================================================

# Medical-related words
MEDICAL_KEYWORDS = [
    "medical",
    "injured",
    "injury",
    "hurt",
    "pain",
    "bleeding",
    "blood",
    "unconscious",
    "collapsed",
    "fainted",
    "faint",
    "sick",
    "ill",
    "ambulance",
    "hospital",
    "breathing",
    "breath",
    "breathe",
]


# Specific breathing-related words
BREATHING_KEYWORDS = [
    "breathing difficulty",
    "difficulty breathing",
    "trouble breathing",
    "cannot breathe",
    "can't breathe",
    "unable to breathe",
    "shortness of breath",
    "breathing problem",
    "not breathing",
]


# Elderly-related words
ELDERLY_KEYWORDS = [
    "elderly",
    "old person",
    "old man",
    "old woman",
    "grandmother",
    "grandfather",
    "grandma",
    "grandpa",
    "senior citizen",
    "senior",
]


# Children-related words
CHILD_KEYWORDS = [
    "child",
    "children",
    "kid",
    "kids",
    "baby",
    "infant",
    "toddler",
]


# Mobility-related words
MOBILITY_KEYWORDS = [
    "cannot walk",
    "can't walk",
    "unable to walk",
    "cannot move",
    "can't move",
    "unable to move",
    "wheelchair",
    "bedridden",
    "mobility problem",
    "mobility issue",
    "difficulty walking",
]


# Trapped-related words
TRAPPED_KEYWORDS = [
    "trapped",
    "stuck",
    "cannot escape",
    "can't escape",
    "unable to escape",
    "cannot leave",
    "can't leave",
    "unable to leave",
    "locked inside",
    "blocked",
]


# Immediate danger-related words
DANGER_KEYWORDS = [
    "danger",
    "dangerous",
    "critical",
    "emergency",
    "urgent",
    "immediately",
    "help immediately",
    "save us",
    "rescue us",
]


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(message):
    """
    Cleans the incoming emergency message.

    Converts:
        "WATER!!! has entered   our house"

    into:
        "water has entered our house"
    """

    message = message.lower()

    # Remove unnecessary special characters
    message = re.sub(
        r"[^a-z0-9\s']",
        " ",
        message
    )

    # Remove multiple spaces
    message = re.sub(
        r"\s+",
        " ",
        message
    )

    return message.strip()


# ============================================================
# KEYWORD DETECTION
# ============================================================

def contains_keyword(text, keywords):
    """
    Checks whether any keyword from a list
    appears in the message.
    """

    for keyword in keywords:

        if keyword in text:
            return True

    return False


# ============================================================
# PEOPLE COUNT EXTRACTION
# ============================================================

def extract_people_count(text):
    """
    Attempts to find the number of people
    mentioned in the emergency message.

    Examples:

        "There are 5 people"
        -> 5

        "We are 4 people"
        -> 4

        "There are 3 of us"
        -> 3
    """

    patterns = [

        r"(\d+)\s+people",

        r"(\d+)\s+persons",

        r"(\d+)\s+of\s+us",

        r"we\s+are\s+(\d+)",

        r"there\s+are\s+(\d+)",

        r"(\d+)\s+people\s+inside",

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return int(
                match.group(1)
            )


    # If no number is found
    return None


# ============================================================
# EXTRACT AGE GROUP INFORMATION
# ============================================================

def detect_people_categories(text):
    """
    Detects whether children or elderly people
    are mentioned.
    """

    elderly_present = contains_keyword(
        text,
        ELDERLY_KEYWORDS
    )

    children_present = contains_keyword(
        text,
        CHILD_KEYWORDS
    )

    return {
        "elderly_present": elderly_present,
        "children_present": children_present
    }


# ============================================================
# EXTRACT MEDICAL INFORMATION
# ============================================================

def detect_medical_information(text):
    """
    Detects medical emergency indicators.
    """

    medical_emergency = contains_keyword(
        text,
        MEDICAL_KEYWORDS
    )

    breathing_problem = contains_keyword(
        text,
        BREATHING_KEYWORDS
    )

    return {
        "medical_emergency": medical_emergency,
        "breathing_problem": breathing_problem
    }


# ============================================================
# EXTRACT MOBILITY INFORMATION
# ============================================================

def detect_mobility_issue(text):
    """
    Detects whether someone has difficulty
    walking or moving.
    """

    return contains_keyword(
        text,
        MOBILITY_KEYWORDS
    )


# ============================================================
# EXTRACT TRAPPED STATUS
# ============================================================

def detect_trapped_status(text):
    """
    Detects whether the victim or another person
    is trapped or unable to escape.
    """

    return contains_keyword(
        text,
        TRAPPED_KEYWORDS
    )


# ============================================================
# EXTRACT IMMEDIATE DANGER
# ============================================================

def detect_immediate_danger(text):
    """
    Detects words indicating immediate danger.
    """

    return contains_keyword(
        text,
        DANGER_KEYWORDS
    )


# ============================================================
# MAIN MESSAGE ANALYSIS FUNCTION
# ============================================================

def analyze_message(message):
    """
    Main AI message-analysis function.

    Input:
        Natural-language emergency message

    Output:
        Structured emergency information
    """

    # --------------------------------------------
    # Validate message
    # --------------------------------------------

    if not message or not message.strip():

        raise ValueError(
            "Emergency message cannot be empty."
        )


    # --------------------------------------------
    # Clean message
    # --------------------------------------------

    text = clean_text(message)


    # --------------------------------------------
    # Extract number of people
    # --------------------------------------------

    people = extract_people_count(text)


    # --------------------------------------------
    # Detect elderly / children
    # --------------------------------------------

    categories = detect_people_categories(
        text
    )


    # --------------------------------------------
    # Detect medical information
    # --------------------------------------------

    medical = detect_medical_information(
        text
    )


    # --------------------------------------------
    # Detect mobility
    # --------------------------------------------

    mobility_issue = detect_mobility_issue(
        text
    )


    # --------------------------------------------
    # Detect trapped condition
    # --------------------------------------------

    trapped = detect_trapped_status(
        text
    )


    # --------------------------------------------
    # Detect immediate danger
    # --------------------------------------------

    immediate_danger = detect_immediate_danger(
        text
    )


    # ========================================================
    # CREATE STRUCTURED RESULT
    # ========================================================

    result = {

        "original_message": message,

        "cleaned_message": text,

        "people": people,

        "elderly_present":
            categories["elderly_present"],

        "children_present":
            categories["children_present"],

        "medical_emergency":
            medical["medical_emergency"],

        "breathing_problem":
            medical["breathing_problem"],

        "mobility_issue":
            mobility_issue,

        "trapped":
            trapped,

        "immediate_danger":
            immediate_danger

    }


    return result


# ============================================================
# TEST SECTION
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       RESQ-FLOW AI MESSAGE ANALYSIS")
    print("========================================\n")


    message = input(
        "Enter emergency message:\n> "
    )


    try:

        result = analyze_message(
            message
        )


        print("\n----------------------------------------")
        print("AI MESSAGE ANALYSIS")
        print("----------------------------------------")


        for key, value in result.items():

            print(
                f"{key}: {value}"
            )


        print("----------------------------------------")


    except ValueError as error:

        print(
            f"\nError: {error}"
        )