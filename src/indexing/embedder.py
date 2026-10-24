from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import EMBED_BATCH_SIZE, EMBEDDING_MODEL_NAME, QUERY_INSTRUCTION


class BgeEmbeddings(HuggingFaceEmbeddings):
    """HuggingFaceEmbeddings that adds the BGE instruction to search queries only."""

    def embed_query(self, text: str):
        return super().embed_query(QUERY_INSTRUCTION + text)


def build_embedder():
    """Local embedding model. The first run downloads about 130 MB from Hugging Face."""
    return BgeEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True,   # needed for cosine similarity
            "batch_size": EMBED_BATCH_SIZE,
        },
    )