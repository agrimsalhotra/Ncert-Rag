from collections import Counter

from config.settings import RAW_DIR, PARSED_DIR, CHUNKS_DIR
from src.parsing.pdf_reader import parse_chapter_pdf
from src.chunking.hierarchical import build_chunks


def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item.model_dump_json() + "\n")


def main():
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_DIR.glob("*.pdf"))
    if len(pdf_files) == 0:
        print(f"No PDFs found in {RAW_DIR}")
        return

    for pdf_path in pdf_files:
        print(f"Parsing {pdf_path.name} ...")
        chapter = parse_chapter_pdf(pdf_path)
        parsed_path = PARSED_DIR / (pdf_path.stem + ".json")
        parsed_path.write_text(chapter.model_dump_json(indent=2), encoding="utf-8")

        parents, children = build_chunks(chapter)
        write_jsonl(CHUNKS_DIR / (pdf_path.stem + "_parents.jsonl"), parents)
        write_jsonl(CHUNKS_DIR / (pdf_path.stem + "_children.jsonl"), children)

        print(f"  chapter_name = {parents[0].chapter_name!r}")
        print(f"  parents={len(parents)}, children={len(children)}")
        print(f"  by type: {dict(Counter(p.content_type for p in parents))}")

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