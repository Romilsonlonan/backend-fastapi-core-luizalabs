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
COLUNAS_GOLEIROS = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "D", "GS", "A", "FC", "FS", "CA", "CV"]
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

for tabela in tabelas:
    # Captura o cabeçalho original
    cabecalho_original = [th.text.strip() for th in tabela.find_all("th")]

    # Captura todas as linhas de dados
    linhas = []
    for tr in tabela.find_all("tr")[1:]:  # Pula o cabeçalho
        colunas = [td.text.strip() for td in tr.find_all("td")]
        if colunas:  # Só adiciona se tiver dados
            linhas.append(colunas)

    if linhas and cabecalho_original:
        # Cria DataFrame temporário para analisar
        df_temp = pd.DataFrame(linhas, columns=COLUNAS_JOGADORES[:len(linhas[0])])

        # Verifica se é goleiro pela posição
        if 'POS' in df_temp.columns:
            tem_goleiro = (df_temp['POS'] == 'G').any()

            if tem_goleiro:
                # É tabela de goleiros
                print("📊 TABELA DE GOLEIROS DETECTADA")

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

                print(f"  - GOLEIROS ENCONTRADOS: {len(df_goleiros)}")
                print(f"  - COLUNAS: {list(df_goleiros.columns)}")

                # Mostra exemplo de processamento
                if len(df_goleiros) > 0:
                    print(f"  - Exemplo: {df_goleiros.iloc[0]['NOME']} (Camisa #{df_goleiros.iloc[0]['C']})")

            else:
                # É tabela de jogadores de campo
                print("📊 TABELA DE JOGADORES DE CAMPO DETECTADA")

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

                print(f"  - JOGADORES DE CAMPO ENCONTRADOS: {len(df_jogadores)}")
                print(f"  - COLUNAS: {list(df_jogadores.columns)}")

                # Mostra exemplo de processamento
                if len(df_jogadores) > 0:
                    print(f"  - Exemplo: {df_jogadores.iloc[0]['NOME']} (Camisa #{df_jogadores.iloc[0]['C']})")
            print()

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

print("="*80)
print(f"📋 RESUMO FINAL:")
print(f"TOTAL DE GOLEIROS: {len(df_goleiros_final) if not df_goleiros_final.empty else 0}")
print(f"TOTAL DE JOGADORES DE CAMPO: {len(df_jogadores_final) if not df_jogadores_final.empty else 0}")
print()

# Salva arquivos separados
if not df_goleiros_final.empty:
    print("GOLEIROS:")
    print(df_goleiros_final.head(10))
    df_goleiros_final.to_csv("goleiros_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'goleiros_vasco_espn.csv' SALVO COM SUCESSO!")
    print()

if not df_jogadores_final.empty:
    print("JOGADORES DE CAMPO:")
    print(df_jogadores_final.head(10))
    df_jogadores_final.to_csv("jogadores_campo_vasco_espn.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ ARQUIVO 'jogadores_campo_vasco_espn.csv' SALVO COM SUCESSO!")

if df_goleiros_final.empty and df_jogadores_final.empty:
    print("❌ NENHUMA TABELA ENCONTRADA OU DADOS EXTRAÍDOS.")
