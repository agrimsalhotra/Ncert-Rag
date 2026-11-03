import re
from pathlib import Path

import pymupdf as fitz
import pymupdf4llm
from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders

from src.parsing.schemas import ParsedChapter, ParsedPage

# Matches names like class8_science_ch03.pdf or class_8_science_ch_3.pdf
FILENAME_PATTERN = re.compile(
    r"class[_-]?(\d+)[_-]([a-zA-Z]+)[_-]ch[_-]?(\d+)\.pdf", re.IGNORECASE
)


def read_filename_info(pdf_path: Path):
    """Return (class_num, subject, chapter_num) from the file name."""
    match = FILENAME_PATTERN.fullmatch(pdf_path.name)
    if match is None:
        raise ValueError(
            f"File name '{pdf_path.name}' does not match "
            "class{N}_{subject}_ch{NN}.pdf"
        )
    class_num = int(match.group(1))
    subject = match.group(2).lower()
    chapter_num = int(match.group(3))
    return class_num, subject, chapter_num


def parse_chapter_pdf(pdf_path: Path) -> ParsedChapter:
    """Parse one chapter PDF into a validated ParsedChapter object."""
    class_num, subject, chapter_num = read_filename_info(pdf_path)

    doc = fitz.open(str(pdf_path))

    # Learns which font sizes are headings by analysing the whole document
    header_info = IdentifyHeaders(doc)

    # One dictionary per page, each with 'text', 'tables', 'images', 'metadata'
    page_dicts = pymupdf4llm.to_markdown(
        doc,
        hdr_info=header_info,
        page_chunks=True,
        write_images=False,
        header=False,   # omit running page headers
        footer=False,   # omit running page footers
    )

    pages = []
    for index, page_dict in enumerate(page_dicts):
        page = ParsedPage(
            page_number=index + 1,
            markdown=page_dict.get("text", "") or "",
            table_count=len(page_dict.get("tables", []) or []),
            image_count=len(page_dict.get("images", []) or []),
        )
        pages.append(page)

    doc.close()

    return ParsedChapter(
        source_file=pdf_path.name,
        class_num=class_num,
        subject=subject,
        chapter_num=chapter_num,
        pages=pages,
    )
