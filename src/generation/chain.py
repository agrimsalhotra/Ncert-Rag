import logging
from typing import List

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

from src.chunking.schemas import ParentChunk
from src.generation.guardrails import (
    CITATION_FAILURE_MESSAGE,
    REFUSAL_MESSAGE,
    SERVICE_ERROR_MESSAGE,
    check_retrieval,
    extract_citation_numbers,
    keep_relevant_passages,
)
from src.generation.llm import build_llm
from src.generation.prompts import ANSWER_PROMPT, INSUFFICIENT_MARKER
from src.retrieval.search import NcertSearch

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2   # one retry if the answer has no valid citation
CITATION_REMINDER = (
    "\n\nReminder: after every fact, cite the excerpt number in square brackets, "
    "like [1]. Reply with only the answer."
)


class Source(BaseModel):
    number: int
    label: str
    content_type: str
    score: float


class RagAnswer(BaseModel):
    question: str
    answer: str
    refused: bool
    reason: str          # "ok", or why the answer was refused
    sources: List[Source]
    raw_answer: str = ""  # what the LLM actually returned (for debugging)
    retrieved_parents: List[ParentChunk] = []   # passages shown to the LLM (for evaluation)


def build_source_label(parent: ParentChunk) -> str:
    """Human-readable location, built from metadata (never written by the LLM)."""
    parts = [
        f"Class {parent.class_num} {parent.subject.title()}",
        f"Chapter {parent.chapter_num}: {parent.chapter_name}",
    ]
    if parent.section_number != "":
        parts.append(f"Section {parent.section_number} {parent.section_title}")
    elif parent.section_title != "":
        parts.append(parent.section_title)
    if parent.activity_label != "":
        parts.append(parent.activity_label)
    return ", ".join(parts)


def build_context(passages) -> str:
    """Number the passages [1], [2], ... and put their location above the text."""
    blocks = []
    for number, (parent, score) in enumerate(passages, start=1):
        blocks.append(f"[{number}] {build_source_label(parent)}\n{parent.text}")
    return "\n\n---\n\n".join(blocks)


class NcertRag:
    def __init__(self):
        self.searcher = NcertSearch()
        llm = build_llm()
        self.chain = ANSWER_PROMPT | llm | StrOutputParser()  # LCEL pipeline

    def _refuse(
        self, question, message, reason, raw_answer="", retrieved_parents=None
    ) -> RagAnswer:
        if raw_answer != "":
            logger.warning("Refused (%s). Raw LLM answer: %r", reason, raw_answer[:500])
        return RagAnswer(
            question=question,
            answer=message,
            refused=True,
            reason=reason,
            sources=[],
            raw_answer=raw_answer,
            retrieved_parents=retrieved_parents or [],
        )

    def ask(self, question: str, class_num=None) -> RagAnswer:
        # Gate 1: is there anything relevant at all?
        results = self.searcher.search(question, class_num=class_num)
        passed, reason = check_retrieval(results)
        if not passed:
            return self._refuse(question, REFUSAL_MESSAGE, reason)

        passages = keep_relevant_passages(results)
        retrieved = [parent for parent, score in passages]
        context = build_context(passages)

        # Ask the LLM. If the answer has no valid citation, try once more.
        answer_text = ""
        cited_numbers = []
        for attempt in range(1, MAX_ATTEMPTS + 1):
            prompt_question = question
            if attempt > 1:
                prompt_question = question + CITATION_REMINDER

            try:
                answer_text = self.chain.invoke(
                    {"context": context, "question": prompt_question}
                ).strip()
                answer_text = answer_text.replace("\u202f", " ").replace("\u00a0", " ")
            except Exception as error:
                # Every provider failed (rate limit, network, bad key, ...)
                reason = f"llm_error: {type(error).__name__}"
                return self._refuse(
                    question, SERVICE_ERROR_MESSAGE, reason, retrieved_parents=retrieved
                )

            # Gate 2: the LLM itself says the excerpts are not enough
            if INSUFFICIENT_MARKER in answer_text:
                return self._refuse(
                    question, REFUSAL_MESSAGE, "llm_insufficient_context",
                    answer_text, retrieved,
                )

            # Gate 3: the answer must cite at least one real excerpt
            cited_numbers = extract_citation_numbers(answer_text, len(passages))
            if len(cited_numbers) > 0:
                break
            logger.warning(
                "Attempt %d had no valid citation. Raw answer: %r", attempt, answer_text[:500]
            )

        if len(cited_numbers) == 0:
            if answer_text == "":
                return self._refuse(
                    question, SERVICE_ERROR_MESSAGE, "empty_llm_response",
                    retrieved_parents=retrieved,
                )
            return self._refuse(
                question, CITATION_FAILURE_MESSAGE, "no_valid_citation",
                answer_text, retrieved,
            )

        sources = []
        for number in cited_numbers:
            parent, score = passages[number - 1]
            sources.append(
                Source(
                    number=number,
                    label=build_source_label(parent),
                    content_type=parent.content_type,
                    score=score,
                )
            )
        return RagAnswer(
            question=question,
            answer=answer_text,
            refused=False,
            reason="ok",
            sources=sources,
            raw_answer=answer_text,
            retrieved_parents=retrieved,
        )