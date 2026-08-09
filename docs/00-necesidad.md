# 00 — Necesidad

> Working name: **scholar-rag** (final se decide en `02-nombres.md`).
> Rol de este proyecto: **pieza de portafolio primero** (proyecto ancla de carrera Backend Python/AI). Negocio = upside si valida. Ver `Personal/Carrera/INDEX.md` en el vault.

## El dolor

El repositorio institucional de la Universidad de Córdoba (DSpace) guarda ~271 tesis de Ingeniería de Sistemas — investigación con dolores reales, hiperlocales, ya documentados. Ese conocimiento está **enterrado y es inaccesible en la práctica**:

- La búsqueda del DSpace es por metadata (título/autor/palabra clave), no por significado. Preguntar "qué problemas de logística se han estudiado en Montería" no devuelve nada útil.
- El texto vive en PDFs que nadie lee completos. No hay forma de preguntarle al corpus y recibir una respuesta con citas.
- La web pública bloquea scraping (BunkerWeb); la **API DSpace sí responde** (validado). El corpus es accesible por API, no por navegador.

## Quién lo sufre

- Estudiantes/tesistas nuevos que reinventan temas ya investigados (no saben qué se hizo antes).
- Docentes/jurados que necesitan ubicar antecedentes rápido.
- (Para Josse) una fuente de **dolores reales por sector** para productos Geosdata — este servicio es también un instrumento de descubrimiento.

## Por qué ahora / por qué yo

- El corpus ya está identificado y la vía de acceso (API DSpace) ya está validada — cero fricción de datos, que es donde mueren la mayoría de los RAG.
- Cierra de un solo golpe los 6 gaps técnicos que el mercado pide y que tumbaron la técnica de EPAM (Python idiomático, FastAPI/Pydantic, DB/índices, testing, arquitectura, AI-agentic). Ver `DEBRIEF-ENTREVISTA-EPAM-2026-07-16.md`.
- Da narrativa verificable de entrevista: "servicio RAG que indexa 271 tesis y responde con citas".

## Resultado esperado (outcome verificable)

Un servicio donde un usuario pregunta en lenguaje natural sobre la investigación local y recibe una **respuesta sintetizada con citas trazables a la tesis y página de origen** — no una lista de PDFs, una respuesta con evidencia.
