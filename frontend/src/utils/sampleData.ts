import type {
  ChatCommandsResponse,
  ProviderMetadata,
  QueryExecutionResponse,
  SchemaSummaryResponse,
  SQLValidationResponse,
} from "../api/types";

export const demoSql = `SELECT
  c.customer_id,
  c.name,
  SUM(o.total_amount) AS total_revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC
LIMIT 10;`;

export const demoProviderMetadata: ProviderMetadata = {
  provider_mode: "fallback",
  selected_provider: "fallback",
  model: "demo-fallback",
  fallback_used: true,
  warnings: ["Demo mode uses sample data. Connect a local backend to use a real PostgreSQL database."],
};

export const demoValidation: SQLValidationResponse = {
  is_valid: true,
  is_readonly: true,
  blocked_reason: null,
  risk_level: "low",
  detected_statement_type: "SELECT",
  referenced_tables: ["customers", "orders"],
  referenced_columns: ["customer_id", "name", "total_amount"],
  warnings: ["Read-only SELECT detected.", "LIMIT 10 bounds the result set."],
  normalized_sql: demoSql,
  suggested_sql: null,
};

export const demoSchema: SchemaSummaryResponse = {
  database_available: false,
  masked_database_url: null,
  schemas: ["public"],
  truncated: false,
  max_tables: 25,
  enum_types: [],
  tables: [
    {
      schema_name: "public",
      table_name: "customers",
      table_type: "BASE TABLE",
      primary_key: ["customer_id"],
      sensitive_columns: ["email"],
      approximate_row_count: 1240,
      columns: [
        { name: "customer_id", data_type: "uuid", is_nullable: false },
        { name: "name", data_type: "text", is_nullable: false },
        { name: "email", data_type: "text", is_nullable: true },
        { name: "created_at", data_type: "timestamp with time zone", is_nullable: false },
      ],
      foreign_keys: [],
      indexes: [{ name: "customers_pkey", definition: "PRIMARY KEY (customer_id)" }],
    },
    {
      schema_name: "public",
      table_name: "orders",
      table_type: "BASE TABLE",
      primary_key: ["order_id"],
      sensitive_columns: [],
      approximate_row_count: 9850,
      columns: [
        { name: "order_id", data_type: "uuid", is_nullable: false },
        { name: "customer_id", data_type: "uuid", is_nullable: false },
        { name: "ordered_at", data_type: "timestamp with time zone", is_nullable: false },
        { name: "status", data_type: "text", is_nullable: false },
        { name: "total_amount", data_type: "numeric", is_nullable: false },
      ],
      foreign_keys: [
        {
          name: "orders_customer_id_fkey",
          column_names: ["customer_id"],
          referenced_schema: "public",
          referenced_table: "customers",
          referenced_columns: ["customer_id"],
        },
      ],
      indexes: [
        { name: "orders_pkey", definition: "PRIMARY KEY (order_id)" },
        { name: "orders_customer_id_idx", definition: "INDEX (customer_id)" },
      ],
    },
    {
      schema_name: "public",
      table_name: "order_items",
      table_type: "BASE TABLE",
      primary_key: ["order_item_id"],
      sensitive_columns: [],
      approximate_row_count: 28600,
      columns: [
        { name: "order_item_id", data_type: "uuid", is_nullable: false },
        { name: "order_id", data_type: "uuid", is_nullable: false },
        { name: "product_id", data_type: "uuid", is_nullable: false },
        { name: "quantity", data_type: "integer", is_nullable: false },
        { name: "unit_price", data_type: "numeric", is_nullable: false },
      ],
      foreign_keys: [
        {
          name: "order_items_order_id_fkey",
          column_names: ["order_id"],
          referenced_schema: "public",
          referenced_table: "orders",
          referenced_columns: ["order_id"],
        },
        {
          name: "order_items_product_id_fkey",
          column_names: ["product_id"],
          referenced_schema: "public",
          referenced_table: "products",
          referenced_columns: ["product_id"],
        },
      ],
      indexes: [{ name: "order_items_order_id_idx", definition: "INDEX (order_id)" }],
    },
    {
      schema_name: "public",
      table_name: "products",
      table_type: "BASE TABLE",
      primary_key: ["product_id"],
      sensitive_columns: [],
      approximate_row_count: 320,
      columns: [
        { name: "product_id", data_type: "uuid", is_nullable: false },
        { name: "sku", data_type: "text", is_nullable: false },
        { name: "name", data_type: "text", is_nullable: false },
        { name: "category", data_type: "text", is_nullable: true },
        { name: "list_price", data_type: "numeric", is_nullable: false },
      ],
      foreign_keys: [],
      indexes: [{ name: "products_sku_key", definition: "UNIQUE (sku)" }],
    },
  ],
};

export const demoResult: QueryExecutionResponse = {
  sql: demoSql,
  normalized_sql: demoSql,
  row_limit: 10,
  columns: ["customer_id", "name", "total_revenue"],
  rows: [
    { customer_id: "c_1027", name: "Northwind Labs", total_revenue: 184230.5 },
    { customer_id: "c_0881", name: "Valley Analytics", total_revenue: 152901.75 },
    { customer_id: "c_0644", name: "Atlas Retail", total_revenue: 138440.2 },
    { customer_id: "c_0319", name: "Bluebird Supply", total_revenue: 126775.0 },
  ],
  row_count: 4,
  truncated: false,
  execution_time_ms: 18,
  warnings: ["Demo result preview only. No live PostgreSQL query was executed."],
  provider_metadata: demoProviderMetadata,
};

export const demoCommands: ChatCommandsResponse = {
  commands: [
    { command: "/schema", description: "Inspect database schemas and tables." },
    { command: "/generate", description: "Generate read-only SQL from natural language." },
    { command: "/explain", description: "Explain a SQL query." },
    { command: "/fix", description: "Fix SQL errors or invalid syntax." },
    { command: "/validate", description: "Validate SQL safety." },
    { command: "/run", description: "Run safe read-only SQL." },
    { command: "/optimize", description: "Suggest query optimizations." },
    { command: "/summarize", description: "Summarize query results." },
    { command: "/provider", description: "Show provider selection behavior." },
    { command: "/help", description: "Show command help." },
  ],
};
