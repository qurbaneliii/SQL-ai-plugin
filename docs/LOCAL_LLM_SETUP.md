# Local LLM Setup

1. Install [Ollama](https://ollama.com/).
2. Pull the default local model:
   - `ollama pull qwen3:4b`
3. Start Ollama:
   - `ollama serve`
4. Keep the backend pointed at:
   - `http://localhost:11434/v1`
5. Use either:
   - `LLM_PROVIDER=local`
   - `LLM_PROVIDER=auto`

Backend env keys:

```env
LOCAL_LLM_ENABLED=true
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=qwen3:4b
LOCAL_LLM_TIMEOUT_SECONDS=120
```

Test from PowerShell:

```powershell
Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/llm/test-local -ContentType "application/json" -Body '{"providerMode":"local"}'
```

The backend marks local as available only if the configured model responds through the Ollama OpenAI-compatible chat-completions endpoint.

Optional alternatives:

- Lighter: `ollama pull llama3.2:3b`
- Stronger: `ollama pull qwen3:8b`

Local quality and latency depend on your hardware.
