from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config.settings import get_settings


@lru_cache
def get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        base_url=settings.gateway_url,
        api_key="gateway",
        model=settings.gateway_model,
        temperature=0,
        default_headers={"X-Tenant-ID": "thesis-rag"},
    )
