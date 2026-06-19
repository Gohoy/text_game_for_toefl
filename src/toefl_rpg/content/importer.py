from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_VOCABULARY_PATH = Path("/Users/gaohongyu1/Downloads/TOEFLiBT  词以类记2.0.txt")
WORD_LIST_HEADING = re.compile(
    r"^(?P<group>\S+)\s+Word List\s+(?P<number>\d+)\s+(?P<labels>.+)$"
)


@dataclass(frozen=True)
class VocabularyCategory:
    heading: str
    group: str
    list_number: int | None
    labels: tuple[str, ...]
    words: tuple[str, ...] = field(default_factory=tuple)

    @property
    def primary_label(self) -> str:
        return self.labels[0] if self.labels else self.heading


def load_vocabulary_categories(
    path: Path = DEFAULT_VOCABULARY_PATH,
    *,
    include_appendices: bool = False,
) -> list[VocabularyCategory]:
    return parse_vocabulary_text(path.read_text(encoding="utf-8"), include_appendices=include_appendices)


def parse_vocabulary_text(text: str, *, include_appendices: bool = False) -> list[VocabularyCategory]:
    categories: list[VocabularyCategory] = []
    current_heading = ""
    current_words: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            _append_category(categories, current_heading, current_words, include_appendices)
            current_heading = line.removeprefix("#").strip()
            current_words = []
            continue
        if current_heading:
            current_words.append(line)

    _append_category(categories, current_heading, current_words, include_appendices)
    return categories


def find_category(categories: list[VocabularyCategory], label: str) -> VocabularyCategory | None:
    for category in categories:
        if label in category.labels:
            return category
    return None


def _append_category(
    categories: list[VocabularyCategory],
    heading: str,
    words: list[str],
    include_appendices: bool,
) -> None:
    if not heading or not words:
        return

    parsed = _parse_heading(heading)
    if parsed is None:
        if not include_appendices:
            return
        category = VocabularyCategory(
            heading=heading,
            group="appendix",
            list_number=None,
            labels=(heading,),
            words=tuple(words),
        )
    else:
        group, list_number, labels = parsed
        category = VocabularyCategory(
            heading=heading,
            group=group,
            list_number=list_number,
            labels=labels,
            words=tuple(words),
        )

    categories.append(category)


def _parse_heading(heading: str) -> tuple[str, int, tuple[str, ...]] | None:
    match = WORD_LIST_HEADING.match(heading)
    if match is None:
        return None
    labels = tuple(label for label in match.group("labels").split() if label)
    return match.group("group"), int(match.group("number")), labels
