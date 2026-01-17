from typing import List, Optional
from .interfaces import IUserRepository
from .domain import UserDomain
from ... import schemas
from ...core.exceptions import NotFoundException, DomainException
from ...security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from ...config import settings

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
        self.domain = UserDomain()

    def register_user(self, user_schema: schemas.UserCreate):
        data = user_schema.model_dump()
        self.domain.validate_user_data(data)
        self.domain.validate_password(user_schema.password)
        
        if self.repository.get_by_email(user_schema.email):
            raise DomainException("Email já registrado")

        hashed_password = get_password_hash(user_schema.password)
        user_data = {
            "name": user_schema.name or "Usuário",
            "email": user_schema.email.lower(),
            "hashed_password": hashed_password,
            "profession": user_schema.profession,
            "subscription_status": user_schema.subscription_status or "free"
        }
        return self.repository.create(user_data)

    def authenticate_user(self, email: str, password: str):
        user = self.repository.get_by_email(email.lower())
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def update_profile(self, user_id: int, user_update: schemas.UserBase):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            self.domain.validate_user_data(update_data)
            
        return self.repository.update(user, update_data)

    def change_password(self, user_id: int, password_data: schemas.PasswordChange):
        user = self.repository.get_by_id(user_id)
        if not user or not verify_password(password_data.current_password, user.hashed_password):
            raise DomainException("Senha atual incorreta")
        
        self.domain.validate_password(password_data.new_password)
        hashed_password = get_password_hash(password_data.new_password)
        return self.repository.update(user, {"hashed_password": hashed_password})

    def update_profile_image(self, user_id: int, image_url: str):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")
        return self.repository.update(user, {"profile_image_url": image_url})

    def delete_user(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")
        return self.repository.delete(user)

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)
