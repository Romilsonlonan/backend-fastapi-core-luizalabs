from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup


from .database import get_db
from .models import Goalkeeper, FieldPlayer, Club
from .scraper_altura_peso import scraper_espn_altura_peso

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


def processar_dados_atletas(df: pd.DataFrame, clube_id: int, tipo: str) -> List[Dict[str, Any]]:
    """
    Processa DataFrame e converte para lista de dicionários de atletas
    """
    atletas_processados = []

    for _, row in df.iterrows():
        common_data = {
            "name": str(row.get("NOME", "")).strip(),
            "jersey_number": int(row.get("C", "0") or "0"),
            "position": str(row.get("POS", "")).strip(),
            "age": int(row.get("IDADE", "0") or "0"),
            "height": float(row.get("ALT", "0") or "0"),
            "weight": float(row.get("P", "0") or "0"),
            "nationality": str(row.get("NAC", "")).strip(),
            "games": int(row.get("J", "0") or "0"),
            "substitutions": int(row.get("SUB", "0") or "0"),
            "club_id": clube_id,
            "fouls_committed": int(row.get("FC", "0") or "0"),
            "fouls_suffered": int(row.get("FS", "0") or "0"),
            "yellow_cards": int(row.get("CA", "0") or "0"),
            "red_cards": int(row.get("CV", "0") or "0"),
            "assists": int(row.get("A", "0") or "0"),
        }

        if tipo == "goleiro":
            atleta_data = {
                **common_data,
                "saves": int(row.get("D", "0") or "0"),
                "goals_conceded": int(row.get("GS", "0") or "0"),
            }
        else:  # jogador de campo
            atleta_data = {
                **common_data,
                "goals": int(row.get("G", "0") or "0"),
                "total_shots": int(row.get("TC", "0") or "0"),
                "shots_on_goal": int(row.get("CG", "0") or "0"),
            }
        atletas_processados.append(atleta_data)

    return atletas_processados


@router.post("/atualizar-atletas/{clube_id}")
async def atualizar_atletas(clube_id: int, db: Session = Depends(get_db)):
    """
    Atualiza dados dos atletas de um clube específico usando web scraping
    """
    try:
        # Verifica se o clube existe
        clube = db.query(Club).filter(Club.id == clube_id).first()
        if not clube:
            raise HTTPException(status_code=404, detail="Clube não encontrado")

        if not clube.espn_url:
            raise HTTPException(status_code=400, detail="URL ESPN não configurada para este clube")

        print(f"🔄 Atualizando atletas do {clube.name}...")

        # Executa o scraper
        resultados = scraper_espn_altura_peso(clube.espn_url)

        goleiros_df = resultados["goleiros"]
        jogadores_df = resultados["jogadores"]

        print(f"📊 Goleiros encontrados: {len(goleiros_df)}")
        print(f"📊 Jogadores encontrados: {len(jogadores_df)}")

        # Remove atletas antigos do clube
        db.query(Goalkeeper).filter(Goalkeeper.club_id == clube_id).delete()
        db.query(FieldPlayer).filter(FieldPlayer.club_id == clube_id).delete()

        # Processa e insere novos atletas
        all_atletas_processados = []

        if not goleiros_df.empty:
            goleiros_data = processar_dados_atletas(goleiros_df, clube_id, "goleiro")
            for atleta_data in goleiros_data:
                goalkeeper = Goalkeeper(**atleta_data)
                db.add(goalkeeper)
                all_atletas_processados.append(atleta_data)

        if not jogadores_df.empty:
            jogadores_data = processar_dados_atletas(jogadores_df, clube_id, "jogador")
            for atleta_data in jogadores_data:
                field_player = FieldPlayer(**atleta_data)
                db.add(field_player)
                all_atletas_processados.append(atleta_data)

        # Commit das mudanças
        db.commit()

        print(f"✅ Atualização concluída: {len(all_atletas_processados)} atletas processados")

        return {
            "message": "Atletas atualizados com sucesso",
            "clube": clube.name,
            "total_atletas": len(all_atletas_processados),
            "goleiros": len(goleiros_df),
            "jogadores_campo": len(jogadores_df),
            "data_atualizacao": datetime.now().isoformat()
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar atletas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar atletas: {str(e)}")


@router.get("/status/{clube_id}")
async def verificar_status_atualizacao(clube_id: int, db: Session = Depends(get_db)):
    """
    Verifica status da última atualização de atletas de um clube
    """
    try:
        total_goalkeepers = db.query(Goalkeeper).filter(Goalkeeper.club_id == clube_id).count()
        total_field_players = db.query(FieldPlayer).filter(FieldPlayer.club_id == clube_id).count()
        total_atletas = total_goalkeepers + total_field_players

        # Pega a data mais recente de atualização entre goleiros e jogadores de campo
        latest_goalkeeper = db.query(Goalkeeper).filter(
            Goalkeeper.club_id == clube_id
        ).order_by(Goalkeeper.updated_at.desc()).first() # Assuming 'updated_at' field exists

        latest_field_player = db.query(FieldPlayer).filter(
            FieldPlayer.club_id == clube_id
        ).order_by(FieldPlayer.updated_at.desc()).first() # Assuming 'updated_at' field exists

        data_ultima_atualizacao = None
        if latest_goalkeeper and latest_field_player:
            data_ultima_atualizacao = max(latest_goalkeeper.updated_at, latest_field_player.updated_at).isoformat()
        elif latest_goalkeeper:
            data_ultima_atualizacao = latest_goalkeeper.updated_at.isoformat()
        elif latest_field_player:
            data_ultima_atualizacao = latest_field_player.updated_at.isoformat()

        clube = db.query(Club).filter(Club.id == clube_id).first()

        if not clube:
            raise HTTPException(status_code=404, detail="Clube não encontrado")

        return {
            "clube": clube.name,
            "total_atletas": total_atletas,
            "data_ultima_atualizacao": data_ultima_atualizacao,
            "possui_url_espn": bool(clube.espn_url)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")


@router.get("/atletas/{clube_id}")
async def listar_atletas_por_clube(clube_id: int, db: Session = Depends(get_db)):
    """
    Lista todos os atletas de um clube específico
    """
    try:
        goleiros = db.query(Goalkeeper).filter(Goalkeeper.club_id == clube_id).all()
        jogadores = db.query(FieldPlayer).filter(FieldPlayer.club_id == clube_id).all()

        # Ordena por número da camisa
        goleiros.sort(key=lambda x: x.jersey_number if x.jersey_number is not None else float('inf'))
        jogadores.sort(key=lambda x: x.jersey_number if x.jersey_number is not None else float('inf'))

        return {
            "goleiros": goleiros,
            "jogadores_campo": jogadores,
            "total": len(goleiros) + len(jogadores)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar atletas: {str(e)}")


@router.post("/brasileirao-leaderboard")
async def scrape_brasileirao_leaderboard(db: Session = Depends(get_db)):
    """
    Faz scraping da classificação do Brasileirão na ESPN
    """
    try:
        print("🔄 Iniciando scraping da classificação do Brasileirão...")
        
        # URL da tabela de classificação do Brasileirão na ESPN
        url = "https://www.espn.com.br/futebol/classificacao/_/liga/bra.1/temporada/2025"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # A ESPN usa duas tabelas separadas: uma para os nomes e outra para as estatísticas
        # Usando seletores mais flexíveis para encontrar as tabelas
        tabela_nomes = soup.select_one('div.Table__Scroller--fixed table')
        tabela_stats = soup.select_one('div.Table__Scroller table')
        
        if not tabela_nomes or not tabela_stats:
            # Fallback para seletores genéricos se os específicos falharem
            tabelas = soup.find_all('table', class_=lambda x: x and 'Table' in x)
            if len(tabelas) >= 2:
                tabela_nomes = tabelas[0]
                tabela_stats = tabelas[1]

        if not tabela_nomes or not tabela_stats:
            print(f"❌ Tabelas não encontradas. Nomes: {bool(tabela_nomes)}, Stats: {bool(tabela_stats)}")
            raise HTTPException(status_code=404, detail="Tabelas de classificação não encontradas na página da ESPN")
        
        # Extrai as linhas de ambas as tabelas
        linhas_nomes = tabela_nomes.select('tbody tr')
        linhas_stats = tabela_stats.select('tbody tr')
        
        print(f"📊 Linhas encontradas - Nomes: {len(linhas_nomes)}, Stats: {len(linhas_stats)}")
        
        classificacao = []
        
        # Itera sobre as linhas (geralmente 20 times no Brasileirão)
        for i in range(min(len(linhas_nomes), len(linhas_stats))):
            col_nome = linhas_nomes[i].find_all('td')
            col_stat = linhas_stats[i].find_all('td')
            
            if len(col_nome) >= 1 and len(col_stat) >= 8:
                posicao = i + 1
                
                # Tenta encontrar o nome do clube de forma mais robusta
                # Na ESPN, a estrutura costuma ser: <span class="team-name"> ou <a> dentro da célula
                # O nome completo geralmente está em um span com classe 'hide-mobile'
                nome_element = col_nome[0].select_one('.hide-mobile') or \
                               col_nome[0].select_one('a') or \
                               col_nome[0].select_one('span') or \
                               col_nome[0]
                
                # Pega o texto e remove espaços extras
                clube_nome = nome_element.get_text(strip=True)
                
                # Se o nome vier com a posição (ex: "1Flamengo"), removemos os números do início
                import re
                clube_nome = re.sub(r'^\d+', '', clube_nome).strip()
                
                # Caso especial: se o nome ainda estiver vazio ou for apenas um caractere (sigla)
                # tentamos buscar o atributo 'title' ou 'alt' em imagens/links dentro da célula
                if not clube_nome or len(clube_nome) <= 3:
                    img = col_nome[0].find('img')
                    if img and img.get('title'):
                        clube_nome = img.get('title')
                    elif img and img.get('alt'):
                        clube_nome = img.get('alt')
                
                # Debug para verificar o que está sendo capturado
                if not clube_nome:
                    print(f"⚠️ Nome do clube vazio na posição {posicao}. HTML: {col_nome[0]}")
                
                # Na ESPN, a ordem das colunas de stats é: J, V, E, D, GP, GC, SG, PTS
                try:
                    jogos = int(col_stat[0].get_text(strip=True) or 0)
                    vitorias = int(col_stat[1].get_text(strip=True) or 0)
                    empates = int(col_stat[2].get_text(strip=True) or 0)
                    derrotas = int(col_stat[3].get_text(strip=True) or 0)
                    gp = int(col_stat[4].get_text(strip=True) or 0)
                    gc = int(col_stat[5].get_text(strip=True) or 0)
                    saldo_gols = int(col_stat[6].get_text(strip=True) or 0)
                    pontos = int(col_stat[7].get_text(strip=True) or 0)
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Erro ao converter valores para o time {clube_nome}: {e}")
                    continue
                
                # Busca o clube no banco de dados
                clube = db.query(Club).filter(Club.name.ilike(f"%{clube_nome}%")).first()
                clube_id = clube.id if clube else None
                
                classificacao.append({
                    "posicao": posicao,
                    "clube_nome": clube_nome,
                    "clube_id": clube_id,
                    "pontos": pontos,
                    "jogos": jogos,
                    "vitorias": vitorias,
                    "empates": empates,
                    "derrotas": derrotas,
                    "gols_pro": gp,
                    "gols_contra": gc,
                    "saldo_gols": saldo_gols
                })
        
        print(f"✅ Classificação obtida com sucesso: {len(classificacao)} clubes")
        
        return {
            "message": "Classificação do Brasileirão obtida com sucesso",
            "classificacao": classificacao,
            "data_atualizacao": datetime.now().isoformat(),
            "fonte": "ESPN"
        }
        
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar ESPN: {e}")
        raise HTTPException(status_code=503, detail=f"Erro ao acessar ESPN: {str(e)}")
    except Exception as e:
        print(f"❌ Erro no scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter classificação: {str(e)}")
