from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from ...database import SessionLocal
from ... import schemas
from .repository import ClubRepository
from .service import ClubService
from ...dependencies import get_current_active_user, get_db

router = APIRouter(prefix="/clubs", tags=["Clubs"])

def get_club_service(db: Session = Depends(get_db)) -> ClubService:
    repository = ClubRepository(db)
    return ClubService(repository)

@router.post("/", response_model=schemas.ClubResponse)
async def create_club(
    name: str = Form(...),
    initials: str = Form(...),
    city: str = Form(...),
    foundation_date: Optional[str] = Form(None),
    br_titles: Optional[int] = Form(0),
    training_center: Optional[str] = Form(None),
    espn_url: Optional[str] = Form(None),
    shield_image: Optional[UploadFile] = File(None),
    banner_image: Optional[UploadFile] = File(None),
    service: ClubService = Depends(get_club_service),
):
    club_data = schemas.ClubCreate(
        name=name,
        initials=initials,
        city=city,
        foundation_date=date.fromisoformat(foundation_date) if foundation_date else None,
        br_titles=br_titles,
        training_center=training_center,
        espn_url=espn_url,
    )
    return await service.create_club(club_data, shield_image, banner_image)

@router.get("/", response_model=List[schemas.ClubResponse])
def read_clubs(
    skip: int = 0, 
    limit: int = 100, 
    service: ClubService = Depends(get_club_service)
):
    return service.get_clubs(skip=skip, limit=limit)

@router.get("/{club_id}", response_model=schemas.ClubResponse)
def read_club(
    club_id: int, 
    service: ClubService = Depends(get_club_service)
):
    return service.get_club_by_id(club_id, with_players=True)

@router.patch("/{club_id}", response_model=schemas.ClubResponse)
async def update_club(
    club_id: int,
    name: Optional[str] = Form(None),
    initials: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    foundation_date: Optional[str] = Form(None),
    br_titles: Optional[int] = Form(None),
    training_center: Optional[str] = Form(None),
    espn_url: Optional[str] = Form(None),
    shield_image: Optional[UploadFile] = File(None),
    banner_image: Optional[UploadFile] = File(None),
    service: ClubService = Depends(get_club_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    club_update_data = {
        "name": name,
        "initials": initials,
        "city": city,
        "br_titles": br_titles,
        "training_center": training_center,
        "espn_url": espn_url,
    }

    if foundation_date:
        club_update_data["foundation_date"] = date.fromisoformat(foundation_date)

    club_update_data = {k: v for k, v in club_update_data.items() if v is not None}
    club_update_schema = schemas.ClubCreate(**club_update_data)

    return await service.update_club(club_id, club_update_schema, shield_image, banner_image)

@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    club_id: int,
    service: ClubService = Depends(get_club_service),
    current_user: schemas.User = Depends(get_current_active_user),
):
    service.delete_club(club_id)
