import os

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.status import HTTP_200_OK

from app.app import app
from app.config import settings
from app.database import Base, get_db
from app.models import User
from app.security import get_password_hash

load_dotenv(dotenv_path='.secretstest')  # Carrega variáveis do arquivo .secretstest

senha = os.getenv('ADMIN_PASSWORD')

# Carrega variáveis do ambiente (.env)
# load_dotenv()

# Define variáveis globais
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'teste123')

# Cria o banco de teste (SQLite local)
SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas no banco de teste
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Substitui a dependência de banco de dados para usar o SQLite local."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Substitui o get_db padrão pelo de teste
app.dependency_overrides[get_db] = override_get_db

# Cria o cliente de teste
client = TestClient(app)


def setup_admin_user():
    """Garante que o usuário admin exista antes do teste."""
    db = TestingSessionLocal()
    try:
        admin_email = settings.ADMIN_EMAIL
        admin_password = ADMIN_PASSWORD[:72]  # Limita a 72 bytes (bcrypt)

        db_user = db.query(User).filter(User.email == admin_email).first()
        if not db_user:
            hashed_password = get_password_hash(admin_password)
            new_admin = User(email=admin_email, hashed_password=hashed_password)
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
    finally:
        db.close()


def test_admin_login():
    """Testa login do admin e acesso à rota protegida."""
    setup_admin_user()

    response = client.post(
        '/token',
        data={
            'username': settings.ADMIN_EMAIL,
            'password': ADMIN_PASSWORD,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

    # Testa acesso à rota protegida
    headers = {'Authorization': f'Bearer {data["access_token"]}'}
    response = client.get('/users/me/', headers=headers)
    HTTP_200_OK
