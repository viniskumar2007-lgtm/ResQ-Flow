"""
ResQ-Flow Data Models

Defines the common data structures used by:
    - AI
    - Emergency processing
    - Mesh networking
    - Rescue dashboard
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid


# ============================================================
# HELPER
# ============================================================

def current_timestamp() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


# ============================================================
# LOCATION
# ============================================================

@dataclass
class Location:
    """
    Victim's emergency location.
    """

    latitude: float
    longitude: float

    accuracy: Optional[float] = None

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
        }


# ============================================================
# AI ANALYSIS
# ============================================================

@dataclass
class AIAnalysis:
    """
    Result produced by the AI system.
    """

    disaster_type: str

    severity: str

    confidence: float

    priority: int

    people_at_risk: bool = False

    medical_help_required: bool = False

    explanation: Optional[str] = None

    def to_dict(self):
        return {
            "disaster_type": self.disaster_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "priority": self.priority,
            "people_at_risk": self.people_at_risk,
            "medical_help_required": self.medical_help_required,
            "explanation": self.explanation,
        }


# ============================================================
# EMERGENCY REPORT
# ============================================================

@dataclass
class EmergencyReport:
    """
    Represents an emergency submitted by a victim.
    """

    message: str

    location: Location

    victim_id: Optional[str] = None

    emergency_id: str = field(
        default_factory=generate_id
    )

    created_at: str = field(
        default_factory=current_timestamp
    )

    ai_analysis: Optional[AIAnalysis] = None

    status: str = "created"

    def to_dict(self):

        return {
            "emergency_id": self.emergency_id,

            "victim_id": self.victim_id,

            "message": self.message,

            "location": self.location.to_dict(),

            "created_at": self.created_at,

            "ai_analysis": (
                self.ai_analysis.to_dict()
                if self.ai_analysis
                else None
            ),

            "status": self.status,
        }


# ============================================================
# MESH DEVICE
# ============================================================

@dataclass
class MeshDevice:
    """
    Represents a device participating in ResQ-Flow mesh.

    Roles:
        victim
        relay
        rescue
    """

    role: str

    device_id: str = field(
        default_factory=generate_id
    )

    device_name: Optional[str] = None

    network_id: str = "RESQ_FLOW"

    is_online: bool = True

    last_seen: str = field(
        default_factory=current_timestamp
    )

    def __post_init__(self):

        self.role = self.role.lower()

        valid_roles = {
            "victim",
            "relay",
            "rescue",
        }

        if self.role not in valid_roles:

            raise ValueError(
                f"Invalid device role: {self.role}. "
                f"Use victim, relay, or rescue."
            )

        if not self.device_name:

            self.device_name = (
                f"ResQ-{self.role}-"
                f"{self.device_id[:6]}"
            )

    def to_dict(self):

        return {
            "device_id": self.device_id,

            "device_name": self.device_name,

            "role": self.role,

            "network_id": self.network_id,

            "is_online": self.is_online,

            "last_seen": self.last_seen,
        }


# ============================================================
# MESH PACKET
# ============================================================

@dataclass
class MeshPacket:
    """
    Emergency packet transmitted through the mesh network.
    """

    emergency_id: str

    source_device_id: str

    source_role: str

    current_device_id: str

    hop_count: int = 0

    max_hops: int = 10

    status: str = "created"

    packet_id: str = field(
        default_factory=generate_id
    )

    created_at: str = field(
        default_factory=current_timestamp
    )

    next_device_id: Optional[str] = None

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {
            "packet_id": self.packet_id,

            "emergency_id": self.emergency_id,

            "source_device_id": self.source_device_id,

            "source_role": self.source_role,

            "current_device_id": self.current_device_id,

            "next_device_id": self.next_device_id,

            "hop_count": self.hop_count,

            "max_hops": self.max_hops,

            "status": self.status,

            "created_at": self.created_at,

            "payload": self.payload,
        }


# ============================================================
# RESCUE RESPONSE
# ============================================================

@dataclass
class RescueResponse:
    """
    Response/action from the rescue team.
    """

    emergency_id: str

    rescue_device_id: str

    action: str

    message: Optional[str] = None

    response_id: str = field(
        default_factory=generate_id
    )

    created_at: str = field(
        default_factory=current_timestamp
    )

    def to_dict(self):

        return {
            "response_id": self.response_id,

            "emergency_id": self.emergency_id,

            "rescue_device_id": self.rescue_device_id,

            "action": self.action,

            "message": self.message,

            "created_at": self.created_at,
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n=== RESQ-FLOW MODELS TEST ===")

    # Create location
    location = Location(
        latitude=13.0827,
        longitude=80.2707,
        accuracy=10.0,
    )

    # Create AI result
    ai_result = AIAnalysis(

        disaster_type="flood",

        severity="critical",

        confidence=0.94,

        priority=95,

        people_at_risk=True,

        medical_help_required=False,

        explanation=(
            "The message indicates "
            "rapidly rising flood water "
            "and trapped people."
        ),
    )

    # Create emergency
    emergency = EmergencyReport(

        message=(
            "Water has entered my house "
            "and people are trapped."
        ),

        location=location,

        victim_id="victim_001",

        ai_analysis=ai_result,
    )

    print("\nEmergency:")
    print(emergency.to_dict())

    # Create devices
    victim_device = MeshDevice(
        role="victim",
        device_name="Victim Phone",
    )

    relay_device = MeshDevice(
        role="relay",
        device_name="Nearby Relay",
    )

    rescue_device = MeshDevice(
        role="rescue",
        device_name="Rescue Team Device",
    )

    print("\nVictim Device:")
    print(victim_device.to_dict())

    print("\nRelay Device:")
    print(relay_device.to_dict())

    print("\nRescue Device:")
    print(rescue_device.to_dict())

    # Create mesh packet
    packet = MeshPacket(

        emergency_id=emergency.emergency_id,

        source_device_id=victim_device.device_id,

        source_role=victim_device.role,

        current_device_id=victim_device.device_id,

        payload={
            "message": emergency.message,

            "location": location.to_dict(),

            "ai_analysis": ai_result.to_dict(),
        },
    )

    print("\nMesh Packet:")
    print(packet.to_dict())