from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel

ContentType = Literal["concept", "activity", "exercise", "general"]


class ChunkMetadata(BaseModel):
    class_num: int
    subject: str
    chapter_num: int
    chapter_name: str
    section_number: str = ""   # e.g. "2.1.3" ("" if none)
    section_title: str = ""
    activity_label: str = ""   # e.g. "Activity 2.5" ("" if not an activity)
    content_type: ContentType = "concept"
    strategy: Optional[str] = None  # e.g. "fixed", "recursive", "token", "semantic", "markdown", "hierarchical"


class Chunk(ChunkMetadata):
    chunk_id: str
    text: str


class ParentChunk(ChunkMetadata):
    parent_id: str
    text: str


class ChildChunk(ChunkMetadata):
    chunk_id: str
    parent_id: str
    text: str