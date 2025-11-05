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

print(f"📊 ENCONTRADAS {len(tabelas)} TABELAS NA PÁGINA")
print("="*80)

goleiros = []
jogadores_campo = []

for i, tabela in enumerate(tabelas, 1):
    print(f"\n🔍 ANALISANDO TABELA {i}")

    # Captura o cabeçalho original
    cabecalho_original = [th.text.strip() for th in tabela.find_all("th")]
    print(f"  - Cabeçalho: {cabecalho_original}")
    print(f"  - Número de colunas: {len(cabecalho_original)}")

    # Determina o tipo de tabela
    if len(cabecalho_original) <= 14:  # Tabela de goleiros
        print("  ✅ IDENTIFICADA COMO TABELA DE GOLEIROS")
        colunas_tipo = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "D", "GS", "AFC", "FS", "CA", "CV"]
    else:  # Tabela de jogadores de campo
        print("  ✅ IDENTIFICADA COMO TABELA DE JOGADORES DE CAMPO")
        colunas_tipo = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"]

    # Processa as linhas
    linhas = []
    for tr in tabela.find_all("tr")[1:]:  # Pula o cabeçalho
        colunas = [td.text.strip() for td in tr.find_all("td")]
        if colunas:  # Só adiciona se tiver dados
            linhas.append(colunas)

    print(f"  - Total de linhas: {len(linhas)}")

    for linha in linhas:
        if len(linha) > 2:  # Verifica se tem dados suficientes
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

            if posicao == 'G':
                # Processa goleiro
                nova_linha = [nome, numero] + linha[1:]
                goleiros.append(nova_linha)
            elif posicao in ['D', 'M', 'A']:
                # Processa jogador de campo
                nova_linha = [nome, numero] + linha[1:]
                jogadores_campo.append(nova_linha)

print("\n" + "="*80)
print(f"📋 RESUMO FINAL:")
print(f"TOTAL DE GOLEIROS: {len(goleiros)}")
print(f"TOTAL DE JOGADORES DE CAMPO: {len(jogadores_campo)}")

# Cria DataFrames
if goleiros:
    df_goleiros = pd.DataFrame(goleiros, columns=["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "D", "GS", "AFC", "FS", "CA", "CV"])
    print("\n🥅 GOLEIROS:")
    print(df_goleiros.head())
    df_goleiros.to_csv("goleiros_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'goleiros_vasco_espn.csv' SALVO COM SUCESSO!")

if jogadores_campo:
    df_jogadores = pd.DataFrame(jogadores_campo, columns=["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"])
    print("\n⚽ JOGADORES DE CAMPO:")
    print(df_jogadores.head())
    df_jogadores.to_csv("jogadores_campo_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'jogadores_campo_vasco_espn.csv' SALVO COM SUCESSO!")
