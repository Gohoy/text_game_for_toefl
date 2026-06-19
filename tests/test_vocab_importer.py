from pathlib import Path

import pytest

from toefl_rpg.content.importer import (
    DEFAULT_VOCABULARY_PATH,
    find_category,
    load_vocabulary_categories,
    parse_vocabulary_text,
)


def test_parse_subject_and_semantic_categories() -> None:
    text = """
#按学科分类 Word List 1 生物
parasite
symbiosis

#按意群分类 Word List 28 心理 傲慢
arrogant
haughty

#附录二 阅读必备重要词组 第一部分 文章必备词组
in terms of
"""

    categories = parse_vocabulary_text(text)

    assert len(categories) == 2
    assert categories[0].group == "按学科分类"
    assert categories[0].list_number == 1
    assert categories[0].labels == ("生物",)
    assert categories[0].words == ("parasite", "symbiosis")
    assert categories[1].labels == ("心理", "傲慢")
    assert categories[1].words == ("arrogant", "haughty")


def test_parse_can_include_appendices() -> None:
    text = """
#附录二 阅读必备重要词组 第一部分 文章必备词组
in terms of
as a result
"""

    categories = parse_vocabulary_text(text, include_appendices=True)

    assert len(categories) == 1
    assert categories[0].group == "appendix"
    assert categories[0].words == ("in terms of", "as a result")


def test_find_category_by_label() -> None:
    categories = parse_vocabulary_text(
        """
#按学科分类 Word List 1 生物
parasite
#按学科分类 Word List 2 艺术
portrait
"""
    )

    biology = find_category(categories, "生物")

    assert biology is not None
    assert biology.words == ("parasite",)


def test_load_real_toefl_file_when_available() -> None:
    if not Path(DEFAULT_VOCABULARY_PATH).exists():
        pytest.skip("Local TOEFL vocabulary source file is not available.")

    categories = load_vocabulary_categories(DEFAULT_VOCABULARY_PATH)
    biology = find_category(categories, "生物")

    assert len(categories) >= 100
    assert biology is not None
    assert "parasite" in biology.words
    assert "fungus" in biology.words
