from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..services.file_storage import file_storage_service
from ..services.appointment_service import appointment_service

# Create API router
router = APIRouter()

# Pydantic models for request/response
class AppointmentBase(BaseModel):
    customer_name: str
    service_date: datetime
    service_type: str
    volatility_level: str
    observations: Optional[str] = None
    required_tools: Optional[List[str]] = []

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    customer_name: Optional[str] = None
    service_date: Optional[datetime] = None
    service_type: Optional[str] = None
    volatility_level: Optional[str] = None
    observations: Optional[str] = None
    required_tools: Optional[List[str]] = None
    status: Optional[str] = None

class Appointment(AppointmentBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    occurrences: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True

class OccurrenceBase(BaseModel):
    type: str
    description: str
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None

class OccurrenceCreate(OccurrenceBase):
    pass

class Occurrence(OccurrenceBase):
    id: str
    appointment_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class AIChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AIChatResponse(BaseModel):
    message: str
    action: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False

# Appointment endpoints
@router.get("/appointments", response_model=Dict[str, Any])
async def get_appointments():
    """Get all appointments sorted by priority"""
    appointments = file_storage_service.get_all_appointments()
    
    # Sort by priority (delayed first, then by proximity and volatility)
    now = datetime.now()
    
    # Separate delayed and upcoming appointments
    delayed = [apt for apt in appointments if 
               datetime.fromisoformat(apt["service_date"].replace('Z', '+00:00')) < now and 
               apt["status"] != "completed"]
    
    upcoming = [apt for apt in appointments if 
                datetime.fromisoformat(apt["service_date"].replace('Z', '+00:00')) >= now and 
                apt["status"] == "pending"]
    
    in_progress = [apt for apt in appointments if apt["status"] == "in_progress"]
    
    # Sort delayed by delay duration (most delayed first)
    delayed.sort(key=lambda x: datetime.fromisoformat(x["service_date"].replace('Z', '+00:00')))
    
    # Sort upcoming by priority score
    def calculate_priority(appointment):
        volatility_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
        volatility_weight = volatility_weights.get(appointment["volatility_level"], 0.5)
        
        service_datetime = datetime.fromisoformat(appointment["service_date"].replace('Z', '+00:00'))
        hours_until = (service_datetime - now).total_seconds() / 3600
        proximity_weight = max(0, 1 - (hours_until / 168))  # Normalize to week (168 hours)
        
        return (volatility_weight * 0.6) + (proximity_weight * 0.4)
    
    upcoming.sort(key=calculate_priority, reverse=True)
    
    # Sort in_progress by start time (oldest first)
    in_progress.sort(key=lambda x: datetime.fromisoformat(x["service_date"].replace('Z', '+00:00')))
    
    # Combine all appointments
    sorted_appointments = delayed + upcoming + in_progress
    
    return {
        "success": True,
        "data": sorted_appointments,
        "total": len(sorted_appointments)
    }

@router.post("/appointments", response_model=Dict[str, Any])
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment"""
    result = appointment_service.create_appointment(appointment)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create appointment"))

@router.get("/appointments/{appointment_id}", response_model=Dict[str, Any])
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    appointment = file_storage_service.get_appointment_by_id(appointment_id)
    if appointment:
        return {
            "success": True,
            "data": appointment
        }
    else:
        raise HTTPException(status_code=404, detail="Appointment not found")

@router.put("/appointments/{appointment_id}", response_model=Dict[str, Any])
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate):
    """Update an existing appointment"""
    result = appointment_service.update_appointment(appointment_id, appointment_update)
    if result["success"]:
        return result
    else:
        error_msg = result.get("error", "Appointment not found")
        if error_msg == "Appointment not found":
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

@router.delete("/appointments/{appointment_id}", response_model=Dict[str, Any])
async def delete_appointment(appointment_id: str):
    """Delete an appointment"""
    try:
        success = file_storage_service.delete_appointment(appointment_id)
        if success:
            return {
                "success": True,
                "message": "Appointment deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Appointment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments/{appointment_id}/complete", response_model=Dict[str, Any])
async def complete_appointment(appointment_id: str):
    """Mark an appointment as completed"""
    result = appointment_service.complete_appointment(appointment_id)
    if result["success"]:
        return result
    else:
        error_msg = result.get("error", "Appointment not found")
        if error_msg == "Appointment not found":
            raise HTTPException(status_code=404, detail=error_msg)
        elif error_msg == "Appointment is already completed":
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

@router.post("/appointments/{appointment_id}/occurrence", response_model=Dict[str, Any])
async def create_occurrence(appointment_id: str, occurrence: OccurrenceCreate):
    """Create a new occurrence for an appointment"""
    try:
        # Check if appointment exists
        existing_appointment = file_storage_service.get_appointment_by_id(appointment_id)
        if not existing_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        new_occurrence = {
            "id": str(uuid.uuid4()),
            "appointment_id": appointment_id,
            "timestamp": datetime.now().isoformat(),
            "type": occurrence.type,
            "description": occurrence.description,
            "previous_data": occurrence.previous_data,
            "new_data": occurrence.new_data
        }
        
        success = file_storage_service.add_occurrence_to_appointment(appointment_id, new_occurrence)
        if success:
            return {
                "success": True,
                "data": new_occurrence,
                "message": "Occurrence created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create occurrence")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# AI Assistant endpoints (placeholder for now)
@router.post("/ai/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest):
    """AI assistant interaction"""
    # This is a placeholder implementation
    # Will be implemented in a later task with Google Gemini integration
    return AIChatResponse(
        message="AI assistant is not yet implemented. This will be available in a future update.",
        requires_confirmation=False
    )

@router.get("/ai/recommendations", response_model=Dict[str, Any])
async def get_ai_recommendations(excluded_appointment_id: Optional[str] = None):
    """Get AI-powered appointment recommendations"""
    # This is a placeholder implementation
    # Will be implemented in a later task with Google Gemini integration
    return {
        "success": True,
        "data": {
            "recommendations": [],
            "reasoning": "AI recommendations are not yet implemented. This will be available in a future update."
        }
    }