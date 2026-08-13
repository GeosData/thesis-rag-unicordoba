# 05 — Plan de implementación (incremental)

> Cada incremento = un módulo de la ruta `dev.jotive.com.co/learn` aplicado al corpus real de scholar-rag. Estudiar la ruta y construir el capstone son la misma actividad: la ruta da el *entender/fijar*, este proyecto da el *aplicar/defender* que el mercado verifica en técnica.
>
> Orden por dependencia (cada uno se apoya en el anterior). Un incremento no está "hecho" hasta pasar su **salida verificable**. No se avanza al siguiente con el anterior a medias.
>
> Corpus: 271 tesis Ing. Sistemas Unicórdoba, ya bajadas en `Reporting/Scouts/unicordoba-ideas/` (`unicordoba_ideas.json` + `dump_unicordoba.py` re-ejecutable). Stack lockeado en [`04-decisiones.md`](04-decisiones.md). Alcance v1 en [`03-alcance.md`](03-alcance.md).

---

## Inc 0 — Scaffold + config por capas ✅ HECHO
**Módulo ruta:** A0 (build step FastAPI) + arquitectura por capas (D6, ref `api-newsletter`).
**Estado:** `api/app/` con las 6 capas cableadas (config/routes/controllers/services/repositories/middleware), `Settings` pydantic-settings, pool asyncpg lazy, `GET /health` atraviesa las capas y responde 200 (`database: not_configured` sin `DATABASE_URL`, `up`/`down` con Neon). Dockerfile uv. Verificado con TestClient.
**Gap que cierra:** arquitectura/SOLID (razón rechazo EPAM) + FastAPI/Pydantic.
**Construir:** estructura `config / routes / controllers / services / repositories / middleware`, bootstrap separado de la lógica, `Settings` Pydantic (env: Neon URL, LLM keys), endpoint `/health`, conexión a Neon verificada.
**Salida verificable:** `uvicorn` levanta, `GET /health` responde 200 con estado de DB, capas vacías pero cableadas.

## Inc 1 — Ingesta del corpus (RAG core) ✅ HECHO
**Módulo ruta:** A1 (chunking, embeddings, pgvector).
**Estado:** DB `scholar_rag` en Neon (proyecto geosdata-platform) con pgvector + índice HNSW cosine. Tablas `thesis` (metadata) + `chunk` (contenido + `vector(384)`). Pipeline `scripts/ingest.py` (un comando: `uv run python -m scripts.ingest`) lee el corpus, chunkea (title+keywords+abstract), embeddings locales fastembed (`paraphrase-multilingual-MiniLM-L12-v2`, sin API key), upsert idempotente. **271 tesis → 575 chunks indexados.** Búsqueda semántica verificada con `scripts/search.py` (retrieval relevante: "riego automatizado" → tesis de riego por goteo). Pendiente futuro: full-text del PDF (hoy solo abstract) + re-bajar corpus con encoding limpio.
**Gap:** RAG + vector DB (máxima demanda de mercado).
**Construir:** pipeline reproducible (un comando) que reusa `dump_unicordoba.py` → metadata + PDF vía API DSpace → extrae texto → chunkea con metadata de origen (tesis, autor, año, sección) → embeddings → `pgvector`. Tablas: `thesis` (metadata) + `chunk` (texto + embedding + FK a thesis).
**Salida verificable:** comando único indexa las 271 tesis; retrieval top-k por consola devuelve chunks con su origen trazable.

## Inc 2 — Retrieval de calidad
**Módulo ruta:** A2 (reranking, hybrid search RRF, metadata filtering).
**Gap:** RAG avanzado.
**Construir:** sobre el retrieval base, hybrid search + reranking + filtrado por metadata (año/sección).
**Salida verificable:** para 5 preguntas de prueba, los chunks recuperados son relevantes y cada uno arrastra su cita de origen.

## Inc 3 — Grafo LangGraph (el corazón) ✅ HECHO
**Módulo ruta:** A3 (StateGraph, conditional edges, límite de pasos) + A0 (structured output para citas).
**Estado:** grafo `retrieve → grade → (generate | fallback)` en `app/services/rag_graph.py`. LLM = Groq `llama-3.3-70b-versatile` (`with_structured_output` sobre schema `Answer`+`Citation`, temperature 0). `grade` usa umbral de score coseno (`relevance_min_score=0.35`): si el top chunk no llega, ruta a `fallback` honesto y NO alucina. Verificado con `scripts/ask.py`: pregunta del corpus → respuesta sintetizada de 2 tesis reales con citas trazables (handle exacto); "capital de Francia" → fallback. **Nota:** se saltó el Inc 2 (retrieval de calidad) para llegar antes al corazón; queda pendiente como mejora (reranking/hybrid).
**Gap:** agentic/LangGraph (gap #1 de demanda) + LLM apps prod.
**Construir:** grafo `retrieve → grade relevancia → generate → forzar citas (structured output) → fallback`. Si no hay contexto suficiente responde "no encontré evidencia" (no alucina). Estado tipado, END sentinel real, límite de pasos.
**Salida verificable:** el grafo responde una pregunta con citas trazables (tesis + sección enlazada a DSpace) o el fallback honesto; se puede explicar por qué es grafo y no cadena.

## Inc 4 — API /ask
**Módulo ruta:** A6 (FastAPI async, guardrails, rate-limit).
**Gap:** producción AI.
**Construir:** endpoint `/ask` público con rate-limit, I/O Pydantic tipado, integra el grafo del Inc 3 por las capas del Inc 0.
**Salida verificable:** `POST /ask` con una pregunta real devuelve respuesta + lista de citas por HTTP, con rate-limit activo.

## Inc 5 — Evals + observabilidad
**Módulo ruta:** A5 (RAGAS, LLM-as-judge, Langfuse).
**Gap:** LLM eval (lo que distingue de un demo de fin de semana).
**Construir:** set de eval con RAGAS (faithfulness + context precision) que gatea; tracing Langfuse en el grafo.
**Salida verificable:** score RAGAS baseline registrado, traces visibles en Langfuse, el eval corre como gate (regression gate).

## Inc 6 — Testing + CI
**Módulo ruta:** M1 (pytest) + D7.
**Gap:** testing/CI (default senior, gap EPAM).
**Construir:** pytest unit (chunking, grading) + integration (retrieval sobre DB de test) + API (`/ask`, `/health`); GitHub Actions.
**Salida verificable:** CI verde, caminos críticos cubiertos, PR no mergeable con CI roja.

## Inc 7 — Web
**Módulo ruta:** front (skills de diseño, sin look IA-default).
**Gap:** entrega completa punta a punta (no "MVP mínimo").
**Construir:** página que consume `/ask`, muestra respuesta + citas enlazadas a la tesis en DSpace. Identidad propia, iconos, no UI plana.
**Salida verificable:** la web corre local consumiendo la API, respuesta + citas navegables.

## Inc 8 — Deploy (terminado v1)
**Módulo ruta:** A6 + paved-road deploy (D8).
**Gap:** deploy real con dominio.
**Construir:** api → Cloud Run + Neon; web → Cloudflare Pages; dominio; ADR final de región/costos.
**Salida verificable (= definición de terminado v1 de [`03-alcance.md`](03-alcance.md)):** deploy vivo respondiendo preguntas reales del corpus con citas correctas, CI verde, RAGAS baseline registrado, README + handbook + ADR contables en entrevista sin abrir el código.

---

## Cómo se usa este plan
- Un incremento a la vez, en orden. El módulo de la ruta se estudia (entender/fijar) y acto seguido se aplica acá sobre el corpus real (aplicar).
- Al cerrar cada incremento: se puede explicar en EN, sin mirar, la decisión central de ese incremento (regla de dominio, [[Plan-Profundidad-Tecnica]]).
- Los incrementos 0-3 son el núcleo defendible mínimo (RAG + agente con citas). 4-8 lo vuelven producto y evidencia de entrevista.
