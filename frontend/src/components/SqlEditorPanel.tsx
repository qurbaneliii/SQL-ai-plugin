import type { SQLValidationResponse } from "../api/types";
import { StatusBadge } from "./StatusBadge";

interface SqlEditorPanelProps {
  sql: string;
  safety?: SQLValidationResponse;
  loading?: boolean;
  onChange: (value: string) => void;
  onValidate: () => Promise<void>;
  onExplain: () => Promise<void>;
  onFix: () => Promise<void>;
  onRun: () => Promise<void>;
  onOptimize: () => Promise<void>;
  onCopy: () => Promise<void>;
  onClear: () => void;
}

export function SqlEditorPanel({
  sql,
  safety,
  loading,
  onChange,
  onValidate,
  onExplain,
  onFix,
  onRun,
  onOptimize,
  onCopy,
  onClear,
}: SqlEditorPanelProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>SQL Editor</h2>
          <p>Review generated SQL before execution.</p>
        </div>
        {safety ? <StatusBadge label={`${safety.risk_level} risk`} tone={safety.risk_level === "low" ? "success" : safety.risk_level === "medium" ? "warning" : "danger"} /> : null}
      </div>
      <textarea className="sql-editor" value={sql} onChange={(e) => onChange(e.target.value)} placeholder="Generated or pasted PostgreSQL appears here..." disabled={loading} />
      {safety ? (
        <div className="editor-validation">
          <span>{safety.is_readonly ? "Read-only" : "Not read-only"}</span>
          <span>{safety.is_valid ? "Valid" : "Blocked"}</span>
          {safety.blocked_reason ? <span>{safety.blocked_reason}</span> : null}
        </div>
      ) : null}
      <div className="button-row wrap">
        <button className="primary-button" onClick={onValidate} disabled={loading || !sql.trim()}>
          Validate
        </button>
        <button className="secondary-button" onClick={onExplain} disabled={loading || !sql.trim()}>
          Explain
        </button>
        <button className="secondary-button" onClick={onFix} disabled={loading}>
          Fix
        </button>
        <button className="primary-button" onClick={onRun} disabled={loading || !sql.trim()}>
          Run read-only
        </button>
        <button className="secondary-button" onClick={onOptimize} disabled={loading || !sql.trim()}>
          Optimize
        </button>
        <button className="secondary-button" onClick={onCopy} disabled={!sql.trim()}>
          Copy SQL
        </button>
        <button className="secondary-button" onClick={onClear} disabled={loading || !sql.trim()}>
          Clear
        </button>
      </div>
    </div>
  );
}
