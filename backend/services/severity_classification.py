# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI SEVERITY CLASSIFICATION
# ============================================================
#
# Classifies the severity of any user-defined emergency.
#
# Pipeline:
#
# User message
#      ↓
# preprocessing.py
#      ↓
# AI zero-shot classification
#      ↓
# Severity + confidence
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

severity_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)


# ------------------------------------------------------------
# SEVERITY LEVELS
# ------------------------------------------------------------

SEVERITY_LEVELS = [
    "critical emergency requiring immediate rescue",
    "high severity emergency requiring urgent assistance",
    "moderate emergency requiring assistance",
    "low severity emergency with limited immediate danger"
]


# ------------------------------------------------------------
# CLASSIFY SEVERITY
# ------------------------------------------------------------

def classify_severity(message):

    if not message or not message.strip():
        raise ValueError(
            "Emergency message cannot be empty."
        )

    # Preprocess user message
    cleaned_message = preprocess_text(message)

    # Send cleaned message to AI model
    result = severity_classifier(
        cleaned_message,
        candidate_labels=SEVERITY_LEVELS,
        multi_label=False
    )

    severity_description = result["labels"][0]

    confidence = result["scores"][0] * 100

    # Convert AI label into simple severity level

    if severity_description.startswith("critical"):

        severity = "Critical"

    elif severity_description.startswith("high"):

        severity = "High"

    elif severity_description.startswith("moderate"):

        severity = "Moderate"

    else:

        severity = "Low"

    return {
        "original_message": message,
        "processed_message": cleaned_message,
        "severity": severity,
        "confidence": round(confidence, 2)
    }


# ------------------------------------------------------------
# TEST THE CLASSIFIER
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n==========================================")
    print("        RESQ-FLOW")
    print("    AI Severity Classification")
    print("==========================================")

    print("\nEnter any emergency description.")
    print("The description can be completely unique.")
    print("Type 'exit' to stop.\n")

    while True:

        message = input("Emergency: ")

        if message.strip().lower() == "exit":

            print("\nSeverity classifier stopped.")

            break

        try:

            result = classify_severity(message)

            print("\nAI RESULT")
            print("----------------------------")

            print(
                "Processed Message:",
                result["processed_message"]
            )

            print(
                "Severity:",
                result["severity"]
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