import requests
import re
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Union, Dict
from loguru import logger
from ... import models, schemas
from ..athletes.interfaces import IAthleteRepository
from ...core.exceptions import InfrastructureException, DomainException

class ScraperService:
    def __init__(self, athlete_repository: IAthleteRepository):
        self.athlete_repository = athlete_repository
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def scrape_club_players(self, espn_url: str, club_id: int):
        logger.info(f"Iniciando scraping robusto | clube={club_id} | url={espn_url}")
        
        try:
            response = requests.get(espn_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
        except Exception as e:
            logger.error(f"Erro ao acessar ESPN: {e}")
            raise InfrastructureException(f"Erro ao acessar a ESPN: {str(e)}")

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_=lambda x: x and "Table" in x)
        
        if not tables:
            raise DomainException("Nenhum dado de atleta encontrado na página da ESPN.")

        accumulated_players: dict[tuple[str, bool], dict] = {}

        for table in tables:
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
            
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")[1:]
            
            # Identifica se é tabela de goleiros
            is_goalkeeper_table = any(h in headers for h in ["GS", "SAVES", "D", "GOLS SOFRIDOS", "S", "GC"])

            for row in rows:
                player_data = self._extract_player_from_row(row, is_goalkeeper_table, header_map)
                if player_data:
                    key = (player_data["name"], player_data["position"] == "Goleiro")
                    if key not in accumulated_players:
                        accumulated_players[key] = player_data
                    else:
                        # Merge data
                        for k, v in player_data.items():
                            if v not in [0, 0.0, "0", "N/A", None]:
                                accumulated_players[key][k] = v

        new_count = 0
        updated_count = 0

        for (name, is_gk), data in accumulated_players.items():
            data["club_id"] = club_id
            if is_gk:
                is_new = self._save_goalkeeper(data)
            else:
                is_new = self._save_field_player(data)
            
            if is_new:
                new_count += 1
            else:
                updated_count += 1

        return {
            "new_count": new_count,
            "updated_count": updated_count,
            "total_count": len(accumulated_players)
        }

    def _save_goalkeeper(self, data: dict) -> bool:
        from ... import models
        existing = self.athlete_repository.db.query(models.Goalkeeper).filter(
            models.Goalkeeper.name == data["name"],
            models.Goalkeeper.club_id == data["club_id"]
        ).first()
        
        is_new = False
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            self.athlete_repository.db.add(existing)
        else:
            new_gk = models.Goalkeeper(**data)
            self.athlete_repository.db.add(new_gk)
            is_new = True
        self.athlete_repository.db.commit()
        return is_new

    def _save_field_player(self, data: dict) -> bool:
        from ... import models
        existing = self.athlete_repository.db.query(models.FieldPlayer).filter(
            models.FieldPlayer.name == data["name"],
            models.FieldPlayer.club_id == data["club_id"]
        ).first()
        
        is_new = False
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            self.athlete_repository.db.add(existing)
        else:
            new_fp = models.FieldPlayer(**data)
            self.athlete_repository.db.add(new_fp)
            is_new = True
        self.athlete_repository.db.commit()
        return is_new

    def _extract_player_from_row(self, row, is_goalkeeper: bool, header_map: dict) -> Optional[dict]:
        cols = row.find_all("td")
        if len(cols) < 5: # Mínimo de colunas para ser válido
            return None

        name_text = cols[0].text.strip()
        # Limpeza de nome (remove números de camisa grudados)
        name = re.sub(r'\d+$', '', name_text).strip()
        
        try:
            def get_val(possible_headers, default=0, is_float=False):
                for h in possible_headers:
                    if h in header_map:
                        idx = header_map[h]
                        if idx < len(cols):
                            val_text = cols[idx].text.strip()
                            return self._parse_float(val_text, "") if is_float else self._parse_int(val_text)
                return default

            # Extração robusta de nacionalidade
            nationality = "N/A"
            if "NAC" in header_map or "NAT" in header_map:
                idx = header_map.get("NAC") or header_map.get("NAT")
                if idx < len(cols):
                    cell = cols[idx]
                    text = cell.text.strip()
                    img = cell.find("img")
                    if img:
                        nationality = img.get("title") or img.get("alt") or text
                    else:
                        nationality = text
            
            if not nationality or nationality.strip() in ["", "--", "0", "N / D"]:
                nationality = "N/A"

            data = {
                "name": name,
                "age": get_val(["IDADE", "AGE"]),
                "height": get_val(["ALT", "HT", "ALT"], 0.0, True),
                "weight": get_val(["WT", "P"], 0.0, True),
                "nationality": nationality.strip(),
                "games": get_val(["J", "P", "APP"]),
                "substitutions": get_val(["SUB", "SB"]),
            }

            if is_goalkeeper:
                data.update({
                    "position": "Goleiro",
                    "saves": get_val(["S", "D", "SV", "SAVES"]),
                    "goals_conceded": get_val(["GC", "GS", "GA"]),
                    "assists": get_val(["A", "AST"]),
                    "fouls_committed": get_val(["FC"]),
                    "fouls_suffered": get_val(["FA", "FS"]),
                    "yellow_cards": get_val(["YC", "CA"]),
                    "red_cards": get_val(["RC", "CV"]),
                })
            else:
                pos_raw = cols[header_map["POS"]].get_text(strip=True) if "POS" in header_map and header_map["POS"] < len(cols) else ""
                position_map = {"D": "Defensor", "M": "Meio-Campista", "A": "Atacante"}
                data.update({
                    "position": position_map.get(pos_raw, pos_raw or "Jogador"),
                    "goals": get_val(["G", "GLS"]),
                    "assists": get_val(["A", "AST"]),
                    "total_shots": get_val(["TC", "SH"]),
                    "shots_on_goal": get_val(["CG", "ST"]),
                    "fouls_committed": get_val(["FC"]),
                    "fouls_suffered": get_val(["FA", "FS"]),
                    "yellow_cards": get_val(["YC", "CA"]),
                    "red_cards": get_val(["RC", "CV"]),
                })
            
            # Log para depuração
            logger.debug(f"Atleta extraído: {data['name']} | G={data.get('goals', 0)} | A={data.get('assists', 0)} | FC={data.get('fouls_committed', 0)} | FS={data.get('fouls_suffered', 0)} | YC={data.get('yellow_cards', 0)} | RC={data.get('red_cards', 0)}")
            
            return data
        except Exception as e:
            logger.debug(f"Pulando linha devido a erro de parse: {e}")
            return None

    def _parse_int(self, text: str) -> int:
        try:
            clean = re.sub(r"[^\d]", "", text)
            return int(clean) if clean else 0
        except:
            return 0

    def _parse_float(self, text: str, unit: str) -> float:
        try:
            if not text or text.strip() in ["", "--"]:
                return 0.0
            # Remove any non-numeric characters except dot and comma
            clean = re.sub(r"[^\d.,]", "", text).replace(",", ".")
            return float(clean) if clean else 0.0
        except:
            return 0.0
