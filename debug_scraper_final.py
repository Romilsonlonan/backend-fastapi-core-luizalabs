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

def processar_tabela(tabela, cabecalho_original):
    """Processa uma tabela e retorna goleiros e jogadores de campo separados"""
    # Captura todas as linhas de dados
    linhas = []
    for tr in tabela.find_all("tr")[1:]:  # Pula o cabeçalho
        colunas = [td.text.strip() for td in tr.find_all("td")]
        if colunas:  # Só adiciona se tiver dados
            linhas.append(colunas)

    if not linhas or not cabecalho_original:
        return [], []

    # Determina as colunas baseado no cabeçalho
    if len(cabecalho_original) <= 10:  # Tabela de goleiros tem menos colunas
        colunas_tipo = COLUNAS_GOLEIROS
    else:  # Tabela de jogadores de campo
        colunas_tipo = COLUNAS_JOGADORES

    # Separa goleiros e jogadores de campo
    goleiros_linhas = []
    jogadores_campo_linhas = []

    for linha in linhas:
        if len(linha) > 1:  # Verifica se tem dados suficientes
            # Procura pela posição na linha
            pos_encontrada = None
            for i, valor in enumerate(linha):
                if valor == 'G':
                    pos_encontrada = 'G'
                    break
                elif valor in ['D', 'M', 'A']:
                    pos_encontrada = 'CAMPO'
                    break

            # Processa a linha para separar nome e camisa
            if len(linha) > 0:
                nome_original = linha[0]
                nome, camisa = extrair_nome_e_camisa(nome_original)

                if pos_encontrada == 'G':
                    # É goleiro - usa colunas de goleiros
                    nova_linha = [nome, camisa] + linha[1:len(COLUNAS_GOLEIROS)-1]
                    goleiros_linhas.append(nova_linha)
                elif pos_encontrada == 'CAMPO':
                    # É jogador de campo - usa colunas de jogadores
                    nova_linha = [nome, camisa] + linha[1:len(COLUNAS_JOGADORES)-1]
                    jogadores_campo_linhas.append(nova_linha)

    return goleiros_linhas, jogadores_campo_linhas

# Processa todas as tabelas
todos_goleiros = []
todos_jogadores_campo = []

print(f"📊 ENCONTRADAS {len(tabelas)} TABELAS NA PÁGINA")
print("="*80)

for i, tabela in enumerate(tabelas, 1):
    print(f"\n🔍 ANALISANDO TABELA {i}")

    # Captura o cabeçalho original
    cabecalho_original = [th.text.strip() for th in tabela.find_all("th")]
    print(f"  - Cabeçalho: {cabecalho_original}")

    # Processa a tabela
    goleiros_tabela, jogadores_campo_tabela = processar_tabela(tabela, cabecalho_original)

    print(f"  - Goleiros encontrados: {len(goleiros_tabela)}")
    print(f"  - Jogadores de campo: {len(jogadores_campo_tabela)}")

    if goleiros_tabela:
        todos_goleiros.extend(goleiros_tabela)
        print(f"  ✅ ADICIONADOS {len(goleiros_tabela)} GOLEIROS")

    if jogadores_campo_tabela:
        todos_jogadores_campo.extend(jogadores_campo_tabela)
        print(f"  ✅ ADICIONADOS {len(jogadores_campo_tabela)} JOGADORES DE CAMPO")

# Cria DataFrames finais
if todos_goleiros:
    df_goleiros_final = pd.DataFrame(todos_goleiros, columns=COLUNAS_GOLEIROS)
else:
    df_goleiros_final = pd.DataFrame()

if todos_jogadores_campo:
    df_jogadores_final = pd.DataFrame(todos_jogadores_campo, columns=COLUNAS_JOGADORES)
else:
    df_jogadores_final = pd.DataFrame()

print("\n" + "="*80)
print(f"📋 RESUMO FINAL:")
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
