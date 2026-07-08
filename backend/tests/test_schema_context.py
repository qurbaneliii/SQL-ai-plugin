from app.schemas import ColumnInfo, SchemaSummaryResponse, TableInfo
from app.services.schema_context import schema_context_text


def _table(name: str, columns: list[str], sensitive: list[str] | None = None) -> TableInfo:
    return TableInfo(
        schema_name="public",
        table_name=name,
        table_type="table",
        columns=[ColumnInfo(name=column, data_type="text", is_nullable=True) for column in columns],
        primary_key=[columns[0]],
        sensitive_columns=sensitive or [],
    )


def test_schema_context_prioritizes_selected_and_keyword_tables() -> None:
    schema = SchemaSummaryResponse(
        database_available=True,
        schemas=["public"],
        tables=[
            _table("audit_logs", ["audit_log_id", "message"]),
            _table("customers", ["customer_id", "name", "email"], ["email"]),
            _table("orders", ["order_id", "customer_id", "total_amount"]),
        ],
        enum_types=[],
        truncated=False,
        max_tables=80,
    )

    context = schema_context_text(schema, ["public.orders"], "top customers by total revenue")

    assert context.index("public.orders") < context.index("public.customers")
    assert "public.audit_logs" not in context
    assert "primary key" in context
    assert "sensitive columns: email" in context
