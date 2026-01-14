import re
from typing import Dict
from ...core.exceptions import DomainException

class UserDomain:
    @staticmethod
    def validate_user_data(data: Dict) -> None:
        if not data.get("email"):
            raise DomainException("O email é obrigatório.")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            raise DomainException("Formato de email inválido.")

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < 6:
            raise DomainException("A senha deve ter pelo menos 6 caracteres.")
