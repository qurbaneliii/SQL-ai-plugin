# Frontend

The frontend is a Vite + React + TypeScript app under `frontend/`. It is a standalone SQL AI Copilot interface, not an Excel or Office.js add-in.

## Architecture

- `src/App.tsx`: app orchestration, backend health check, real/demo API routing, and core workflow handlers.
- `src/api/client.ts`: backend API client using `VITE_API_BASE_URL`.
- `src/api/mockApi.ts`: safe demo API used when the backend is unavailable.
- `src/api/types.ts`: shared frontend response/request types aligned to the FastAPI schemas.
- `src/state/appStore.ts`: app state shape and initial chat state.
- `src/components/*`: modular product panels for chat, provider status, database connection, schema, SQL editor, safety, results, and command help.
- `src/styles/main.css`: responsive developer-tool UI styling.
- `src/utils/sampleData.ts`: demo schema, SQL, validation, commands, and result samples.
- `src/utils/formatters.ts`: small display formatting helpers.

## Components

- `Layout`: desktop sidebar plus main workspace layout.
- `ChatPanel`, `MessageBubble`, `PromptInput`: chatbot workflow, example prompts, SQL blocks, copy/validate/explain/fix/run/optimize/summarize actions.
- `DatabaseConnectionPanel`: hidden PostgreSQL URL input, connection test, schema load, masked connection display, and security note.
- `ProviderStatusPanel`: provider mode selector, OpenAI/local/fallback status, model names, local provider, and router route hint.
- `SchemaBrowser`: schemas, tables, columns, data types, primary keys, foreign-key hints, index counts, sensitive columns, and table selection for context.
- `SqlEditorPanel`: SQL textarea and actions for validate, explain, fix, run read-only, optimize, copy, and clear.
- `SafetyWarnings`: risk level, statement type, blocked reason, and validation warnings.
- `ResultTable`: columns, rows, row count, truncation state, execution time, copy JSON, copy CSV, and summarize action.
- `CommandHelp`: supported command list.
- `StatusBadge`, `EmptyState`: small reusable UI primitives.

## API Client

`src/api/client.ts` defaults to `http://127.0.0.1:8000` and can be configured with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Supported functions:

- `getHealth()`
- `getLLMStatus()`
- `testOpenAI()`
- `testLocal()`
- `connectTest()`
- `getSchema()`
- `validateSql()`
- `generateSql()`
- `explainSql()`
- `fixSql()`
- `runReadonly()`
- `optimizeSql()`
- `summarizeResult()`
- `sendChatMessage()`
- `getChatCommands()`

The frontend sends `providerMode` to backend operations that support provider routing.

## Demo Mode

Demo mode activates automatically when the frontend cannot reach `/health`, or can be forced with:

```bash
VITE_DEMO_MODE=true
```

Demo mode uses `src/api/mockApi.ts` and sample data from `src/utils/sampleData.ts`. It shows explicit demo wording, uses sample ecommerce tables, and never claims to be connected to PostgreSQL.

GitHub Pages deployment relies on this behavior because Pages cannot run the FastAPI backend.

## Environment Variables

- `VITE_API_BASE_URL`: backend URL. Default: `http://127.0.0.1:8000`.
- `VITE_DEMO_MODE`: `auto`, `true`, or `demo`. Default: `auto`.
- `VITE_BASE_PATH`: local/custom Vite base path. Default: `/`.

Do not add OpenAI keys, database passwords, or other secrets to frontend env files.

## Local Development

Vite 8 requires Node.js 20.19+ or 22.12+.

```bash
cd frontend
npm install
npm run dev
```

Run checks:

```bash
npm run typecheck
npm run build
```

## GitHub Pages

The Pages workflow sets:

```bash
GITHUB_PAGES=true
VITE_DEMO_MODE=auto
```

`vite.config.ts` uses `/SQL-ai-plugin/` when `GITHUB_PAGES=true`, and `/` for local development.
