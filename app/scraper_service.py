import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from . import models, schemas, crud
import re

class ESPNScraperService:
    """
    Serviço oficial de scraping da ESPN para integração com o banco de dados
    Usa apenas colunas que realmente existem no web scraping
    """

    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def _parse_height(self, height_text: str) -> float:
        """Converte altura de texto para metros"""
        if not height_text or height_text == '--':
            return 0.0
        # Remove 'm' e espaços, converte para float
        height_clean = height_text.replace('m', '').strip()
        try:
            return float(height_clean)
        except ValueError:
            return 0.0

    def _parse_weight(self, weight_text: str) -> float:
        """Converte peso de texto para kg"""
        if not weight_text or weight_text == '--':
            return 0.0
        # Remove 'kg' e espaços, converte para float
        weight_clean = weight_text.replace('kg', '').strip()
        try:
            return float(weight_clean)
        except ValueError:
            return 0.0

    def _parse_stat(self, stat_text: str) -> int:
        """Converte estatística de texto para inteiro"""
        if not stat_text or stat_text == '--':
            return 0
        try:
            return int(stat_text.strip())
        except ValueError:
            return 0

    def _extract_name_and_number(self, name_text: str) -> Tuple[str, int]:
        """Extrai nome e número da camisa do texto, se presente no final do nome."""
        # O usuário indicou que o número da camisa aparece no final do nome, ex: "Nome do Jogador 10"
        match = re.match(r'^(.*?)\s*(\d+)$', name_text.strip())
        if match:
            name = match.group(1).strip()
            number = int(match.group(2))
            return name, number
        return name_text.strip(), 0 # Retorna 0 se nenhum número for encontrado

    def _extract_player_data(self, row, is_goalkeeper: bool = False) -> Dict:
        """Extrai dados de uma linha da tabela usando as colunas reais do scraping."""
        cols = row.find_all('td')
        # print(f"DEBUG: _extract_player_data - Raw columns: {[c.get_text(strip=True) for c in cols]}") # Debug raw columns

        # Mapeamento de índices baseado nas colunas fornecidas pelo usuário
        # Goleiros: Nome, POS, Idade, Alt, P, NAC, J, SUB, D, GS, A, FC, FS, CA, CV
        # Jogadores de campo: Nome, POS, Idade, Alt, P, NAC, J, SUB, G, A, TC, CG, FC, FS, CA, CV

        # Colunas comuns
        name_col_idx = 0
        pos_col_idx = 1
        age_col_idx = 2
        height_col_idx = 3
        weight_col_idx = 4
        nationality_col_idx = 5
        games_col_idx = 6
        sub_appearances_col_idx = 7

        if len(cols) < (sub_appearances_col_idx + 1): # Mínimo de colunas comuns
            print(f"DEBUG: _extract_player_data - Not enough common columns ({len(cols)}), skipping row.")
            return None

        # Extrai nome e número da camisa
        raw_name_text = cols[name_col_idx].get_text(strip=True)
        name, jersey_number = self._extract_name_and_number(raw_name_text)

        position = cols[pos_col_idx].get_text(strip=True)

        if not name or not position:
            print(f"DEBUG: _extract_player_data - Name or Position missing, skipping row. Name: '{name}', Position: '{position}'")
            return None

        player_data = {
            'name': name,
            'jersey_number': jersey_number,
            'position': position,
            'age': self._parse_stat(cols[age_col_idx].get_text(strip=True)) if len(cols) > age_col_idx else 0,
            'height': self._parse_height(cols[height_col_idx].get_text(strip=True)) if len(cols) > height_col_idx else 0.0,
            'weight': self._parse_weight(cols[weight_col_idx].get_text(strip=True)) if len(cols) > weight_col_idx else 0.0,
            'nationality': cols[nationality_col_idx].get_text(strip=True) if len(cols) > nationality_col_idx else '',
            'games': self._parse_stat(cols[games_col_idx].get_text(strip=True)) if len(cols) > games_col_idx else 0,
            'substitute_appearances': self._parse_stat(cols[sub_appearances_col_idx].get_text(strip=True)) if len(cols) > sub_appearances_col_idx else 0,
        }

        # Estatísticas específicas por posição
        if is_goalkeeper:
            # Goleiros: D, GS, A, FC, FS, CA, CV (a partir do índice 8)
            # D = Defesas, GS = Gols Sofridos (Goals Conceded)
            defenses_idx = 8
            goals_conceded_idx = 9
            assists_idx = 10
            fouls_committed_idx = 11
            fouls_suffered_idx = 12
            yellow_cards_idx = 13
            red_cards_idx = 14

            player_data.update({
                'defenses': self._parse_stat(cols[defenses_idx].get_text(strip=True)) if len(cols) > defenses_idx else 0,
                'goals_conceded': self._parse_stat(cols[goals_conceded_idx].get_text(strip=True)) if len(cols) > goals_conceded_idx else 0,
                'assists': self._parse_stat(cols[assists_idx].get_text(strip=True)) if len(cols) > assists_idx else 0,
                'fouls_committed': self._parse_stat(cols[fouls_committed_idx].get_text(strip=True)) if len(cols) > fouls_committed_idx else 0,
                'fouls_suffered': self._parse_stat(cols[fouls_suffered_idx].get_text(strip=True)) if len(cols) > fouls_suffered_idx else 0,
                'yellow_cards': self._parse_stat(cols[yellow_cards_idx].get_text(strip=True)) if len(cols) > yellow_cards_idx else 0,
                'red_cards': self._parse_stat(cols[red_cards_idx].get_text(strip=True)) if len(cols) > red_cards_idx else 0,
                # Zera estatísticas de jogadores de campo
                'goals': 0,
                'shots': 0,
                'shots_on_goal': 0,
            })
        else:
            # Jogadores de campo: G, A, TC, CG, FC, FS, CA, CV (a partir do índice 8)
            # G = Gols, A = Assistências, TC = Tentativas de Cruzamento (Shots), CG = Cruzamentos Certos (Shots on Goal)
            goals_idx = 8
            assists_idx = 9
            shots_idx = 10
            shots_on_goal_idx = 11
            fouls_committed_idx = 12
            fouls_suffered_idx = 13
            yellow_cards_idx = 14
            red_cards_idx = 15

            player_data.update({
                'goals': self._parse_stat(cols[goals_idx].get_text(strip=True)) if len(cols) > goals_idx else 0,
                'assists': self._parse_stat(cols[assists_idx].get_text(strip=True)) if len(cols) > assists_idx else 0,
                'shots': self._parse_stat(cols[shots_idx].get_text(strip=True)) if len(cols) > shots_idx else 0,
                'shots_on_goal': self._parse_stat(cols[shots_on_goal_idx].get_text(strip=True)) if len(cols) > shots_on_goal_idx else 0,
                'fouls_committed': self._parse_stat(cols[fouls_committed_idx].get_text(strip=True)) if len(cols) > fouls_committed_idx else 0,
                'fouls_suffered': self._parse_stat(cols[fouls_suffered_idx].get_text(strip=True)) if len(cols) > fouls_suffered_idx else 0,
                'yellow_cards': self._parse_stat(cols[yellow_cards_idx].get_text(strip=True)) if len(cols) > yellow_cards_idx else 0,
                'red_cards': self._parse_stat(cols[red_cards_idx].get_text(strip=True)) if len(cols) > red_cards_idx else 0,
                # Zera estatísticas de goleiro
                'defenses': 0,
                'goals_conceded': 0,
            })

        return player_data

    def scrape_club_squad(self, espn_url: str, club_id: int) -> Tuple[List[models.Player], List[str]]:
        """
        Faz scraping do elenco de um clube e salva no banco de dados
        Usa apenas dados reais do web scraping, sem campos fictícios
        Agora é dinâmico e aceita qualquer URL da ESPN

        Args:
            espn_url: URL da ESPN para fazer o scraping (ex: https://www.espn.com.br/futebol/time/elenco/_/id/3454)
            club_id: ID do clube no banco de dados

        Returns:
            Tuple com (lista de jogadores criados/atualizados, lista de erros)
        """
        errors = []
        updated_players = []

        try:
            print(f"🌐 Iniciando scraping do clube ID: {club_id}")
            print(f"📡 URL: {espn_url}")

            # Faz requisição HTTP com headers dinâmicos
            response = requests.get(espn_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Debug: Print all h2 tags found on the page (still useful for context)
            all_h2_tags = soup.find_all('h2')
            print(f"DEBUG: Todos os cabeçalhos <h2> encontrados: {[h2.get_text(strip=True) for h2 in all_h2_tags]}")

            all_players_data: List[Dict] = []

            # Encontra todas as tabelas com a classe 'Table'
            tables = soup.find_all('table', class_='Table')
            print(f"DEBUG: Encontradas {len(tables)} tabelas com class='Table'.")

            for i, table in enumerate(tables):
                print(f"\nDEBUG: --- Processando Tabela {i+1} ---")
                thead = table.find('thead')
                if not thead:
                    print(f"DEBUG: Thead não encontrado na Tabela {i+1}, pulando.")
                    continue

                headers = [th.get_text(strip=True) for th in thead.find_all('th')]
                print(f"DEBUG: Cabeçalhos da Tabela {i+1}: {headers}")

                is_goalkeeper_table = False
                # Heurística para identificar o tipo de tabela pelos cabeçalhos
                if 'D' in headers and 'GS' in headers: # Defesas e Gols Sofridos são típicos de goleiros
                    is_goalkeeper_table = True
                    print(f"DEBUG: Tabela {i+1} identificada como GOLEIROS pelos cabeçalhos.")
                elif 'G' in headers and 'A' in headers and 'TC' in headers: # Gols, Assistências, Tentativas de Cruzamento são típicos de jogadores de campo
                    is_goalkeeper_table = False
                    print(f"DEBUG: Tabela {i+1} identificada como JOGADORES DE CAMPO pelos cabeçalhos.")
                else:
                    print(f"DEBUG: Não foi possível determinar o tipo da Tabela {i+1} pelos cabeçalhos, pulando.")
                    continue # Pula tabelas que não podem ser identificadas

                tbody = table.find('tbody')
                if not tbody:
                    print(f"DEBUG: Tbody não encontrado na Tabela {i+1}, pulando.")
                    continue

                rows = tbody.find_all('tr')
                print(f"DEBUG: Encontradas {len(rows)} linhas na Tabela {i+1}.")

                for row in rows:
                    raw_cols_text = [td.get_text(strip=True) for td in row.find_all('td')]
                    print(f"DEBUG: _extract_player_data - Raw columns (full text) for Tabela {i+1}: {raw_cols_text}")

                    player_data = self._extract_player_data(row, is_goalkeeper=is_goalkeeper_table)
                    if player_data:
                        all_players_data.append(player_data)

            print(f"✅ Total de jogadores extraídos: {len(all_players_data)}")

            # Salva/atualiza no banco de dados
            for player_data in all_players_data:
                try:
                    # Verifica se o jogador já existe (por nome e clube)
                    existing_player = self.db.query(models.Player).filter(
                        models.Player.name == player_data['name'],
                        models.Player.club_id == club_id
                    ).first()

                    if existing_player:
                        # Atualiza jogador existente
                        for key, value in player_data.items():
                            setattr(existing_player, key, value)
                        updated_players.append(existing_player)
                        print(f"🔄 Atualizado: {existing_player.name} (ID: {existing_player.id}, Posição: {existing_player.position}, Número: {existing_player.jersey_number})")
                    else:
                        # Cria novo jogador
                        player_create = schemas.PlayerCreate(
                            **player_data,
                            club_id=club_id
                        )
                        new_player = crud.create_player(self.db, player_create)
                        updated_players.append(new_player)
                        print(f"✅ Criado: {new_player.name} (ID: {new_player.id}, Posição: {new_player.position}, Número: {new_player.jersey_number})")

                except Exception as e:
                    error_msg = f"Erro ao salvar {player_data['name']}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")

            # Commit final
            self.db.commit()
            print(f"💾 Commit realizado. Jogadores processados: {len(updated_players)}")

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de requisição: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Erro geral: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {e}")
            import traceback
            traceback.print_exc()

        return updated_players, errors

    def get_club_players(self, club_id: int) -> List[models.Player]:
        """Retorna todos os jogadores de um clube"""
        return self.db.query(models.Player).filter(models.Player.club_id == club_id).all()
