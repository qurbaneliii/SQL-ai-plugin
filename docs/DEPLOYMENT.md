# Deployment

This project deploys the frontend demo to GitHub Pages through GitHub Actions. The FastAPI backend is not deployed to GitHub Pages.

## GitHub Actions Workflow

Workflow file:

```text
.github/workflows/frontend-demo.yml
```

The workflow:

- Runs on pushes to `main` and `master`.
- Supports manual `workflow_dispatch`.
- Installs Node 22.
- Installs frontend dependencies.
- Runs `npm run typecheck --if-present`.
- Runs `npm run lint --if-present`.
- Builds the Vite frontend.
- Uploads `frontend/dist`.
- Deploys through GitHub Pages Actions.

Required workflow permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

## GitHub Pages Setup

1. Open the repository on GitHub.
2. Go to Settings.
3. Open Pages.
4. Set Source to GitHub Actions.
5. Push to `main` or `master`, or run the `Frontend Demo` workflow manually.
6. Open the deployed URL after the workflow completes.

For this repository, the Vite base path is `/SQL-ai-plugin/` during Pages builds.

## Build Commands

Local frontend build:

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Demo Behavior On Pages

GitHub Pages hosts static files only. When the deployed frontend cannot reach `http://127.0.0.1:8000/health`, it switches into demo mode and uses sample data.

Demo mode does not require:

- OpenAI API keys
- Ollama
- PostgreSQL
- A deployed backend

It clearly displays that sample data is being used.

For real OpenAI, Ollama, or PostgreSQL testing, run the FastAPI backend and the Vite frontend locally. Some browsers restrict HTTPS GitHub Pages pages from calling a local HTTP backend, even though the backend CORS policy includes the Pages origin.

## Backend Deployment Limitation

FastAPI, PostgreSQL, OpenAI provider routing, and Ollama provider routing require a backend runtime. GitHub Pages cannot run those services.

Future backend deployment options include:

- Render, Fly.io, Railway, or a VPS for FastAPI.
- Managed PostgreSQL such as Supabase, Neon, or RDS.
- A private local backend for sidecar usage beside SQL desktop tools.
- Vercel or another platform for frontend hosting if GitHub Pages is not desired.

## Troubleshooting

- Blank page on Pages: verify the workflow used `GITHUB_PAGES=true` and Vite built with `/SQL-ai-plugin/`.
- `npm ci` failure: make sure `frontend/package-lock.json` is committed.
- Backend status offline: expected on GitHub Pages unless a reachable backend is configured.
- OpenAI unavailable: confirm `OPENAI_API_KEY` is set in the backend environment, not the frontend.
- Local unavailable: confirm Ollama is running and the backend `LOCAL_LLM_BASE_URL` is correct.
- SQL blocked: inspect the Safety panel for risk level and blocked reason.
