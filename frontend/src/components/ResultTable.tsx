import type { QueryExecutionResponse } from "../api/types";
import { formatDuration, formatValue } from "../utils/formatters";
import { EmptyState } from "./EmptyState";
import { StatusBadge } from "./StatusBadge";

interface ResultTableProps {
  result?: QueryExecutionResponse;
  onSummarize: () => Promise<void>;
}

export function ResultTable({ result, onSummarize }: ResultTableProps) {
  async function copyJson() {
    if (!result) {
      return;
    }
    await navigator.clipboard.writeText(JSON.stringify(result.rows, null, 2));
  }

  async function copyCsv() {
    if (!result) {
      return;
    }
    const header = result.columns.join(",");
    const rows = result.rows.map((row) =>
      result.columns
        .map((column) => {
          const value = formatValue(row[column]).replace(/"/g, '""');
          return value.includes(",") || value.includes("\n") ? `"${value}"` : value;
        })
        .join(",")
    );
    await navigator.clipboard.writeText([header, ...rows].join("\n"));
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Results</h2>
          <p>Read-only query output.</p>
        </div>
        <div className="panel-actions">
          {result ? <StatusBadge label={result.truncated ? "Truncated" : "Complete"} tone={result.truncated ? "warning" : "success"} /> : null}
          <button className="secondary-button" onClick={() => void copyJson()} disabled={!result}>
            Copy JSON
          </button>
          <button className="secondary-button" onClick={() => void copyCsv()} disabled={!result}>
            Copy CSV
          </button>
          <button className="secondary-button" onClick={onSummarize} disabled={!result}>
            Summarize
          </button>
        </div>
      </div>
      {!result ? <EmptyState title="No result preview" detail="Run safe read-only SQL, or use demo mode sample results." /> : null}
      {result ? (
        <>
          <div className="result-meta">
            <span>Rows: {result.row_count}</span>
            <span>Limit: {result.row_limit}</span>
            <span>Time: {formatDuration(result.execution_time_ms)}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {result.columns.map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, index) => (
                  <tr key={index}>
                    {result.columns.map((column) => (
                      <td key={column}>{formatValue(row[column])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </div>
  );
}
