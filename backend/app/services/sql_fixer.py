from __future__ import annotations

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import SQLTaskRequest, SQLTaskResponse
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
        validation = self.validator.validate(data.get("sql") or "") if data.get("sql") else None
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
