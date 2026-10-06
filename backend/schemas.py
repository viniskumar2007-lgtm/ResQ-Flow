from pydantic import BaseModel
from typing import Optional


class SOSCreate(BaseModel):
    name: str
    message: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    people_count: int = 1

    disaster_type: Optional[str] = None
    severity: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    status: str

class ResourceCreate(BaseModel):
    name: str
    type: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    available: bool = True

    contact: Optional[str] = None

class IncidentAnalysis(BaseModel):
    disaster_type: Optional[str] = None
    severity: Optional[str] = None
    priority_score: int = 0
    ai_confidence: Optional[float] = None
class ResourceRecommendationRequest(BaseModel):
    disaster_type: Optional[str] = None
    severity: Optional[str] = None
class SyncSOSRequest(BaseModel):
    local_id: str

    name: str
    message: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    people_count: int = 1

    disaster_type: Optional[str] = None
    severity: Optional[str] = None

    timestamp: Optional[str] = None
class LoginRequest(BaseModel):
    email: str
    password: str