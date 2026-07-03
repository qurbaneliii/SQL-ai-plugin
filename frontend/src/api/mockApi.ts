import type {
  ChatMessageResponse,
  DatabaseConnectResponse,
  HealthResponse,
  LLMStatusResponse,
  ProviderMode,
  ProviderTestResponse,
  QueryExecutionResponse,
  SchemaSummaryResponse,
  SQLTaskResponse,
  SQLValidationResponse,
} from "./types";
import { demoCommands, demoProviderMetadata, demoResult, demoSchema, demoSql, demoValidation } from "../utils/sampleData";

const wait = (ms = 240) => new Promise((resolve) => window.setTimeout(resolve, ms));

function provider(providerMode?: ProviderMode) {
  return {
    ...demoProviderMetadata,
    provider_mode: providerMode ?? "fallback",
  };
}

export async function getHealth(): Promise<HealthResponse> {
  await wait(120);
  return {
    status: "demo",
    provider_mode: "fallback",
    local_llm_enabled: false,
    database_configured: false,
  };
}

export async function getLLMStatus(): Promise<LLMStatusResponse> {
  await wait(120);
  return {
    configured_mode: "fallback",
    effective_mode: "fallback",
    openai_available: false,
    local_available: false,
    fallback_available: true,
    openai_model: "backend-only",
    local_model: "not connected",
    local_provider: "ollama",
    router_preferences: {
      auto: ["openai", "local", "fallback"],
      fallback: ["fallback"],
    },
  };
}

export async function testOpenAI(providerMode?: ProviderMode): Promise<ProviderTestResponse> {
  await wait();
  return {
    ok: false,
    message: "Demo mode cannot test OpenAI. Start the FastAPI backend with OPENAI_API_KEY configured.",
    provider_metadata: provider(providerMode),
  };
}

export async function testLocal(providerMode?: ProviderMode): Promise<ProviderTestResponse> {
  await wait();
  return {
    ok: false,
    message: "Demo mode cannot test Ollama. Start the backend and local model server to test local LLMs.",
    provider_metadata: provider(providerMode),
  };
}

export async function connectTest(): Promise<DatabaseConnectResponse> {
  await wait();
  return {
    ok: false,
    message: "Demo mode uses sample data and is not connected to PostgreSQL.",
    masked_database_url: null,
    server_version: null,
  };
}

export async function getSchema(): Promise<SchemaSummaryResponse> {
  await wait();
  return demoSchema;
}

export async function validateSql(sql: string): Promise<SQLValidationResponse> {
  await wait();
  const destructive = /\b(drop|delete|update|insert|alter|truncate|create|grant|revoke)\b/i.test(sql);
  if (destructive) {
    return {
      ...demoValidation,
      is_valid: false,
      is_readonly: false,
      risk_level: "high",
      detected_statement_type: "WRITE_OR_DDL",
      blocked_reason: "Demo validator blocks destructive or write SQL.",
      warnings: ["Only read-only SELECT statements can run through the copilot workflow."],
      normalized_sql: sql,
    };
  }
  return {
    ...demoValidation,
    normalized_sql: sql || demoSql,
  };
}

export async function generateSql(payload: {
  prompt: string;
  providerMode?: ProviderMode;
}): Promise<SQLTaskResponse> {
  await wait();
  return {
    content: `Generated PostgreSQL for: "${payload.prompt}". The demo uses customers and orders sample tables.`,
    sql: demoSql,
    warnings: ["Demo mode response. Connect the backend for provider-backed generation."],
    provider_metadata: provider(payload.providerMode),
    validation: demoValidation,
  };
}

export async function explainSql(payload: { sql: string; providerMode?: ProviderMode }): Promise<SQLTaskResponse> {
  await wait();
  return {
    content:
      "This query joins customers to orders, groups revenue by customer, sorts the highest totals first, and limits the output to ten rows.",
    sql: payload.sql || demoSql,
    warnings: ["Demo explanation based on sample schema."],
    provider_metadata: provider(payload.providerMode),
    validation: await validateSql(payload.sql || demoSql),
  };
}

export async function fixSql(payload: { sql?: string; error?: string; providerMode?: ProviderMode }): Promise<SQLTaskResponse> {
  await wait();
  return {
    content: `Demo fix prepared for PostgreSQL${payload.error ? `: ${payload.error}` : "."}`,
    sql: payload.sql?.trim() ? payload.sql : demoSql,
    warnings: ["Review generated SQL before running it against a real database."],
    provider_metadata: provider(payload.providerMode),
    validation: await validateSql(payload.sql || demoSql),
  };
}

export async function runReadonly(payload: { sql: string; providerMode?: ProviderMode }): Promise<QueryExecutionResponse> {
  await wait();
  return {
    ...demoResult,
    sql: payload.sql || demoSql,
    normalized_sql: payload.sql || demoSql,
    provider_metadata: provider(payload.providerMode),
  };
}

export async function optimizeSql(payload: { sql: string; providerMode?: ProviderMode }): Promise<SQLTaskResponse> {
  await wait();
  return {
    content:
      "Optimization notes: keep indexes on orders.customer_id and consider a covering index for ordered_at when adding date filters.",
    sql: payload.sql || demoSql,
    warnings: ["Demo optimization advice is illustrative."],
    provider_metadata: provider(payload.providerMode),
    validation: await validateSql(payload.sql || demoSql),
  };
}

export async function summarizeResult(payload: {
  sql: string;
  rows: Record<string, unknown>[];
  providerMode?: ProviderMode;
}): Promise<SQLTaskResponse> {
  await wait();
  return {
    content: `Demo summary: ${payload.rows.length || demoResult.rows.length} rows show the highest revenue customers in descending order.`,
    sql: payload.sql,
    warnings: ["Demo summary uses table-preview data only."],
    provider_metadata: provider(payload.providerMode),
    validation: await validateSql(payload.sql || demoSql),
  };
}

export async function sendChatMessage(payload: {
  message: string;
  currentSql?: string;
  providerMode?: ProviderMode;
  autoRun?: boolean;
}): Promise<ChatMessageResponse> {
  await wait(360);
  const message = payload.message.toLowerCase();
  const sql = message.includes("explain") || message.includes("fix") || message.includes("optimize") ? payload.currentSql || demoSql : demoSql;
  return {
    assistant_message:
      "Demo mode uses sample ecommerce tables. Here is safe read-only PostgreSQL you can review, validate, copy, or run as a sample preview.",
    intent: message.includes("explain") ? "sql_explain" : "sql_generate",
    sql,
    actions: [
      { type: "copy_sql", label: "Copy SQL" },
      { type: "validate_sql", label: "Validate" },
      { type: "explain_sql", label: "Explain" },
      { type: "run_readonly", label: "Run read-only" },
      { type: "optimize_sql", label: "Optimize" },
    ],
    safety: await validateSql(sql),
    result_preview: payload.autoRun ? await runReadonly({ sql, providerMode: payload.providerMode }) : null,
    provider_metadata: provider(payload.providerMode),
  };
}

export async function getChatCommands() {
  await wait(120);
  return demoCommands;
}
