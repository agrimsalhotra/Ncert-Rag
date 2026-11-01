"""
CLI tool to test and compare different chunking strategies on any parsed NCERT chapter.
Usage:
    python -m scripts.compare_chunking
    python -m scripts.compare_chunking --file class10_science_ch01.json
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from config.settings import PARSED_DIR
from src.parsing.schemas import ParsedChapter
from src.chunking import (
    split_fixed_size,
    split_recursive,
    split_token_based,
    split_semantic_sentences,
    split_markdown_sections,
    split_hierarchical,
)


def analyze_chunks(name: str, chunks) -> Dict[str, Any]:
    count = len(chunks)
    if count == 0:
        return {"name": name, "count": 0, "avg_chars": 0, "min_chars": 0, "max_chars": 0}
    lengths = [len(c.text) for c in chunks]
    return {
        "name": name,
        "count": count,
        "avg_chars": round(sum(lengths) / count, 1),
        "min_chars": min(lengths),
        "max_chars": max(lengths),
    }


def main():
    parser = argparse.ArgumentParser(description="Compare NCERT chunking strategies")
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Specific parsed json file in data/parsed (e.g. class10_science_ch01.json)",
    )
    args = parser.parse_args()

    parsed_files = sorted(PARSED_DIR.glob("*.json"))
    if not parsed_files:
        print(f"No parsed chapters found in {PARSED_DIR}. Run run_ingestion first.")
        return

    if args.file:
        target_path = PARSED_DIR / args.file
        if not target_path.exists():
            print(f"File {target_path} not found.")
            return
    else:
        target_path = parsed_files[0]

    print(f"Loading {target_path.name}...")
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    chapter = ParsedChapter(**data)
    print(f"Chapter: Class {chapter.class_num} Science Ch {chapter.chapter_num} ({len(chapter.pages)} pages)\n")

    # Run all strategies
    fixed_chunks = split_fixed_size(chapter, chunk_size=500, chunk_overlap=50)
    rec_chunks = split_recursive(chapter, chunk_size=800, chunk_overlap=100)
    tok_chunks = split_token_based(chapter, chunk_size=250, chunk_overlap=25)
    sem_chunks = split_semantic_sentences(chapter, target_chunk_chars=800)
    md_chunks = split_markdown_sections(chapter, max_chunk_size=1200)
    parents, children = split_hierarchical(chapter)

    results = [
        analyze_chunks("Fixed Character (500 chars)", fixed_chunks),
        analyze_chunks("Recursive Character (800 chars)", rec_chunks),
        analyze_chunks("Token-based (250 tokens)", tok_chunks),
        analyze_chunks("Semantic/Sentence boundary", sem_chunks),
        analyze_chunks("Markdown Section-based", md_chunks),
        analyze_chunks("Hierarchical Parents", parents),
        analyze_chunks("Hierarchical Children", children),
    ]

    header_fmt = "{:<32} | {:<8} | {:<10} | {:<10} | {:<10}"
    row_fmt = "{:<32} | {:<8} | {:<10} | {:<10} | {:<10}"
    print(header_fmt.format("Strategy", "Chunks", "Avg Chars", "Min Chars", "Max Chars"))
    print("-" * 80)
    for res in results:
        print(row_fmt.format(res["name"], res["count"], res["avg_chars"], res["min_chars"], res["max_chars"]))

    print("\n--- Sample Chunks Preview (First chunk of each strategy) ---")
    samples = [
        ("Fixed-Size", fixed_chunks),
        ("Recursive", rec_chunks),
        ("Token-based", tok_chunks),
        ("Semantic", sem_chunks),
        ("Markdown", md_chunks),
        ("Hierarchical (Parent)", parents),
    ]
    for label, chunk_list in samples:
        if chunk_list:
            first_text = chunk_list[0].text.replace("\n", " ")[:120]
            print(f"\n[{label}] ID: {getattr(chunk_list[0], 'chunk_id', getattr(chunk_list[0], 'parent_id', 'N/A'))}")
            print(f"Preview: {first_text}...")


if __name__ == "__main__":
    main()
