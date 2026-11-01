import re

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from config.settings import BM25_TOP_K

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text):
    """'Na2CO3(s) + 2 HCl(aq)' -> ['na2co3', 's', '2', 'hcl', 'aq']"""
    return TOKEN_PATTERN.findall(text.lower())


def load_documents(vectorstore, where_filter):
    """Read the chunks that match the filter back out of Chroma."""
    stored = vectorstore.get(where=where_filter, include=["documents", "metadatas"])
    documents = []
    for text, metadata in zip(stored["documents"], stored["metadatas"]):
        documents.append(Document(page_content=text, metadata=metadata))
    return documents


def build_bm25_retriever(documents):
    if len(documents) == 0:
        raise ValueError("No chunks match this filter, so BM25 cannot be built.")
    return BM25Retriever.from_documents(
        documents,
        preprocess_func=tokenize,
        k=BM25_TOP_K,
    )