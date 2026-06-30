from __future__ import annotations

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import SQLTaskRequest, SQLTaskResponse
from app.services.providers.router import LLMRouter
from app.services.sql_safety import SQLSafetyValidator


class ExplainResponse(BaseModel):
    content: str
    sql: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SQLExplainerService:
    def __init__(self, router: LLMRouter, validator: SQLSafetyValidator) -> None:
        self.router = router
        self.validator = validator

    async def explain(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        sql = payload.sql or payload.prompt or ""
        validation = self.validator.validate(sql)
        provider_mode = payload.providerMode or self.router.settings.llm_provider
        selected_provider = self.router.select_provider_name("sql_explain", payload.providerMode)
        provider = self.router.get_provider(selected_provider)
        data = await provider.generate_json(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=f"Explain this PostgreSQL query in clear engineering language:\n{sql}",
            response_model=ExplainResponse,
        )
        warnings = list(dict.fromkeys([*data.get("warnings", []), *validation.warnings]))
        return SQLTaskResponse(
            content=data["content"],
            sql=payload.sql,
            warnings=warnings,
            provider_metadata=self.router.build_metadata(
                provider_mode=provider_mode,
                selected_provider=selected_provider,
            ),
            validation=validation.to_response(),
        )
