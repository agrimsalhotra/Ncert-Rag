from config.settings import ANSWER_CONTENT_TYPES, MAX_PARENTS, RERANK_TOP_N
from src.indexing.embedder import build_embedder
from src.indexing.loader import load_all_parents
from src.retrieval.bm25_retriever import build_bm25_retriever, load_documents
from src.retrieval.dense_retriever import (
    build_dense_retriever,
    build_vectorstore,
    build_where_filter,
)
from src.retrieval.fusion import build_hybrid_retriever
from src.retrieval.reranker import build_reranker, rerank_documents


class NcertSearch:
    """hybrid search -> re-rank children -> expand to parent sections."""

    def __init__(self):
        self.embedder = build_embedder()
        self.vectorstore = build_vectorstore(self.embedder)
        self.ranker = build_reranker()
        self.parents = load_all_parents()
        self._bm25_cache = {}   # (content_types, class_num) -> BM25 retriever

    def hybrid_search(self, question, class_num=None, content_types=ANSWER_CONTENT_TYPES):
        where_filter = build_where_filter(content_types, class_num)

        # BM25 is built once per filter combination, then reused
        cache_key = (tuple(content_types) if content_types else (), class_num)
        if cache_key not in self._bm25_cache:
            documents = load_documents(self.vectorstore, where_filter)
            self._bm25_cache[cache_key] = build_bm25_retriever(documents)
        bm25_retriever = self._bm25_cache[cache_key]

        dense_retriever = build_dense_retriever(self.vectorstore, where_filter)
        hybrid_retriever = build_hybrid_retriever(bm25_retriever, dense_retriever)
        if hybrid_retriever is None:
            return []
        return hybrid_retriever.invoke(question)

    def search(self, question, class_num=None, content_types=ANSWER_CONTENT_TYPES):
        """Return a list of (ParentChunk, rerank_score), best first."""
        candidates = self.hybrid_search(question, class_num, content_types)
        if len(candidates) == 0:
            return []

        ranked_children = rerank_documents(self.ranker, question, candidates, RERANK_TOP_N)

        results = []
        seen_parent_ids = set()
        for child, score in ranked_children:
            parent_id = child.metadata.get("parent_id")
            if not parent_id or parent_id in seen_parent_ids:
                continue   # several top children can share one parent
            parent = self.parents.get(parent_id)
            if parent is None:
                continue
            seen_parent_ids.add(parent_id)
            results.append((parent, score))
            if len(results) == MAX_PARENTS:
                break
        return results
