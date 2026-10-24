import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

from config.settings import COLLECTION_NAME, DENSE_TOP_K, VECTORSTORE_DIR


def build_where_filter(content_types, class_num=None):
    """Chroma metadata filter. Two or more conditions must be wrapped in $and."""
    conditions = [{"content_type": {"$in": list(content_types)}}]
    if class_num is not None:
        conditions.append({"class_num": class_num})

    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def build_vectorstore(embedder):
    """LangChain wrapper around the collection we created in Step 3."""
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
    return vectorstore.as_retriever(
        search_kwargs={"k": DENSE_TOP_K, "filter": where_filter}
    )