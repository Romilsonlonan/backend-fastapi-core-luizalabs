import os
import uuid
from typing import Tuple, Dict
from ...core.exceptions import DomainException

class ClubDomain:
    """
    Camada de Domain Rules: Contém a lógica pura do domínio, 
    independente de frameworks ou banco de dados.
    """
    
    @staticmethod
    def validate_club_data(data: Dict) -> None:
        """
        Validações complexas de domínio para o clube.
        """
        if not data.get("name"):
            raise DomainException("O nome do clube é obrigatório.")
        
        if len(data.get("name", "")) < 3:
            raise DomainException("O nome do clube deve ter pelo menos 3 caracteres.")

        if not data.get("initials"):
            raise DomainException("As iniciais do clube são obrigatórias.")

    @staticmethod
    def format_initials(initials: str) -> str:
        if not initials:
            return ""
        return initials.upper()[:3]
