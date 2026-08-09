# 01 — Estado del arte

> Qué existe hoy para "preguntarle a un corpus de investigación" y por qué no cubre este caso.

## Alternativas existentes

| Solución | Qué hace | Por qué no resuelve esto |
|---|---|---|
| **Búsqueda DSpace nativa** | Filtra por metadata (título, autor, keyword) | No entiende significado; no responde preguntas; no cita párrafos |
| **Google Scholar / Google** | Indexa lo público de la web | El repositorio local no rankea; la web pública está bloqueada (BunkerWeb) |
| **ChatPDF / AskYourPDF** | RAG sobre 1 PDF que subís | Un documento a la vez, no un corpus; sin ingesta automatizada ni citas trazables a fuente institucional |
| **NotebookLM** | RAG multi-doc de Google | Subida manual, sin pipeline reproducible, sin control de infra/eval, no es un servicio propio |
| **Perplexity** | Búsqueda web con citas | No indexa un corpus privado/local cerrado |

## Hueco

Ninguna indexa **un corpus institucional local cerrado** (accesible solo por API DSpace) con:
- ingesta reproducible (pipeline, no subida manual),
- respuestas con **citas trazables** a tesis + sección/página,
- infra propia + **evaluación de calidad** del retrieval (faithfulness, precisión de contexto).

## Referencias técnicas a estudiar (alimenta 04-decisiones)

- DSpace REST API v7 (endpoints de items/bitstreams para bajar PDFs + metadata).
- Patrones RAG con citas: chunking con metadata de origen, re-ranking, structured output para forzar el modelo a citar.
- pgvector sobre Postgres (Neon) para el vector store — dentro del paved-road de datos.
- LangGraph para orquestar el flujo retrieve→grade→generate→cite (vs cadena lineal).
- Eval: RAGAS (faithfulness, context precision) + Langfuse (tracing) — cierra el gap "LLM eval" del mercado.
