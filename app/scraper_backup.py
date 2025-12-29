from typing import List

import requests
from bs4 import BeautifulSoup

from .schemas import AthleteScrapeResponse


def scrape_espn_squad(url: str) -> List[AthleteScrapeResponse]:
    response = requests.get(url)
    response.raise_for_status()  # Levanta um erro para status de resposta HTTP ruins (4xx ou 5xx)

    soup = BeautifulSoup(response.text, 'html.parser')

    players_data: List[AthleteScrapeResponse] = []

    # Encontrar a tabela de elenco
    # A estrutura da ESPN pode mudar, então esta é uma suposição baseada em tabelas comuns.
    # Pode ser necessário inspecionar o HTML da página para encontrar o seletor correto.
    table = soup.find('table', class_='Table Table--responsive Table--fixed-Header')
    if not table:
        print("Tabela de elenco não encontrada. Verifique o seletor CSS.")
        return []

    rows = table.find('tbody').find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 15:  # Deve ter pelo menos 15 colunas conforme o pedido
            continue

        try:
            name = cols[1].find('a').text.strip() if cols[1].find('a') else cols[1].text.strip()
            position = cols[2].text.strip()
            age = int(cols[3].text.strip()) if cols[3].text.strip().isdigit() else 0
            height = float(cols[4].text.strip().replace(' m', '')) if 'm' in cols[4].text.strip() else 0.0
            weight = float(cols[5].text.strip().replace(' kg', '')) if 'kg' in cols[5].text.strip() else 0.0
            nationality = cols[6].text.strip()
            games = int(cols[7].text.strip()) if cols[7].text.strip().isdigit() else 0
            substitute_appearances = int(cols[8].text.strip()) if cols[8].text.strip().isdigit() else 0
            defenses = int(cols[9].text.strip()) if cols[9].text.strip().isdigit() else 0  # D
            goals_conceded = int(cols[10].text.strip()) if cols[10].text.strip().isdigit() else 0  # GS
            assists = int(cols[11].text.strip()) if cols[11].text.strip().isdigit() else 0  # A
            fouls_committed = int(cols[12].text.strip()) if cols[12].text.strip().isdigit() else 0  # FC
            fouls_suffered = int(cols[13].text.strip()) if cols[13].text.strip().isdigit() else 0  # FS
            yellow_cards = int(cols[14].text.strip()) if cols[14].text.strip().isdigit() else 0  # CA
            red_cards = int(cols[15].text.strip()) if cols[15].text.strip().isdigit() else 0  # CV

            # Campos que não estão diretamente na tabela da ESPN ou precisam de lógica adicional
            # Para simplificar, vamos definir como 0 ou None por enquanto, ou buscar se possível.
            # O usuário não especificou como obter 'Gols', 'Finalizações', 'Chutes a gol', 'Lesões', 'Passes errados', 'Passes corretos', 'Salário'
            # A ESPN geralmente não mostra salário ou passes em tabelas de elenco.
            goals = 0  # Gols totais, não goals_2025
            shots = 0
            shots_on_goal = 0
            salary = 0.0
            injuries = 0
            wrong_passes = 0
            correct_passes = 0

            player_data = AthleteScrapeResponse(
                name=name,
                position=position,
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
            print(f"Erro ao processar linha da tabela: {e}")
            continue

    return players_data


# Exemplo de uso (para testes)
if __name__ == "__main__":
    url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/liga/BRA.1/temporada/2025"
    scraped_players = scrape_espn_squad(url)
    for player in scraped_players:
        print(player.name, player.position, player.age)
