from __future__ import annotations

from app.schemas import SchemaSummaryResponse


def schema_context_text(schema: SchemaSummaryResponse, selected_tables: list[str] | None = None) -> str:
    selected = set(selected_tables or [])
    lines = [f"Schemas: {', '.join(schema.schemas) or 'none'}"]
    for table in schema.tables:
        full_name = f"{table.schema_name}.{table.table_name}"
        if selected and table.table_name not in selected and full_name not in selected:
            continue
        cols = ", ".join(f"{col.name}:{col.data_type}" for col in table.columns[:12])
        lines.append(f"- {full_name} [{table.table_type}] columns: {cols}")
        if table.primary_key:
            lines.append(f"  primary key: {', '.join(table.primary_key)}")
        if table.foreign_keys:
            fk = table.foreign_keys[0]
            lines.append(
                f"  fk example: {', '.join(fk.column_names)} -> {fk.referenced_schema}.{fk.referenced_table}({', '.join(fk.referenced_columns)})"
            )
    return "\n".join(lines)
