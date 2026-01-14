from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...dependencies import get_current_active_user, get_db
from ... import schemas
from ...core.container import DIContainer
from .service import AthleteService

router = APIRouter(tags=["Athletes"])

def get_athlete_service(db: Session = Depends(get_db)) -> AthleteService:
    return DIContainer.get_athlete_service(db)

@router.patch("/athletes/{athlete_id}/health", response_model=Union[schemas.GoalkeeperResponse, schemas.FieldPlayerResponse])
def update_athlete_health(
    athlete_id: int,
    is_goalkeeper: bool,
    health_data: schemas.AthleteHealthUpdate,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.update_health(athlete_id, is_goalkeeper, health_data)

@router.post("/athletes/progress/", response_model=schemas.AthleteProgressResponse)
def create_athlete_progress(
    progress: schemas.AthleteProgressCreate,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_progress(progress)

@router.get("/athletes/{athlete_id}/progress", response_model=List[schemas.AthleteProgressResponse])
def read_athlete_progress(
    athlete_id: int,
    is_goalkeeper: bool,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_progress(athlete_id, is_goalkeeper)

@router.post("/athletes/nutritional_plans/", response_model=schemas.NutritionalPlanResponse)
def create_nutritional_plan(
    plan: schemas.NutritionalPlanCreate,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.create_nutritional_plan(plan)

@router.get("/athletes/{athlete_id}/nutritional_plans", response_model=List[schemas.NutritionalPlanResponse])
def read_nutritional_plans(
    athlete_id: int,
    is_goalkeeper: bool,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_nutritional_plans(athlete_id, is_goalkeeper)

@router.delete("/athletes/nutritional_plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nutritional_plan(
    plan_id: int,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    service.delete_nutritional_plan(plan_id)

@router.get("/field_players/", response_model=List[schemas.FieldPlayerResponse])
def read_field_players(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    name: Optional[str] = None,
    position: Optional[str] = None,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_field_players(skip, limit, club_id, name, position)

@router.get("/goalkeepers/", response_model=List[schemas.GoalkeeperResponse])
def read_goalkeepers(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    name: Optional[str] = None,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_goalkeepers(skip, limit, club_id, name)

@router.get("/statistics/top_goal_scorers/", response_model=List[schemas.FieldPlayerResponse])
def get_top_goal_scorers(
    limit: int = 7,
    position: Optional[str] = None,
    club_id: Optional[int] = None,
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return service.get_top_goal_scorers(limit, position, club_id)

@router.get("/statistics/total_athletes_count/", response_model=schemas.TotalCountResponse)
def get_total_athletes_count(
    service: AthleteService = Depends(get_athlete_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    total_count = service.get_total_athletes_count()
    return {"total_count": total_count}

@router.get("/statistics/total_clubs_count/", response_model=schemas.TotalCountResponse)
def get_total_clubs_count(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    from ..clubs.repository import ClubRepository
    repo = ClubRepository(db)
    return {"total_count": repo.count()}

@router.get("/statistics/top_players_by_statistic/", response_model=List[Union[schemas.FieldPlayerResponse, schemas.GoalkeeperResponse]])
def get_top_players_by_statistic(
    limit: int = 7,
    statistic: str = None,
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    from ...crud_modules.athletes_common import get_top_players_by_statistic as legacy_get_top
    return legacy_get_top(db, limit=limit, statistic=statistic, club_id=club_id)

@router.get("/statistics/top_players_by_age/", response_model=List[Union[schemas.FieldPlayerResponse, schemas.GoalkeeperResponse]])
def get_top_players_by_age(
    limit: int = 7,
    age_filter: str = 'oldest',
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    from ...crud_modules.athletes_common import get_top_players_by_age as legacy_get_age
    return legacy_get_age(db, limit=limit, age_filter=age_filter, club_id=club_id)
