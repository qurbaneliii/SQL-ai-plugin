from __future__ import annotations

import json

from pydantic import BaseModel, Field

from app.prompts import SQL_SYSTEM_PROMPT
from app.schemas import ResultSummaryRequest, SQLTaskResponse
from app.services.providers.router import LLMRouter


class ResultResponse(BaseModel):
    content: str
    sql: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ResultAnalyzerService:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def summarize(self, payload: ResultSummaryRequest) -> SQLTaskResponse:
        provider_mode = payload.providerMode or self.router.settings.llm_provider
        selected_provider = self.router.select_provider_name("result_summary", payload.providerMode)
        provider = self.router.get_provider(selected_provider)
        sample_rows = payload.rows[:20]
        data = await provider.generate_json(
            system_prompt=SQL_SYSTEM_PROMPT,
            user_prompt=(
                "Summarize this PostgreSQL query result for a product engineer.\n"
                f"SQL: {payload.sql}\n"
                f"Prompt: {payload.prompt or 'Summarize the rows.'}\n"
                f"Rows: {json.dumps(sample_rows)}"
            ),
            response_model=ResultResponse,
        )
        return SQLTaskResponse(
            content=data["content"],
            sql=None,
            warnings=data.get("warnings", []),
            provider_metadata=self.router.build_metadata(
                provider_mode=provider_mode,
                selected_provider=selected_provider,
            ),
        )
