import { useState } from "react";

import type { DatabaseConnectResponse } from "../api/types";
import { compactDatabaseUrl } from "../utils/formatters";
import { StatusBadge } from "./StatusBadge";

interface DatabaseConnectionPanelProps {
  databaseUrl: string;
  connection?: DatabaseConnectResponse;
  demoMode: boolean;
  loading?: boolean;
  onChange: (value: string) => void;
  onConnect: () => Promise<void>;
  onLoadSchema: () => Promise<void>;
}

export function DatabaseConnectionPanel({
  databaseUrl,
  connection,
  demoMode,
  loading,
  onChange,
  onConnect,
  onLoadSchema,
}: DatabaseConnectionPanelProps) {
  const [showUrl, setShowUrl] = useState(false);

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Database</h2>
          <p>Connect with a PostgreSQL URL.</p>
        </div>
        {connection ? <StatusBadge label={connection.ok ? "Connected" : "Unavailable"} tone={connection.ok ? "success" : "warning"} /> : null}
      </div>
      <label className="field-label">
        PostgreSQL URL
        <input
          className="connection-input"
          type={showUrl ? "text" : "password"}
          value={databaseUrl}
          onChange={(e) => onChange(e.target.value)}
          placeholder="postgresql://readonly_user:password@localhost:5432/my_database"
          disabled={loading}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      <div className="button-row slim">
        <button className="chip-button" type="button" onClick={() => setShowUrl((value) => !value)}>
          {showUrl ? "Hide URL" : "Show URL"}
        </button>
        <span className="muted-text">{databaseUrl ? compactDatabaseUrl(databaseUrl.replace(/:[^:@/]+@/, ":****@")) : "No URL entered"}</span>
      </div>
      <p className="security-note">
        Database URLs are sent only to your local/backend API. They are not stored in localStorage and are not sent directly to OpenAI.
      </p>
      <div className="button-row">
        <button className="primary-button" onClick={onConnect} disabled={loading}>
          Connect test
        </button>
        <button className="secondary-button" onClick={onLoadSchema} disabled={loading}>
          Load schema
        </button>
      </div>
      {demoMode ? (
        <div className="inline-alert">Demo mode uses sample schema only. Start the backend to test a real PostgreSQL database.</div>
      ) : null}
      {connection ? (
        <div className="status-card">
          <div>{connection.message}</div>
          <div>{compactDatabaseUrl(connection.masked_database_url)}</div>
          {connection.server_version ? <div className="muted-text">{connection.server_version}</div> : null}
        </div>
      ) : null}
    </div>
  );
}
