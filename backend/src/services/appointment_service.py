from typing import List, Optional
from datetime import datetime
import uuid
import logging
from enum import Enum # Import Enum for type checking

from ..models.appointment import Appointment, CreateAppointmentRequest, UpdateAppointmentRequest, AppointmentStatus
from ..models.occurrence import Occurrence, OccurrenceType, CreateOccurrenceRequest
from ..services.file_storage import FileStorageService

logger = logging.getLogger("maxfrio-service")

class AppointmentService:
    def __init__(self):
        self.storage = FileStorageService()

    async def create_appointment(self, request: CreateAppointmentRequest) -> Appointment:
        logger.info(f"Creating new appointment for customer: {request.customer_name}")
        now = datetime.now()
        appointment_id = uuid.uuid4()
        
        appointment_data = {
            "id": str(appointment_id),
            "customer_name": request.customer_name,
            "service_date": request.service_date.isoformat(),
            "service_type": request.service_type,
            "volatility_level": request.volatility_level,
            "observations": request.observations,
            "required_tools": request.required_tools or [],
            "status": AppointmentStatus.PENDING,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "occurrences": []
        }
        
        await self.storage.save_appointment(appointment_data)
        logger.info(f"Appointment created successfully with ID: {appointment_id}")
        return Appointment(**appointment_data)

    async def get_all_appointments(self) -> List[Appointment]:
        data = await self.storage.get_appointments()
        return [Appointment(**item) for item in data]

    async def get_appointment(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        all_appointments = await self.get_all_appointments()
        for appointment in all_appointments:
            if appointment.id == appointment_id:
                return appointment
        return None

    async def update_appointment(self, appointment_id: uuid.UUID, request: UpdateAppointmentRequest) -> Optional[Appointment]:
        existing_appointment = await self.get_appointment(appointment_id)
        if not existing_appointment:
            return None

        update_data = request.dict(exclude_unset=True)
        if not update_data:
            return existing_appointment

        # Get a dictionary representation suitable for JSON storage
        # Use model_dump(mode='json') for Pydantic v2 for complete serialization, handling datetimes and enums
        appointment_dict = existing_appointment.model_dump(mode='json')
        
        # Update fields from request
        for key, value in update_data.items():
            if value is not None:
                # Ensure datetime objects from request are also ISO formatted if updated
                if isinstance(value, datetime):
                    appointment_dict[key] = value.isoformat()
                elif isinstance(value, Enum): # Handle Enum updates from request
                    appointment_dict[key] = value.value
                else:
                    appointment_dict[key] = value
        
        appointment_dict['updated_at'] = datetime.now().isoformat() # Always update 'updated_at'
        # Ensure status enum is serialized as string if it was updated in the request (model_dump usually handles this, but explicit check for safety)
        if 'status' in update_data and isinstance(appointment_dict.get('status'), Enum):
            appointment_dict['status'] = appointment_dict['status'].value
        
        await self.storage.save_appointment(appointment_dict)
        return Appointment(**appointment_dict)

    async def delete_appointment(self, appointment_id: uuid.UUID) -> bool:
        return await self.storage.delete_appointment(str(appointment_id))

    async def add_occurrence(self, appointment_id: uuid.UUID, request: CreateOccurrenceRequest) -> Optional[Appointment]:
        appointment = await self.get_appointment(appointment_id)
        if not appointment:
            return None

        occurrence = Occurrence(
            id=uuid.uuid4(),
            appointment_id=appointment_id,
            timestamp=datetime.now(),
            type=request.type,
            description=request.description
        )
        
        appointment.occurrences.append(occurrence)
        appointment.updated_at = datetime.now() # Update the actual object's timestamp
        
        # Get a dictionary representation suitable for JSON storage
        appointment_dict = appointment.model_dump(mode='json') # This should handle all datetime and enum serialization
        
        await self.storage.save_appointment(appointment_dict)
        return appointment

    async def complete_appointment(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        appointment = await self.get_appointment(appointment_id)
        if not appointment:
            return None

        appointment.status = AppointmentStatus.COMPLETED
        
        # First, mark as completed
        completion_occurrence_req = CreateOccurrenceRequest(
            type=OccurrenceType.COMPLETION,
            description="Serviço marcado como concluído."
        )
        await self.add_occurrence(appointment_id, completion_occurrence_req)
        
        # Then, change status to awaiting_payment
        appointment.status = AppointmentStatus.AWAITING_PAYMENT
        appointment.updated_at = datetime.now()
        
        # Get a dictionary representation suitable for JSON storage
        appointment_dict = appointment.model_dump(mode='json')
        
        await self.storage.save_appointment(appointment_dict)
        return appointment
    
    async def mark_as_paid(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Mark an appointment as paid and change status to finalized."""
        appointment = await self.get_appointment(appointment_id)
        if not appointment:
            return None
            
        if appointment.status != AppointmentStatus.AWAITING_PAYMENT:
            raise ValueError("Appointment must be in 'awaiting_payment' status to be marked as paid.")
        
        # Add a payment occurrence
        payment_occurrence = Occurrence(
            id=uuid.uuid4(),
            appointment_id=appointment_id,
            timestamp=datetime.now(),
            type=OccurrenceType.PAYMENT,
            description="Serviço marcado como pago e finalizado."
        )
        
        appointment.occurrences.append(payment_occurrence)
        appointment.status = AppointmentStatus.FINALIZED
        appointment.updated_at = datetime.now()
        
        # Get a dictionary representation suitable for JSON storage
        appointment_dict = appointment.model_dump(mode='json')
        
        await self.storage.save_appointment(appointment_dict)
        return appointment