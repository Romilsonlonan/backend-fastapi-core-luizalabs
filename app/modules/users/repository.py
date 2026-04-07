from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ... import models
from .interfaces import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create(self, user_data: dict) -> models.User:
        db_user = models.User(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, db_user: models.User, update_data: dict) -> models.User:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, db_user: models.User) -> bool:
        self.db.delete(db_user)
        self.db.commit()
        return True

    def create_password_reset_token(
        self, *, user_id: int, token: str, expires_at: datetime
    ) -> models.PasswordResetToken:
        db_token = models.PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used_at=None,
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_password_reset_token(self, token: str) -> Optional[models.PasswordResetToken]:
        return (
            self.db.query(models.PasswordResetToken)
            .filter(models.PasswordResetToken.token == token)
            .first()
        )

    def mark_password_reset_token_used(
        self, reset_token: models.PasswordResetToken
    ) -> models.PasswordResetToken:
        reset_token.used_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(reset_token)
        return reset_token
