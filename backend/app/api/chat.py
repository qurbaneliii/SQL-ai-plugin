from fastapi import APIRouter, Depends

from app.schemas import ChatCommandsResponse, ChatMessageRequest, ChatMessageResponse
from app.services.chat_orchestrator import ChatOrchestrator
from app.settings import Settings, get_settings


router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_orchestrator(settings: Settings = Depends(get_settings)) -> ChatOrchestrator:
    return ChatOrchestrator.from_settings(settings)


@router.post("/message", response_model=ChatMessageResponse)
async def message(
    payload: ChatMessageRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> ChatMessageResponse:
    return await orchestrator.handle_chat_message(payload)


@router.get("/commands", response_model=ChatCommandsResponse)
async def commands() -> ChatCommandsResponse:
    return ChatCommandsResponse(
        commands=[
            {"command": "/schema", "description": "Inspect database schemas and tables."},
            {"command": "/generate", "description": "Generate read-only SQL from natural language."},
            {"command": "/explain", "description": "Explain a SQL query."},
            {"command": "/fix", "description": "Fix SQL errors or invalid syntax."},
            {"command": "/validate", "description": "Validate SQL safety."},
            {"command": "/run", "description": "Run safe read-only SQL."},
            {"command": "/optimize", "description": "Suggest query optimizations."},
            {"command": "/summarize", "description": "Summarize query results."},
            {"command": "/provider", "description": "Show provider selection behavior."},
            {"command": "/help", "description": "Show command help."},
        ]
    )
