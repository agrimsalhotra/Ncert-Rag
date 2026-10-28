def parent_matches(parent, expected_list):
    """True if the parent's section number, activity label or section title is expected."""
    return (
        parent.section_number in expected_list
        or parent.activity_label in expected_list
        or parent.section_title in expected_list
    )


def retrieval_hit(item, retrieved_parents):
    """Did any passage shown to the LLM come from an expected location? None = not applicable."""
    if len(item.expected_any) == 0:
        return None
    for parent in retrieved_parents:
        if parent_matches(parent, item.expected_any):
            return True
    return False


def answer_check(item, answer_text):
    """Does the answer contain at least one required word? None = not applicable."""
    if len(item.must_include_any) == 0:
        return None
    lowered = answer_text.lower()
    for word in item.must_include_any:
        if word.lower() in lowered:
            return True
    return False


def refusal_ok(item, result):
    """Refused when it should be, answered when it should be. Technical failures count as wrong."""
    technical_failure = (
        result.reason.startswith("llm_error") or result.reason == "empty_llm_response"
    )
    if technical_failure:
        return False
    return result.refused == item.should_refuse