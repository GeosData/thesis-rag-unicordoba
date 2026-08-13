# scholar-rag *(working name)*

Servicio RAG sobre el corpus de tesis de Ingeniería de Sistemas de la Universidad de Córdoba (~271 tesis, vía API DSpace). Pregunta en lenguaje natural → respuesta sintetizada **con citas trazables** a la tesis y sección de origen.

> **Proyecto ancla** de carrera (Backend Python / AI). Pieza de portafolio primero; negocio = upside si valida.
> Discovery docs-first en [`docs/`](docs/). Empezar por [`00-necesidad`](docs/00-necesidad.md).

## Estado

`implementacion` — docs-first (00→04) + plan incremental en [`docs/05-plan-implementacion.md`](docs/05-plan-implementacion.md). **Inc 0 hecho:** scaffold FastAPI por capas + `/health` (verificado 200). Próximo: **Inc 1 — ingesta RAG core** (chunking + embeddings + pgvector sobre el corpus).

### Correr el api (local)
```
cd api && uv sync && uv run uvicorn app.main:app --reload
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
