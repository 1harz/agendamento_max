from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VolatilityLevel(str, Enum):
    """Customer volatility level for rescheduling"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AppointmentStatus(str, Enum):
    """Appointment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OccurrenceType(str, Enum):
    """Types of occurrences that can be recorded"""
    STATUS_CHANGE = "status_change"
    RESCHEDULE = "reschedule"
    MODIFICATION = "modification"
    COMPLETION = "completion"


class Occurrence(BaseModel):
    """Historical record of changes made to an appointment"""
    id: str = Field(..., description="Unique identifier for the occurrence")
    appointment_id: str = Field(..., description="Reference to the parent appointment")
    timestamp: datetime = Field(..., description="When the occurrence was created")
    type: OccurrenceType = Field(..., description="Type of occurrence")
    description: str = Field(..., min_length=5, max_length=200, description="Human-readable description of the change")
    previous_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data before change")
    new_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data after change")

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    """Base appointment model with common fields"""
    customer_name: str = Field(..., min_length=2, max_length=100, description="Name of the customer receiving service")
    service_date: datetime = Field(..., description="Date and time when service is scheduled")
    service_type: str = Field(..., min_length=2, max_length=50, description="Type of service to be performed")
    volatility_level: VolatilityLevel = Field(..., description="Customer's flexibility for rescheduling")
    observations: Optional[str] = Field(None, max_length=500, description="Additional notes about the service")
    required_tools: Optional[List[str]] = Field(default_factory=list, description="Tools needed for the service")

    @validator('service_date')
    def service_date_must_be_future(cls, v):
        """Validate that service_date is in the future when creating new appointments"""
        if v <= datetime.now():
            raise ValueError('Service date must be in the future')
        return v

    @validator('required_tools')
    def validate_required_tools(cls, v):
        """Validate required tools list"""
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tools allowed')
        if v:
            for tool in v:
                if len(tool) > 50:
                    raise ValueError('Each tool name must be maximum 50 characters')
        return v


class AppointmentCreate(AppointmentBase):
    """Model for creating a new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Model for updating an existing appointment"""
    customer_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Name of the customer receiving service")
    service_date: Optional[datetime] = Field(None, description="Date and time when service is scheduled")
    service_type: Optional[str] = Field(None, min_length=2, max_length=50, description="Type of service to be performed")
    volatility_level: Optional[VolatilityLevel] = Field(None, description="Customer's flexibility for rescheduling")
    observations: Optional[str] = Field(None, max_length=500, description="Additional notes about the service")
    required_tools: Optional[List[str]] = Field(None, description="Tools needed for the service")
    status: Optional[AppointmentStatus] = Field(None, description="Current status of the appointment")

    @validator('required_tools')
    def validate_required_tools(cls, v):
        """Validate required tools list"""
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tools allowed')
        if v:
            for tool in v:
                if len(tool) > 50:
                    raise ValueError('Each tool name must be maximum 50 characters')
        return v


class Appointment(AppointmentBase):
    """Complete appointment model with all fields"""
    id: str = Field(..., description="Unique identifier for the appointment")
    status: AppointmentStatus = Field(..., description="Current status of the appointment")
    created_at: datetime = Field(..., description="When the appointment was created")
    updated_at: datetime = Field(..., description="When the appointment was last modified")
    occurrences: List[Occurrence] = Field(default_factory=list, description="History of changes to the appointment")

    class Config:
        from_attributes = True


class OccurrenceCreate(BaseModel):
    """Model for creating a new occurrence"""
    type: OccurrenceType = Field(..., description="Type of occurrence")
    description: str = Field(..., min_length=5, max_length=200, description="Human-readable description of the change")
    previous_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data before change")
    new_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data after change")


# Helper functions for appointment management
def create_occurrence_record(
    appointment_id: str,
    occurrence_type: OccurrenceType,
    description: str,
    previous_data: Optional[Dict[str, Any]] = None,
    new_data: Optional[Dict[str, Any]] = None
) -> Occurrence:
    """Create a new occurrence record"""
    import uuid
    
    return Occurrence(
        id=str(uuid.uuid4()),
        appointment_id=appointment_id,
        timestamp=datetime.now(),
        type=occurrence_type,
        description=description,
        previous_data=previous_data,
        new_data=new_data
    )


def calculate_appointment_priority(appointment: Appointment, current_time: datetime = None) -> float:
    """Calculate priority score for an appointment based on volatility and proximity"""
    if current_time is None:
        current_time = datetime.now()
    
    # Get volatility weight
    volatility_weights = {
        VolatilityLevel.HIGH: 1.0,
        VolatilityLevel.MEDIUM: 0.6,
        VolatilityLevel.LOW: 0.3
    }
    volatility_weight = volatility_weights.get(appointment.volatility_level, 0.5)
    
    # Calculate proximity weight
    hours_until = (appointment.service_date - current_time).total_seconds() / 3600
    proximity_weight = max(0, 1 - (hours_until / 168))  # Normalize to week (168 hours)
    
    # Calculate final priority score
    return (volatility_weight * 0.6) + (proximity_weight * 0.4)


def is_appointment_delayed(appointment: Appointment, current_time: datetime = None) -> bool:
    """Check if an appointment is delayed"""
    if current_time is None:
        current_time = datetime.now()
    
    return appointment.service_date < current_time and appointment.status != AppointmentStatus.COMPLETED