from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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

    goalkeepers = relationship("Goalkeeper", back_populates="club")
    field_players = relationship("FieldPlayer", back_populates="club")


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

    club_id = Column(Integer, ForeignKey('clubs.id'))
    club = relationship("Club", back_populates="goalkeepers")


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

    club_id = Column(Integer, ForeignKey('clubs.id'))
    club = relationship("Club", back_populates="field_players")


class TrainingRoutine(Base):
    __tablename__ = 'training_routines'

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey('clubs.id'))
    day_of_week = Column(String, index=True)  # Ex: "Segunda-feira", "Terça-feira"
    time = Column(String)  # Ex: "07:00", "09:00-11:00"
    activity = Column(String)
    description = Column(String, nullable=True)

    club = relationship("Club", back_populates="training_routines")


# Adicionar relacionamento em Club para TrainingRoutine
Club.training_routines = relationship("TrainingRoutine", back_populates="club")
