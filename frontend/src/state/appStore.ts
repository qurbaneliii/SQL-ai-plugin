import type {
  ChatMessageResponse,
  DatabaseConnectResponse,
  LLMStatusResponse,
  ProviderMode,
  QueryExecutionResponse,
  SchemaSummaryResponse,
  SQLTaskResponse,
  SQLValidationResponse,
} from "../api/types";

export interface ChatEntry {
  id: string;
  role: "user" | "assistant";
  message: string;
  sql?: string | null;
  actions?: Array<{ type: string; label: string }>;
  provider?: string;
}

export interface AppState {
  providerMode: ProviderMode;
  databaseUrl: string;
  connection?: DatabaseConnectResponse;
  llmStatus?: LLMStatusResponse;
  schema?: SchemaSummaryResponse;
  currentSql: string;
  validation?: SQLValidationResponse;
  result?: QueryExecutionResponse;
  lastTask?: SQLTaskResponse;
  chat: ChatEntry[];
  selectedSchemas: string[];
  selectedTables: string[];
  autoRun: boolean;
  lastAssistant?: ChatMessageResponse;
}

export function initialState(): AppState {
  return {
    providerMode: "auto",
    databaseUrl: "",
    currentSql: "",
    chat: [
      {
        id: "welcome",
        role: "assistant",
        message: "Ask for SQL generation, explanation, fixes, schema help, read-only execution, or result summaries.",
      },
    ],
    selectedSchemas: [],
    selectedTables: [],
    autoRun: false,
  };
}
