from services.predict import predict_emergency
from services.resource_engine import recommend_resources

from fastapi import FastAPI, HTTPException, Depends
from auth import get_current_user

from database import supabase, supabase_admin
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
def create_sos(
    sos: SOSCreate,
    current_user=Depends(get_current_user)
):

    try:
        # ====================================================
        # 1. RUN AI ANALYSIS
        # ====================================================

        prediction = predict_emergency(sos.message)

        # Get disaster information from AI
        disaster_result = prediction.get("disaster", {})

        if isinstance(disaster_result, dict):
            disaster_type = disaster_result.get(
                "primary",
                "other"
            )

            ai_confidence = disaster_result.get(
                "confidence",
                0.0
            )

        else:
            disaster_type = str(disaster_result)
            ai_confidence = 0.0

        # Get urgency information from AI
        urgency_score = prediction.get(
            "urgency_score",
            0
        )

        urgency_level = prediction.get(
            "urgency_level",
            "NONE"
        )

        # ====================================================
        # 2. GET PRIORITY
        # ====================================================

        priority_result = prediction.get(
            "priority",
            {}
        )

        priority_score = priority_result.get(
            "urgency_score",
            urgency_score
        )

        priority_level = priority_result.get(
            "priority_level",
            urgency_level
        )

        # ====================================================
        # 3. GET RECOMMENDED RESOURCES
        # ====================================================

        resources = prediction.get(
            "resources",
            recommend_resources(
                disaster_type,
                urgency_level
            )
        )

        # ====================================================
        # 4. CREATE INCIDENT DATA
        # ====================================================

        incident_data = {
            "user_id": current_user.id,

            "name": sos.name,

            "message": sos.message,

            "latitude": sos.latitude,

            "longitude": sos.longitude,

            "people_count": sos.people_count,

            "disaster_type": disaster_type,

            "severity": urgency_level,

            "priority_score": priority_score,

            "ai_confidence": ai_confidence,

            "status": "NEW"
        }

        # ====================================================
        # 5. SAVE TO SUPABASE
        # ====================================================

        response = (
            supabase_admin
            .table("incidents")
            .insert(incident_data)
            .execute()
        )

        # ====================================================
        # 6. RETURN COMPLETE RESULT
        # ====================================================

        return {
            "success": True,

            "message": "SOS analyzed and created successfully",

            "incident": response.data[0],

            "ai_analysis": {
                "disaster_type": disaster_type,
                "confidence": ai_confidence,
                "urgency_score": urgency_score,
                "urgency_level": urgency_level
            },

            "priority": {
                "score": priority_score,
                "level": priority_level
            },

            "recommended_resources": resources
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    try:
        incident_data = {
            "user_id": current_user.id,
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
def get_incidents(
    current_user=Depends(get_current_user)
):
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
def get_incident(
    incident_id: int,
    current_user=Depends(get_current_user)
):

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
    status_update: IncidentStatusUpdate,
    current_user=Depends(get_current_user)
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
def create_resource(
    resource: ResourceCreate,
    current_user=Depends(get_current_user)
):
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
def get_resources(
    current_user=Depends(get_current_user)
):

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
    analysis: IncidentAnalysis,
    current_user=Depends(get_current_user)
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



@app.post("/api/resources/recommend")
def recommend_incident_resources(
    request: ResourceRecommendationRequest,
    current_user=Depends(get_current_user)
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
def sync_offline_sos(
    sos: SyncSOSRequest,
    current_user=Depends(get_current_user)
):

    try:
        incident_data = {
            "local_id": sos.local_id,
            "user_id": current_user.id,
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

        if response.user is None or response.session is None:
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
        print("LOGIN ERROR:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )