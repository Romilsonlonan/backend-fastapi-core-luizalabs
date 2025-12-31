import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc

from . import models, schemas


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
        # Carrega goleiros e jogadores de campo
        club.goalkeepers  # Acessa para carregar o relacionamento
        club.field_players  # Acessa para carregar o relacionamento
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

        update_data = club_update.dict(exclude_unset=True)
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


# Funções de Goleiro
def create_goalkeeper(db: Session, goalkeeper: schemas.GoalkeeperCreate, club_id: int):
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise ValueError(f"Clube com ID {club_id} não encontrado")

    db_goalkeeper = models.Goalkeeper(
        name=goalkeeper.name,
        position=goalkeeper.position,
        age=goalkeeper.age,
        height=goalkeeper.height,
        weight=goalkeeper.weight,
        nationality=goalkeeper.nationality,
        games=goalkeeper.games,
        substitutions=goalkeeper.substitutions,
        saves=goalkeeper.saves,
        goals_conceded=goalkeeper.goals_conceded,
        assists=goalkeeper.assists,
        fouls_committed=goalkeeper.fouls_committed,
        fouls_suffered=goalkeeper.fouls_suffered,
        yellow_cards=goalkeeper.yellow_cards,
        red_cards=goalkeeper.red_cards,
        club_id=club_id,
    )
    db.add(db_goalkeeper)
    db.commit()
    db.refresh(db_goalkeeper)
    return db_goalkeeper


def get_goalkeepers(db: Session, skip: int = 0, limit: int = 100, club_id: int = None, name: str = None):
    query = db.query(models.Goalkeeper)
    if club_id:
        query = query.filter(models.Goalkeeper.club_id == club_id)
    if name:
        query = query.filter(models.Goalkeeper.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()


def get_goalkeeper(db: Session, goalkeeper_id: int):
    return db.query(models.Goalkeeper).filter(models.Goalkeeper.id == goalkeeper_id).first()


def update_goalkeeper(db: Session, goalkeeper_id: int, goalkeeper_update: schemas.Goalkeeper):
    db_goalkeeper = db.query(models.Goalkeeper).filter(models.Goalkeeper.id == goalkeeper_id).first()
    if db_goalkeeper:
        update_data = goalkeeper_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_goalkeeper, field, value)
        db.commit()
        db.refresh(db_goalkeeper)
    return db_goalkeeper


def delete_goalkeeper(db: Session, goalkeeper_id: int):
    db_goalkeeper = db.query(models.Goalkeeper).filter(models.Goalkeeper.id == goalkeeper_id).first()
    if db_goalkeeper:
        db.delete(db_goalkeeper)
        db.commit()
        return True
    return False


# Funções de Jogador de Campo
def create_field_player(db: Session, field_player: schemas.FieldPlayerCreate, club_id: int):
    club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not club:
        raise ValueError(f"Clube com ID {club_id} não encontrado")

    db_field_player = models.FieldPlayer(
        name=field_player.name,
        position=field_player.position,
        age=field_player.age,
        height=field_player.height,
        weight=field_player.weight,
        nationality=field_player.nationality,
        games=field_player.games,
        substitutions=field_player.substitutions,
        goals=field_player.goals,
        assists=field_player.assists,
        total_shots=field_player.total_shots,
        shots_on_goal=field_player.shots_on_goal,
        fouls_committed=field_player.fouls_committed,
        fouls_suffered=field_player.fouls_suffered,
        yellow_cards=field_player.yellow_cards,
        red_cards=field_player.red_cards,
        club_id=club_id,
    )
    db.add(db_field_player)
    db.commit()
    db.refresh(db_field_player)
    return db_field_player


def get_field_players(db: Session, skip: int = 0, limit: int = 100, club_id: int = None, name: str = None, position: str = None):
    query = db.query(models.FieldPlayer)
    if club_id:
        query = query.filter(models.FieldPlayer.club_id == club_id)
    if name:
        query = query.filter(models.FieldPlayer.name.ilike(f"%{name}%"))
    if position:
        query = query.filter(models.FieldPlayer.position.ilike(f"%{position}%"))
    return query.offset(skip).limit(limit).all()


def get_field_player(db: Session, field_player_id: int):
    return db.query(models.FieldPlayer).filter(models.FieldPlayer.id == field_player_id).first()


def update_field_player(db: Session, field_player_id: int, field_player_update: schemas.FieldPlayer):
    db_field_player = db.query(models.FieldPlayer).filter(models.FieldPlayer.id == field_player_id).first()
    if db_field_player:
        update_data = field_player_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_field_player, field, value)
        db.commit()
        db.refresh(db_field_player)
    return db_field_player


def delete_field_player(db: Session, field_player_id: int):
    db_field_player = db.query(models.FieldPlayer).filter(models.FieldPlayer.id == field_player_id).first()
    if db_field_player:
        db.delete(db_field_player)
        db.commit()
        return True
    return False


def get_top_goal_scorers(db: Session, limit: int = 7, position: str = None):
    query = db.query(models.FieldPlayer).filter(models.FieldPlayer.goals > 0)
    if position:
        query = query.filter(models.FieldPlayer.position == position)
    query = query.order_by(desc(models.FieldPlayer.goals))
    return query.limit(limit).all()


def get_top_players_by_statistic(db: Session, limit: int = 7, statistic: str = None):
    if statistic not in ['fouls_suffered', 'fouls_committed', 'yellow_cards', 'red_cards']:
        raise ValueError("Estatística inválida fornecida.")

    # Query for FieldPlayers
    field_players_query = db.query(models.FieldPlayer).filter(getattr(models.FieldPlayer, statistic) > 0)
    field_players_query = field_players_query.order_by(desc(getattr(models.FieldPlayer, statistic)))
    field_players = field_players_query.all()

    # Query for Goalkeepers
    goalkeepers_query = db.query(models.Goalkeeper).filter(getattr(models.Goalkeeper, statistic) > 0)
    goalkeepers_query = goalkeepers_query.order_by(desc(getattr(models.Goalkeeper, statistic)))
    goalkeepers = goalkeepers_query.all()

    # Combine and sort
    all_players = field_players + goalkeepers
    all_players.sort(key=lambda p: getattr(p, statistic), reverse=True)

    return all_players[:limit]


def get_top_players_by_age(db: Session, limit: int = 7, age_filter: str = 'oldest'):
    if age_filter not in ['oldest', 'youngest']:
        raise ValueError("Filtro de idade inválido fornecido.")

    field_player_order_by_clause = desc(models.FieldPlayer.age) if age_filter == 'oldest' else models.FieldPlayer.age
    goalkeeper_order_by_clause = desc(models.Goalkeeper.age) if age_filter == 'oldest' else models.Goalkeeper.age
    
    # Query for FieldPlayers
    field_players_query = db.query(models.FieldPlayer).filter(models.FieldPlayer.age > 0)
    field_players_query = field_players_query.order_by(field_player_order_by_clause)
    field_players = field_players_query.all()

    # Query for Goalkeepers
    goalkeepers_query = db.query(models.Goalkeeper).filter(models.Goalkeeper.age > 0)
    goalkeepers_query = goalkeepers_query.order_by(goalkeeper_order_by_clause)
    goalkeepers = goalkeepers_query.all()

    # Combine and sort
    all_players = field_players + goalkeepers
    all_players.sort(key=lambda p: p.age, reverse=(age_filter == 'oldest'))

    return all_players[:limit]


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


def get_total_athletes_count(db: Session) -> int:
    total_field_players = db.query(models.FieldPlayer).count()
    total_goalkeepers = db.query(models.Goalkeeper).count()
    return total_field_players + total_goalkeepers


def get_total_clubs_count(db: Session) -> int:
    return db.query(models.Club).count()


# Funções de TrainingRoutine
def create_training_routine(db: Session, routine: schemas.TrainingRoutineCreate):
    # Validar se o clube existe
    club = db.query(models.Club).filter(models.Club.id == routine.club_id).first()
    if not club:
        raise ValueError(f"Clube com ID {routine.club_id} não encontrado")

    db_routine = models.TrainingRoutine(
        club_id=routine.club_id,
        day_of_week=routine.day_of_week,
        time=routine.time,
        activity=routine.activity,
        description=routine.description
    )
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine


def get_training_routines(db: Session, skip: int = 0, limit: int = 100, club_id: int = None):
    query = db.query(models.TrainingRoutine)
    if club_id:
        query = query.filter(models.TrainingRoutine.club_id == club_id)
    return query.offset(skip).limit(limit).all()


def get_training_routine(db: Session, routine_id: int):
    return db.query(models.TrainingRoutine).filter(models.TrainingRoutine.id == routine_id).first()


def update_training_routine(db: Session, routine_id: int, routine_update: schemas.TrainingRoutineUpdate):
    db_routine = db.query(models.TrainingRoutine).filter(models.TrainingRoutine.id == routine_id).first()
    if db_routine:
        update_data = routine_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_routine, field, value)
        db.commit()
        db.refresh(db_routine)
    return db_routine


def delete_training_routine(db: Session, routine_id: int):
    db_routine = db.query(models.TrainingRoutine).filter(models.TrainingRoutine.id == routine_id).first()
    if db_routine:
        db.delete(db_routine)
        db.commit()
        return True
    return False
