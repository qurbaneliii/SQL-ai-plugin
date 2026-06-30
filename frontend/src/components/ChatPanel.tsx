import { useState } from "react";

import type { ChatEntry } from "../state/appStore";
import { MessageBubble } from "./MessageBubble";

interface ChatPanelProps {
  messages: ChatEntry[];
  autoRun: boolean;
  onToggleAutoRun: (value: boolean) => void;
  onSend: (message: string) => Promise<void>;
  onAction: (actionType: string) => void;
}

export function ChatPanel({ messages, autoRun, onToggleAutoRun, onSend, onAction }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);

  async function submit() {
    if (!message.trim()) {
      return;
    }
    setSending(true);
    try {
      await onSend(message);
      setMessage("");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="panel chat-panel">
      <div className="panel-header">
        <div>
          <h2>Chat</h2>
          <p>Natural-language SQL copilot workflow.</p>
        </div>
        <label className="toggle">
          <input type="checkbox" checked={autoRun} onChange={(e) => onToggleAutoRun(e.target.checked)} />
          Auto-run safe SQL
        </label>
      </div>
      <div className="message-list">
        {messages.map((entry) => (
          <MessageBubble key={entry.id} entry={entry} onAction={onAction} />
        ))}
      </div>
      <div className="chat-input-row">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Try: Show me the top 10 customers by revenue"
        />
        <button className="primary-button" onClick={submit} disabled={sending}>
          {sending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
