from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.chunking.schemas import Chunk
from src.chunking.headings import clean_page_text, find_chapter_name
from src.parsing.schemas import ParsedChapter

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_recursive(
    chapter: ParsedChapter,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Chunk]:
    """Split chapter text recursively using natural text boundaries (paragraphs, lines, sentences)."""
    full_text = "\n\n".join(clean_page_text(page.markdown) for page in chapter.pages)
    chapter_name = find_chapter_name(
        chapter.pages[0].markdown,
        class_num=chapter.class_num,
        chapter_num=chapter.chapter_num,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=SEPARATORS,
    )
    raw_chunks = splitter.split_text(full_text)

    chunks: List[Chunk] = []
    prefix = f"class{chapter.class_num}_{chapter.subject}_ch{chapter.chapter_num:02d}_rec"

    for idx, text in enumerate(raw_chunks):
        text_clean = text.strip()
        if not text_clean:
            continue
        chunks.append(
            Chunk(
                chunk_id=f"{prefix}_{idx:04d}",
                text=text_clean,
                class_num=chapter.class_num,
                subject=chapter.subject,
                chapter_num=chapter.chapter_num,
                chapter_name=chapter_name,
                strategy="recursive",
            )
        )
    return chunks
