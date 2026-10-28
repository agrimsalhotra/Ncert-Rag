import json
from typing import List

from pydantic import BaseModel

from config.settings import GOLDEN_SET_PATH


class GoldenItem(BaseModel):
    id: str
    question: str
    reference: str = ""               # ground-truth answer ("" for refusal tests)
    expected_any: List[str] = []      # section numbers / activity labels where the answer lives
    must_include_any: List[str] = []  # the answer must contain at least one of these
    should_refuse: bool = False       # True for out-of-syllabus or junk questions


def load_golden_set() -> List[GoldenItem]:
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        raw_items = json.load(f)
    return [GoldenItem.model_validate(raw) for raw in raw_items]