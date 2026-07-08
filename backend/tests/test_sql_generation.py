import asyncio
from types import SimpleNamespace

from app.schemas import ProviderMetadata, SchemaSummaryResponse, SQLTaskRequest
from app.services.sql_generator import SQLGeneratorService
from app.services.sql_safety import SQLSafetyValidator
from app.settings import Settings


class FakeProvider:
    model_name = "fake-model"

    def __init__(self) -> None:
        self.calls = 0

    def is_available(self) -> bool:
        return True

    async def health_check(self) -> tuple[bool, str]:
        return True, "ok"

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return "{}"

    async def generate_json(self, *, system_prompt: str, user_prompt: str, response_model=None) -> dict:
        self.calls += 1
        if self.calls == 1:
            return {"content": "Unsafe first draft.", "sql": "DROP TABLE users", "warnings": []}
        return {"content": "Safe repair.", "sql": "SELECT id FROM users LIMIT 10", "warnings": []}


class FakeRouter:
    def __init__(self, provider: FakeProvider) -> None:
        self.settings = SimpleNamespace(llm_provider="auto")
        self.provider = provider

    def select_provider_name(self, task, provider_mode):
        return "openai"

    def get_provider(self, selected_provider):
        return self.provider

    def build_metadata(self, *, provider_mode, selected_provider, warnings=None):
        return ProviderMetadata(
            provider_mode=provider_mode,
            selected_provider=selected_provider,
            model=self.provider.model_name,
            fallback_used=False,
            warnings=warnings or [],
        )


class FakeDb:
    settings = Settings()

    def get_schema_summary(self, database_url=None, selected_schemas=None):
        return SchemaSummaryResponse(
            database_available=False,
            schemas=[],
            tables=[],
            enum_types=[],
            truncated=False,
            max_tables=80,
        )


def test_generated_unsafe_sql_is_repaired_before_return() -> None:
    provider = FakeProvider()
    service = SQLGeneratorService(FakeRouter(provider), FakeDb(), SQLSafetyValidator(Settings()))

    result = asyncio.run(service.generate(SQLTaskRequest(prompt="drop users and show count")))

    assert result.sql == "SELECT id FROM users LIMIT 10"
    assert result.validation is not None
    assert result.validation.is_valid is True
    assert provider.calls == 2
