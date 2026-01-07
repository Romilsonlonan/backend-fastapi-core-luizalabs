from datetime import date
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default='Usuário')
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile_image_url = Column(String, nullable=True)


class Club(Base):
    __tablename__ = 'clubs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    initials = Column(String(3), index=True)
    city = Column(String)
    shield_image_url = Column(String, nullable=True)
    foundation_date = Column(Date, nullable=True)
    br_titles = Column(Integer, default=0)
    training_center = Column(String, nullable=True)  # Adicionado para centro de treinamento
    espn_url = Column(String, nullable=True)
    banner_image_url = Column(String, nullable=True) # Adiciona campo para URL do banner

    goalkeepers = relationship("Goalkeeper", back_populates="club", cascade="all, delete-orphan")
    field_players = relationship("FieldPlayer", back_populates="club", cascade="all, delete-orphan")


class Goalkeeper(Base):
    __tablename__ = 'goalkeepers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String, default="Goleiro")
    age = Column(Integer, default=0)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    nationality = Column(String, nullable=True)
    games = Column(Integer, default=0)
    substitutions = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    fouls_suffered = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    club_id = Column(Integer, ForeignKey('clubs.id'))
    club = relationship("Club", back_populates="goalkeepers")

    # Campos para Centro de Treinamento
    body_fat = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    hdl = Column(Float, nullable=True)
    ldl = Column(Float, nullable=True)
    total_cholesterol = Column(Float, nullable=True)
    triglycerides = Column(Float, nullable=True)

    progress_history = relationship("AthleteProgress", back_populates="goalkeeper")
    nutritional_plans = relationship("NutritionalPlan", back_populates="goalkeeper")


class FieldPlayer(Base):
    __tablename__ = 'field_players'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String, index=True)
    age = Column(Integer, default=0)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    nationality = Column(String, nullable=True)
    games = Column(Integer, default=0)
    substitutions = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    total_shots = Column(Integer, default=0)
    shots_on_goal = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    fouls_suffered = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    club_id = Column(Integer, ForeignKey('clubs.id'))
    club = relationship("Club", back_populates="field_players")

    # Campos para Centro de Treinamento
    body_fat = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    hdl = Column(Float, nullable=True)
    ldl = Column(Float, nullable=True)
    total_cholesterol = Column(Float, nullable=True)
    triglycerides = Column(Float, nullable=True)

    progress_history = relationship("AthleteProgress", back_populates="field_player")
    nutritional_plans = relationship("NutritionalPlan", back_populates="field_player")


class AthleteProgress(Base):
    __tablename__ = 'athlete_progress'

    id = Column(Integer, primary_key=True, index=True)
    goalkeeper_id = Column(Integer, ForeignKey('goalkeepers.id'), nullable=True)
    field_player_id = Column(Integer, ForeignKey('field_players.id'), nullable=True)
    week = Column(String, index=True)
    weight = Column(Float)
    body_fat = Column(Float)
    muscle_mass = Column(Float)
    date = Column(Date, default=date.today)

    goalkeeper = relationship("Goalkeeper", back_populates="progress_history")
    field_player = relationship("FieldPlayer", back_populates="progress_history")


class NutritionalPlan(Base):
    __tablename__ = 'nutritional_plans'

    id = Column(Integer, primary_key=True, index=True)
    goalkeeper_id = Column(Integer, ForeignKey('goalkeepers.id'), nullable=True)
    field_player_id = Column(Integer, ForeignKey('field_players.id'), nullable=True)
    plan_details = Column(String)
    nutritionist_name = Column(String)
    nutritionist_id = Column(String)
    date = Column(Date, default=date.today)

    goalkeeper = relationship("Goalkeeper", back_populates="nutritional_plans")
    field_player = relationship("FieldPlayer", back_populates="nutritional_plans")


class TrainingRoutine(Base):
    __tablename__ = 'training_routines'

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey('clubs.id'))
    day_of_week = Column(String, index=True)  # Ex: "Segunda-feira", "Terça-feira"
    time = Column(String)  # Ex: "07:00", "09:00-11:00"
    activity = Column(String)
    description = Column(String, nullable=True)

    club = relationship("Club", back_populates="training_routines")


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, nullable=True)
    athlete_type = Column(String, nullable=True)  # 'G' for Goalkeeper, 'F' for FieldPlayer
    nutritionist_id = Column(Integer, ForeignKey('users.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    status = Column(String, default='pending')  # confirmed, pending, canceled
    notes = Column(String, nullable=True)
    is_special_event = Column(Boolean, default=False)
    event_title = Column(String, nullable=True)

    nutritionist = relationship("User")
    service = relationship("Service")
    location = relationship("Location")


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    duration = Column(Integer)  # in minutes
    price = Column(Float)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class Availability(Base):
    __tablename__ = 'availabilities'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    day_of_week = Column(Integer)  # 0-6 (Monday-Sunday)
    start_time = Column(String)  # "08:00"
    end_time = Column(String)  # "20:00"
    is_active = Column(Boolean, default=True)


# Adicionar relacionamento em Club para TrainingRoutine
Club.training_routines = relationship("TrainingRoutine", back_populates="club")
