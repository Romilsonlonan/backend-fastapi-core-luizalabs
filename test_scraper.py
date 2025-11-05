import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adiciona o diretório 'app' ao sys.path para que as importações funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from scraper_service import ESPNScraperService
from database import Base, SessionLocal, engine
from models import Club, Player # Importar modelos para garantir que as tabelas existam

# Garante que as tabelas sejam criadas no banco de dados de teste
Base.metadata.create_all(bind=engine)

def run_test_scraper():
    db = SessionLocal()
    try:
        scraper_service = ESPNScraperService(db)

        # Exemplo de URL da ESPN para o Vasco da Gama
        espn_url = "https://www.espn.com.br/futebol/time/elenco/_/id/874/vasco-da-gama"

        # Crie um clube de teste ou use um existente
        # Para este teste, vamos criar um clube temporário se não houver um com ID 1
        club_id = 1
        test_club = db.query(Club).filter(Club.id == club_id).first()
        if not test_club:
            print(f"Criando clube de teste com ID {club_id}...")
            test_club = Club(
                id=club_id,
                name="Vasco da Gama Teste",
                initials="VAS",
                city="Rio de Janeiro",
                espn_url=espn_url # Define a URL da ESPN para o clube de teste
            )
            db.add(test_club)
            db.commit()
            db.refresh(test_club)
            print(f"Clube de teste '{test_club.name}' criado.")
        else:
            print(f"Usando clube existente com ID {club_id}: {test_club.name}")
            # Atualiza a URL da ESPN para o clube existente, se necessário
            if test_club.espn_url != espn_url:
                test_club.espn_url = espn_url
                db.commit()
                db.refresh(test_club)
                print(f"URL da ESPN do clube ID {club_id} atualizada para: {espn_url}")


        print(f"\n--- Iniciando teste de scraping para o clube ID {club_id} ({test_club.name}) ---")
        updated_players, errors = scraper_service.scrape_club_squad(espn_url, club_id)

        if updated_players:
            print("\n--- Jogadores processados com sucesso: ---")
            for player in updated_players:
                print(f"ID: {player.id}, Nome: {player.name}, Posição: {player.position}, Clube ID: {player.club_id}")
        else:
            print("\n--- Nenhum jogador foi processado. ---")

        if errors:
            print("\n--- Erros encontrados durante o scraping: ---")
            for error in errors:
                print(f"- {error}")
        else:
            print("\n--- Nenhum erro reportado pelo scraper. ---")

    except Exception as e:
        print(f"\n❌ Erro inesperado durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\n--- Teste de scraping concluído ---")

if __name__ == "__main__":
    run_test_scraper()
