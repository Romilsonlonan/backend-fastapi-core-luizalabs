from sqlalchemy.orm import Session
from ..modules.clubs.repository import ClubRepository
from ..modules.clubs.service import ClubService
from ..modules.athletes.repository import AthleteRepository
from ..modules.athletes.service import AthleteService
from ..modules.training.repository import TrainingRepository
from ..modules.training.service import TrainingService
from ..modules.scraper.service import ScraperService
from ..modules.payments.service import PaymentService
from ..modules.appointments.repository import AppointmentRepository
from ..modules.appointments.service import AppointmentService
from ..modules.users.repository import UserRepository
from ..modules.users.service import UserService
from ..modules.common.file_service import FileService

class DIContainer:
    """
    Dependency Injection Container para centralizar a criação de instâncias.
    """
    @staticmethod
    def get_file_service() -> FileService:
        return FileService()

    @staticmethod
    def get_club_service(db: Session) -> ClubService:
        repository = ClubRepository(db)
        file_service = DIContainer.get_file_service()
        return ClubService(repository, file_service)

    @staticmethod
    def get_athlete_service(db: Session) -> AthleteService:
        repository = AthleteRepository(db)
        return AthleteService(repository)

    @staticmethod
    def get_training_service(db: Session) -> TrainingService:
        repository = TrainingRepository(db)
        return TrainingService(repository)

    @staticmethod
    def get_scraper_service(db: Session) -> ScraperService:
        athlete_repository = AthleteRepository(db)
        return ScraperService(athlete_repository)

    @staticmethod
    def get_appointment_service(db: Session) -> AppointmentService:
        repository = AppointmentRepository(db)
        return AppointmentService(repository)

    @staticmethod
    def get_user_service(db: Session) -> UserService:
        repository = UserRepository(db)
        return UserService(repository)

    @staticmethod
    def get_payment_service(db: Session) -> PaymentService:
        user_repository = UserRepository(db)
        return PaymentService(user_repository)
