from fastapi import APIRouter, Depends

from app.schemas import HealthResponse
from app.settings import Settings, get_settings


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider_mode=settings.llm_provider,
        local_llm_enabled=settings.local_llm_enabled,
        database_configured=bool(settings.database_url),
    )
