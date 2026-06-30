from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def mask_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return None
    parsed = urlparse(database_url)
    if parsed.username is None:
        return database_url
    password = "****" if parsed.password else ""
    auth = parsed.username
    if password:
        auth = f"{auth}:{password}"
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    netloc = f"{auth}@{host}"
    return urlunparse(parsed._replace(netloc=netloc))
