from enum import Enum
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, Dict, Any

class OccurrenceType(str, Enum):
    STATUS_CHANGE = "status_change"
    RESCHEDULE = "reschedule"
    MODIFICATION = "modification"
    COMPLETION = "completion"

class Occurrence(BaseModel):
    id: UUID4
    appointment_id: UUID4
    timestamp: datetime
    type: OccurrenceType
    description: str = Field(min_length=5, max_length=200)
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174111",
                "appointment_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-12-09T15:30:00",
                "type": "modification",
                "description": "Updated service type and added new tools",
                "previous_data": {"service_type": "Installation", "required_tools": []},
                "new_data": {"service_type": "Maintenance", "required_tools": ["Wrench"]}
            }
        }

class CreateOccurrenceRequest(BaseModel):
    type: OccurrenceType
    description: str = Field(min_length=5, max_length=200)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "modification",
                "description": "Updated service type and added new tools"
            }
        }