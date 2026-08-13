from app.services.corpus import build_document, chunk_text


def test_chunk_short_returns_single():
    assert chunk_text("una idea corta") == ["una idea corta"]


def test_chunk_long_respects_size_and_overlaps():
    text = "a" * 2500
    chunks = chunk_text(text, size=1000, overlap=150)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_build_document_joins_present_fields():
    document = build_document({"title": "Titulo", "keywords": "kw", "abstract": "resumen"})
    assert "Titulo" in document and "kw" in document and "resumen" in document


def test_build_document_skips_empty_and_none():
    document = build_document({"title": "Solo titulo", "keywords": None, "abstract": ""})
    assert document == "Solo titulo"
