from abc import ABC, abstractmethod
from datetime import datetime
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
    def create_password_reset_token(
        self, *, user_id: int, token: str, expires_at: datetime
    ) -> models.PasswordResetToken:
        pass

    @abstractmethod
    def get_password_reset_token(self, token: str) -> Optional[models.PasswordResetToken]:
        pass

    @abstractmethod
    def mark_password_reset_token_used(
        self, reset_token: models.PasswordResetToken
    ) -> models.PasswordResetToken:
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
