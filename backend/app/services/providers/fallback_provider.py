from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel

from app.services.providers.base import LLMProvider
from app.services.providers.json_utils import validate_json_payload


class FallbackProvider(LLMProvider):
    name = "fallback"
    model_name = "deterministic"

    def is_available(self) -> bool:
        return True

    async def health_check(self) -> tuple[bool, str]:
        return True, "Deterministic fallback provider is always available."

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return self._build_payload(user_prompt)["content"]

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        return validate_json_payload(self._build_payload(user_prompt), response_model)

    def _build_payload(self, prompt: str) -> dict[str, Any]:
        text = prompt.lower()
        if "generate safe postgresql sql" in text:
            table = self._first_context_table(prompt)
            sql = f"SELECT * FROM {table} LIMIT 100" if table else "SELECT 1 AS sample_value LIMIT 1"
            return {
                "content": "Fallback mode generated a conservative read-only starting point. Review table and column names before running it.",
                "sql": sql,
                "warnings": ["Fallback mode cannot infer full business semantics."],
            }
        if "optimiz" in text:
            return {
                "content": "Fallback mode suggests checking predicates, indexes, and whether the query can use a narrower SELECT list or stricter filters.",
                "sql": None,
                "warnings": ["No LLM optimization reasoning was used."],
            }
        if "explain" in text:
            return {
                "content": "This looks like a read-only PostgreSQL query intended to inspect data. Review predicates, joins, and limits to understand scope and cost.",
                "sql": None,
                "warnings": [],
            }
        if "fix" in text or "error" in text:
            return {
                "content": "Fallback mode cannot deeply repair SQL, but you should verify column names, aliases, commas, join conditions, and PostgreSQL-specific syntax.",
                "sql": None,
                "warnings": ["Fallback repair is heuristic only."],
            }
        if "summarize" in text or "result" in text:
            return {
                "content": "Fallback mode can only provide a lightweight result summary. Inspect the returned rows and key columns directly.",
                "sql": None,
                "warnings": ["No LLM summarization was performed."],
            }
        if "schema" in text:
            return {
                "content": "Fallback mode can help navigate schema metadata already loaded by the backend, but it will not infer business semantics reliably.",
                "sql": None,
                "warnings": [],
            }
        return {
            "content": "Fallback mode generated a conservative read-only starting point. Review table and column names before running it.",
            "sql": "SELECT 1 AS sample_value LIMIT 1",
            "warnings": ["Fallback mode cannot infer the exact schema semantics."],
        }

    def _first_context_table(self, prompt: str) -> str | None:
        match = re.search(r"^-\s+([a-zA-Z_][\w]*\.[a-zA-Z_][\w]*)\s+\[", prompt, re.MULTILINE)
        return match.group(1) if match else None
