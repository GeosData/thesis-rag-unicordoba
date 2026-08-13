from app.services.rag_graph import grade, route


def test_grade_grounded_when_cosine_high():
    state = {"contexts": [{"cosine": 0.9}, {"cosine": 0.4}]}
    assert grade(state)["grounded"] is True


def test_grade_grounded_uses_best_not_first():
    state = {"contexts": [{"cosine": 0.2}, {"cosine": 0.8}]}
    assert grade(state)["grounded"] is True


def test_grade_not_grounded_when_all_low():
    state = {"contexts": [{"cosine": 0.1}, {"cosine": 0.05}]}
    assert grade(state)["grounded"] is False


def test_grade_not_grounded_when_no_contexts():
    state = {"contexts": []}
    assert grade(state)["grounded"] is False


def test_route_sends_grounded_to_generate():
    assert route({"grounded": True}) == "generate"


def test_route_sends_ungrounded_to_fallback():
    assert route({"grounded": False}) == "fallback"
