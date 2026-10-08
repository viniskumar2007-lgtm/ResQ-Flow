def calculate_priority(
    ai_analysis: dict,
    message: str = ""
):
    score = 0

    # AI-derived urgency
    urgency_score = ai_analysis.get("urgency_score", 0)

    if isinstance(urgency_score, (int, float)):
        score += min(urgency_score * 0.4, 40)

    # Critical danger signals
    if ai_analysis.get("immediate_danger") is True:
        score += 20

    if ai_analysis.get("trapped") is True:
        score += 15

    if ai_analysis.get("breathing_problem") is True:
        score += 15

    if ai_analysis.get("medical_emergency") is True:
        score += 10

    if ai_analysis.get("elderly_present") is True:
        score += 5

    if ai_analysis.get("children_present") is True:
        score += 5

    # Number of people
    people_count = ai_analysis.get("people", 0)

    if isinstance(people_count, int):
        if people_count >= 10:
            score += 10
        elif people_count >= 5:
            score += 8
        elif people_count >= 2:
            score += 5
        elif people_count == 1:
            score += 2

    # Keep score within 0-100
    score = min(round(score), 100)

    # Priority level
    if score >= 80:
        priority_level = "CRITICAL"
    elif score >= 60:
        priority_level = "HIGH"
    elif score >= 40:
        priority_level = "MODERATE"
    else:
        priority_level = "LOW"

    return {
        "priority_score": score,
        "priority_level": priority_level
    }