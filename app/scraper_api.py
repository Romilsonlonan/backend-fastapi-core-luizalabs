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
        url = "https://www.espn.com.br/futebol/classificacao/_/liga/BRA.1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontra a tabela de classificação
        tabela = soup.find('table', {'class': 'Table'})
        if not tabela:
            raise HTTPException(status_code=404, detail="Tabela de classificação não encontrada")
        
        # Extrai os dados da tabela
        linhas = tabela.find('tbody').find_all('tr')
        classificacao = []
        
        for i, linha in enumerate(linhas[:20]):  # Top 20 clubes
            colunas = linha.find_all('td')
            if len(colunas) >= 8:
                posicao = i + 1
                clube_nome = colunas[1].get_text(strip=True)
                pontos = int(colunas[2].get_text(strip=True))
                jogos = int(colunas[3].get_text(strip=True))
                vitorias = int(colunas[4].get_text(strip=True))
                empates = int(colunas[5].get_text(strip=True))
                derrotas = int(colunas[6].get_text(strip=True))
                saldo_gols = int(colunas[7].get_text(strip=True))
                
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