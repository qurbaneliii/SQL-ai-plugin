from __future__ import annotations

import argparse
import json
import sys
from urllib import error, parse, request


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


def post_json(base_url: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        parse.urljoin(base_url, path),
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(base_url: str, path: str) -> dict:
    with request.urlopen(parse.urljoin(base_url, path)) as response:
        return json.loads(response.read().decode("utf-8"))


def maybe_copy(text: str, enabled: bool) -> None:
    if not enabled:
        return
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        print("Copied to clipboard.")
    except Exception:
        print("Clipboard copy unavailable. Install pyperclip to enable --copy.")


def print_json(data: dict) -> None:
    print(json.dumps(data, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="SQL AI Copilot sidecar bridge for Valentina Studio workflows.")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")

    schema_parser = subparsers.add_parser("schema")
    schema_parser.add_argument("--database-url", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--sql", required=True)

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--prompt", required=True)
    generate_parser.add_argument("--database-url")
    generate_parser.add_argument("--copy", action="store_true")

    explain_parser = subparsers.add_parser("explain")
    explain_parser.add_argument("--sql", required=True)

    fix_parser = subparsers.add_parser("fix")
    fix_parser.add_argument("--sql", required=True)
    fix_parser.add_argument("--error", required=True)
    fix_parser.add_argument("--copy", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--sql", required=True)
    run_parser.add_argument("--database-url", required=True)

    args = parser.parse_args()

    try:
        if args.command == "status":
            print_json(get_json(args.backend_url, "/api/llm/status"))
            return 0
        if args.command == "schema":
            print_json(post_json(args.backend_url, "/api/db/schema", {"databaseUrl": args.database_url}))
            return 0
        if args.command == "validate":
            print_json(post_json(args.backend_url, "/api/sql/validate", {"sql": args.sql, "allow_write": False}))
            return 0
        if args.command == "generate":
            data = post_json(
                args.backend_url,
                "/api/sql/generate",
                {"prompt": args.prompt, "databaseUrl": args.database_url},
            )
            print_json(data)
            if data.get("sql"):
                maybe_copy(data["sql"], args.copy)
            return 0
        if args.command == "explain":
            print_json(post_json(args.backend_url, "/api/sql/explain", {"sql": args.sql}))
            return 0
        if args.command == "fix":
            data = post_json(args.backend_url, "/api/sql/fix", {"sql": args.sql, "error": args.error})
            print_json(data)
            if data.get("sql"):
                maybe_copy(data["sql"], args.copy)
            return 0
        if args.command == "run":
            print_json(
                post_json(
                    args.backend_url,
                    "/api/sql/run-readonly",
                    {"sql": args.sql, "databaseUrl": args.database_url},
                )
            )
            return 0
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {body}", file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
