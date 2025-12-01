import os
from datetime import date, timedelta
from typing import Annotated, List, Optional

import requests  # Importar requests separadamente
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    staticfiles,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .config import settings
from .database import SessionLocal, engine
from .security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)

# =====================================================
# 📘 Inicialização do Banco de Dados
# =====================================================
models.Base.metadata.create_all(bind=engine)


# =====================================================
# 🚀 Instanciação da Aplicação FastAPI
# =====================================================
app = FastAPI()


# 🛠️ **Correções Aplicadas:**

# **1. Backend - CORS Melhorado**

# 🌐 Configuração CORS
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# =====================================================
# 🗃️ Dependência de Banco de Dados
# =====================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# 🔐 Configuração de Autenticação (OAuth2)
# =====================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """Retorna o usuário autenticado e ativo."""
    return current_user


# =====================================================
# 📁 Configuração de Upload de Arquivos
# =====================================================
UPLOAD_DIRECTORY = "uploaded_images"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app.mount(
    f"/{UPLOAD_DIRECTORY}",
    staticfiles.StaticFiles(directory=UPLOAD_DIRECTORY),
    name="static",
)


# =====================================================
# ⚽ Rotas de Clubes
# =====================================================
@app.post("/clubs/", response_model=schemas.ClubResponse)
async def create_club(
    name: str = Form(...),
    initials: str = Form(...),
    city: str = Form(...),
    foundation_date: Optional[str] = Form(None),
    br_titles: Optional[int] = Form(0),
    training_center: Optional[str] = Form(None),
    espn_url: Optional[str] = Form(None),  # Adicionado
    shield_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    club_data = schemas.ClubCreate(
        name=name,
        initials=initials,
        city=city,
        foundation_date=date.fromisoformat(foundation_date)
        if foundation_date
        else None,
        br_titles=br_titles,
        training_center=training_center,
        espn_url=espn_url,  # Adicionado
    )
    return crud.create_club(db=db, club=club_data, shield_file=shield_image)


@app.get("/clubs/", response_model=List[schemas.ClubResponse])
def read_clubs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clubs = crud.get_clubs(db, skip=skip, limit=limit)
    return clubs


@app.get("/clubs/{club_id}", response_model=schemas.ClubResponse)
def read_club(club_id: int, db: Session = Depends(get_db)):
    db_club = crud.get_club_with_players(db, club_id=club_id)
    if db_club is None:
        raise HTTPException(status_code=404, detail="Clube não encontrado")
    return db_club


@app.patch("/clubs/{club_id}", response_model=schemas.ClubResponse)
async def update_club(
    club_id: int,
    name: Optional[str] = Form(None),
    initials: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    foundation_date: Optional[str] = Form(None),
    br_titles: Optional[int] = Form(None),
    training_center: Optional[str] = Form(None),
    espn_url: Optional[str] = Form(None),
    shield_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    club_update_data = {
        "name": name,
        "initials": initials,
        "city": city,
        "br_titles": br_titles,
        "training_center": training_center,
        "espn_url": espn_url,
    }

    # Convert foundation_date string to date object if provided
    if foundation_date:
        club_update_data["foundation_date"] = date.fromisoformat(foundation_date)
    else:
        club_update_data["foundation_date"] = None # Explicitly set to None if empty string is sent

    # Filter out None values to allow partial updates
    club_update_data = {k: v for k, v in club_update_data.items() if v is not None}

    # Handle shield_image separately if provided
    shield_url = None
    if shield_image:
        # Validações de segurança (similar ao create_club)
        if not shield_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Apenas imagens são permitidas")
        if shield_image.size > 5 * 1024 * 1024:  # 5MB limite
            raise HTTPException(status_code=400, detail="Imagem muito grande (máximo 5MB)")

        file_ext = os.path.splitext(shield_image.filename)[1]
        file_name = f"shield_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

        try:
            with open(file_path, "wb") as buffer:
                content = await shield_image.read()
                buffer.write(content)
            shield_url = f"/{UPLOAD_DIRECTORY}/{file_name}"
            club_update_data["shield_image_url"] = shield_url
        except Exception:
            raise HTTPException(status_code=500, detail="Erro ao salvar imagem do escudo")
    
    # If shield_image is explicitly sent as an empty string (e.g., to clear it), set URL to None
    # This logic might need refinement based on how the frontend sends "clear image" signal
    # For now, if shield_image is None and no new file is uploaded, existing URL remains
    # If frontend sends a specific signal to clear, we'd handle it here.

    club_update_schema = schemas.ClubCreate(**club_update_data) # Use ClubCreate for validation

    db_club = crud.update_club(db, club_id=club_id, club_update=club_update_schema)
    if db_club is None:
        raise HTTPException(status_code=404, detail="Clube não encontrado")
    return db_club


# =====================================================
# 🕸️ Rotas de Web Scraping - VERSÃO CORRIGIDA
# =====================================================
from .scraper_service import ESPNScraperService


@app.post("/clubs/{club_id}/scrape_players", response_model=List[schemas.PlayerResponse])
async def scrape_players_for_club_endpoint(
    club_id: int,
    db: Session = Depends(get_db),
    # current_user: schemas.User = Depends(get_current_active_user), # Removido para permitir scraping sem autenticação
):
    """
    Faz scraping do elenco de um clube na ESPN e salva/atualiza no banco de dados.
    A URL da ESPN é obtida do próprio objeto Club.
    """
    club = crud.get_club(db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Clube não encontrado")

    if not club.espn_url:
        raise HTTPException(status_code=400, detail="URL da ESPN não configurada para este clube.")

    try:
        scraper_service = ESPNScraperService(db)
        updated_players, errors = scraper_service.scrape_club_squad(club.espn_url, club_id)

        if errors:
            print(f"⚠️ Erros durante o scraping: {errors}")

        if not updated_players:
            raise HTTPException(status_code=404, detail="Nenhum atleta foi encontrado ou processado.")

        player_names = [player.name for player in updated_players]
        print(f"✅ Jogadores raspados e atualizados para o clube {club.name}: {', '.join(player_names)}")

        player_responses = []
        for player in updated_players:
            player_responses.append(schemas.PlayerResponse.model_validate(player))

        return player_responses

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao acessar a URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no scraping: {e}")


# =====================================================
# 🗓️ Rotas de Rotinas de Treinamento
# =====================================================
@app.post("/training_routines/", response_model=schemas.TrainingRoutineResponse)
def create_training_routine(
    routine: schemas.TrainingRoutineCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    try:
        return crud.create_training_routine(db=db, routine=routine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/training_routines/", response_model=List[schemas.TrainingRoutineResponse])
def read_training_routines(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    routines = crud.get_training_routines(db, skip=skip, limit=limit, club_id=club_id)
    return routines


@app.get("/training_routines/{routine_id}", response_model=schemas.TrainingRoutineResponse)
def read_training_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_routine = crud.get_training_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Rotina de treinamento não encontrada")
    return db_routine


@app.put("/training_routines/{routine_id}", response_model=schemas.TrainingRoutineResponse)
def update_training_routine(
    routine_id: int,
    routine: schemas.TrainingRoutineUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_routine = crud.update_training_routine(db, routine_id=routine_id, routine_update=routine)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Rotina de treinamento não encontrada")
    return db_routine


@app.delete("/training_routines/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    if not crud.delete_training_routine(db, routine_id=routine_id):
        raise HTTPException(status_code=404, detail="Rotina de treinamento não encontrada")


# =====================================================
# 🧍 Rotas de Jogadores
# =====================================================
@app.post("/players/", response_model=schemas.PlayerResponse)
def create_player(
    player: schemas.PlayerCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    try:
        return crud.create_player(db=db, player=player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/players/", response_model=List[schemas.PlayerResponse])
def read_players(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    name: Optional[str] = None,  # Adicione esta linha
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    players = crud.get_players(db, skip=skip, limit=limit, club_id=club_id, name=name)  # Adicione name=name
    return players


@app.get("/players/{player_id}", response_model=schemas.PlayerResponse)
def read_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return db_player


@app.put("/players/{player_id}", response_model=schemas.PlayerResponse)
def update_player(
    player_id: int,
    player: schemas.PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_player = crud.update_player(db, player_id=player_id, player_update=player)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return db_player


@app.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    if not crud.delete_player(db, player_id=player_id):
        raise HTTPException(status_code=404, detail="Jogador não encontrado")


# =====================================================
# 👤 Rotas de Autenticação e Usuários
# =====================================================
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")

    hashed_password = get_password_hash(user.password)
    db_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    return db_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email não registrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return current_user


@app.put("/users/me/", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserBase,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    db_user = crud.update_user_profile(db, current_user.id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user


@app.put("/users/me/password", response_model=schemas.User)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    hashed_password = get_password_hash(new_password)
    db_user = crud.update_user_password(db, current_user.id, hashed_password)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user


@app.delete("/users/me/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not crud.delete_user(db, current_user.id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


@app.post("/users/me/photo", response_model=schemas.User)
async def upload_profile_image(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
):
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension.lower() not in [".png", ".jpg", ".jpeg", ".gif"]:
        raise HTTPException(
            status_code=400,
            detail="Formato de imagem inválido. Apenas PNG, JPG, JPEG e GIF são permitidos.",
        )

    file_location = os.path.join(UPLOAD_DIRECTORY, f"{current_user.id}{file_extension}")
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    image_url = f"http://localhost:8000/{UPLOAD_DIRECTORY}/{current_user.id}{file_extension}"  # Assuming backend runs on 8000

    db_user = crud.update_user_profile_image(db, current_user.id, image_url)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user


# =====================================================
# 🛠️ Criação automática de usuário administrador
# =====================================================
with next(get_db()) as db:
    crud.create_admin_user_if_not_exists(
        db,
        settings.ADMIN_EMAIL,
        settings.ADMIN_PASSWORD,
        settings.ADMIN_NAME,
        get_password_hash,
    )
