from __future__ import annotations

from typing import TypedDict


class ContentItem(TypedDict):
    q: str
    handle: str
    must_contain: str
    note: str


GOLD_CONTENT: list[ContentItem] = [
    {
        "q": "que APIs o servicios de inteligencia artificial integro el sistema para generar texto y documentos legales",
        "handle": "ucordoba/9727",
        "must_contain": "openai",
        "note": "LEXBOT integra OpenAI y DeepSeek",
    },
    {
        "q": "que tecnicas integro el marco unificado de deteccion de ataques ddos en redes sdn",
        "handle": "ucordoba/10038",
        "must_contain": "dimensionalidad",
        "note": "seleccion de caracteristicas y reduccion de dimensionalidad",
    },
    {
        "q": "que se monitorea dentro de las instituciones educativas para hacer seguimiento al consumo de cigarrillo",
        "handle": "ucordoba/2750",
        "must_contain": "gases",
        "note": "monitoreo de gases (humo)",
    },
    {
        "q": "que estadisticas ofrece la web app sobre una cuenta de red social",
        "handle": "ucordoba/288",
        "must_contain": "likes",
        "note": "estadisticas de likes y seguidores",
    },
    {
        "q": "para que tipo de pacientes es el sistema de reconocimiento gestual usado en la anamnesis",
        "handle": "ucordoba/3722",
        "must_contain": "sordomudos",
        "note": "pacientes sordomudos",
    },
    {
        "q": "que metaheuristica se utilizo para optimizar pronosticos de series de tiempo",
        "handle": "ucordoba/3946",
        "must_contain": "cromatico",
        "note": "algoritmo cromatico",
    },
]
