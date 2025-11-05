from sqlalchemy.orm import Session
from . import models, schemas
import uuid
import os
from fastapi import UploadFile, HTTPException
from datetime import date

def create_club(db: Session, club: schemas.ClubCreate, shield_file: UploadFile = None):
    shield_url = None

    if shield_file:
        # Validações de segurança
        if not shield_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Apenas imagens são permitidas")

        if shield_file.size > 5 * 1024 * 1024:  # 5MB limite
            raise HTTPException(status_code=400, detail="Imagem muito grande (máximo 5MB)")

        # Salvar arquivo com nome único
        file_ext = os.path.splitext(shield_file.filename)[1]
        file_name = f"shield_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploaded_images", file_name)

        try:
            with open(file_path, "wb") as buffer:
                content = shield_file.file.read()
                buffer.write(content)

            shield_url = f"/uploaded_images/{file_name}"
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao salvar imagem")

    db_club = models.Club(
        name=club.name,
        initials=club.initials.upper(),
        city=club.city,
        shield_image_url=shield_url,
        foundation_date=club.foundation_date,
        br_titles=club.br_titles or 0,
        training_center=club.training_center,
        espn_url=club.espn_url # Adicionado
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
    return db.query(models.Club).filter(models.Club.id == club_id).first()

def update_club(db: Session, club_id: int, club_update: schemas.ClubCreate):
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if db_club:
        update_data = club_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_club, field, value)
        db.commit()
        db.refresh(db_club)
    return db_club

# Funções de Player
def create_player(db: Session, player: schemas.PlayerCreate):
    # Validar se o clube existe
    club = db.query(models.Club).filter(models.Club.id == player.club_id).first()
    if not club:
        raise ValueError(f"Clube com ID {player.club_id} não encontrado")

    db_player = models.Player(
        name=player.name,
        jersey_number=player.jersey_number,
        position=player.position,
        age=player.age,
        height=player.height,
        weight=player.weight,
        nationality=player.nationality,
        games=player.games,
        substitute_appearances=player.substitute_appearances,
        goals=player.goals,
        assists=player.assists,
        shots=player.shots,
        shots_on_goal=player.shots_on_goal,
        fouls_committed=player.fouls_committed,
        fouls_suffered=player.fouls_suffered,
        yellow_cards=player.yellow_cards,
        red_cards=player.red_cards,
        defenses=player.defenses,
        goals_conceded=player.goals_conceded,
        club_id=player.club_id,
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def get_players(db: Session, skip: int = 0, limit: int = 100, club_id: int = None):
    query = db.query(models.Player)
    if club_id:
        query = query.filter(models.Player.club_id == club_id)
    return query.offset(skip).limit(limit).all()

def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def update_player(db: Session, player_id: int, player_update: schemas.PlayerUpdate):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if db_player:
        update_data = player_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_player, field, value)
        db.commit()
        db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: int):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if db_player:
        db.delete(db_player)
        db.commit()
        return True
    return False

# Funções de User (mantidas)
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile_image(db: Session, user_id: int, image_url: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.profile_image_url = image_url
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, user_update: schemas.UserBase):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user_update.name is not None:
            db_user.name = user_update.name
        if user_update.email is not None:
            db_user.email = user_update.email
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, hashed_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.hashed_password = hashed_password
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def create_admin_user_if_not_exists(db: Session, admin_email: str, admin_password: str, admin_name: str, get_password_hash_func):
    db_user = get_user_by_email(db, email=admin_email)
    if not db_user:
        hashed_password = get_password_hash_func(admin_password)
        admin_user = models.User(name=admin_name, email=admin_email, hashed_password=hashed_password)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Usuário administrador '{admin_email}' criado.")
        return admin_user
    print(f"Usuário administrador '{admin_email}' já existe.")
    return db_user
