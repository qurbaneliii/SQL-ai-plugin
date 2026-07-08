# Valentina Integration

This MVP does not depend on a native Valentina Studio plugin SDK.

Current supported integration paths:

- Local web sidecar opened beside Valentina Studio
- External script workflow through `scripts/valentina_bridge.py`
- Browser-based SQL copilot used next to Valentina, pgAdmin, DBeaver, or DataGrip

Example bridge commands:

```powershell
python scripts/valentina_bridge.py status
python scripts/valentina_bridge.py schema --database-url "$env:DATABASE_URL"
python scripts/valentina_bridge.py validate --sql "SELECT * FROM users LIMIT 10"
python scripts/valentina_bridge.py generate --prompt "top 10 customers by revenue" --database-url "$env:DATABASE_URL"
python scripts/valentina_bridge.py explain --sql "SELECT * FROM users LIMIT 10"
python scripts/valentina_bridge.py fix --sql "SELECT namee FROM users" --error "column namee does not exist"
python scripts/valentina_bridge.py run --sql "SELECT * FROM users LIMIT 10" --database-url "$env:DATABASE_URL"
```

The bridge sends database URLs only to the configured backend URL and prints backend responses as JSON.

Future options:

- Electron wrapper
- Tauri wrapper
- Deeper external-tool and clipboard workflows
- Native plugin work if a stable official SDK becomes practical
