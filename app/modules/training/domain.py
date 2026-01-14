from typing import Dict
from ...core.exceptions import DomainException

class TrainingDomain:
    @staticmethod
    def validate_routine_data(data: Dict) -> None:
        if not data.get("day_of_week"):
            raise DomainException("O dia da semana é obrigatório.")
        
        if not data.get("activity"):
            raise DomainException("A atividade é obrigatória.")

        valid_days = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        if data.get("day_of_week") not in valid_days:
            raise DomainException(f"Dia da semana inválido. Deve ser um de: {', '.join(valid_days)}")
