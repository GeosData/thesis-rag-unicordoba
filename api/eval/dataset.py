from __future__ import annotations

from typing import TypedDict


class GoldItem(TypedDict):
    q: str
    relevant_handles: list[str]
    note: str


GOLD: list[GoldItem] = [
    {
        "q": "que trabajo configuro reglas de firewall usando el controlador RYU en una red definida por software",
        "relevant_handles": ["ucordoba/11271"],
        "note": "firewall SDN con RYU",
    },
    {
        "q": "sistema que automatiza la generacion de facturas con inteligencia artificial y n8n",
        "relevant_handles": ["ucordoba/9752"],
        "note": "Sistefa",
    },
    {
        "q": "como detectar depresion en estudiantes universitarios con algoritmos de aprendizaje supervisado",
        "relevant_handles": ["ucordoba/11295"],
        "note": "deteccion de depresion, aprendizaje supervisado",
    },
    {
        "q": "chatbot para dar acceso a informacion agricola y asistencia tecnica a campesinos",
        "relevant_handles": ["ucordoba/9719"],
        "note": "chatbot agricola",
    },
    {
        "q": "herramienta que ofrece orientacion legal basica a ciudadanos",
        "relevant_handles": ["ucordoba/9727"],
        "note": "LEXBOT",
    },
    {
        "q": "deteccion de ataques ddos usando modelos de machine learning explicables con el dataset cicddos2019",
        "relevant_handles": ["ucordoba/10038"],
        "note": "DDoS ML explicable",
    },
    {
        "q": "sistema de reconocimiento de la morfologia facial de una persona",
        "relevant_handles": ["ucordoba/11469"],
        "note": "MAI morfologia facial",
    },
    {
        "q": "sistema de internet de las cosas para monitorear y controlar el flujo electrico en una casa",
        "relevant_handles": ["ucordoba/11291"],
        "note": "IoT flujo electrico hogar",
    },
    {
        "q": "visualizador 3d de algoritmos para mejorar la ensenanza de la programacion",
        "relevant_handles": ["ucordoba/9886"],
        "note": "codescape3d",
    },
    {
        "q": "solucion para la gestion de proyectos y requerimientos de software",
        "relevant_handles": ["ucordoba/9722"],
        "note": "ERFISOFT",
    },
    {
        "q": "administrador de tareas web basado en la metodologia scrum",
        "relevant_handles": ["ucordoba/9716"],
        "note": "Task Manager Scrum",
    },
    {
        "q": "sistema de inventario y gestion de servicios tecnicos para una empresa",
        "relevant_handles": ["ucordoba/9844"],
        "note": "inventario Moninet",
    },
    {
        "q": "analisis de factores de riesgo en pacientes con hipertension mediante aprendizaje automatico",
        "relevant_handles": ["ucordoba/9710"],
        "note": "hipertension ML",
    },
    {
        "q": "mapa 3d interactivo de la universidad de cordoba en forma de sitio web",
        "relevant_handles": ["ucordoba/11293", "ucordoba/9728", "ucordoba/9726"],
        "note": "varias tesis cubren el mapa 3D interactivo (respuesta repartida)",
    },
]
