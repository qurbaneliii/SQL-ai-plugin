from __future__ import annotations

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import SQLTaskRequest, SQLTaskResponse
from app.services.providers.base import ProviderError
from app.services.providers.router import LLMRouter
from app.services.sql_safety import SQLSafetyValidator


class FixResponse(BaseModel):
    content: str
    sql: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SQLFixerService:
    def __init__(self, router: LLMRouter, validator: SQLSafetyValidator) -> None:
        self.router = router
        self.validator = validator

    async def fix(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        provider_mode = payload.providerMode or self.router.settings.llm_provider
        selected_provider = self.router.select_provider_name("sql_fix", payload.providerMode)
        provider = self.router.get_provider(selected_provider)
        data = await provider.generate_json(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=(
                "Fix this PostgreSQL SQL conservatively.\n"
                f"SQL: {payload.sql}\n"
                f"Error: {payload.error or 'not provided'}"
            ),
            response_model=FixResponse,
        )
        data, validation = await self._ensure_safe_fix(data, payload.sql or "", payload.error or "", provider)
        warnings = list(data.get("warnings", []))
        if validation and not validation.is_valid and validation.blocked_reason:
            warnings.append(validation.blocked_reason)
        return SQLTaskResponse(
            content=data["content"],
            sql=data.get("sql"),
            warnings=list(dict.fromkeys(warnings)),
            provider_metadata=self.router.build_metadata(
                provider_mode=provider_mode,
                selected_provider=selected_provider,
            ),
            validation=validation.to_response() if validation else None,
        )

    async def _ensure_safe_fix(self, data: dict, sql: str, error: str, provider):
        candidate = data.get("sql")
        if not candidate:
            return data, None
        validation = self.validator.validate(candidate)
        warnings = list(data.get("warnings", []))
        if validation.is_valid and validation.suggested_sql and validation.suggested_sql != validation.normalized_sql:
            data["sql"] = validation.suggested_sql
            warnings.append("A bounded LIMIT was added before returning fixed SQL.")
            data["warnings"] = list(dict.fromkeys(warnings))
            return data, self.validator.validate(validation.suggested_sql)
        if validation.is_valid:
            data["warnings"] = list(dict.fromkeys(warnings))
            return data, validation

        try:
            repaired = await provider.generate_json(
                system_prompt=SQL_SYSTEM_PROMPT,
                user_prompt=(
                    "The previous SQL fix failed deterministic safety validation.\n"
                    f"Blocked reason: {validation.blocked_reason}\n"
                    f"Original SQL: {sql}\n"
                    f"Original error: {error or 'not provided'}\n"
                    "Return a safe read-only PostgreSQL SELECT with LIMIT, or null SQL if the fix would require writes."
                ),
                response_model=FixResponse,
            )
        except ProviderError:
            repaired = {"content": data["content"], "sql": None, "warnings": []}
        repaired_validation = self.validator.validate(repaired.get("sql") or "") if repaired.get("sql") else None
        if repaired_validation and repaired_validation.is_valid:
            repaired["warnings"] = list(
                dict.fromkeys(
                    [
                        *warnings,
                        "Initial fixed SQL was blocked and replaced after one safe repair attempt.",
                        *repaired.get("warnings", []),
                    ]
                )
            )
            if repaired_validation.suggested_sql and repaired_validation.suggested_sql != repaired_validation.normalized_sql:
                repaired["sql"] = repaired_validation.suggested_sql
                repaired_validation = self.validator.validate(repaired_validation.suggested_sql)
            return repaired, repaired_validation

        warnings.append(validation.blocked_reason or "Fixed SQL failed deterministic safety validation.")
        data["content"] = f"{data['content']}\n\nThe fixed SQL was blocked by deterministic safety validation and was not returned as runnable SQL."
        data["sql"] = None
        data["warnings"] = list(dict.fromkeys(warnings))
        return data, validation
