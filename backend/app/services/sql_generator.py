from __future__ import annotations

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import SchemaSummaryResponse, SQLTaskRequest, SQLTaskResponse
from app.services.providers.router import LLMRouter
from app.services.schema_context import schema_context_text
from app.services.sql_safety import SQLSafetyValidator
from app.services.database import PostgresService


class StructuredSQLResponse(BaseModel):
    content: str
    sql: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SQLGeneratorService:
    def __init__(self, router: LLMRouter, db: PostgresService, validator: SQLSafetyValidator) -> None:
        self.router = router
        self.db = db
        self.validator = validator

    async def generate(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        try:
            schema = self.db.get_schema_summary(payload.databaseUrl, payload.selectedSchemas)
        except ValueError:
            schema = SchemaSummaryResponse(
                database_available=False,
                masked_database_url=None,
                schemas=[],
                tables=[],
                enum_types=[],
                truncated=False,
                max_tables=self.db.settings.db_schema_max_tables,
            )
        provider_mode = payload.providerMode or self.router.settings.llm_provider
        selected_provider = self.router.select_provider_name("sql_generate", payload.providerMode)
        provider = self.router.get_provider(selected_provider)
        data = await provider.generate_json(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=(
                "Generate safe PostgreSQL SQL for this request.\n"
                f"Request: {payload.prompt}\n"
                f"Selected tables: {', '.join(payload.selectedTables) or 'none'}\n"
                f"Schema context:\n{schema_context_text(schema, payload.selectedTables)}"
            ),
            response_model=StructuredSQLResponse,
        )
        validation = self.validator.validate(data.get("sql") or "") if data.get("sql") else None
        return SQLTaskResponse(
            content=data["content"],
            sql=data.get("sql"),
            warnings=data.get("warnings", []),
            provider_metadata=self.router.build_metadata(
                provider_mode=provider_mode,
                selected_provider=selected_provider,
            ),
            validation=validation.to_response() if validation else None,
        )
