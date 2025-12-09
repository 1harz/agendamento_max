import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List
import aiofiles
from ..config import Config

class FileStorageService:
    def __init__(self):
        self.file_path = Config.APPOINTMENTS_FILE
        self.backup_dir = Config.BACKUP_DIR
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure the data file exists with valid initial structure."""
        if not os.path.exists(self.file_path):
            initial_data = self._get_empty_data_structure()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)

    async def _create_backup(self):
        """Create a backup of the current data file."""
        if os.path.exists(self.file_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"appointments_backup_{timestamp}.txt")
            shutil.copy2(self.file_path, backup_path)
            print(f"Backup created at: {backup_path}")  # Debug line

    async def read_data(self) -> Dict[str, Any]:
        """Read all data from the storage file."""
        try:
            async with aiofiles.open(self.file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                # Handle empty file
                if not content.strip():
                    return self._get_empty_data_structure()
                return json.loads(content)
        except json.JSONDecodeError:
            return self._get_empty_data_structure()
        except Exception as e:
            raise RuntimeError(f"Failed to read data file: {str(e)}")
    
    def _get_empty_data_structure(self) -> Dict[str, Any]:
        """Returns the default empty data structure."""
        return {
            "appointments": [],
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "total_appointments": 0
            }
        }

    async def write_data(self, data: Dict[str, Any], create_backup=False):
        """Write data to the storage file safely."""
        try:
            # Only create backup if explicitly requested (not on every write)
            if create_backup:
                await self._create_backup()
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_appointments"] = len(data.get("appointments", []))
            
            # Write to a temporary file first, then move to avoid corruption
            temp_file_path = self.file_path + '.tmp'
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Write to temporary file
            async with aiofiles.open(temp_file_path, mode='w', encoding='utf-8') as f:
                await f.write(json_data)
            
            # Verify the temporary file was written correctly
            async with aiofiles.open(temp_file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                if not content or len(content) != len(json_data):
                    raise RuntimeError("Temporary file verification failed")
            
            # On Windows, we need to remove the target file first if it exists
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            
            # Move the temporary file to the target location
            shutil.move(temp_file_path, self.file_path)
            
        except Exception as e:
            # Clean up temp file if it exists
            temp_file_path = self.file_path + '.tmp'
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise RuntimeError(f"Failed to write data file: {str(e)}")

    async def get_appointments(self) -> List[Dict[str, Any]]:
        """Get list of all appointments."""
        data = await self.read_data()
        return data.get("appointments", [])

    async def save_appointment(self, appointment: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new appointment or update an existing one."""
        data = await self.read_data()
        appointments = data.get("appointments", [])
        
        # Check if update or create
        existing_index = next((index for (index, d) in enumerate(appointments) if d["id"] == appointment["id"]), None)
        
        if existing_index is not None:
            appointments[existing_index] = appointment
        else:
            appointments.append(appointment)
            
        data["appointments"] = appointments
        await self.write_data(data, create_backup=False)  # Don't create backup on every save
        return appointment

    async def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment by ID."""
        data = await self.read_data()
        appointments = data.get("appointments", [])
        
        filtered_appointments = [app for app in appointments if app["id"] != appointment_id]
        
        if len(filtered_appointments) == len(appointments):
            return False
            
        data["appointments"] = filtered_appointments
        await self.write_data(data, create_backup=False)  # Don't create backup on every delete
        return True