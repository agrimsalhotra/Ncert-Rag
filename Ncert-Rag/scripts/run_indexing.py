from collections import Counter

from config.settings import CHUNKS_DIR
from src.indexing.embedder import build_embedder
from src.indexing.loader import load_all_parents, load_children, validate_children
from src.indexing.vector_store import delete_chapter, get_collection, index_chapter

# (question, where the answer should come from)
SMOKE_TEST_QUERIES = [
    ("What is a balanced chemical equation?", "Chapter 1, section 1.1.2"),
    ("How is Plaster of Paris made from gypsum?", "Chapter 2, section 2.4.4"),
    ("Which metals react with cold water?", "Chapter 3"),
]


def main():
    embedder = build_embedder()
    collection = get_collection()
    parents = load_all_parents()

    children_files = sorted(CHUNKS_DIR.glob("*_children.jsonl"))
    if len(children_files) == 0:
        print(f"No chunk files in {CHUNKS_DIR}. Run scripts.run_ingestion first.")
        return

    for path in children_files:
        children = load_children(path)
        validate_children(children, parents)

        first = children[0]
        print(f"Indexing {path.name}: {len(children)} children")
        delete_chapter(collection, first.class_num, first.subject, first.chapter_num)
        index_chapter(collection, embedder, children)

    # --- Summary ---
    stored = collection.get(include=["metadatas"])
    type_counts = Counter(m["content_type"] for m in stored["metadatas"])
    print(f"\nCollection now holds {collection.count()} vectors: {dict(type_counts)}")

    # --- Smoke test: only search concept and activity chunks ---
    print("\n=== Smoke test ===")
    for question, expected in SMOKE_TEST_QUERIES:
        query_vector = embedder.embed_query(question)
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3,
            where={"content_type": {"$in": ["concept", "activity"]}},
            include=["documents", "metadatas", "distances"],
        )
        print(f"\nQ: {question}")
        print(f"   expected: {expected}")
        for text, meta, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            preview = text.replace("\n", " ")[:90]
            print(
                f"   {distance:.3f} | ch{meta['chapter_num']} | sec {meta['section_number']:6} "
                f"| {meta['content_type']:8} | {preview}"
            )


if __name__ == "__main__":
    main()