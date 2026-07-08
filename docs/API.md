# API

## Health

- `GET /health`

## LLM

- `GET /api/llm/status`
- `POST /api/llm/test-openai`
- `POST /api/llm/test-local`

## Database

- `POST /api/db/connect-test`
- `POST /api/db/schema`

## SQL

- `POST /api/sql/validate`
- `POST /api/sql/generate`
- `POST /api/sql/explain`
- `POST /api/sql/fix`
- `POST /api/sql/run-readonly`
- `POST /api/sql/optimize`

`/api/sql/run-readonly` always validates before database access. Unsafe SQL returns `400`; safe SQL is executed in a read-only PostgreSQL session with statement timeout and row-limit enforcement.

## Chat

- `POST /api/chat/message`
- `GET /api/chat/commands`

## Result

- `POST /api/result/summarize`

## Provider Metadata Shape

Every AI-backed response includes:

```json
{
  "provider_metadata": {
    "provider_mode": "auto",
    "selected_provider": "openai",
    "model": "gpt-4.1-mini",
    "fallback_used": false,
    "warnings": []
  }
}
```

Provider test endpoints return `ok: false` when the requested provider is unavailable, while still reporting fallback availability in `provider_metadata`.

## SQL Validation Shape

Validation responses include:

- `is_valid`
- `is_readonly`
- `risk_level`
- `detected_statement_type`
- `blocked_reason`
- `warnings`
- `referenced_tables`
- `referenced_columns`
- `normalized_sql`
- `suggested_sql`

Generated or fixed SQL that fails deterministic safety validation is repaired once. If it still fails, the SQL is not returned as runnable output.
