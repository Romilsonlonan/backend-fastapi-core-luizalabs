from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...dependencies import get_db
from ...core.container import DIContainer
from ... import schemas
from .service import ScraperService
from ..clubs.service import ClubService

# Mantendo o prefixo esperado pelo frontend
router = APIRouter(prefix="/api/scraper", tags=["Scraper"])

def get_scraper_service(db: Session = Depends(get_db)) -> ScraperService:
    return DIContainer.get_scraper_service(db)

def get_club_service(db: Session = Depends(get_db)) -> ClubService:
    return DIContainer.get_club_service(db)

@router.post("/scrape-athletes/{club_id}")
async def scrape_athletes_legacy_path(
    club_id: int,
    url: str,
    scraper_service: ScraperService = Depends(get_scraper_service),
):
    """
    Endpoint para compatibilidade com o caminho legado /scrape-athletes/{club_id}
    """
    return await scraper_service.scrape_club_players(url, club_id)

@router.post("/clubs/{club_id}/scrape_players")
async def scrape_players(
    club_id: int,
    scraper_service: ScraperService = Depends(get_scraper_service),
    club_service: ClubService = Depends(get_club_service),
):
    club = club_service.get_club_by_id(club_id)
    if not club.espn_url:
        raise HTTPException(status_code=400, detail="URL da ESPN não configurada para este clube.")

    try:
        return await scraper_service.scrape_club_players(club.espn_url, club_id)
    except Exception as e:
        if "conexão" in str(e).lower() or "dns" in str(e).lower():
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Erro no scraping: {str(e)}")

@router.post("/brasileirao-leaderboard")
async def scrape_brasileirao_leaderboard(
    db: Session = Depends(get_db)
):
    """
    Endpoint para raspar a classificação do Brasileirão.
    Restaurado usando a lógica original para garantir funcionamento imediato.
    """
    from ...scraper_api import scrape_brasileirao_leaderboard as legacy_scrape
    return await legacy_scrape(db)
