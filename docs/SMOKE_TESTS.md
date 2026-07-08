# Smoke Tests

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run typecheck
npm run build
npm run dev
```

Browser smoke:

- Open `http://127.0.0.1:5173/`.
- Verify the command bar, Database panel, Providers panel, Schema Browser, Copilot Chat, SQL Editor, Safety panel, and Results panel render.
- With backend running, verify backend mode appears and no Vite error overlay is visible.
- With backend unavailable, verify automatic demo mode shows sample schema and sample result data.

## Smoke Endpoints

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/llm/status
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/llm/test-openai -ContentType "application/json" -Body '{"providerMode":"openai"}'
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/llm/test-local -ContentType "application/json" -Body '{"providerMode":"local"}'
```

Safe validation:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/validate -ContentType "application/json" -Body '{"sql":"SELECT * FROM users LIMIT 10","allow_write":false}'
```

Blocked validation:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/validate -ContentType "application/json" -Body '{"sql":"DROP TABLE users","allow_write":false}'
```

Blocked read-only execution:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/run-readonly -ContentType "application/json" -Body '{"sql":"DROP TABLE users"}'
```

Expected result: HTTP `400`.

Chat:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/chat/message -ContentType "application/json" -Body '{"message":"Generate SQL for top 10 users","currentSql":"","selectedSchemas":[],"selectedTables":[],"providerMode":"fallback","autoRun":false}'
```

## OpenAI

- Add `OPENAI_API_KEY` to `backend/.env`
- Set `LLM_PROVIDER=openai` or `auto`
- Restart the backend
- Test `/api/llm/test-openai`

## Ollama

```powershell
ollama pull qwen3:4b
ollama serve
```

- Set `LLM_PROVIDER=local` or `auto`
- Test `/api/llm/test-local`

## Fallback

- Set `LLM_PROVIDER=fallback`
- Restart the backend
- Use chat, generate, explain, and validate without OpenAI or Ollama
