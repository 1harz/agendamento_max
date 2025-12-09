from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class OccurrenceType(str, Enum):
    """Types of occurrences that can be recorded"""
    STATUS_CHANGE = "status_change"
    RESCHEDULE = "reschedule"
    MODIFICATION = "modification"
    COMPLETION = "completion"


class OccurrenceBase(BaseModel):
    """Base occurrence model with common fields"""
    appointment_id: str = Field(..., description="Reference to the parent appointment")
    timestamp: datetime = Field(..., description="When the occurrence was created")
    type: OccurrenceType = Field(..., description="Type of occurrence")
    description: str = Field(..., min_length=5, max_length=200, description="Human-readable description of the change")
    previous_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data before change")
    new_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of appointment data after change")


class OccurrenceCreate(OccurrenceBase):
    """Model for creating a new occurrence"""
    pass


class Occurrence(OccurrenceBase):
    """Complete occurrence model with all fields"""
    id: str = Field(..., description="Unique identifier for the occurrence")

    class Config:
        from_attributes = True


# Helper functions for occurrence management
def create_status_change_occurrence(
    appointment_id: str,
    previous_status: str,
    new_status: str,
    additional_info: Optional[str] = None
) -> OccurrenceCreate:
    """Create a status change occurrence"""
    import uuid
    
    description = f"Status changed from {previous_status} to {new_status}"
    if additional_info:
        description += f": {additional_info}"
    
    return OccurrenceCreate(
        appointment_id=appointment_id,
        timestamp=datetime.now(),
        type=OccurrenceType.STATUS_CHANGE,
        description=description,
        previous_data={"status": previous_status},
        new_data={"status": new_status}
    )


def create_reschedule_occurrence(
    appointment_id: str,
    previous_date: datetime,
    new_date: datetime,
    reason: Optional[str] = None
) -> OccurrenceCreate:
    """Create a reschedule occurrence"""
    import uuid
    
    description = f"Service rescheduled from {previous_date.strftime('%Y-%m-%d %H:%M')} to {new_date.strftime('%Y-%m-%d %H:%M')}"
    if reason:
        description += f": {reason}"
    
    return OccurrenceCreate(
        appointment_id=appointment_id,
        timestamp=datetime.now(),
        type=OccurrenceType.RESCHEDULE,
        description=description,
        previous_data={"service_date": previous_date.isoformat()},
        new_data={"service_date": new_date.isoformat()}
    )


def create_modification_occurrence(
    appointment_id: str,
    modified_fields: Dict[str, Any],
    reason: Optional[str] = None
) -> OccurrenceCreate:
    """Create a modification occurrence"""
    import uuid
    
    field_names = ", ".join(modified_fields.keys())
    description = f"Modified fields: {field_names}"
    if reason:
        description += f": {reason}"
    
    return OccurrenceCreate(
        appointment_id=appointment_id,
        timestamp=datetime.now(),
        type=OccurrenceType.MODIFICATION,
        description=description,
        new_data=modified_fields
    )


def create_completion_occurrence(
    appointment_id: str,
    completion_notes: Optional[str] = None
) -> OccurrenceCreate:
    """Create a completion occurrence"""
    import uuid
    
    description = "Service marked as completed"
    if completion_notes:
        description += f": {completion_notes}"
    
    return OccurrenceCreate(
        appointment_id=appointment_id,
        timestamp=datetime.now(),
        type=OccurrenceType.COMPLETION,
        description=description
    )