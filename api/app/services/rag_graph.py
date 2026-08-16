from __future__ import annotations

from functools import lru_cache
from typing import TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.repositories import retrieval_repository
from app.schemas.qa import Answer
from app.services import embeddings, llm


class Relevance(BaseModel):
    relevant: bool = Field(
        description="true solo si el contexto contiene informacion concreta para responder la pregunta"
    )


class RagState(TypedDict):
    question: str
    contexts: list[dict]
    grounded: bool
    answer: str
    citations: list[dict]


async def retrieve(state: RagState) -> dict:
    settings = get_settings()
    vector = embeddings.embed_query(state["question"])
    contexts = await retrieval_repository.hybrid_search(
        state["question"], vector, settings.retrieval_top_k
    )
    return {"contexts": contexts}


async def grade(state: RagState) -> dict:
    contexts = state["contexts"]
    if not contexts:
        return {"grounded": False}
    block = "\n\n".join(f"[{c['handle']}] {c['content'][:600]}" for c in contexts[:5])
    prompt = (
        "Decide si el CONTEXTO contiene informacion concreta para responder la PREGUNTA. "
        "Responde relevant=true solo si al menos un fragmento aporta datos directos sobre lo "
        "que se pregunta; si el contexto trata de otro tema, responde relevant=false.\n\n"
        f"PREGUNTA: {state['question']}\n\nCONTEXTO:\n{block}"
    )
    judge = llm.get_llm().with_structured_output(Relevance, method="function_calling")
    verdict: Relevance = await judge.ainvoke(prompt)
    return {"grounded": verdict.relevant}


def route(state: RagState) -> str:
    return "generate" if state["grounded"] else "fallback"


async def generate(state: RagState) -> dict:
    context_block = "\n\n".join(
        f"[{context['title']} - {context['handle']}]\n{context['content']}"
        for context in state["contexts"]
    )
    prompt = (
        "Eres un asistente que responde sobre un corpus de tesis universitarias. "
        "Responde la pregunta usando UNICAMENTE el contexto dado. "
        "Cita solo las tesis que efectivamente uses (title y handle exactos). "
        "Si el contexto no alcanza para responder, dilo explicitamente.\n\n"
        f"Contexto:\n{context_block}\n\n"
        f"Pregunta: {state['question']}"
    )
    structured = llm.get_llm().with_structured_output(Answer, method="function_calling")
    result: Answer = await structured.ainvoke(prompt)
    return {
        "answer": result.answer,
        "citations": [citation.model_dump() for citation in result.citations],
    }


def fallback(state: RagState) -> dict:
    return {
        "answer": "No encontre evidencia suficiente en el corpus para responder esto.",
        "citations": [],
    }


def build_graph():
    graph = StateGraph(RagState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade", grade)
    graph.add_node("generate", generate)
    graph.add_node("fallback", fallback)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", route, {"generate": "generate", "fallback": "fallback"})
    graph.add_edge("generate", END)
    graph.add_edge("fallback", END)
    return graph.compile()


@lru_cache
def get_graph():
    return build_graph()
