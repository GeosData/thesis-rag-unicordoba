# eval — harness de evaluación de retrieval

Mide qué tan bueno es el retrieval de scholar-rag con números reproducibles, en vez de a ojo. Es la Fase 1 del mapa de profundidad (`Personal/Carrera/Mapa-Profundidad-scholar-rag.md` en el vault) y el instrumento contra el que se comparan todas las mejoras posteriores.

## Correr

```bash
cd api
PYTHONPATH=. ./.venv/Scripts/python.exe -m eval.run   # Windows
# PYTHONPATH=. .venv/bin/python -m eval.run            # unix
```

Necesita `DATABASE_URL` en `api/.env` (la misma BD con el corpus ingerido).

## Qué mide

- **recall@k**: de la(s) tesis relevante(s), cuántas aparecen en el top-k. Mide si el retrieval trae lo correcto.
- **MRR**: promedio de 1/posición de la primera tesis relevante. Mide si lo trae arriba.
- **p50 ms**: latencia mediana por query.
- Compara dos retrievers: `vector-only` (`search`) vs `hybrid-rrf` (`hybrid_search`). Esa comparación es la ablación de M3 en vivo.

## Limitación conocida (v1)

Mide a **nivel de tesis** (`handle`), no de chunk, porque `retrieval_repository` no expone `c.id` en la salida. Para recall por chunk hay que exponer el id del chunk en las queries de `retrieval_repository.py`. Anotado como mejora; el nivel tesis ya da señal fuerte.

## Expandir el gold

`dataset.py` tiene 14 preguntas semilla sobre tesis reales del corpus. Para más señal, agrega entradas con `q` (pregunta como la haría un usuario) y `relevant_handles` (los `handle` de la o las tesis que la responden, verificados abriendo el corpus). 50-100 preguntas dan una medición sólida. Incluye casos difíciles: términos exactos, respuestas repartidas en varias tesis.

## Estructura

- `dataset.py` — el gold (preguntas + tesis correctas).
- `metrics.py` — recall@k, precision@k, reciprocal_rank (puros, testeables).
- `run.py` — conecta al retrieval real, corre el gold, imprime la tabla comparativa.
