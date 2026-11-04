# thesis-rag-unicordoba

Servicio RAG sobre el corpus de tesis de Ingeniería de Sistemas de la Universidad de Córdoba (~271 tesis, vía API DSpace). Pregunta en lenguaje natural → respuesta sintetizada **con citas trazables** a la tesis y sección de origen.

> **Proyecto ancla** de carrera (Backend Python / AI). Pieza de portafolio primero; negocio = upside si valida.
> Discovery docs-first en [`docs/`](docs/). Empezar por [`00-necesidad`](docs/00-necesidad.md).

## Estado

`implementacion` — docs-first (00→04) + plan incremental en [`docs/05-plan-implementacion.md`](docs/05-plan-implementacion.md). **Inc 0-1 + 3 hechos:** scaffold FastAPI por capas + `/health`; ingesta RAG (271 tesis → 575 chunks en Neon+pgvector); **agente LangGraph** (retrieve→grade→generate con citas trazables / fallback sin alucinar, LLM Groq). **VIVO end-to-end** 🟢 — web **https://scholar-rag.pages.dev** → api **https://scholar-rag-api-448285277410.us-east1.run.app** (Cloud Run + Neon+pgvector + LangGraph). **Analytics de producto:** cada pregunta se registra (tabla `query_log`), métricas en `GET /stats` (total, % con evidencia, últimas preguntas). **Inc 6 hecho:** tests pytest (retrieval y grafo con LLM stubbeado) + workflow CI. **Inc 2 hecho:** hybrid search (vector + léxico con RRF). Pendiente: web analytics CF (1 toggle), dominio propio, Inc 5 (evals RAGAS).

**Subir cambios rápido:** ver [`docs/DEPLOY.md`](docs/DEPLOY.md) (api → Cloud Run, web → CF Pages, 1 comando cada uno).

### Correr (local)

Requisitos: Python 3.12+, [`uv`](https://docs.astral.sh/uv/), y para el flujo completo una base Postgres con la extensión `pgvector` (p. ej. Neon).

```
cd api
uv sync
cp .env.example .env   # y completar las variables (ver tabla)
uv run python -m scripts.ingest              # indexa el corpus
uv run python -m scripts.search "tu pregunta"  # busca chunks en el corpus
uv run python -m scripts.ask "tu pregunta"     # respuesta del agente con citas
uv run uvicorn app.main:app --reload         # levanta el api en http://127.0.0.1:8000
```

Sin `DATABASE_URL` el api arranca igual (`/health` responde `database: not_configured`), pero `/ask` y `/stats` fallan porque necesitan la base.

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | para `/ask`, `/stats`, ingesta | `postgresql://user:password@host/dbname` |
| `CORPUS_PATH` | solo para ingesta | JSON del corpus (lista de tesis con `uuid`, `title`, `author`, `advisor`, `year`, `type`, `keywords`, `abstract`, `handle`) |
| `GATEWAY_URL` / `GATEWAY_MODEL` | no | endpoint compatible con OpenAI que usa el LLM; tiene valor por defecto en `app/config/settings.py` |
| `EMBEDDING_MODEL` / `FASTEMBED_CACHE` | no | modelo fastembed (se descarga en el primer uso) y su directorio de caché |
| `RETRIEVAL_TOP_K` | no | chunks recuperados por pregunta (por defecto 5) |

Las variables se leen del entorno o de `api/.env` (no se versiona).

**Base de datos:** usa las tablas `thesis`, `chunk` (con columnas `embedding vector` y `tsv` generada) y `query_log`. El DDL base no está en el repo; solo la migración [`api/migrations/001_fts_unaccent.sql`](api/migrations/001_fts_unaccent.sql), que debe aplicarse sobre una base que ya tenga esas tablas.

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | estado del servicio y de la base |
| `POST` | `/ask` | body `{"question": "..."}` (máx. 2000 caracteres, 10 req/min por IP) → `{"answer", "citations": [{"title", "handle"}], "grounded"}`; si no hay evidencia, `grounded=false` y sin citas |
| `GET` | `/stats` | total de preguntas, % con evidencia y últimas preguntas |

Docs interactivos en `/docs` cuando el api está corriendo.

### Tests

```
cd api
uv run pytest -q
```

No necesitan red, base de datos ni claves: el LLM, los embeddings y el repositorio de retrieval se reemplazan por stubs (`api/tests/conftest.py`). Cubren el grafo `retrieve → grade → generate/fallback` (citas presentes, fallback sin evidencia, errores propagados, texto recuperado delimitado contra prompt injection) y la API HTTP. El workflow de CI (`.github/workflows/ci.yml`) ejecuta lo mismo en cada push a `main` y en cada PR.

### Docker

```
cd api
docker build -t scholar-rag-api .
docker run --rm -p 8080:8080 --env-file .env scholar-rag-api
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
