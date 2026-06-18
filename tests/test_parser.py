from toefl_rpg.language.parser import parse_intent


def test_parse_full_sentence_movement() -> None:
    intent = parse_intent("I want to go to the east")

    assert intent.action == "move"
    assert intent.target == "east"


def test_parse_inspect_sentence() -> None:
    intent = parse_intent("I want to inspect the microscope")

    assert intent.action == "inspect"
    assert intent.target == "the microscope"


def test_parse_collect_sentence() -> None:
    intent = parse_intent("I want to collect the fungus sample")

    assert intent.action == "collect"
    assert intent.target == "the fungus sample"


def test_parse_use_sentence() -> None:
    intent = parse_intent("I want to use the microscope")

    assert intent.action == "use"
    assert intent.target == "the microscope"
