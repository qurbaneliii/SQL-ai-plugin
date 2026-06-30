# Architecture

## Frontend

The frontend is a Vite React + TypeScript sidecar UI with a left sidebar for database and provider controls, a central chat panel, and lower workspace panels for SQL editing, safety validation, and result viewing.

## Backend

The FastAPI backend exposes health, LLM status/testing, database connection/schema, SQL actions, chat orchestration, and result summarization endpoints.

## Provider Router

`LLMRouter` supports `auto`, `openai`, `local`, and `fallback`. It routes by task type instead of using one fixed provider order for every request.

## OpenAI Provider

`OpenAIProvider` uses the official OpenAI Python SDK, reads `OPENAI_API_KEY` from the backend environment, supports health checks, text generation, JSON generation, and one JSON repair attempt.

## Ollama Provider

`OllamaProvider` uses the OpenAI-compatible Ollama endpoint at `http://localhost:11434/v1`, supports health checks, text generation, JSON generation, and one JSON repair attempt.

## Fallback Provider

`FallbackProvider` is deterministic, always available, and never emits destructive SQL. It supports safe starter behavior for generation, explanation, fixing, optimization, schema help, summaries, and general chat.

## Chat Orchestrator

`ChatOrchestrator` performs command-first intent detection, routes to the right SQL or result service, validates SQL before execution, and returns provider metadata plus suggested UI actions.

## SQL Safety Layer

`SQLSafetyValidator` uses `sqlglot` to parse PostgreSQL SQL, detect statement shape, block non-read-only operations, warn on risky query patterns, and suggest a bounded `LIMIT` when missing.

## Database Adapter

`PostgresService` manages connection testing, schema introspection, masked database URLs, read-only execution, safe serialization, and statement timeout setup.

## Schema Browser

The frontend schema browser is backed by `/api/db/schema`, showing schemas, tables, columns, keys, indexes, and sensitive column hints.

## Result Flow

The user can generate or edit SQL, validate it, run it through `/api/sql/run-readonly`, inspect rows in the results table, and summarize rows through `/api/result/summarize`.
