def recommend_resources(disaster_type, severity):
    resources = []

    if disaster_type == "Flood":
        resources = [
            "Rescue Team",
            "Ambulance",
            "Medical Team",
            "Shelter"
        ]

    elif disaster_type == "Fire":
        resources = [
            "Fire Rescue Team",
            "Ambulance",
            "Medical Team"
        ]

    elif disaster_type == "Earthquake":
        resources = [
            "Rescue Team",
            "Ambulance",
            "Medical Team",
            "Shelter"
        ]

    else:
        resources = [
            "Rescue Team"
        ]

    return resources
print(recommend_resources("Flood", "CRITICAL"))