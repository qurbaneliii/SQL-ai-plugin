from __future__ import annotations

import time
from typing import Any

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.services.providers.base import LLMProvider, ProviderError
from app.services.providers.json_utils import build_json_repair_prompt, parse_json_payload
from app.settings import Settings


class OllamaProvider(LLMProvider):
    name = "local"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_name = settings.local_llm_model
        self.client = None
        self._available_cache: tuple[float, bool, str] | None = None
        if settings.local_llm_enabled and settings.local_llm_provider.lower() == "ollama":
            self.client = AsyncOpenAI(
                api_key="ollama",
                base_url=settings.local_llm_base_url,
                timeout=settings.local_llm_timeout_seconds,
            )

    def is_available(self) -> bool:
        if not self.client:
            return False
        now = time.monotonic()
        if self._available_cache and now - self._available_cache[0] < 30:
            return self._available_cache[1]
        ok, message = self._sync_probe()
        self._available_cache = (now, ok, message)
        return ok

    async def health_check(self) -> tuple[bool, str]:
        if not self.client:
            return False, "Local Ollama provider is disabled."
        try:
            await self.generate_text(system_prompt="Reply briefly.", user_prompt="Say local provider is healthy.")
            return True, "Local provider responded successfully."
        except Exception as exc:
            return False, f"Local provider check failed: {exc}"

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            raise ProviderError("Local provider is not configured.")
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
        except Exception as exc:
            raise ProviderError(f"Local provider request failed: {exc}") from exc
        message = response.choices[0].message.content if response.choices else ""
        if isinstance(message, list):
            return "\n".join(str(part) for part in message)
        return message or ""

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

    def _sync_probe(self) -> tuple[bool, str]:
        if not self.settings.local_llm_enabled:
            return False, "Local LLM is disabled."
        url = f"{self.settings.local_llm_base_url.rstrip('/')}/chat/completions"
        timeout = min(max(float(self.settings.local_llm_timeout_seconds), 1.0), 5.0)
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Reply with ok only."},
                {"role": "user", "content": "health"},
            ],
            "stream": False,
            "temperature": 0,
            "max_tokens": 8,
        }
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            return False, f"Local Ollama probe failed: {exc}"
        choices = data.get("choices") if isinstance(data, dict) else None
        if not choices:
            return False, "Local Ollama probe returned no model response."
        return True, "Local Ollama model responded successfully."
