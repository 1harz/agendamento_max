import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..config import settings


class FileStorageService:
    """Service for handling file-based storage operations"""
    
    def __init__(self):
        self.appointments_file = settings.APPOINTMENTS_FILE
        self._ensure_data_directory_exists()
    
    def _ensure_data_directory_exists(self):
        """Ensure the data directory exists"""
        data_dir = Path(self.appointments_file).parent
        data_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_backup(self):
        """Create a backup of the appointments file"""
        if not os.path.exists(self.appointments_file):
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.appointments_file.replace(".txt", f"_backup_{timestamp}.txt")
        shutil.copy2(self.appointments_file, backup_file)
    
    def _read_data(self) -> Dict[str, Any]:
        """Read data from the appointments file"""
        if not os.path.exists(self.appointments_file):
            return {"appointments": [], "metadata": {"last_updated": "", "version": "1.0", "total_appointments": 0}}
        
        try:
            with open(self.appointments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading appointments file: {e}")
            return {"appointments": [], "metadata": {"last_updated": "", "version": "1.0", "total_appointments": 0}}
    
    def _write_data(self, data: Dict[str, Any]) -> bool:
        """Write data to the appointments file"""
        try:
            # Create backup before writing
            self._create_backup()
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_appointments"] = len(data.get("appointments", []))
            
            # Write to file
            with open(self.appointments_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error writing appointments file: {e}")
            return False
    
    def get_all_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments from storage"""
        data = self._read_data()
        return data.get("appointments", [])
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific appointment by ID"""
        appointments = self.get_all_appointments()
        for appointment in appointments:
            if appointment.get("id") == appointment_id:
                return appointment
        return None
    
    def save_appointment(self, appointment: Dict[str, Any]) -> bool:
        """Save a new appointment to storage"""
        try:
            data = self._read_data()
            appointments = data.get("appointments", [])
            
            # Check if appointment already exists
            for i, existing_appointment in enumerate(appointments):
                if existing_appointment.get("id") == appointment.get("id"):
                    # Update existing appointment
                    appointments[i] = appointment
                    data["appointments"] = appointments
                    return self._write_data(data)
            
            # Add new appointment
            appointments.append(appointment)
            data["appointments"] = appointments
            return self._write_data(data)
        except Exception as e:
            print(f"Error saving appointment: {e}")
            return False
    
    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment by ID"""
        try:
            data = self._read_data()
            appointments = data.get("appointments", [])
            
            # Find and remove the appointment
            appointments = [apt for apt in appointments if apt.get("id") != appointment_id]
            data["appointments"] = appointments
            return self._write_data(data)
        except Exception as e:
            print(f"Error deleting appointment: {e}")
            return False
    
    def update_appointment(self, appointment_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing appointment"""
        try:
            data = self._read_data()
            appointments = data.get("appointments", [])
            
            # Find and update the appointment
            for i, appointment in enumerate(appointments):
                if appointment.get("id") == appointment_id:
                    appointments[i] = {**appointment, **updated_data}
                    data["appointments"] = appointments
                    return self._write_data(data)
            
            return False  # Appointment not found
        except Exception as e:
            print(f"Error updating appointment: {e}")
            return False
    
    def add_occurrence_to_appointment(self, appointment_id: str, occurrence: Dict[str, Any]) -> bool:
        """Add an occurrence to an appointment"""
        try:
            data = self._read_data()
            appointments = data.get("appointments", [])
            
            # Find the appointment and add the occurrence
            for i, appointment in enumerate(appointments):
                if appointment.get("id") == appointment_id:
                    if "occurrences" not in appointment:
                        appointment["occurrences"] = []
                    appointment["occurrences"].append(occurrence)
                    appointments[i] = appointment
                    data["appointments"] = appointments
                    return self._write_data(data)
            
            return False  # Appointment not found
        except Exception as e:
            print(f"Error adding occurrence to appointment: {e}")
            return False


# Create a singleton instance
file_storage_service = FileStorageService()