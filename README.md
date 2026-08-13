# scholar-rag *(working name)*

Servicio RAG sobre el corpus de tesis de Ingeniería de Sistemas de la Universidad de Córdoba (~271 tesis, vía API DSpace). Pregunta en lenguaje natural → respuesta sintetizada **con citas trazables** a la tesis y sección de origen.

> **Proyecto ancla** de carrera (Backend Python / AI). Pieza de portafolio primero; negocio = upside si valida.
> Discovery docs-first en [`docs/`](docs/). Empezar por [`00-necesidad`](docs/00-necesidad.md).

## Estado

`discovery + plan` — docs-first completo (00→04) y plan de implementación incremental en [`docs/05-plan-implementacion.md`](docs/05-plan-implementacion.md) (cada incremento = un módulo de `jotive.dev/learn` sobre el corpus real). Próximo: **Inc 0 — scaffold por capas + /health**.

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
