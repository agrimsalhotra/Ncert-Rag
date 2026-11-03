import torch
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import EMBED_BATCH_SIZE, EMBEDDING_MODEL_NAME, QUERY_INSTRUCTION

device = (
    "cuda"
    if torch.cuda.is_available()
    else ("mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu")
)


class BgeEmbeddings(HuggingFaceEmbeddings):
    """HuggingFaceEmbeddings that adds the BGE instruction to search queries only."""

    def embed_query(self, text: str):
        return super().embed_query(QUERY_INSTRUCTION + text)


def build_embedder():
    """Build embedding model. Prefers local cache if available, otherwise downloads model weights."""
    batch_size = 64 if device != "cpu" else EMBED_BATCH_SIZE

    # First attempt: load offline from local Hugging Face cache
    try:
        return BgeEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": device, "local_files_only": True},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": batch_size,
            },
        )
    except Exception:
        # Fallback: allow download on fresh machines or empty cache
        return BgeEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": device},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": batch_size,
            },
        )
