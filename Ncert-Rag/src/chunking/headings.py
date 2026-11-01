import re

# "1.2 Title" or "1.2.3 Title" (needs at least one dot, so "1. A solution..." is NOT matched)
NUMBERED_PATTERN = re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)$")
ACTIVITY_PATTERN = re.compile(
    r"^(Activity\s+\d+\.\d+|Carry out the following Activity)", re.IGNORECASE
)
CHAPTER_HEADING_PATTERN = re.compile(r"^CHAPTER\s*\d+", re.IGNORECASE)

# "CHAPTER2 Acids, Bases and Salts 1064CH02" -> captures the title only
# CHAPTER_TITLE_PATTERN = re.compile(r"CHAPTER\s*\d+\s*(.+?)(?=\s+\d{3,4}CH\d{2}|\n|$)")

NCERT_SCIENCE_CHAPTERS = {
    # Class 6 - Curiosity
    6: {
        1: "The Wonderful World of Science",
        2: "Diversity in the Living World",
        3: "Mindful Eating: A Path to a Healthy Body",
        4: "Exploring Magnets",
        5: "Measurement of Length and Motion",
        6: "Materials Around Us",
        7: "Temperature and its Measurement",
        8: "A Journey through States of Water",
        9: "Methods of Separation in Everyday Life",
        10: "Living Creatures: Exploring their Characteristics",
        11: "Nature's Treasures",
        12: "Beyond Earth",
    },
    # Class 7 - Curiosity
    7: {
        1: "The Ever-Evolving World of Science",
        2: "Exploring Substances: Acidic, Basic, and Neutral",
        3: "Electricity: Circuits and their Components",
        4: "The World of Metals and Non-metals",
        5: "Changes Around Us: Physical and Chemical",
        6: "Adolescence: A Stage of Growth and Change",
        7: "Heat Transfer in Nature",
        8: "Measurement of Time and Motion",
        9: "Life Processes in Animals",
        10: "Life Processes in Plants",
        11: "Light: Shadows and Reflections",
        12: "Earth, Moon, and the Sun",
    },
    # Class 8 - Curiosity
    8: {
        1: "Exploring the Investigative World of Science",
        2: "The Invisible Living World: Beyond Our Naked Eye",
        3: "Health: The Ultimate Treasure",
        4: "Electricity: Magnetic and Heating Effects",
        5: "Exploring Forces",
        6: "Pressure, Winds, Storms, and Cyclones",
        7: "Particulate Nature of Matter",
        8: "Nature of Matter: Elements, Compounds, and Mixtures",
        9: "The Amazing World of Solutes, Solvents, and Solutions",
        10: "Light: Mirrors and Lenses",
        11: "Keeping Time with the Skies",
        12: "How Nature Works in Harmony",
        13: "Our Home: Earth, a Unique Life-Sustaining Planet",
    },
    # Class 9 - Exploration
    9: {
        1: "Exploration: Entering the World of Secondary Science",
        2: "Cell: The Building Block of Life",
        3: "Tissues in Action",
        4: "Describing Motion Around Us",
        5: "Exploring Mixtures and Their Separation",
        6: "How Forces Affect Motion",
        7: "Work, Energy, and Simple Machines",
        8: "Journey Inside the Atom",
        9: "Atomic Foundations of Matter",
        10: "Sound Waves: Characteristics and Applications",
        11: "Reproduction: How Life Continues",
        12: "Patterns in Life: Diversity and Classification",
        13: "Earth as a System: Energy, Matter, and Life",
    },
    # Class 10 - Science (Rationalised Syllabus)
    10: {
        1: "Chemical Reactions and Equations",
        2: "Acids, Bases and Salts",
        3: "Metals and Non-metals",
        4: "Carbon and its Compounds",
        5: "Life Processes",
        6: "Control and Coordination",
        7: "How do Organisms Reproduce?",
        8: "Heredity",
        9: "Light – Reflection and Refraction",
        10: "The Human Eye and the Colourful World",
        11: "Electricity",
        12: "Magnetic Effects of Electric Current",
        13: "Our Environment",
    },
}
CHAPTER_TITLE_PATTERNS = [
    # "CHAPTER 5 Life Processes 1064CH05"
    re.compile(r"CHAPTER\s*\d+\s*(.+?)(?=\s+\d{3,4}CH\d{2}|\n|$)", re.IGNORECASE),
    # "5 Exploring Forces" or "5. Exploring Forces"
    re.compile(r"^\s*#*\s*\d+\s*[\.\-:]?\s+([A-Za-z][A-Za-z\s:,]+?)(?=\s+\d{3,4}CH\d{2}|\n|$)", re.MULTILINE),
    # "**Diversity in the Living World 2**"
    re.compile(r"\*{0,2}([A-Za-z][A-Za-z\s:,]+?)\s+\d+\*{0,2}", re.MULTILINE),
]

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


# def is_exercise_heading(text):
#     # "E X E R C I S E S" -> "EXERCISES"  (end-of-chapter exercises)
#     squashed = text.replace(" ", "").upper()
    
#     return squashed.startswith("EXERCISE")
def is_exercise_heading(text):
    # Remove all whitespace and convert to uppercase for robust matching
    squashed = "".join(text.split()).upper()
    
    target_prefixes = (
        "EXERCISE",
        "LETUSENHANCEOURLEARNING",
        "REVISEREFLECTREFINE",
        "KEEPTHECURIOSITYALIVE",
    )
    
    return squashed.startswith(target_prefixes)


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


# def find_chapter_name(first_page_markdown):
#     """Read the chapter title from the raw text of page 1."""
#     match = CHAPTER_TITLE_PATTERN.search(first_page_markdown)
#     if match is None:
#         return "Unknown"
#     title = match.group(1)
#     title = CJK_PATTERN.sub("", title)
#     title = title.replace("#", "").replace("*", "")
#     title = " ".join(title.split())
#     return title
def find_chapter_name(first_page_markdown: str, class_num: int = None, chapter_num: int = None) -> str:
    """Read the chapter title using catalog lookup, regex, or page-1 header heuristics."""
    # 1. Exact catalog match if class and chapter numbers are provided
    if class_num in NCERT_SCIENCE_CHAPTERS and chapter_num in NCERT_SCIENCE_CHAPTERS[class_num]:
        return NCERT_SCIENCE_CHAPTERS[class_num][chapter_num]

    # 2. Try regex extraction from the first page text
    for pattern in CHAPTER_TITLE_PATTERNS:
        match = pattern.search(first_page_markdown)
        if match:
            candidate = match.group(1).strip()
            candidate = CJK_PATTERN.sub("", candidate)
            candidate = candidate.replace("#", "").replace("*", "").strip()
            candidate = " ".join(candidate.split())
            if 3 < len(candidate) < 80:
                return candidate

    # 3. Fallback: inspect the first non-empty heading line
    for line in first_page_markdown.splitlines():
        line = line.strip()
        if line.startswith("#"):
            cleaned = clean_heading_text(line)
            if cleaned and len(cleaned) < 80:
                return cleaned

    return "Unknown"