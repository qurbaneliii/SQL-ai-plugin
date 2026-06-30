from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.api.health import router as health_router


app = FastAPI(
    title="SQL AI Copilot",
    version="0.2.0",
    description="Standalone PostgreSQL SQL copilot with hybrid OpenAI, Ollama, and fallback providers.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router)
