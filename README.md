# scholar-rag *(working name)*

Servicio RAG sobre el corpus de tesis de Ingeniería de Sistemas de la Universidad de Córdoba (~271 tesis, vía API DSpace). Pregunta en lenguaje natural → respuesta sintetizada **con citas trazables** a la tesis y sección de origen.

> **Proyecto ancla** de carrera (Backend Python / AI). Pieza de portafolio primero; negocio = upside si valida.
> Discovery docs-first en [`docs/`](docs/). Empezar por [`00-necesidad`](docs/00-necesidad.md).

## Estado

`implementacion` — docs-first (00→04) + plan incremental en [`docs/05-plan-implementacion.md`](docs/05-plan-implementacion.md). **Inc 0-1 + 3 hechos:** scaffold FastAPI por capas + `/health`; ingesta RAG (271 tesis → 575 chunks en Neon+pgvector); **agente LangGraph** (retrieve→grade→generate con citas trazables / fallback sin alucinar, LLM Groq). **VIVO end-to-end** 🟢 — web **https://scholar-rag.pages.dev** → api **https://scholar-rag-api-448285277410.us-east1.run.app** (Cloud Run + Neon+pgvector + LangGraph). Pendiente: dominio propio + analytics (medir si crece), Inc 2 (retrieval de calidad), Inc 5 (evals), Inc 6 (tests/CI).

### Correr (local)
```
cd api && uv sync
cp .env.example .env   # y completar DATABASE_URL (Neon) + CORPUS_PATH
uv run python -m scripts.ingest              # indexa el corpus
uv run python -m scripts.search "tu pregunta"  # busca chunks en el corpus
uv run python -m scripts.ask "tu pregunta"     # respuesta del agente con citas
uv run uvicorn app.main:app --reload         # levanta el api
```

## Stack (lockeado)

FastAPI · Postgres/Neon + pgvector · LangGraph · API DSpace REST · RAGAS + Langfuse · pytest + GitHub Actions · Cloud Run (api) + Cloudflare Pages (web).

## Estructura

```
api/    servicio FastAPI (por capas)
web/    página que consume /ask
docs/   discovery docs-first (00-necesidad → 04-decisiones)
```

## Por qué existe

Cierra en un producto real los 6 gaps que pide el mercado backend/AI y que tumbaron la técnica de EPAM: Python idiomático, FastAPI/Pydantic, DB/índices, testing/CI, arquitectura/SOLID, AI-agentic + eval.
