def calculate_priority(
    people_count: int,
    severity: str | None,
    message: str
):
    score = 0

    # Number of people
    if people_count >= 10:
        score += 30
    elif people_count >= 5:
        score += 25
    elif people_count >= 2:
        score += 15
    else:
        score += 5

    # Severity
    if severity == "CRITICAL":
        score += 40
    elif severity == "HIGH":
        score += 30
    elif severity == "MODERATE":
        score += 20
    else:
        score += 10

    # Emergency keywords
    message_lower = message.lower()

    critical_keywords = [
        "severe injury",
        "serious injury",
        "trapped",
        "unconscious",
        "not breathing",
        "water increasing",
        "help immediately"
    ]

    for keyword in critical_keywords:
        if keyword in message_lower:
            score += 5

    # Maximum score = 100
    score = min(score, 100)

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