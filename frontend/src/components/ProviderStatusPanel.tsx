import type { LLMStatusResponse, ProviderMode } from "../api/types";

interface ProviderStatusPanelProps {
  providerMode: ProviderMode;
  status?: LLMStatusResponse;
  lastProvider?: string;
  onChangeMode: (mode: ProviderMode) => void;
  onTestOpenAI: () => Promise<void>;
  onTestLocal: () => Promise<void>;
}

export function ProviderStatusPanel({
  providerMode,
  status,
  lastProvider,
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
      </div>
      <label className="field-label">
        Provider mode
        <select value={providerMode} onChange={(e) => onChangeMode(e.target.value as ProviderMode)}>
          <option value="auto">Auto</option>
          <option value="openai">OpenAI</option>
          <option value="local">Local</option>
          <option value="fallback">Fallback</option>
        </select>
      </label>
      {status ? (
        <div className="status-grid">
          <div>OpenAI: {status.openai_available ? "Ready" : "Unavailable"}</div>
          <div>Local: {status.local_available ? `Ready (${status.local_model})` : "Unavailable"}</div>
          <div>Fallback: Ready</div>
          <div>Router now: {status.effective_mode}</div>
          {lastProvider ? <div>Last response: {lastProvider}</div> : null}
        </div>
      ) : null}
      <div className="button-row">
        <button className="secondary-button" onClick={onTestOpenAI}>
          Test OpenAI
        </button>
        <button className="secondary-button" onClick={onTestLocal}>
          Test Local
        </button>
      </div>
    </div>
  );
}
