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

Optional alternatives:

- Lighter: `ollama pull llama3.2:3b`
- Stronger: `ollama pull qwen3:8b`

Local quality and latency depend on your hardware.
