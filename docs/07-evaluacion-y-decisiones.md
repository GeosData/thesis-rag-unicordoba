# 07 — Evaluación y decisiones de diseño

Este documento explica las decisiones de diseño del sistema de recuperación y generación, cada una respaldada por medición. Las cifras crudas y su bitácora viven en `api/eval/BASELINE.md`; el harness que las produce, en `api/eval/`.

Principio que ordena todo: **no se optimiza lo que no se mide**. El primer trabajo fue construir el instrumento (un dataset gold + métricas reproducibles), no tocar el retrieval. Cada decisión posterior se defendió con un número antes/después.

---

## Arquitectura

- **API:** FastAPI por capas (`routes / controllers / services / repositories`).
- **Datos:** Postgres + pgvector. Tabla `chunk` con `embedding` (índice HNSW) y `tsv` (índice GIN para full-text).
- **Embeddings:** FastEmbed local, modelo multilingüe (384 dimensiones).
- **Recuperación:** híbrida — búsqueda vectorial + búsqueda léxica en español, fusionadas con Reciprocal Rank Fusion (RRF).
- **Generación:** grafo LangGraph `retrieve → grade → generate`, con salida estructurada (Pydantic) y fallback explícito.

---

## Decisión 1 — Recuperación híbrida con RRF

**Qué:** combinar búsqueda vectorial (significado) con léxica (`tsvector` español) y fusionar por RRF.

**Por qué, con evidencia:** en el gold de *contenido* (preguntas cuya respuesta está en el cuerpo), el híbrido supera al vector puro — content-hit@1 0.83 vs 0.67, hit@3 1.0 vs 0.83. La búsqueda léxica cubre el punto ciego del embedding (términos exactos, nombres, códigos).

**El bug que lo tenía muerto:** durante meses el "hybrid search" se comportó como vector puro. Causa: el full-text era sensible a acentos (el corpus dice "orientación", las consultas llegan "orientacion") y la extensión `unaccent` nunca se instaló, así que la rama léxica no matcheaba nada (`orientacion` → 0 resultados; `orientación` → 49). Se descubrió midiendo la ablación: vector-only y híbrido daban idénticos. Fix: configuración de búsqueda `spanish_unaccent` aplicada en el `tsv` y en la `tsquery`. Efecto medido: recall@3 del híbrido 0.93 → 1.00.

---

## Decisión 2 — Ingesta: cuerpo + metadata, no solo resúmenes

**Qué:** indexar el texto completo de cada tesis (bundle TEXT de DSpace) más un chunk de metadata (título/keywords/abstract), en vez de solo metadata.

**Por qué, con evidencia:** el corpus original tenía ~2 chunks por tesis (solo el resumen). El sistema *encontraba* la tesis correcta (recall@1 0.88) pero no podía *responder su contenido*: una pregunta como "qué APIs de IA integró LexBot" no tenía respuesta en el índice. Con texto completo (avg 34.7 chunks/tesis), esa misma pregunta recupera el pasaje del cuerpo ("OpenAI y DeepSeek").

**Trade-offs medidos, sin maquillar:**
- **66% de las tesis (178 de 271) caen en fallback**: sus PDFs no tienen texto extraíble en DSpace (escaneados sin OCR). El salto de contenido solo aplica a un tercio del corpus.
- **recall@1 a nivel tesis bajó 0.95 → 0.81**: con 16x más contenido entra ruido en la posición #1 (otra tesis menciona el tema de pasada). recall@3 se mantuvo en 1.0, que es lo que consume el LLM. Se cambió precisión en el #1 exacto por capacidad de responder contenido.
- Se mantiene un chunk de metadata por tesis para no perder la búsqueda por tema, que ya funcionaba.

---

## Decisión 3 — Grade por LLM, no por umbral de coseno

**Qué:** el nodo `grade` (que decide si el contexto alcanza para responder) usa un LLM que juzga relevancia, no un umbral de distancia coseno.

**Por qué, con evidencia:** el diseño original usaba `best_cosine >= 0.35`. Con casos adversariales (preguntas fuera del corpus: Marte, paella, mundial 86) se descubrió que ese umbral **nunca disparaba**: preguntas totalmente ajenas puntúan 0.44–0.63 en coseno con el modelo multilingüe, siempre por encima de 0.35. El `grade` era decorativo; la única defensa anti-alucinación real era la instrucción del prompt de `generate`, y aun así una pregunta se coló (el modelo respondió la distancia Tierra–Marte con conocimiento propio). Fix: reemplazar el umbral por un juicio de relevancia del LLM. Efecto medido: refusal en adversariales 5/6 → 6/6 (la alucinación desapareció), sin regresión en las preguntas válidas (content-hit@3 se mantuvo en 1.0).

**Trade-off medido:** el grade-by-LLM agrega una llamada al modelo por consulta. En el perfilado de latencia representa el **47% del wall time total**. Es el precio explícito de la robustez. Palanca de mejora anotada: usar un modelo más pequeño/rápido solo para el sí/no del grade.

---

## Decisión 4 — Evaluación como instrumento permanente

**Qué:** un harness reproducible (`api/eval/`) con varios ejes: recall a nivel tesis, content-hit a nivel pasaje, faithfulness (con juez LLM), adversariales (rechazo vs alucinación), latencia por etapa y carga.

**Por qué:** cada mejora de este documento se validó contra este harness. Sin él, "mejoró" sería opinión. Con él, cada cambio tiene un antes/después. El `BASELINE.md` es la bitácora.

**Límites reconocidos (honestidad de medición):**
- La faithfulness (1.0) se midió con el mismo modelo que genera → sesgo de auto-juicio; falta un juez independiente más fuerte.
- El benchmark de carga es de una sola corrida y ruidoso; sirve para una hipótesis (el pool `min_size=1` paga el establecimiento de conexiones en el primer pico), no para una conclusión firme.

---

## Trabajo futuro (priorizado)

1. Juez de faithfulness independiente para validar el 1.0.
2. Grade con modelo barato para recuperar la latencia que cuesta la robustez.
3. Subir `min_size` del pool y re-medir la carga con repeticiones.
4. Bajar `retrieval_top_k` / recortar chunks y medir costo vs faithfulness.
5. OCR del 66% de tesis sin texto extraíble, si el contenido de esas justifica el costo.
