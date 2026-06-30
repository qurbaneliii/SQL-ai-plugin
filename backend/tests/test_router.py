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
