import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.language.parser import parse_intent


CORPUS_PATH = Path(__file__).parent / "fixtures" / "learner_sentence_regression.json"


def load_corpus() -> list[dict[str, Any]]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


class CorpusAIProvider(FakeAIProvider):
    def __init__(self, case: dict[str, Any]) -> None:
        super().__init__()
        self.case = case

    def interpret_player_sentence(self, request):
        self.interpretation_requests.append(request)
        interpretation = self.case.get("ai_interpretation")
        if not interpretation:
            return PlayerSentenceInterpretation(
                action="unknown",
                target="",
                confidence=0,
                reason="No corpus fallback expected.",
            )
        return PlayerSentenceInterpretation(**interpretation)


def test_learner_sentence_corpus_has_required_case_types() -> None:
    categories = {case["category"] for case in load_corpus()}

    assert {"accepted", "rejected", "ambiguous"} <= categories


@pytest.mark.parametrize("case", load_corpus(), ids=lambda case: case["id"])
def test_learner_sentence_corpus_routes(case: dict[str, Any]) -> None:
    provider = CorpusAIProvider(case)
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    for command in case["setup_commands"]:
        assert engine.handle(command).success
    provider.interpretation_requests.clear()
    before_state = deepcopy(engine.state)

    parsed = parse_intent(case["sentence"])
    result = engine.handle(case["sentence"])

    assert result.success is case["expected_success"]
    assert case["expected_message_contains"] in result.message

    if case["route"] == "deterministic_parser":
        assert parsed.action == case["expected_parser"]["action"]
        assert parsed.target == case["expected_parser"]["target"]
        assert provider.interpretation_requests == []
    else:
        assert parsed.action == "unknown"
        assert len(provider.interpretation_requests) == 1
        assert provider.interpretation_requests[0].player_sentence == case["sentence"]

    if "expected_room_id" in case:
        assert engine.state.current_room_id == case["expected_room_id"]
    if "expected_inventory_contains" in case:
        assert case["expected_inventory_contains"] in engine.state.player.inventory
    if case["category"] in {"rejected", "ambiguous"}:
        assert engine.state == before_state
