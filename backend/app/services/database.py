from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import psycopg
from psycopg.rows import dict_row

from app.schemas import (
    ColumnInfo,
    DatabaseConnectResponse,
    EnumInfo,
    ForeignKeyInfo,
    IndexInfo,
    QueryExecutionResponse,
    SchemaSummaryResponse,
    TableInfo,
    make_json_safe,
)
from app.settings import Settings
from app.utils.secrets import mask_database_url


class PostgresService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def resolve_database_url(self, override: str | None = None) -> str:
        database_url = override or self.settings.database_url
        if not database_url:
            raise ValueError("DATABASE_URL is not configured.")
        return database_url

    def _dsn_with_timeout(self, database_url: str) -> str:
        parsed = urlparse(database_url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["connect_timeout"] = str(self.settings.db_connect_timeout_seconds)
        return urlunparse(parsed._replace(query=urlencode(query)))

    @contextmanager
    def connect(self, database_url: str | None = None, *, readonly: bool = False) -> Iterable[psycopg.Connection]:
        resolved = self.resolve_database_url(database_url)
        dsn = self._dsn_with_timeout(resolved)
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = {int(self.settings.db_statement_timeout_ms)}")
                if readonly:
                    cur.execute("SET default_transaction_read_only = on")
            yield conn

    def test_connection(self, database_url: str | None = None) -> DatabaseConnectResponse:
        resolved = self.resolve_database_url(database_url)
        with self.connect(resolved) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
        return DatabaseConnectResponse(
            ok=True,
            message="Database connection succeeded.",
            masked_database_url=mask_database_url(resolved),
            server_version=str(version[0]) if version else None,
        )

    def get_schema_summary(
        self,
        database_url: str | None = None,
        selected_schemas: list[str] | None = None,
    ) -> SchemaSummaryResponse:
        resolved = self.resolve_database_url(database_url)
        selected_schemas = [item for item in (selected_schemas or []) if item]

        schema_filter_sql = ""
        params: list[Any] = []
        if selected_schemas:
            schema_filter_sql = " AND n.nspname = ANY(%s) "
            params.append(selected_schemas)

        table_sql = f"""
            SELECT
                n.nspname AS schema_name,
                c.relname AS table_name,
                CASE c.relkind
                    WHEN 'r' THEN 'table'
                    WHEN 'v' THEN 'view'
                    WHEN 'm' THEN 'materialized_view'
                    ELSE c.relkind::text
                END AS table_type,
                obj_description(c.oid) AS table_comment,
                COALESCE(s.n_live_tup::bigint, 0) AS approx_rows
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
            WHERE c.relkind IN ('r', 'v', 'm')
              AND n.nspname NOT IN ('pg_catalog', 'information_schema')
              {schema_filter_sql}
            ORDER BY n.nspname, c.relname
        """

        column_sql = """
            SELECT
                cols.table_schema,
                cols.table_name,
                cols.column_name,
                cols.data_type,
                cols.is_nullable = 'YES' AS is_nullable,
                cols.column_default,
                pgd.description AS column_comment
            FROM information_schema.columns cols
            LEFT JOIN pg_catalog.pg_statio_all_tables stat
              ON stat.schemaname = cols.table_schema
             AND stat.relname = cols.table_name
            LEFT JOIN pg_catalog.pg_description pgd
              ON pgd.objoid = stat.relid
             AND pgd.objsubid = cols.ordinal_position
            WHERE cols.table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY cols.table_schema, cols.table_name, cols.ordinal_position
        """

        pk_sql = """
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
        """

        fk_sql = """
            SELECT
                tc.table_schema,
                tc.table_name,
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """

        index_sql = """
            SELECT
                schemaname AS schema_name,
                tablename AS table_name,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        """

        enum_sql = """
            SELECT
                n.nspname AS schema_name,
                t.typname AS type_name,
                e.enumlabel AS enum_value
            FROM pg_type t
            JOIN pg_enum e ON e.enumtypid = t.oid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            ORDER BY n.nspname, t.typname, e.enumsortorder
        """

        with self.connect(resolved) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(table_sql, params)
                table_rows = cur.fetchall()
                cur.execute(column_sql)
                column_rows = cur.fetchall()
                cur.execute(pk_sql)
                pk_rows = cur.fetchall()
                cur.execute(fk_sql)
                fk_rows = cur.fetchall()
                cur.execute(index_sql)
                index_rows = cur.fetchall()
                cur.execute(enum_sql)
                enum_rows = cur.fetchall()

        tables_map: dict[tuple[str, str], TableInfo] = {}
        for row in table_rows:
            key = (row["schema_name"], row["table_name"])
            tables_map[key] = TableInfo(
                schema_name=row["schema_name"],
                table_name=row["table_name"],
                table_type=row["table_type"],
                columns=[],
                comment=row["table_comment"],
                approximate_row_count=int(row["approx_rows"]) if row["approx_rows"] is not None else None,
            )

        patterns = self.settings.sensitive_column_patterns
        for row in column_rows:
            key = (row["table_schema"], row["table_name"])
            table = tables_map.get(key)
            if not table:
                continue
            column = ColumnInfo(
                name=row["column_name"],
                data_type=row["data_type"],
                is_nullable=bool(row["is_nullable"]),
                default=row["column_default"],
                comment=row["column_comment"],
            )
            table.columns.append(column)
            if any(pattern in row["column_name"].lower() for pattern in patterns):
                table.sensitive_columns.append(row["column_name"])

        for row in pk_rows:
            key = (row["table_schema"], row["table_name"])
            table = tables_map.get(key)
            if table:
                table.primary_key.append(row["column_name"])

        fk_grouped: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(dict)
        for row in fk_rows:
            group_key = (row["table_schema"], row["table_name"], row["constraint_name"])
            bucket = fk_grouped.setdefault(
                group_key,
                {
                    "name": row["constraint_name"],
                    "column_names": [],
                    "referenced_schema": row["foreign_table_schema"],
                    "referenced_table": row["foreign_table_name"],
                    "referenced_columns": [],
                },
            )
            bucket["column_names"].append(row["column_name"])
            bucket["referenced_columns"].append(row["foreign_column_name"])

        for (schema_name, table_name, _), data in fk_grouped.items():
            table = tables_map.get((schema_name, table_name))
            if table:
                table.foreign_keys.append(ForeignKeyInfo(**data))

        for row in index_rows:
            key = (row["schema_name"], row["table_name"])
            table = tables_map.get(key)
            if table:
                table.indexes.append(IndexInfo(name=row["indexname"], definition=row["indexdef"]))

        enum_grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
        for row in enum_rows:
            enum_grouped[(row["schema_name"], row["type_name"])].append(row["enum_value"])

        tables = list(tables_map.values())
        truncated = len(tables) > self.settings.db_schema_max_tables
        tables = tables[: self.settings.db_schema_max_tables]
        schema_names = sorted({table.schema_name for table in tables})
        enum_types = [
            EnumInfo(schema_name=schema_name, type_name=type_name, values=values)
            for (schema_name, type_name), values in sorted(enum_grouped.items())
        ]

        return SchemaSummaryResponse(
            database_available=True,
            masked_database_url=mask_database_url(resolved),
            schemas=schema_names,
            tables=tables,
            enum_types=enum_types,
            truncated=truncated,
            max_tables=self.settings.db_schema_max_tables,
        )

    def execute_read_only(self, sql: str, database_url: str | None = None, row_limit: int | None = None) -> QueryExecutionResponse:
        resolved = self.resolve_database_url(database_url)
        started = time.perf_counter()
        with self.connect(resolved, readonly=True) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [item.name for item in cur.description] if cur.description else []
        execution_time_ms = int((time.perf_counter() - started) * 1000)
        safe_rows = [make_json_safe(row) for row in rows]
        capped_rows = safe_rows[:row_limit] if row_limit else safe_rows
        return QueryExecutionResponse(
            sql=sql,
            normalized_sql=sql,
            row_limit=row_limit or len(capped_rows) or self.settings.db_default_row_limit,
            columns=columns,
            rows=capped_rows,
            row_count=len(capped_rows),
            truncated=bool(row_limit and len(safe_rows) > row_limit),
            execution_time_ms=execution_time_ms,
            warnings=[],
        )
