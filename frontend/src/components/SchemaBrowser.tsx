import type { SchemaSummaryResponse } from "../api/types";

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
      </div>
      {!schema ? <div className="empty-state">Load schema to inspect tables.</div> : null}
      {schema?.tables.map((table) => {
        const fullName = `${table.schema_name}.${table.table_name}`;
        const checked = selectedTables.includes(fullName);
        return (
          <label className="schema-item" key={fullName}>
            <input type="checkbox" checked={checked} onChange={() => onToggleTable(fullName)} />
            <div>
              <div className="schema-name">{fullName}</div>
              <div className="muted-text">
                {table.columns.slice(0, 4).map((column) => column.name).join(", ")}
                {table.columns.length > 4 ? " ..." : ""}
              </div>
            </div>
          </label>
        );
      })}
    </div>
  );
}
