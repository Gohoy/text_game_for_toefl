from typing import get_args

import pytest

from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.engine.actions import DETERMINISTIC_ACTIONS
from toefl_rpg.engine.actions import DeterministicAction
from toefl_rpg.language.parser import parse_intent


INTENT_TARGET_CONTRACT_CASES = [
    ("help", "help", ""),
    ("go north", "move", "north"),
    ("look", "look", ""),
    ("inspect microscope", "inspect", "microscope"),
    ("collect fungus sample", "collect", "fungus sample"),
    ("use microscope", "use", "microscope"),
    ("talk to Dr. Lin", "talk", "dr. lin"),
    ("attack invasive vine", "attack", "invasive vine"),
    ("review vocabulary", "review", ""),
    ("explain fungus", "explain", "fungus"),
    ("inventory", "inventory", ""),
    ("status", "status", ""),
    ("quit", "quit", ""),
    ("sing a song", "unknown", "sing a song"),
]


def test_shared_action_contract_matches_literal_type() -> None:
    assert DETERMINISTIC_ACTIONS == get_args(DeterministicAction)


def test_intent_target_contract_covers_every_shared_action() -> None:
    documented_actions = tuple(case[1] for case in INTENT_TARGET_CONTRACT_CASES)

    assert documented_actions == DETERMINISTIC_ACTIONS


@pytest.mark.parametrize(
    ("sentence", "expected_action", "expected_target"),
    INTENT_TARGET_CONTRACT_CASES,
)
def test_parser_target_conventions_for_shared_actions(
    sentence: str, expected_action: DeterministicAction, expected_target: str
) -> None:
    intent = parse_intent(sentence)

    assert intent.action == expected_action
    assert intent.target == expected_target


@pytest.mark.parametrize(
    ("sentence", "expected_action", "expected_target"),
    INTENT_TARGET_CONTRACT_CASES,
)
def test_ai_interpretation_target_conventions_match_parser_contract(
    sentence: str, expected_action: DeterministicAction, expected_target: str
) -> None:
    response = PlayerSentenceInterpretation(
        action=expected_action,
        target=expected_target,
        confidence=0.9,
        reason=f"Interpret {sentence!r} using the shared deterministic contract.",
    )

    assert response.action == expected_action
    assert response.target == expected_target


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


def test_parse_punctuation_heavy_movement_sentence() -> None:
    intent = parse_intent("I want to go north, please!!!")

    assert intent.action == "move"
    assert intent.target == "north"


def test_parse_broad_destination_request_as_unknown() -> None:
    intent = parse_intent("Please take me to the lab.")

    assert intent.action == "unknown"
    assert intent.target == "please take me to the lab"


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
