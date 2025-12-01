#!/usr/bin/env python3
"""
Script genérico para adicionar clubes ao banco de dados
Uso: python add_club.py "Nome do Clube" "SIG" "Cidade" "YYYY-MM-DD" [titulos] [centro_treinamento]
"""

import sys

import requests


def add_club_to_database(name, initials, city, foundation_date, br_titles=0, training_center=None):
    """Adiciona um clube ao banco de dados via API"""

    # Dados do clube
    club_data = {
        "name": name,
        "initials": initials,
        "city": city,
        "foundation_date": foundation_date,
        "br_titles": br_titles,
        "training_center": training_center
    }

    try:
        # Faz login para obter token
        print("🔐 Fazendo login...")
        login_response = requests.post(
            "http://localhost:8000/token",
            data={
                "username": os.getenv("ADMIN_EMAIL"),
                "password": os.getenv("ADMIN_PASSWORD")
            }
        )

        if login_response.status_code != 200:
            print(f"❌ Erro ao fazer login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            return False

        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✅ Login realizado com sucesso!")

        # Cria o clube via API
        print(f"📡 Criando clube: {name}...")
        response = requests.post(
            "http://localhost:8000/clubs/",
            data=club_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            club_info = response.json()
            print("✅ Clube criado com sucesso!")
            print(f"📊 ID do clube: {club_info['id']}")
            print(f"🏷️  Nome: {club_info['name']}")
            print(f"🏙️  Cidade: {club_info['city']}")
            print(f"🏆 Títulos: {club_info.get('br_titles', 0)}")
            return True
        else:
            print(f"❌ Erro ao criar clube: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Certifique-se de que o servidor FastAPI está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("❌ Uso incorreto!")
        print("Uso: python add_club.py \"Nome do Clube\" \"SIG\" \"Cidade\" \"YYYY-MM-DD\" [titulos] [centro_treinamento]")
        print("\nExemplos:")
        print('  python add_club.py "Club de Regatas Vasco da Gama" "VAS" "Rio de Janeiro" "1898-08-21" 4 "CT Moacyr Barbosa"')
        print('  python add_club.py "Flamengo" "FLA" "Rio de Janeiro" "1895-11-15" 7')
        print('  python add_club.py "Palmeiras" "PAL" "São Paulo" "1914-08-26" 12 "Academia de Futebol"')
        return

    name = sys.argv[1]
    initials = sys.argv[2]
    city = sys.argv[3]
    foundation_date = sys.argv[4]
    br_titles = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    training_center = sys.argv[6] if len(sys.argv) > 6 else None

    print("🚀 Adicionando clube ao banco de dados...")
    print("=" * 50)
    print("📋 Dados do clube:")
    print(f"   Nome: {name}")
    print(f"   Sigla: {initials}")
    print(f"   Cidade: {city}")
    print(f"   Fundação: {foundation_date}")
    print(f"   Títulos: {br_titles}")
    print(f"   CT: {training_center or 'N/A'}")
    print("=" * 50)

    success = add_club_to_database(name, initials, city, foundation_date, br_titles, training_center)

    if success:
        print("\n✅ Processo concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Acesse o frontend em http://localhost:3000")
        print("2. Faça login com suas credenciais")
        print("3. Vá para a página de Clubes")
        print("4. Selecione o clube criado")
        print("5. Clique em 'Atualizar Atletas' para buscar os dados do ESPN")
        print(f"\n🔗 URL ESPN sugerida para {name}:")
        print("   https://www.espn.com.br/futebol/time/_/id/XXXX/nome-do-clube")
        print("   (Substitua XXXX pelo ID do clube na ESPN)")
    else:
        print("\n❌ Falha ao adicionar clube!")


if __name__ == "__main__":
    main()
