from pathlib import Path
from typing import Dict, List

from config.settings import CHUNKS_DIR
from src.chunking.schemas import ChildChunk, ParentChunk


def load_children(path: Path) -> List[ChildChunk]:
    """Read a *_children.jsonl file. Pydantic validates every line."""
    children = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() == "":
                continue
            # Raises ValidationError if a field is missing or content_type is not allowed
            children.append(ChildChunk.model_validate_json(line))
    return children


def load_parents(path: Path) -> Dict[str, ParentChunk]:
    """Read a *_parents.jsonl file into a dictionary: parent_id -> ParentChunk."""
    parents = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip() == "":
                continue
            parent = ParentChunk.model_validate_json(line)
            parents[parent.parent_id] = parent
    return parents


def load_all_parents() -> Dict[str, ParentChunk]:
    """Load the parents of every chapter (used again in Step 4)."""
    all_parents = {}
    for path in sorted(CHUNKS_DIR.glob("*_parents.jsonl")):
        all_parents.update(load_parents(path))
    return all_parents


def validate_children(children: List[ChildChunk], parents: Dict[str, ParentChunk]):
    """Extra checks that a plain schema cannot do."""
    seen_ids = set()
    for child in children:
        if child.chunk_id in seen_ids:
            raise ValueError(f"Duplicate chunk_id: {child.chunk_id}")
        seen_ids.add(child.chunk_id)

        if child.parent_id not in parents:
            raise ValueError(f"{child.chunk_id} points to missing parent {child.parent_id}")

        if child.text.strip() == "":
            raise ValueError(f"{child.chunk_id} has empty text")