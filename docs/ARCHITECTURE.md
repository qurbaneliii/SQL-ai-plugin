# Architecture

## Frontend

The frontend is a Vite React + TypeScript sidecar UI with a left sidebar for database and provider controls, a central chat panel, and lower workspace panels for SQL editing, safety validation, and result viewing.

## Backend

The FastAPI backend exposes health, LLM status/testing, database connection/schema, SQL actions, chat orchestration, and result summarization endpoints.

## Provider Router

`LLMRouter` supports `auto`, `openai`, `local`, and `fallback`. It routes by task type instead of using one fixed provider order for every request.

## OpenAI Provider

`OpenAIProvider` uses the official OpenAI Python SDK and reads `OPENAI_API_KEY` from the backend environment. JSON tasks first try structured output through the Responses API, then fall back to strict JSON instructions, Pydantic validation, and one JSON repair attempt when the selected model/API does not support the structured path.

## Ollama Provider

`OllamaProvider` uses the OpenAI-compatible Ollama endpoint at `http://localhost:11434/v1`. Availability is a real cached probe against chat completions for the configured model, not merely the existence of a client object. Missing or stopped Ollama falls back safely.

## Fallback Provider

`FallbackProvider` is deterministic, always available, and never emits destructive SQL. It supports safe starter behavior for generation, explanation, fixing, optimization, schema help, summaries, and general chat.

## Chat Orchestrator

`ChatOrchestrator` performs command-first intent detection, routes to the right SQL or result service, validates SQL before execution, and returns provider metadata plus suggested UI actions.

## SQL Safety Layer

`SQLSafetyValidator` uses `sqlglot` to parse PostgreSQL SQL, detect statement shape, block non-read-only operations, block known side-effect functions, warn on risky query patterns, and suggest or enforce a bounded `LIMIT`.

## Database Adapter

`PostgresService` manages connection testing, schema introspection, masked database URLs, read-only execution, safe serialization, sanitized database errors, and statement timeout setup. Read-only execution fetches at most the requested row cap plus one row to detect truncation instead of fetching the full result set.

## Schema Context Builder

`schema_context_text` ranks selected tables first, then keyword-matched tables and columns from the user request. It emits compact table context with columns, primary keys, foreign key hints, indexes, comments, row estimates, and sensitive-column warnings. If the schema is truncated or no relevant tables are found, the prompt instructs the assistant to ask the user to narrow context.

## Schema Browser

The frontend schema browser is backed by `/api/db/schema`, showing schemas, tables, columns, keys, indexes, and sensitive column hints.

## Result Flow

The user can generate or edit SQL, validate it, run it through `/api/sql/run-readonly`, inspect rows in the results table, and summarize rows through `/api/result/summarize`.
