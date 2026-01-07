from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime

def get_appointments(db: Session, nutritionist_id: int, start_date: datetime = None, end_date: datetime = None):
    query = db.query(models.Appointment).filter(models.Appointment.nutritionist_id == nutritionist_id)
    if start_date:
        query = query.filter(models.Appointment.start_time >= start_date)
    if end_date:
        query = query.filter(models.Appointment.start_time <= end_date)
    return query.all()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment_status(db: Session, appointment_id: int, status: str):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = status
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentBase):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        update_data = appointment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_appointment, key, value)
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
        return True
    return False

def get_services(db: Session):
    return db.query(models.Service).filter(models.Service.is_active == True).all()

def create_service(db: Session, service: schemas.ServiceCreate):
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_locations(db: Session):
    return db.query(models.Location).filter(models.Location.is_active == True).all()

def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_availabilities(db: Session, user_id: int):
    return db.query(models.Availability).filter(models.Availability.user_id == user_id).all()

def update_availability(db: Session, availability: schemas.AvailabilityCreate):
    db_availability = db.query(models.Availability).filter(
        models.Availability.user_id == availability.user_id,
        models.Availability.day_of_week == availability.day_of_week
    ).first()
    
    if db_availability:
        db_availability.start_time = availability.start_time
        db_availability.end_time = availability.end_time
        db_availability.is_active = availability.is_active
    else:
        db_availability = models.Availability(**availability.model_dump())
        db.add(db_availability)
    
    db.commit()
    db.refresh(db_availability)
    return db_availability
