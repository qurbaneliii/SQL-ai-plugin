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
npm run dev
```

## Smoke Endpoints

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/llm/status
```

Safe validation:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/validate -ContentType "application/json" -Body '{"sql":"SELECT * FROM users LIMIT 10","allow_write":false}'
```

Blocked validation:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/sql/validate -ContentType "application/json" -Body '{"sql":"DROP TABLE users","allow_write":false}'
```

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
