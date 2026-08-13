# 06 — Corpus y RAG: estado actual + cómo mejorar

> Referencia técnica del pipeline RAG y su roadmap de mejora. Estado a 2026-08-13 (v1 vivo). Complementa [`04-decisiones.md`](04-decisiones.md) (stack lockeado) y [`05-plan-implementacion.md`](05-plan-implementacion.md) (incrementos).

## Estado actual (v1)

| Eje | Hoy | Dónde |
|---|---|---|
| **Corpus** | 271 tesis Ing. Sistemas Unicórdoba. Solo `title + keywords + abstract`, **no el PDF completo** | `Reporting/Scouts/unicordoba-ideas/unicordoba_ideas.json` |
| **Documento a indexar** | `title\nkeywords\nabstract` concatenados por tesis | `api/app/services/corpus.py` → `build_document` |
| **Chunking** | Por caracteres, `size=1000`, `overlap=150`. La mayoría de abstracts = 1 chunk | `corpus.py` → `chunk_text`. 271 tesis → **575 chunks** |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` vía **fastembed local** (sin API key), **384 dim**, multilingüe ES | `api/app/services/embeddings.py` |
| **Vector store** | **pgvector en Postgres/Neon** (no vector DB aparte). Tabla `chunk (embedding vector(384))` + índice **HNSW `vector_cosine_ops`** | Neon `scholar_rag`; schema en el Inc 1 |
| **Retrieval** | top-k (`k=5`) por distancia coseno `<=>`, sin reranking ni hybrid | `api/app/repositories/retrieval_repository.py` |
| **Grade** | Umbral de score coseno (`relevance_min_score=0.35`); si el top no llega → fallback honesto | `api/app/services/rag_graph.py` |

## Cómo mejorar (roadmap, mayor impacto primero)

### 1. Aumentar las fuentes (lo más fácil y de más impacto)
- **Full-text de los PDF** (hoy solo abstract): la API DSpace da los bitstreams (`core/items/<uuid>/bundles` → ORIGINAL → `content.href`). Extraer texto (pdfplumber/pymupdf) → chunking real de documentos largos → respuestas mucho más ricas y citas a sección/página. **El mayor salto de calidad.**
- **Otras comunidades Unicórdoba** (~10: Medicina, Agronomía, Veterinaria, Derecho…): cambiar el `scope` UUID en el dump. Banco por sector.
- **Otros repositorios DSpace** (otras universidades): mismo pipeline, otra `base` URL. El corpus se vuelve multi-institución.
- Guardar `source`/institución en `thesis` para filtrar y citar por fuente.

### 2. Chunking (cuando entre el full-text)
- Con abstracts (hoy) el chunking casi no importa (caben en 1). **Con PDF completo sí:** pasar a chunking por tokens (tiktoken) o por estructura (secciones/párrafos), calibrar `size/overlap` con datos reales. Guardar `page`/`section` en el chunk para citar con precisión.

### 3. Embeddings
- Hoy local 384d (gratis, reproducible). Mejoras posibles: modelo multilingüe más grande (e5-large 1024d, mpnet 768d) o **embeddings de API** (OpenAI `text-embedding-3`, Gemini) = mejor recall, pero suma dependencia/costo y cambia la `dim` (hay que recrear la columna `vector(N)` y re-indexar).

### 4. Retrieval de calidad (Inc 2, pendiente)
- **Reranking** con un cross-encoder (fastembed tiene `TextCrossEncoder`) sobre el top-k → reordena por relevancia real.
- **Hybrid search**: combinar semántico (pgvector) + léxico (full-text `tsvector` de Postgres) con RRF → captura términos exactos que el embedding pierde.
- **Metadata filtering**: filtrar por año/tipo/comunidad antes o después del vector search.

### 5. Calidad y evidencia (Inc 5, pendiente)
- Evals RAGAS (faithfulness, context precision) + tracing Langfuse → medir que las mejoras de arriba suben la calidad, no bajarla a ojo.

## Higiene pendiente
- **Encoding del corpus**: el JSON actual tiene acentos mal codificados en algunos campos. Re-bajar con `dump_unicordoba.py` asegurando UTF-8 antes de escalar el corpus.
- La ingesta hoy lee un JSON ya bajado (`CORPUS_PATH`); idealmente el pipeline baja de DSpace de punta a punta (un comando) para ser 100% reproducible.
