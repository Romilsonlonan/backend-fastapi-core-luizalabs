from sqlalchemy.orm import Session
from ... import models, schemas
from .interfaces import IClubRepository

class ClubRepository(IClubRepository):
    """
    Camada de Repositories: Responsável apenas pelo acesso ao banco de dados.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, club_data: dict) -> models.Club:
        db_club = models.Club(**club_data)
        self.db.add(db_club)
        self.db.commit()
        self.db.refresh(db_club)
        return db_club

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(models.Club).offset(skip).limit(limit).all()

    def get_by_id(self, club_id: int):
        return self.db.query(models.Club).filter(models.Club.id == club_id).first()

    def get_with_players(self, club_id: int):
        club = self.get_by_id(club_id)
        if club:
            # Trigger lazy loading or use joinedload in a real scenario
            _ = club.goalkeepers
            _ = club.field_players
        return club

    def update(self, db_club: models.Club, update_data: dict) -> models.Club:
        for field, value in update_data.items():
            setattr(db_club, field, value)
        self.db.commit()
        self.db.refresh(db_club)
        return db_club

    def delete(self, db_club: models.Club) -> bool:
        self.db.delete(db_club)
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(models.Club).count()
