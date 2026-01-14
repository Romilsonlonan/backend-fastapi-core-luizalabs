from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ... import models

class IAppointmentRepository(ABC):
    @abstractmethod
    def get_appointments(self, nutritionist_id: int, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[models.Appointment]:
        pass

    @abstractmethod
    def create_appointment(self, appointment_data: dict) -> models.Appointment:
        pass

    @abstractmethod
    def get_by_id(self, appointment_id: int) -> Optional[models.Appointment]:
        pass

    @abstractmethod
    def update(self, db_appointment: models.Appointment, update_data: dict) -> models.Appointment:
        pass

    @abstractmethod
    def delete(self, db_appointment: models.Appointment) -> bool:
        pass

    @abstractmethod
    def get_services(self) -> List[models.Service]:
        pass

    @abstractmethod
    def create_service(self, service_data: dict) -> models.Service:
        pass

    @abstractmethod
    def get_locations(self) -> List[models.Location]:
        pass

    @abstractmethod
    def create_location(self, location_data: dict) -> models.Location:
        pass

    @abstractmethod
    def get_availabilities(self, user_id: int) -> List[models.Availability]:
        pass

    @abstractmethod
    def update_availability(self, user_id: int, day_of_week: int, availability_data: dict) -> models.Availability:
        pass
