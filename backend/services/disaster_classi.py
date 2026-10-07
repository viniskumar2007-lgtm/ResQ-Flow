# ============================================================
# RESQ-FLOW
# MEMBER 3 - DISASTER CLASSIFICATION
# ============================================================
#
# Classifies a user's emergency message into a disaster type.
#
# IMPORTANT:
# No predefined emergency sentences are used.
# The user can enter any unique emergency description.
#
# Model:
#   Zero-Shot Classification
#
# Categories:
#   Flood
#   Cyclone / Storm
#   Fire
#   Earthquake
#   Landslide
#   Other
#
# ============================================================

from transformers import pipeline


# ============================================================
# 1. LOAD AI MODEL
# ============================================================

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


# ============================================================
# 2. DISASTER CATEGORIES
# ============================================================

DISASTER_CATEGORIES = [
    "flood",
    "cyclone or storm",
    "fire",
    "earthquake",
    "landslide",
    "other"
]


# ============================================================
# 3. CLASSIFICATION FUNCTION
# ============================================================

def classify_disaster(message):

    if not message or not message.strip():
        raise ValueError(
            "Emergency message cannot be empty."
        )

    result = classifier(
        message,
        candidate_labels=DISASTER_CATEGORIES,
        multi_label=False
    )

    disaster = result["labels"][0]
    confidence = result["scores"][0] * 100

    return {
        "disaster": disaster,
        "confidence": round(confidence, 2)
    }


# ============================================================
# 4. DISPLAY RESULT
# ============================================================

def print_result(message):

    result = classify_disaster(message)

    print("\n" + "=" * 60)

    print("USER MESSAGE:")
    print(message)

    print("\nAI CLASSIFICATION:")

    print(
        "Disaster   :",
        result["disaster"]
    )

    print(
        "Confidence :",
        str(result["confidence"]) + "%"
    )

    print("=" * 60)


# ============================================================
# 5. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\nRESQ-FLOW")
    print("AI Disaster Classification")

    print(
        "\nEnter any emergency description."
    )

    print(
        "The message does not need to match a predefined statement."
    )

    print(
        "Type 'exit' to stop."
    )

    while True:

        message = input(
            "\nDescribe the emergency:\n> "
        )

        if message.lower().strip() == "exit":

            print(
                "\nClassification module stopped."
            )

            break

        try:

            print_result(message)

        except Exception as error:

            print(
                "\nError:",
                error
            )