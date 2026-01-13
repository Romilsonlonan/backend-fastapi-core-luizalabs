from abc import ABC, abstractmethod
from typing import List, Optional
from ... import models

class IClubRepository(ABC):
    @abstractmethod
    def create(self, club_data: dict) -> models.Club:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Club]:
        pass

    @abstractmethod
    def get_by_id(self, club_id: int) -> Optional[models.Club]:
        pass

    @abstractmethod
    def get_with_players(self, club_id: int) -> Optional[models.Club]:
        pass

    @abstractmethod
    def update(self, db_club: models.Club, update_data: dict) -> models.Club:
        pass

    @abstractmethod
    def delete(self, db_club: models.Club) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
