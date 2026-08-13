from __future__ import annotations

import asyncio
import sys

from app.repositories import db
from app.services.rag_graph import build_graph


async def main(question: str) -> None:
    await db.get_pool()
    graph = build_graph()
    result = await graph.ainvoke({"question": question})
    print(f"Q: {question}\n")
    print(f"grounded: {result['grounded']}\n")
    print(f"A: {result['answer']}\n")
    if result.get("citations"):
        print("Citas:")
        for citation in result["citations"]:
            print(f"  - {citation['title']} ({citation['handle']})")
    await db.close_pool()


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "que investigaciones hay sobre riego de cultivos?"
    asyncio.run(main(question))
