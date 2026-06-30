import type {
  ChatCommandsResponse,
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

const API_BASE = "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getHealth() {
  return request<HealthResponse>("/health");
}

export function getLLMStatus() {
  return request<LLMStatusResponse>("/api/llm/status");
}

export function testOpenAI(providerMode?: ProviderMode) {
  return request<ProviderTestResponse>("/api/llm/test-openai", {
    method: "POST",
    body: JSON.stringify({ providerMode }),
  });
}

export function testLocal(providerMode?: ProviderMode) {
  return request<ProviderTestResponse>("/api/llm/test-local", {
    method: "POST",
    body: JSON.stringify({ providerMode }),
  });
}

export function connectTest(databaseUrl: string) {
  return request<DatabaseConnectResponse>("/api/db/connect-test", {
    method: "POST",
    body: JSON.stringify({ databaseUrl }),
  });
}

export function getSchema(databaseUrl: string, selectedSchemas: string[] = []) {
  return request<SchemaSummaryResponse>("/api/db/schema", {
    method: "POST",
    body: JSON.stringify({ databaseUrl, selectedSchemas }),
  });
}

export function validateSql(sql: string) {
  return request<SQLValidationResponse>("/api/sql/validate", {
    method: "POST",
    body: JSON.stringify({ sql, allow_write: false }),
  });
}

export function generateSql(payload: {
  prompt: string;
  databaseUrl?: string;
  selectedSchemas?: string[];
  selectedTables?: string[];
  providerMode?: ProviderMode;
}) {
  return request<SQLTaskResponse>("/api/sql/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function explainSql(payload: { sql: string; providerMode?: ProviderMode }) {
  return request<SQLTaskResponse>("/api/sql/explain", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fixSql(payload: { sql?: string; error?: string; providerMode?: ProviderMode }) {
  return request<SQLTaskResponse>("/api/sql/fix", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function runReadonly(payload: { sql: string; databaseUrl?: string; rowLimit?: number; providerMode?: ProviderMode }) {
  return request<QueryExecutionResponse>("/api/sql/run-readonly", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function optimizeSql(payload: { sql: string; providerMode?: ProviderMode }) {
  return request<SQLTaskResponse>("/api/sql/optimize", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function summarizeResult(payload: {
  sql: string;
  rows: Record<string, unknown>[];
  prompt?: string;
  providerMode?: ProviderMode;
}) {
  return request<SQLTaskResponse>("/api/result/summarize", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function sendChatMessage(payload: {
  message: string;
  databaseUrl?: string;
  currentSql?: string;
  selectedSchemas?: string[];
  selectedTables?: string[];
  providerMode?: ProviderMode;
  autoRun?: boolean;
}) {
  return request<ChatMessageResponse>("/api/chat/message", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getChatCommands() {
  return request<ChatCommandsResponse>("/api/chat/commands");
}
