# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI DISASTER CLASSIFICATION
# ============================================================
#
# Classifies any user-defined emergency message.
#
# Pipeline:
#
# User message
#      ↓
# preprocessing.py
#      ↓
# AI zero-shot classification
#      ↓
# Disaster type + confidence
#
# ============================================================

from transformers import pipeline

# ------------------------------------------------------------
# IMPORT PREPROCESSING MODULE
# ------------------------------------------------------------

try:
    from .preprocessing import preprocess_text
except ImportError:
    from preprocessing import preprocess_text


# ------------------------------------------------------------
# LOAD AI MODEL
# ------------------------------------------------------------

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


# ------------------------------------------------------------
# DISASTER CATEGORIES
# ------------------------------------------------------------

DISASTER_CATEGORIES = [
    "flood",
    "cyclone or storm",
    "fire",
    "earthquake",
    "landslide",
    "other"
]


# ------------------------------------------------------------
# CLASSIFY DISASTER
# ------------------------------------------------------------

def classify_disaster(message):

    if not message or not message.strip():
        raise ValueError(
            "Emergency message cannot be empty."
        )

    # Preprocess the user's message
    cleaned_message = preprocess_text(message)

    # Send cleaned message to AI model
    result = classifier(
        cleaned_message,
        candidate_labels=DISASTER_CATEGORIES,
        multi_label=False
    )

    disaster = result["labels"][0]

    confidence = result["scores"][0] * 100

    return {
        "original_message": message,
        "processed_message": cleaned_message,
        "disaster": disaster,
        "confidence": round(confidence, 2)
    }


# ------------------------------------------------------------
# TEST THE CLASSIFIER
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n==========================================")
    print("        RESQ-FLOW")
    print("   AI Disaster Classification")
    print("==========================================")

    print("\nEnter any emergency description.")
    print("The description can be completely unique.")
    print("Type 'exit' to stop.\n")

    while True:

        message = input("Emergency: ")

        if message.strip().lower() == "exit":

            print("\nClassifier stopped.")

            break

        try:

            result = classify_disaster(message)

            print("\nAI RESULT")
            print("----------------------------")

            print(
                "Processed Message:",
                result["processed_message"]
            )

            print(
                "Disaster:",
                result["disaster"]
            )

            print(
                "Confidence:",
                str(result["confidence"]) + "%"
            )

            print("----------------------------")

        except (ValueError, TypeError) as error:

            print(
                "\nError:",
                error
            )