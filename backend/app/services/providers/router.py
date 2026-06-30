from __future__ import annotations

from typing import Literal

from app.schemas import LLMStatusResponse, ProviderMetadata, ProviderMode, ProviderTestResponse
from app.services.providers.base import LLMProvider, ProviderError
from app.services.providers.fallback_provider import FallbackProvider
from app.services.providers.ollama_provider import OllamaProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.settings import Settings


TaskType = Literal[
    "sql_generate",
    "sql_fix",
    "sql_optimize",
    "sql_explain",
    "schema_qa",
    "result_summary",
    "chat",
    "safety_validation",
]


class LLMRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.openai = OpenAIProvider(settings)
        self.local = OllamaProvider(settings)
        self.fallback = FallbackProvider()
        self.task_preferences: dict[str, list[str]] = {
            "sql_generate": ["openai", "local", "fallback"],
            "sql_fix": ["openai", "local", "fallback"],
            "sql_optimize": ["openai", "local", "fallback"],
            "sql_explain": ["local", "openai", "fallback"],
            "schema_qa": ["local", "openai", "fallback"],
            "result_summary": ["local", "openai", "fallback"],
            "chat": ["openai", "local", "fallback"],
            "safety_validation": ["fallback"],
        }

    def status(self) -> LLMStatusResponse:
        return LLMStatusResponse(
            configured_mode=self.settings.llm_provider,
            effective_mode=self.select_provider_name("chat", self.settings.llm_provider),
            openai_available=self.openai.is_available(),
            local_available=self.local.is_available(),
            openai_model=self.settings.openai_model,
            local_model=self.settings.local_llm_model,
            local_provider=self.settings.local_llm_provider,
            router_preferences=self.task_preferences,
        )

    def get_provider(self, name: str) -> LLMProvider:
        if name == "openai":
            return self.openai
        if name == "local":
            return self.local
        return self.fallback

    def select_provider_name(self, task: TaskType, requested_mode: ProviderMode | None) -> Literal["openai", "local", "fallback"]:
        mode = requested_mode or self.settings.llm_provider
        if mode == "fallback" or task == "safety_validation":
            return "fallback"
        if mode == "openai":
            return "openai" if self.openai.is_available() else "fallback"
        if mode == "local":
            return "local" if self.local.is_available() else "fallback"
        for provider_name in self.task_preferences[task]:
            provider = self.get_provider(provider_name)
            if provider_name == "fallback" or provider.is_available():
                return provider_name  # type: ignore[return-value]
        return "fallback"

    def build_metadata(
        self,
        *,
        provider_mode: ProviderMode,
        selected_provider: Literal["openai", "local", "fallback"],
        warnings: list[str] | None = None,
    ) -> ProviderMetadata:
        provider = self.get_provider(selected_provider)
        return ProviderMetadata(
            provider_mode=provider_mode,
            selected_provider=selected_provider,
            model=provider.model_name,
            fallback_used=selected_provider == "fallback",
            warnings=warnings or [],
        )

    async def test_provider(
        self,
        provider_name: Literal["openai", "local"],
        prompt: str,
        provider_mode: ProviderMode | None,
    ) -> ProviderTestResponse:
        selected_provider = self.select_provider_name("chat", provider_name if provider_mode is None else provider_mode)
        warnings: list[str] = []
        if selected_provider != provider_name:
            warnings.append(f"Requested {provider_name} but router used fallback because the provider is unavailable.")
        provider = self.get_provider(selected_provider)
        ok, message = await provider.health_check()
        if ok and selected_provider != "fallback":
            try:
                sample = await provider.generate_text(system_prompt="Reply briefly.", user_prompt=prompt)
                message = sample.strip() or message
            except ProviderError as exc:
                ok = False
                message = str(exc)
        return ProviderTestResponse(
            ok=ok,
            message=message,
            provider_metadata=self.build_metadata(
                provider_mode=provider_mode or provider_name,
                selected_provider=selected_provider,
                warnings=warnings,
            ),
        )
