from typing import List
from langchain_text_splitters import TokenTextSplitter
from src.chunking.schemas import Chunk
from src.chunking.headings import clean_page_text, find_chapter_name
from src.parsing.schemas import ParsedChapter


def split_token_based(
    chapter: ParsedChapter,
    chunk_size: int = 250,
    chunk_overlap: int = 25,
    encoding_name: str = "cl100k_base",
) -> List[Chunk]:
    """Split chapter text based on BPE token counts (e.g., tiktoken cl100k_base)."""
    if not chapter.pages:
        return []

    full_text = "\n\n".join(clean_page_text(page.markdown) for page in chapter.pages)
    first_markdown = chapter.pages[0].markdown if chapter.pages else ""
    chapter_name = find_chapter_name(
        first_markdown,
        class_num=chapter.class_num,
        chapter_num=chapter.chapter_num,
    )

    try:
        splitter = TokenTextSplitter(
            encoding_name=encoding_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        raw_chunks = splitter.split_text(full_text)
    except Exception:
        # Fallback approximate token splitting (1 token ~ 4 chars) if tiktoken encoding unavailable
        from langchain_text_splitters import CharacterTextSplitter
        splitter = CharacterTextSplitter(
            chunk_size=chunk_size * 4,
            chunk_overlap=chunk_overlap * 4,
            separator=" ",
        )
        raw_chunks = splitter.split_text(full_text)

    chunks: List[Chunk] = []
    prefix = f"class{chapter.class_num}_{chapter.subject}_ch{chapter.chapter_num:02d}_tok"

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
                strategy="token",
            )
        )
    return chunks
