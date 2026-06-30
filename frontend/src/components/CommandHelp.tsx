import type { ChatCommandsResponse } from "../api/types";

interface CommandHelpProps {
  commands?: ChatCommandsResponse;
}

export function CommandHelp({ commands }: CommandHelpProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Commands</h2>
          <p>Quick intent routing helpers.</p>
        </div>
      </div>
      {!commands ? <div className="empty-state">Loading command help...</div> : null}
      {commands?.commands.map((item) => (
        <div className="command-row" key={item.command}>
          <code>{item.command}</code>
          <span>{item.description}</span>
        </div>
      ))}
    </div>
  );
}
