import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile
from ...core.exceptions import InfrastructureException, DomainException

class FileService:
    """
    Serviço centralizado para operações de arquivo.
    """
    def __init__(self, upload_dir: str = "uploaded_images"):
        self.upload_dir = upload_dir
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def save_image(self, file: UploadFile, prefix: str) -> str:
        if not file.content_type.startswith("image/"):
            raise DomainException(f"Apenas imagens são permitidas para o {prefix}.")
        
        if file.size > 5 * 1024 * 1024:
            raise DomainException(f"Imagem do {prefix} muito grande (máximo 5MB).")

        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{prefix}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, file_name)

        try:
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            return f"/{self.upload_dir}/{file_name}"
        except Exception as e:
            raise InfrastructureException(f"Erro ao salvar arquivo: {str(e)}")

    def delete_file(self, file_path: str):
        # Remove leading slash if present
        actual_path = file_path.lstrip("/")
        if os.path.exists(actual_path):
            os.remove(actual_path)
