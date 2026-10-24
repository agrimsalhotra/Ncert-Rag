import re
from typing import List, Tuple

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.chunking.headings import find_chapter_name, normalize_headings
from src.chunking.metadata import build_metadata
from src.chunking.schemas import ChildChunk, ParentChunk
from src.parsing.schemas import ParsedChapter

from src.chunking.headings import clean_page_text, find_chapter_name, normalize_headings


PARENT_MAX_CHARS = 4000
PARENT_OVERLAP = 200
MIN_PARENT_CHARS = 60

CHILD_MAX_CHARS = 800
CHILD_OVERLAP = 100

QUESTION_START_PATTERN = re.compile(
    r"(?m)(?:^(?=\d{1,2}\.\s)|(?<=[?.]\s)(?=\d{1,2}\.\s+[A-Z]))"
)

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
    ("#####", "h5"),
]

# Try paragraph breaks first, then lines, then sentences, then words
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def has_body_text(text):
    """True if the text has at least one non-heading, non-blank line."""
    for line in text.split("\n"):
        if line.strip() != "" and not line.startswith("#"):
            return True
    return False


def split_exercise_text(section_text):
    """Split an exercise section into one piece per numbered question."""
    pieces = QUESTION_START_PATTERN.split(section_text)
    questions = []
    for piece in pieces:
        if has_body_text(piece):
            questions.append(piece.strip())
    return questions

def build_chunks(chapter: ParsedChapter) -> Tuple[List[ParentChunk], List[ChildChunk]]:
    # 1. Join all pages so chunks can cross page boundaries
    #full_text = "\n\n".join(page.markdown for page in chapter.pages)
    full_text = "\n\n".join(clean_page_text(page.markdown) for page in chapter.pages)
    # 2. Fix heading levels, then read the chapter title
    normalized_text = normalize_headings(full_text)
    chapter_name = find_chapter_name(chapter.pages[0].markdown)

    # 3. Split into sections along headings (heading text stays inside the section)
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    section_docs = header_splitter.split_text(normalized_text)

    # parent_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=PARENT_MAX_CHARS, chunk_overlap=0, separators=SEPARATORS
    # )
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=PARENT_MAX_CHARS, chunk_overlap=PARENT_OVERLAP, separators=SEPARATORS
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHILD_MAX_CHARS, chunk_overlap=CHILD_OVERLAP, separators=SEPARATORS
    )

    parents = []
    children = []
    parent_counter = 0
    prefix = f"class{chapter.class_num}_{chapter.subject}_ch{chapter.chapter_num:02d}"

    for doc in section_docs:
        if not has_body_text(doc.page_content):
            continue  # heading-only section, its title lives in the children's metadata

        meta = build_metadata(doc.metadata, chapter, chapter_name)

        if meta["content_type"] == "exercise":
            # Each question is its own parent and its own child
            parent_texts = split_exercise_text(doc.page_content)
            child_groups = [[text] for text in parent_texts]
        else:
            parent_texts = parent_splitter.split_text(doc.page_content)
            child_groups = [child_splitter.split_text(text) for text in parent_texts]

        for parent_text, child_texts in zip(parent_texts, child_groups):
            if meta["content_type"] != "exercise" and len(parent_text) < MIN_PARENT_CHARS:
                continue  # tiny leftovers such as an empty table caption
            parent_id = f"{prefix}_p{parent_counter:03d}" 
            parent_counter += 1
            parents.append(ParentChunk(parent_id=parent_id, text=parent_text, **meta))

            for child_index, child_text in enumerate(child_texts):
                child = ChildChunk(
                    chunk_id=f"{parent_id}_c{child_index:02d}",
                    parent_id=parent_id,
                    text=child_text,
                    **meta,
                )
                children.append(child)

    return parents, children