from typing import List, Optional
from .interfaces import ITrainingRepository
from .domain import TrainingDomain
from ... import schemas
from ...core.exceptions import NotFoundException

class TrainingService:
    def __init__(self, repository: ITrainingRepository):
        self.repository = repository
        self.domain = TrainingDomain()

    def create_routine(self, routine_schema: schemas.TrainingRoutineCreate):
        data = routine_schema.model_dump()
        self.domain.validate_routine_data(data)
        return self.repository.create_routine(data)

    def get_routines(self, skip: int = 0, limit: int = 100, club_id: Optional[int] = None):
        return self.repository.get_routines(skip, limit, club_id)

    def get_routine_by_id(self, routine_id: int):
        routine = self.repository.get_routine_by_id(routine_id)
        if not routine:
            raise NotFoundException("Rotina de treinamento não encontrada")
        return routine

    def update_routine(self, routine_id: int, routine_update: schemas.TrainingRoutineUpdate):
        db_routine = self.get_routine_by_id(routine_id)
        update_data = routine_update.model_dump(exclude_unset=True)
        # Re-validate if critical fields are updated
        if "day_of_week" in update_data or "activity" in update_data:
            # Create a temporary dict to validate
            temp_data = {
                "day_of_week": update_data.get("day_of_week", db_routine.day_of_week),
                "activity": update_data.get("activity", db_routine.activity)
            }
            self.domain.validate_routine_data(temp_data)
        return self.repository.update_routine(db_routine, update_data)

    def delete_routine(self, routine_id: int):
        db_routine = self.get_routine_by_id(routine_id)
        return self.repository.delete(db_routine)
