from app.services.rag_graph import grade, route


def test_grade_grounded_when_top_score_high():
    state = {"contexts": [{"score": 0.9}, {"score": 0.4}]}
    assert grade(state)["grounded"] is True


def test_grade_not_grounded_when_top_score_low():
    state = {"contexts": [{"score": 0.1}]}
    assert grade(state)["grounded"] is False


def test_grade_not_grounded_when_no_contexts():
    state = {"contexts": []}
    assert grade(state)["grounded"] is False


def test_route_sends_grounded_to_generate():
    assert route({"grounded": True}) == "generate"


def test_route_sends_ungrounded_to_fallback():
    assert route({"grounded": False}) == "fallback"
