import type { SQLValidationResponse } from "../api/types";

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
      </div>
      {!safety ? <div className="empty-state">Validate SQL to inspect safety warnings.</div> : null}
      {safety ? (
        <div className={`safety-box ${safety.risk_level}`}>
          <div>Risk: {safety.risk_level}</div>
          <div>Valid: {safety.is_valid ? "yes" : "no"}</div>
          <div>Read-only: {safety.is_readonly ? "yes" : "no"}</div>
          {safety.blocked_reason ? <div>Blocked: {safety.blocked_reason}</div> : null}
          {safety.warnings.length ? (
            <ul>
              {safety.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
