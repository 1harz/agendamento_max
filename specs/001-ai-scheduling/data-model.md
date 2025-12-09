# Data Model: AI-Powered Appointment Scheduling System

**Feature**: AI-Powered Appointment Scheduling System  
**Date**: 2025-12-09  
**Purpose**: Entity definitions, relationships, and validation rules

## Core Entities

### Appointment

Represents a scheduled service with customer information, timing, status, and service details.

**Fields**:
- `id` (String, UUID): Unique identifier for the appointment
- `customer_name` (String, required): Name of the customer receiving service
- `service_date` (DateTime, required): Date and time when service is scheduled
- `service_type` (String, required): Type of service to be performed
- `volatility_level` (Enum, required): Customer's flexibility for rescheduling
  - Values: `low`, `medium`, `high`
- `observations` (Text, optional): Additional notes about the service
- `required_tools` (Array of Strings, optional): Tools needed for the service
- `status` (Enum, required): Current status of the appointment
  - Values: `pending`, `in_progress`, `completed`
- `created_at` (DateTime, required): When the appointment was created
- `updated_at` (DateTime, required): When the appointment was last modified
- `occurrences` (Array of Occurrence, optional): History of changes to the appointment

**Validation Rules**:
- `customer_name`: Minimum 2 characters, maximum 100 characters
- `service_date`: Must be in the future when creating new appointments
- `service_type`: Minimum 2 characters, maximum 50 characters
- `observations`: Maximum 500 characters
- `required_tools`: Maximum 10 items, each maximum 50 characters

**State Transitions**:
```
pending → in_progress → completed
pending → completed (direct completion allowed)
in_progress → completed
```

### Occurrence

Historical record of changes made to an appointment over time.

**Fields**:
- `id` (String, UUID): Unique identifier for the occurrence
- `appointment_id` (String, required): Reference to the parent appointment
- `timestamp` (DateTime, required): When the occurrence was created
- `type` (Enum, required): Type of occurrence
  - Values: `status_change`, `reschedule`, `modification`, `completion`
- `description` (Text, required): Human-readable description of the change
- `previous_data` (Object, optional): Snapshot of appointment data before change
- `new_data` (Object, optional): Snapshot of appointment data after change

**Validation Rules**:
- `description`: Minimum 5 characters, maximum 200 characters
- `previous_data` and `new_data`: Valid JSON objects

## Entity Relationships

### Appointment ↔ Occurrence (One-to-Many)

One appointment can have multiple occurrences, but each occurrence belongs to exactly one appointment.

**Relationship Details**:
- `appointment.occurrences` → Array of occurrence objects
- `occurrence.appointment_id` → References parent appointment ID
- Cascade delete: Deleting an appointment removes all associated occurrences

## Data Storage Format

### File Structure

All data is stored in a single `appointments.txt` file using JSON format:

```json
{
  "appointments": [
    {
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
  ],
  "metadata": {
    "last_updated": "2025-12-09T14:30:00",
    "version": "1.0",
    "total_appointments": 1
  }
}
```

### Backup Strategy

Before any write operation, a backup is created with timestamp:
- `appointments_backup_20251209_143000.txt`

## Business Logic Constraints

### Appointment Priority Calculation

Appointments are sorted by priority using the following algorithm:

1. **Delayed appointments** (service_date < now AND status != completed)
   - Sort by delay duration (most delayed first)

2. **Upcoming appointments** (service_date >= now AND status == pending)
   - Calculate priority score: `(volatility_weight * 0.6) + (proximity_weight * 0.4)`
   - Volatility weights: high=1.0, medium=0.6, low=0.3
   - Proximity weight: Based on hours until service (closer = higher weight)
   - Sort by priority score (highest first)

3. **In-progress appointments** (status == in_progress)
   - Sort by start time (oldest first)

### AI Recommendation Logic

When AI recommends alternative appointments:

1. **Filter eligible appointments**:
   - Status must be `pending`
   - Service date must be within reasonable timeframe (next 7 days)
   - Exclude the appointment being rescheduled

2. **Calculate recommendation score**:
   ```
   score = (volatility_level_weight * 0.7) + (time_proximity_weight * 0.3)
   ```

3. **Rank and present**:
   - Top recommendation shown first
   - Up to 2 alternatives available if user rejects

### Occurrence Generation Rules

Occurrences are automatically generated when:

1. **Status changes**: From any status to another status
2. **Rescheduling**: When service_date is modified
3. **Field modifications**: When any field is edited (except status)
4. **Completion**: When status changes to `completed`

## Data Integrity Rules

### Unique Constraints

- `appointment.id`: Must be unique across all appointments
- `occurrence.id`: Must be unique across all occurrences

### Referential Integrity

- `occurrence.appointment_id`: Must reference a valid appointment ID
- Occurrences cannot exist without their parent appointment

### Consistency Rules

- `appointment.updated_at` must be >= `appointment.created_at`
- `occurrence.timestamp` must be <= `appointment.updated_at`
- All dates must be in ISO 8601 format
- Status transitions must follow defined state machine

## Performance Considerations

### File Access Patterns

1. **Read operations**: Load entire file into memory, parse JSON
2. **Write operations**: Modify in-memory representation, write entire file atomically
3. **Search operations**: Filter in-memory array, no file system searches

### Memory Usage

- Estimated memory usage: ~1KB per appointment
- Maximum recommended appointments: 10,000 (≈10MB memory usage)
- For larger datasets, implement pagination or file splitting

### Caching Strategy

- Backend: In-memory cache of appointment data
- Frontend: Local storage cache for offline viewing
- Cache invalidation: When file timestamp changes

## Security Considerations

### Input Sanitization

- All string fields: Strip HTML tags, escape special characters
- Date fields: Validate format and range
- Enum fields: Validate against allowed values

### File Access Control

- File permissions: Read/write for application user only
- Backup files: Same permissions as main file
- Temporary files: Clean up after operations

### Data Privacy

- Customer names: No PII beyond what's necessary for scheduling
- Observations: May contain sensitive information, handle with care
- Access logging: Log file access for audit purposes