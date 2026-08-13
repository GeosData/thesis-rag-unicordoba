from fastapi import APIRouter, Request

from app.controllers import ask_controller
from app.middleware.rate_limit import limiter
from app.schemas.qa import AskRequest, AskResponse

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
@limiter.limit("10/minute")
async def ask(request: Request, body: AskRequest) -> AskResponse:
    return await ask_controller.ask(body)
