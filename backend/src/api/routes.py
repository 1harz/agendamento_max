from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from ..models.appointment import Appointment, CreateAppointmentRequest, UpdateAppointmentRequest
from ..models.occurrence import CreateOccurrenceRequest
from ..services.appointment_service import AppointmentService
from ..services.ai_service import AIService

router = APIRouter()
appointment_service = AppointmentService()
ai_service = AIService()

class AIChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class AIChatResponse(BaseModel):
    message: str
    action: Optional[dict] = None
    requires_confirmation: bool = False

@router.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.post("/appointments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointment(request: CreateAppointmentRequest):
    try:
        appointment = await appointment_service.create_appointment(request)
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments", response_model=dict)
async def get_appointments():
    try:
        appointments = await appointment_service.get_all_appointments()
        return {
            "success": True,
            "data": appointments,
            "total": len(appointments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: UUID):
    appointment = await appointment_service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "success": True,
        "data": appointment
    }

@router.put("/appointments/{appointment_id}", response_model=dict)
async def update_appointment(appointment_id: UUID, request: UpdateAppointmentRequest):
    try:
        appointment = await appointment_service.update_appointment(appointment_id, request)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/appointments/{appointment_id}", response_model=dict)
async def delete_appointment(appointment_id: UUID):
    success = await appointment_service.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "success": True,
        "message": "Appointment deleted successfully"
    }

@router.post("/appointments/{appointment_id}/complete", response_model=dict)
async def complete_appointment(appointment_id: UUID):
    appointment = await appointment_service.complete_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "success": True,
        "data": appointment,
        "message": "Appointment marked as completed"
    }

@router.post("/appointments/{appointment_id}/paid", response_model=dict)
async def mark_as_paid(appointment_id: UUID):
    try:
        appointment = await appointment_service.mark_as_paid(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return {
            "success": True,
            "data": appointment,
            "message": "Appointment marked as paid and finalized"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments/{appointment_id}/occurrence", response_model=dict)
async def create_occurrence(appointment_id: UUID, request: CreateOccurrenceRequest):
    appointment = await appointment_service.add_occurrence(appointment_id, request)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "success": True,
        "data": appointment,
        "message": "Occurrence created successfully"
    }

@router.post("/ai/chat", response_model=dict)
async def ai_chat(request: AIChatRequest):
    try:
        context = request.context or {}
        context['current_time'] = datetime.now().isoformat()
        
        response = await ai_service.process_message(request.message, context)
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/recommendations", response_model=dict)
async def ai_recommendations(excluded_appointment_id: Optional[str] = None):
    try:
        recommendations = await ai_service.get_recommendations(excluded_appointment_id)
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))