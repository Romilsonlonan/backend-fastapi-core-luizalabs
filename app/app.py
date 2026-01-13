import os
import uuid  # Adicionado
from datetime import date, timedelta, datetime
from typing import Annotated, List, Optional, Union

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

from . import crud_modules as crud, models, schemas
from .crud_modules.seed_data import seed_appointment_data
from .config import settings  # Correct import for settings
from .database import SessionLocal, engine
from .security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from .scraper_api import router as scraper_router # Import the scraper router
from .routers.webhooks import router as webhooks_router
from .modules.clubs.router import router as clubs_router
from .dependencies import get_db, get_current_active_user

# =====================================================
# 📘 Inicialização do Banco de Dados
# =====================================================
models.Base.metadata.create_all(bind=engine)


# =====================================================
# 🚀 Instanciação da Aplicação FastAPI
# =====================================================
app = FastAPI()

# 🌐 Configuração CORS
# =====================================================
# Nota: allow_origins não pode ser ["*"] quando allow_credentials é True.
# Listamos explicitamente as origens permitidas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9002",
        "http://127.0.0.1:9002",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include the routers
app.include_router(scraper_router)
app.include_router(webhooks_router)
app.include_router(clubs_router)

print("Routers included and CORS configured in FastAPI app.")


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
# 🕸️ Rotas de Web Scraping - VERSÃO CORRIGIDA
# =====================================================
from .scraper_service import ESPNScraperService


@app.post("/clubs/{club_id}/scrape_players", response_model=List[Union[schemas.GoalkeeperResponse, schemas.FieldPlayerResponse]])
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
        goalkeepers, field_players, errors = scraper_service.scrape_club_squad(club.espn_url, club_id)

        if errors:
            print(f"⚠️ Erros durante o scraping: {errors}")

        if not goalkeepers and not field_players:
            raise HTTPException(status_code=404, detail="Nenhum atleta foi encontrado ou processado.")

        all_players_response = []
        for gk in goalkeepers:
            all_players_response.append(schemas.GoalkeeperResponse.model_validate(gk))
        for fp in field_players:
            all_players_response.append(schemas.FieldPlayerResponse.model_validate(fp))

        print(f"✅ Scraping finalizado para o clube {club.name}. Goleiros: {len(goalkeepers)}, Jogadores de Campo: {len(field_players)}")

        return all_players_response

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
# 🥅 Rotas de Goleiros
# =====================================================
@app.post("/goalkeepers/", response_model=schemas.GoalkeeperResponse)
def create_goalkeeper(
    goalkeeper: schemas.Goalkeeper,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    try:
        return crud.create_goalkeeper(db=db, goalkeeper=goalkeeper, club_id=club_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/goalkeepers/", response_model=List[schemas.GoalkeeperResponse])
def read_goalkeepers(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    goalkeepers = crud.get_goalkeepers(db, skip=skip, limit=limit, club_id=club_id, name=name)
    return goalkeepers


@app.get("/goalkeepers/{goalkeeper_id}", response_model=schemas.GoalkeeperResponse)
def read_goalkeeper(
    goalkeeper_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_goalkeeper = crud.get_goalkeeper(db, goalkeeper_id=goalkeeper_id)
    if db_goalkeeper is None:
        raise HTTPException(status_code=404, detail="Goleiro não encontrado")
    return db_goalkeeper


@app.put("/goalkeepers/{goalkeeper_id}", response_model=schemas.GoalkeeperResponse)
def update_goalkeeper(
    goalkeeper_id: int,
    goalkeeper: schemas.Goalkeeper,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_goalkeeper = crud.update_goalkeeper(db, goalkeeper_id=goalkeeper_id, goalkeeper_update=goalkeeper)
    if db_goalkeeper is None:
        raise HTTPException(status_code=404, detail="Goleiro não encontrado")
    return db_goalkeeper


@app.delete("/goalkeepers/{goalkeeper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goalkeeper(
    goalkeeper_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    if not crud.delete_goalkeeper(db, goalkeeper_id=goalkeeper_id):
        raise HTTPException(status_code=404, detail="Goleiro não encontrado")


# =====================================================
# 🏥 Rotas de Centro de Treinamento (Saúde e Nutrição)
# =====================================================
@app.patch("/athletes/{athlete_id}/health", response_model=Union[schemas.GoalkeeperResponse, schemas.FieldPlayerResponse])
def update_athlete_health(
    athlete_id: int,
    is_goalkeeper: bool,
    health_data: schemas.AthleteHealthUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_athlete = crud.update_athlete_health(db, athlete_id, is_goalkeeper, health_data)
    if not db_athlete:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    return db_athlete


@app.post("/athletes/progress/", response_model=schemas.AthleteProgressResponse)
def create_athlete_progress(
    progress: schemas.AthleteProgressCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.create_athlete_progress(db, progress)


@app.get("/athletes/{athlete_id}/progress", response_model=List[schemas.AthleteProgressResponse])
def read_athlete_progress(
    athlete_id: int,
    is_goalkeeper: bool,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.get_athlete_progress(db, athlete_id, is_goalkeeper)


@app.post("/athletes/nutritional_plans/", response_model=schemas.NutritionalPlanResponse)
def create_nutritional_plan(
    plan: schemas.NutritionalPlanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.create_nutritional_plan(db, plan)


@app.get("/athletes/{athlete_id}/nutritional_plans", response_model=List[schemas.NutritionalPlanResponse])
def read_nutritional_plans(
    athlete_id: int,
    is_goalkeeper: bool,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.get_nutritional_plans(db, athlete_id, is_goalkeeper)


# =====================================================
# 📅 Rotas de Agenda e Consultas
# =====================================================
@app.get("/appointments/", response_model=List[schemas.AppointmentResponse])
def read_appointments(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.get_appointments(db, nutritionist_id=current_user.id, start_date=start_date, end_date=end_date)


@app.post("/appointments/", response_model=schemas.AppointmentResponse)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.create_appointment(db, appointment)


@app.patch("/appointments/{appointment_id}/status", response_model=schemas.AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.update_appointment_status(db, appointment_id, status)


@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_appointment = crud.update_appointment(db, appointment_id, appointment)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return db_appointment


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    if not crud.delete_appointment(db, appointment_id):
        raise HTTPException(status_code=404, detail="Consulta não encontrada")


@app.get("/services/", response_model=List[schemas.ServiceResponse])
def read_services(db: Session = Depends(get_db)):
    return crud.get_services(db)


@app.post("/services/", response_model=schemas.ServiceResponse)
def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.create_service(db, service)


@app.get("/locations/", response_model=List[schemas.LocationResponse])
def read_locations(db: Session = Depends(get_db)):
    return crud.get_locations(db)


@app.post("/locations/", response_model=schemas.LocationResponse)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.create_location(db, location)


@app.get("/availabilities/", response_model=List[schemas.AvailabilityResponse])
def read_availabilities(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.get_availabilities(db, user_id=current_user.id)


@app.post("/availabilities/", response_model=schemas.AvailabilityResponse)
def update_availability(
    availability: schemas.AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    return crud.update_availability(db, availability)


# =====================================================
# 🏃 Rotas de Jogadores de Campo
# =====================================================
@app.post("/field_players/", response_model=schemas.FieldPlayerResponse)
def create_field_player(
    field_player: schemas.FieldPlayer,
    club_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    try:
        return crud.create_field_player(db=db, field_player=field_player, club_id=club_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/field_players/", response_model=List[schemas.FieldPlayerResponse])
def read_field_players(
    skip: int = 0,
    limit: int = 100,
    club_id: Optional[int] = None,
    name: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    field_players = crud.get_field_players(db, skip=skip, limit=limit, club_id=club_id, name=name, position=position)
    return field_players


@app.get("/field_players/{field_player_id}", response_model=schemas.FieldPlayerResponse)
def read_field_player(
    field_player_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_field_player = crud.get_field_player(db, field_player_id=field_player_id)
    if db_field_player is None:
        raise HTTPException(status_code=404, detail="Jogador de campo não encontrado")
    return db_field_player


@app.put("/field_players/{field_player_id}", response_model=schemas.FieldPlayerResponse)
def update_field_player(
    field_player_id: int,
    field_player: schemas.FieldPlayer,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    db_field_player = crud.update_field_player(db, field_player_id=field_player_id, field_player_update=field_player)
    if db_field_player is None:
        raise HTTPException(status_code=404, detail="Jogador de campo não encontrado")
    return db_field_player


@app.delete("/field_players/{field_player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_player(
    field_player_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    if not crud.delete_field_player(db, field_player_id=field_player_id):
        raise HTTPException(status_code=404, detail="Jogador de campo não encontrado")


@app.get("/statistics/top_goal_scorers/", response_model=List[schemas.FieldPlayerResponse])
def get_top_goal_scorers_endpoint(
    limit: int = 7,
    position: Optional[str] = None,
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retorna os 7 maiores artilheiros do campeonato brasileiro,
    com opção de filtrar por posição e clube.
    """
    return crud.get_top_goal_scorers(db, limit=limit, position=position, club_id=club_id)


@app.get("/statistics/top_players_by_statistic/", response_model=List[Union[schemas.FieldPlayerResponse, schemas.GoalkeeperResponse]])
def get_top_players_by_statistic_endpoint(
    limit: int = 7,
    statistic: str = None,
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retorna os 7 maiores jogadores por uma estatística específica,
    com opção de filtrar por clube.
    """
    valid_statistics = [
        'goals', 'assists', 'total_shots', 'shots_on_goal', 
        'goals_conceded', 'saves', 'fouls_suffered', 
        'fouls_committed', 'yellow_cards', 'red_cards'
    ]
    if statistic not in valid_statistics:
        raise HTTPException(status_code=400, detail=f"Estatística inválida fornecida: {statistic}")
    return crud.get_top_players_by_statistic(db, limit=limit, statistic=statistic, club_id=club_id)


@app.get("/statistics/top_players_by_age/", response_model=List[Union[schemas.FieldPlayerResponse, schemas.GoalkeeperResponse]])
def get_top_players_by_age_endpoint(
    limit: int = 7,
    age_filter: str = 'oldest',
    club_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retorna os 7 jogadores mais velhos ou mais novos do campeonato,
    com opção de filtrar por clube.
    """
    if age_filter not in ['oldest', 'youngest']:
        raise HTTPException(status_code=400, detail="Filtro de idade inválido fornecido.")
    return crud.get_top_players_by_age(db, limit=limit, age_filter=age_filter, club_id=club_id)


@app.get("/statistics/total_athletes_count/", response_model=schemas.TotalCountResponse)
def get_total_athletes_count_endpoint(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retorna o número total de atletas (jogadores de campo e goleiros).
    """
    total_count = crud.get_total_athletes_count(db)
    return {"total_count": total_count}


@app.get("/statistics/total_clubs_count/", response_model=schemas.TotalCountResponse)
def get_total_clubs_count_endpoint(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retorna o número total de clubes.
    """
    total_count = crud.get_total_clubs_count(db)
    return {"total_count": total_count}


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


@app.post("/create-payment-intent")
async def create_payment_intent(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    try:
        # Em um cenário real, você usaria stripe.PaymentIntent.create
        # Aqui vamos simular a criação de uma intenção de pagamento
        # intent = stripe.PaymentIntent.create(
        #     amount=2990, # R$ 29,90
        #     currency='brl',
        #     metadata={'user_id': current_user.id}
        # )
        # return {"client_secret": intent.client_secret}
        
        # Simulação para fins de demonstração
        return {
            "client_secret": f"pi_simulated_{uuid.uuid4()}_secret_{uuid.uuid4()}",
            "payment_id": f"pi_simulated_{uuid.uuid4()}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    password_data: schemas.PasswordChange,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")

    hashed_password = get_password_hash(password_data.new_password)
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
# 🛠️ Criação automática de usuário administrador e dados de semente
# =====================================================
with next(get_db()) as db:
    crud.create_admin_user_if_not_exists(
        db,
        settings.ADMIN_EMAIL,
        settings.ADMIN_PASSWORD,
        settings.ADMIN_NAME,
        get_password_hash,
    )
    seed_appointment_data(db)
