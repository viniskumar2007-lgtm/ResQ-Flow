"""
ResQ-Flow Mesh Sync Service
---------------------------

Handles emergency packet routing between:

    VICTIM  ->  RELAY  ->  RELAY  ->  RESCUE

This file contains the routing/intelligence logic.
Actual Bluetooth / Nearby Connections transmission should
be handled by the mobile/network layer.

Device roles:
    victim
    relay
    rescue
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

NETWORK_ID = "RESQ_FLOW"

MAX_HOPS = 10

DEVICE_ROLES = {
    "victim",
    "relay",
    "rescue",
}


# ============================================================
# DEVICE CONFIGURATION
# ============================================================

class MeshDevice:
    """
    Represents one device participating in the ResQ-Flow network.
    """

    def __init__(
        self,
        role: str,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
    ):
        role = role.lower().strip()

        if role not in DEVICE_ROLES:
            raise ValueError(
                f"Invalid device role: {role}. "
                f"Use victim, relay, or rescue."
            )

        self.device_id = device_id or str(uuid.uuid4())
        self.device_name = device_name or f"ResQ-{role}-{self.device_id[:6]}"
        self.role = role
        self.network_id = NETWORK_ID

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "role": self.role,
            "network_id": self.network_id,
        }


# ============================================================
# PACKET STORAGE
# ============================================================

# Stores packet IDs that this device has already processed.
seen_packets = set()

# Stores the latest known status of packets.
packet_status = {}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_timestamp():
    """Return UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


# ============================================================
# CREATE EMERGENCY PACKET
# ============================================================

def create_emergency_packet(
    device: MeshDevice,
    message: str,
    disaster_type: str,
    severity: str,
    priority: int,
    location: Optional[dict] = None,
    analysis: Optional[dict] = None,
):
    """
    Create a new emergency packet.

    Only a VICTIM device should normally create a new
    emergency packet.
    """

    if device.role != "victim":
        raise PermissionError(
            "Only a victim device can create an emergency packet."
        )

    if not message or not message.strip():
        raise ValueError("Emergency message cannot be empty.")

    if not 0 <= priority <= 100:
        raise ValueError("Priority must be between 0 and 100.")

    packet_id = generate_id()

    packet = {
        "network_id": NETWORK_ID,

        "packet_id": packet_id,

        "source_device_id": device.device_id,

        "source_role": device.role,

        "created_at": get_timestamp(),

        # Current routing information
        "current_device_id": device.device_id,

        "hop_count": 0,

        "max_hops": MAX_HOPS,

        "status": "created",

        # Emergency information
        "message": message.strip(),

        "disaster_type": disaster_type,

        "severity": severity,

        "priority": priority,

        "location": location,

        # Output from AI analysis
        "analysis": analysis or {},
    }

    packet_status[packet_id] = {
        "status": "created",
        "current_device_id": device.device_id,
        "updated_at": get_timestamp(),
    }

    return packet


# ============================================================
# PACKET VALIDATION
# ============================================================

def validate_packet(packet):
    """
    Validate a packet before processing.
    """

    required_fields = [
        "network_id",
        "packet_id",
        "source_device_id",
        "source_role",
        "current_device_id",
        "hop_count",
        "max_hops",
    ]

    for field in required_fields:
        if field not in packet:
            return False, f"Missing field: {field}"

    if packet["network_id"] != NETWORK_ID:
        return False, "Packet belongs to another network."

    if packet["source_role"] not in DEVICE_ROLES:
        return False, "Invalid source role."

    if packet["hop_count"] > packet["max_hops"]:
        return False, "Maximum hop count exceeded."

    return True, "Packet valid"


# ============================================================
# RECEIVE PACKET
# ============================================================

def receive_packet(
    device: MeshDevice,
    packet: dict,
):
    """
    Process an incoming packet on a device.

    Victim:
        Normally does not receive forwarded packets.

    Relay:
        Receives and forwards packets.

    Rescue:
        Receives and delivers packets to the rescue team.
    """

    valid, reason = validate_packet(packet)

    if not valid:
        return {
            "success": False,
            "status": "rejected",
            "reason": reason,
        }

    packet_id = packet["packet_id"]

    # --------------------------------------------------------
    # Duplicate protection
    # --------------------------------------------------------

    if packet_id in seen_packets:
        return {
            "success": False,
            "status": "duplicate",
            "packet_id": packet_id,
            "message": "Packet already processed.",
        }

    # Mark packet as seen
    seen_packets.add(packet_id)

    # --------------------------------------------------------
    # Hop protection
    # --------------------------------------------------------

    if packet["hop_count"] >= packet["max_hops"]:
        packet_status[packet_id] = {
            "status": "expired",
            "current_device_id": device.device_id,
            "updated_at": get_timestamp(),
        }

        return {
            "success": False,
            "status": "expired",
            "packet_id": packet_id,
            "message": "Maximum number of hops reached.",
        }

    # --------------------------------------------------------
    # Update packet
    # --------------------------------------------------------

    packet["current_device_id"] = device.device_id
    packet["hop_count"] += 1

    # --------------------------------------------------------
    # RESCUE DEVICE
    # --------------------------------------------------------

    if device.role == "rescue":

        packet["status"] = "delivered_to_rescue"

        packet_status[packet_id] = {
            "status": "delivered_to_rescue",
            "current_device_id": device.device_id,
            "updated_at": get_timestamp(),
        }

        return {
            "success": True,
            "status": "delivered_to_rescue",
            "packet": packet,
        }

    # --------------------------------------------------------
    # RELAY DEVICE
    # --------------------------------------------------------

    if device.role == "relay":

        packet["status"] = "ready_for_relay"

        packet_status[packet_id] = {
            "status": "ready_for_relay",
            "current_device_id": device.device_id,
            "updated_at": get_timestamp(),
        }

        return {
            "success": True,
            "status": "ready_for_relay",
            "packet": packet,
        }

    # --------------------------------------------------------
    # VICTIM DEVICE
    # --------------------------------------------------------

    return {
        "success": False,
        "status": "ignored",
        "message": "Victim devices should not relay incoming packets.",
    }


# ============================================================
# FIND NEARBY RESQ-FLOW DEVICES
# ============================================================

def find_relay_nodes(
    nearby_devices: list,
    packet: dict,
):
    """
    Filter nearby devices that can participate in routing.

    Expected nearby device format:

    {
        "device_id": "...",
        "device_name": "...",
        "role": "relay",
        "network_id": "RESQ_FLOW"
    }
    """

    valid_nodes = []

    for node in nearby_devices:

        # Ignore devices from another network
        if node.get("network_id") != NETWORK_ID:
            continue

        # Ignore the device that already handled the packet
        if node.get("device_id") == packet.get("current_device_id"):
            continue

        # Only relay and rescue devices can receive forwarded packets
        if node.get("role") not in {"relay", "rescue"}:
            continue

        valid_nodes.append(node)

    return valid_nodes


# ============================================================
# SELECT BEST NEXT DEVICE
# ============================================================

def select_next_device(
    nearby_devices: list,
    packet: dict,
):
    """
    Select the next device.

    Priority:
        1. Rescue device
        2. Relay device

    Later you can improve this using:
        - signal strength
        - distance
        - battery
        - number of hops
        - rescue-team proximity
    """

    valid_nodes = find_relay_nodes(
        nearby_devices,
        packet,
    )

    if not valid_nodes:
        return None

    # Prefer rescue devices
    rescue_nodes = [
        node
        for node in valid_nodes
        if node.get("role") == "rescue"
    ]

    if rescue_nodes:
        return rescue_nodes[0]

    # Otherwise use relay
    relay_nodes = [
        node
        for node in valid_nodes
        if node.get("role") == "relay"
    ]

    if relay_nodes:
        return relay_nodes[0]

    return None


# ============================================================
# PREPARE PACKET FOR TRANSMISSION
# ============================================================

def prepare_for_transmission(
    packet: dict,
    target_device: dict,
):
    """
    Prepare packet metadata before sending it through
    Bluetooth / Nearby Connections / another transport.
    """

    packet_copy = packet.copy()

    packet_copy["next_device_id"] = target_device["device_id"]

    packet_copy["next_device_role"] = target_device["role"]

    packet_copy["status"] = "transmitting"

    packet_status[packet_copy["packet_id"]] = {
        "status": "transmitting",
        "current_device_id": packet_copy["current_device_id"],
        "next_device_id": target_device["device_id"],
        "updated_at": get_timestamp(),
    }

    return packet_copy


# ============================================================
# ROUTE PACKET
# ============================================================

def route_packet(
    packet: dict,
    current_device: MeshDevice,
    nearby_devices: list,
):
    """
    Decide where the packet should go next.
    """

    if current_device.role not in {"victim", "relay"}:
        return {
            "success": False,
            "status": "not_allowed",
            "message": "Only victim and relay devices route packets.",
        }

    # Find best next device
    next_device = select_next_device(
        nearby_devices,
        packet,
    )

    if not next_device:

        packet["status"] = "waiting_for_nearby_device"

        packet_status[packet["packet_id"]] = {
            "status": "waiting_for_nearby_device",
            "current_device_id": current_device.device_id,
            "updated_at": get_timestamp(),
        }

        return {
            "success": False,
            "status": "waiting_for_nearby_device",
            "packet": packet,
        }

    # Prepare packet
    outgoing_packet = prepare_for_transmission(
        packet,
        next_device,
    )

    return {
        "success": True,
        "status": "transmitting",
        "next_device": next_device,
        "packet": outgoing_packet,
    }


# ============================================================
# DELIVER TO RESCUE
# ============================================================

def deliver_to_rescue(
    device: MeshDevice,
    packet: dict,
):
    """
    Mark a packet as delivered when it reaches
    a rescue device.
    """

    if device.role != "rescue":
        raise PermissionError(
            "Only rescue devices can receive final emergency packets."
        )

    packet["current_device_id"] = device.device_id

    packet["status"] = "delivered_to_rescue"

    packet_status[packet["packet_id"]] = {
        "status": "delivered_to_rescue",
        "current_device_id": device.device_id,
        "updated_at": get_timestamp(),
    }

    return packet


# ============================================================
# PACKET STATUS
# ============================================================

def get_packet_status(packet_id: str):
    """
    Get current status of an emergency packet.
    """

    return packet_status.get(
        packet_id,
        {
            "status": "unknown",
        },
    )


# ============================================================
# MESH STATUS
# ============================================================

def get_mesh_status(device: MeshDevice):
    """
    Return information about the current device.
    """

    return {
        "network_id": NETWORK_ID,
        "device_id": device.device_id,
        "device_name": device.device_name,
        "role": device.role,
        "max_hops": MAX_HOPS,
        "packets_seen": len(seen_packets),
        "packets_tracked": len(packet_status),
    }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Create devices
    # --------------------------------------------------------

    victim = MeshDevice(
        role="victim",
        device_name="Victim Phone",
    )

    relay = MeshDevice(
        role="relay",
        device_name="Nearby Relay Phone",
    )

    rescue = MeshDevice(
        role="rescue",
        device_name="Rescue Team Device",
    )

    print("\n=== DEVICES ===")

    print(victim.to_dict())
    print(relay.to_dict())
    print(rescue.to_dict())

    # --------------------------------------------------------
    # Victim creates emergency
    # --------------------------------------------------------

    packet = create_emergency_packet(
        device=victim,

        message="There are people trapped inside a damaged building.",

        disaster_type="earthquake",

        severity="critical",

        priority=95,

        location={
            "lat": 13.0827,
            "lon": 80.2707,
        },

        analysis={
            "confidence": 0.94,
            "people_at_risk": True,
            "medical_help_required": True,
        },
    )

    print("\n=== EMERGENCY CREATED ===")
    print(packet)

    # --------------------------------------------------------
    # Victim finds nearby relay
    # --------------------------------------------------------

    nearby_devices = [
        relay.to_dict(),
    ]

    route_result = route_packet(
        packet,
        victim,
        nearby_devices,
    )

    print("\n=== VICTIM → RELAY ===")
    print(route_result)

    # --------------------------------------------------------
    # Relay receives packet
    # --------------------------------------------------------

    relay_result = receive_packet(
        relay,
        packet,
    )

    print("\n=== RELAY RECEIVED ===")
    print(relay_result)

    # --------------------------------------------------------
    # Relay finds rescue device
    # --------------------------------------------------------

    nearby_devices = [
        rescue.to_dict(),
    ]

    route_result = route_packet(
        packet,
        relay,
        nearby_devices,
    )

    print("\n=== RELAY → RESCUE ===")
    print(route_result)

    # --------------------------------------------------------
    # Rescue receives packet
    # --------------------------------------------------------

    rescue_result = receive_packet(
        rescue,
        packet,
    )

    print("\n=== RESCUE RECEIVED ===")
    print(rescue_result)

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print("\n=== FINAL STATUS ===")

    print(
        get_packet_status(
            packet["packet_id"]
        )
    )

    print("\n=== MESH STATUS ===")

    print(get_mesh_status(victim))