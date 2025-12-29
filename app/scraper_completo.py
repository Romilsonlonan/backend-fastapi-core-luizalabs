import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def scraper_espn_completo(url: str):
    """
    Scraper com separação robusta de nome e número da camisa + visualização completa
    """

    # COLUNAS FIXAS - NUNCA ALTERAR!
    COLUNAS_GOLEIROS = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "D", "GS", "A", "FC", "FS", "CA", "CV"]
    COLUNAS_JOGADORES = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def separar_nome_camisa_robusto(texto):
        """
        Separa nome e número da camisa com múltiplas estratégias
        """
        if not texto or texto.strip() == "":
            return "", "0"

        texto = texto.strip()

        # Estratégia 1: Número no início + espaço + nome
        match = re.match(r'^(\d+)\s+(.+)$', texto)
        if match:
            numero = match.group(1)
            nome = match.group(2).strip()
            return nome, numero

        # Estratégia 2: Número entre parênteses no final
        match = re.match(r'^(.+?)\s*\((\d+)\)$', texto)
        if match:
            nome = match.group(1).strip()
            numero = match.group(2)
            return nome, numero

        # Estratégia 3: Número no final do nome
        match = re.match(r'^(.+?)\s*(\d+)$', texto)
        if match:
            nome = match.group(1).strip()
            numero = match.group(2)
            if len(numero) <= 3 and int(numero) <= 999:
                return nome, numero

        # Se nenhuma estratégia funcionou: nome completo + número 0
        return texto, "0"

    def limpar_valor(valor, tipo="texto"):
        """Limpa valores vazios, '--' e converte para número quando necessário"""
        if not valor or valor.strip() == "" or valor.strip() == "--":
            return "0" if tipo == "numero" else ""

        valor_limpo = valor.strip()

        if tipo == "numero":
            numeros = re.findall(r'\d+\.?\d*', valor_limpo)
            return numeros[0] if numeros else "0"

        return valor_limpo

    print(f"🌐 Acessando: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        tabelas = soup.find_all('table')

        print(f"📊 Encontradas {len(tabelas)} tabelas")

        goleiros = []
        jogadores = []

        for i, tabela in enumerate(tabelas):
            # Pega cabeçalho
            cabecalho = [th.text.strip() for th in tabela.find_all('th')]
            print(f"\n🔍 Tabela {i + 1}: {len(cabecalho)} colunas")

            # Pega dados
            dados = []
            for tr in tabela.find_all('tr')[1:]:  # Pula cabeçalho
                colunas = [td.text.strip() for td in tr.find_all('td')]
                if colunas and len(colunas) >= 5:  # Mínimo de colunas
                    dados.append(colunas)

            if not dados:
                continue

            # Identifica tipo
            num_cols = len(dados[0])
            cabecalho_str = " ".join(cabecalho).upper()

            if num_cols <= 14 or "D" in cabecalho_str or "GS" in cabecalho_str:
                tipo = "goleiro"
                colunas_destino = COLUNAS_GOLEIROS
                print(f"  ✅ Identificado como: GOLEIRO ({num_cols} colunas)")
            else:
                tipo = "jogador"
                colunas_destino = COLUNAS_JOGADORES
                print(f"  ✅ Identificado como: JOGADOR DE CAMPO ({num_cols} colunas)")

            # Processa cada linha
            for linha in dados:
                try:
                    # SEPARAÇÃO: nome e número da camisa
                    nome, camisa = separar_nome_camisa_robusto(linha[0])

                    # Nova linha
                    nova_linha = [nome, camisa]

                    # Processa demais colunas
                    for j, valor in enumerate(linha[1:], 1):
                        if j >= len(colunas_destino) - 2:
                            break

                        nome_coluna = colunas_destino[j + 1]

                        if nome_coluna in ["IDADE", "J", "SUB", "D", "GS", "A", "TC", "CG", "FC", "FS", "CA", "CV", "G"]:
                            valor_proc = limpar_valor(valor, "numero")
                        else:
                            valor_proc = limpar_valor(valor, "texto")

                        nova_linha.append(valor_proc)

                    # Completa colunas faltantes
                    while len(nova_linha) < len(colunas_destino):
                        col_faltante = colunas_destino[len(nova_linha)]
                        if col_faltante in ["IDADE", "J", "SUB", "D", "GS", "A", "TC", "CG", "FC", "FS", "CA", "CV", "G"]:
                            nova_linha.append("0")
                        else:
                            nova_linha.append("")

                    # Ajusta tamanho final
                    nova_linha = nova_linha[:len(colunas_destino)]

                    # Adiciona
                    if tipo == "goleiro":
                        goleiros.append(nova_linha)
                    else:
                        jogadores.append(nova_linha)

                except Exception as e:
                    print(f"⚠️  Erro linha: {e}")
                    continue

        # Cria DataFrames
        df_goleiros = pd.DataFrame(goleiros, columns=COLUNAS_GOLEIROS) if goleiros else pd.DataFrame(columns=COLUNAS_GOLEIROS)
        df_jogadores = pd.DataFrame(jogadores, columns=COLUNAS_JOGADORES) if jogadores else pd.DataFrame(columns=COLUNAS_JOGADORES)

        print(f"\n✅ GOLEIROS: {len(df_goleiros)} registros")
        print(f"✅ JOGADORES: {len(df_jogadores)} registros")

        # VISUALIZAÇÃO COMPLETA DE TODAS AS COLUNAS
        pd.set_option('display.max_columns', None)  # Mostra todas as colunas
        pd.set_option('display.width', None)        # Largura automática
        pd.set_option('display.max_colwidth', 20)   # Limita largura de cada coluna

        print("\n📊 VISUALIZAÇÃO COMPLETA DOS DADOS:")

        if not df_goleiros.empty:
            print(f"\n🔸 GOLEIROS COMPLETOS ({len(df_goleiros)} registros):")
            print(df_goleiros.to_string(index=False))

            print("\n🔸 Estatísticas dos goleiros:")
            print(f"   - Total: {len(df_goleiros)} jogadores")
            print(f"   - Posições únicas: {df_goleiros['POS'].unique()}")
            print(f"   - Nacionalidades únicas: {df_goleiros['NAC'].unique()}")

        if not df_jogadores.empty:
            print(f"\n🔸 JOGADORES DE CAMPO COMPLETOS ({len(df_jogadores)} registros):")
            print(df_jogadores.to_string(index=False))

            print("\n🔸 Estatísticas dos jogadores:")
            print(f"   - Total: {len(df_jogadores)} jogadores")
            print(f"   - Posições únicas: {df_jogadores['POS'].unique()}")
            print(f"   - Nacionalidades únicas: {df_jogadores['NAC'].unique()}")

        return {
            "goleiros": df_goleiros,
            "jogadores": df_jogadores
        }

    except Exception as e:
        print(f"❌ Erro: {e}")
        return {
            "goleiros": pd.DataFrame(columns=COLUNAS_GOLEIROS),
            "jogadores": pd.DataFrame(columns=COLUNAS_JOGADORES)
        }


# Teste
if __name__ == "__main__":
    url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/liga/BRA.1/temporada/2025"
    resultados = scraper_espn_completo(url)

    # Salva resultados
    if not resultados["goleiros"].empty:
        resultados["goleiros"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/goleiros_completo.csv', index=False, encoding='utf-8-sig')
        print("\n💾 Goleiros salvos em: goleiros_completo.csv")

    if not resultados["jogadores"].empty:
        resultados["jogadores"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/jogadores_completo.csv', index=False, encoding='utf-8-sig')
        print("\n💾 Jogadores salvos em: jogadores_completo.csv")
