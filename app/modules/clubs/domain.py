import os
import uuid
from typing import Tuple
from fastapi import HTTPException, UploadFile

class ClubDomain:
    """
    Camada de Domain Rules: Contém a lógica pura do domínio, 
    independente de frameworks ou banco de dados.
    """
    
    @staticmethod
    def validate_image(file: UploadFile, context: str) -> None:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Apenas imagens são permitidas para o {context}.")
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Imagem do {context} muito grande (máximo 5MB).")

    @staticmethod
    def generate_file_path(file: UploadFile, prefix: str) -> Tuple[str, str]:
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{prefix}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploaded_images", file_name)
        return file_path, file_name

    @staticmethod
    def format_initials(initials: str) -> str:
        return initials.upper()[:3]
