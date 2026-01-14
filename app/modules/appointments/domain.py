from typing import Dict
from datetime import datetime
from ...core.exceptions import DomainException

class AppointmentDomain:
    @staticmethod
    def validate_appointment_data(data: Dict) -> None:
        if not data.get("start_time"):
            raise DomainException("O horário de início é obrigatório.")
        
        if not data.get("end_time"):
            raise DomainException("O horário de término é obrigatório.")

        if data["start_time"] >= data["end_time"]:
            raise DomainException("O horário de início deve ser anterior ao horário de término.")

    @staticmethod
    def validate_availability_data(data: Dict) -> None:
        if "start_time" in data and "end_time" in data:
            if data["start_time"] >= data["end_time"]:
                raise DomainException("O horário de início da disponibilidade deve ser anterior ao término.")
