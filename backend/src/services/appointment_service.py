from typing import List, Optional
from datetime import datetime
import uuid
import logging
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

        appointment_dict = existing_appointment.dict()
        
        # Convert UUID to string for storage
        appointment_dict['id'] = str(appointment_dict['id'])
        
        # Update fields
        for key, value in update_data.items():
            if value is not None:
                if isinstance(value, datetime):
                    appointment_dict[key] = value.isoformat()
                else:
                    appointment_dict[key] = value

        appointment_dict['updated_at'] = datetime.now().isoformat()
        
        # Handle complex types for storage (Enum, UUID, etc are handled by Pydantic on read, but need strings for JSON)
        # Note: In a real app with Pydantic v2, model_dump(mode='json') helps.
        # Here we manually ensure serialization compatibility if needed, but dict() usually handles basic types.
        # However, for saving back to JSON storage, we need to ensure everything is JSON serializable.
        
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
        appointment.updated_at = datetime.now()
        
        appointment_dict = appointment.dict()
        appointment_dict['id'] = str(appointment.id)
        
        # Serialize occurrences
        appointment_dict['occurrences'] = [occ.dict() for occ in appointment.occurrences]
        # Ensure all UUIDs are strings
        for occ in appointment_dict['occurrences']:
            occ['id'] = str(occ['id'])
            occ['appointment_id'] = str(occ['appointment_id'])

        await self.storage.save_appointment(appointment_dict)
        return appointment

    async def complete_appointment(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        appointment = await self.get_appointment(appointment_id)
        if not appointment:
            return None

        appointment.status = AppointmentStatus.COMPLETED
        
        occurrence_req = CreateOccurrenceRequest(
            type=OccurrenceType.COMPLETION,
            description="Serviço marcado como concluído."
        )
        
        return await self.add_occurrence(appointment_id, occurrence_req)