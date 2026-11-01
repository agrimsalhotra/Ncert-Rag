from src.chunking.headings import (
    is_activity_heading,
    is_exercise_heading,
    is_questions_heading,
    is_summary_heading,
    parse_numbered_heading,
)
from src.parsing.schemas import ParsedChapter


def build_metadata(headers, chapter: ParsedChapter, chapter_name):
    """Build the metadata dict for one section.

    `headers` comes from MarkdownHeaderTextSplitter, e.g.
    {"h1": "CHAPTER1 ...", "h2": "1.2 ...", "h3": "1.2.2 ...", "h4": "Activity 1.5"}
    """
    section_number = ""
    section_title = ""
    activity_label = ""
    is_end_exercises = False
    is_questions_box = False
    is_summary = False

    # Check deepest heading first so we pick the closest numbered section
    for key in ["h5", "h4", "h3", "h2", "h1"]:
        text = headers.get(key)
        if text is None:
            continue

        if is_exercise_heading(text):
            is_end_exercises = True
        elif is_questions_heading(text):
            is_questions_box = True
        elif is_summary_heading(text):
            is_summary = True
        elif is_activity_heading(text):
            if activity_label == "":
                activity_label = text
        else:
            parsed = parse_numbered_heading(text)
            if parsed is not None and section_number == "":
                section_number, section_title = parsed

    if is_end_exercises or is_questions_box:
        content_type = "exercise"
    elif activity_label != "":
        content_type = "activity"
    else:
        content_type = "concept"

    # These two blocks are not part of any numbered section
    if is_end_exercises:
        section_number = ""
        section_title = "Exercises"
    if is_summary:
        section_number = ""
        section_title = "What you have learnt"

    return {
        "class_num": chapter.class_num,
        "subject": chapter.subject,
        "chapter_num": chapter.chapter_num,
        "chapter_name": chapter_name,
        "section_number": section_number,
        "section_title": section_title,
        "activity_label": activity_label,
        "content_type": content_type,
    }