from fastapi import APIRouter, Depends

from app.schemas import ResultSummaryRequest, SQLTaskResponse
from app.services.chat_orchestrator import ChatOrchestrator
from app.settings import Settings, get_settings


router = APIRouter(prefix="/api/result", tags=["result"])


def get_orchestrator(settings: Settings = Depends(get_settings)) -> ChatOrchestrator:
    return ChatOrchestrator.from_settings(settings)


@router.post("/summarize", response_model=SQLTaskResponse)
async def summarize(
    payload: ResultSummaryRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLTaskResponse:
    return await orchestrator.summarize_results(payload)
