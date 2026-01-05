import os
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas


def create_club(db: Session, club: schemas.ClubCreate, shield_file: UploadFile = None, banner_file: UploadFile = None):
    shield_url = None
    banner_url = None

    if shield_file:
        if not shield_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Apenas imagens são permitidas para o escudo.")
        if shield_file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagem do escudo muito grande (máximo 5MB).")
        file_ext = os.path.splitext(shield_file.filename)[1]
        file_name = f"shield_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploaded_images", file_name)
        try:
            with open(file_path, "wb") as buffer:
                content = shield_file.file.read()
                buffer.write(content)
            shield_url = f"/uploaded_images/{file_name}"
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao salvar imagem do escudo.")

    if banner_file:
        if not banner_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Apenas imagens são permitidas para o banner.")
        if banner_file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagem do banner muito grande (máximo 5MB).")
        file_ext = os.path.splitext(banner_file.filename)[1]
        file_name = f"banner_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploaded_images", file_name)
        try:
            with open(file_path, "wb") as buffer:
                content = banner_file.file.read()
                buffer.write(content)
            banner_url = f"/uploaded_images/{file_name}"
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao salvar imagem do banner.")

    initials = club.initials.upper()[:3]
    
    db_club = models.Club(
        name=club.name,
        initials=initials,
        city=club.city,
        shield_image_url=shield_url,
        foundation_date=club.foundation_date,
        br_titles=club.br_titles or 0,
        training_center=club.training_center,
        espn_url=club.espn_url,
        banner_image_url=banner_url
    )

    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


def get_clubs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Club).offset(skip).limit(limit).all()


def get_club(db: Session, club_id: int):
    return db.query(models.Club).filter(models.Club.id == club_id).first()


def get_club_with_players(db: Session, club_id: int):
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if club:
        club.goalkeepers
        club.field_players
    return club


def update_club(db: Session, club_id: int, club_update: schemas.ClubCreate, shield_file: UploadFile = None, banner_file: UploadFile = None):
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if db_club:
        if shield_file:
            if not shield_file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Apenas imagens são permitidas para o escudo.")
            if shield_file.size > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Imagem do escudo muito grande (máximo 5MB).")
            file_ext = os.path.splitext(shield_file.filename)[1]
            file_name = f"shield_{uuid.uuid4()}{file_ext}"
            file_path = os.path.join("uploaded_images", file_name)
            try:
                with open(file_path, "wb") as buffer:
                    content = shield_file.file.read()
                    buffer.write(content)
                db_club.shield_image_url = f"/uploaded_images/{file_name}"
            except Exception:
                raise HTTPException(status_code=500, detail="Erro ao salvar imagem do escudo.")

        if banner_file:
            if not banner_file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Apenas imagens são permitidas para o banner.")
            if banner_file.size > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Imagem do banner muito grande (máximo 5MB).")
            file_ext = os.path.splitext(banner_file.filename)[1]
            file_name = f"banner_{uuid.uuid4()}{file_ext}"
            file_path = os.path.join("uploaded_images", file_name)
            try:
                with open(file_path, "wb") as buffer:
                    content = banner_file.file.read()
                    buffer.write(content)
                db_club.banner_image_url = f"/uploaded_images/{file_name}"
            except Exception:
                raise HTTPException(status_code=500, detail="Erro ao salvar imagem do banner.")

        update_data = club_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_club, field, value)
        db.commit()
        db.refresh(db_club)
    return db_club


def delete_club(db: Session, club_id: int):
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if db_club:
        db.delete(db_club)
        db.commit()
        return True
    return False


def get_total_clubs_count(db: Session) -> int:
    return db.query(models.Club).count()
