from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ... import models
from .interfaces import IAppointmentRepository

class AppointmentRepository(IAppointmentRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_appointments(self, nutritionist_id: Optional[int], start_date: Optional[datetime], end_date: Optional[datetime]) -> List[models.Appointment]:
        query = self.db.query(models.Appointment)
        if nutritionist_id is not None:
            query = query.filter(models.Appointment.nutritionist_id == nutritionist_id)
        if start_date:
            query = query.filter(models.Appointment.start_time >= start_date)
        if end_date:
            query = query.filter(models.Appointment.start_time <= end_date)
        return query.all()

    def create_appointment(self, appointment_data: dict) -> models.Appointment:
        db_appointment = models.Appointment(**appointment_data)
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def get_by_id(self, appointment_id: int) -> Optional[models.Appointment]:
        return self.db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    def update(self, db_appointment: models.Appointment, update_data: dict) -> models.Appointment:
        for key, value in update_data.items():
            setattr(db_appointment, key, value)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def delete(self, db_appointment: models.Appointment) -> bool:
        self.db.delete(db_appointment)
        self.db.commit()
        return True

    def get_services(self) -> List[models.Service]:
        return self.db.query(models.Service).filter(models.Service.is_active == True).all()

    def create_service(self, service_data: dict) -> models.Service:
        db_service = models.Service(**service_data)
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        return db_service

    def get_locations(self) -> List[models.Location]:
        return self.db.query(models.Location).filter(models.Location.is_active == True).all()

    def create_location(self, location_data: dict) -> models.Location:
        db_location = models.Location(**location_data)
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def get_availabilities(self, user_id: int) -> List[models.Availability]:
        return self.db.query(models.Availability).filter(models.Availability.user_id == user_id).all()

    def update_availability(self, user_id: int, day_of_week: int, availability_data: dict) -> models.Availability:
        db_availability = self.db.query(models.Availability).filter(
            models.Availability.user_id == user_id,
            models.Availability.day_of_week == day_of_week
        ).first()
        
        if db_availability:
            for key, value in availability_data.items():
                setattr(db_availability, key, value)
        else:
            db_availability = models.Availability(user_id=user_id, day_of_week=day_of_week, **availability_data)
            self.db.add(db_availability)
        
        self.db.commit()
        self.db.refresh(db_availability)
        return db_availability
