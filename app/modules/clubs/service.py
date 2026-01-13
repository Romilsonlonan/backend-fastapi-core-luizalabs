from typing import Optional
from fastapi import UploadFile
from .interfaces import IClubRepository
from .domain import ClubDomain
from ... import schemas
from ...core.exceptions import NotFoundException, InfrastructureException

class ClubService:
    """
    Camada de Services: Orquestra a lógica de negócio, 
    chamando o Domain e o Repository.
    """
    def __init__(self, repository: IClubRepository):
        self.repository = repository
        self.domain = ClubDomain()

    async def create_club(
        self, 
        club_schema: schemas.ClubCreate, 
        shield_file: Optional[UploadFile] = None, 
        banner_file: Optional[UploadFile] = None
    ):
        shield_url = await self._handle_file_upload(shield_file, "shield")
        banner_url = await self._handle_file_upload(banner_file, "banner")

        club_data = club_schema.model_dump()
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
            update_data["shield_image_url"] = await self._handle_file_upload(shield_file, "shield")
        
        if banner_file:
            update_data["banner_image_url"] = await self._handle_file_upload(banner_file, "banner")

        return self.repository.update(db_club, update_data)

    def delete_club(self, club_id: int):
        db_club = self.get_club_by_id(club_id)
        return self.repository.delete(db_club)

    async def _handle_file_upload(self, file: Optional[UploadFile], prefix: str) -> Optional[str]:
        if not file:
            return None
        
        self.domain.validate_image(file, prefix)
        file_path, file_name = self.domain.generate_file_path(file, prefix)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return f"/uploaded_images/{file_name}"
        except Exception:
            raise InfrastructureException(f"Erro ao salvar imagem do {prefix}.")
