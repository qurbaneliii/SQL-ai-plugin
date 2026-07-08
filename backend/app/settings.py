from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ProviderMode = Literal["auto", "openai", "local", "fallback"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    llm_provider: ProviderMode = Field(default="auto", alias="LLM_PROVIDER")

    local_llm_enabled: bool = Field(default=True, alias="LOCAL_LLM_ENABLED")
    local_llm_provider: str = Field(default="ollama", alias="LOCAL_LLM_PROVIDER")
    local_llm_base_url: str = Field(default="http://localhost:11434/v1", alias="LOCAL_LLM_BASE_URL")
    local_llm_model: str = Field(default="qwen3:4b", alias="LOCAL_LLM_MODEL")
    local_llm_timeout_seconds: int = Field(default=120, alias="LOCAL_LLM_TIMEOUT_SECONDS")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    db_connect_timeout_seconds: int = Field(default=10, alias="DB_CONNECT_TIMEOUT_SECONDS")
    db_statement_timeout_ms: int = Field(default=15000, alias="DB_STATEMENT_TIMEOUT_MS")
    db_default_row_limit: int = Field(default=100, alias="DB_DEFAULT_ROW_LIMIT")
    db_max_row_limit: int = Field(default=1000, alias="DB_MAX_ROW_LIMIT")
    db_schema_max_tables: int = Field(default=80, alias="DB_SCHEMA_MAX_TABLES")
    sql_allow_write_default: bool = Field(default=False, alias="SQL_ALLOW_WRITE_DEFAULT")
    sql_enable_explain_analyze: bool = Field(default=False, alias="SQL_ENABLE_EXPLAIN_ANALYZE")
    sql_sensitive_column_patterns: str = Field(
        default="password,passwd,secret,token,api_key,private_key,ssn,credit_card,card_number,email,phone",
        alias="SQL_SENSITIVE_COLUMN_PATTERNS",
    )

    @property
    def sensitive_column_patterns(self) -> list[str]:
        return [item.strip().lower() for item in self.sql_sensitive_column_patterns.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
