from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.appointment import (
    Appointment, AppointmentCreate, AppointmentUpdate,
    AppointmentStatus, VolatilityLevel,
    create_occurrence_record, calculate_appointment_priority
)
from ..models.occurrence import (
    OccurrenceCreate, OccurrenceType,
    create_status_change_occurrence, create_modification_occurrence
)
from .file_storage import file_storage_service


class AppointmentService:
    """Service for managing appointment business logic"""
    
    def create_appointment(self, appointment_data: AppointmentCreate) -> Dict[str, Any]:
        """Create a new appointment with validation and occurrence tracking"""
        try:
            # Convert to dict for storage
            new_appointment = {
                "id": str(uuid.uuid4()),
                "customer_name": appointment_data.customer_name,
                "service_date": appointment_data.service_date.isoformat(),
                "service_type": appointment_data.service_type,
                "volatility_level": appointment_data.volatility_level,
                "observations": appointment_data.observations,
                "required_tools": appointment_data.required_tools or [],
                "status": AppointmentStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "occurrences": []
            }
            
            # Save to storage
            success = file_storage_service.save_appointment(new_appointment)
            
            if success:
                # Create creation occurrence
                creation_occurrence = create_occurrence_record(
                    appointment_id=new_appointment["id"],
                    occurrence_type=OccurrenceType.MODIFICATION,
                    description=f"Appointment created for {appointment_data.customer_name}",
                    new_data={"status": AppointmentStatus.PENDING.value}
                )
                
                file_storage_service.add_occurrence_to_appointment(
                    new_appointment["id"], 
                    creation_occurrence.dict()
                )
                
                return {
                    "success": True,
                    "data": new_appointment,
                    "message": "Appointment created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save appointment"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_appointment(self, appointment_id: str, update_data: AppointmentUpdate) -> Dict[str, Any]:
        """Update an existing appointment with occurrence tracking"""
        try:
            # Get existing appointment
            existing_appointment = file_storage_service.get_appointment_by_id(appointment_id)
            if not existing_appointment:
                return {
                    "success": False,
                    "error": "Appointment not found"
                }
            
            # Prepare update data
            update_dict = update_data.dict(exclude_unset=True)
            
            # Convert datetime fields to string if present
            if "service_date" in update_dict:
                update_dict["service_date"] = update_dict["service_date"].isoformat()
            
            # Track status change
            status_changed = False
            if "status" in update_dict and update_dict["status"] != existing_appointment.get("status"):
                status_changed = True
                old_status = existing_appointment.get("status")
                new_status = update_dict["status"]
            
            # Track reschedule
            rescheduled = False
            if "service_date" in update_dict and update_dict["service_date"] != existing_appointment.get("service_date"):
                rescheduled = True
                old_date = existing_appointment.get("service_date")
                new_date = update_dict["service_date"]
            
            # Update timestamp
            update_dict["updated_at"] = datetime.now().isoformat()
            
            # Save updated appointment
            success = file_storage_service.update_appointment(appointment_id, update_dict)
            
            if success:
                updated_appointment = file_storage_service.get_appointment_by_id(appointment_id)
                
                # Create appropriate occurrence records
                if status_changed:
                    status_occurrence = create_status_change_occurrence(
                        appointment_id=appointment_id,
                        previous_status=old_status,
                        new_status=new_status,
                        additional_info=f"Status changed from {old_status} to {new_status}"
                    )
                    file_storage_service.add_occurrence_to_appointment(
                        appointment_id, 
                        status_occurrence.dict()
                    )
                
                if rescheduled:
                    reschedule_occurrence = create_reschedule_occurrence(
                        appointment_id=appointment_id,
                        previous_date=datetime.fromisoformat(old_date.replace('Z', '+00:00')),
                        new_date=datetime.fromisoformat(new_date.replace('Z', '+00:00')),
                        reason="Appointment rescheduled"
                    )
                    file_storage_service.add_occurrence_to_appointment(
                        appointment_id, 
                        reschedule_occurrence.dict()
                    )
                
                # Track other modifications
                other_changes = {k: v for k, v in update_dict.items() 
                               if k not in ["status", "service_date", "updated_at"]}
                if other_changes:
                    mod_occurrence = create_modification_occurrence(
                        appointment_id=appointment_id,
                        modified_fields=other_changes,
                        reason="Appointment details updated"
                    )
                    file_storage_service.add_occurrence_to_appointment(
                        appointment_id, 
                        mod_occurrence.dict()
                    )
                
                return {
                    "success": True,
                    "data": updated_appointment,
                    "message": "Appointment updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update appointment"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """Mark an appointment as completed"""
        try:
            # Get existing appointment
            existing_appointment = file_storage_service.get_appointment_by_id(appointment_id)
            if not existing_appointment:
                return {
                    "success": False,
                    "error": "Appointment not found"
                }
            
            # Check if already completed
            if existing_appointment.get("status") == AppointmentStatus.COMPLETED.value:
                return {
                    "success": False,
                    "error": "Appointment is already completed"
                }
            
            # Update status to completed
            update_data = {
                "status": AppointmentStatus.COMPLETED.value,
                "updated_at": datetime.now().isoformat()
            }
            
            success = file_storage_service.update_appointment(appointment_id, update_data)
            
            if success:
                updated_appointment = file_storage_service.get_appointment_by_id(appointment_id)
                
                # Create completion occurrence
                completion_occurrence = create_completion_occurrence(
                    appointment_id=appointment_id,
                    completion_notes=f"Appointment marked as completed"
                )
                file_storage_service.add_occurrence_to_appointment(
                    appointment_id, 
                    completion_occurrence.dict()
                )
                
                return {
                    "success": True,
                    "data": updated_appointment,
                    "message": "Appointment marked as completed"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to complete appointment"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_appointments_sorted_by_priority(self) -> List[Dict[str, Any]]:
        """Get all appointments sorted by priority"""
        appointments = file_storage_service.get_all_appointments()
        
        # Sort by priority (delayed first, then by proximity and volatility)
        now = datetime.now()
        
        # Separate delayed and upcoming appointments
        delayed = [apt for apt in appointments if 
                   datetime.fromisoformat(apt["service_date"].replace('Z', '+00:00')) < now and 
                   apt["status"] != AppointmentStatus.COMPLETED.value]
        
        upcoming = [apt for apt in appointments if 
                    datetime.fromisoformat(apt["service_date"].replace('Z', '+00:00')) >= now and 
                    apt["status"] == AppointmentStatus.PENDING.value]
        
        in_progress = [apt for apt in appointments if apt["status"] == AppointmentStatus.IN_PROGRESS.value]
        
        # Sort delayed by delay duration (most delayed first)
        delayed.sort(key=lambda x: datetime.fromisoformat(x["service_date"].replace('Z', '+00:00')))
        
        # Sort upcoming by priority score
        def calculate_priority_score(appointment):
            volatility_weights = {
                VolatilityLevel.HIGH.value: 1.0, 
                VolatilityLevel.MEDIUM.value: 0.6, 
                VolatilityLevel.LOW.value: 0.3
            }
            volatility_weight = volatility_weights.get(appointment["volatility_level"], 0.5)
            
            service_datetime = datetime.fromisoformat(appointment["service_date"].replace('Z', '+00:00'))
            hours_until = (service_datetime - now).total_seconds() / 3600
            proximity_weight = max(0, 1 - (hours_until / 168))  # Normalize to week (168 hours)
            
            return (volatility_weight * 0.6) + (proximity_weight * 0.4)
        
        upcoming.sort(key=calculate_priority_score, reverse=True)
        
        # Sort in_progress by start time (oldest first)
        in_progress.sort(key=lambda x: datetime.fromisoformat(x["service_date"].replace('Z', '+00:00')))
        
        # Combine all appointments
        return delayed + upcoming + in_progress


# Create singleton instance
appointment_service = AppointmentService()