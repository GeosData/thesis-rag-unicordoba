from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from app.config.settings import get_settings

MIN_USABLE_CHARS = 500
_WHITESPACE = re.compile(r"[ \t]+")
_BLANKLINES = re.compile(r"\n\s*\n\s*")


def _get_json(url: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_text(url: str, timeout: int = 60) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _normalize(text: str) -> str:
    text = _WHITESPACE.sub(" ", text)
    text = _BLANKLINES.sub("\n", text)
    return text.strip()


def _cache_path(uuid: str) -> Path:
    cache_dir = Path(get_settings().fulltext_cache)
    return cache_dir / f"{uuid}.txt"


def _text_bitstream_url(base: str, uuid: str) -> str | None:
    bundles = _get_json(f"{base}/core/items/{uuid}/bundles")
    text_href = None
    for bundle in bundles.get("_embedded", {}).get("bundles", []):
        if bundle.get("name") == "TEXT":
            text_href = bundle["_links"]["bitstreams"]["href"]
    if not text_href:
        return None
    bitstreams = _get_json(text_href).get("_embedded", {}).get("bitstreams", [])
    if not bitstreams:
        return None
    return bitstreams[0]["_links"]["content"]["href"]


def fetch_fulltext(uuid: str) -> str | None:
    cached = _cache_path(uuid)
    if cached.exists():
        text = cached.read_text(encoding="utf-8")
        return text if len(text) >= MIN_USABLE_CHARS else None
    try:
        content_url = _text_bitstream_url(get_settings().dspace_api_base, uuid)
        if not content_url:
            return None
        text = _normalize(_get_text(content_url))
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return None
    if len(text) < MIN_USABLE_CHARS:
        return None
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(text, encoding="utf-8")
    return text
