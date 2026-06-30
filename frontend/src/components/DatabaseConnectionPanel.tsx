import type { DatabaseConnectResponse } from "../api/types";

interface DatabaseConnectionPanelProps {
  databaseUrl: string;
  connection?: DatabaseConnectResponse;
  onChange: (value: string) => void;
  onConnect: () => Promise<void>;
  onLoadSchema: () => Promise<void>;
}

export function DatabaseConnectionPanel({
  databaseUrl,
  connection,
  onChange,
  onConnect,
  onLoadSchema,
}: DatabaseConnectionPanelProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Database</h2>
          <p>Connect with a PostgreSQL URL.</p>
        </div>
      </div>
      <textarea
        className="input-area"
        value={databaseUrl}
        onChange={(e) => onChange(e.target.value)}
        placeholder="postgresql://readonly_user:password@localhost:5432/my_database"
      />
      <div className="button-row">
        <button className="primary-button" onClick={onConnect}>
          Connect test
        </button>
        <button className="secondary-button" onClick={onLoadSchema}>
          Load schema
        </button>
      </div>
      {connection ? (
        <div className="status-card">
          <div>Status: {connection.ok ? "Connected" : "Unavailable"}</div>
          <div>{connection.masked_database_url}</div>
          {connection.server_version ? <div className="muted-text">{connection.server_version}</div> : null}
        </div>
      ) : null}
    </div>
  );
}
