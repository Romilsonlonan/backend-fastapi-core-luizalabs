from sqlalchemy.orm import Session
from .. import models, schemas


def create_goalkeeper(db: Session, goalkeeper: schemas.GoalkeeperCreate):
    club = db.query(models.Club).filter(models.Club.id == goalkeeper.club_id).first()
    if not club:
        raise ValueError(f"Clube com ID {goalkeeper.club_id} não encontrado")

    db_goalkeeper = models.Goalkeeper(
        **goalkeeper.model_dump()
    )
    db.add(db_goalkeeper)
    db.commit()
    db.refresh(db_goalkeeper)
    return db_goalkeeper


def get_goalkeepers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    club_id: int | None = None,
    name: str | None = None,
):
    query = db.query(models.Goalkeeper)

    if club_id is not None:
        query = query.filter(models.Goalkeeper.club_id == club_id)

    if name:
        query = query.filter(models.Goalkeeper.name.ilike(f"%{name}%"))

    return query.offset(skip).limit(limit).all()


def get_goalkeeper(db: Session, goalkeeper_id: int):
    return db.query(models.Goalkeeper).filter(models.Goalkeeper.id == goalkeeper_id).first()


def update_goalkeeper(
    db: Session, goalkeeper_id: int, goalkeeper_update: schemas.GoalkeeperUpdate
):
    db_goalkeeper = get_goalkeeper(db, goalkeeper_id)
    if not db_goalkeeper:
        return None

    update_data = goalkeeper_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_goalkeeper, field, value)

    db.commit()
    db.refresh(db_goalkeeper)
    return db_goalkeeper


def delete_goalkeeper(db: Session, goalkeeper_id: int):
    db_goalkeeper = get_goalkeeper(db, goalkeeper_id)
    if not db_goalkeeper:
        return False

    db.delete(db_goalkeeper)
    db.commit()
    return True
