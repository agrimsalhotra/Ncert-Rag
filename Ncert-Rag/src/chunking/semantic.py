import re
from typing import List, Optional
from src.chunking.schemas import Chunk
from src.chunking.headings import clean_page_text, find_chapter_name
from src.parsing.schemas import ParsedChapter

# Sentence boundary regex handling punctuation, newlines, and list items
SENTENCE_END_REGEX = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])|(?<=\n\n)")


def split_sentences(text: str) -> List[str]:
    """Split text into individual sentences."""
    raw_sentences = SENTENCE_END_REGEX.split(text)
    sentences = []
    for s in raw_sentences:
        clean_s = s.strip()
        if clean_s:
            sentences.append(clean_s)
    return sentences


def split_semantic_sentences(
    chapter: ParsedChapter,
    target_chunk_chars: int = 800,
    max_chunk_chars: int = 1200,
    overlap_sentences: int = 1,
) -> List[Chunk]:
    """
    Split text at coherent sentence and paragraph boundaries without breaking sentences mid-way.
    Groups consecutive sentences into semantic paragraph units up to target_chunk_chars.
    """
    full_text = "\n\n".join(clean_page_text(page.markdown) for page in chapter.pages)
    chapter_name = find_chapter_name(
        chapter.pages[0].markdown,
        class_num=chapter.class_num,
        chapter_num=chapter.chapter_num,
    )

    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

    chunks: List[Chunk] = []
    chunk_counter = 0
    prefix = f"class{chapter.class_num}_{chapter.subject}_ch{chapter.chapter_num:02d}_sem"

    current_sentences: List[str] = []
    current_length = 0

    for para in paragraphs:
        para_sentences = split_sentences(para)
        for sent in para_sentences:
            sent_len = len(sent)
            if current_length + sent_len > target_chunk_chars and current_sentences:
                # Emit current group
                chunk_text = " ".join(current_sentences)
                chunks.append(
                    Chunk(
                        chunk_id=f"{prefix}_{chunk_counter:04d}",
                        text=chunk_text,
                        class_num=chapter.class_num,
                        subject=chapter.subject,
                        chapter_num=chapter.chapter_num,
                        chapter_name=chapter_name,
                        strategy="semantic",
                    )
                )
                chunk_counter += 1

                # Retain overlap sentences
                if overlap_sentences > 0:
                    current_sentences = current_sentences[-overlap_sentences:]
                    current_length = sum(len(s) + 1 for s in current_sentences)
                else:
                    current_sentences = []
                    current_length = 0

            current_sentences.append(sent)
            current_length += sent_len + 1

    # Emit leftover sentences
    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append(
            Chunk(
                chunk_id=f"{prefix}_{chunk_counter:04d}",
                text=chunk_text,
                class_num=chapter.class_num,
                subject=chapter.subject,
                chapter_num=chapter.chapter_num,
                chapter_name=chapter_name,
                strategy="semantic",
            )
        )

    return chunks
