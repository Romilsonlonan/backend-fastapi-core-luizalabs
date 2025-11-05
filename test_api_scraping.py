import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
CLUB_ID = 1  # ID do clube Vasco
TEST_URL = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/ordenar/position/dir/desce/bra.cr_vasco_da_gama"

# Função para obter token
def get_token():
    import os
    login_data = {
        "username": os.getenv("ADMIN_EMAIL", "admin@cbfmanager.com"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123")
    }

    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return None

# Função para testar o scraping
def test_scraping():
    print("� Iniciando teste de scraping...")

    # Obtém token
    token = get_token()
    if not token:
        print("❌ Não foi possível obter token. Verifique as credenciais.")
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Dados para o scraping
    scrape_data = {
        "url": TEST_URL
    }

    print(f"🌐 Testando URL: {TEST_URL}")
    print(f"📊 Clube ID: {CLUB_ID}")

    try:
        # Faz a requisição para o endpoint de scraping
        response = requests.post(
            f"{BASE_URL}/scrape-athletes/{CLUB_ID}",
            params=scrape_data,
            headers=headers
        )

        print(f"📡 Status da resposta: {response.status_code}")

        if response.status_code == 200:
            players = response.json()
            print(f"✅ Sucesso! {len(players)} jogadores encontrados:")
            for player in players[:5]:  # Mostra apenas os 5 primeiros
                print(f"  - {player.get('name', 'N/A')} ({player.get('position', 'N/A')})")
        else:
            print(f"❌ Erro na resposta: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📄 Detalhes do erro: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Texto do erro: {response.text}")

    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraping()
