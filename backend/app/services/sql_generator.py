from __future__ import annotations

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import SchemaSummaryResponse, SQLTaskRequest, SQLTaskResponse
from app.services.providers.base import LLMProvider, ProviderError
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
        schema_context = schema_context_text(schema, payload.selectedTables, payload.prompt)
        user_prompt = (
            "Generate safe PostgreSQL SQL for this request.\n"
            f"Request: {payload.prompt}\n"
            f"Selected tables: {', '.join(payload.selectedTables) or 'none'}\n"
            "Return null SQL if the request cannot be answered safely from the schema context.\n"
            f"Schema context:\n{schema_context}"
        )
        data = await provider.generate_json(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=StructuredSQLResponse,
        )
        data, validation = await self._ensure_safe_payload(data, user_prompt, provider)
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

    async def _ensure_safe_payload(
        self,
        data: dict,
        original_prompt: str,
        provider: LLMProvider,
    ):
        sql = data.get("sql")
        if not sql:
            return data, None

        validation = self.validator.validate(sql)
        warnings = list(data.get("warnings", []))
        if validation.is_valid and validation.suggested_sql and validation.suggested_sql != validation.normalized_sql:
            data["sql"] = validation.suggested_sql
            warnings.append("A bounded LIMIT was added before returning SQL.")
            data["warnings"] = list(dict.fromkeys(warnings))
            return data, self.validator.validate(validation.suggested_sql)

        if validation.is_valid:
            data["warnings"] = list(dict.fromkeys(warnings))
            return data, validation

        try:
            repaired = await provider.generate_json(
                system_prompt=SQL_SYSTEM_PROMPT,
                user_prompt=(
                    "Previous generated SQL failed deterministic safety validation.\n"
                    f"Blocked reason: {validation.blocked_reason}\n"
                    f"Original generation prompt:\n{original_prompt}\n"
                    "Return a conservative read-only SELECT with LIMIT, or null SQL if unsure."
                ),
                response_model=StructuredSQLResponse,
            )
        except ProviderError:
            repaired = {"content": data["content"], "sql": None, "warnings": []}
        repaired_validation = self.validator.validate(repaired.get("sql") or "") if repaired.get("sql") else None
        if repaired_validation and repaired_validation.is_valid:
            repaired_warnings = [
                *warnings,
                "Initial generated SQL was blocked and replaced with a deterministic safe fallback.",
                *repaired.get("warnings", []),
            ]
            repaired["warnings"] = list(dict.fromkeys(repaired_warnings))
            if repaired_validation.suggested_sql and repaired_validation.suggested_sql != repaired_validation.normalized_sql:
                repaired["sql"] = repaired_validation.suggested_sql
                repaired_validation = self.validator.validate(repaired_validation.suggested_sql)
            return repaired, repaired_validation

        warnings.append(validation.blocked_reason or "Generated SQL failed deterministic safety validation.")
        data["content"] = (
            f"{data['content']}\n\nThe generated SQL was blocked by deterministic safety validation and was not returned as runnable SQL."
        )
        data["sql"] = None
        data["warnings"] = list(dict.fromkeys(warnings))
        return data, validation
