import { useEffect, useMemo, useState } from "react";

import * as api from "./api/client";
import * as mockApi from "./api/mockApi";
import type { ChatCommandsResponse, ProviderMode, SQLTaskResponse } from "./api/types";
import { ChatPanel } from "./components/ChatPanel";
import { CommandHelp } from "./components/CommandHelp";
import { DatabaseConnectionPanel } from "./components/DatabaseConnectionPanel";
import { Layout } from "./components/Layout";
import { ProviderStatusPanel } from "./components/ProviderStatusPanel";
import { ResultTable } from "./components/ResultTable";
import { SafetyWarnings } from "./components/SafetyWarnings";
import { SchemaBrowser } from "./components/SchemaBrowser";
import { SqlEditorPanel } from "./components/SqlEditorPanel";
import { StatusBadge } from "./components/StatusBadge";
import { initialState } from "./state/appStore";
import { demoResult, demoSchema, demoValidation } from "./utils/sampleData";

const demoPreference = (import.meta.env.VITE_DEMO_MODE ?? "auto").toLowerCase();
const forceDemo = demoPreference === "true" || demoPreference === "demo";

function newId() {
  return crypto.randomUUID();
}

export default function App() {
  const [state, setState] = useState(initialState);
  const [commands, setCommands] = useState<ChatCommandsResponse>();
  const [banner, setBanner] = useState("Checking backend connection...");
  const [busy, setBusy] = useState(false);

  const activeApi = useMemo(() => (state.demoMode ? mockApi : api), [state.demoMode]);

  useEffect(() => {
    void boot();
  }, []);

  async function boot() {
    if (forceDemo) {
      await enterDemoMode("Demo mode forced by VITE_DEMO_MODE.");
      return;
    }

    try {
      const [health, llm, cmds] = await Promise.all([api.getHealth(), api.getLLMStatus(), api.getChatCommands()]);
      setState((current) => ({
        ...current,
        backendOnline: true,
        demoMode: false,
        providerMode: health.provider_mode,
        llmStatus: llm,
      }));
      setCommands(cmds);
      setBanner("Backend connected. Real PostgreSQL and provider calls go through FastAPI.");
    } catch (error) {
      await enterDemoMode(`Backend unavailable. Demo mode uses sample data. ${String(error)}`);
    }
  }

  async function enterDemoMode(reason: string) {
    const [health, llm, cmds] = await Promise.all([mockApi.getHealth(), mockApi.getLLMStatus(), mockApi.getChatCommands()]);
    setState((current) => ({
      ...current,
      backendOnline: false,
      demoMode: true,
      providerMode: health.provider_mode,
      llmStatus: llm,
      schema: demoSchema,
      validation: demoValidation,
      result: demoResult,
      currentSql: current.currentSql || demoResult.sql,
      chat: [
        ...current.chat,
        {
          id: newId(),
          role: "assistant",
          message: "Demo mode uses sample data. Connect a local backend to use a real PostgreSQL database.",
          provider: "fallback",
          warnings: ["No OpenAI key, Ollama server, or PostgreSQL database is required for this demo."],
        },
      ],
    }));
    setCommands(cmds);
    setBanner(reason);
  }

  async function runOperation(operation: () => Promise<void>) {
    setBusy(true);
    try {
      await operation();
    } catch (error) {
      setBanner(`Operation failed: ${String(error)}`);
    } finally {
      setBusy(false);
    }
  }

  async function handleConnect() {
    await runOperation(async () => {
      const connection = await activeApi.connectTest(state.databaseUrl);
      setState((current) => ({ ...current, connection }));
      setBanner(connection.message);
    });
  }

  async function handleLoadSchema() {
    await runOperation(async () => {
      const schema = await activeApi.getSchema(state.databaseUrl, state.selectedSchemas);
      setState((current) => ({ ...current, schema }));
      setBanner(schema.database_available ? `Loaded ${schema.tables.length} table entries.` : "Loaded demo schema sample.");
    });
  }

  async function refreshStatus() {
    const llmStatus = await activeApi.getLLMStatus();
    setState((current) => ({ ...current, llmStatus }));
  }

  async function handleSend(message: string) {
    setState((current) => ({
      ...current,
      chat: [...current.chat, { id: newId(), role: "user", message }],
    }));

    await runOperation(async () => {
      const response = await activeApi.sendChatMessage({
        message,
        databaseUrl: state.databaseUrl || undefined,
        currentSql: state.currentSql,
        selectedSchemas: state.selectedSchemas,
        selectedTables: state.selectedTables,
        providerMode: state.providerMode,
        autoRun: state.autoRun,
      });
      setState((current) => ({
        ...current,
        currentSql: response.sql ?? current.currentSql,
        validation: response.safety ?? current.validation,
        result: response.result_preview ?? current.result,
        lastAssistant: response,
        chat: [
          ...current.chat,
          {
            id: newId(),
            role: "assistant",
            message: response.assistant_message,
            sql: response.sql,
            actions: response.actions,
            provider: response.provider_metadata.selected_provider,
            warnings: response.provider_metadata.warnings,
          },
        ],
      }));
      setBanner(`Intent: ${response.intent}. Provider: ${response.provider_metadata.selected_provider}.`);
      await refreshStatus();
    });
  }

  async function handleValidate(sql = state.currentSql) {
    await runOperation(async () => {
      const validation = await activeApi.validateSql(sql);
      setState((current) => ({ ...current, currentSql: sql, validation }));
      setBanner(validation.is_readonly ? "SQL validated as read-only." : "SQL blocked by the safety layer.");
    });
  }

  async function addTaskResponse(result: SQLTaskResponse, fallbackSql = state.currentSql) {
    setState((current) => ({
      ...current,
      currentSql: result.sql ?? fallbackSql,
      lastTask: result,
      validation: result.validation ?? current.validation,
      chat: [
        ...current.chat,
        {
          id: newId(),
          role: "assistant",
          message: result.content,
          sql: result.sql,
          provider: result.provider_metadata.selected_provider,
          warnings: [...result.warnings, ...result.provider_metadata.warnings],
        },
      ],
    }));
    setBanner(`Provider: ${result.provider_metadata.selected_provider}.`);
  }

  async function handleExplain(sql = state.currentSql) {
    await runOperation(async () => {
      const result = await activeApi.explainSql({ sql, providerMode: state.providerMode });
      await addTaskResponse(result, sql);
    });
  }

  async function handleFix(sql = state.currentSql) {
    await runOperation(async () => {
      const result = await activeApi.fixSql({ sql, error: "Fix this SQL for PostgreSQL", providerMode: state.providerMode });
      await addTaskResponse(result, sql);
    });
  }

  async function handleRun(sql = state.currentSql) {
    await runOperation(async () => {
      const validation = await activeApi.validateSql(sql);
      if (!validation.is_valid || !validation.is_readonly) {
        setState((current) => ({ ...current, validation }));
        setBanner(validation.blocked_reason ?? "SQL was blocked before execution.");
        return;
      }
      const result = await activeApi.runReadonly({
        sql,
        databaseUrl: state.databaseUrl || undefined,
        providerMode: state.providerMode,
      });
      setState((current) => ({ ...current, currentSql: sql, validation, result }));
      setBanner(`Query finished in ${result.execution_time_ms} ms.`);
    });
  }

  async function handleOptimize(sql = state.currentSql) {
    await runOperation(async () => {
      const result = await activeApi.optimizeSql({ sql, providerMode: state.providerMode });
      await addTaskResponse(result, sql);
    });
  }

  async function handleCopy(sql = state.currentSql) {
    if (!sql.trim()) {
      return;
    }
    await navigator.clipboard.writeText(sql);
    setBanner("SQL copied to clipboard.");
  }

  async function handleSummarize() {
    if (!state.result) {
      return;
    }
    await runOperation(async () => {
      const result = await activeApi.summarizeResult({
        sql: state.currentSql,
        rows: state.result?.rows ?? [],
        providerMode: state.providerMode,
      });
      await addTaskResponse(result);
    });
  }

  async function handleAction(actionType: string, sql?: string | null) {
    const targetSql = sql || state.currentSql;
    if (sql) {
      setState((current) => ({ ...current, currentSql: sql }));
    }
    if (actionType === "validate_sql") {
      await handleValidate(targetSql);
    } else if (actionType === "run_readonly") {
      await handleRun(targetSql);
    } else if (actionType === "copy_sql") {
      await handleCopy(targetSql);
    } else if (actionType === "refresh_schema") {
      await handleLoadSchema();
    } else if (actionType === "explain_sql") {
      await handleExplain(targetSql);
    } else if (actionType === "optimize_sql") {
      await handleOptimize(targetSql);
    }
  }

  async function handleTestOpenAI() {
    await runOperation(async () => {
      const response = await activeApi.testOpenAI(state.providerMode);
      setBanner(response.message);
    });
  }

  async function handleTestLocal() {
    await runOperation(async () => {
      const response = await activeApi.testLocal(state.providerMode);
      setBanner(response.message);
    });
  }

  function toggleSelectedTable(tableName: string) {
    setState((current) => ({
      ...current,
      selectedTables: current.selectedTables.includes(tableName)
        ? current.selectedTables.filter((item) => item !== tableName)
        : [...current.selectedTables, tableName],
    }));
  }

  return (
    <div>
      <header className="topbar">
        <div>
          <div className="product-kicker">Standalone SQL sidecar</div>
          <h1>SQL AI Copilot</h1>
          <p>PostgreSQL-focused chat, safety validation, schema context, and read-only result previews.</p>
        </div>
        <div className="topbar-status">
          <StatusBadge label={state.demoMode ? "Demo Mode" : "Backend Mode"} tone={state.demoMode ? "demo" : "success"} />
          <StatusBadge label={`Provider: ${state.providerMode}`} tone={state.providerMode === "fallback" ? "warning" : "neutral"} />
          <div className="banner">{banner}</div>
        </div>
      </header>

      {state.demoMode ? (
        <div className="demo-banner">
          Demo mode uses sample data. Connect a local backend to use a real PostgreSQL database.
        </div>
      ) : null}

      <Layout
        sidebar={
          <>
            <DatabaseConnectionPanel
              databaseUrl={state.databaseUrl}
              connection={state.connection}
              demoMode={state.demoMode}
              loading={busy}
              onChange={(databaseUrl) => setState((current) => ({ ...current, databaseUrl }))}
              onConnect={handleConnect}
              onLoadSchema={handleLoadSchema}
            />
            <ProviderStatusPanel
              providerMode={state.providerMode}
              status={state.llmStatus}
              lastProvider={state.lastAssistant?.provider_metadata.selected_provider}
              backendOnline={state.backendOnline}
              demoMode={state.demoMode}
              loading={busy}
              onChangeMode={(providerMode: ProviderMode) => setState((current) => ({ ...current, providerMode }))}
              onTestOpenAI={handleTestOpenAI}
              onTestLocal={handleTestLocal}
            />
            <SchemaBrowser schema={state.schema} selectedTables={state.selectedTables} onToggleTable={toggleSelectedTable} />
            <CommandHelp commands={commands} />
          </>
        }
        main={
          <ChatPanel
            messages={state.chat}
            autoRun={state.autoRun}
            demoMode={state.demoMode}
            loading={busy}
            onToggleAutoRun={(autoRun) => setState((current) => ({ ...current, autoRun }))}
            onSend={handleSend}
            onAction={handleAction}
          />
        }
        bottom={
          <div className="workspace-grid">
            <SqlEditorPanel
              sql={state.currentSql}
              safety={state.validation}
              loading={busy}
              onChange={(currentSql) => setState((current) => ({ ...current, currentSql }))}
              onValidate={handleValidate}
              onExplain={handleExplain}
              onFix={handleFix}
              onRun={handleRun}
              onOptimize={handleOptimize}
              onCopy={handleCopy}
              onClear={() => setState((current) => ({ ...current, currentSql: "", validation: undefined }))}
            />
            <SafetyWarnings safety={state.validation} />
            <ResultTable result={state.result} onSummarize={handleSummarize} />
          </div>
        }
      />
    </div>
  );
}
