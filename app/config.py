from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = 'sqlite:///./sql_app.db'
    SECRET_KEY: str = 'sua-chave-secreta-super-segura-aqui'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_EMAIL: str = ''
    ADMIN_PASSWORD: str = ''
    ADMIN_NAME: str = 'Administrador CBF'
    CORS_ORIGINS_RAW: str = 'http://localhost:8000,http://127.0.0.1:8000'


    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(',') if origin.strip()]

    class Config:
        env_file = '.env'


settings = Settings()
