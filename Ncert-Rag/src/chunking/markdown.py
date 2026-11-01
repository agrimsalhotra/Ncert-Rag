from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.chunking.headings import clean_page_text, find_chapter_name, normalize_headings, has_body_text
from src.chunking.metadata import build_metadata
from src.chunking.schemas import Chunk
from src.parsing.schemas import ParsedChapter

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
]


def split_markdown_sections(
    chapter: ParsedChapter,
    max_chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> List[Chunk]:
    """Split chapter text based on Markdown headers, preserving section structure and headings."""
    full_text = "\n\n".join(clean_page_text(page.markdown) for page in chapter.pages)
    normalized_text = normalize_headings(full_text)
    chapter_name = find_chapter_name(
        chapter.pages[0].markdown,
        class_num=chapter.class_num,
        chapter_num=chapter.chapter_num,
    )

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    section_docs = header_splitter.split_text(normalized_text)

    recursive_subsplitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks: List[Chunk] = []
    chunk_counter = 0
    prefix = f"class{chapter.class_num}_{chapter.subject}_ch{chapter.chapter_num:02d}_md"

    for doc in section_docs:
        if not has_body_text(doc.page_content):
            continue

        meta = build_metadata(doc.metadata, chapter, chapter_name)
        sub_texts = recursive_subsplitter.split_text(doc.page_content)

        for text in sub_texts:
            text_clean = text.strip()
            if not text_clean:
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{prefix}_{chunk_counter:04d}",
                    text=text_clean,
                    strategy="markdown",
                    **meta,
                )
            )
            chunk_counter += 1

    return chunks
