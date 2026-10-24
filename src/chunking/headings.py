import re

# "1.2 Title" or "1.2.3 Title" (needs at least one dot, so "1. A solution..." is NOT matched)
NUMBERED_PATTERN = re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)$")
ACTIVITY_PATTERN = re.compile(
    r"^(Activity\s+\d+\.\d+|Carry out the following Activity)", re.IGNORECASE
)
CHAPTER_HEADING_PATTERN = re.compile(r"^CHAPTER\s*\d+", re.IGNORECASE)

# "CHAPTER2 Acids, Bases and Salts 1064CH02" -> captures the title only
CHAPTER_TITLE_PATTERN = re.compile(r"CHAPTER\s*\d+\s*(.+?)(?=\s+\d{3,4}CH\d{2}|\n|$)")

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
BULLET_GLYPH_PATTERN = re.compile(r"(?m)^(\s*)-\s+n\s+(?=[A-Z])")
BOOK_CODE_PATTERN = re.compile(r"\b\d{3,4}CH\d{2}\b")
CJK_PATTERN = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")  # stray OCR glyphs like 元

ACTIVITY_LABEL_ONLY_PATTERN = re.compile(r"^Activity\s+\d+\.\d+$", re.IGNORECASE)

# "Q U E S T I O N S 1. What is..." -> group 1 = heading word, group 2 = trailing text
QUESTIONS_WITH_TEXT_PATTERN = re.compile(
    r"^(Q\s?U\s?E\s?S\s?T\s?I\s?O\s?N\s?S?)\s+(\S.*)$", re.IGNORECASE
)

# Private-use glyphs (font bullets) and the Unicode replacement character
PRIVATE_USE_PATTERN = re.compile(r"[\ue000-\uf8ff\ufffd]")
MAX_HEADING_LENGTH = 150  # longer "headings" are really paragraphs


def clean_page_text(text):
    """Remove parser noise from one page of markdown."""
    text = HTML_COMMENT_PATTERN.sub("", text)        # <!-- ... --> markers (keeps OCR text between them)
    text = text.replace("<br>", " ")                 # line breaks inside OCR'd pictures
    text = PRIVATE_USE_PATTERN.sub("", text)         # font bullets such as the "�"
    text = CJK_PATTERN.sub("", text)                 # OCR garbage characters
    text = BOOK_CODE_PATTERN.sub("", text)           # 1064CH02
    text = BULLET_GLYPH_PATTERN.sub(r"\1- ", text)   # "- n Take" -> "- Take"
    text = re.sub(r"(?m)^(\s*-)\s{2,}", r"\1 ", text)  # "-  Test" -> "- Test"
    return text


def clean_heading_text(line):
    """Turn '##### **Activity 2.4**' into 'Activity 2.4'."""
    text = line.lstrip("#")
    text = text.replace("*", "")
    text = " ".join(text.split())   # collapse repeated spaces
    text = text.strip("_ ")         # italic markers like _Carry out..._
    return text


def parse_numbered_heading(text):
    """Return (section_number, title) or None if not a numbered heading."""
    match = NUMBERED_PATTERN.match(text)
    if match is None:
        return None
    return match.group(1), match.group(2)


def is_activity_heading(text):
    return ACTIVITY_PATTERN.match(text) is not None


def is_exercise_heading(text):
    # "E X E R C I S E S" -> "EXERCISES"  (end-of-chapter exercises)
    squashed = text.replace(" ", "").upper()
    return squashed.startswith("EXERCISE")


def is_questions_heading(text):
    # "Q U E S T I O N S" -> "QUESTIONS"  (in-text question boxes)
    squashed = text.replace(" ", "").upper()
    return squashed.startswith("QUESTION")


def is_summary_heading(text):
    return text.lower().startswith("what you have learnt")


def normalize_headings(markdown_text):
    """Rewrite all heading lines with proper levels and merge wrapped headings.

    Level rules:
      - 'CHAPTER<n> ...' heading            -> level 1
      - numbered heading '1.2' / '1.2.3'    -> level 2 / level 3
      - EXERCISES, 'What you have learnt'   -> level 2
      - Activity, Questions box, other
        plain headings                      -> one level below the last numbered heading
    """
    output_lines = []
    last_numbered_level = 1
    merge_target = None  # index of a numbered heading that may continue on the next heading line

    for line in markdown_text.split("\n"):
        # A lone "- **Activity 2.11**" bullet is really a heading: promote it
        bare = line.strip().lstrip("-").replace("*", "").strip()
        if not line.startswith("#") and ACTIVITY_LABEL_ONLY_PATTERN.match(bare):
            line = "##### " + bare

        if not line.startswith("#"):
            output_lines.append(line)
            if line.strip() != "":
                merge_target = None  # real text appeared, so no wrapped heading possible
            continue

        text = clean_heading_text(line)

        # Skip empty headings and icon headings such as "#### ?"
        has_letters_or_digits = any(ch.isalnum() for ch in text)
        if not has_letters_or_digits:
            continue

        # "Q U E S T I O N S 1. What is ..." -> heading "Q U E S T I O N S" + body text
        trailing_text = ""
        questions_match = QUESTIONS_WITH_TEXT_PATTERN.match(text)
        if questions_match is not None:
            text = questions_match.group(1)
            trailing_text = questions_match.group(2)

        # A "heading" this long is really a paragraph: keep it as plain text
        if len(text) > MAX_HEADING_LENGTH:
            output_lines.append(text)
            merge_target = None
            continue

        numbered = parse_numbered_heading(text)
        is_chapter = CHAPTER_HEADING_PATTERN.match(text) is not None
        is_activity = is_activity_heading(text)
        is_exercise = is_exercise_heading(text)
        is_questions = is_questions_heading(text)
        is_summary = is_summary_heading(text)
        is_plain = (
            numbered is None
            and not is_chapter
            and not is_activity
            and not is_exercise
            and not is_questions
            and not is_summary
        )

        # Wrapped heading: a plain heading right after a numbered heading
        if is_plain and merge_target is not None:
            output_lines[merge_target] += " " + text
            continue

        if is_chapter:
            level = 1
        elif numbered is not None:
            level = min(len(numbered[0].split(".")), 5)
            last_numbered_level = level
        elif is_exercise or is_summary:
            level = 2
            last_numbered_level = 2
        else:
            level = min(last_numbered_level + 1, 5)

        output_lines.append("#" * level + " " + text)

        if trailing_text != "":
            output_lines.append(trailing_text)
            merge_target = None
        elif numbered is not None:
            merge_target = len(output_lines) - 1
        else:
            merge_target = None

    

    return "\n".join(output_lines)


def find_chapter_name(first_page_markdown):
    """Read the chapter title from the raw text of page 1."""
    match = CHAPTER_TITLE_PATTERN.search(first_page_markdown)
    if match is None:
        return "Unknown"
    title = match.group(1)
    title = CJK_PATTERN.sub("", title)
    title = title.replace("#", "").replace("*", "")
    title = " ".join(title.split())
    return title