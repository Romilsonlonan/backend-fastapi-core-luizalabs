from typing import List, Optional, Union
from .interfaces import IAthleteRepository
from .domain import AthleteDomain
from ... import schemas
from ...core.exceptions import NotFoundException

class AthleteService:
    def __init__(self, repository: IAthleteRepository):
        self.repository = repository
        self.domain = AthleteDomain()

    def update_health(self, athlete_id: int, is_goalkeeper: bool, health_data: schemas.AthleteHealthUpdate):
        athlete = self._get_athlete(athlete_id, is_goalkeeper)
        data = health_data.model_dump(exclude_unset=True)
        self.domain.validate_health_data(data)
        return self.repository.update_health(athlete, data)

    def create_progress(self, progress_schema: schemas.AthleteProgressCreate):
        data = progress_schema.model_dump()
        self.domain.validate_progress_data(data)
        return self.repository.create_progress(data)

    def get_progress(self, athlete_id: int, is_goalkeeper: bool):
        self._get_athlete(athlete_id, is_goalkeeper) # Validate existence
        return self.repository.get_progress(athlete_id, is_goalkeeper)

    def create_nutritional_plan(self, plan_schema: schemas.NutritionalPlanCreate):
        data = plan_schema.model_dump()
        self.domain.validate_nutritional_plan(data)
        return self.repository.create_nutritional_plan(data)

    def get_nutritional_plans(self, athlete_id: int, is_goalkeeper: bool):
        self._get_athlete(athlete_id, is_goalkeeper) # Validate existence
        return self.repository.get_nutritional_plans(athlete_id, is_goalkeeper)

    def delete_nutritional_plan(self, plan_id: int):
        success = self.repository.delete_nutritional_plan(plan_id)
        if not success:
            raise NotFoundException("Plano nutricional não encontrado")
        return True

    def get_top_goal_scorers(self, limit: int = 7, position: Optional[str] = None, club_id: Optional[int] = None):
        return self.repository.get_top_goal_scorers(limit, position, club_id)

    def get_field_players(self, skip: int = 0, limit: int = 100, club_id: Optional[int] = None, name: Optional[str] = None, position: Optional[str] = None):
        return self.repository.get_field_players(skip, limit, club_id, name, position)

    def get_goalkeepers(self, skip: int = 0, limit: int = 100, club_id: Optional[int] = None, name: Optional[str] = None):
        return self.repository.get_goalkeepers(skip, limit, club_id, name)

    def get_total_athletes_count(self) -> int:
        return self.repository.count_total_athletes()

    def _get_athlete(self, athlete_id: int, is_goalkeeper: bool):
        if is_goalkeeper:
            athlete = self.repository.get_goalkeeper_by_id(athlete_id)
        else:
            athlete = self.repository.get_field_player_by_id(athlete_id)
        
        if not athlete:
            raise NotFoundException("Atleta não encontrado")
        return athlete
