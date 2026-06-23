import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.ai.contract import ReviewAnswerEvaluation
from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.language.parser import parse_intent


CORPUS_PATH = Path(__file__).parent / "fixtures" / "learner_sentence_regression.json"
REVIEW_CORPUS_PATH = Path(__file__).parent / "fixtures" / "review_answer_regression.json"


def load_corpus() -> list[dict[str, Any]]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def load_review_corpus() -> list[dict[str, Any]]:
    return json.loads(REVIEW_CORPUS_PATH.read_text(encoding="utf-8"))


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
        if self.case["category"] == "malformed":
            return interpretation
        return PlayerSentenceInterpretation(**interpretation)


class ReviewCorpusAIProvider(FakeAIProvider):
    def __init__(self, case: dict[str, Any]) -> None:
        super().__init__()
        self.case = case

    def evaluate_review_answer(self, request):
        self.review_evaluation_requests.append(request)
        evaluation = self.case.get("ai_review_evaluation")
        if evaluation is None:
            return super().evaluate_review_answer(request)
        if self.case["category"] == "malformed":
            return evaluation
        return ReviewAnswerEvaluation(**evaluation)


def test_learner_sentence_corpus_has_required_case_types() -> None:
    categories = {case["category"] for case in load_corpus()}

    assert {
        "accepted",
        "rejected",
        "low_confidence",
        "unknown_interpretation",
        "malformed",
    } <= categories


def test_learner_sentence_corpus_covers_polite_command_routes() -> None:
    polite_cases = {
        case["route"]
        for case in load_corpus()
        if case["sentence"].lower().startswith(("could you", "please"))
    }

    assert {"deterministic_parser", "ai_interpretation_fallback"} <= polite_cases


def test_learner_sentence_corpus_covers_desire_based_commands() -> None:
    desire_cases = [
        case
        for case in load_corpus()
        if case["sentence"].lower().startswith(("i would like to", "i need to"))
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] in {"deterministic_parser", "ai_interpretation_fallback"}
        and (
            "expected_room_id" in case
            or "expected_inventory_contains" in case
            or case.get("expected_state_unchanged") is not None
        )
        for case in desire_cases
    )


def test_learner_sentence_corpus_covers_permission_questions() -> None:
    permission_cases = [
        case
        for case in load_corpus()
        if case["sentence"].lower().startswith(("can i", "may i"))
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] in {"deterministic_parser", "ai_interpretation_fallback"}
        and (
            "expected_room_id" in case
            or "expected_inventory_contains" in case
            or case.get("expected_state_unchanged") is not None
        )
        for case in permission_cases
    )


def test_learner_sentence_corpus_covers_negative_request_no_mutation() -> None:
    negative_cases = [
        case
        for case in load_corpus()
        if any(
            marker in case["sentence"].lower()
            for marker in ("do not", "don't", "dont", "never")
        )
    ]

    assert any(
        case["category"] == "unknown_interpretation"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in negative_cases
    )


def test_learner_sentence_corpus_covers_indirect_polite_questions() -> None:
    indirect_polite_cases = [
        case
        for case in load_corpus()
        if case["sentence"].lower().startswith("would you mind")
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case.get("expected_inventory_contains") == "fungus sample"
        for case in indirect_polite_cases
    )


def test_learner_sentence_corpus_covers_hedged_intention_phrasing() -> None:
    hedged_cases = [
        case
        for case in load_corpus()
        if case["sentence"].lower().startswith("i think i should")
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] in {"deterministic_parser", "ai_interpretation_fallback"}
        and case["expected_success"] is True
        and "expected_room_id" in case
        for case in hedged_cases
    )


def test_learner_sentence_corpus_covers_pronoun_like_item_references() -> None:
    pronoun_cases = [
        case
        for case in load_corpus()
        if " it " in f" {case['sentence'].lower()} "
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case.get("expected_inventory_contains") == "fungus sample"
        for case in pronoun_cases
    )


def test_learner_sentence_corpus_covers_compound_action_requests() -> None:
    compound_cases = [
        case
        for case in load_corpus()
        if " and " in f" {case['sentence'].lower()} "
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is True
        and "expected_room_id" in case
        and "expected_inventory_not_contains" in case
        for case in compound_cases
    )


def test_learner_sentence_corpus_covers_self_correction_phrasing() -> None:
    self_correction_cases = [
        case
        for case in load_corpus()
        if "i mean" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case.get("expected_inventory_contains") == "fungus sample"
        for case in self_correction_cases
    )


def test_learner_sentence_corpus_covers_broad_location_requests() -> None:
    broad_location_cases = [
        case
        for case in load_corpus()
        if " to the lab" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "unknown_interpretation"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in broad_location_cases
    )


def test_learner_sentence_corpus_covers_ambiguous_enemy_references() -> None:
    ambiguous_enemy_cases = [
        case
        for case in load_corpus()
        if "the threat" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in ambiguous_enemy_cases
    )


def test_learner_sentence_corpus_covers_vague_combat_requests() -> None:
    vague_combat_cases = [
        case
        for case in load_corpus()
        if "fight it" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in vague_combat_cases
    )


def test_learner_sentence_corpus_covers_broad_tool_use_requests() -> None:
    broad_tool_cases = [
        case
        for case in load_corpus()
        if "the tool" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in broad_tool_cases
    )


def test_learner_sentence_corpus_covers_broad_conversation_requests() -> None:
    broad_conversation_cases = [
        case
        for case in load_corpus()
        if "talk to someone" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in broad_conversation_cases
    )


def test_learner_sentence_corpus_covers_broad_collection_requests() -> None:
    broad_collection_cases = [
        case
        for case in load_corpus()
        if "collect the thing" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in broad_collection_cases
    )


def test_learner_sentence_corpus_covers_broad_inspection_requests() -> None:
    broad_inspection_cases = [
        case
        for case in load_corpus()
        if "inspect everything" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        for case in broad_inspection_cases
    )


def test_learner_sentence_corpus_covers_vague_inventory_requests() -> None:
    vague_inventory_cases = [
        case
        for case in load_corpus()
        if "my stuff" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in vague_inventory_cases
    )


def test_learner_sentence_corpus_covers_broad_status_requests() -> None:
    broad_status_cases = [
        case
        for case in load_corpus()
        if "how i am doing" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in broad_status_cases
    )


def test_learner_sentence_corpus_covers_indirect_help_requests() -> None:
    indirect_help_cases = [
        case
        for case in load_corpus()
        if "what can i do now" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_help_cases
    )


def test_review_answer_corpus_has_required_case_types() -> None:
    categories = {case["category"] for case in load_review_corpus()}

    assert {"accepted", "rejected", "malformed"} <= categories


def test_review_answer_corpus_covers_synonym_heavy_incorrect_use() -> None:
    synonym_cases = [
        case
        for case in load_review_corpus()
        if "synonym" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in synonym_cases
    )


def test_review_answer_corpus_covers_definition_style_misuse() -> None:
    definition_cases = [
        case
        for case in load_review_corpus()
        if "means" in case["sentence"].lower()
        and "memorized" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in definition_cases
    )


def test_review_answer_corpus_covers_context_mismatch() -> None:
    context_mismatch_cases = [
        case
        for case in load_review_corpus()
        if "financial portfolio" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in context_mismatch_cases
    )


def test_review_answer_corpus_covers_vague_target_use() -> None:
    vague_cases = [
        case
        for case in load_review_corpus()
        if "many different ways" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in vague_cases
    )


def test_review_answer_corpus_covers_metaphorical_target_use() -> None:
    metaphorical_cases = [
        case
        for case in load_review_corpus()
        if "of doubt" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in metaphorical_cases
    )


def test_review_answer_corpus_covers_copied_example_reuse() -> None:
    copied_example_cases = [
        case
        for case in load_review_corpus()
        if "as you suggested" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in copied_example_cases
    )


def test_review_answer_corpus_covers_negated_target_word_use() -> None:
    negated_cases = [
        case
        for case in load_review_corpus()
        if "not clear" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in negated_cases
    )


def test_review_answer_corpus_covers_list_like_fragments() -> None:
    list_like_cases = [
        case
        for case in load_review_corpus()
        if "fungus," in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is False
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in list_like_cases
    )


def test_review_answer_corpus_covers_question_form_target_use() -> None:
    question_form_cases = [
        case
        for case in load_review_corpus()
        if case["sentence"].endswith("?")
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in question_form_cases
    )


def test_review_answer_corpus_covers_quoted_target_word_mention() -> None:
    quoted_cases = [
        case
        for case in load_review_corpus()
        if '"fungus"' in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in quoted_cases
    )


def test_review_answer_corpus_covers_hypothetical_target_word_use() -> None:
    hypothetical_cases = [
        case
        for case in load_review_corpus()
        if case["sentence"].lower().startswith("if i saw a fungus")
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in hypothetical_cases
    )


def test_review_answer_corpus_covers_overgeneralized_target_word_use() -> None:
    overgeneralized_cases = [
        case
        for case in load_review_corpus()
        if "any living thing" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in overgeneralized_cases
    )


def test_review_answer_corpus_covers_uncertainty_target_word_use() -> None:
    uncertainty_cases = [
        case
        for case in load_review_corpus()
        if "not sure" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in uncertainty_cases
    )


@pytest.mark.parametrize("case", load_corpus(), ids=lambda case: case["id"])
def test_learner_sentence_corpus_routes(case: dict[str, Any]) -> None:
    provider = CorpusAIProvider(case)
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    for command in case["setup_commands"]:
        assert engine.handle(command).success
    provider.interpretation_requests.clear()
    before_state = deepcopy(engine.state)

    parsed = parse_intent(case["sentence"])
    if "expected_exception" in case:
        with pytest.raises(AIProviderUnavailable, match=case["expected_exception"]):
            engine.handle(case["sentence"])
        assert engine.state == before_state
        assert parsed.action == "unknown"
        assert len(provider.interpretation_requests) == 1
        assert provider.interpretation_requests[0].player_sentence == case["sentence"]
        return

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
    if "expected_inventory_not_contains" in case:
        assert case["expected_inventory_not_contains"] not in engine.state.player.inventory
    if case.get("expected_state_unchanged") or case["category"] == "rejected":
        assert engine.state == before_state


@pytest.mark.parametrize("case", load_review_corpus(), ids=lambda case: case["id"])
def test_review_answer_corpus_routes(case: dict[str, Any]) -> None:
    provider = ReviewCorpusAIProvider(case)
    engine = GameEngine.new_game(build_biology_realm(), ai_provider=provider)
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")
    engine.handle("review")
    provider.review_evaluation_requests.clear()
    before_state = deepcopy(engine.state)

    if "expected_exception" in case:
        with pytest.raises(AIProviderUnavailable, match=case["expected_exception"]):
            engine.handle(case["sentence"])
        assert engine.state == before_state
    else:
        result = engine.handle(case["sentence"])
        assert result.success is case["expected_success"]
        assert case["expected_message_contains"] in result.message

    reached_ai = bool(provider.review_evaluation_requests)
    assert reached_ai is case["expected_ai_evaluation"]
    if reached_ai:
        assert provider.review_evaluation_requests[0].word == "fungus"
        assert (
            provider.review_evaluation_requests[0].learner_sentence
            == case["sentence"]
        )

    fungus = engine.state.vocabulary_mastery["fungus"]
    assert engine.state.active_review_word == case["expected_active_review_word"]
    assert fungus.review_stage == case["expected_review_stage"]
    assert engine.state.player.xp == case["expected_xp"]
