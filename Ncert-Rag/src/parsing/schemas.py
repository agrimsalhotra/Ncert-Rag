from typing import List
from pydantic import BaseModel


class ParsedPage(BaseModel):
    page_number: int       # 1-based, matches the printed PDF page order
    markdown: str          # page text with headings as # lines
    table_count: int
    image_count: int


class ParsedChapter(BaseModel):
    source_file: str
    class_num: int
    subject: str
    chapter_num: int
    pages: List[ParsedPage]