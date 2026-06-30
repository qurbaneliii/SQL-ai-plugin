from fastapi import APIRouter, Depends

from app.schemas import LLMStatusResponse, ProviderTestRequest, ProviderTestResponse
from app.services.providers.router import LLMRouter
from app.settings import Settings, get_settings


router = APIRouter(prefix="/api/llm", tags=["llm"])


def get_router(settings: Settings = Depends(get_settings)) -> LLMRouter:
    return LLMRouter(settings)


@router.get("/status", response_model=LLMStatusResponse)
async def llm_status(router_service: LLMRouter = Depends(get_router)) -> LLMStatusResponse:
    return router_service.status()


@router.post("/test-openai", response_model=ProviderTestResponse)
async def test_openai(
    payload: ProviderTestRequest,
    router_service: LLMRouter = Depends(get_router),
) -> ProviderTestResponse:
    return await router_service.test_provider("openai", payload.prompt, payload.providerMode)


@router.post("/test-local", response_model=ProviderTestResponse)
async def test_local(
    payload: ProviderTestRequest,
    router_service: LLMRouter = Depends(get_router),
) -> ProviderTestResponse:
    return await router_service.test_provider("local", payload.prompt, payload.providerMode)
