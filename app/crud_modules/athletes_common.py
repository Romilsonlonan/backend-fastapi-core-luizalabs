from sqlalchemy.orm import Session
from sqlalchemy import desc

from .. import models, schemas


def update_athlete_health(db: Session, athlete_id: int, is_goalkeeper: bool, health_data: schemas.AthleteHealthUpdate):
    model = models.Goalkeeper if is_goalkeeper else models.FieldPlayer
    db_athlete = db.query(model).filter(model.id == athlete_id).first()
    if db_athlete:
        update_data = health_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_athlete, key, value)
        db.commit()
        db.refresh(db_athlete)
        return db_athlete
    return None


def create_athlete_progress(db: Session, progress: schemas.AthleteProgressCreate):
    db_progress = models.AthleteProgress(**progress.model_dump())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


def get_athlete_progress(db: Session, athlete_id: int, is_goalkeeper: bool):
    if is_goalkeeper:
        return db.query(models.AthleteProgress).filter(models.AthleteProgress.goalkeeper_id == athlete_id).all()
    return db.query(models.AthleteProgress).filter(models.AthleteProgress.field_player_id == athlete_id).all()


def create_nutritional_plan(db: Session, plan: schemas.NutritionalPlanCreate):
    db_plan = models.NutritionalPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_nutritional_plans(db: Session, athlete_id: int, is_goalkeeper: bool):
    if is_goalkeeper:
        return db.query(models.NutritionalPlan).filter(models.NutritionalPlan.goalkeeper_id == athlete_id).all()
    return db.query(models.NutritionalPlan).filter(models.NutritionalPlan.field_player_id == athlete_id).all()


def get_top_goal_scorers(db: Session, limit: int = 7, position: str = None, club_id: int = None):
    query = db.query(models.FieldPlayer).filter(models.FieldPlayer.goals > 0)
    if position:
        query = query.filter(models.FieldPlayer.position == position)
    if club_id:
        query = query.filter(models.FieldPlayer.club_id == club_id)
    query = query.order_by(desc(models.FieldPlayer.goals))
    return query.limit(limit).all()


def get_top_players_by_statistic(db: Session, limit: int = 7, statistic: str = None, club_id: int = None):
    valid_statistics = [
        'goals', 'assists', 'total_shots', 'shots_on_goal', 
        'goals_conceded', 'saves', 'fouls_suffered', 
        'fouls_committed', 'yellow_cards', 'red_cards'
    ]
    if statistic not in valid_statistics:
        raise ValueError(f"Estatística inválida fornecida: {statistic}")

    field_players = []
    if hasattr(models.FieldPlayer, statistic):
        field_players_query = db.query(models.FieldPlayer).filter(getattr(models.FieldPlayer, statistic) > 0)
        if club_id:
            field_players_query = field_players_query.filter(models.FieldPlayer.club_id == club_id)
        field_players_query = field_players_query.order_by(desc(getattr(models.FieldPlayer, statistic)))
        field_players = field_players_query.all()

    goalkeepers = []
    if hasattr(models.Goalkeeper, statistic):
        goalkeepers_query = db.query(models.Goalkeeper).filter(getattr(models.Goalkeeper, statistic) > 0)
        if club_id:
            goalkeepers_query = goalkeepers_query.filter(models.Goalkeeper.club_id == club_id)
        goalkeepers_query = goalkeepers_query.order_by(desc(getattr(models.Goalkeeper, statistic)))
        goalkeepers = goalkeepers_query.all()

    all_players = field_players + goalkeepers
    all_players.sort(key=lambda p: getattr(p, statistic, 0), reverse=True)

    return all_players[:limit]


def get_top_players_by_age(db: Session, limit: int = 7, age_filter: str = 'oldest', club_id: int = None):
    if age_filter not in ['oldest', 'youngest']:
        raise ValueError("Filtro de idade inválido fornecido.")

    field_player_order_by_clause = desc(models.FieldPlayer.age) if age_filter == 'oldest' else models.FieldPlayer.age
    goalkeeper_order_by_clause = desc(models.Goalkeeper.age) if age_filter == 'oldest' else models.Goalkeeper.age
    
    field_players_query = db.query(models.FieldPlayer).filter(models.FieldPlayer.age > 0)
    if club_id:
        field_players_query = field_players_query.filter(models.FieldPlayer.club_id == club_id)
    field_players_query = field_players_query.order_by(field_player_order_by_clause)
    field_players = field_players_query.all()

    goalkeepers_query = db.query(models.Goalkeeper).filter(models.Goalkeeper.age > 0)
    if club_id:
        goalkeepers_query = goalkeepers_query.filter(models.Goalkeeper.club_id == club_id)
    goalkeepers_query = goalkeepers_query.order_by(goalkeeper_order_by_clause)
    goalkeepers = goalkeepers_query.all()

    all_players = field_players + goalkeepers
    all_players.sort(key=lambda p: p.age, reverse=(age_filter == 'oldest'))

    return all_players[:limit]


def get_total_athletes_count(db: Session) -> int:
    total_field_players = db.query(models.FieldPlayer).count()
    total_goalkeepers = db.query(models.Goalkeeper).count()
    return total_field_players + total_goalkeepers


def get_athletes_with_health_data(db: Session, skip: int = 0, limit: int = 100):
    """
    Busca atletas (goleiros e jogadores de campo) com dados de saúde.
    Aplica skip/limit em cada consulta e retorna defaults 0.0 para métricas ausentes.
    Obs.: a paginação é aplicada separadamente por tipo; se quiser paginação global, me avise.
    """
    athletes = []

    # Goleiros
    goalkeepers = db.query(models.Goalkeeper).offset(skip).limit(limit).all()
    for gk in goalkeepers:
        athletes.append({
            "id": gk.id,
            "name": gk.name,
            "position": gk.position,
            "age": gk.age,
            "height": gk.height,
            "weight": gk.weight,
            "nationality": gk.nationality,
            "club_id": gk.club_id,
            "club_name": gk.club.name if getattr(gk, "club", None) else None,
            "club_initials": gk.club.initials if getattr(gk, "club", None) else None,
            "is_goalkeeper": True,
            "body_fat": float(gk.body_fat or 0.0),
            "muscle_mass": float(gk.muscle_mass or 0.0),
            "hdl": float(gk.hdl or 0.0),
            "ldl": float(gk.ldl or 0.0),
            "total_cholesterol": float(gk.total_cholesterol or 0.0),
            "triglycerides": float(gk.triglycerides or 0.0),
        })

    # Jogadores de Campo
    field_players = db.query(models.FieldPlayer).offset(skip).limit(limit).all()
    for fp in field_players:
        athletes.append({
            "id": fp.id,
            "name": fp.name,
            "position": fp.position,
            "age": fp.age,
            "height": fp.height,
            "weight": fp.weight,
            "nationality": fp.nationality,
            "club_id": fp.club_id,
            "club_name": fp.club.name if getattr(fp, "club", None) else None,
            "club_initials": fp.club.initials if getattr(fp, "club", None) else None,
            "is_goalkeeper": False,
            "body_fat": float(fp.body_fat or 0.0),
            "muscle_mass": float(fp.muscle_mass or 0.0),
            "hdl": float(fp.hdl or 0.0),
            "ldl": float(fp.ldl or 0.0),
            "total_cholesterol": float(fp.total_cholesterol or 0.0),
            "triglycerides": float(fp.triglycerides or 0.0),
        })

    return athletes
