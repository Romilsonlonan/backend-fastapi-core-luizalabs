from sqlalchemy.orm import Session
from .. import models, schemas


# -------------------------------------------------------------------------
# CREATE
# -------------------------------------------------------------------------
def create_field_player(
    db: Session,
    field_player: schemas.FieldPlayerCreate,
):
    club = db.query(models.Club).filter(
        models.Club.id == field_player.club_id
    ).first()

    if not club:
        raise ValueError(f"Clube com ID {field_player.club_id} não encontrado")

    db_field_player = models.FieldPlayer(
        **field_player.model_dump()
    )

    db.add(db_field_player)
    db.commit()
    db.refresh(db_field_player)
    return db_field_player


# -------------------------------------------------------------------------
# READ
# -------------------------------------------------------------------------
def get_field_player(db: Session, field_player_id: int):
    return db.query(models.FieldPlayer).filter(
        models.FieldPlayer.id == field_player_id
    ).first()


def get_field_players(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    club_id: int | None = None,
    name: str | None = None,
    position: str | None = None,
):
    query = db.query(models.FieldPlayer)

    if club_id is not None:
        query = query.filter(models.FieldPlayer.club_id == club_id)

    if name:
        query = query.filter(models.FieldPlayer.name.ilike(f"%{name}%"))

    if position:
        query = query.filter(models.FieldPlayer.position.ilike(f"%{position}%"))

    return query.offset(skip).limit(limit).all()


# -------------------------------------------------------------------------
# UPDATE
# -------------------------------------------------------------------------
def update_field_player(
    db: Session,
    field_player_id: int,
    field_player_update: schemas.FieldPlayerUpdate,
):
    db_field_player = get_field_player(db, field_player_id)
    if not db_field_player:
        return None

    update_data = field_player_update.model_dump(exclude_unset=True)

    if "club_id" in update_data:
        club = db.query(models.Club).filter(
            models.Club.id == update_data["club_id"]
        ).first()
        if not club:
            raise ValueError(
                f"Clube com ID {update_data['club_id']} não encontrado"
            )

    for field, value in update_data.items():
        setattr(db_field_player, field, value)

    db.commit()
    db.refresh(db_field_player)
    return db_field_player


# -------------------------------------------------------------------------
# DELETE
# -------------------------------------------------------------------------
def delete_field_player(db: Session, field_player_id: int):
    db_field_player = get_field_player(db, field_player_id)
    if not db_field_player:
        return False

    db.delete(db_field_player)
    db.commit()
    return True
