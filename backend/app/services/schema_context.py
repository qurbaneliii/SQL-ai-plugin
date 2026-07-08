from __future__ import annotations

import re

from app.schemas import ColumnInfo, SchemaSummaryResponse, TableInfo


def schema_context_text(
    schema: SchemaSummaryResponse,
    selected_tables: list[str] | None = None,
    prompt: str | None = None,
    *,
    max_tables: int = 12,
    max_columns: int = 14,
) -> str:
    selected = {item.lower() for item in (selected_tables or [])}
    tokens = _keywords(prompt or "")
    lines = [
        f"Schemas: {', '.join(schema.schemas) or 'none'}",
        f"Schema source: {'live database' if schema.database_available else 'demo/sample context'}",
    ]
    if schema.truncated:
        lines.append(
            f"Schema was truncated at {schema.max_tables} tables; ask the user to narrow schema or table selection if needed."
        )

    ranked = sorted(
        schema.tables,
        key=lambda table: (-_score_table(table, selected, tokens), table.schema_name, table.table_name),
    )
    if selected or tokens:
        ranked = [table for table in ranked if _score_table(table, selected, tokens) > 0]
    ranked = ranked[:max_tables]

    if not ranked:
        return "\n".join([*lines, "No relevant tables were available. Ask the user to load schema or select tables."])

    for table in ranked:
        full_name = f"{table.schema_name}.{table.table_name}"
        cols = ", ".join(_format_column(column) for column in _rank_columns(table, tokens, max_columns))
        row_hint = f", approx rows: {table.approximate_row_count}" if table.approximate_row_count is not None else ""
        lines.append(f"- {full_name} [{table.table_type}{row_hint}] columns: {cols}")
        if table.comment:
            lines.append(f"  comment: {table.comment[:220]}")
        if table.primary_key:
            lines.append(f"  primary key: {', '.join(table.primary_key)}")
        for fk in table.foreign_keys[:3]:
            lines.append(
                f"  fk: {', '.join(fk.column_names)} -> {fk.referenced_schema}.{fk.referenced_table}({', '.join(fk.referenced_columns)})"
            )
        if table.indexes:
            lines.append(f"  indexes: {', '.join(index.name for index in table.indexes[:3])}")
        if table.sensitive_columns:
            lines.append(f"  sensitive columns: {', '.join(table.sensitive_columns)}")

    return "\n".join(lines)


def _keywords(text: str) -> set[str]:
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "show",
        "give",
        "list",
        "top",
        "sql",
        "query",
        "table",
        "tables",
        "schema",
        "select",
        "where",
    }
    return {
        token
        for token in re.split(r"[^a-zA-Z0-9_]+", text.lower())
        if len(token) >= 2 and token not in stop_words
    }


def _score_table(table: TableInfo, selected: set[str], tokens: set[str]) -> int:
    full_name = f"{table.schema_name}.{table.table_name}".lower()
    table_name = table.table_name.lower()
    if selected and (full_name in selected or table_name in selected):
        return 1000
    score = 0
    names = {table_name, full_name, *table_name.split("_")}
    score += 80 * len(tokens.intersection(names))
    for column in table.columns:
        column_name = column.name.lower()
        column_parts = set(column_name.split("_"))
        if column_name in tokens:
            score += 30
        score += 8 * len(tokens.intersection(column_parts))
        if column.comment:
            score += 3 * sum(1 for token in tokens if token in column.comment.lower())
    if table.comment:
        score += 4 * sum(1 for token in tokens if token in table.comment.lower())
    return score


def _rank_columns(table: TableInfo, tokens: set[str], max_columns: int) -> list[ColumnInfo]:
    def score(column: ColumnInfo) -> tuple[int, str]:
        name = column.name.lower()
        parts = set(name.split("_"))
        value = 0
        if column.name in table.primary_key:
            value += 100
        if name in table.sensitive_columns:
            value += 20
        if name in tokens:
            value += 70
        value += 12 * len(tokens.intersection(parts))
        return (-value, column.name)

    return sorted(table.columns, key=score)[:max_columns]


def _format_column(column: ColumnInfo) -> str:
    nullable = " nullable" if column.is_nullable else ""
    return f"{column.name}:{column.data_type}{nullable}"
