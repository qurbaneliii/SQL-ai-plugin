from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import (
    DatabaseConnectRequest,
    DatabaseConnectResponse,
    SchemaSummaryRequest,
    SchemaSummaryResponse,
)
from app.services.database import PostgresService
from app.settings import Settings, get_settings


router = APIRouter(prefix="/api/db", tags=["db"])


def get_db(settings: Settings = Depends(get_settings)) -> PostgresService:
    return PostgresService(settings)


@router.post("/connect-test", response_model=DatabaseConnectResponse)
async def connect_test(
    payload: DatabaseConnectRequest,
    db: PostgresService = Depends(get_db),
) -> DatabaseConnectResponse:
    try:
        return db.test_connection(payload.databaseUrl)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/schema", response_model=SchemaSummaryResponse)
async def schema_summary(
    payload: SchemaSummaryRequest,
    db: PostgresService = Depends(get_db),
) -> SchemaSummaryResponse:
    try:
        return db.get_schema_summary(payload.databaseUrl, payload.selectedSchemas)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
