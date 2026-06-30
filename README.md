# SQL AI Copilot

SQL AI Copilot is a standalone PostgreSQL-focused AI sidecar app. It combines a FastAPI backend, a React + TypeScript frontend, a hybrid provider router for OpenAI, Ollama, and deterministic fallback, a deterministic SQL safety layer, and a lightweight bridge script for sidecar usage beside tools such as Valentina Studio, pgAdmin, DBeaver, or DataGrip.

It is not an Excel add-in, not an Office.js plugin, and not a frontend that calls LLMs directly. All AI calls stay backend-only, and read-only SQL safety is enforced before execution.

## Repo Layout

- `backend/`: FastAPI API, PostgreSQL services, LLM providers, router, safety validation, chat orchestration, and tests.
- `frontend/`: Vite React app with chat, provider controls, schema browser, SQL editor, safety display, and results table.
- `scripts/valentina_bridge.py`: lightweight CLI sidecar bridge for external SQL editor workflows.
- `docs/`: architecture, API, setup, security, smoke tests, integration notes, and roadmap.

## Backend Setup

1. `cd backend`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `copy .env.example .env`
6. Edit `backend/.env` with your PostgreSQL and optional OpenAI settings.
7. `uvicorn app.main:app --reload --port 8000`

## Frontend Setup

1. `cd frontend`
2. `npm install`
3. `npm run dev`

The frontend expects the backend at `http://127.0.0.1:8000`.

## OpenAI Setup

- Add `OPENAI_API_KEY` to `backend/.env`
- Keep the key backend-only
- Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=auto`
- Restart the backend
- Test with `POST /api/llm/test-openai`

## Ollama Local Setup

- Install [Ollama](https://ollama.com/)
- `ollama pull qwen3:4b`
- `ollama serve`
- Set `LLM_PROVIDER=local` or `LLM_PROVIDER=auto`
- Keep `LOCAL_LLM_BASE_URL=http://localhost:11434/v1`
- Test with `POST /api/llm/test-local`

Optional models:

- `ollama pull llama3.2:3b`
- `ollama pull qwen3:8b`

## Fallback-Only Mode

- Set `LLM_PROVIDER=fallback`
- Restart the backend
- Generate, explain, validate, and chat without any cloud or local LLM dependency

## PostgreSQL Connection

- Use `DATABASE_URL` in `backend/.env`, or
- Paste a PostgreSQL URL into the frontend connection panel, or
- Pass `--database-url` to `scripts/valentina_bridge.py`

## Chatbot Workflow

- Ask for SQL generation, explanation, fixes, safety validation, optimizations, schema help, and result summaries
- Use commands such as `/generate`, `/explain`, `/fix`, `/validate`, `/run`, `/schema`, `/optimize`, `/summarize`, `/provider`, `/help`
- Generated SQL is not auto-run unless `autoRun` is enabled and the SQL passes safety validation

## SQL Safety Model

- Deterministic validation only
- Read-only by default
- Blocks destructive, privilege, and procedural SQL
- Warns on `SELECT *`, missing `LIMIT`, `CROSS JOIN`, suspicious comments, possible cartesian joins, sensitive columns, and possible side-effect functions
- Enforces statement timeout and bounded row limits

## Valentina Sidecar Concept

Use the local frontend in a browser or call the backend from `scripts/valentina_bridge.py` while working in Valentina Studio or another SQL tool.

## Core Run Commands

- Backend: `uvicorn app.main:app --reload --port 8000`
- Frontend: `npm run dev`
- Backend compile: `python -m compileall app`
- Backend tests: `pytest`
- Frontend build: `npm run build`
