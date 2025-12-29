import re
import sys
from typing import Dict, List, Tuple, Optional

import requests
import pandas as pd
import re
import sys
from typing import Dict, List, Tuple, Optional, Union

import requests
import pandas as pd

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from loguru import logger

from . import crud, models, schemas
from .schemas import Goalkeeper, FieldPlayer


# -------------------------------------------------------------------------
# CONFIGURAÇÃO GLOBAL DE LOG (TERMINAL + ARQUIVO)
# -------------------------------------------------------------------------
logger.remove()

# 🔹 LOG NO TERMINAL (ESSENCIAL)
logger.add(
    sys.stdout,
    level="DEBUG",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
)

# 🔹 LOG EM ARQUIVO
logger.add(
    "logs/espn_scraper.log",
    level="DEBUG",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


# -------------------------------------------------------------------------
# SERVIÇO
# -------------------------------------------------------------------------
class ESPNScraperService:

    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    # ------------------------------------------------------------------
    # PARSERS
    # ------------------------------------------------------------------
    def _parse_float(self, text: str, unit: str = "") -> Optional[float]:
        if not text or text == "--":
            return None
        try:
            return float(text.replace(unit, "").strip())
        except ValueError:
            logger.warning(f"Falha ao converter float: '{text}'")
            return None

    def _parse_int(self, text: str) -> int:
        if not text or text == "--":
            return 0
        try:
            return int(text.strip())
        except ValueError:
            logger.warning(f"Falha ao converter int: '{text}'")
            return 0

    def _extract_name_and_number(self, text: str) -> Tuple[str, int]:
        match = re.match(r"^(.*?)\s*(\d+)$", text.strip())
        if match:
            return match.group(1).strip(), int(match.group(2))
        return text.strip(), 0

    # ------------------------------------------------------------------
    # EXTRAÇÃO DE LINHA
    # ------------------------------------------------------------------
    def _extract_player_data(self, row, is_goalkeeper: bool) -> Optional[Union[Goalkeeper, FieldPlayer]]:
        cols = row.find_all("td")

        if len(cols) < 8:
            logger.debug("Linha ignorada (colunas insuficientes)")
            return None

        name_raw = cols[0].get_text(strip=True)
        position_raw = cols[1].get_text(strip=True)
        age = self._parse_int(cols[2].text)
        height = self._parse_float(cols[3].text, "m")
        weight = self._parse_float(cols[4].text, "kg")
        nationality = cols[5].text.strip()
        games = self._parse_int(cols[6].text)
        substitutions = self._parse_int(cols[7].text)

        if is_goalkeeper:
            try:
                return Goalkeeper(
                    Nome=name_raw,
                    POS="Goleiro",
                    Idade=age,
                    Alt=height,
                    P=weight,
                    NAC=nationality,
                    J=games,
                    SUB=substitutions,
                    D=self._parse_int(cols[8].text),
                    GS=self._parse_int(cols[9].text),
                    A=self._parse_int(cols[10].text),
                    FC=self._parse_int(cols[11].text),
                    FS=self._parse_int(cols[12].text),
                    CA=self._parse_int(cols[13].text),
                    CV=self._parse_int(cols[14].text),
                )
            except IndexError:
                logger.warning(f"Colunas insuficientes para goleiro: {name_raw}")
                return None
            except Exception as e:
                logger.error(f"Erro ao criar Goalkeeper para {name_raw}: {e}")
                return None
        else:
            position_map = {
                "D": "Defensor",
                "M": "Meio-Campista",
                "A": "Atacante",
            }
            position = position_map.get(position_raw, position_raw)
            try:
                return FieldPlayer(
                    Nome=name_raw,
                    POS=position,
                    Idade=age,
                    Alt=height,
                    P=weight,
                    NAC=nationality,
                    J=games,
                    SUB=substitutions,
                    G=self._parse_int(cols[8].text),
                    A=self._parse_int(cols[9].text),
                    TC=self._parse_int(cols[10].text),
                    CG=self._parse_int(cols[11].text),
                    FC=self._parse_int(cols[12].text),
                    FS=self._parse_int(cols[13].text),
                    CA=self._parse_int(cols[14].text),
                    CV=self._parse_int(cols[15].text),
                )
            except IndexError:
                logger.warning(f"Colunas insuficientes para jogador de campo: {name_raw}")
                return None
            except Exception as e:
                logger.error(f"Erro ao criar FieldPlayer para {name_raw}: {e}")
                return None

    # ------------------------------------------------------------------
    # SCRAPING PRINCIPAL
    # ------------------------------------------------------------------
    def scrape_club_squad(self, espn_url: str, club_id: int):
        logger.info(f"Iniciando scraping | clube={club_id} | url={espn_url}")

        errors = []
        goalkeepers_data: List[Goalkeeper] = []
        field_players_data: List[FieldPlayer] = []

        try:
            response = requests.get(espn_url, headers=self.headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Erro HTTP ao acessar ESPN")
            return [], [], ["Erro HTTP"]

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="Table")

        # 🔍 LOG DE TODAS AS TABELAS
        logger.debug(f"Total de tabelas encontradas: {len(tables)}")

        for idx, table in enumerate(tables, start=1):
            headers = [th.text.strip() for th in table.find_all("th")]
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else []

            is_goalkeeper = "GS" in headers or "Saves" in headers

            logger.debug(
                f"Tabela #{idx} | "
                f"Goleiros={is_goalkeeper} | "
                f"Colunas={headers} | "
                f"Linhas={len(rows)}"
            )

            for row in rows:
                player = self._extract_player_data(row, is_goalkeeper)
                if player:
                    if isinstance(player, Goalkeeper):
                        goalkeepers_data.append(player)
                    elif isinstance(player, FieldPlayer):
                        field_players_data.append(player)

        logger.debug(f"Goleiros extraídos: {len(goalkeepers_data)}")
        logger.debug(f"Jogadores de campo extraídos: {len(field_players_data)}")

        saved_goalkeepers = []
        saved_field_players = []

        # Save Goalkeepers
        for gk_data in goalkeepers_data:
            try:
                goalkeeper_create_data = schemas.GoalkeeperCreate(
                    name=gk_data.name,
                    position=gk_data.position,
                    age=gk_data.age,
                    height=gk_data.height,
                    weight=gk_data.weight,
                    nationality=gk_data.nationality,
                    games=gk_data.games,
                    substitutions=gk_data.substitutions,
                    saves=gk_data.saves,
                    goals_conceded=gk_data.goals_conceded,
                    assists=gk_data.assists,
                    fouls_committed=gk_data.fouls_committed,
                    fouls_suffered=gk_data.fouls_suffered,
                    yellow_cards=gk_data.yellow_cards,
                    red_cards=gk_data.red_cards,
                    club_id=club_id,
                )
                existing_goalkeeper = self.db.query(models.Goalkeeper).filter(
                    models.Goalkeeper.name == gk_data.name,
                    models.Goalkeeper.club_id == club_id,
                ).first()

                if existing_goalkeeper:
                    for k, v in goalkeeper_create_data.model_dump(exclude_unset=True).items():
                        setattr(existing_goalkeeper, k, v)
                    self.db.add(existing_goalkeeper)
                    saved_goalkeepers.append(existing_goalkeeper)
                else:
                    saved_goalkeepers.append(crud.create_goalkeeper(self.db, goalkeeper_create_data, club_id))
            except Exception:
                logger.exception(f"Erro salvando goleiro {gk_data.name}")
                errors.append(gk_data.name)

        # Save Field Players
        for fp_data in field_players_data:
            try:
                field_player_create_data = schemas.FieldPlayerCreate(
                    name=fp_data.name,
                    position=fp_data.position,
                    age=fp_data.age,
                    height=fp_data.height,
                    weight=fp_data.weight,
                    nationality=fp_data.nationality,
                    games=fp_data.games,
                    substitutions=fp_data.substitutions,
                    goals=fp_data.goals,
                    assists=fp_data.assists,
                    total_shots=fp_data.total_shots,
                    shots_on_goal=fp_data.shots_on_goal,
                    fouls_committed=fp_data.fouls_committed,
                    fouls_suffered=fp_data.fouls_suffered,
                    yellow_cards=fp_data.yellow_cards,
                    red_cards=fp_data.red_cards,
                    club_id=club_id,
                )
                existing_field_player = self.db.query(models.FieldPlayer).filter(
                    models.FieldPlayer.name == fp_data.name,
                    models.FieldPlayer.club_id == club_id,
                ).first()

                if existing_field_player:
                    for k, v in field_player_create_data.model_dump(exclude_unset=True).items():
                        setattr(existing_field_player, k, v)
                    self.db.add(existing_field_player)
                    saved_field_players.append(existing_field_player)
                else:
                    saved_field_players.append(crud.create_field_player(self.db, field_player_create_data, club_id))
            except Exception:
                logger.exception(f"Erro salvando jogador de campo {fp_data.name}")
                errors.append(fp_data.name)

        self.db.commit()
        logger.success(f"Scraping finalizado | jogadores_salvos={len(saved_goalkeepers) + len(saved_field_players)}")

        return saved_goalkeepers, saved_field_players, errors
