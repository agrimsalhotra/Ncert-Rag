from langchain.retrievers import EnsembleRetriever

from config.settings import HYBRID_WEIGHTS


def build_hybrid_retriever(bm25_retriever, dense_retriever):
    """Weighted Reciprocal Rank Fusion of BM25 and dense results."""
    return EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=list(HYBRID_WEIGHTS),
        c=60,                 # standard RRF constant
        id_key="chunk_id",    # a chunk found by both retrievers is counted once
    )