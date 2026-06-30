from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.services.providers.base import LLMProvider, ProviderError
from app.services.providers.json_utils import build_json_repair_prompt, parse_json_payload
from app.settings import Settings


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_name = settings.openai_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def is_available(self) -> bool:
        return self.client is not None

    async def health_check(self) -> tuple[bool, str]:
        if not self.client:
            return False, "OPENAI_API_KEY is not configured."
        try:
            await self.generate_text(system_prompt="Reply briefly.", user_prompt="Say OpenAI provider is healthy.")
            return True, "OpenAI provider responded successfully."
        except Exception as exc:
            return False, f"OpenAI provider check failed: {exc}"

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            raise ProviderError("OpenAI provider is not configured.")
        try:
            response = await self.client.responses.create(
                model=self.model_name,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise ProviderError(f"OpenAI request failed: {exc}") from exc
        return response.output_text

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        raw = await self.generate_text(
            system_prompt=f"{system_prompt}\nReturn strict JSON only.",
            user_prompt=user_prompt,
        )
        try:
            return parse_json_payload(raw, response_model)
        except ProviderError:
            repaired = await self.generate_text(
                system_prompt="You are a JSON repair tool. Return strict JSON only.",
                user_prompt=build_json_repair_prompt(raw),
            )
            return parse_json_payload(repaired, response_model)
