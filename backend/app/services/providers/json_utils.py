from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ValidationError

from app.services.providers.base import ProviderError


def _extract_json_candidate(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def validate_json_payload(payload: dict[str, Any], response_model: type[BaseModel] | None) -> dict[str, Any]:
    if response_model is None:
        return payload
    try:
        validated = response_model.model_validate(payload)
    except ValidationError as exc:
        raise ProviderError(f"Structured provider response failed validation: {exc}") from exc
    return validated.model_dump()


def parse_json_payload(text: str, response_model: type[BaseModel] | None = None) -> dict[str, Any]:
    candidate = _extract_json_candidate(text)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Provider returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProviderError("Provider JSON response must be an object.")
    return validate_json_payload(payload, response_model)


def build_json_repair_prompt(text: str) -> str:
    return (
        "Repair the following content into a strict JSON object only. "
        "Do not add markdown fences or commentary.\n\n"
        f"{text}"
    )
