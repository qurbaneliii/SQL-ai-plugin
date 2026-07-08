import type { SQLValidationResponse } from "../api/types";
import { EmptyState } from "./EmptyState";
import { StatusBadge } from "./StatusBadge";

interface SafetyWarningsProps {
  safety?: SQLValidationResponse;
}

export function SafetyWarnings({ safety }: SafetyWarningsProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Safety</h2>
          <p>Deterministic validation before execution.</p>
        </div>
        {safety ? <StatusBadge label={safety.is_readonly ? "Read-only" : "Blocked"} tone={safety.is_readonly ? "success" : "danger"} /> : null}
      </div>
      {!safety ? <EmptyState title="No safety check yet" detail="Validate SQL before running read-only queries." /> : null}
      {safety ? (
        <div className={`safety-box ${safety.risk_level}`}>
          <div>Risk: {safety.risk_level}</div>
          <div>Statement: {safety.detected_statement_type}</div>
          {safety.blocked_reason ? <div>Blocked: {safety.blocked_reason}</div> : null}
          {safety.referenced_tables.length ? <div>Tables: {safety.referenced_tables.join(", ")}</div> : null}
          {safety.referenced_columns.length ? <div>Columns: {safety.referenced_columns.slice(0, 8).join(", ")}</div> : null}
          {safety.warnings.length ? (
            <ul className="warning-list">
              {safety.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
          {safety.suggested_sql && safety.suggested_sql !== safety.normalized_sql ? (
            <pre className="mini-sql">{safety.suggested_sql}</pre>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
