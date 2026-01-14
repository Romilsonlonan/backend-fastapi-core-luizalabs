from abc import ABC, abstractmethod
from typing import List, Optional
from ... import models

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[models.User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[models.User]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        pass

    @abstractmethod
    def create(self, user_data: dict) -> models.User:
        pass

    @abstractmethod
    def update(self, db_user: models.User, update_data: dict) -> models.User:
        pass

    @abstractmethod
    def delete(self, db_user: models.User) -> bool:
        pass
