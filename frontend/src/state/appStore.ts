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
  warnings?: string[];
}

export interface AppState {
  demoMode: boolean;
  backendOnline: boolean;
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
    demoMode: false,
    backendOnline: false,
    providerMode: "auto",
    databaseUrl: "",
    currentSql: "",
    chat: [
      {
        id: "welcome",
        role: "assistant",
        message:
          "Ask for SQL generation, explanation, fixes, schema help, read-only execution, or result summaries. Generated SQL stays review-first and never auto-runs unless you explicitly enable it.",
      },
    ],
    selectedSchemas: [],
    selectedTables: [],
    autoRun: false,
  };
}
