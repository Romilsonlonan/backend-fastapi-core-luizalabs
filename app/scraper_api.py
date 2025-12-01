from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Atleta, Clube
from app.scraper_altura_peso import scraper_espn_altura_peso

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


def processar_dados_atletas(df: pd.DataFrame, clube_id: int, tipo: str) -> List[Dict[str, Any]]:
    """
    Processa DataFrame e converte para lista de dicionários de atletas
    """
    atletas = []

    for _, row in df.iterrows():
        atleta = {
            "nome": str(row.get("NOME", "")).strip(),
            "numero_camisa": int(row.get("C", "0") or "0"),
            "posicao": str(row.get("POS", "")).strip(),
            "idade": int(row.get("IDADE", "0") or "0"),
            "altura": float(row.get("ALT", "0") or "0"),
            "peso": int(row.get("P", "0") or "0"),
            "nacionalidade": str(row.get("NAC", "")).strip(),
            "jogos": int(row.get("J", "0") or "0"),
            "substituicoes": int(row.get("SUB", "0") or "0"),
            "clube_id": clube_id,
            "tipo": tipo,  # "goleiro" ou "jogador"
            "data_atualizacao": datetime.now()
        }

        # Adiciona estatísticas específicas por tipo
        if tipo == "goleiro":
            atleta.update({
                "defesas": int(row.get("D", "0") or "0"),
                "gols_sofridos": int(row.get("GS", "0") or "0"),
                "assistencias": int(row.get("A", "0") or "0"),
                "faltas_cometidas": int(row.get("FC", "0") or "0"),
                "faltas_sofridas": int(row.get("FS", "0") or "0"),
                "cartoes_amarelos": int(row.get("CA", "0") or "0"),
                "cartoes_vermelhos": int(row.get("CV", "0") or "0")
            })
        else:  # jogador de campo
            atleta.update({
                "gols": int(row.get("G", "0") or "0"),
                "assistencias": int(row.get("A", "0") or "0"),
                "total_chutes": int(row.get("TC", "0") or "0"),
                "chutes_no_gol": int(row.get("CG", "0") or "0"),
                "faltas_cometidas": int(row.get("FC", "0") or "0"),
                "faltas_sofridas": int(row.get("FS", "0") or "0"),
                "cartoes_amarelos": int(row.get("CA", "0") or "0"),
                "cartoes_vermelhos": int(row.get("CV", "0") or "0")
            })

        atletas.append(atleta)

    return atletas


@router.post("/atualizar-atletas/{clube_id}")
async def atualizar_atletas(clube_id: int, db: Session = Depends(get_db)):
    """
    Atualiza dados dos atletas de um clube específico usando web scraping
    """
    try:
        # Verifica se o clube existe
        clube = db.query(Clube).filter(Clube.id == clube_id).first()
        if not clube:
            raise HTTPException(status_code=404, detail="Clube não encontrado")

        if not clube.espn_url:
            raise HTTPException(status_code=400, detail="URL ESPN não configurada para este clube")

        print(f"🔄 Atualizando atletas do {clube.nome}...")

        # Executa o scraper
        resultados = scraper_espn_altura_peso(clube.espn_url)

        goleiros_df = resultados["goleiros"]
        jogadores_df = resultados["jogadores"]

        print(f"📊 Goleiros encontrados: {len(goleiros_df)}")
        print(f"📊 Jogadores encontrados: {len(jogadores_df)}")

        # Remove atletas antigos do clube
        db.query(Atleta).filter(Atleta.clube_id == clube_id).delete()

        # Processa e insere novos atletas
        atletas_processados = []

        if not goleiros_df.empty:
            goleiros_data = processar_dados_atletas(goleiros_df, clube_id, "goleiro")
            for atleta_data in goleiros_data:
                atleta = Atleta(**atleta_data)
                db.add(atleta)
                atletas_processados.append(atleta_data)

        if not jogadores_df.empty:
            jogadores_data = processar_dados_atletas(jogadores_df, clube_id, "jogador")
            for atleta_data in jogadores_data:
                atleta = Atleta(**atleta_data)
                db.add(atleta)
                atletas_processados.append(atleta_data)

        # Commit das mudanças
        db.commit()

        print(f"✅ Atualização concluída: {len(atletas_processados)} atletas processados")

        return {
            "message": "Atletas atualizados com sucesso",
            "clube": clube.nome,
            "total_atletas": len(atletas_processados),
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
        # Conta atletas por clube
        total_atletas = db.query(Atleta).filter(Atleta.clube_id == clube_id).count()

        # Pega a data mais recente de atualização
        ultimo_atleta = db.query(Atleta).filter(
            Atleta.clube_id == clube_id
        ).order_by(Atleta.data_atualizacao.desc()).first()

        clube = db.query(Clube).filter(Clube.id == clube_id).first()

        if not clube:
            raise HTTPException(status_code=404, detail="Clube não encontrado")

        return {
            "clube": clube.nome,
            "total_atletas": total_atletas,
            "data_ultima_atualizacao": ultimo_atleta.data_atualizacao.isoformat() if ultimo_atleta else None,
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
        atletas = db.query(Atleta).filter(Atleta.clube_id == clube_id).all()

        # Organiza por tipo (goleiros primeiro)
        goleiros = [a for a in atletas if a.tipo == "goleiro"]
        jogadores = [a for a in atletas if a.tipo == "jogador"]

        # Ordena por número da camisa
        goleiros.sort(key=lambda x: x.numero_camisa)
        jogadores.sort(key=lambda x: x.numero_camisa)

        return {
            "goleiros": goleiros,
            "jogadores_campo": jogadores,
            "total": len(atletas)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar atletas: {str(e)}")
