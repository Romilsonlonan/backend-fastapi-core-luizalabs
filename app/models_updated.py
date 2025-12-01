from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
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
    training_center = Column(String, nullable=True)
    espn_url = Column(String, nullable=True)  # URL do clube no ESPN

    # Relacionamento com elenco
    players = relationship("Player", back_populates="club")


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    jersey_number = Column(Integer, default=0)  # Número da camisa
    position = Column(String, index=True)
    age = Column(Integer, default=0)
    height = Column(Float, default=0.0)  # ALT em metros
    weight = Column(Float, default=0.0)   # P em kg
    nationality = Column(String, nullable=True)  # NAC
    games = Column(Integer, default=0)  # J
    substitute_appearances = Column(Integer, default=0)  # SUB
    player_type = Column(String, default="jogador")  # "goleiro" ou "jogador"

    # Data da última atualização
    updated_at = Column(DateTime, default=datetime.now)

    # Estatísticas de ataque (jogadores de campo)
    goals = Column(Integer, default=0)           # G
    assists = Column(Integer, default=0)         # A
    shots = Column(Integer, default=0)           # TC (tentativas de cruzamento)
    shots_on_goal = Column(Integer, default=0)   # CG (cruzamentos certos)

    # Estatísticas de defesa
    fouls_committed = Column(Integer, default=0)  # FC
    fouls_suffered = Column(Integer, default=0)   # FS

    # Estatísticas de goleiro
    saves = Column(Integer, default=0)            # DGS
    goals_conceded = Column(Integer, default=0)   # AFC (usado como gols sofridos)

    # Cartões
    yellow_cards = Column(Integer, default=0)  # CA
    red_cards = Column(Integer, default=0)     # CV

    # Chave estrangeira para o clube
    club_id = Column(Integer, ForeignKey('clubs.id'))
    club = relationship("Club", back_populates="players")
