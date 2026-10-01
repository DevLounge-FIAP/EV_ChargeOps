from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.routes_chat import router as chat_router
from .api.routes_sessions import router as sessions_router
from .api.routes_billing import router as billing_router
from .api.routes_analytics import router as analytics_router
from .api.routes_admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir acesso do Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos roteadores da API
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(billing_router)
app.include_router(analytics_router)
app.include_router(admin_router)


@app.get("/api/status", tags=["Status"])
def api_status():
    return {
        "status": "online",
        "system": "EV ChargeOps API",
        "partnership": "GoodWe + FIAP (Energy Innovation Lab)",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "charger_model": "GoodWe HCA G2"
    }

@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "healthy", "service": "ev-chargeops-backend"}

# Servir Frontend automaticamente se a pasta existir
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
