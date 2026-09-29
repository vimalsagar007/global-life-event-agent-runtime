from backend.rag.pipeline import RAG_PIPELINE
from backend.rag.citations import CitationValidator


def test_rag_retrieval_and_citations():
    results = RAG_PIPELINE.retrieve("Ontario driver licence exchange", country="Canada")
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc.country == "Canada"

    score = CitationValidator.calculate_authority_score(top_doc)
    assert score >= 0.90

    citation = CitationValidator.format_citation(top_doc)
    assert citation["authority_level"] == "OFFICIAL_GOVERNMENT"
