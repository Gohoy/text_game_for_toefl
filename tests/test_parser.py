from typing import get_args

from toefl_rpg.engine.actions import DETERMINISTIC_ACTIONS
from toefl_rpg.engine.actions import DeterministicAction
from toefl_rpg.language.parser import parse_intent


def test_shared_action_contract_matches_literal_type() -> None:
    assert DETERMINISTIC_ACTIONS == get_args(DeterministicAction)


def test_parser_outputs_only_shared_deterministic_actions() -> None:
    samples = [
        "help",
        "I want to go to the east",
        "look",
        "I want to inspect the microscope",
        "I want to collect the fungus sample",
        "I want to use the microscope",
        "talk to Dr. Lin",
        "I attack the invasive vine",
        "review vocabulary",
        "Please explain the word fungus",
        "inventory",
        "status",
        "quit",
        "Could you grab the specimen for my research?",
    ]

    for sample in samples:
        assert parse_intent(sample).action in DETERMINISTIC_ACTIONS


def test_parse_full_sentence_movement() -> None:
    intent = parse_intent("I want to go to the east")

    assert intent.action == "move"
    assert intent.target == "east"


def test_parse_verbose_movement_to_named_room() -> None:
    intent = parse_intent("I go north to the fungus grove.")

    assert intent.action == "move"
    assert intent.target == "north"


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


def test_parse_attack_sentence() -> None:
    intent = parse_intent("I attack the invasive vine")

    assert intent.action == "attack"
    assert intent.target == "the invasive vine"


def test_parse_review_command() -> None:
    intent = parse_intent("review vocabulary")

    assert intent.action == "review"
    assert intent.target == ""


def test_parse_explain_command() -> None:
    intent = parse_intent("Please explain the word fungus")

    assert intent.action == "explain"
    assert intent.target == "the word fungus"


def test_parse_what_does_word_mean_question() -> None:
    intent = parse_intent("What does bacteria mean?")

    assert intent.action == "explain"
    assert intent.target == "bacteria"
