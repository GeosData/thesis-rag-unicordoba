# Baseline de retrieval — scholar-rag

Primer número medido. El "antes" contra el que se comparan las mejoras del mapa de profundidad.

## 2026-08-15 — baseline inicial

Corpus: 271 tesis, 575 chunks. Gold: 14 preguntas, métrica a nivel tesis (handle), retrieve_k=10.

| retriever    | recall@1 | recall@3 | recall@5 | MRR   | p50 ms |
|--------------|----------|----------|----------|-------|--------|
| vector-only  | 0.881    | 0.929    | 0.929    | 0.929 | 156    |
| hybrid-rrf   | 0.881    | 0.929    | 0.929    | 0.929 | 156    |

### Hallazgos (investigados)

1. **CONFIRMADO — el "hybrid search" no es híbrido: la rama full-text está rota por acentos.**
   El corpus tiene tildes ("orientación"), pero `websearch_to_tsquery('spanish', ...)` es sensible a acentos y la extensión `unaccent` **no está instalada**. Evidencia: `"orientacion"` (sin tilde) → 0 matches; `"orientación"` (con tilde) → 49 matches. Como los usuarios (y el gold) escriben sin tildes, la rama léxica casi nunca matchea, y el `hybrid_search` colapsa a solo-vector. Por eso `hybrid-rrf` == `vector-only` en la tabla. **Fix:** instalar `unaccent` y aplicarlo al generar `tsv` (ingest) y en la `tsquery` (retrieval). Medible: re-correr el eval con y sin el fix.
2. **CONFIRMADO — el miss de LEXBOT es consecuencia del hallazgo 1.** Su chunk contiene literalmente "orientación legal básica dirigida a ciudadanos", pero el vector no lo trae al top-10 y el rescate léxico está muerto por los acentos. Con `unaccent`, este miss debería desaparecer.
3. **DESCARTADO — no hay mismatch de embeddings.** Verificado: `cos(embedding_almacenado, embedding_recalculado) = 1.0000` en varios chunks (passage y query). fastembed 0.8.0 reproduce exactamente lo ingerido; el warning de mean pooling es inocuo aquí.
4. **ESTRUCTURAL — el corpus indexado es casi solo título + resumen.** 575 chunks para 271 tesis = **2.12 chunks/tesis**, y **73 tesis tienen un solo chunk**. El RAG puede encontrar la tesis por su tema, pero no responder detalles del contenido porque el texto completo no está indexado. Es el techo real del producto (chunking/ingesta, M3).

## 2026-08-15 — después del fix `unaccent`

Aplicado: extensión `unaccent` + config de búsqueda `spanish_unaccent` (normaliza acentos en `tsv` y en la `tsquery`). Migración en `migrations/001_fts_unaccent.sql`; query actualizada en `retrieval_repository.py`.

| retriever    | recall@1 | recall@3 | recall@5 | MRR   | p50 ms |
|--------------|----------|----------|----------|-------|--------|
| vector-only  | 0.881    | 0.929    | 0.929    | 0.929 | 158    |
| hybrid-rrf   | 0.881    | **1.000**| **1.000**| **0.964** | 156 |

**Resultado medido:** el híbrido pasó de idéntico a vector (léxico muerto) a superarlo — recall@3/5 de 0.929 a **1.000**, MRR de 0.929 a **0.964**. LEXBOT deja de perderse en el híbrido. `vector-only` intacto (control). El "hybrid search" ahora sí es híbrido.

Este es el primer antes/después de mejora medida: material directo para el design doc y el post del capstone.

### Pendiente

1. **Estructural (el techo real):** 2.12 chunks/tesis, 73 tesis con un solo chunk. El corpus es casi solo título + resumen; el RAG encuentra la tesis pero no responde su contenido. Decidir si se ingiere el texto completo (subir el nº de chunks).
2. **Corregir el curso M2:** afirmaba "probablemente no hay índice ANN"; la BD sí tiene `chunk_embedding_idx` HNSW. Ajustar el material publicado.
3. **Expandir el gold** a 50+ preguntas (con tildes y sin, términos exactos) para medición más robusta.
