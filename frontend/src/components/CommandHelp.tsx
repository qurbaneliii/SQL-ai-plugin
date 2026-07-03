import type { ChatCommandsResponse } from "../api/types";
import { EmptyState } from "./EmptyState";

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
      {!commands ? <EmptyState title="Loading commands" /> : null}
      {commands?.commands.map((item) => (
        <div className="command-row" key={item.command}>
          <code>{item.command}</code>
          <span>{item.description}</span>
        </div>
      ))}
    </div>
  );
}
