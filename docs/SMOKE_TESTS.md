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

```powershell
cd backend
copy .env.example .env
notepad .env
```

Set these values in `backend/.env`:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4.1-mini
LLM_PROVIDER=openai
```

Start or restart the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Test OpenAI:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/llm/test-openai -ContentType "application/json" -Body '{"providerMode":"openai","prompt":"Reply with OpenAI OK."}'
```

Then open the UI provider panel, choose `OpenAI` or `Auto`, and click `Test OpenAI`.

## Ollama

```powershell
ollama pull qwen3:4b
ollama serve
```

In a separate PowerShell window, set these values in `backend/.env`:

```env
LOCAL_LLM_ENABLED=true
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=qwen3:4b
LOCAL_LLM_TIMEOUT_SECONDS=120
LLM_PROVIDER=local
```

Start or restart the backend:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Test Ollama:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/llm/test-local -ContentType "application/json" -Body '{"providerMode":"local","prompt":"Reply with local OK."}'
```

Then open the UI provider panel, choose `Local` or `Auto`, and click `Test Local`.

## PostgreSQL Read-Only Flow

Create a read-only role:

```powershell
psql -U postgres -d my_database -c "CREATE ROLE sql_ai_readonly LOGIN PASSWORD 'change_me';"
psql -U postgres -d my_database -c "GRANT CONNECT ON DATABASE my_database TO sql_ai_readonly;"
psql -U postgres -d my_database -c "GRANT USAGE ON SCHEMA public TO sql_ai_readonly;"
psql -U postgres -d my_database -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO sql_ai_readonly;"
psql -U postgres -d my_database -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sql_ai_readonly;"
```

Set the backend URL:

```env
DATABASE_URL=postgresql://sql_ai_readonly:change_me@localhost:5432/my_database
```

Test connection and schema:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/db/connect-test -ContentType "application/json" -Body '{}'
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/db/schema -ContentType "application/json" -Body '{}'
```

Test generate, validate, run, and summarize:

```powershell
$generated = Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/generate -ContentType "application/json" -Body '{"prompt":"show 10 recent rows from a safe table","providerMode":"fallback"}'
$generated.sql
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/validate -ContentType "application/json" -Body (@{ sql = $generated.sql; allow_write = $false } | ConvertTo-Json)
$result = Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/run-readonly -ContentType "application/json" -Body (@{ sql = $generated.sql; rowLimit = 25 } | ConvertTo-Json)
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/result/summarize -ContentType "application/json" -Body (@{ sql = $generated.sql; rows = $result.rows; providerMode = "fallback" } | ConvertTo-Json -Depth 6)
```

In the UI, paste the read-only `DATABASE_URL`, click `Connect test`, click `Load schema`, select tables, generate SQL, validate it, run read-only, then summarize the result preview.

## Fallback

- Set `LLM_PROVIDER=fallback`
- Restart the backend
- Use chat, generate, explain, and validate without OpenAI or Ollama
