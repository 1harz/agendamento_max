from enum import Enum
from pydantic import BaseModel, Field, UUID4, validator
from datetime import datetime
from typing import List, Optional
from .occurrence import Occurrence

class VolatilityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    AWAITING_PAYMENT = "awaiting_payment"
    FINALIZED = "finalized"

class Appointment(BaseModel):
    id: UUID4
    customer_name: str = Field(min_length=2, max_length=100)
    service_date: datetime
    service_type: str = Field(min_length=2, max_length=50)
    volatility_level: VolatilityLevel
    observations: Optional[str] = Field(None, max_length=500)
    required_tools: Optional[List[str]] = Field(default_factory=list, max_items=10)
    status: AppointmentStatus = AppointmentStatus.PENDING
    created_at: datetime
    updated_at: datetime
    occurrences: List[Occurrence] = Field(default_factory=list)
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        if isinstance(v, str):
            try:
                return AppointmentStatus(v)
            except ValueError:
                raise ValueError(f"Invalid status value: {v}")
        return v
    
    class Config:
        # Allow enum values to be converted from strings
        use_enum_values = True
        # For Pydantic v1 compatibility
        validate_assignment = True

    @validator('required_tools', each_item=True)
    def validate_tool_length(cls, v):
        if len(v) > 50:
            raise ValueError('Tool name must be less than 50 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_name": "João Silva",
                "service_date": "2025-12-10T14:30:00",
                "service_type": "Manutenção de Ar Condicionado",
                "volatility_level": "medium",
                "observations": "Cliente solicita verificação do filtro",
                "required_tools": ["Chave de fenda", "Medidor de pressão"],
                "status": "pending",
                "created_at": "2025-12-09T10:00:00",
                "updated_at": "2025-12-09T10:00:00",
                "occurrences": []
            }
        }

class CreateAppointmentRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    service_date: datetime
    service_type: str = Field(min_length=2, max_length=50)
    volatility_level: VolatilityLevel
    observations: Optional[str] = Field(None, max_length=500)
    required_tools: Optional[List[str]] = Field(default_factory=list, max_items=10)

    @validator('service_date')
    def validate_future_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Service date must be in the future')
        return v

    @validator('required_tools', each_item=True)
    def validate_tool_length(cls, v):
        if len(v) > 50:
            raise ValueError('Tool name must be less than 50 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "João Silva",
                "service_date": "2025-12-10T14:30:00",
                "service_type": "Manutenção de Ar Condicionado",
                "volatility_level": "medium",
                "observations": "Cliente solicita verificação do filtro",
                "required_tools": ["Chave de fenda", "Medidor de pressão"]
            }
        }

class UpdateAppointmentRequest(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=2, max_length=100)
    service_date: Optional[datetime] = None
    service_type: Optional[str] = Field(None, min_length=2, max_length=50)
    volatility_level: Optional[VolatilityLevel] = None
    observations: Optional[str] = Field(None, max_length=500)
    required_tools: Optional[List[str]] = Field(None, max_items=10)
    status: Optional[AppointmentStatus] = None

    @validator('required_tools', each_item=True)
    def validate_tool_length(cls, v):
        if len(v) > 50:
            raise ValueError('Tool name must be less than 50 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "João Silva",
                "service_type": "Instalação",
                "status": "in_progress"
            }
        }