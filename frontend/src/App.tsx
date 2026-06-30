import { useEffect, useState } from "react";

import {
  connectTest,
  explainSql,
  fixSql,
  generateSql,
  getChatCommands,
  getHealth,
  getLLMStatus,
  getSchema,
  optimizeSql,
  runReadonly,
  sendChatMessage,
  summarizeResult,
  testLocal,
  testOpenAI,
  validateSql,
} from "./api/client";
import type { ChatCommandsResponse, ProviderMode } from "./api/types";
import { ChatPanel } from "./components/ChatPanel";
import { CommandHelp } from "./components/CommandHelp";
import { DatabaseConnectionPanel } from "./components/DatabaseConnectionPanel";
import { Layout } from "./components/Layout";
import { ProviderStatusPanel } from "./components/ProviderStatusPanel";
import { ResultTable } from "./components/ResultTable";
import { SafetyWarnings } from "./components/SafetyWarnings";
import { SchemaBrowser } from "./components/SchemaBrowser";
import { SqlEditorPanel } from "./components/SqlEditorPanel";
import { initialState } from "./state/appStore";

export default function App() {
  const [state, setState] = useState(initialState);
  const [commands, setCommands] = useState<ChatCommandsResponse>();
  const [banner, setBanner] = useState("Backend connection pending.");

  useEffect(() => {
    void boot();
  }, []);

  async function boot() {
    try {
      const [health, llm, cmds] = await Promise.all([getHealth(), getLLMStatus(), getChatCommands()]);
      setState((current) => ({ ...current, providerMode: health.provider_mode, llmStatus: llm }));
      setCommands(cmds);
      setBanner("Backend connected.");
    } catch (error) {
      setBanner(`Backend unavailable: ${String(error)}`);
    }
  }

  async function handleConnect() {
    const connection = await connectTest(state.databaseUrl);
    setState((current) => ({ ...current, connection }));
    setBanner(connection.message);
  }

  async function handleLoadSchema() {
    const schema = await getSchema(state.databaseUrl, state.selectedSchemas);
    setState((current) => ({ ...current, schema }));
    setBanner(`Loaded ${schema.tables.length} table entries.`);
  }

  async function refreshStatus() {
    const llmStatus = await getLLMStatus();
    setState((current) => ({ ...current, llmStatus }));
  }

  async function handleSend(message: string) {
    setState((current) => ({
      ...current,
      chat: [...current.chat, { id: crypto.randomUUID(), role: "user", message }],
    }));
    const response = await sendChatMessage({
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
          id: crypto.randomUUID(),
          role: "assistant",
          message: response.assistant_message,
          sql: response.sql,
          actions: response.actions,
          provider: response.provider_metadata.selected_provider,
        },
      ],
    }));
    setBanner(`Intent: ${response.intent}`);
    await refreshStatus();
  }

  async function handleValidate() {
    const validation = await validateSql(state.currentSql);
    setState((current) => ({ ...current, validation }));
    setBanner("SQL validated.");
  }

  async function handleExplain() {
    const result = await explainSql({ sql: state.currentSql, providerMode: state.providerMode });
    setState((current) => ({
      ...current,
      lastTask: result,
      validation: result.validation ?? current.validation,
      chat: [
        ...current.chat,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          message: result.content,
          sql: result.sql,
          provider: result.provider_metadata.selected_provider,
        },
      ],
    }));
  }

  async function handleFix() {
    const result = await fixSql({ sql: state.currentSql, error: "Fix this SQL for PostgreSQL", providerMode: state.providerMode });
    setState((current) => ({
      ...current,
      currentSql: result.sql ?? current.currentSql,
      lastTask: result,
      validation: result.validation ?? current.validation,
      chat: [
        ...current.chat,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          message: result.content,
          sql: result.sql,
          provider: result.provider_metadata.selected_provider,
        },
      ],
    }));
  }

  async function handleRun() {
    const result = await runReadonly({
      sql: state.currentSql,
      databaseUrl: state.databaseUrl || undefined,
      providerMode: state.providerMode,
    });
    setState((current) => ({ ...current, result }));
    setBanner(`Query finished in ${result.execution_time_ms} ms.`);
  }

  async function handleOptimize() {
    const result = await optimizeSql({ sql: state.currentSql, providerMode: state.providerMode });
    setState((current) => ({
      ...current,
      lastTask: result,
      validation: result.validation ?? current.validation,
      chat: [
        ...current.chat,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          message: result.content,
          sql: result.sql,
          provider: result.provider_metadata.selected_provider,
        },
      ],
    }));
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(state.currentSql);
    setBanner("SQL copied to clipboard.");
  }

  async function handleSummarize() {
    if (!state.result) {
      return;
    }
    const result = await summarizeResult({
      sql: state.currentSql,
      rows: state.result.rows,
      providerMode: state.providerMode,
    });
    setState((current) => ({
      ...current,
      lastTask: result,
      chat: [
        ...current.chat,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          message: result.content,
          provider: result.provider_metadata.selected_provider,
        },
      ],
    }));
  }

  async function handleAction(actionType: string) {
    if (actionType === "validate_sql") {
      await handleValidate();
    } else if (actionType === "run_readonly") {
      await handleRun();
    } else if (actionType === "copy_sql") {
      await handleCopy();
    } else if (actionType === "refresh_schema") {
      await handleLoadSchema();
    }
  }

  async function handleTestOpenAI() {
    const response = await testOpenAI(state.providerMode);
    setBanner(response.message);
  }

  async function handleTestLocal() {
    const response = await testLocal(state.providerMode);
    setBanner(response.message);
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
          <h1>SQL AI Copilot</h1>
          <p>Standalone PostgreSQL copilot for SQL editors and sidecar workflows.</p>
        </div>
        <div className="banner">{banner}</div>
      </header>
      <Layout
        sidebar={
          <>
            <DatabaseConnectionPanel
              databaseUrl={state.databaseUrl}
              connection={state.connection}
              onChange={(databaseUrl) => setState((current) => ({ ...current, databaseUrl }))}
              onConnect={handleConnect}
              onLoadSchema={handleLoadSchema}
            />
            <ProviderStatusPanel
              providerMode={state.providerMode}
              status={state.llmStatus}
              lastProvider={state.lastAssistant?.provider_metadata.selected_provider}
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
            onToggleAutoRun={(autoRun) => setState((current) => ({ ...current, autoRun }))}
            onSend={handleSend}
            onAction={handleAction}
          />
        }
        bottom={
          <div className="workspace-grid">
            <SqlEditorPanel
              sql={state.currentSql}
              onChange={(currentSql) => setState((current) => ({ ...current, currentSql }))}
              onValidate={handleValidate}
              onExplain={handleExplain}
              onFix={handleFix}
              onRun={handleRun}
              onOptimize={handleOptimize}
              onCopy={handleCopy}
            />
            <SafetyWarnings safety={state.validation} />
            <ResultTable result={state.result} onSummarize={handleSummarize} />
          </div>
        }
      />
    </div>
  );
}
