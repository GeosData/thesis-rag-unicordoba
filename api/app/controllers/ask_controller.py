from app.schemas.qa import AskRequest, AskResponse
from app.services import qa_service


async def ask(request: AskRequest) -> AskResponse:
    return await qa_service.answer_question(request.question)
