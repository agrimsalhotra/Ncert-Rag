from langchain_core.documents import Document

from src.retrieval.bm25_retriever import build_bm25_retriever, tokenize
from src.retrieval.dense_retriever import build_where_filter
from src.retrieval.fusion import build_hybrid_retriever
from src.retrieval.reranker import rerank_documents


def test_tokenize():
    tokens = tokenize("Na2CO3(s) + 2 HCl(aq) -> 2 NaCl + H2O + CO2")
    assert "na2co3" in tokens
    assert "hcl" in tokens
    assert "nacl" in tokens
    assert "h2o" in tokens
    assert "co2" in tokens


def test_build_where_filter():
    # Both filters
    f1 = build_where_filter(content_types=["concept", "activity"], class_num=10)
    assert "$and" in f1
    assert len(f1["$and"]) == 2

    # Single filter: content_types only
    f2 = build_where_filter(content_types=["concept"])
    assert f2 == {"content_type": {"$in": ["concept"]}}

    # Single filter: class_num only
    f3 = build_where_filter(class_num=10)
    assert f3 == {"class_num": 10}

    # Empty filters
    assert build_where_filter() is None
    assert build_where_filter(content_types=[]) is None


def test_bm25_empty_documents():
    assert build_bm25_retriever([]) is None


def test_build_hybrid_retriever_fallbacks():
    doc = Document(page_content="test", metadata={"chunk_id": "c1"})
    bm25 = build_bm25_retriever([doc])

    # If dense is None, returns bm25
    assert build_hybrid_retriever(bm25, None) == bm25

    # If bm25 is None, returns dense
    dense_dummy = object()
    assert build_hybrid_retriever(None, dense_dummy) == dense_dummy

    # If both None
    assert build_hybrid_retriever(None, None) is None


def test_rerank_empty_documents():
    assert rerank_documents(None, "question", [], 5) == []
