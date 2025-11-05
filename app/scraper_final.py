import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from typing import List, Dict, Any, Optional

class ESPNScraperFinal:
    """
    Scraper robusto da ESPN com colunas fixas e tratamento de dados faltantes
    """

    # COLUNAS FIXAS - NUNCA MUDAR!
    COLUNAS_GOLEIROS = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "D", "GS", "A", "FC", "FS", "CA", "CV"]
    COLUNAS_JOGADORES = ["NOME", "C", "POS", "IDADE", "ALT", "P", "NAC", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"]

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def limpar_valor(self, valor: str, tipo: str = "texto") -> str:
        """
        Limpa e trata valores faltantes ou inválidos
        """
        if not valor or valor.strip() == "" or valor.strip() == "--":
            if tipo == "numero":
                return "0"
            return "0"

        valor_limpo = valor.strip()

        # Para valores numéricos, remove textos e mantém apenas números
        if tipo == "numero":
            # Extrai apenas números de strings como "1.83 m" ou "82 kg"
            numeros = re.findall(r'\d+\.?\d*', valor_limpo)
            if numeros:
                return numeros[0]  # Retorna o primeiro número encontrado
            else:
                return "0"

        return valor_limpo

    def separar_nome_camisa(self, texto: str) -> tuple:
        """
        Separa nome e número da camisa, tratando casos onde não há número
        """
        if not texto or texto.strip() == "":
            return "", "0"

        # Remove espaços extras
        texto = texto.strip()

        # Procura por padrão: número seguido de nome (ex: "10 Philippe Coutinho")
        match = re.match(r'^(\d+)\s+(.+)$', texto)
        if match:
            camisa = match.group(1)
            nome = match.group(2).strip()
            return nome, camisa

        # Procura por padrão: nome seguido de número entre parênteses (ex: "Philippe Coutinho (10)")
        match = re.match(r'^(.+?)\s*\((\d+)\)$', texto)
        if match:
            nome = match.group(1).strip()
            camisa = match.group(2)
            return nome, camisa

        # Se não encontrar número, retorna nome completo e camisa "0"
        return texto, "0"

    def processar_dados_tabela(self, linhas: List[List[str]], tipo_tabela: str) -> List[List[str]]:
        """
        Processa os dados da tabela aplicando todas as regras de tratamento
        """
        dados_processados = []

        # Define as colunas esperadas baseado no tipo
        if tipo_tabela == "goleiros":
            colunas_esperadas = self.COLUNAS_GOLEIROS
        else:
            colunas_esperadas = self.COLUNAS_JOGADORES

        print(f"📊 Processando {len(linhas)} linhas para tabela de {tipo_tabela}")

        for i, linha in enumerate(linhas):
            if not linha or len(linha) == 0:
                continue

            try:
                # Separa nome e camisa da primeira coluna
                nome, camisa = self.separar_nome_camisa(linha[0])

                # Inicia a nova linha com nome e camisa
                nova_linha = [nome, camisa]

                # Processa as demais colunas
                for j, valor in enumerate(linha[1:], 1):
                    if j >= len(colunas_esperadas) - 2:  # -2 porque já processamos nome e camisa
                        break

                    # Determina o tipo de dado baseado no nome da coluna
                    coluna_nome = colunas_esperadas[j + 1]  # +1 porque pulamos a primeira coluna original

                    # Colunas numéricas
                    if coluna_nome in ["IDADE", "J", "SUB", "D", "GS", "A", "TC", "CG", "FC", "FS", "CA", "CV"]:
                        valor_processado = self.limpar_valor(valor, "numero")
                    else:
                        valor_processado = self.limpar_valor(valor, "texto")

                    nova_linha.append(valor_processado)

                # Preenche colunas faltantes com valores padrão
                while len(nova_linha) < len(colunas_esperadas):
                    coluna_faltante = colunas_esperadas[len(nova_linha)]
                    if coluna_faltante in ["IDADE", "J", "SUB", "D", "GS", "A", "TC", "CG", "FC", "FS", "CA", "CV"]:
                        nova_linha.append("0")
                    else:
                        nova_linha.append("")

                # Garante que temos exatamente o número certo de colunas
                nova_linha = nova_linha[:len(colunas_esperadas)]

                dados_processados.append(nova_linha)

            except Exception as e:
                print(f"⚠️  Erro ao processar linha {i}: {e}")
                continue

        return dados_processados

    def identificar_tipo_tabela(self, cabecalho: List[str]) -> str:
        """
        Identifica se é tabela de goleiros ou jogadores baseado no cabeçalho
        """
        cabecalho_str = " ".join(cabecalho).upper()

        # Verifica se tem as colunas específicas de goleiros
        if any(col in cabecalho_str for col in ["D", "GS", "DEFESA"]):
            return "goleiros"

        # Verifica se tem as colunas específicas de jogadores de campo
        if any(col in cabecalho_str for col in ["G", "A", "TC", "CG", "GOL"]):
            return "jogadores"

        # Se não conseguir identificar, usa o número de colunas como fallback
        if len(cabecalho) <= 14:
            return "goleiros"
        else:
            return "jogadores"

    def scrape_espn(self, url: str) -> Dict[str, pd.DataFrame]:
        """
        Faz o scraping completo da ESPN
        """
        print(f"🌐 Iniciando scraping da URL: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontra todas as tabelas
            tabelas = soup.find_all('table')
            print(f"📊 Encontradas {len(tabelas)} tabelas")

            resultados = {
                "goleiros": pd.DataFrame(),
                "jogadores": pd.DataFrame()
            }

            for i, tabela in enumerate(tabelas):
                print(f"\n🔍 Analisando tabela {i+1}")

                # Captura o cabeçalho
                cabecalho = [th.text.strip() for th in tabela.find_all('th')]
                print(f"  - Cabeçalho: {cabecalho}")

                # Captura os dados
                linhas = []
                for tr in tabela.find_all('tr')[1:]:  # Pula cabeçalho
                    colunas = [td.text.strip() for td in tr.find_all('td')]
                    if colunas:
                        linhas.append(colunas)

                if not linhas:
                    print("  - Tabela vazia, pulando...")
                    continue

                # Identifica o tipo de tabela
                tipo_tabela = self.identificar_tipo_tabela(cabecalho)
                print(f"  - Tipo identificado: {tipo_tabela}")

                # Processa os dados
                dados_processados = self.processar_dados_tabela(linhas, tipo_tabela)

                if dados_processados:
                    # Cria DataFrame com as colunas fixas
                    if tipo_tabela == "goleiros":
                        df = pd.DataFrame(dados_processados, columns=self.COLUNAS_GOLEIROS)
                        resultados["goleiros"] = pd.concat([resultados["goleiros"], df], ignore_index=True)
                    else:
                        df = pd.DataFrame(dados_processados, columns=self.COLUNAS_JOGADORES)
                        resultados["jogadores"] = pd.concat([resultados["jogadores"], df], ignore_index=True)

                    print(f"  - ✅ Processadas {len(dados_processados)} linhas")
                else:
                    print("  - ❌ Nenhum dado processado")

            return resultados

        except Exception as e:
            print(f"❌ Erro no scraping: {e}")
            return {"goleiros": pd.DataFrame(), "jogadores": pd.DataFrame()}

def testar_scraper():
    """
    Função de teste do scraper
    """
    scraper = ESPNScraperFinal()

    # Testa com o Vasco da Gama
    url = "https://www.espn.com.br/futebol/time/elenco/_/id/3454/ordenar/position/dir/desce/bra.cr_vasco_da_gama"

    resultados = scraper.scrape_espn(url)

    # Salva os resultados
    if not resultados["goleiros"].empty:
        resultados["goleiros"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/goleiros_teste_final.csv', index=False, encoding='utf-8-sig')
        print(f"\n✅ Goleiros salvos: {len(resultados['goleiros'])} registros")
        print("Colunas:", list(resultados["goleiros"].columns))

    if not resultados["jogadores"].empty:
        resultados["jogadores"].to_csv('/home/romilson/Projetos/luizalabs/backend/fastapi_core/jogadores_teste_final.csv', index=False, encoding='utf-8-sig')
        print(f"\n✅ Jogadores salvos: {len(resultados['jogadores'])} registros")
        print("Colunas:", list(resultados["jogadores"].columns))

    # Mostra exemplos
    print("\n📋 EXEMPLOS DE DADOS PROCESSADOS:")

    if not resultados["goleiros"].empty:
        print("\n🔸 GOLEIROS:")
        print(resultados["goleiros"].head(3))

    if not resultados["jogadores"].empty:
        print("\n🔸 JOGADORES DE CAMPO:")
        print(resultados["jogadores"].head(3))

if __name__ == "__main__":
    testar_scraper()
