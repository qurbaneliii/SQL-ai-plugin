# SQL AI Copilot

SQL AI Copilot is a standalone PostgreSQL-focused AI sidecar for developers working beside Valentina Studio, pgAdmin, DBeaver, DataGrip, or another SQL editor. It is not an Excel add-in, not an Office.js add-in, and not a spreadsheet tool.

The app combines a FastAPI backend, a React + TypeScript frontend, a PostgreSQL integration layer, an OpenAI provider, an Ollama/local LLM provider, a deterministic fallback provider, SQL safety validation, and a chatbot-style workflow.

## Features

- Chat interface for SQL generation, explanation, fixes, optimization, schema help, and result summaries.
- SQL editor with validate, explain, fix, run read-only, optimize, copy, and clear actions.
- Database connection test panel with masked connection display.
- Provider status panel for Auto, OpenAI, Local, and Fallback modes.
- Schema browser with tables, columns, data types, relationship hints, and selected table context.
- Safety warnings panel for risk level, blocked reason, read-only status, and warnings.
- Result table preview with row count, execution time, truncation state, and summarize action.
- Safe demo mode for GitHub Pages when the FastAPI backend is unavailable.

## Repo Layout

- `backend/`: FastAPI API, PostgreSQL services, LLM providers, router, safety validation, chat orchestration, and tests.
- `frontend/`: Vite React app with the SQL Copilot product UI and demo-mode fallback.
- `scripts/valentina_bridge.py`: lightweight CLI sidecar bridge for external SQL editor workflows.
- `docs/`: architecture, API, frontend, deployment, security, smoke tests, integration notes, and roadmap.

## Backend Setup

1. `cd backend`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate` on Windows, or `source .venv/bin/activate` on macOS/Linux
4. `pip install -r requirements.txt`
5. `copy .env.example .env` on Windows, or `cp .env.example .env` on macOS/Linux.
6. Edit `backend/.env`. Keep OpenAI keys and database URLs backend-only.
7. `uvicorn app.main:app --reload --port 8000`

The backend exposes `/health`, `/api/llm/status`, `/api/db/*`, `/api/sql/*`, `/api/chat/*`, and `/api/result/summarize`.

## Frontend Setup

Requires Node.js 20.19+ or 22.12+.

1. `cd frontend`
2. `npm install`
3. `copy .env.example .env` on Windows, or `cp .env.example .env` on macOS/Linux
4. `npm run dev`

Default environment:

- `VITE_API_BASE_URL=http://127.0.0.1:8000`
- `VITE_DEMO_MODE=auto`
- `VITE_BASE_PATH=/`

Build commands:

- `npm run typecheck`
- `npm run build`
- `npm run preview`

## Demo Mode

GitHub Pages can host only the frontend, so the deployed demo automatically falls back to mock responses if `/health` is unavailable.

Demo mode:

- Requires no OpenAI API key.
- Requires no Ollama server.
- Requires no PostgreSQL database.
- Shows clear “Demo Mode” wording.
- Uses sample `customers`, `orders`, `order_items`, and `products` schema data.
- Does not claim to be connected to a real database.

To force demo mode locally, set `VITE_DEMO_MODE=true`.

## Provider Modes

- `auto`: backend router chooses OpenAI, local, then fallback according to availability.
- `openai`: backend uses OpenAI if configured.
- `local`: backend uses the Ollama-compatible local provider if available.
- `fallback`: backend uses deterministic fallback responses.

The frontend never calls OpenAI or Ollama directly. All AI operations go through the FastAPI backend.

Provider responses include metadata showing requested mode, selected provider, model, fallback state, and warnings. In `auto`, generation/fix/optimization prefer OpenAI, then local, then fallback; explanation/schema/result summary prefer local, then OpenAI, then fallback.

## OpenAI Setup

- Add `OPENAI_API_KEY` to the backend environment only.
- Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=auto`.
- Restart the backend.
- Test from the UI provider panel or with `POST /api/llm/test-openai`.

Do not put OpenAI keys in `frontend/.env`.

The OpenAI provider uses structured JSON output when the selected model/API supports it. If structured output is unavailable, the backend falls back to strict JSON instructions, Pydantic validation, and one JSON repair attempt.

## Ollama Local Setup

1. Install [Ollama](https://ollama.com/).
2. `ollama pull qwen3:4b`
3. `ollama serve`
4. Set backend `LLM_PROVIDER=local` or `LLM_PROVIDER=auto`.
5. Keep `LOCAL_LLM_BASE_URL=http://localhost:11434/v1` unless customized.
6. Test from the UI provider panel or with `POST /api/llm/test-local`.

The local provider is considered available only after the backend confirms the Ollama-compatible chat-completions endpoint can return a model response.

## PostgreSQL Connection

Use one of these options:

- Set `DATABASE_URL` in the backend environment.
- Paste a PostgreSQL URL into the frontend Database panel.
- Pass `--database-url` to `scripts/valentina_bridge.py`.

Database URLs are sent only to the backend API. The frontend does not store database passwords in localStorage.

Use a read-only PostgreSQL user for real testing. The backend validates SQL before DB access, starts read-only sessions, applies statement timeouts, injects or reduces `LIMIT` where safe, and fetches only up to the requested row cap plus one extra row to detect truncation.

## GitHub Pages Deployment

The repository includes `.github/workflows/frontend-demo.yml`, which builds `frontend/dist` and deploys it to GitHub Pages.

1. Go to repository Settings.
2. Open Pages.
3. Set Source to GitHub Actions.
4. Push to `main` or `master`, or run the workflow manually.
5. Open the deployed Pages URL after the workflow completes.

The workflow sets `GITHUB_PAGES=true`, so Vite builds with the base path `/SQL-ai-plugin/`. The backend is not deployed to GitHub Pages; the public Pages build runs as a safe frontend demo until a local/backend API is connected.

## Security Notes

- No OpenAI API key belongs in the frontend.
- No API key input field is exposed in the frontend.
- The frontend does not call OpenAI directly.
- The frontend does not call Ollama directly.
- Generated SQL does not auto-run unless the user explicitly enables auto-run and the backend validates it as safe.
- Destructive SQL is blocked by the safety layer.
- `.env.example` files use placeholders and no secrets.

## More Docs

- `docs/FRONTEND.md`
- `docs/DEPLOYMENT.md`
- `docs/API.md`
- `docs/SECURITY.md`
- `docs/LOCAL_LLM_SETUP.md`
