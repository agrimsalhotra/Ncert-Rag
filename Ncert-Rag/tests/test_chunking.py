import pytest
from src.chunking.headings import (
    clean_heading_text,
    clean_page_text,
    find_chapter_name,
    is_activity_heading,
    is_exercise_heading,
    is_questions_heading,
    is_summary_heading,
    normalize_headings,
    parse_numbered_heading,
)
from src.chunking.fixed import split_fixed_size
from src.chunking.recursive import split_recursive
from src.chunking.token_based import split_token_based
from src.chunking.semantic import split_semantic_sentences, split_sentences
from src.chunking.markdown import split_markdown_sections
from src.chunking.hierarchical import build_chunks
from src.parsing.schemas import ParsedChapter, ParsedPage


@pytest.fixture
def sample_chapter():
    page1 = ParsedPage(
        page_number=1,
        markdown=(
            "# CHAPTER 1 Chemical Reactions and Equations\n\n"
            "## 1.1 Chemical Equations\n"
            "Activity 1.1: Clean a magnesium ribbon about 3-4 cm long.\n\n"
            "Magnesium ribbon burns with a dazzling white flame and changes into a white powder.\n\n"
            "### 1.1.1 Writing a Chemical Equation\n"
            "Magnesium + Oxygen -> Magnesium oxide\n\n"
            "## 1.2 Types of Chemical Reactions\n"
            "We have learnt that during a chemical reaction atoms of one element do not change.\n"
        ),
        table_count=0,
        image_count=1,
    )
    page2 = ParsedPage(
        page_number=2,
        markdown=(
            "## EXERCISES\n\n"
            "1. Which of the statements about the reaction below are incorrect?\n"
            "2. Fe2O3 + 2Al -> Al2O3 + 2Fe. The above reaction is an example of a?\n\n"
            "## What you have learnt\n"
            "A complete chemical equation represents the reactants, products and their physical states."
        ),
        table_count=0,
        image_count=0,
    )
    return ParsedChapter(
        source_file="class10_science_ch01.pdf",
        class_num=10,
        subject="science",
        chapter_num=1,
        pages=[page1, page2],
    )


def test_parse_numbered_heading():
    assert parse_numbered_heading("1.2 Title") == ("1.2", "Title")
    assert parse_numbered_heading("1.2") == ("1.2", "")
    assert parse_numbered_heading("1.2.3") == ("1.2.3", "")
    assert parse_numbered_heading("1.2.3 Deep Subsection") == ("1.2.3", "Deep Subsection")
    assert parse_numbered_heading("1. Single dot not section") is None
    assert parse_numbered_heading("No numbers here") is None


def test_heading_detection():
    assert is_exercise_heading("EXERCISES")
    assert is_exercise_heading("Let us enhance our learning")
    assert is_questions_heading("QUESTIONS")
    assert is_questions_heading("Q U E S T I O N S")
    assert is_activity_heading("Activity 1.1")
    assert is_summary_heading("What you have learnt")


def test_find_chapter_name():
    # Catalog lookup
    assert find_chapter_name("", class_num=10, chapter_num=1) == "Chemical Reactions and Equations"
    assert find_chapter_name("", class_num="10", chapter_num="2") == "Acids, Bases and Salts"
    # Fallback when empty
    assert find_chapter_name("") == "Unknown"


def test_empty_chapter_does_not_crash():
    empty_ch = ParsedChapter(
        source_file="class10_science_ch01.pdf",
        class_num=10,
        subject="science",
        chapter_num=1,
        pages=[],
    )
    assert split_fixed_size(empty_ch) == []
    assert split_recursive(empty_ch) == []
    assert split_token_based(empty_ch) == []
    assert split_semantic_sentences(empty_ch) == []
    assert split_markdown_sections(empty_ch) == []
    parents, children = build_chunks(empty_ch)
    assert parents == []
    assert children == []


def test_all_strategies_on_sample(sample_chapter):
    fixed = split_fixed_size(sample_chapter, chunk_size=200, chunk_overlap=20)
    assert len(fixed) > 0
    assert all(c.strategy == "fixed" for c in fixed)

    rec = split_recursive(sample_chapter, chunk_size=300, chunk_overlap=50)
    assert len(rec) > 0
    assert all(c.strategy == "recursive" for c in rec)

    tok = split_token_based(sample_chapter, chunk_size=100, chunk_overlap=10)
    assert len(tok) > 0
    assert all(c.strategy == "token" for c in tok)

    sem = split_semantic_sentences(sample_chapter, target_chunk_chars=300)
    assert len(sem) > 0
    assert all(c.strategy == "semantic" for c in sem)

    md = split_markdown_sections(sample_chapter, max_chunk_size=400)
    assert len(md) > 0
    assert all(c.strategy == "markdown" for c in md)

    parents, children = build_chunks(sample_chapter)
    assert len(parents) > 0
    assert len(children) >= len(parents)
    # Check parent-child linkage
    parent_ids = {p.parent_id for p in parents}
    for child in children:
        assert child.parent_id in parent_ids
        assert child.text.strip() != ""


def test_semantic_overlap_no_duplicates():
    # Ensure long sentence does not cause duplicate chunk emission
    page = ParsedPage(
        page_number=1,
        markdown="A" * 900 + ". Short sentence. Another short sentence.",
        table_count=0,
        image_count=0,
    )
    ch = ParsedChapter(
        source_file="class10_science_ch01.pdf",
        class_num=10,
        subject="science",
        chapter_num=1,
        pages=[page],
    )
    chunks = split_semantic_sentences(ch, target_chunk_chars=800, overlap_sentences=1)
    assert len(chunks) >= 2
    # Chunk 0 and Chunk 1 should not be identical
    assert chunks[0].text != chunks[1].text
