export type ProviderMode = "auto" | "openai" | "local" | "fallback";

export interface ProviderMetadata {
  provider_mode: ProviderMode;
  selected_provider: "openai" | "local" | "fallback";
  model: string;
  fallback_used: boolean;
  warnings: string[];
}

export interface HealthResponse {
  status: string;
  provider_mode: ProviderMode;
  local_llm_enabled: boolean;
  database_configured: boolean;
}

export interface LLMStatusResponse {
  configured_mode: ProviderMode;
  effective_mode: "openai" | "local" | "fallback";
  openai_available: boolean;
  local_available: boolean;
  fallback_available: boolean;
  openai_model: string;
  local_model: string;
  local_provider: string;
  router_preferences: Record<string, string[]>;
}

export interface ProviderTestResponse {
  ok: boolean;
  message: string;
  provider_metadata: ProviderMetadata;
}

export interface DatabaseConnectResponse {
  ok: boolean;
  message: string;
  masked_database_url?: string | null;
  server_version?: string | null;
}

export interface ColumnInfo {
  name: string;
  data_type: string;
  is_nullable: boolean;
  default?: string | null;
  comment?: string | null;
}

export interface ForeignKeyInfo {
  name: string;
  column_names: string[];
  referenced_schema: string;
  referenced_table: string;
  referenced_columns: string[];
}

export interface IndexInfo {
  name: string;
  definition: string;
}

export interface TableInfo {
  schema_name: string;
  table_name: string;
  table_type: string;
  columns: ColumnInfo[];
  primary_key: string[];
  foreign_keys: ForeignKeyInfo[];
  indexes: IndexInfo[];
  comment?: string | null;
  approximate_row_count?: number | null;
  sensitive_columns: string[];
}

export interface EnumInfo {
  schema_name: string;
  type_name: string;
  values: string[];
}

export interface SchemaSummaryResponse {
  database_available: boolean;
  masked_database_url?: string | null;
  schemas: string[];
  tables: TableInfo[];
  enum_types: EnumInfo[];
  truncated: boolean;
  max_tables: number;
}

export interface SQLValidationResponse {
  is_valid: boolean;
  is_readonly: boolean;
  blocked_reason?: string | null;
  risk_level: "low" | "medium" | "high";
  detected_statement_type: string;
  referenced_tables: string[];
  referenced_columns: string[];
  warnings: string[];
  normalized_sql?: string | null;
  suggested_sql?: string | null;
}

export interface SQLTaskResponse {
  content: string;
  sql?: string | null;
  warnings: string[];
  provider_metadata: ProviderMetadata;
  validation?: SQLValidationResponse | null;
}

export interface QueryExecutionResponse {
  sql: string;
  normalized_sql: string;
  row_limit: number;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  truncated: boolean;
  execution_time_ms: number;
  warnings: string[];
  provider_metadata?: ProviderMetadata | null;
}

export interface ChatAction {
  type: string;
  label: string;
}

export interface ChatMessageResponse {
  assistant_message: string;
  intent: string;
  sql?: string | null;
  actions: ChatAction[];
  safety?: SQLValidationResponse | null;
  result_preview?: QueryExecutionResponse | null;
  provider_metadata: ProviderMetadata;
}

export interface ChatCommandsResponse {
  commands: Array<{ command: string; description: string }>;
}
