"""Layout extraction and analysis utilities for NCERT PDF documents."""

import re
from typing import List, Dict, Any


def is_table_block(block_text: str) -> bool:
    """Detect if a markdown block represents a table."""
    lines = [line.strip() for line in block_text.splitlines() if line.strip()]
    if len(lines) >= 2:
        return lines[0].startswith("|") and ("---" in lines[1] or lines[1].startswith("|"))
    return False


def clean_layout_noise(text: str) -> str:
    """Normalize whitespace and strip layout artifacts."""
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on lines
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()
