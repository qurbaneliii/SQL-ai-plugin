# Security

- OpenAI API keys are backend-only and never sent to the frontend.
- Ollama is also accessed only through the backend.
- SQL execution is read-only by default.
- Destructive, write, privilege, and procedural SQL are blocked by deterministic validation.
- Missing `LIMIT` results in a bounded suggested SQL variant before execution.
- Statement timeout is configured on the PostgreSQL session.
- Sensitive-column patterns trigger warnings.
- Generated SQL is not auto-executed unless explicitly requested and validated as safe.
- This MVP is not a native Valentina Studio plugin yet; it is a sidecar app and optional CLI bridge.
