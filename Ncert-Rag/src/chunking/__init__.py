"""
Chunking module offering multiple chunking strategies for NCERT textbooks:
- Fixed-size character chunking
- Recursive character text splitting
- Token-based splitting
- Sentence / Semantic splitting
- Markdown / Header-based splitting
- Hierarchical (Parent-Child) splitting
"""

from src.chunking.schemas import Chunk, ParentChunk, ChildChunk, ChunkMetadata
from src.chunking.fixed import split_fixed_size
from src.chunking.recursive import split_recursive
from src.chunking.token_based import split_token_based
from src.chunking.semantic import split_semantic_sentences
from src.chunking.markdown import split_markdown_sections
from src.chunking.hierarchical import build_chunks as split_hierarchical

__all__ = [
    "Chunk",
    "ParentChunk",
    "ChildChunk",
    "ChunkMetadata",
    "split_fixed_size",
    "split_recursive",
    "split_token_based",
    "split_semantic_sentences",
    "split_markdown_sections",
    "split_hierarchical",
]
