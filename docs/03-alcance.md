# 03 — Alcance

> Alcance v1 **completo y cómodo** (no "MVP mínimo"): la experiencia se entrega funcionando de punta a punta. Se recorta amplitud de corpus/features, no la calidad de lo que sí entra.

## Usuario y caso central

Tesista/estudiante de Ing. Sistemas Unicórdoba (y por extensión, cualquiera investigando lo local) que pregunta en lenguaje natural y recibe una respuesta con citas trazables.

**Flujo v1:** pregunta → retrieval sobre el corpus indexado → respuesta sintetizada + lista de citas (tesis, autor, año, sección/página) enlazadas a la fuente en DSpace.

## Dentro de v1

- **Ingesta:** pipeline que baja tesis vía API DSpace (metadata + PDF), extrae texto, chunkea con metadata de origen, embeddings → pgvector. Reproducible (un comando).
- **Retrieval + generación:** orquestado en LangGraph (retrieve → grade relevancia → generate → forzar citas con structured output). Fallback si no hay contexto suficiente ("no encontré evidencia", no alucina).
- **API:** FastAPI, endpoint `/ask` (público, con rate-limit) + `/health`. Pydantic para I/O tipado.
- **Web:** una página que consume `/ask` y muestra respuesta + citas. Simple, sin look IA-default.
- **Calidad:** suite pytest (unit + integration + API) + CI en GitHub Actions. Eval RAGAS (faithfulness/context precision) + tracing Langfuse.
- **Arquitectura por capas** (config/routes/controllers/services/repositories) + 1 ADR de decisiones clave.

## Fuera de v1 (backlog)

- Corpus más allá de Ing. Sistemas Unicórdoba (otras facultades/universidades).
- Auth de usuarios / cuentas (v1 es `/ask` público con rate-limit).
- Multi-idioma, re-ranking avanzado, conversación multi-turno con memoria.
- Panel de administración / re-indexado incremental automático.

## Definición de "terminado v1"

- Deploy vivo con dominio, respondiendo preguntas reales del corpus con citas correctas.
- CI verde, cobertura de los caminos críticos, score RAGAS baseline registrado.
- README + handbook + ADR → contable en una entrevista técnica sin abrir el código.
