import type { SchemaSummaryResponse } from "../api/types";
import { EmptyState } from "./EmptyState";
import { StatusBadge } from "./StatusBadge";

interface SchemaBrowserProps {
  schema?: SchemaSummaryResponse;
  selectedTables: string[];
  onToggleTable: (tableName: string) => void;
}

export function SchemaBrowser({ schema, selectedTables, onToggleTable }: SchemaBrowserProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Schema Browser</h2>
          <p>Choose tables to bias SQL generation.</p>
        </div>
        {schema ? <StatusBadge label={schema.database_available ? "Live schema" : "Demo schema"} tone={schema.database_available ? "success" : "demo"} /> : null}
      </div>
      {!schema ? <EmptyState title="No schema loaded" detail="Load schema from the backend, or use demo mode sample tables." /> : null}
      {schema?.tables.map((table) => {
        const fullName = `${table.schema_name}.${table.table_name}`;
        const checked = selectedTables.includes(fullName);
        return (
          <label className="schema-item" key={fullName}>
            <input type="checkbox" checked={checked} onChange={() => onToggleTable(fullName)} />
            <div className="schema-detail">
              <div className="schema-title-row">
                <div className="schema-name">{fullName}</div>
                <span className="schema-count">{table.approximate_row_count?.toLocaleString() ?? "?"} rows</span>
              </div>
              <div className="column-list">
                {table.columns.slice(0, 8).map((column) => (
                  <span
                    className={`column-pill ${table.sensitive_columns.includes(column.name) ? "sensitive" : ""}`}
                    key={`${fullName}.${column.name}`}
                    title={column.comment ?? undefined}
                  >
                    {column.name}:{column.data_type}
                  </span>
                ))}
                {table.columns.length > 8 ? <span className="column-pill muted">+{table.columns.length - 8}</span> : null}
              </div>
              <div className="schema-meta-row">
                {table.primary_key.length ? <span>PK {table.primary_key.join(", ")}</span> : null}
                {table.foreign_keys.length ? <span>{table.foreign_keys.length} FK hints</span> : null}
                {table.indexes.length ? <span>{table.indexes.length} indexes</span> : null}
              </div>
              {table.sensitive_columns.length ? (
                <div className="sensitive-note">Sensitive columns: {table.sensitive_columns.join(", ")}</div>
              ) : null}
            </div>
          </label>
        );
      })}
    </div>
  );
}
