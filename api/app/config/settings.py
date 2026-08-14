from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "scholar-rag"
    environment: str = "development"
    database_url: str | None = None
    corpus_path: str = ""
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    fastembed_cache: str | None = None
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    gateway_url: str = "https://llm-quota-gateway-448285277410.us-east1.run.app/v1"
    gateway_model: str = "meta-llama/llama-3.3-70b-instruct"
    retrieval_top_k: int = 5
    relevance_min_score: float = 0.35


@lru_cache
def get_settings() -> Settings:
    return Settings()
