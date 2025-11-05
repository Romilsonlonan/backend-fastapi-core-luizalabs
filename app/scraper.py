import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .schemas import AthleteScrapeResponse
import re

def scrape_espn_squad(url: str) -> List[AthleteScrapeResponse]:
    """
    Scraping da ESPN com correção automática das colunas
    """

    # Headers para simular navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        print(f"🌐 Acessando: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"📊 Status: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')

        players_data: List[AthleteScrapeResponse] = []

        # Encontra todas as tabelas
        tabelas = soup.find_all("table")
        print(f"📊 ENCONTRADAS {len(tabelas)} TABELAS NA PÁGINA")

        for i, tabela in enumerate(tabelas, 1):
            print(f"\n🔍 ANALISANDO TABELA {i}")

            # Captura o cabeçalho original
            cabecalho_original = [th.text.strip() for th in tabela.find_all("th")]
            print(f"  - Cabeçalho: {cabecalho_original}")
            print(f"  - Número de colunas: {len(cabecalho_original)}")

            # Determina o tipo de tabela
            if len(cabecalho_original) <= 14:  # Tabela de goleiros
                print("  ✅ IDENTIFICADA COMO TABELA DE GOLEIROS")
                tipo_tabela = "goleiros"
            else:  # Tabela de jogadores de campo
                print("  ✅ IDENTIFICADA COMO TABELA DE JOGADORES DE CAMPO")
                tipo_tabela = "jogadores_campo"

            # Processa as linhas
            linhas = []
            for tr in tabela.find_all("tr")[1:]:  # Pula o cabeçalho
                colunas = [td.text.strip() for td in tr.find_all("td")]
                if colunas:  # Só adiciona se tiver dados
                    linhas.append(colunas)

            print(f"  - Total de linhas: {len(linhas)}")

            for linha in linhas:
                if len(linha) < 3:  # Verifica se tem dados suficientes
                    continue

                try:
                    # Extrai nome e camisa
                    nome_original = linha[0]
                    match = re.search(r'(\d+)$', nome_original.strip())
                    if match:
                        numero = int(match.group(1))
                        nome = nome_original[:match.start()].strip()
                    else:
                        nome = nome_original.strip()
                        numero = 0

                    # Procura posição
                    posicao = None
                    for valor in linha:
                        if valor in ['G', 'D', 'M', 'A']:
                            posicao = valor
                            break

                    if not posicao:
                        continue

                    # Dados base
                    age = 0
                    if len(linha) > 3:
                        age_text = linha[3].strip()
                        if age_text.isdigit():
                            age = int(age_text)

                    height = 0.0
                    if len(linha) > 4:
                        height_text = linha[4].strip()
                        if 'm' in height_text:
                            height = float(height_text.replace(' m', ''))

                    weight = 0.0
                    if len(linha) > 5:
                        weight_text = linha[5].strip()
                        if 'kg' in weight_text:
                            weight = float(weight_text.replace(' kg', ''))

                    nationality = linha[6].strip() if len(linha) > 6 else ""

                    # Estatísticas base
                    games = 0
                    substitute_appearances = 0
                    assists = 0
                    fouls_committed = 0
                    fouls_suffered = 0
                    yellow_cards = 0
                    red_cards = 0

                    if len(linha) > 7:
                        games_text = linha[7].strip()
                        if games_text.isdigit():
                            games = int(games_text)

                    if len(linha) > 8:
                        sub_text = linha[8].strip()
                        if sub_text.isdigit():
                            substitute_appearances = int(sub_text)

                    if len(linha) > 11:
                        ast_text = linha[11].strip()
                        if ast_text.isdigit():
                            assists = int(ast_text)

                    # Estatísticas específicas por tipo
                    goals = 0
                    shots = 0
                    shots_on_goal = 0
                    defenses = 0
                    goals_conceded = 0

                    if tipo_tabela == "goleiros":
                        # Estatísticas de goleiros
                        if len(linha) > 9:
                            def_text = linha[9].strip()
                            if def_text.isdigit():
                                defenses = int(def_text)

                        if len(linha) > 10:
                            gc_text = linha[10].strip()
                            if gc_text.isdigit():
                                goals_conceded = int(gc_text)
                    else:
                        # Estatísticas de jogadores de campo
                        if len(linha) > 9:
                            goals_text = linha[9].strip()
                            if goals_text.isdigit():
                                goals = int(goals_text)

                        if len(linha) > 10:
                            shots_text = linha[10].strip()
                            if shots_text.isdigit():
                                shots = int(shots_text)

                    # Campos que não estão disponíveis na ESPN
                    salary = 0.0
                    injuries = 0
                    wrong_passes = 0
                    correct_passes = 0

                    player_data = AthleteScrapeResponse(
                        name=nome,
                        position=posicao,
                        age=age,
                        height=height,
                        weight=weight,
                        nationality=nationality,
                        games=games,
                        substitute_appearances=substitute_appearances,
                        goals=goals,
                        assists=assists,
                        shots=shots,
                        shots_on_goal=shots_on_goal,
                        fouls_committed=fouls_committed,
                        fouls_suffered=fouls_suffered,
                        yellow_cards=yellow_cards,
                        red_cards=red_cards,
                        defenses=defenses,
                        goals_conceded=goals_conceded,
                        salary=salary,
                        injuries=injuries,
                        wrong_passes=wrong_passes,
                        correct_passes=correct_passes
                    )
                    players_data.append(player_data)

                except Exception as e:
                    print(f"⚠️ Erro ao processar linha: {e}")
                    continue

        print(f"✅ Total de jogadores processados: {len(players_data)}")
        return players_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de requisição: {e}")
        raise Exception(f"Erro ao acessar a URL: {e}")
    except Exception as e:
        print(f"❌ Erro geral no scraping: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Erro no scraping: {e}")

# Exemplo de uso (para testes)
if __name__ == "__main__":
    url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/ordenar/position/dir/desce/bra.cr_vasco_da_gama"
    scraped_players = scrape_espn_squad(url)
    for player in scraped_players:
        print(f"{player.name} - {player.position} - G:{player.goals} - D:{player.defenses}")
