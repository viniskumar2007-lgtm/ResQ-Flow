from fastapi import FastAPI, HTTPException

from database import supabase_admin
from schemas import (
    SOSCreate,
    IncidentStatusUpdate,
    ResourceCreate,
    IncidentAnalysis,
    ResourceRecommendationRequest,
    SyncSOSRequest,
    LoginRequest
)


app = FastAPI(
    title="ResQ-Flow API",
    description="Emergency Response and Rescue Coordination API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "ResQ-Flow API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/sos")
def create_sos(sos: SOSCreate):

    try:
        incident_data = {
        "local_id": sos.local_id,
        "name": sos.name,
        "message": sos.message,
        "latitude": sos.latitude,
        "longitude": sos.longitude,
        "people_count": sos.people_count,
        "disaster_type": sos.disaster_type,
        "severity": sos.severity,
        "status": "NEW"
    }

        response = (
            supabase_admin
            .table("incidents")
            .insert(incident_data)
            .execute()
        )

        return {
            "success": True,
            "message": "SOS created successfully",
            "incident": response.data[0]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/api/incidents")
def get_incidents():

    try:
        response = (
            supabase_admin
            .table("incidents")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "success": True,
            "count": len(response.data),
            "incidents": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: int):

    try:
        response = (
            supabase_admin
            .table("incidents")
            .select("*")
            .eq("id", incident_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        return {
            "success": True,
            "incident": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.put("/api/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    status_update: IncidentStatusUpdate
):

    allowed_statuses = [
        "NEW",
        "ASSIGNED",
        "RESCUE_IN_PROGRESS",
        "RESCUED"
    ]

    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident status"
        )

    try:
        response = (
            supabase_admin
            .table("incidents")
            .update({
                "status": status_update.status
            })
            .eq("id", incident_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        return {
            "success": True,
            "message": "Incident status updated successfully",
            "incident": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/api/resources")
def create_resource(resource: ResourceCreate):

    allowed_types = [
        "AMBULANCE",
        "RESCUE_TEAM",
        "MEDICAL_TEAM",
        "SHELTER",
        "FOOD",
        "WATER"
    ]

    if resource.type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid resource type"
        )

    try:
        resource_data = {
            "name": resource.name,
            "type": resource.type,
            "latitude": resource.latitude,
            "longitude": resource.longitude,
            "available": resource.available,
            "contact": resource.contact
        }

        response = (
            supabase_admin
            .table("resources")
            .insert(resource_data)
            .execute()
        )

        return {
            "success": True,
            "message": "Resource created successfully",
            "resource": response.data[0]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/api/resources")
def get_resources():

    try:
        response = (
            supabase_admin
            .table("resources")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "success": True,
            "count": len(response.data),
            "resources": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.put("/api/incidents/{incident_id}/analyze")
def analyze_incident(
    incident_id: int,
    analysis: IncidentAnalysis
):

    try:
        response = (
            supabase_admin
            .table("incidents")
            .update({
                "disaster_type": analysis.disaster_type,
                "severity": analysis.severity,
                "priority_score": analysis.priority_score,
                "ai_confidence": analysis.ai_confidence
            })
            .eq("id", incident_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        return {
            "success": True,
            "message": "Incident analysis updated successfully",
            "incident": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
from services.resource_engine import recommend_resources


@app.post("/api/resources/recommend")
def recommend_incident_resources(
    request: ResourceRecommendationRequest
):

    try:
        recommendations = recommend_resources(
            request.disaster_type,
            request.severity
        )

        return {
            "success": True,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/api/sync")
def sync_offline_sos(sos: SyncSOSRequest):

    try:
        incident_data = {
            "name": sos.name,
            "message": sos.message,
            "latitude": sos.latitude,
            "longitude": sos.longitude,
            "people_count": sos.people_count,
            "disaster_type": sos.disaster_type,
            "severity": sos.severity,
            "status": "NEW"
        }

        response = (
            supabase_admin
            .table("incidents")
            .insert(incident_data)
            .execute()
        )

        return {
            "success": True,
            "message": "Offline SOS synchronized successfully",
            "local_id": sos.local_id,
            "incident": response.data[0]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/api/auth/login")
def login(login_data: LoginRequest):

    try:
        response = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })

        if not response.session:
            raise HTTPException(
                status_code=401,
                detail="Login failed"
            )

        return {
            "success": True,
            "message": "Login successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )