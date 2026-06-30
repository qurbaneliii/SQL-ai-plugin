from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


ProviderMode = Literal["auto", "openai", "local", "fallback"]
IntentType = Literal[
    "sql_generate",
    "sql_explain",
    "sql_fix",
    "sql_validate",
    "sql_run",
    "sql_optimize",
    "schema_question",
    "result_summary",
    "general_help",
]


class ProviderMetadata(BaseModel):
    provider_mode: ProviderMode
    selected_provider: Literal["openai", "local", "fallback"]
    model: str
    fallback_used: bool
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    provider_mode: ProviderMode
    local_llm_enabled: bool
    database_configured: bool


class LLMStatusResponse(BaseModel):
    configured_mode: ProviderMode
    effective_mode: Literal["openai", "local", "fallback"]
    openai_available: bool
    local_available: bool
    fallback_available: bool = True
    openai_model: str
    local_model: str
    local_provider: str
    router_preferences: dict[str, list[str]]


class ProviderTestRequest(BaseModel):
    providerMode: ProviderMode | None = None
    prompt: str = "Return a short health confirmation."


class ProviderTestResponse(BaseModel):
    ok: bool
    message: str
    provider_metadata: ProviderMetadata


class DatabaseConnectRequest(BaseModel):
    databaseUrl: str | None = None


class DatabaseConnectResponse(BaseModel):
    ok: bool
    message: str
    masked_database_url: str | None = None
    server_version: str | None = None


class ColumnInfo(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    default: str | None = None
    comment: str | None = None


class ForeignKeyInfo(BaseModel):
    name: str
    column_names: list[str]
    referenced_schema: str
    referenced_table: str
    referenced_columns: list[str]


class IndexInfo(BaseModel):
    name: str
    definition: str


class TableInfo(BaseModel):
    schema_name: str
    table_name: str
    table_type: str
    columns: list[ColumnInfo]
    primary_key: list[str] = Field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = Field(default_factory=list)
    indexes: list[IndexInfo] = Field(default_factory=list)
    comment: str | None = None
    approximate_row_count: int | None = None
    sensitive_columns: list[str] = Field(default_factory=list)


class EnumInfo(BaseModel):
    schema_name: str
    type_name: str
    values: list[str]


class SchemaSummaryRequest(BaseModel):
    databaseUrl: str | None = None
    selectedSchemas: list[str] = Field(default_factory=list)


class SchemaSummaryResponse(BaseModel):
    database_available: bool
    masked_database_url: str | None = None
    schemas: list[str] = Field(default_factory=list)
    tables: list[TableInfo] = Field(default_factory=list)
    enum_types: list[EnumInfo] = Field(default_factory=list)
    truncated: bool = False
    max_tables: int = 0


class SQLValidationRequest(BaseModel):
    sql: str
    allow_write: bool = False


class SQLValidationResponse(BaseModel):
    is_valid: bool
    is_readonly: bool
    blocked_reason: str | None = None
    risk_level: Literal["low", "medium", "high"]
    detected_statement_type: str
    referenced_tables: list[str] = Field(default_factory=list)
    referenced_columns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    normalized_sql: str | None = None
    suggested_sql: str | None = None


class SQLTaskRequest(BaseModel):
    prompt: str | None = None
    sql: str | None = None
    error: str | None = None
    databaseUrl: str | None = None
    selectedSchemas: list[str] = Field(default_factory=list)
    selectedTables: list[str] = Field(default_factory=list)
    providerMode: ProviderMode | None = None


class SQLTaskResponse(BaseModel):
    content: str
    sql: str | None = None
    warnings: list[str] = Field(default_factory=list)
    provider_metadata: ProviderMetadata
    validation: SQLValidationResponse | None = None


class SQLRunRequest(BaseModel):
    sql: str
    databaseUrl: str | None = None
    rowLimit: int | None = None
    providerMode: ProviderMode | None = None


class QueryExecutionResponse(BaseModel):
    sql: str
    normalized_sql: str
    row_limit: int
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool
    execution_time_ms: int
    warnings: list[str] = Field(default_factory=list)
    provider_metadata: ProviderMetadata | None = None


class ResultSummaryRequest(BaseModel):
    sql: str
    rows: list[dict[str, Any]]
    prompt: str | None = None
    providerMode: ProviderMode | None = None


class ChatAction(BaseModel):
    type: str
    label: str


class ChatMessageRequest(BaseModel):
    message: str
    databaseUrl: str | None = None
    currentSql: str = ""
    selectedSchemas: list[str] = Field(default_factory=list)
    selectedTables: list[str] = Field(default_factory=list)
    providerMode: ProviderMode | None = None
    autoRun: bool = False


class ChatMessageResponse(BaseModel):
    assistant_message: str
    intent: IntentType
    sql: str | None = None
    actions: list[ChatAction] = Field(default_factory=list)
    safety: SQLValidationResponse | None = None
    result_preview: QueryExecutionResponse | None = None
    provider_metadata: ProviderMetadata


class ChatCommandsResponse(BaseModel):
    commands: list[dict[str, str]]


SerializableScalar = str | int | float | bool | None


def make_json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, UUID)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    return str(value)
