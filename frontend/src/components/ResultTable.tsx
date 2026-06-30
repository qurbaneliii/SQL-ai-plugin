import type { QueryExecutionResponse } from "../api/types";

interface ResultTableProps {
  result?: QueryExecutionResponse;
  onSummarize: () => Promise<void>;
}

export function ResultTable({ result, onSummarize }: ResultTableProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Results</h2>
          <p>Read-only query output.</p>
        </div>
        <button className="secondary-button" onClick={onSummarize} disabled={!result}>
          Summarize
        </button>
      </div>
      {!result ? <div className="empty-state">No query results yet.</div> : null}
      {result ? (
        <>
          <div className="result-meta">
            <span>Rows: {result.row_count}</span>
            <span>Limit: {result.row_limit}</span>
            <span>Time: {result.execution_time_ms} ms</span>
            <span>{result.truncated ? "Truncated" : "Complete"}</span>
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
                      <td key={column}>{String(row[column] ?? "")}</td>
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
