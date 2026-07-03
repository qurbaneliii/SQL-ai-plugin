import { useState } from "react";

const examplePrompts = [
  "Generate SQL for top 10 customers by revenue",
  "Explain this query",
  "Fix this PostgreSQL error",
  "Optimize this slow query",
  "Show likely relationships in my schema",
  "Summarize this query result",
];

interface PromptInputProps {
  disabled?: boolean;
  onSend: (message: string) => Promise<void>;
}

export function PromptInput({ disabled, onSend }: PromptInputProps) {
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);

  async function submit(value = message) {
    const trimmed = value.trim();
    if (!trimmed || sending || disabled) {
      return;
    }
    setSending(true);
    try {
      await onSend(trimmed);
      setMessage("");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="prompt-input">
      <div className="prompt-examples" aria-label="Example prompts">
        {examplePrompts.map((prompt) => (
          <button key={prompt} className="chip-button" type="button" onClick={() => void submit(prompt)} disabled={sending || disabled}>
            {prompt}
          </button>
        ))}
      </div>
      <div className="chat-input-row">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask for PostgreSQL generation, explanation, fixes, optimization, schema help, or result summaries..."
          disabled={sending || disabled}
          onKeyDown={(event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
              void submit();
            }
          }}
        />
        <button className="primary-button" type="button" onClick={() => void submit()} disabled={sending || disabled}>
          {sending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}
