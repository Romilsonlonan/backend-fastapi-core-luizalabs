from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool = True
    profile_image_url: str | None = None

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
    foundation_date: Optional[date] = None
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
    foundation_date: Optional[date]
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

    class Config:
        from_attributes = True


class ClubResponse(BaseModel):
    id: int
    name: str
    initials: str
    city: str
    shield_image_url: Optional[str]
    foundation_date: Optional[date]
    br_titles: int
    training_center: Optional[str]
    espn_url: Optional[str]
    banner_image_url: Optional[str]
    goalkeepers: List[GoalkeeperResponse] = []
    field_players: List[FieldPlayerResponse] = []
    training_routines: List["TrainingRoutineResponse"] = []

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
