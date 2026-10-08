# ============================================================
# RESQ-FLOW
# RESOURCE RECOMMENDATION ENGINE
# ============================================================
#
# AI Analysis
#      ↓
# Disaster Type + Urgency
#      ↓
# Resource Recommendation
#
# The engine recommends resources based on:
#   1. Disaster type
#   2. Severity / urgency
#
# ============================================================


def recommend_resources(disaster_type, severity):

    # Normalize AI output
    disaster = str(disaster_type).lower().strip()
    severity = str(severity).upper().strip()

    resources = []

    # ========================================================
    # FLOOD
    # ========================================================
    if disaster in ["flood", "flooding"]:

        resources = [
            "Water Rescue Team",
            "Rescue Boat",
            "Life Jackets",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # FIRE
    # ========================================================
    elif disaster in ["fire", "wildfire"]:

        resources = [
            "Fire Rescue Team",
            "Fire Extinguishing Equipment",
            "Ambulance",
            "Medical Team",
            "Evacuation Support"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Fire Team")

    # ========================================================
    # EARTHQUAKE
    # ========================================================
    elif disaster in ["earthquake"]:

        resources = [
            "Search and Rescue Team",
            "Heavy Rescue Equipment",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # LANDSLIDE
    # ========================================================
    elif disaster in ["landslide"]:

        resources = [
            "Search and Rescue Team",
            "Heavy Rescue Equipment",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # CYCLONE / STORM / TORNADO
    # ========================================================
    elif disaster in ["cyclone", "storm", "tornado"]:

        resources = [
            "Emergency Rescue Team",
            "Evacuation Support",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # TSUNAMI
    # ========================================================
    elif disaster in ["tsunami"]:

        resources = [
            "Water Rescue Team",
            "Rescue Boat",
            "Life Jackets",
            "Evacuation Support",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # CHEMICAL / GAS EMERGENCY
    # ========================================================
    elif disaster in [
        "chemical",
        "chemical_gas",
        "chemical gas",
        "gas",
        "gas leak"
    ]:

        resources = [
            "Hazmat Response Team",
            "Protective Equipment",
            "Evacuation Support",
            "Ambulance",
            "Medical Team"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Hazmat Team")

    # ========================================================
    # STRUCTURAL COLLAPSE
    # ========================================================
    elif disaster in [
        "structural collapse",
        "structural_collapse",
        "building collapse"
    ]:

        resources = [
            "Search and Rescue Team",
            "Heavy Rescue Equipment",
            "Ambulance",
            "Medical Team",
            "Emergency Shelter"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    # ========================================================
    # MEDICAL EMERGENCY
    # ========================================================
    elif disaster in [
        "medical",
        "medical emergency",
        "medical_emergency"
    ]:

        resources = [
            "Ambulance",
            "Emergency Medical Team",
            "First Aid Support"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Advanced Medical Response Team")

    # ========================================================
    # UNKNOWN / OTHER EMERGENCY
    # ========================================================
    else:

        resources = [
            "Emergency Rescue Team",
            "Ambulance",
            "Medical Team"
        ]

        if severity == "CRITICAL":
            resources.insert(0, "Rapid Response Rescue Team")

    return resources


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = recommend_resources("Flood", "CRITICAL")

    print("Recommended Resources:")

    for resource in result:
        print("-", resource)