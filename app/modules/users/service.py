import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from .interfaces import IUserRepository
from .domain import UserDomain
from ... import schemas
from ...core.exceptions import NotFoundException, DomainException
from ...security import get_password_hash, verify_password, create_access_token
from ...config import settings
from ..common.email_service import EmailService


RESET_PASSWORD_REGEX = re.compile(r'^[A-Z][a-zA-Z0-9]{5,7}$')

class UserService:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
        self.domain = UserDomain()
        self.email_service = EmailService()

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

    def request_password_reset(self, email: str) -> None:
        user = self.repository.get_by_email(email.lower())
        if not user:
            return

        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )

        self.repository.create_password_reset_token(
            user_id=user.id, token=token, expires_at=expires_at
        )

        base = settings.FRONTEND_BASE_URL.rstrip('/')
        reset_link = f"{base}/login?token={token}"

        # Importante: não deixar exception estourar para não virar 500 e vazar diferença
        # entre e-mail existente e inexistente.
        try:
            self.email_service.send_password_reset_email(user.email, reset_link)
        except Exception as e:
            # Mantemos silencioso para o cliente; logamos no backend para facilitar diagnóstico.
            print(f"[forgot-password] Falha ao enviar e-mail para {user.email}: {e}", flush=True)

    def reset_password(self, token: str, new_password: str) -> None:
        if not RESET_PASSWORD_REGEX.match(new_password):
            raise DomainException(
                'Senha inválida. Use 6-8 caracteres, sem especiais, começando com maiúscula.'
            )

        reset_token = self.repository.get_password_reset_token(token)
        if not reset_token:
            raise DomainException('Token inválido ou expirado')

        now = datetime.utcnow()
        if reset_token.used_at is not None or reset_token.expires_at < now:
            raise DomainException('Token inválido ou expirado')

        user = self.repository.get_by_id(reset_token.user_id)
        if not user:
            raise NotFoundException('Usuário não encontrado')

        hashed_password = get_password_hash(new_password)
        self.repository.update(user, {'hashed_password': hashed_password})
        self.repository.mark_password_reset_token_used(reset_token)
