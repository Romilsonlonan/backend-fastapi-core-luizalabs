import os
from fastapi import FastAPI, staticfiles
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .core.setup import initialize_data

# Importação dos Routers Modulares
from .modules.clubs.router import router as clubs_router
from .modules.athletes.router import router as athletes_router
from .modules.training.router import router as training_router
from .modules.scraper.router import router as scraper_router
from .modules.appointments.router import router as appointments_router
from .modules.users.router import router as users_router
from .modules.payments.router import router as payments_router

# =====================================================
# 📘 Inicialização do Banco de Dados
# =====================================================
models.Base.metadata.create_all(bind=engine)

# =====================================================
# 🚀 Instanciação da Aplicação FastAPI
# =====================================================
app = FastAPI(
    title="CBF Manager API",
    description="API para gestão de clubes e atletas com arquitetura modular.",
    version="2.0.0"
)

# 🌐 Configuração CORS
# =====================================================
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

# =====================================================
# 🛣️ Registro de Rotas (Arquitetura Modular)
# =====================================================
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(clubs_router)
app.include_router(athletes_router)
app.include_router(training_router)
app.include_router(scraper_router)
app.include_router(appointments_router)
app.include_router(users_router)
app.include_router(payments_router)

print("✅ Todos os módulos carregados com sucesso.")

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
# 🛠️ Inicialização de Dados (Admin & Seeds)
# =====================================================
initialize_data()
