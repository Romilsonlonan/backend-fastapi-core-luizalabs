import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# URL da página
url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/bra.cr_vasco_da_gama"

# Cabeçalho para evitar bloqueio
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Faz a requisição
response = requests.get(url, headers=headers)
response.raise_for_status()

# Faz o parse do HTML
soup = BeautifulSoup(response.text, "html.parser")

# Localiza todas as tabelas
tabelas = soup.find_all("table")

# Define as colunas corretas para cada tipo de tabela - TUDO EM MAIÚSCULO
# Agora com coluna "C" para número da camisa
COLUNAS_GOLEIROS = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "DGS", "AFC", "FS", "CA", "CV"]
COLUNAS_JOGADORES = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"]

def extrair_nome_e_camisa(nome_completo: str) -> tuple:
    """
    Extrai o nome do jogador e o número da camisa.
    Ex: "Léo Jardim1" -> ("Léo Jardim", 1)
        "Gabriel Pec10" -> ("Gabriel Pec", 10)
    """
    if not nome_completo:
        return "", 0

    # Procura por números no final do nome
    match = re.search(r'(\d+)$', nome_completo.strip())

    if match:
        numero = int(match.group(1))
        nome = nome_completo[:match.start()].strip()
        return nome, numero
    else:
        return nome_completo.strip(), 0

goleiros = []
jogadores_campo = []

print(f"📊 ENCONTRADAS {len(tabelas)} TABELAS NA PÁGINA")
print("="*80)

for i, tabela in enumerate(tabelas, 1):
    print(f"\n🔍 ANALISANDO TABELA {i}")

    # Captura o cabeçalho original
    cabecalho_original = [th.text.strip() for th in tabela.find_all("th")]
    print(f"  - Cabeçalho: {cabecalho_original}")

    # Captura todas as linhas de dados
    linhas = []
    for tr in tabela.find_all("tr")[1:]:  # Pula o cabeçalho
        colunas = [td.text.strip() for td in tr.find_all("td")]
        if colunas:  # Só adiciona se tiver dados
            linhas.append(colunas)

    if linhas and cabecalho_original:
        print(f"  - Total de linhas: {len(linhas)}")

        # Mostra primeira linha como exemplo
        print(f"  - Primeira linha: {linhas[0] if linhas else 'Nenhuma'}")

        # Cria DataFrame temporário para analisar
        df_temp = pd.DataFrame(linhas, columns=COLUNAS_JOGADORES[:len(linhas[0])])

        # Verifica se é goleiro pela posição
        if 'POS' in df_temp.columns:
            # Conta quantos goleiros e quantos jogadores de campo
            qtd_goleiros = (df_temp['POS'] == 'G').sum()
            qtd_jogadores = (df_temp['POS'] != 'G').sum()

            print(f"  - Goleiros encontrados: {qtd_goleiros}")
            print(f"  - Jogadores de campo: {qtd_jogadores}")

            if qtd_goleiros > 0:
                # É tabela de goleiros
                print("  ✅ CLASSIFICANDO COMO: TABELA DE GOLEIROS")

                # Processa cada linha para separar nome e camisa
                dados_processados = []
                for linha in linhas:
                    if len(linha) > 0:
                        nome_original = linha[0]
                        nome, camisa = extrair_nome_e_camisa(nome_original)

                        # Cria nova linha com nome separado e número da camisa
                        nova_linha = [nome, camisa] + linha[1:len(COLUNAS_GOLEIROS)-1]
                        dados_processados.append(nova_linha)

                # Cria DataFrame com as colunas corretas
                df_goleiros = pd.DataFrame(dados_processados, columns=COLUNAS_GOLEIROS)
                goleiros.append(df_goleiros)

                print(f"  - GOLEIROS PROCESSADOS: {len(df_goleiros)}")

            if qtd_jogadores > 0:
                # É tabela de jogadores de campo
                print("  ✅ CLASSIFICANDO COMO: TABELA DE JOGADORES DE CAMPO")

                # Processa cada linha para separar nome e camisa
                dados_processados = []
                for linha in linhas:
                    if len(linha) > 0:
                        nome_original = linha[0]
                        nome, camisa = extrair_nome_e_camisa(nome_original)

                        # Cria nova linha com nome separado e número da camisa
                        nova_linha = [nome, camisa] + linha[1:len(COLUNAS_JOGADORES)-1]
                        dados_processados.append(nova_linha)

                # Cria DataFrame com as colunas corretas
                df_jogadores = pd.DataFrame(dados_processados, columns=COLUNAS_JOGADORES)
                jogadores_campo.append(df_jogadores)

                print(f"  - JOGADORES DE CAMPO PROCESSADOS: {len(df_jogadores)}")
        else:
            print("  ❌ Nenhuma coluna 'POS' encontrada - pulando tabela")
    else:
        print("  ❌ Tabela vazia ou sem cabeçalho - pulando")

# Combina goleiros se houver mais de uma tabela
if goleiros:
    df_goleiros_final = pd.concat(goleiros, ignore_index=True) if len(goleiros) > 1 else goleiros[0]
else:
    df_goleiros_final = pd.DataFrame()

# Combina jogadores de campo se houver mais de uma tabela
if jogadores_campo:
    df_jogadores_final = pd.concat(jogadores_campo, ignore_index=True) if len(jogadores_campo) > 1 else jogadores_campo[0]
else:
    df_jogadores_final = pd.DataFrame()

print("\n" + "="*80)
print(f"📋 RESUMO FINAL:")
print(f"TOTAL DE TABELAS PROCESSADAS: {len(tabelas)}")
print(f"TABELAS DE GOLEIROS: {len(goleiros)}")
print(f"TABELAS DE JOGADORES DE CAMPO: {len(jogadores_campo)}")
print(f"TOTAL DE GOLEIROS: {len(df_goleiros_final) if not df_goleiros_final.empty else 0}")
print(f"TOTAL DE JOGADORES DE CAMPO: {len(df_jogadores_final) if not df_jogadores_final.empty else 0}")
print()

# Salva arquivos separados
if not df_goleiros_final.empty:
    print("🥅 GOLEIROS:")
    print(df_goleiros_final.head(10))
    df_goleiros_final.to_csv("goleiros_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'goleiros_vasco_espn.csv' SALVO COM SUCESSO!")
    print()

if not df_jogadores_final.empty:
    print("⚽ JOGADORES DE CAMPO:")
    print(df_jogadores_final.head(10))
    df_jogadores_final.to_csv("jogadores_campo_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'jogadores_campo_vasco_espn.csv' SALVO COM SUCESSO!")

if df_goleiros_final.empty and df_jogadores_final.empty:
    print("❌ NENHUMA TABELA PROCESSADA COM SUCESSO.")
