import type { ChatEntry } from "../state/appStore";
import { MessageBubble } from "./MessageBubble";
import { PromptInput } from "./PromptInput";
import { StatusBadge } from "./StatusBadge";

interface ChatPanelProps {
  messages: ChatEntry[];
  autoRun: boolean;
  demoMode: boolean;
  loading?: boolean;
  onToggleAutoRun: (value: boolean) => void;
  onSend: (message: string) => Promise<void>;
  onAction: (actionType: string, sql?: string | null) => void;
}

export function ChatPanel({ messages, autoRun, demoMode, loading, onToggleAutoRun, onSend, onAction }: ChatPanelProps) {
  return (
    <div className="panel chat-panel">
      <div className="panel-header">
        <div>
          <h2>Copilot Chat</h2>
          <p>Natural-language SQL copilot workflow.</p>
        </div>
        <div className="panel-actions">
          {demoMode ? <StatusBadge label="Demo Mode" tone="demo" /> : <StatusBadge label="Backend Mode" tone="success" />}
          <label className="toggle">
            <input type="checkbox" checked={autoRun} onChange={(e) => onToggleAutoRun(e.target.checked)} />
            Auto-run safe SQL
          </label>
        </div>
      </div>
      <div className="message-list">
        {messages.map((entry) => (
          <MessageBubble key={entry.id} entry={entry} onAction={onAction} />
        ))}
        {loading ? <div className="typing-state">Copilot is working...</div> : null}
      </div>
      <PromptInput disabled={loading} onSend={onSend} />
    </div>
  );
}
