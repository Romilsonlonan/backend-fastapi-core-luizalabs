from typing import Dict
from ...core.exceptions import DomainException

class AthleteDomain:
    @staticmethod
    def validate_health_data(data: Dict) -> None:
        if "body_fat" in data and (data["body_fat"] < 0 or data["body_fat"] > 100):
            raise DomainException("Percentual de gordura inválido.")
        
        if "muscle_mass" in data and data["muscle_mass"] < 0:
            raise DomainException("Massa muscular não pode ser negativa.")

    @staticmethod
    def validate_progress_data(data: Dict) -> None:
        if not data.get("week"):
            raise DomainException("A semana é obrigatória para o progresso.")
        
        if data.get("weight", 0) <= 0:
            raise DomainException("O peso deve ser maior que zero.")

    @staticmethod
    def validate_nutritional_plan(data: Dict) -> None:
        if not data.get("plan_details"):
            raise DomainException("Os detalhes do plano nutricional são obrigatórios.")
