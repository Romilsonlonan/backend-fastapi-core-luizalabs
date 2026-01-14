from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...dependencies import get_current_active_user, get_db
from ... import schemas
from ...core.container import DIContainer
from .service import TrainingService

router = APIRouter(prefix="/training_routines", tags=["Training Routines"])

def get_training_service(db: Session = Depends(get_db)) -> TrainingService:
    return DIContainer.get_training_service(db)

@router.post("/", response_model=schemas.TrainingRoutineResponse)
def create_training_routine(
    routine: schemas.TrainingRoutineCreate,
    service: TrainingService = Depends(get_training_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_routine(routine)

@router.get("/", response_model=List[schemas.TrainingRoutineResponse])
def read_training_routines(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    service: TrainingService = Depends(get_training_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_routines(skip, limit, club_id)

@router.get("/{routine_id}", response_model=schemas.TrainingRoutineResponse)
def read_training_routine(
    routine_id: int,
    service: TrainingService = Depends(get_training_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_routine_by_id(routine_id)

@router.put("/{routine_id}", response_model=schemas.TrainingRoutineResponse)
def update_training_routine(
    routine_id: int,
    routine: schemas.TrainingRoutineUpdate,
    service: TrainingService = Depends(get_training_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.update_routine(routine_id, routine)

@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_routine(
    routine_id: int,
    service: TrainingService = Depends(get_training_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    service.delete_routine(routine_id)
