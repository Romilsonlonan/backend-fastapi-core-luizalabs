from typing import List, Optional
from sqlalchemy.orm import Session
from ... import models
from .interfaces import ITrainingRepository

class TrainingRepository(ITrainingRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_routine(self, routine_data: dict) -> models.TrainingRoutine:
        db_routine = models.TrainingRoutine(**routine_data)
        self.db.add(db_routine)
        self.db.commit()
        self.db.refresh(db_routine)
        return db_routine

    def get_routines(self, skip: int, limit: int, club_id: Optional[int]) -> List[models.TrainingRoutine]:
        query = self.db.query(models.TrainingRoutine)
        if club_id:
            query = query.filter(models.TrainingRoutine.club_id == club_id)
        return query.offset(skip).limit(limit).all()

    def get_routine_by_id(self, routine_id: int) -> Optional[models.TrainingRoutine]:
        return self.db.query(models.TrainingRoutine).filter(models.TrainingRoutine.id == routine_id).first()

    def update_routine(self, db_routine: models.TrainingRoutine, update_data: dict) -> models.TrainingRoutine:
        for key, value in update_data.items():
            setattr(db_routine, key, value)
        self.db.commit()
        self.db.refresh(db_routine)
        return db_routine

    def delete_routine(self, db_routine: models.TrainingRoutine) -> bool:
        self.db.delete(db_routine)
        self.db.commit()
        return True
