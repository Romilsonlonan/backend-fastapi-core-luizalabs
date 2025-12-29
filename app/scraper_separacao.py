import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def scraper_espn_separacao(url: str):
    """
    Scraper com separação robusta de nome e número da camisa
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

        print(f"  📋 Processando: '{texto}'")

        # Estratégia 1: Número no início + espaço + nome
        # Ex: "10 Philippe Coutinho"
        match = re.match(r'^(\d+)\s+(.+)$', texto)
        if match:
            numero = match.group(1)
            nome = match.group(2).strip()
            print(f"    ✅ Estratégia 1: Número '{numero}' + Nome '{nome}'")
            return nome, numero

        # Estratégia 2: Número entre parênteses no final
        # Ex: "Philippe Coutinho (10)"
        match = re.match(r'^(.+?)\s*\((\d+)\)$', texto)
        if match:
            nome = match.group(1).strip()
            numero = match.group(2)
            print(f"    ✅ Estratégia 2: Nome '{nome}' + Número '{numero}'")
            return nome, numero

        # Estratégia 3: Número no final do nome (sem espaço ou com espaço)
        # Ex: "Philippe Coutinho10" ou "Philippe Coutinho 10"
        match = re.match(r'^(.+?)\s*(\d+)$', texto)
        if match:
            nome = match.group(1).strip()
            numero = match.group(2)
            # Valida que o número não é muito grande (números de camisa normais)
            if len(numero) <= 3 and int(numero) <= 999:
                print(f"    ✅ Estratégia 3: Nome '{nome}' + Número '{numero}'")
                return nome, numero

        # Estratégia 4: Número com hashtag ou outro separador
        # Ex: "Philippe Coutinho #10"
        match = re.match(r'^(.+?)\s*#(\d+)$', texto)
        if match:
            nome = match.group(1).strip()
            numero = match.group(2)
            print(f"    ✅ Estratégia 4: Nome '{nome}' + Número '{numero}'")
            return nome, numero

        # Se nenhuma estratégia funcionou: nome completo + número 0
        print("    ⚠️  Nenhum número encontrado, usando '0'")
        return texto, "0"

    def limpar_valor(valor, tipo="texto"):
        """Limpa valores vazios, '--' e converte para número quando necessário"""
        if not valor or valor.strip() == "" or valor.strip() == "--":
            return "0" if tipo == "numero" else ""

        valor_limpo = valor.strip()

        if tipo == "numero":
            # Extrai números de strings como "1.83 m" ou "82 kg"
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

            # Identifica tipo pela quantidade de colunas e conteúdo
            num_cols = len(dados[0])
            cabecalho_str = " ".join(cabecalho).upper()

            # Decide se é goleiro ou jogador de campo
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
                    # SEPARAÇÃO ROBUSTA: nome e número da camisa
                    nome, camisa = separar_nome_camisa_robusto(linha[0])

                    # Nova linha começa com nome e camisa
                    nova_linha = [nome, camisa]

                    # Processa demais colunas
                    for j, valor in enumerate(linha[1:], 1):
                        if j >= len(colunas_destino) - 2:  # -2: nome e camisa já processados
                            break

                        # Determina tipo de dado pela coluna
                        nome_coluna = colunas_destino[j + 1]  # +1: pulamos primeira coluna original

                        # Colunas numéricas
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

                    # Adiciona à lista correta
                    if tipo == "goleiro":
                        goleiros.append(nova_linha)
                    else:
                        jogadores.append(nova_linha)

                except Exception as e:
                    print(f"⚠️  Erro linha: {e}")
                    continue

        # Cria DataFrames finais
        df_goleiros = pd.DataFrame(goleiros, columns=COLUNAS_GOLEIROS) if goleiros else pd.DataFrame(columns=COLUNAS_GOLEIROS)
        df_jogadores = pd.DataFrame(jogadores, columns=COLUNAS_JOGADORES) if jogadores else pd.DataFrame(columns=COLUNAS_JOGADORES)

        print(f"\n✅ GOLEIROS: {len(df_goleiros)} registros")
        print(f"✅ JOGADORES: {len(df_jogadores)} registros")

        # Mostra exemplos de separação
        print("\n📊 EXEMPLOS DE SEPARAÇÃO:")
        if not df_goleiros.empty:
            print("🔸 GOLEIROS:")
            for i, row in df_goleiros.head(5).iterrows():
                print(f"   '{row['NOME']}' -> Camisa: {row['C']}")

        if not df_jogadores.empty:
            print("🔸 JOGADORES:")
            for i, row in df_jogadores.head(5).iterrows():
                print(f"   '{row['NOME']}' -> Camisa: {row['C']}")

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
    resultados = scraper_espn_separacao(url)

    # Salva resultados
    if not resultados["goleiros"].empty:
        resultados["goleiros"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/goleiros_separacao.csv', index=False, encoding='utf-8-sig')
        print("\n🔸 GOLEIROS SALVOS:")
        print(resultados["goleiros"][["NOME", "C", "POS", "IDADE"]].head())

    if not resultados["jogadores"].empty:
        resultados["jogadores"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/jogadores_separacao.csv', index=False, encoding='utf-8-sig')
        print("\n🔸 JOGADORES SALVOS:")
        print(resultados["jogadores"][["NOME", "C", "POS", "IDADE"]].head())
