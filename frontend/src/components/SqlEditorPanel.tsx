interface SqlEditorPanelProps {
  sql: string;
  onChange: (value: string) => void;
  onValidate: () => Promise<void>;
  onExplain: () => Promise<void>;
  onFix: () => Promise<void>;
  onRun: () => Promise<void>;
  onOptimize: () => Promise<void>;
  onCopy: () => Promise<void>;
}

export function SqlEditorPanel({
  sql,
  onChange,
  onValidate,
  onExplain,
  onFix,
  onRun,
  onOptimize,
  onCopy,
}: SqlEditorPanelProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>SQL Editor</h2>
          <p>Review generated SQL before execution.</p>
        </div>
      </div>
      <textarea className="sql-editor" value={sql} onChange={(e) => onChange(e.target.value)} />
      <div className="button-row wrap">
        <button className="primary-button" onClick={onValidate}>
          Validate
        </button>
        <button className="secondary-button" onClick={onExplain}>
          Explain
        </button>
        <button className="secondary-button" onClick={onFix}>
          Fix
        </button>
        <button className="primary-button" onClick={onRun}>
          Run read-only
        </button>
        <button className="secondary-button" onClick={onOptimize}>
          Optimize
        </button>
        <button className="secondary-button" onClick={onCopy}>
          Copy SQL
        </button>
      </div>
    </div>
  );
}
