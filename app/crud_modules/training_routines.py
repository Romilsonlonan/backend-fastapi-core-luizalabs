from sqlalchemy.orm import Session

from .. import models, schemas


# -------------------------------------------------------------------------
# CREATE
# -------------------------------------------------------------------------
def create_training_routine(
    db: Session,
    routine: schemas.TrainingRoutineCreate,
):
    club = db.query(models.Club).filter(
        models.Club.id == routine.club_id
    ).first()

    if not club:
        raise ValueError(f"Clube com ID {routine.club_id} não encontrado")

    db_routine = models.TrainingRoutine(
        **routine.model_dump()
    )

    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine


# -------------------------------------------------------------------------
# READ
# -------------------------------------------------------------------------
def get_training_routine(db: Session, routine_id: int):
    return db.query(models.TrainingRoutine).filter(
        models.TrainingRoutine.id == routine_id
    ).first()


def get_training_routines(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    club_id: int | None = None,
):
    query = db.query(models.TrainingRoutine)

    if club_id is not None:
        query = query.filter(models.TrainingRoutine.club_id == club_id)

    return query.offset(skip).limit(limit).all()


# -------------------------------------------------------------------------
# UPDATE
# -------------------------------------------------------------------------
def update_training_routine(
    db: Session,
    routine_id: int,
    routine_update: schemas.TrainingRoutineUpdate,
):
    db_routine = get_training_routine(db, routine_id)
    if not db_routine:
        return None

    update_data = routine_update.model_dump(exclude_unset=True)

    # Se permitir atualização de club_id, validar novamente
    if "club_id" in update_data:
        club = db.query(models.Club).filter(
            models.Club.id == update_data["club_id"]
        ).first()
        if not club:
            raise ValueError(
                f"Clube com ID {update_data['club_id']} não encontrado"
            )

    for field, value in update_data.items():
        setattr(db_routine, field, value)

    db.commit()
    db.refresh(db_routine)
    return db_routine


# -------------------------------------------------------------------------
# DELETE
# -------------------------------------------------------------------------
def delete_training_routine(db: Session, routine_id: int):
    db_routine = get_training_routine(db, routine_id)
    if not db_routine:
        return False

    db.delete(db_routine)
    db.commit()
    return True
