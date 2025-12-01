import json

import requests
from bs4 import BeautifulSoup


def analisar_colunas_espn(url: str):
    """
    Analisa e lista todas as colunas das tabelas da ESPN
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        print(f"🌐 Acessando: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontra todas as tabelas
        tabelas = soup.find_all("table")
        print(f"\n📊 ENCONTRADAS {len(tabelas)} TABELAS NA PÁGINA")

        resultado = {
            "tabelas": [],
            "total_tabelas": len(tabelas)
        }

        for i, tabela in enumerate(tabelas, 1):
            print(f"\n{'=' * 60}")
            print(f"🔍 TABELA {i}")
            print(f"{'=' * 60}")

            # Captura o cabeçalho
            cabecalho = [th.text.strip() for th in tabela.find_all("th")]
            print(f"📋 CABEÇALHO ({len(cabecalho)} colunas):")
            for j, col in enumerate(cabecalho, 1):
                print(f"  {j:2d}. {col}")

            # Analisa o tipo de tabela
            if len(cabecalho) <= 14:
                tipo = "GOLEIROS"
            else:
                tipo = "JOGADORES DE CAMPO"

            print(f"\n🏷️  TIPO IDENTIFICADO: {tipo}")

            # Pega algumas linhas de exemplo
            tbody = tabela.find("tbody")
            if tbody:
                linhas = tbody.find_all("tr")[:3]  # Primeiras 3 linhas como exemplo
                print("\n📄 EXEMPLOS DE LINHAS:")

                for k, tr in enumerate(linhas, 1):
                    colunas = [td.text.strip() for td in tr.find_all("td")]
                    print(f"\n  Linha {k} ({len(colunas)} colunas):")
                    for j, col in enumerate(colunas, 1):
                        if j <= len(cabecalho):
                            print(f"    {cabecalho[j - 1]:<15}: {col}")
                        else:
                            print(f"    Coluna {j}: {col}")

            # Salva informações da tabela
            info_tabela = {
                "numero": i,
                "tipo": tipo,
                "colunas": cabecalho,
                "numero_colunas": len(cabecalho)
            }
            resultado["tabelas"].append(info_tabela)

            print(f"\n{'=' * 60}")

        # Salva resultado em JSON
        with open('/home/romilson/Projetos/luizalabs/backend/fastapi_core/analise_colunas_espn.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print("\n✅ Análise completa! Resultado salvo em 'analise_colunas_espn.json'")

        # Resumo final
        print("\n📊 RESUMO DAS COLUNAS:")
        print(f"Tabelas encontradas: {len(tabelas)}")

        for tabela in resultado["tabelas"]:
            print(f"\nTabela {tabela['numero']} ({tabela['tipo']}):")
            print(f"  {tabela['numero_colunas']} colunas")
            print(f"  Principais: {', '.join(tabela['colunas'][:5])}...")

        return resultado

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


# Testa com o Vasco da Gama
if __name__ == "__main__":
    url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/ordenar/position/dir/desce/bra.cr_vasco_da_gama"
    resultado = analisar_colunas_espn(url)

    if resultado:
        print(f"\n{'=' * 80}")
        print("LISTA COMPLETA DE COLUNAS POR TIPO DE TABELA:")
        print(f"{'=' * 80}")

        for tabela in resultado["tabelas"]:
            print(f"\n🔸 TABELA {tabela['numero']} - {tabela['tipo']}:")
            for j, coluna in enumerate(tabela['colunas'], 1):
                print(f"  {j:2d}. {coluna}")
