from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...dependencies import get_current_active_user, get_db
from ... import schemas
from ...core.container import DIContainer
from .service import AppointmentService

router = APIRouter(tags=["Appointments"])

def get_appointment_service(db: Session = Depends(get_db)) -> AppointmentService:
    return DIContainer.get_appointment_service(db)

@router.get("/appointments/", response_model=List[schemas.AppointmentResponse])
def read_appointments(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    nutritionist_id: Optional[int] = None,
    current_user: schemas.User = Depends(get_current_active_user),
    service: AppointmentService = Depends(get_appointment_service),
):
    # Se nutritionist_id não for passado, retorna todas as consultas (ou você pode manter o filtro se preferir)
    # O usuário pediu para ver a agenda, então provavelmente quer ver tudo ou filtrar por profissional
    return service.get_appointments(nutritionist_id=nutritionist_id, start_date=start_date, end_date=end_date)

@router.post("/appointments/", response_model=schemas.AppointmentResponse)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_appointment(appointment)

@router.patch("/appointments/{appointment_id}/status", response_model=schemas.AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status: str,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.update_appointment_status(appointment_id, status)

@router.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentBase,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.update_appointment(appointment_id, appointment)

@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    service.delete_appointment(appointment_id)

@router.get("/services/", response_model=List[schemas.ServiceResponse])
def read_services(service: AppointmentService = Depends(get_appointment_service)):
    return service.get_services()

@router.post("/services/", response_model=schemas.ServiceResponse)
def create_service(
    service_schema: schemas.ServiceCreate,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_service(service_schema)

@router.get("/locations/", response_model=List[schemas.LocationResponse])
def read_locations(service: AppointmentService = Depends(get_appointment_service)):
    return service.get_locations()

@router.post("/locations/", response_model=schemas.LocationResponse)
def create_location(
    location: schemas.LocationCreate,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_location(location)

@router.get("/availabilities/", response_model=List[schemas.AvailabilityResponse])
def read_availabilities(
    current_user: schemas.User = Depends(get_current_active_user),
    service: AppointmentService = Depends(get_appointment_service),
):
    return service.get_availabilities(user_id=current_user.id)

@router.post("/availabilities/", response_model=schemas.AvailabilityResponse)
def update_availability(
    availability: schemas.AvailabilityCreate,
    service: AppointmentService = Depends(get_appointment_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.update_availability(availability)
