# ============================================================
# RESQ-FLOW
# MEMBER 3 - AI PREDICTION PIPELINE
# ============================================================
#
# User message
#       ↓
# Preprocessing
#       ↓
# AI Message Analysis
#       ↓
# Urgency
#       ↓
# Priority
#       ↓
# Resource Recommendation
#
# ============================================================


try:
    from .preprocessing import preprocess_text
    from .ai_message import analyze_message
    from .priority_engine import calculate_priority
    from .resource_engine import recommend_resources

except ImportError:
    from preprocessing import preprocess_text
    from ai_message import analyze_message
    from priority_engine import calculate_priority
    from resource_engine import recommend_resources


def predict_emergency(message):

    if not message or not message.strip():
        raise ValueError("Emergency message cannot be empty.")

    # ========================================================
    # 1. PREPROCESS MESSAGE
    # ========================================================

    processed_message = preprocess_text(message)

    # ========================================================
    # 2. AI MESSAGE ANALYSIS
    # ========================================================

    message_analysis = analyze_message(processed_message)

    # ========================================================
    # 3. GET DISASTER INFORMATION
    # ========================================================

    disaster_result = message_analysis.get(
        "disaster",
        {}
    )

    if isinstance(disaster_result, dict):

        disaster_type = disaster_result.get(
            "primary",
            "other"
        )

        disaster_confidence = disaster_result.get(
            "confidence"
        )

    else:

        disaster_type = str(disaster_result)

        disaster_confidence = None

    # ========================================================
    # 4. GET AI URGENCY
    # ========================================================

    urgency_score = message_analysis.get(
        "urgency_score",
        0
    )

    urgency_level = message_analysis.get(
        "urgency_level",
        "NONE"
    )

    # ========================================================
    # 5. CALCULATE PRIORITY
    # ========================================================

    priority_result = calculate_priority(
        urgency_score
    )

    # ========================================================
    # 6. RECOMMEND RESOURCES
    # ========================================================

    resources = recommend_resources(
        disaster_type,
        urgency_level
    )

    # ========================================================
    # 7. COMBINED RESULT
    # ========================================================

    prediction = {

        "original_message": message,

        "processed_message": processed_message,

        "message_analysis": message_analysis,

        "disaster": {
            "primary": disaster_type,
            "confidence": disaster_confidence
        },

        "urgency_score": urgency_score,

        "urgency_level": urgency_level,

        "priority": priority_result,

        "resources": resources
    }

    return prediction


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = predict_emergency(
        "The water is entering my house and my grandmother is trapped upstairs"
    )

    print("\n===== RESQ-FLOW AI RESULT =====")

    print("\nDisaster:")
    print(result["disaster"])

    print("\nUrgency Score:")
    print(result["urgency_score"])

    print("\nUrgency Level:")
    print(result["urgency_level"])

    print("\nPriority:")
    print(result["priority"])

    print("\nRecommended Resources:")

    for resource in result["resources"]:
        print("-", resource)