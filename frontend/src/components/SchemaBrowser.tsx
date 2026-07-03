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
            <div>
              <div className="schema-name">{fullName}</div>
              <div className="muted-text">
                {table.columns.slice(0, 4).map((column) => `${column.name}: ${column.data_type}`).join(", ")}
                {table.columns.length > 4 ? " ..." : ""}
              </div>
              {table.foreign_keys.length ? <div className="muted-text">{table.foreign_keys.length} relationship hints</div> : null}
            </div>
          </label>
        );
      })}
    </div>
  );
}
