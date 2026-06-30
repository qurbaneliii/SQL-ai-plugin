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
