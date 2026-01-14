from typing import Optional
from fastapi import UploadFile
from .interfaces import IClubRepository
from .domain import ClubDomain
from ..common.file_service import FileService
from ... import schemas
from ...core.exceptions import NotFoundException, InfrastructureException

class ClubService:
    """
    Camada de Services: Orquestra a lógica de negócio, 
    chamando o Domain e o Repository.
    """
    def __init__(self, repository: IClubRepository, file_service: FileService):
        self.repository = repository
        self.file_service = file_service
        self.domain = ClubDomain()

    async def create_club(
        self, 
        club_schema: schemas.ClubCreate, 
        shield_file: Optional[UploadFile] = None, 
        banner_file: Optional[UploadFile] = None
    ):
        club_data = club_schema.model_dump()
        self.domain.validate_club_data(club_data)

        shield_url = await self.file_service.save_image(shield_file, "shield") if shield_file else None
        banner_url = await self.file_service.save_image(banner_file, "banner") if banner_file else None

        club_data["initials"] = self.domain.format_initials(club_schema.initials)
        club_data["shield_image_url"] = shield_url
        club_data["banner_image_url"] = banner_url

        return self.repository.create(club_data)

    def get_clubs(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)

    def get_club_by_id(self, club_id: int, with_players: bool = False):
        if with_players:
            club = self.repository.get_with_players(club_id)
        else:
            club = self.repository.get_by_id(club_id)
        
        if not club:
            raise NotFoundException("Clube não encontrado")
        return club

    async def update_club(
        self, 
        club_id: int, 
        club_update: schemas.ClubCreate, 
        shield_file: Optional[UploadFile] = None, 
        banner_file: Optional[UploadFile] = None
    ):
        db_club = self.get_club_by_id(club_id)
        
        update_data = club_update.model_dump(exclude_unset=True)
        
        if "initials" in update_data:
            update_data["initials"] = self.domain.format_initials(update_data["initials"])

        if shield_file:
            update_data["shield_image_url"] = await self.file_service.save_image(shield_file, "shield")
        
        if banner_file:
            update_data["banner_image_url"] = await self.file_service.save_image(banner_file, "banner")

        return self.repository.update(db_club, update_data)

    def delete_club(self, club_id: int):
        db_club = self.get_club_by_id(club_id)
        # Opcional: deletar arquivos físicos ao deletar o clube
        if db_club.shield_image_url:
            self.file_service.delete_file(db_club.shield_image_url)
        if db_club.banner_image_url:
            self.file_service.delete_file(db_club.banner_image_url)
            
        return self.repository.delete(db_club)
