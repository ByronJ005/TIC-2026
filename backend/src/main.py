from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.auth_router import router as auth_router
from src.core.config import settings

app = FastAPI(
    title="BoletoYa API",
    description="API para la gestión y reserva de boletos de transporte terrestre",
    version="1.0.0",
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


@app.get("/api/v1/health", tags=["Salud"])
def health_check():
    return {"status": "ok", "service": "BoletoYa API"}
