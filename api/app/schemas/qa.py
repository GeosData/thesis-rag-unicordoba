from pydantic import BaseModel, Field


class Citation(BaseModel):
    title: str = Field(description="titulo de la tesis citada")
    handle: str = Field(description="handle de la tesis, ej ucordoba/2706")


class Answer(BaseModel):
    answer: str = Field(description="respuesta fundada solo en el contexto dado")
    citations: list[Citation] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    grounded: bool
