import re
from typing import List, Optional

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from config.settings import BM25_TOP_K

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """'Na2CO3(s) + 2 HCl(aq)' -> ['na2co3', 's', '2', 'hcl', 'aq']"""
    return TOKEN_PATTERN.findall(text.lower())


def load_documents(vectorstore, where_filter) -> List[Document]:
    """Read the chunks that match the filter back out of Chroma."""
    try:
        kwargs = {"include": ["documents", "metadatas"]}
        if where_filter:
            kwargs["where"] = where_filter
        stored = vectorstore.get(**kwargs)
    except Exception:
        return []

    documents = []
    if stored and "documents" in stored and "metadatas" in stored:
        docs = stored.get("documents") or []
        metas = stored.get("metadatas") or []
        for text, metadata in zip(docs, metas):
            documents.append(Document(page_content=text, metadata=metadata or {}))
    return documents


def build_bm25_retriever(documents: List[Document]) -> Optional[BM25Retriever]:
    if not documents:
        return None
    return BM25Retriever.from_documents(
        documents,
        preprocess_func=tokenize,
        k=BM25_TOP_K,
    )
