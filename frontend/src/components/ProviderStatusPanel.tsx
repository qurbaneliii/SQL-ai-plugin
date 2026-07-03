import type { LLMStatusResponse, ProviderMode } from "../api/types";
import { StatusBadge } from "./StatusBadge";

interface ProviderStatusPanelProps {
  providerMode: ProviderMode;
  status?: LLMStatusResponse;
  lastProvider?: string;
  backendOnline: boolean;
  demoMode: boolean;
  loading?: boolean;
  onChangeMode: (mode: ProviderMode) => void;
  onTestOpenAI: () => Promise<void>;
  onTestLocal: () => Promise<void>;
}

export function ProviderStatusPanel({
  providerMode,
  status,
  lastProvider,
  backendOnline,
  demoMode,
  loading,
  onChangeMode,
  onTestOpenAI,
  onTestLocal,
}: ProviderStatusPanelProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Providers</h2>
          <p>Hybrid routing through the backend.</p>
        </div>
        <StatusBadge label={backendOnline ? "Backend Online" : "Backend Offline"} tone={backendOnline ? "success" : "warning"} />
      </div>
      <label className="field-label">
        Provider mode
        <select value={providerMode} onChange={(e) => onChangeMode(e.target.value as ProviderMode)} disabled={loading}>
          <option value="auto">Auto</option>
          <option value="openai">OpenAI</option>
          <option value="local">Local</option>
          <option value="fallback">Fallback</option>
        </select>
      </label>
      {status ? (
        <div className="status-grid">
          <div><span>OpenAI</span><StatusBadge label={status.openai_available ? "Ready" : "Unavailable"} tone={status.openai_available ? "success" : "neutral"} /></div>
          <div><span>Local Ollama</span><StatusBadge label={status.local_available ? `Ready: ${status.local_model}` : "Unavailable"} tone={status.local_available ? "success" : "neutral"} /></div>
          <div><span>Fallback</span><StatusBadge label={status.fallback_available ? "Ready" : "Unavailable"} tone={status.fallback_available ? "success" : "danger"} /></div>
          <div><span>Router now</span><StatusBadge label={status.effective_mode} tone={status.effective_mode === "fallback" ? "warning" : "success"} /></div>
          {lastProvider ? <div><span>Last response</span><StatusBadge label={lastProvider} tone={lastProvider === "fallback" ? "warning" : "success"} /></div> : null}
        </div>
      ) : null}
      {demoMode || status?.effective_mode === "fallback" ? (
        <div className="inline-alert">Fallback/demo mode is deterministic and safe, but not provider-backed generation.</div>
      ) : null}
      <div className="button-row">
        <button className="secondary-button" onClick={onTestOpenAI} disabled={loading}>
          Test OpenAI
        </button>
        <button className="secondary-button" onClick={onTestLocal} disabled={loading}>
          Test Local
        </button>
      </div>
    </div>
  );
}
