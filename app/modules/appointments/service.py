from typing import List, Optional
from datetime import datetime
from .interfaces import IAppointmentRepository
from .domain import AppointmentDomain
from ... import schemas
from ...core.exceptions import NotFoundException

class AppointmentService:
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
        self.domain = AppointmentDomain()

    def get_appointments(self, nutritionist_id: Optional[int], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        return self.repository.get_appointments(nutritionist_id, start_date, end_date)

    def create_appointment(self, appointment_schema: schemas.AppointmentCreate):
        data = appointment_schema.model_dump()
        self.domain.validate_appointment_data(data)
        return self.repository.create_appointment(data)

    def update_appointment_status(self, appointment_id: int, status: str):
        db_appointment = self.repository.get_by_id(appointment_id)
        if not db_appointment:
            raise NotFoundException("Consulta não encontrada")
        return self.repository.update(db_appointment, {"status": status})

    def update_appointment(self, appointment_id: int, appointment_update: schemas.AppointmentBase):
        db_appointment = self.repository.get_by_id(appointment_id)
        if not db_appointment:
            raise NotFoundException("Consulta não encontrada")
        
        update_data = appointment_update.model_dump(exclude_unset=True)
        # Validate if times are being updated
        if "start_time" in update_data or "end_time" in update_data:
            temp_data = {
                "start_time": update_data.get("start_time", db_appointment.start_time),
                "end_time": update_data.get("end_time", db_appointment.end_time)
            }
            self.domain.validate_appointment_data(temp_data)
            
        return self.repository.update(db_appointment, update_data)

    def delete_appointment(self, appointment_id: int):
        db_appointment = self.repository.get_by_id(appointment_id)
        if not db_appointment:
            raise NotFoundException("Consulta não encontrada")
        return self.repository.delete(db_appointment)

    def get_services(self):
        return self.repository.get_services()

    def create_service(self, service_schema: schemas.ServiceCreate):
        return self.repository.create_service(service_schema.model_dump())

    def get_locations(self):
        return self.repository.get_locations()

    def create_location(self, location_schema: schemas.LocationCreate):
        return self.repository.create_location(location_schema.model_dump())

    def get_availabilities(self, user_id: int):
        return self.repository.get_availabilities(user_id)

    def update_availability(self, availability_schema: schemas.AvailabilityCreate):
        data = availability_schema.model_dump()
        self.domain.validate_availability_data(data)
        user_id = data.pop("user_id")
        day_of_week = data.pop("day_of_week")
        return self.repository.update_availability(user_id, day_of_week, data)
