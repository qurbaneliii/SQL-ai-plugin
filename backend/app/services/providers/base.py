from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ProviderError(RuntimeError):
    pass


class LLMProvider(ABC):
    name: str
    model_name: str

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> tuple[bool, str]:
        raise NotImplementedError

    @abstractmethod
    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError
