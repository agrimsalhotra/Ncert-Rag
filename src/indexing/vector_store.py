import chromadb
from chromadb.config import Settings
from tqdm import tqdm

from config.settings import COLLECTION_NAME, VECTORSTORE_DIR
from src.chunking.schemas import ChildChunk


def get_collection():
    """Open (or create) the persistent Chroma collection."""
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_embedding_text(chunk: ChildChunk) -> str:
    """Context header + chunk text. Only used for embedding, never stored."""
    parts = [
        f"Class {chunk.class_num} {chunk.subject.title()}",
        f"Chapter {chunk.chapter_num}: {chunk.chapter_name}",
    ]
    if chunk.section_number != "":
        parts.append(f"Section {chunk.section_number} {chunk.section_title}")
    elif chunk.section_title != "":
        parts.append(chunk.section_title)
    if chunk.activity_label != "":
        parts.append(chunk.activity_label)

    header = " | ".join(parts)
    return header + "\n" + chunk.text


def chunk_to_metadata(chunk: ChildChunk) -> dict:
    """Everything except the text becomes filterable metadata (all values are str or int)."""
    return chunk.model_dump(exclude={"text"})


def delete_chapter(collection, class_num: int, subject: str, chapter_num: int):
    """Remove the old vectors of one chapter before re-indexing it."""
    collection.delete(
        where={
            "$and": [
                {"class_num": class_num},
                {"subject": subject},
                {"chapter_num": chapter_num},
            ]
        }
    )


def index_chapter(collection, embedder, children, batch_size=64):
    """Embed the children in batches and upsert them into Chroma."""
    for start in tqdm(range(0, len(children), batch_size), desc="  embedding"):
        batch = children[start:start + batch_size]

        texts_to_embed = [build_embedding_text(chunk) for chunk in batch]
        vectors = embedder.embed_documents(texts_to_embed)

        collection.upsert(
            ids=[chunk.chunk_id for chunk in batch],
            embeddings=vectors,
            documents=[chunk.text for chunk in batch],
            metadatas=[chunk_to_metadata(chunk) for chunk in batch],
        )