from flashrank import Ranker, RerankRequest

from config.settings import MODELS_DIR, RERANKER_MODEL_NAME


def build_reranker():
    """Downloads the small ONNX cross-encoder on first use."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return Ranker(model_name=RERANKER_MODEL_NAME, cache_dir=str(MODELS_DIR))


def rerank_documents(ranker, question, documents, top_n):
    """Return the best `top_n` documents as (document, score) pairs, best first."""
    passages = []
    for index, document in enumerate(documents):
        passages.append({"id": index, "text": document.page_content})

    request = RerankRequest(query=question, passages=passages)
    results = ranker.rerank(request)   # already sorted, best first

    ranked = []
    for result in results[:top_n]:
        document = documents[result["id"]]
        ranked.append((document, float(result["score"])))
    return ranked