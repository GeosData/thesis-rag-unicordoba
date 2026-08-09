# 04 — Decisiones (stack lockeado)

> Estilo ADR condensado. Cada decisión con alternativa considerada + razón. Decisiones de stack no se reabren sin trigger + ADR nuevo (anti-churn).

## D1 — Lenguaje/framework API: **Python + FastAPI**
- Alternativas: Node/Express (stack fuerte de Josse), Django.
- Razón: el proyecto ancla existe para consolidar Python idiomático + FastAPI/Pydantic (gap de mercado y de EPAM). Node sería cómodo pero no mueve el objetivo de carrera. Async nativo encaja con I/O de LLM/DB.

## D2 — Vector store: **Postgres (Neon) + pgvector**
- Alternativas: Pinecone/Weaviate (dedicados), Chroma (local).
- Razón: dentro del paved-road de datos (SQL = Neon). Un solo motor para datos relacionales (metadata de tesis) + vectores. pgvector es exactamente lo que piden las ofertas. Menos infra que un vector DB aparte.

## D3 — Orquestación: **LangGraph**
- Alternativas: cadena lineal LangChain, orquestación a mano.
- Razón: el flujo retrieve→grade→generate→cite con fallback es un grafo con estado, no una cadena. LangGraph es el gap #1 de demanda del mercado. Se ejercita en contexto real, no en tutorial.

## D4 — Ingesta: **API DSpace REST v7**
- Alternativas: scraping web (bloqueado por BunkerWeb), descarga manual.
- Razón: la API responde y la web no. Pipeline reproducible por API > manual.

## D5 — Eval + observabilidad: **RAGAS + Langfuse**
- Alternativas: sin eval (demo-grade), solo logs.
- Razón: "servicio con eval de calidad" es narrativa senior y cierra el gap LLM-eval. Distingue de un demo de fin de semana.

## D6 — Arquitectura: **por capas** (config / routes / controllers / services / repositories / middleware)
- Alternativas: todo en un `main.py` (demo-grade).
- Razón: el gap "arquitectura/SOLID" fue razón explícita de rechazo EPAM. `server`/bootstrap separado de la lógica. `api-newsletter` como referencia de estructura.

## D7 — CI/CD + testing: **GitHub Actions + pytest** (unit/integration/API)
- Razón: default senior, no nice-to-have. Gap EPAM. Sin CI verde no se considera "terminado".

## D8 — Deploy: **API → GCP Cloud Run + Neon; web/estático → Cloudflare Pages**
- Razón: paved-road de deploy para APIs Python. CF Workers no corre Python. (El ADR final confirma región/costos al llegar a deploy.)

## D9 — Git/repo: **main, SSH, monorepo** `api/` `web/` `docs/`
- Razón: convenciones estándar del ecosistema. Push a GitHub cuando el nombre final esté decidido (`02-nombres.md`).

## Pendientes de decisión (no bloquean arranque)
- Modelo LLM concreto (candidato: Gemini Flash por costo/volumen para generación; embeddings a definir).
- Nombre final del producto → `02-nombres.md`.
- Estrategia de chunking (tamaño/overlap) → se calibra con datos reales en la primera iteración.
