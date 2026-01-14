from abc import ABC, abstractmethod
from typing import List, Optional
from ... import models

class ITrainingRepository(ABC):
    @abstractmethod
    def create_routine(self, routine_data: dict) -> models.TrainingRoutine:
        pass

    @abstractmethod
    def get_routines(self, skip: int, limit: int, club_id: Optional[int]) -> List[models.TrainingRoutine]:
        pass

    @abstractmethod
    def get_routine_by_id(self, routine_id: int) -> Optional[models.TrainingRoutine]:
        pass

    @abstractmethod
    def update_routine(self, db_routine: models.TrainingRoutine, update_data: dict) -> models.TrainingRoutine:
        pass

    @abstractmethod
    def delete_routine(self, db_routine: models.TrainingRoutine) -> bool:
        pass
