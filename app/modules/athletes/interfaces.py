from abc import ABC, abstractmethod
from typing import List, Optional, Union
from ... import models

class IAthleteRepository(ABC):
    @abstractmethod
    def get_goalkeeper_by_id(self, athlete_id: int) -> Optional[models.Goalkeeper]:
        pass

    @abstractmethod
    def get_field_player_by_id(self, athlete_id: int) -> Optional[models.FieldPlayer]:
        pass

    @abstractmethod
    def update_health(self, athlete: Union[models.Goalkeeper, models.FieldPlayer], health_data: dict) -> Union[models.Goalkeeper, models.FieldPlayer]:
        pass

    @abstractmethod
    def create_progress(self, progress_data: dict) -> models.AthleteProgress:
        pass

    @abstractmethod
    def get_progress(self, athlete_id: int, is_goalkeeper: bool) -> List[models.AthleteProgress]:
        pass

    @abstractmethod
    def create_nutritional_plan(self, plan_data: dict) -> models.NutritionalPlan:
        pass

    @abstractmethod
    def get_nutritional_plans(self, athlete_id: int, is_goalkeeper: bool) -> List[models.NutritionalPlan]:
        pass

    @abstractmethod
    def delete_nutritional_plan(self, plan_id: int) -> bool:
        pass

    @abstractmethod
    def get_top_goal_scorers(self, limit: int, position: Optional[str], club_id: Optional[int]) -> List[models.FieldPlayer]:
        pass

    @abstractmethod
    def get_field_players(self, skip: int, limit: int, club_id: Optional[int], name: Optional[str], position: Optional[str]) -> List[models.FieldPlayer]:
        pass

    @abstractmethod
    def get_goalkeepers(self, skip: int, limit: int, club_id: Optional[int], name: Optional[str]) -> List[models.Goalkeeper]:
        pass

    @abstractmethod
    def count_total_athletes(self) -> int:
        pass
