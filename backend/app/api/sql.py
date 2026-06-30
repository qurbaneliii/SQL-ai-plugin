from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import (
    QueryExecutionResponse,
    SQLRunRequest,
    SQLTaskRequest,
    SQLTaskResponse,
    SQLValidationRequest,
    SQLValidationResponse,
)
from app.services.chat_orchestrator import ChatOrchestrator
from app.settings import Settings, get_settings


router = APIRouter(prefix="/api/sql", tags=["sql"])


def get_orchestrator(settings: Settings = Depends(get_settings)) -> ChatOrchestrator:
    return ChatOrchestrator.from_settings(settings)


@router.post("/validate", response_model=SQLValidationResponse)
async def validate_sql(
    payload: SQLValidationRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLValidationResponse:
    return orchestrator.validate_sql(payload.sql, payload.allow_write)


@router.post("/generate", response_model=SQLTaskResponse)
async def generate_sql(
    payload: SQLTaskRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLTaskResponse:
    return await orchestrator.generate_sql(payload)


@router.post("/explain", response_model=SQLTaskResponse)
async def explain_sql(
    payload: SQLTaskRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLTaskResponse:
    return await orchestrator.explain_sql(payload)


@router.post("/fix", response_model=SQLTaskResponse)
async def fix_sql(
    payload: SQLTaskRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLTaskResponse:
    return await orchestrator.fix_sql(payload)


@router.post("/run-readonly", response_model=QueryExecutionResponse)
async def run_readonly(
    payload: SQLRunRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> QueryExecutionResponse:
    try:
        return orchestrator.run_readonly(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/optimize", response_model=SQLTaskResponse)
async def optimize_sql(
    payload: SQLTaskRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> SQLTaskResponse:
    return await orchestrator.optimize_sql(payload)
