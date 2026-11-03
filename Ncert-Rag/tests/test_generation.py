import os
import pytest

from src.chunking.schemas import ParentChunk
from src.generation.chain import build_source_label
from src.generation.guardrails import (
    check_retrieval,
    extract_citation_numbers,
    keep_relevant_passages,
)
from src.generation.llm import build_llm


def test_extract_citation_numbers():
    assert extract_citation_numbers("According to [1], acids taste sour.", max_number=5) == [1]
    assert extract_citation_numbers("Facts from [1][2] and [3].", max_number=5) == [1, 2, 3]
    assert extract_citation_numbers("See [1, 2, 4].", max_number=5) == [1, 2, 4]
    assert extract_citation_numbers("Range [1-3] is cited.", max_number=5) == [1, 2, 3]
    assert extract_citation_numbers("Range [1–3] with en-dash.", max_number=5) == [1, 2, 3]
    assert extract_citation_numbers("Semicolons [1; 2].", max_number=5) == [1, 2]
    # Out of range citations should be omitted
    assert extract_citation_numbers("Invalid [99].", max_number=5) == []


def test_check_retrieval():
    parent = ParentChunk(
        parent_id="p1",
        text="Sample text",
        class_num=10,
        subject="science",
        chapter_num=1,
        chapter_name="Chemical Reactions",
    )
    # Empty results
    passed, reason = check_retrieval([])
    assert not passed
    assert reason == "no_results"

    # Below refusal score
    passed, reason = check_retrieval([(parent, 0.05)])
    assert not passed
    assert "low_score" in reason

    # Above refusal score
    passed, reason = check_retrieval([(parent, 0.85)])
    assert passed
    assert reason == "ok"


def test_keep_relevant_passages():
    parent = ParentChunk(
        parent_id="p1",
        text="Sample text",
        class_num=10,
        subject="science",
        chapter_num=1,
        chapter_name="Chemical Reactions",
    )
    results = [(parent, 0.45), (parent, 0.20), (parent, 0.80)]
    kept = keep_relevant_passages(results)
    assert len(kept) == 2
    assert kept[0][1] == 0.45
    assert kept[1][1] == 0.80


def test_build_source_label():
    parent = ParentChunk(
        parent_id="p1",
        text="Sample text",
        class_num=10,
        subject="science",
        chapter_num=1,
        chapter_name="Chemical Reactions and Equations",
        section_number="1.1",
        section_title="Chemical Equations",
        activity_label="Activity 1.1",
    )
    label = build_source_label(parent)
    assert "Class 10 Science" in label
    assert "Chapter 1: Chemical Reactions and Equations" in label
    assert "Section 1.1 Chemical Equations" in label
    assert "Activity 1.1" in label


def test_build_llm_graceful_missing_keys(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDERS", "groq,gemini,openrouter")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="None of the configured LLM_PROVIDERS"):
        build_llm()
