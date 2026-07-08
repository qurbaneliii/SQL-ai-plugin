# Security

- OpenAI API keys are backend-only and never sent to the frontend.
- Ollama is also accessed only through the backend.
- SQL execution is read-only by default.
- Destructive, write, privilege, and procedural SQL are blocked by deterministic validation.
- Missing `LIMIT` results in a bounded suggested SQL variant before execution.
- Runtime execution enforces the requested row cap and fetches only `row_limit + 1` rows to detect truncation.
- Statement timeout is configured on the PostgreSQL session.
- Sensitive-column patterns trigger warnings.
- Known side-effect functions such as `dblink_connect` are blocked.
- Database URLs are masked in API responses and database errors are sanitized before returning to the client.
- Generated SQL is not auto-executed unless explicitly requested and validated as safe.
- This MVP is not a native Valentina Studio plugin yet; it is a sidecar app and optional CLI bridge.

## Recommended PostgreSQL Role

Create a dedicated read-only role for testing:

```sql
CREATE ROLE sql_ai_readonly LOGIN PASSWORD 'change_me';
GRANT CONNECT ON DATABASE my_database TO sql_ai_readonly;
GRANT USAGE ON SCHEMA public TO sql_ai_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sql_ai_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sql_ai_readonly;
```

Use that role in `DATABASE_URL` or the UI database URL field. Do not use owner, migration, admin, or production write credentials.
