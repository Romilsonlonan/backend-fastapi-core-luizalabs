from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List


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


class AthleteScrapeResponse(BaseModel):
    """Schema para dados vindos do web scraping"""
    name: str
    jersey_number: Optional[int] = 0 # Adicionado
    position: str
    age: int
    height: Optional[float] = 0.0
    weight: Optional[float] = 0.0
    nationality: Optional[str] = None
    games: Optional[int] = 0
    substitute_appearances: Optional[int] = 0
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    shots: Optional[int] = 0
    shots_on_goal: Optional[int] = 0
    fouls_committed: Optional[int] = 0
    fouls_suffered: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0
    defenses: Optional[int] = 0
    goals_conceded: Optional[int] = 0

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
    espn_url: Optional[str] = None  # ➕ Adiciona campo para URL do ESPN

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
    espn_url: Optional[str]  # ➕ Adiciona campo para URL do ESPN

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
    espn_url: Optional[str]  # ➕ Adiciona campo para URL do ESPN
    players: List["PlayerSimpleResponse"] = []

    class Config:
        from_attributes = True


class PlayerCreate(BaseModel):
    name: str
    jersey_number: Optional[int] = 0 # Adicionado
    position: str
    age: int
    club_id: int
    height: Optional[float] = 0.0
    weight: Optional[float] = 0.0
    nationality: Optional[str] = None
    games: Optional[int] = 0
    substitute_appearances: Optional[int] = 0
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    shots: Optional[int] = 0
    shots_on_goal: Optional[int] = 0
    fouls_committed: Optional[int] = 0
    fouls_suffered: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0
    defenses: Optional[int] = 0
    goals_conceded: Optional[int] = 0

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    jersey_number: Optional[int] = None # Adicionado
    position: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    nationality: Optional[str] = None
    games: Optional[int] = None
    substitute_appearances: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    shots: Optional[int] = None
    shots_on_goal: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    defenses: Optional[int] = None
    goals_conceded: Optional[int] = None
    club_id: Optional[int] = None

class PlayerSimpleResponse(BaseModel):
    """Schema simplificado para jogador usado dentro de ClubResponse"""
    id: int
    name: str
    jersey_number: Optional[int] # Adicionado
    position: str
    age: int
    height: Optional[float]
    weight: Optional[float]
    nationality: Optional[str]
    games: Optional[int]
    substitute_appearances: Optional[int]
    goals: Optional[int]
    assists: Optional[int]
    shots: Optional[int]
    shots_on_goal: Optional[int]
    fouls_committed: Optional[int]
    fouls_suffered: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    defenses: Optional[int]
    goals_conceded: Optional[int]
    club_id: int

    class Config:
        from_attributes = True

class PlayerResponse(BaseModel):
    id: int
    name: str
    jersey_number: Optional[int] # Adicionado
    position: str
    age: int
    height: Optional[float]
    weight: Optional[float]
    nationality: Optional[str]
    games: Optional[int]
    substitute_appearances: Optional[int]
    goals: Optional[int]
    assists: Optional[int]
    shots: Optional[int]
    shots_on_goal: Optional[int]
    fouls_committed: Optional[int]
    fouls_suffered: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    defenses: Optional[int]
    goals_conceded: Optional[int]
    club_id: int
    club: Optional[ClubSimpleResponse] = None

    class Config:
        from_attributes = True
