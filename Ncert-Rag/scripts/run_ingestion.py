from collections import Counter
from pathlib import Path

from config.settings import CHUNKS_DIR, PARSED_DIR, RAW_DIR
from src.chunking import (
    split_fixed_size,
    split_hierarchical,
    split_markdown_sections,
    split_recursive,
    split_semantic_sentences,
    split_token_based,
)
from src.parsing.pdf_reader import parse_chapter_pdf
from src.utils.logging_setup import configure_utf8_output

configure_utf8_output()

# Strategy-specific chunk output directories
STRATEGY_DIRS = {
    "hierarchical": CHUNKS_DIR / "hierarchical",
    "fixed": CHUNKS_DIR / "fixed",
    "recursive": CHUNKS_DIR / "recursive",
    "token": CHUNKS_DIR / "token",
    "semantic": CHUNKS_DIR / "semantic",
    "markdown": CHUNKS_DIR / "markdown",
}


def write_jsonl(path: Path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item.model_dump_json() + "\n")


def main():
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    for dir_path in STRATEGY_DIRS.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if len(pdf_files) == 0:
        print(f"No PDFs found in {RAW_DIR}")
        return

    for pdf_path in pdf_files:
        stem = pdf_path.stem
        print(f"Parsing {pdf_path.name} ...")
        chapter = parse_chapter_pdf(pdf_path)
        parsed_path = PARSED_DIR / (stem + ".json")
        parsed_path.write_text(chapter.model_dump_json(indent=2), encoding="utf-8")

        # 1. Hierarchical (Production RAG strategy)
        parents, children = split_hierarchical(chapter)
        write_jsonl(STRATEGY_DIRS["hierarchical"] / f"{stem}_parents.jsonl", parents)
        write_jsonl(STRATEGY_DIRS["hierarchical"] / f"{stem}_children.jsonl", children)

        # 2. Fixed-size character chunks
        fixed_chunks = split_fixed_size(chapter)
        write_jsonl(STRATEGY_DIRS["fixed"] / f"{stem}_fixed.jsonl", fixed_chunks)

        # 3. Recursive character chunks
        recursive_chunks = split_recursive(chapter)
        write_jsonl(STRATEGY_DIRS["recursive"] / f"{stem}_recursive.jsonl", recursive_chunks)

        # 4. Token-based chunks
        token_chunks = split_token_based(chapter)
        write_jsonl(STRATEGY_DIRS["token"] / f"{stem}_token.jsonl", token_chunks)

        # 5. Semantic / sentence chunks
        semantic_chunks = split_semantic_sentences(chapter)
        write_jsonl(STRATEGY_DIRS["semantic"] / f"{stem}_semantic.jsonl", semantic_chunks)

        # 6. Markdown section chunks
        markdown_chunks = split_markdown_sections(chapter)
        write_jsonl(STRATEGY_DIRS["markdown"] / f"{stem}_markdown.jsonl", markdown_chunks)

        chapter_name = parents[0].chapter_name if parents else "N/A"
        print(f"  chapter_name = {chapter_name!r}")
        print(
            f"  hierarchical: parents={len(parents)}, children={len(children)} | "
            f"fixed: {len(fixed_chunks)} | rec: {len(recursive_chunks)} | "
            f"tok: {len(token_chunks)} | sem: {len(semantic_chunks)} | md: {len(markdown_chunks)}"
        )
        print(f"  by type (hierarchical): {dict(Counter(p.content_type for p in parents))}")

        print("  --- outline (parent_id | type | section | activity | size | preview) ---")
        for parent in parents:
            preview = parent.text.replace("\n", " ")[:50]
            print(
                f"  {parent.parent_id[-4:]} | {parent.content_type:8} | "
                f"{parent.section_number:6} | {parent.activity_label:12} | "
                f"{len(parent.text):5} | {preview}"
            )


if __name__ == "__main__":
    main()
