from datetime import date as date_type, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class User(UserBase):
    id: int
    is_active: bool = True
    profile_image_url: str | None = None
    subscription_status: str = 'free'

    class Config:
        from_attributes = True


class TotalCountResponse(BaseModel):
    total_count: int


class Goalkeeper(BaseModel):
    name: str = Field(..., alias="Nome")
    position: str = Field(..., alias="POS")
    age: int = Field(..., alias="Idade")
    height: Optional[float] = Field(None, alias="Alt")
    weight: Optional[float] = Field(None, alias="P")
    nationality: Optional[str] = Field(None, alias="NAC")
    games: Optional[int] = Field(0, alias="J")
    substitutions: Optional[int] = Field(0, alias="SUB")
    saves: Optional[int] = Field(0, alias="D")
    goals_conceded: Optional[int] = Field(0, alias="GS")
    assists: Optional[int] = Field(0, alias="A")
    fouls_committed: Optional[int] = Field(0, alias="FC")
    fouls_suffered: Optional[int] = Field(0, alias="FS")
    yellow_cards: Optional[int] = Field(0, alias="CA")
    red_cards: Optional[int] = Field(0, alias="CV")

    class Config:
        from_attributes = True


class GoalkeeperCreate(BaseModel):
    name: str
    position: str
    age: int
    height: Optional[float] = None
    weight: Optional[float] = None
    nationality: Optional[str] = None
    games: Optional[int] = 0
    substitutions: Optional[int] = 0
    saves: Optional[int] = 0
    goals_conceded: Optional[int] = 0
    assists: Optional[int] = 0
    fouls_committed: Optional[int] = 0
    fouls_suffered: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0
    club_id: int


class GoalkeeperUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    nationality: Optional[str] = None
    games: Optional[int] = None
    substitutions: Optional[int] = None
    saves: Optional[int] = None
    goals_conceded: Optional[int] = None
    assists: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    club_id: Optional[int] = None


class FieldPlayer(BaseModel):
    name: str = Field(..., alias="Nome")
    position: str = Field(..., alias="POS")
    age: int = Field(..., alias="Idade")
    height: Optional[float] = Field(None, alias="Alt")
    weight: Optional[float] = Field(None, alias="P")
    nationality: Optional[str] = Field(None, alias="NAC")
    games: Optional[int] = Field(0, alias="J")
    substitutions: Optional[int] = Field(0, alias="SUB")
    goals: Optional[int] = Field(0, alias="G")
    assists: Optional[int] = Field(0, alias="A")
    total_shots: Optional[int] = Field(0, alias="TC")
    shots_on_goal: Optional[int] = Field(0, alias="CG")
    fouls_committed: Optional[int] = Field(0, alias="FC")
    fouls_suffered: Optional[int] = Field(0, alias="FS")
    yellow_cards: Optional[int] = Field(0, alias="CA")
    red_cards: Optional[int] = Field(0, alias="CV")

    class Config:
        from_attributes = True


class FieldPlayerCreate(BaseModel):
    name: str
    position: str
    age: int
    height: Optional[float] = None
    weight: Optional[float] = None
    nationality: Optional[str] = None
    games: Optional[int] = 0
    substitutions: Optional[int] = 0
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    total_shots: Optional[int] = 0
    shots_on_goal: Optional[int] = 0
    fouls_committed: Optional[int] = 0
    fouls_suffered: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0
    club_id: int


class FieldPlayerUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    nationality: Optional[str] = None
    games: Optional[int] = None
    substitutions: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    total_shots: Optional[int] = None
    shots_on_goal: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    club_id: Optional[int] = None


class AthleteScrapeResponse(BaseModel):
    """Schema para dados vindos do web scraping"""
    name: str
    jersey_number: Optional[int] = Field(0, alias="jerseyNumber")
    position: str
    age: int
    height: Optional[float] = 0.0
    weight: Optional[float] = 0.0
    nationality: Optional[str] = None
    games: Optional[int] = 0
    substitutions: Optional[int] = Field(0, alias="substitutions")
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    tackles: Optional[int] = Field(0, alias="tackles")
    chances_created: Optional[int] = Field(0, alias="chancesCreated")
    fouls_committed: Optional[int] = Field(0, alias="foulsCommitted")
    fouls_suffered: Optional[int] = Field(0, alias="foulsSuffered")
    yellow_cards: Optional[int] = Field(0, alias="yellowCards")
    red_cards: Optional[int] = Field(0, alias="redCards")
    saves: Optional[int] = Field(0, alias="saves")
    goals_conceded: Optional[int] = Field(0, alias="goalsConceded")
    clean_sheets: Optional[int] = Field(0, alias="cleanSheets")

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class ClubCreate(BaseModel):
    name: str
    initials: str
    city: str
    shield_image_url: Optional[str] = None
    foundation_date: Optional[date_type] = None
    br_titles: Optional[int] = 0
    training_center: Optional[str] = None
    espn_url: Optional[str] = None
    banner_image_url: Optional[str] = None


class ClubSimpleResponse(BaseModel):
    """Schema simplificado para clube usado dentro de PlayerResponse"""
    id: int
    name: str
    initials: str
    city: str
    shield_image_url: Optional[str]
    foundation_date: Optional[date_type]
    br_titles: int
    training_center: Optional[str]
    espn_url: Optional[str]
    banner_image_url: Optional[str]

    class Config:
        from_attributes = True


class GoalkeeperResponse(BaseModel):
    id: int
    name: str
    position: str
    age: int
    height: Optional[float]
    weight: Optional[float]
    nationality: Optional[str]
    games: Optional[int]
    substitutions: Optional[int]
    saves: Optional[int]
    goals_conceded: Optional[int]
    assists: Optional[int]
    fouls_committed: Optional[int]
    fouls_suffered: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    club_id: int
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None
    hdl: Optional[float] = None
    ldl: Optional[float] = None
    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None

    class Config:
        from_attributes = True


class FieldPlayerResponse(BaseModel):
    id: int
    name: str
    position: str
    age: int
    height: Optional[float]
    weight: Optional[float]
    nationality: Optional[str]
    games: Optional[int]
    substitutions: Optional[int]
    goals: Optional[int]
    assists: Optional[int]
    total_shots: Optional[int]
    shots_on_goal: Optional[int]
    fouls_committed: Optional[int]
    fouls_suffered: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    club_id: int
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None
    hdl: Optional[float] = None
    ldl: Optional[float] = None
    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None

    class Config:
        from_attributes = True


class ClubResponse(BaseModel):
    id: int
    name: str
    initials: str
    city: str
    shield_image_url: Optional[str]
    foundation_date: Optional[date_type]
    br_titles: int
    training_center: Optional[str]
    espn_url: Optional[str]
    banner_image_url: Optional[str]
    goalkeepers: List[GoalkeeperResponse] = []
    field_players: List[FieldPlayerResponse] = []
    training_routines: List[Optional["TrainingRoutineResponse"]] = []

    class Config:
        from_attributes = True


class TrainingRoutineBase(BaseModel):
    club_id: int
    day_of_week: str
    time: str
    activity: str
    description: Optional[str] = None


class TrainingRoutineCreate(TrainingRoutineBase):
    pass


class TrainingRoutineUpdate(BaseModel):
    day_of_week: Optional[str] = None
    time: Optional[str] = None
    activity: Optional[str] = None
    description: Optional[str] = None


class TrainingRoutineResponse(TrainingRoutineBase):
    id: int

    class Config:
        from_attributes = True


class AthleteProgressBase(BaseModel):
    week: str
    weight: float
    body_fat: float
    muscle_mass: float
    date: Optional[date_type] = None


class AthleteProgressCreate(AthleteProgressBase):
    goalkeeper_id: Optional[int] = None
    field_player_id: Optional[int] = None


class AthleteProgressResponse(AthleteProgressBase):
    id: int

    class Config:
        from_attributes = True


class NutritionalPlanBase(BaseModel):
    plan_details: str
    nutritionist_name: str
    nutritionist_id: str
    date: Optional[date_type] = None


class NutritionalPlanCreate(NutritionalPlanBase):
    goalkeeper_id: Optional[int] = None
    field_player_id: Optional[int] = None


class NutritionalPlanResponse(NutritionalPlanBase):
    id: int

    class Config:
        from_attributes = True


class AthleteHealthUpdate(BaseModel):
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None
    hdl: Optional[float] = None
    ldl: Optional[float] = None
    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None


class ServiceBase(BaseModel):
    name: str
    duration: int
    price: float
    description: Optional[str] = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    is_online: bool = False
    is_active: bool = True


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True


class AvailabilityBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_active: bool = True


class AvailabilityCreate(AvailabilityBase):
    user_id: int


class AvailabilityResponse(AvailabilityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    athlete_id: Optional[int] = None
    athlete_type: Optional[str] = None
    service_id: int
    location_id: int
    start_time: datetime
    end_time: datetime
    status: str = "pending"
    notes: Optional[str] = None
    is_special_event: bool = False
    event_title: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    nutritionist_id: int


class AppointmentResponse(AppointmentBase):
    id: int
    nutritionist_id: int
    service: ServiceResponse
    location: LocationResponse

    class Config:
        from_attributes = True
