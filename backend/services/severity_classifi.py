# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI SEVERITY CLASSIFICATION
# ============================================================
#
# This module analyzes a user's unique emergency description
# and estimates the severity of the situation.
#
# No predefined emergency sentences are used.
#
# Severity levels:
#   Critical
#   High
#   Moderate
#   Low
#
# ============================================================

from transformers import pipeline


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

    result = severity_classifier(
        message,
        candidate_labels=SEVERITY_LEVELS,
        multi_label=False
    )

    severity_description = result["labels"][0]

    confidence = result["scores"][0] * 100


    # Convert model description into a simple
    # severity level for the rest of ResQ-Flow.

    if severity_description.startswith("critical"):
        severity = "Critical"

    elif severity_description.startswith("high"):
        severity = "High"

    elif severity_description.startswith("moderate"):
        severity = "Moderate"

    else:
        severity = "Low"


    return {
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

    print("\nEnter your emergency description.")
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
                "Severity   :",
                result["severity"]
            )

            print(
                "Confidence :",
                str(result["confidence"]) + "%"
            )

            print("----------------------------")


        except ValueError as error:

            print(
                "\nError:",
                error
            )