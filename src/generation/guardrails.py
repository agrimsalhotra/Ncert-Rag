from typing import List, Tuple

from config.settings import MIN_PASSAGE_SCORE, REFUSAL_SCORE
from src.chunking.schemas import ParentChunk

REFUSAL_MESSAGE = (
    "I can only answer from the NCERT Science chapters loaded in this system, "
    "and I could not find this topic in them. Try rephrasing, or ask about a "
    "topic from those chapters."
)

CITATION_FAILURE_MESSAGE = (
    "I could not produce a properly cited answer from the textbook. "
    "Please try rephrasing your question."
)
SERVICE_ERROR_MESSAGE = (
    "The answer service is temporarily unavailable. Please try again in a moment."
)


def check_retrieval(results: List[Tuple[ParentChunk, float]]):
    """Gate 1: decide whether retrieval found anything worth answering from."""
    if len(results) == 0:
        return False, "no_results"
    best_score = results[0][1]   # results are sorted best first
    if best_score < REFUSAL_SCORE:
        return False, f"low_score ({best_score:.3f})"
    return True, "ok"


def keep_relevant_passages(results: List[Tuple[ParentChunk, float]]):
    """Drop weak matches so the LLM only sees passages that are likely useful."""
    relevant = []
    for parent, score in results:
        if score >= MIN_PASSAGE_SCORE:
            relevant.append((parent, score))
    return relevant


def extract_citation_numbers(answer_text: str, max_number: int) -> List[int]:
    """Find valid citation numbers such as [1], [2][3] or [1, 2], without duplicates."""
    import re

    numbers = []
    for group in re.findall(r"\[([\d,\s]+)\]", answer_text):
        for piece in group.split(","):
            piece = piece.strip()
            if not piece.isdigit():
                continue
            number = int(piece)
            if 1 <= number <= max_number and number not in numbers:
                numbers.append(number)
    return numbers