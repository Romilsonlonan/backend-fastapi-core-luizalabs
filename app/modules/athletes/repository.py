from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ... import models
from .interfaces import IAthleteRepository

class AthleteRepository(IAthleteRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_goalkeeper_by_id(self, athlete_id: int) -> Optional[models.Goalkeeper]:
        return self.db.query(models.Goalkeeper).filter(models.Goalkeeper.id == athlete_id).first()

    def get_field_player_by_id(self, athlete_id: int) -> Optional[models.FieldPlayer]:
        return self.db.query(models.FieldPlayer).filter(models.FieldPlayer.id == athlete_id).first()

    def update_health(self, athlete: Union[models.Goalkeeper, models.FieldPlayer], health_data: dict) -> Union[models.Goalkeeper, models.FieldPlayer]:
        for key, value in health_data.items():
            setattr(athlete, key, value)
        self.db.commit()
        self.db.refresh(athlete)
        return athlete

    def create_progress(self, progress_data: dict) -> models.AthleteProgress:
        db_progress = models.AthleteProgress(**progress_data)
        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress

    def get_progress(self, athlete_id: int, is_goalkeeper: bool) -> List[models.AthleteProgress]:
        if is_goalkeeper:
            return self.db.query(models.AthleteProgress).filter(models.AthleteProgress.goalkeeper_id == athlete_id).all()
        return self.db.query(models.AthleteProgress).filter(models.AthleteProgress.field_player_id == athlete_id).all()

    def create_nutritional_plan(self, plan_data: dict) -> models.NutritionalPlan:
        db_plan = models.NutritionalPlan(**plan_data)
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)
        return db_plan

    def get_nutritional_plans(self, athlete_id: int, is_goalkeeper: bool) -> List[models.NutritionalPlan]:
        if is_goalkeeper:
            return self.db.query(models.NutritionalPlan).filter(models.NutritionalPlan.goalkeeper_id == athlete_id).order_by(desc(models.NutritionalPlan.date)).all()
        return self.db.query(models.NutritionalPlan).filter(models.NutritionalPlan.field_player_id == athlete_id).order_by(desc(models.NutritionalPlan.date)).all()

    def delete_nutritional_plan(self, plan_id: int) -> bool:
        db_plan = self.db.query(models.NutritionalPlan).filter(models.NutritionalPlan.id == plan_id).first()
        if db_plan:
            self.db.delete(db_plan)
            self.db.commit()
            return True
        return False

    def get_top_goal_scorers(self, limit: int, position: Optional[str], club_id: Optional[int]) -> List[models.FieldPlayer]:
        query = self.db.query(models.FieldPlayer).filter(models.FieldPlayer.goals > 0)
        if position:
            query = query.filter(models.FieldPlayer.position == position)
        if club_id:
            query = query.filter(models.FieldPlayer.club_id == club_id)
        return query.order_by(desc(models.FieldPlayer.goals)).limit(limit).all()

    def get_field_players(self, skip: int, limit: int, club_id: Optional[int], name: Optional[str], position: Optional[str]) -> List[models.FieldPlayer]:
        query = self.db.query(models.FieldPlayer)
        if club_id:
            query = query.filter(models.FieldPlayer.club_id == club_id)
        if name:
            query = query.filter(models.FieldPlayer.name.ilike(f"%{name}%"))
        if position:
            query = query.filter(models.FieldPlayer.position == position)
        return query.offset(skip).limit(limit).all()

    def get_goalkeepers(self, skip: int, limit: int, club_id: Optional[int], name: Optional[str]) -> List[models.Goalkeeper]:
        query = self.db.query(models.Goalkeeper)
        if club_id:
            query = query.filter(models.Goalkeeper.club_id == club_id)
        if name:
            query = query.filter(models.Goalkeeper.name.ilike(f"%{name}%"))
        return query.offset(skip).limit(limit).all()

    def count_total_athletes(self) -> int:
        total_field_players = self.db.query(models.FieldPlayer).count()
        total_goalkeepers = self.db.query(models.Goalkeeper).count()
        return total_field_players + total_goalkeepers
