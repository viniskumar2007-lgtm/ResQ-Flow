def calculate_priority(people_count, injury, trapped, immediate_danger):
    score = 0

    if injury == "Severe":
        score += 40
    elif injury == "Moderate":
        score += 20

    if trapped:
        score += 30

    if people_count >= 5:
        score += 20
    elif people_count >= 2:
        score += 10

    if immediate_danger:
        score += 10

    if score >= 80:
        priority = "CRITICAL"
    elif score >= 60:
        priority = "HIGH"
    elif score >= 30:
        priority = "MODERATE"
    else:
        priority = "LOW"

    return {
        "score": score,
        "priority": priority
    }
result = calculate_priority(
    people_count=6,
    injury="Severe",
    trapped=True,
    immediate_danger=True
)

print(result)