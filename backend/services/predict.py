# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI PREDICTION PIPELINE
# ============================================================
#
# This file combines the AI modules into one prediction
# pipeline.
#
# User message
#       ↓
# Preprocessing
#       ↓
# Message Analysis
#       ↓
# Disaster Classification
#       ↓
# Severity Classification
#       ↓
# Combined AI Result
#
# ============================================================


# ------------------------------------------------------------
# IMPORT AI MODULES
# ------------------------------------------------------------

try:
    from .preprocessing import preprocess_text
    from .ai_message import analyze_message
    from .disaster_classification import classify_disaster
    from .severity_classification import classify_severity

except ImportError:
    from preprocessing import preprocess_text
    from ai_message import analyze_message
    from disaster_classification import classify_disaster
    from severity_classification import classify_severity


# ------------------------------------------------------------
# MAIN PREDICTION FUNCTION
# ------------------------------------------------------------

def predict_emergency(message):

    if not message or not message.strip():

        raise ValueError(
            "Emergency message cannot be empty."
        )

    # --------------------------------------------------------
    # STEP 1 - PREPROCESSING
    # --------------------------------------------------------

    processed_message = preprocess_text(
        message
    )


    # --------------------------------------------------------
    # STEP 2 - MESSAGE ANALYSIS
    # --------------------------------------------------------

    message_analysis = analyze_message(
        processed_message
    )


    # --------------------------------------------------------
    # STEP 3 - DISASTER CLASSIFICATION
    # --------------------------------------------------------

    disaster_result = classify_disaster(
        processed_message
    )


    # --------------------------------------------------------
    # STEP 4 - SEVERITY CLASSIFICATION
    # --------------------------------------------------------

    severity_result = classify_severity(
        processed_message
    )


    # --------------------------------------------------------
    # STEP 5 - COMBINE RESULTS
    # --------------------------------------------------------

    prediction = {

        "original_message": message,

        "processed_message": processed_message,

        "message_analysis": message_analysis,

        "disaster": disaster_result,

        "severity": severity_result

    }


    return prediction


# ------------------------------------------------------------
# DISPLAY RESULT
# ------------------------------------------------------------

def print_prediction(result):

    print("\n")
    print("=" * 60)
    print("              RESQ-FLOW AI RESULT")
    print("=" * 60)


    print("\nORIGINAL MESSAGE")
    print("----------------------------")

    print(
        result["original_message"]
    )


    print("\nPROCESSED MESSAGE")
    print("----------------------------")

    print(
        result["processed_message"]
    )


    print("\nMESSAGE ANALYSIS")
    print("----------------------------")

    analysis = result["message_analysis"]

    for key, value in analysis.items():

        print(
            f"{key}: {value}"
        )


    print("\nDISASTER CLASSIFICATION")
    print("----------------------------")

    disaster = result["disaster"]

    print(
        "Disaster   :",
        disaster.get("disaster")
    )

    print(
        "Confidence :",
        str(disaster.get("confidence")) + "%"
    )


    print("\nSEVERITY CLASSIFICATION")
    print("----------------------------")

    severity = result["severity"]

    print(
        "Severity   :",
        severity.get("severity")
    )

    print(
        "Confidence :",
        str(severity.get("confidence")) + "%"
    )


    print("\n")
    print("=" * 60)


# ------------------------------------------------------------
# TEST THE COMPLETE PIPELINE
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n==========================================")
    print("             RESQ-FLOW")
    print("         AI PREDICTION PIPELINE")
    print("==========================================")

    print(
        "\nEnter any emergency description."
    )

    print(
        "The message can be completely unique."
    )

    print(
        "Type 'exit' to stop.\n"
    )


    while True:

        message = input(
            "Emergency: "
        )


        if message.strip().lower() == "exit":

            print(
                "\nPrediction pipeline stopped."
            )

            break


        try:

            result = predict_emergency(
                message
            )

            print_prediction(
                result
            )


        except (ValueError, TypeError) as error:

            print(
                "\nError:",
                error
            )

        except Exception as error:

            print(
                "\nUnexpected error:",
                error
            )