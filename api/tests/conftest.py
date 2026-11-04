import pytest

from app.config.settings import get_settings
from app.middleware.rate_limit import limiter
from app.services import embeddings, llm, rag_graph
from app.repositories import query_log_repository, retrieval_repository


class FakeStructuredLLM:
    def __init__(self, owner, schema):
        self.owner = owner
        self.schema = schema

    async def ainvoke(self, prompt):
        self.owner.prompts.append((self.schema.__name__, prompt))
        failing = self.owner.fail_on in (None, self.schema.__name__)
        if self.owner.error is not None and failing:
            raise self.owner.error
        return self.owner.responses[self.schema.__name__]


class FakeLLM:
    def __init__(self):
        self.prompts = []
        self.responses = {}
        self.error = None
        self.fail_on = None

    def with_structured_output(self, schema, method=None):
        return FakeStructuredLLM(self, schema)

    def prompts_for(self, schema_name):
        return [prompt for name, prompt in self.prompts if name == schema_name]


class FakeRetrieval:
    def __init__(self):
        self.rows = []
        self.error = None
        self.calls = []

    async def __call__(self, query, embedding, k=5, **kwargs):
        self.calls.append((query, embedding, k))
        if self.error is not None:
            raise self.error
        return list(self.rows)


class FakeQueryLog:
    def __init__(self):
        self.entries = []
        self.error = None

    async def __call__(self, question, grounded, citations):
        if self.error is not None:
            raise self.error
        self.entries.append((question, grounded, citations))


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch):
    monkeypatch.setattr(get_settings(), "database_url", None)
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    return fake


@pytest.fixture
def fake_retrieval(monkeypatch):
    fake = FakeRetrieval()
    monkeypatch.setattr(retrieval_repository, "hybrid_search", fake)
    return fake


@pytest.fixture
def fake_query_log(monkeypatch):
    fake = FakeQueryLog()
    monkeypatch.setattr(query_log_repository, "log_query", fake)
    return fake


@pytest.fixture
def fake_embeddings(monkeypatch):
    calls = []

    def embed_query(text):
        calls.append(text)
        return [0.0, 1.0, 0.0]

    monkeypatch.setattr(embeddings, "embed_query", embed_query)
    return calls


@pytest.fixture
def pipeline(fake_llm, fake_retrieval, fake_query_log, fake_embeddings):
    rag_graph.get_graph.cache_clear()
    yield type(
        "Pipeline",
        (),
        {"llm": fake_llm, "retrieval": fake_retrieval, "query_log": fake_query_log, "embedded": fake_embeddings},
    )
    rag_graph.get_graph.cache_clear()


def make_chunk(handle="ucordoba/1", title="Tesis uno", content="contenido relevante", **extra):
    return {"handle": handle, "title": title, "content": content, "score": 0.03, "cosine": 0.8, **extra}
