import re
import sys
from typing import Dict, List, Tuple, Optional, Union

import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from loguru import logger

from . import crud_modules as crud, models, schemas
from .schemas import GoalkeeperCreate, FieldPlayerCreate


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
    def _parse_float(self, text: str, unit: str = "") -> float:
        try:
            if not text or text.strip() in ["", "--"]:
                return 0.0
            if unit:
                text = text.replace(unit, "")
            # Remove any non-numeric characters except dot and comma
            clean = re.sub(r"[^\d.,]", "", text).replace(",", ".")
            return float(clean) if clean else 0.0
        except:
            return 0.0

    def _parse_int(self, text: str) -> int:
        if not text or text.strip() in ["", "--"]:
            return 0
        try:
            return int(text.strip())
        except ValueError:
            logger.warning(f"Falha ao converter int: '{text}'")
            return 0

    def _parse_str(self, text: str) -> str:
        if not text or text.strip() in ["", "--"]:
            return "0"
        return text.strip()

    def _extract_name_and_number(self, text: str) -> Tuple[str, int]:
        # Remove trailing numbers (jersey numbers) from name
        # ESPN often appends the number to the name like "Agustín Rossi1"
        text = text.strip()
        # Try to match name followed by space and number
        match = re.match(r"^(.*?)\s+(\d+)$", text)
        if match:
            return match.group(1).strip(), int(match.group(2))
        
        # If no space before number, try to split at the first digit that is at the end
        match_no_space = re.match(r"^([^\d]+)(\d+)$", text)
        if match_no_space:
            return match_no_space.group(1).strip(), int(match_no_space.group(2))
            
        return text, 0

    # ------------------------------------------------------------------
    # EXTRAÇÃO DE LINHA COM MAPEAMENTO DE CABEÇALHO
    # ------------------------------------------------------------------
    def _extract_player_data_robust(self, row, header_map: Dict[str, int]) -> Optional[Dict]:
        """Extrai dados de uma linha usando o mapeamento de cabeçalhos."""
        cols = row.find_all("td")
        if not cols:
            return None

        def get_val(keys: List[str], default=None):
            for key in keys:
                if key in header_map:
                    idx = header_map[key]
                    if idx < len(cols):
                        return cols[idx].text.strip()
            return default

        name_raw = get_val(["NOME", "NAME", "PLAYER"], "")
        if not name_raw:
            return None
            
        name, jersey_number = self._extract_name_and_number(name_raw)
        pos_raw = get_val(["POS"], "0")
        
        # Determina se é goleiro pela posição na linha
        is_goalkeeper = pos_raw.upper() == "G"

        data = {
            "name": name,
            "position_raw": pos_raw,
            "is_goalkeeper": is_goalkeeper,
            "age": self._parse_int(get_val(["AGE", "IDADE"])),
            "height": self._parse_float(get_val(["HT", "ALT"])),
            "weight": self._parse_float(get_val(["WT", "P"])),
            "nationality": get_val(["NAT", "NAC"], "0"),
            "games": self._parse_int(get_val(["J", "P", "GP"])),
            "substitutions": self._parse_int(get_val(["SUB", "SB"])),
            "fouls_committed": self._parse_int(get_val(["FC"])),
            "fouls_suffered": self._parse_int(get_val(["FA", "FS"])),
            "yellow_cards": self._parse_int(get_val(["YC", "CA"])),
            "red_cards": self._parse_int(get_val(["RC", "CV"])),
            "assists": self._parse_int(get_val(["A"])),
        }

        if is_goalkeeper:
            data["saves"] = self._parse_int(get_val(["D", "S", "SAVES"]))
            data["goals_conceded"] = self._parse_int(get_val(["GS"]))
        else:
            data["goals"] = self._parse_int(get_val(["G"]))
            data["total_shots"] = self._parse_int(get_val(["TC", "SH"]))
            data["shots_on_goal"] = self._parse_int(get_val(["CG", "SO"]))

        return data

    # ------------------------------------------------------------------
    # SCRAPING PRINCIPAL
    # ------------------------------------------------------------------
    def scrape_club_squad(self, espn_url: str, club_id: int):
        logger.info(f"Iniciando scraping robusto | clube={club_id} | url={espn_url}")

        errors = []
        # Acumulador de dados por jogador: {(name, is_goalkeeper): data_dict}
        accumulated_players: Dict[Tuple[str, bool], Dict] = {}

        try:
            logger.debug(f"Acessando URL da ESPN: {espn_url}")
            response = requests.get(espn_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
        except Exception as e:
            logger.exception(f"Erro ao acessar ESPN: {e}")
            return [], [], [f"Erro de conexão/HTTP: {str(e)}"]

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="Table")

        logger.debug(f"Total de tabelas encontradas: {len(tables)}")

        for idx, table in enumerate(tables, start=1):
            headers = [th.text.strip().upper() for th in table.find_all("th")]
            
            # Normalização de headers para lidar com duplicatas (como 'P') e variações
            header_map = {}
            for i, h in enumerate(headers):
                if h == "P":
                    if i < 6: h = "WT" # Peso
                    else: h = "J"     # Jogos
                
                mapping = {
                    "IDADE": "AGE", "ALT": "HT", "NAC": "NAT", "SB": "SUB",
                    "S": "SAVES", "D": "SAVES", "GC": "GA", "GS": "GA",
                    "CA": "YC", "CV": "RC", "SH": "TC", "SO": "CG",
                    "ST": "CG", "A": "AST", "G": "GLS"
                }
                normalized_h = mapping.get(h, h)
                if normalized_h not in header_map:
                    header_map[normalized_h] = i
            
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
            if not rows:
                rows = table.find_all("tr")[1:]

            logger.debug(f"Tabela #{idx} | Colunas={headers} | Linhas={len(rows)}")

            for row in rows:
                player_data = self._extract_player_data_robust(row, header_map)
                if player_data:
                    key = (player_data["name"], player_data["is_goalkeeper"])
                    if key not in accumulated_players:
                        accumulated_players[key] = player_data
                    else:
                        # Atualiza dados existentes com novos valores (se não forem 0)
                        for k, v in player_data.items():
                            if v not in [0, 0.0, "0", None]:
                                accumulated_players[key][k] = v

        logger.info(f"Total de jogadores únicos extraídos: {len(accumulated_players)}")

        saved_goalkeepers = []
        saved_field_players = []

        for (name, is_goalkeeper), data in accumulated_players.items():
            try:
                if is_goalkeeper:
                    gk_create = schemas.GoalkeeperCreate(
                        name=data["name"],
                        position="Goleiro",
                        age=data["age"],
                        height=data.get("height"),
                        weight=data.get("weight"),
                        nationality=data.get("nationality"),
                        games=data.get("games", 0),
                        substitutions=data.get("substitutions", 0),
                        saves=data.get("saves", 0),
                        goals_conceded=data.get("goals_conceded", 0),
                        assists=data.get("assists", 0),
                        fouls_committed=data.get("fouls_committed", 0),
                        fouls_suffered=data.get("fouls_suffered", 0),
                        yellow_cards=data.get("yellow_cards", 0),
                        red_cards=data.get("red_cards", 0),
                        club_id=club_id
                    )
                    
                    existing = self.db.query(models.Goalkeeper).filter(
                        models.Goalkeeper.name == name,
                        models.Goalkeeper.club_id == club_id
                    ).first()
                    
                    if existing:
                        for k, v in gk_create.model_dump(exclude_unset=True).items():
                            setattr(existing, k, v)
                        self.db.add(existing)
                        saved_goalkeepers.append(existing)
                    else:
                        new_gk = crud.create_goalkeeper(self.db, gk_create)
                        saved_goalkeepers.append(new_gk)
                else:
                    position_map = {"D": "Defensor", "M": "Meio-Campista", "A": "Atacante"}
                    pos_raw = data["position_raw"]
                    position = position_map.get(pos_raw, pos_raw)
                    
                    fp_create = schemas.FieldPlayerCreate(
                        name=data["name"],
                        position=position,
                        age=data["age"],
                        height=data.get("height"),
                        weight=data.get("weight"),
                        nationality=data.get("nationality"),
                        games=data.get("games", 0),
                        substitutions=data.get("substitutions", 0),
                        goals=data.get("goals", 0),
                        assists=data.get("assists", 0),
                        total_shots=data.get("total_shots", 0),
                        shots_on_goal=data.get("shots_on_goal", 0),
                        fouls_committed=data.get("fouls_committed", 0),
                        fouls_suffered=data.get("fouls_suffered", 0),
                        yellow_cards=data.get("yellow_cards", 0),
                        red_cards=data.get("red_cards", 0),
                        club_id=club_id
                    )
                    
                    existing = self.db.query(models.FieldPlayer).filter(
                        models.FieldPlayer.name == name,
                        models.FieldPlayer.club_id == club_id
                    ).first()
                    
                    if existing:
                        for k, v in fp_create.model_dump(exclude_unset=True).items():
                            setattr(existing, k, v)
                        self.db.add(existing)
                        saved_field_players.append(existing)
                    else:
                        new_fp = crud.create_field_player(self.db, fp_create)
                        saved_field_players.append(new_fp)
            except Exception as e:
                logger.error(f"Erro ao salvar jogador {name}: {e}")
                errors.append(name)

        self.db.commit()
        logger.success(f"Scraping finalizado | jogadores_salvos={len(saved_goalkeepers) + len(saved_field_players)}")

        return saved_goalkeepers, saved_field_players, errors
