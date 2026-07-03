import type { ChatEntry } from "../state/appStore";
import { StatusBadge } from "./StatusBadge";

interface MessageBubbleProps {
  entry: ChatEntry;
  onAction: (actionType: string, sql?: string | null) => void;
}

export function MessageBubble({ entry, onAction }: MessageBubbleProps) {
  const actions =
    entry.actions?.length || !entry.sql
      ? entry.actions
      : [
          { type: "copy_sql", label: "Copy SQL" },
          { type: "validate_sql", label: "Validate" },
          { type: "explain_sql", label: "Explain" },
          { type: "run_readonly", label: "Run read-only" },
          { type: "optimize_sql", label: "Optimize" },
        ];

  return (
    <div className={`message-bubble ${entry.role}`}>
      <div className="message-meta">
        <div className="message-role">{entry.role === "user" ? "You" : "Copilot"}</div>
        {entry.provider ? <StatusBadge label={`Provider: ${entry.provider}`} tone={entry.provider === "fallback" ? "warning" : "success"} /> : null}
      </div>
      <div className="message-text">{entry.message}</div>
      {entry.sql ? <pre className="sql-block">{entry.sql}</pre> : null}
      {entry.warnings?.length ? (
        <ul className="warning-list compact">
          {entry.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      ) : null}
      {actions?.length ? (
        <div className="action-row">
          {actions.map((action) => (
            <button key={action.type} className="secondary-button" onClick={() => onAction(action.type, entry.sql)}>
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
