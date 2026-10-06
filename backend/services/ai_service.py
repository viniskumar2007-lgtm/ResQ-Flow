def analyze_emergency(message):
    message_lower = message.lower()

    disaster_type = "Unknown"
    injury = "None"
    trapped = False
    immediate_danger = False

    if "flood" in message_lower or "water" in message_lower:
        disaster_type = "Flood"

    elif "fire" in message_lower or "smoke" in message_lower:
        disaster_type = "Fire"

    elif "earthquake" in message_lower or "building collapsed" in message_lower:
        disaster_type = "Earthquake"

    if "severe injury" in message_lower or "serious injury" in message_lower:
        injury = "Severe"

    elif "injury" in message_lower:
        injury = "Moderate"

    if "trapped" in message_lower:
        trapped = True

    if "danger" in message_lower or "water level is increasing" in message_lower:
        immediate_danger = True

    return {
        "disaster_type": disaster_type,
        "injury": injury,
        "trapped": trapped,
        "immediate_danger": immediate_danger
    }