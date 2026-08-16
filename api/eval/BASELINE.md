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

## 2026-08-16 — texto completo (prueba de 1 tesis)

Pipeline nuevo: `services/fulltext.py` resuelve el bundle TEXT de DSpace por uuid (con cache y fallback a metadata), `corpus.build_chunks` arma cuerpo + un chunk de metadata, `ingest.py` lo usa y cuenta fallbacks.

Prueba end-to-end con LEXBOT (`ucordoba/9727`):
- **2 → 107 chunks** (89.653 chars de texto completo).
- Query de contenido *"qué proveedores de IA usó LexBot"* → recupera el chunk del cuerpo con "OpenAI y DeepSeek". Antes imposible (solo abstract indexado).
- Eval global tras la prueba: recall@1 0.881 → **0.952**, recall@3 → **1.000**, MRR → **1.000**. Cuerpo+metadata mejoró sin romper la búsqueda por tema.

Validado el salto "encuentra la tesis" → "responde su contenido". Falta correr la ingesta completa (271 tesis) y medir cuántas caen en fallback (PDF sin bundle TEXT / sin OCR).

## 2026-08-16 — ingesta full-text completa (271 tesis)

- **9392 chunks** (de 575), promedio **34.7 por tesis** (de 2.12).
- **93 tesis con texto completo, 178 en fallback (66%)**: sus PDFs no tienen bundle TEXT usable en DSpace (escaneados sin OCR). Es el techo real de cobertura de contenido del corpus.

Eval (gold de 14 preguntas de tema, nivel tesis):

| retriever    | recall@1 | recall@3 | recall@5 | MRR   |
|--------------|----------|----------|----------|-------|
| solo metadata| 0.952    | 1.000    | 1.000    | 1.000 |
| full-text    | 0.810    | 1.000    | 1.000    | 0.917 |

**Trade-off medido:** recall@1 bajó 0.952 → 0.810. Con 16x más contenido entra ruido en la posición #1 (otra tesis menciona el tema de pasada). recall@3 se mantiene en 1.000: la tesis correcta sigue en el top-3, que es lo que consume el LLM. Se ganó capacidad de responder contenido (probado en LEXBOT: query "APIs de OpenAI/DeepSeek" ahora recupera el chunk del cuerpo) a cambio de algo de precisión en el #1 a nivel tesis.

## 2026-08-16 — eval de contenido (nivel pasaje)

Nuevo instrumento: `dataset_content.py` (6 preguntas de contenido con el pasaje esperado), `metrics.content_hit_at_k` (verifica que un chunk de la tesis correcta contiene la respuesta, accent-insensitive, robusto a re-ingestas), `run_content.py`. `c.id` ahora expuesto en `retrieval_repository`.

| retriever    | content-hit@1 | @3    | @5    |
|--------------|---------------|-------|-------|
| vector-only  | 0.667         | 0.833 | 1.000 |
| hybrid-rrf   | 0.833         | 1.000 | 1.000 |

**Insight:** con preguntas de contenido el híbrido **supera claramente** al vector (hit@1 0.83 vs 0.67, hit@3 1.0 vs 0.83). El gold de tema no lo mostraba (ahí eran idénticos porque la respuesta estaba en el título). Esto justifica con datos el `hybrid_search` + el fix `unaccent`: aportan justo donde importa, en recuperar el pasaje correcto del cuerpo. El pasaje que responde está en el top-3 del híbrido el 100% de las veces.

## 2026-08-16 — faithfulness (¿alucina?)

`run_faith.py`: corre el grafo completo (retrieve→grade→generate contra el gateway LLM) sobre las 6 preguntas de contenido, y un juez LLM descompone cada respuesta en afirmaciones y verifica cuántas soporta el contexto.

- **mean faithfulness = 1.000** sobre 6 respuestas grounded (ninguna cayó en fallback). Las respuestas son correctas y ancladas en los pasajes.

**Límites honestos (no vender el 1.0 como perfecto):**
1. **Self-judging bias:** el juez es el mismo modelo (llama-3.3-70b) que genera. Un modelo juzgándose tiende a ser indulgente; el 1.0 hay que **confirmarlo con un juez independiente más fuerte** (ej. Claude/GPT-4) antes de creerlo.
2. **Set chico y fácil:** 6 preguntas, todas con respuesta clara en el corpus. El caso duro (preguntas sin respuesta en el corpus) se mide abajo.

## 2026-08-16 — adversarial (¿rechaza o inventa?)

`run_adversarial.py`: 6 preguntas cuya respuesta NO está en el corpus (Marte, paella, mundial 86, submarinos, trading cripto, reserva de vuelos). Mide si el sistema hace fallback o alucina.

- **refusal rate: 5/6 = 0.833.** Una alucinación real: *"cuál es la distancia de la Tierra a Marte"* → el LLM respondió "56 a 401 millones de km" con conocimiento propio, no del corpus.

**Hallazgos (los adversariales rompieron dos cosas):**
1. **El `grade` node no filtra nada.** Las 6 dieron `grounded=True` con `best_cosine` 0.44–0.63, todas sobre el umbral `relevance_min_score=0.35`. Con el modelo de embeddings multilingüe, hasta preguntas totalmente ajenas puntúan alto en coseno; el umbral 0.35 nunca discrimina. El nodo es decorativo.
2. **La defensa anti-alucinación real es el prompt, no la arquitectura.** Los 5 rechazos vienen de la instrucción "si el contexto no alcanza, dilo" en `generate`, no del `grade`. Es frágil: depende del LLM. Marte se le escapó porque es un hecho tan común que el modelo lo suelta sin dudar — patrón típico: los hechos generales muy conocidos escapan al grounding.

**Fix identificado:** recalibrar el `grade` (el umbral cosine no sirve; probar el score RRF, un margen relativo, o un grade basado en LLM) para atrapar out-of-domain antes de `generate`, en vez de confiar en que el prompt aguante.

## 2026-08-16 — fix del grade node (grade-by-LLM)

Reemplazado el `grade` de umbral cosine por un grade con LLM: le pregunta al modelo si el contexto recuperado realmente responde la pregunta (structured output `Relevance{relevant: bool}`).

Antes/después medido:

| eval                     | antes (cosine 0.35) | después (grade-by-LLM) |
|--------------------------|---------------------|------------------------|
| adversarial refusal      | 5/6 = 0.833         | **6/6 = 1.000**        |
| content hit@3 (in-domain)| 1.000               | 1.000 (sin regresión)  |
| faithfulness             | 1.000               | 1.000                  |

La alucinación de Marte desapareció (ahora `grounded=False` → fallback). El grade-by-LLM discrimina out-of-domain donde el coseno no podía, y no rechazó ninguna pregunta válida.

**Trade-off honesto:** agrega una llamada LLM por query (el grade ya no es instantáneo). Cada consulta hace ahora 1 llamada (si rechaza) o 2 (grade + generate). Es el costo de la robustez; el impacto en latencia/costo se cuantifica en la pregunta 3 del capstone (pendiente).

### Pendiente
2. **Cobertura:** 66% del corpus sin texto. Si importa, evaluar OCR de los PDFs escaneados (costo aparte) o marcar esas tesis como "solo metadata" en la UI.
3. **Precisión@1:** si el #1 exacto importa para el producto, un reranker (M3) sobre el top-k recuperaría la precisión perdida sin sacrificar el recall de contenido.
2. **Corregir el curso M2:** afirmaba "probablemente no hay índice ANN"; la BD sí tiene `chunk_embedding_idx` HNSW. Ajustar el material publicado.
3. **Expandir el gold** a 50+ preguntas (con tildes y sin, términos exactos) para medición más robusta.
