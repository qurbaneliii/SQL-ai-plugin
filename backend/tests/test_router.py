import asyncio

from app.services.providers.router import LLMRouter
from app.settings import Settings


def test_router_fallback_behavior() -> None:
    router = LLMRouter(Settings())
    assert router.select_provider_name("chat", "auto") in {"openai", "local", "fallback"}


def test_forced_fallback_mode() -> None:
    router = LLMRouter(Settings())
    assert router.select_provider_name("chat", "fallback") == "fallback"


def test_forced_openai_mode_falls_back_if_missing_key() -> None:
    router = LLMRouter(Settings(OPENAI_API_KEY=None))
    assert router.select_provider_name("chat", "openai") == "fallback"


def test_forced_local_mode_falls_back_if_unavailable() -> None:
    router = LLMRouter(Settings(LOCAL_LLM_ENABLED=False))
    assert router.select_provider_name("chat", "local") == "fallback"


def test_provider_test_targets_named_provider_not_conflicting_mode() -> None:
    router = LLMRouter(Settings(OPENAI_API_KEY=None, LOCAL_LLM_ENABLED=False))
    response = asyncio.run(router.test_provider("openai", "health", "local"))

    assert response.ok is False
    assert response.provider_metadata.provider_mode == "openai"
    assert response.provider_metadata.selected_provider == "fallback"
