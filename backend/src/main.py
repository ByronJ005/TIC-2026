import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.v1.auth_router import router as auth_router
from src.api.v1.cooperativas_router import router as cooperativas_router
from src.api.v1.profile_router import router as profile_router
from src.api.v1.users_router import router as users_router
from src.core.config import settings

app = FastAPI(
    title="BoletoYa API",
    description="API para la gestión y reserva de boletos de transporte terrestre",
    version="1.0.0",
)

# Static files for cooperative logos
os.makedirs(settings.LOGO_UPLOAD_DIR, exist_ok=True)
app.mount(
    "/static/logos",
    StaticFiles(directory=settings.LOGO_UPLOAD_DIR),
    name="static-logos",
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(cooperativas_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Salud"])
def health_check():
    return {"status": "ok", "service": "BoletoYa API"}
