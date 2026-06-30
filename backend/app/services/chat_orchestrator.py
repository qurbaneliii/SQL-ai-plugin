from __future__ import annotations

from dataclasses import dataclass

from app.schemas import (
    ChatAction,
    ChatMessageRequest,
    ChatMessageResponse,
    ProviderMode,
    QueryExecutionResponse,
    ResultSummaryRequest,
    SQLRunRequest,
    SQLTaskRequest,
    SQLTaskResponse,
    SQLValidationResponse,
)
from app.services.database import PostgresService
from app.services.result_analyzer import ResultAnalyzerService
from app.services.sql_explainer import SQLExplainerService
from app.services.sql_fixer import SQLFixerService
from app.services.sql_generator import SQLGeneratorService
from app.services.sql_optimizer import SQLOptimizerService
from app.services.sql_safety import SQLSafetyValidator
from app.services.providers.router import LLMRouter
from app.settings import Settings


@dataclass
class IntentMatch:
    intent: str
    message: str


class ChatOrchestrator:
    def __init__(self, settings: Settings, db: PostgresService, router: LLMRouter) -> None:
        self.settings = settings
        self.db = db
        self.router = router
        self.validator = SQLSafetyValidator(settings)
        self.generator = SQLGeneratorService(router, db, self.validator)
        self.explainer = SQLExplainerService(router, self.validator)
        self.fixer = SQLFixerService(router, self.validator)
        self.optimizer = SQLOptimizerService(router, self.validator)
        self.result_analyzer = ResultAnalyzerService(router)

    @classmethod
    def from_settings(cls, settings: Settings) -> "ChatOrchestrator":
        db = PostgresService(settings)
        router = LLMRouter(settings)
        return cls(settings, db, router)

    def validate_sql(self, sql: str, allow_write: bool = False) -> SQLValidationResponse:
        return self.validator.validate(sql, allow_write=allow_write).to_response()

    async def generate_sql(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        return await self.generator.generate(payload)

    async def explain_sql(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        return await self.explainer.explain(payload)

    async def fix_sql(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        return await self.fixer.fix(payload)

    async def optimize_sql(self, payload: SQLTaskRequest) -> SQLTaskResponse:
        return await self.optimizer.optimize(payload)

    async def summarize_results(self, payload: ResultSummaryRequest) -> SQLTaskResponse:
        return await self.result_analyzer.summarize(payload)

    def run_readonly(self, payload: SQLRunRequest) -> QueryExecutionResponse:
        validation = self.validator.validate(payload.sql, allow_write=False)
        if not validation.is_valid or not validation.suggested_sql:
            raise ValueError(validation.blocked_reason or "Unsafe SQL was blocked before execution.")
        requested_limit = payload.rowLimit or self.settings.db_default_row_limit
        row_limit = max(1, min(requested_limit, self.settings.db_max_row_limit))
        execution = self.db.execute_read_only(validation.suggested_sql, payload.databaseUrl, row_limit)
        execution.sql = payload.sql
        execution.normalized_sql = validation.suggested_sql
        execution.row_limit = row_limit
        execution.warnings = validation.warnings
        execution.provider_metadata = self.router.build_metadata(
            provider_mode=payload.providerMode or self.settings.llm_provider,
            selected_provider="fallback",
            warnings=["SQL execution uses deterministic safety validation before database access."],
        )
        return execution

    async def handle_chat_message(self, payload: ChatMessageRequest) -> ChatMessageResponse:
        intent = self._detect_intent(payload.message, payload.currentSql)
        provider_mode = payload.providerMode or self.settings.llm_provider

        if "drop " in payload.message.lower() or "delete " in payload.message.lower() or "update " in payload.message.lower():
            metadata = self.router.build_metadata(provider_mode=provider_mode, selected_provider="fallback")
            return ChatMessageResponse(
                assistant_message="This MVP blocks destructive or write SQL. I can help you inspect the affected rows with a safe SELECT instead.",
                intent="general_help",
                sql=None,
                actions=[ChatAction(type="generate_sql", label="Generate safe SELECT")],
                safety=None,
                result_preview=None,
                provider_metadata=metadata,
            )

        if intent.intent == "sql_generate":
            task = await self.generate_sql(
                SQLTaskRequest(
                    prompt=intent.message,
                    databaseUrl=payload.databaseUrl,
                    selectedSchemas=payload.selectedSchemas,
                    selectedTables=payload.selectedTables,
                    providerMode=payload.providerMode,
                )
            )
            result_preview = None
            if payload.autoRun and task.sql and task.validation and task.validation.is_valid:
                result_preview = self.run_readonly(
                    SQLRunRequest(
                        sql=task.sql,
                        databaseUrl=payload.databaseUrl,
                        providerMode=payload.providerMode,
                    )
                )
            return ChatMessageResponse(
                assistant_message=task.content,
                intent="sql_generate",
                sql=task.sql,
                actions=self._actions_for_sql(),
                safety=task.validation,
                result_preview=result_preview,
                provider_metadata=task.provider_metadata,
            )

        if intent.intent == "sql_explain":
            sql = payload.currentSql or intent.message
            task = await self.explain_sql(SQLTaskRequest(sql=sql, providerMode=payload.providerMode))
            return ChatMessageResponse(
                assistant_message=task.content,
                intent="sql_explain",
                sql=sql,
                actions=[ChatAction(type="validate_sql", label="Validate SQL")],
                safety=task.validation,
                result_preview=None,
                provider_metadata=task.provider_metadata,
            )

        if intent.intent == "sql_fix":
            task = await self.fix_sql(
                SQLTaskRequest(sql=payload.currentSql or None, error=intent.message, providerMode=payload.providerMode)
            )
            return ChatMessageResponse(
                assistant_message=task.content,
                intent="sql_fix",
                sql=task.sql,
                actions=self._actions_for_sql(),
                safety=task.validation,
                result_preview=None,
                provider_metadata=task.provider_metadata,
            )

        if intent.intent == "sql_validate":
            sql = payload.currentSql or intent.message
            safety = self.validate_sql(sql, False)
            metadata = self.router.build_metadata(provider_mode=provider_mode, selected_provider="fallback")
            return ChatMessageResponse(
                assistant_message="SQL safety validation completed.",
                intent="sql_validate",
                sql=sql,
                actions=[ChatAction(type="run_readonly", label="Run read-only")],
                safety=safety,
                result_preview=None,
                provider_metadata=metadata,
            )

        if intent.intent == "sql_run":
            sql = payload.currentSql or intent.message
            preview = self.run_readonly(
                SQLRunRequest(sql=sql, databaseUrl=payload.databaseUrl, providerMode=payload.providerMode)
            )
            return ChatMessageResponse(
                assistant_message="Query executed in read-only mode.",
                intent="sql_run",
                sql=sql,
                actions=[ChatAction(type="summarize_results", label="Summarize results")],
                safety=self.validate_sql(sql, False),
                result_preview=preview,
                provider_metadata=preview.provider_metadata or self.router.build_metadata(
                    provider_mode=provider_mode,
                    selected_provider="fallback",
                ),
            )

        if intent.intent == "sql_optimize":
            sql = payload.currentSql or intent.message
            task = await self.optimize_sql(SQLTaskRequest(sql=sql, providerMode=payload.providerMode))
            return ChatMessageResponse(
                assistant_message=task.content,
                intent="sql_optimize",
                sql=sql,
                actions=[ChatAction(type="copy_sql", label="Copy SQL")],
                safety=task.validation,
                result_preview=None,
                provider_metadata=task.provider_metadata,
            )

        if intent.intent == "schema_question":
            try:
                schema = self.db.get_schema_summary(payload.databaseUrl, payload.selectedSchemas)
            except ValueError:
                schema = None
            selected_provider = self.router.select_provider_name("schema_qa", payload.providerMode)
            metadata = self.router.build_metadata(provider_mode=provider_mode, selected_provider=selected_provider)
            table_names = (
                ", ".join(f"{table.schema_name}.{table.table_name}" for table in schema.tables[:12])
                if schema
                else "No database connected yet."
            ) or "No tables loaded."
            return ChatMessageResponse(
                assistant_message=f"Loaded schema context. Visible tables include: {table_names}",
                intent="schema_question",
                sql=None,
                actions=[ChatAction(type="refresh_schema", label="Refresh schema")],
                safety=None,
                result_preview=None,
                provider_metadata=metadata,
            )

        metadata = self.router.build_metadata(
            provider_mode=provider_mode,
            selected_provider=self.router.select_provider_name("chat", payload.providerMode),
        )
        return ChatMessageResponse(
            assistant_message="Ask me to generate SQL, explain a query, fix an error, validate safety, run a read-only query, inspect schema, or summarize results.",
            intent="general_help",
            sql=None,
            actions=[ChatAction(type="show_help", label="Show commands")],
            safety=None,
            result_preview=None,
            provider_metadata=metadata,
        )

    def _detect_intent(self, message: str, current_sql: str) -> IntentMatch:
        trimmed = message.strip()
        lowered = trimmed.lower()
        if lowered.startswith("/schema") or "schema" in lowered or "table" in lowered and "related" in lowered:
            return IntentMatch("schema_question", trimmed)
        if lowered.startswith("/explain") or ("explain" in lowered and current_sql):
            return IntentMatch("sql_explain", trimmed.replace("/explain", "", 1).strip() or current_sql)
        if lowered.startswith("/fix") or "error" in lowered or "does not exist" in lowered:
            return IntentMatch("sql_fix", trimmed)
        if lowered.startswith("/validate") or "validate" in lowered:
            return IntentMatch("sql_validate", trimmed.replace("/validate", "", 1).strip() or current_sql)
        if lowered.startswith("/run") or "run this" in lowered or "execute" in lowered:
            return IntentMatch("sql_run", trimmed.replace("/run", "", 1).strip() or current_sql)
        if lowered.startswith("/optimize") or "slow" in lowered or "optimiz" in lowered:
            return IntentMatch("sql_optimize", trimmed.replace("/optimize", "", 1).strip() or current_sql)
        if lowered.startswith("/summarize"):
            return IntentMatch("result_summary", trimmed)
        if lowered.startswith("/generate") or lowered.startswith("show me") or lowered.startswith("generate") or lowered.startswith("write sql"):
            return IntentMatch("sql_generate", trimmed.replace("/generate", "", 1).strip() or trimmed)
        if current_sql and ("select " in current_sql.lower() or trimmed.upper().startswith("SELECT")):
            return IntentMatch("sql_explain", current_sql)
        return IntentMatch("general_help", trimmed)

    def _actions_for_sql(self) -> list[ChatAction]:
        return [
            ChatAction(type="copy_sql", label="Copy SQL"),
            ChatAction(type="validate_sql", label="Validate SQL"),
            ChatAction(type="run_readonly", label="Run read-only"),
        ]
