import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

from config.settings import COLLECTION_NAME, DENSE_TOP_K, VECTORSTORE_DIR


def build_where_filter(content_types=None, class_num=None):
    """Chroma metadata filter. Two or more conditions must be wrapped in $and."""
    conditions = []
    if content_types:
        conditions.append({"content_type": {"$in": list(content_types)}})
    if class_num is not None:
        try:
            conditions.append({"class_num": int(class_num)})
        except (ValueError, TypeError):
            conditions.append({"class_num": class_num})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def build_vectorstore(embedder):
    """LangChain wrapper around the persistent Chroma collection."""
    client = chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedder,
    )


def build_dense_retriever(vectorstore, where_filter):
    search_kwargs = {"k": DENSE_TOP_K}
    if where_filter:
        search_kwargs["filter"] = where_filter
    return vectorstore.as_retriever(search_kwargs=search_kwargs)
