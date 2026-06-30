import type { ChatEntry } from "../state/appStore";

interface MessageBubbleProps {
  entry: ChatEntry;
  onAction: (actionType: string) => void;
}

export function MessageBubble({ entry, onAction }: MessageBubbleProps) {
  return (
    <div className={`message-bubble ${entry.role}`}>
      <div className="message-role">{entry.role === "user" ? "You" : "Copilot"}</div>
      <div className="message-text">{entry.message}</div>
      {entry.sql ? <pre className="sql-block">{entry.sql}</pre> : null}
      {entry.provider ? <div className="message-provider">Provider: {entry.provider}</div> : null}
      {entry.actions?.length ? (
        <div className="action-row">
          {entry.actions.map((action) => (
            <button key={action.type} className="secondary-button" onClick={() => onAction(action.type)}>
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
