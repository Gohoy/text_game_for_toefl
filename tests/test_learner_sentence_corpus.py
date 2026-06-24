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


def test_learner_sentence_corpus_covers_indirect_inventory_availability() -> None:
    indirect_inventory_cases = [
        case
        for case in load_corpus()
        if "what am i carrying" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_inventory_cases
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


def test_learner_sentence_corpus_covers_indirect_recap_requests() -> None:
    indirect_recap_cases = [
        case
        for case in load_corpus()
        if "summarize what happened" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "status"
        for case in indirect_recap_cases
    )


def test_learner_sentence_corpus_covers_indirect_status_comparisons() -> None:
    indirect_status_cases = [
        case
        for case in load_corpus()
        if "ready to continue" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_status_cases
    )


def test_learner_sentence_corpus_covers_indirect_route_confirmation() -> None:
    route_confirmation_cases = [
        case
        for case in load_corpus()
        if "right path" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "status"
        and "Quest: Biology Investigation 0/3" in case["expected_message_contains"]
        for case in route_confirmation_cases
    )


def test_learner_sentence_corpus_covers_indirect_readiness_checks() -> None:
    readiness_check_cases = [
        case
        for case in load_corpus()
        if "ready to fight" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "status"
        and case["expected_interpretation_visible_enemies"] == ["Invasive Vine"]
        for case in readiness_check_cases
    )


def test_learner_sentence_corpus_covers_indirect_quest_progress() -> None:
    indirect_quest_progress_cases = [
        case
        for case in load_corpus()
        if "investigation remains" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_quest_progress_cases
    )


def test_learner_sentence_corpus_covers_indirect_goal_reminders() -> None:
    indirect_goal_reminder_cases = [
        case
        for case in load_corpus()
        if "accomplish next" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_goal_reminder_cases
    )


def test_learner_sentence_corpus_covers_indirect_objective_priority() -> None:
    objective_priority_cases = [
        case
        for case in load_corpus()
        if "task is most urgent" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "status"
        for case in objective_priority_cases
    )


def test_learner_sentence_corpus_covers_indirect_enemy_warnings() -> None:
    indirect_enemy_warning_cases = [
        case
        for case in load_corpus()
        if "danger is nearby" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["expected_interpretation_visible_enemies"] == ["Invasive Vine"]
        for case in indirect_enemy_warning_cases
    )


def test_learner_sentence_corpus_covers_indirect_strategy_advice() -> None:
    indirect_strategy_advice_cases = [
        case
        for case in load_corpus()
        if "deal with the vine" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["expected_interpretation_visible_enemies"] == ["Invasive Vine"]
        for case in indirect_strategy_advice_cases
    )


def test_learner_sentence_corpus_covers_indirect_safety_checks() -> None:
    indirect_safety_check_cases = [
        case
        for case in load_corpus()
        if "safe to move on" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "look"
        and case["expected_interpretation_visible_enemies"] == ["Invasive Vine"]
        for case in indirect_safety_check_cases
    )


def test_learner_sentence_corpus_covers_indirect_retreat_advice() -> None:
    indirect_retreat_cases = [
        case
        for case in load_corpus()
        if "retreat from here" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "look"
        and case["expected_interpretation_visible_enemies"] == ["Invasive Vine"]
        for case in indirect_retreat_cases
    )


def test_learner_sentence_corpus_covers_indirect_rest_requests() -> None:
    indirect_rest_cases = [
        case
        for case in load_corpus()
        if "rest here" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "status"
        for case in indirect_rest_cases
    )


def test_learner_sentence_corpus_covers_indirect_save_exit_intent() -> None:
    indirect_save_exit_cases = [
        case
        for case in load_corpus()
        if "done for now" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_should_quit"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_save_exit_cases
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


def test_learner_sentence_corpus_covers_indirect_hint_requests() -> None:
    indirect_hint_cases = [
        case
        for case in load_corpus()
        if "give me a hint" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "help"
        for case in indirect_hint_cases
    )


def test_learner_sentence_corpus_covers_indirect_prerequisite_reminders() -> None:
    prerequisite_cases = [
        case
        for case in load_corpus()
        if "before using the microscope" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in prerequisite_cases
    )


def test_learner_sentence_corpus_covers_indirect_review_requests() -> None:
    indirect_review_cases = [
        case
        for case in load_corpus()
        if "quiz me on words" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_review_cases
    )


def test_learner_sentence_corpus_covers_indirect_review_readiness() -> None:
    review_readiness_cases = [
        case
        for case in load_corpus()
        if "ready for a review" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "review"
        and "No vocabulary is due for review yet." in case["expected_message_contains"]
        for case in review_readiness_cases
    )


def test_learner_sentence_corpus_covers_indirect_explanation_requests() -> None:
    indirect_explanation_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_explanation_request_ai_fallback_visible_word"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == []
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "organism"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_explanation_cases
    )


def test_learner_sentence_corpus_covers_polite_definition_requests() -> None:
    polite_definition_cases = [
        case
        for case in load_corpus()
        if "define organism" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["expected_parser"]["action"] == "explain"
        for case in polite_definition_cases
    )


def test_learner_sentence_corpus_covers_start_room_visible_organism_definition() -> None:
    organism_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "polite_define_visible_word_deterministic"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == []
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "organism"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in organism_definition_cases
    )


def test_learner_sentence_corpus_covers_start_room_visible_species_definition() -> None:
    species_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "start_room_species_visible_definition"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == []
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "species"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in species_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_start_room_visible_species_definition() -> None:
    indirect_species_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_start_room_species_visible_definition"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == []
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "species"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_species_definition_cases
    )


def test_learner_sentence_corpus_covers_start_room_visible_evolve_definition() -> None:
    evolve_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "start_room_evolve_visible_definition"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == []
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "evolve"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in evolve_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_start_room_visible_evolve_definition() -> None:
    indirect_evolve_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_start_room_evolve_visible_definition"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == []
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "evolve"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_evolve_definition_cases
    )


def test_learner_sentence_corpus_covers_unavailable_definition_requests() -> None:
    unavailable_definition_cases = [
        case
        for case in load_corpus()
        if "define vaccine" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in unavailable_definition_cases
    )


def test_learner_sentence_corpus_covers_unknown_definition_requests() -> None:
    unknown_definition_cases = [
        case
        for case in load_corpus()
        if "define astronomy" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["expected_success"] is False
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in unknown_definition_cases
    )


def test_learner_sentence_corpus_covers_encountered_only_definition_away_from_source_room() -> None:
    encountered_only_definition_cases = [
        case
        for case in load_corpus()
        if "define microscope" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go east", "go west"]
        and case["expected_success"] is False
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in encountered_only_definition_cases
    )


def test_learner_sentence_corpus_covers_start_room_encountered_only_organism_definition_after_movement() -> None:
    target_case_id = "start_room_encountered_only_organism_definition_after_movement_rejected"
    start_room_encountered_only_cases = [
        case
        for case in load_corpus()
        if case["id"] == target_case_id
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go north"]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "organism"
        and case["expected_success"] is False
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in start_room_encountered_only_cases
    )


def test_learner_sentence_corpus_covers_indirect_start_room_encountered_only_organism_definition_after_movement() -> None:
    target_case_id = (
        "indirect_start_room_encountered_only_organism_definition_after_movement_rejected"
    )
    indirect_start_room_encountered_only_cases = [
        case
        for case in load_corpus()
        if case["id"] == target_case_id
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == ["go north"]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "organism"
        and case["expected_success"] is False
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in indirect_start_room_encountered_only_cases
    )


def test_learner_sentence_corpus_covers_start_room_encountered_only_species_definition_after_movement() -> None:
    target_case_id = "start_room_encountered_only_species_definition_after_movement_rejected"
    start_room_encountered_only_cases = [
        case
        for case in load_corpus()
        if case["id"] == target_case_id
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go north"]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "species"
        and case["expected_success"] is False
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in start_room_encountered_only_cases
    )


def test_learner_sentence_corpus_covers_start_room_encountered_only_evolve_definition_after_movement() -> None:
    target_case_id = "start_room_encountered_only_evolve_definition_after_movement_rejected"
    start_room_encountered_only_cases = [
        case
        for case in load_corpus()
        if case["id"] == target_case_id
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go north"]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "evolve"
        and case["expected_success"] is False
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in start_room_encountered_only_cases
    )


def test_learner_sentence_corpus_covers_indirect_start_room_encountered_only_species_definition_after_movement() -> None:
    target_case_id = (
        "indirect_start_room_encountered_only_species_definition_after_movement_rejected"
    )
    indirect_start_room_encountered_only_cases = [
        case
        for case in load_corpus()
        if case["id"] == target_case_id
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == ["go north"]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "species"
        and case["expected_success"] is False
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in indirect_start_room_encountered_only_cases
    )


def test_learner_sentence_corpus_covers_item_room_visible_definition_before_item_use() -> None:
    item_room_visible_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "item_room_visible_definition_before_item_use"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go east"]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "microscope"
        and case["expected_success"] is True
        and case["expected_room_id"] == "microscope_tent"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in item_room_visible_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_item_room_visible_definition_before_item_use() -> None:
    indirect_item_room_visible_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_item_room_visible_definition_before_item_use_ai_fallback"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == ["go east"]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "microscope"
        and case["expected_success"] is True
        and case["expected_room_id"] == "microscope_tent"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_item_room_visible_definition_cases
    )


def test_learner_sentence_corpus_covers_item_practiced_definition_away_from_source_room() -> None:
    item_practiced_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "item_practiced_definition_away_from_source_room"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == [
            "go north",
            "collect fungus sample",
            "go south",
            "go east",
            "use microscope",
            "go west",
        ]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in item_practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_item_practiced_definition_away_from_source_room() -> None:
    indirect_item_practiced_definition_cases = [
        case
        for case in load_corpus()
        if "remind me what microscope means" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == [
            "go north",
            "collect fungus sample",
            "go south",
            "go east",
            "use microscope",
            "go west",
        ]
        and case["ai_interpretation"]["action"] == "explain"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_item_practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_source_room_visible_fungus_definition_before_collection() -> None:
    source_room_visible_fungus_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "source_room_visible_fungus_definition_before_collection"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == ["go north"]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "fungus"
        and case["expected_success"] is True
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in source_room_visible_fungus_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_source_room_visible_fungus_definition_before_collection() -> None:
    indirect_source_room_visible_fungus_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_source_room_visible_fungus_definition_before_collection_ai_fallback"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == ["go north"]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "fungus"
        and case["expected_success"] is True
        and case["expected_room_id"] == "fungus_grove"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_source_room_visible_fungus_definition_cases
    )


def test_learner_sentence_corpus_covers_combat_practiced_definition_away_from_source_room() -> None:
    combat_practiced_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "combat_practiced_definition_away_from_source_room"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == [
            "go north",
            "go north",
            "I attack the invasive vine",
            "I attack the invasive vine",
            "I attack the invasive vine",
            "go south",
            "go south",
        ]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "mimicry"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in combat_practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_combat_practiced_definition_away_from_source_room() -> None:
    indirect_combat_practiced_definition_cases = [
        case
        for case in load_corpus()
        if "remind me what mimicry means" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == [
            "go north",
            "go north",
            "I attack the invasive vine",
            "I attack the invasive vine",
            "I attack the invasive vine",
            "go south",
            "go south",
        ]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "mimicry"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_combat_practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_combat_room_encountered_only_definition_rejection() -> None:
    combat_room_encountered_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "combat_room_encountered_only_definition_away_from_source_room_rejected"
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == [
            "go north",
            "go north",
            "go south",
            "go south",
        ]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "mimicry"
        and case["expected_success"] is False
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in combat_room_encountered_definition_cases
    )


def test_learner_sentence_corpus_covers_combat_room_visible_definition_before_combat() -> None:
    combat_room_visible_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "combat_room_visible_definition_before_combat"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == [
            "go north",
            "go north",
        ]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_parser"]["target"] == "mimicry"
        and case["expected_success"] is True
        and case["expected_room_id"] == "mimicry_trail"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in combat_room_visible_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_combat_room_visible_definition_before_combat() -> None:
    indirect_combat_room_visible_definition_cases = [
        case
        for case in load_corpus()
        if case["id"] == "indirect_combat_room_visible_definition_before_combat_ai_fallback"
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == [
            "go north",
            "go north",
        ]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "mimicry"
        and case["expected_success"] is True
        and case["expected_room_id"] == "mimicry_trail"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_combat_room_visible_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_combat_room_encountered_only_definition_rejection() -> None:
    indirect_combat_room_encountered_definition_cases = [
        case
        for case in load_corpus()
        if "remind me what mimicry means before i fight" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == [
            "go north",
            "go north",
            "go south",
            "go south",
        ]
        and case["ai_interpretation"]["action"] == "explain"
        and case["ai_interpretation"]["target"] == "mimicry"
        and case["expected_success"] is False
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 0
        for case in indirect_combat_room_encountered_definition_cases
    )


def test_learner_sentence_corpus_covers_practiced_definition_away_from_source_room() -> None:
    practiced_definition_cases = [
        case
        for case in load_corpus()
        if "define fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "deterministic_parser"
        and case["setup_commands"] == [
            "go north",
            "The fungus is vital for the old forest.",
            "go south",
        ]
        and case["expected_parser"]["action"] == "explain"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_practiced_definition_away_from_source_room() -> None:
    indirect_practiced_definition_cases = [
        case
        for case in load_corpus()
        if "remind me what fungus means" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["setup_commands"] == [
            "go north",
            "collect fungus sample",
            "go south",
        ]
        and case["ai_interpretation"]["action"] == "explain"
        and case["expected_success"] is True
        and case["expected_room_id"] == "research_camp"
        and case["expected_state_unchanged"] is True
        and case["expected_vocabulary_request_count"] == 1
        for case in indirect_practiced_definition_cases
    )


def test_learner_sentence_corpus_covers_indirect_look_requests() -> None:
    indirect_look_cases = [
        case
        for case in load_corpus()
        if "what is around me" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_look_cases
    )


def test_learner_sentence_corpus_covers_indirect_map_or_exits_requests() -> None:
    map_or_exits_cases = [
        case
        for case in load_corpus()
        if "paths can i take" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["expected_interpretation_exits"] == {
            "east": "microscope_tent",
            "north": "fungus_grove",
        }
        for case in map_or_exits_cases
    )


def test_learner_sentence_corpus_covers_indirect_route_planning() -> None:
    route_planning_cases = [
        case
        for case in load_corpus()
        if "reach the microscope tent" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "look"
        and case["expected_interpretation_exits"] == {
            "east": "microscope_tent",
            "north": "fungus_grove",
        }
        for case in route_planning_cases
    )


def test_learner_sentence_corpus_covers_indirect_backtracking() -> None:
    backtracking_cases = [
        case for case in load_corpus() if "get back to camp" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "look"
        and case["expected_interpretation_exits"] == {
            "south": "research_camp",
            "north": "mimicry_trail",
        }
        for case in backtracking_cases
    )


def test_learner_sentence_corpus_covers_indirect_detour_requests() -> None:
    detour_cases = [
        case
        for case in load_corpus()
        if "another way around" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "look"
        and case["expected_interpretation_exits"] == {
            "south": "research_camp",
            "north": "mimicry_trail",
        }
        for case in detour_cases
    )


def test_learner_sentence_corpus_covers_indirect_repeat_room_narration() -> None:
    repeat_room_cases = [
        case
        for case in load_corpus()
        if "where i am" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and "AI room narration for Fungus Grove." in case["expected_message_contains"]
        for case in repeat_room_cases
    )


def test_learner_sentence_corpus_covers_indirect_npc_dialogue_requests() -> None:
    indirect_dialogue_cases = [
        case
        for case in load_corpus()
        if "ask the scientist for advice" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in indirect_dialogue_cases
    )


def test_learner_sentence_corpus_covers_indirect_vocabulary_reminders() -> None:
    vocabulary_reminder_cases = [
        case
        for case in load_corpus()
        if "word should i practice" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        for case in vocabulary_reminder_cases
    )


def test_learner_sentence_corpus_covers_indirect_next_word_requests() -> None:
    next_word_cases = [
        case
        for case in load_corpus()
        if "vocabulary word comes next" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "accepted"
        and case["route"] == "ai_interpretation_fallback"
        and case["expected_success"] is True
        and case["expected_state_unchanged"] is True
        and case["ai_interpretation"]["action"] == "help"
        for case in next_word_cases
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


def test_review_answer_corpus_covers_cause_effect_free_target_use() -> None:
    cause_effect_free_cases = [
        case
        for case in load_review_corpus()
        if "exists in the forest today" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in cause_effect_free_cases
    )


def test_review_answer_corpus_covers_location_only_target_use() -> None:
    location_only_cases = [
        case
        for case in load_review_corpus()
        if "near the old research tent" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in location_only_cases
    )


def test_review_answer_corpus_covers_relation_only_target_use() -> None:
    relation_only_cases = [
        case
        for case in load_review_corpus()
        if "associated with biology" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in relation_only_cases
    )


def test_review_answer_corpus_covers_category_label_target_use() -> None:
    category_label_cases = [
        case
        for case in load_review_corpus()
        if "vocabulary category" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in category_label_cases
    )


def test_review_answer_corpus_covers_answer_label_target_use() -> None:
    answer_label_cases = [
        case
        for case in load_review_corpus()
        if "correct answer" in case["sentence"].lower()
        and "review word" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in answer_label_cases
    )


def test_review_answer_corpus_covers_translation_only_target_use() -> None:
    translation_only_cases = [
        case
        for case in load_review_corpus()
        if "translate fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in translation_only_cases
    )


def test_review_answer_corpus_covers_spelling_only_target_use() -> None:
    spelling_only_cases = [
        case
        for case in load_review_corpus()
        if "spell fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in spelling_only_cases
    )


def test_review_answer_corpus_covers_pronunciation_only_target_use() -> None:
    pronunciation_only_cases = [
        case
        for case in load_review_corpus()
        if "pronounce fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in pronunciation_only_cases
    )


def test_review_answer_corpus_covers_morphology_only_target_use() -> None:
    morphology_only_cases = [
        case
        for case in load_review_corpus()
        if "singular noun form" in case["sentence"].lower()
        and "suffix" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in morphology_only_cases
    )


def test_review_answer_corpus_covers_frequency_only_target_use() -> None:
    frequency_only_cases = [
        case
        for case in load_review_corpus()
        if "common word" in case["sentence"].lower()
        and "toefl biology passages" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in frequency_only_cases
    )


def test_review_answer_corpus_covers_visual_form_only_target_use() -> None:
    visual_form_only_cases = [
        case
        for case in load_review_corpus()
        if "looks short" in case["sentence"].lower()
        and "on the page" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in visual_form_only_cases
    )


def test_review_answer_corpus_covers_difficulty_only_target_use() -> None:
    difficulty_only_cases = [
        case
        for case in load_review_corpus()
        if "difficult for me to remember" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in difficulty_only_cases
    )


def test_review_answer_corpus_covers_memorization_method_only_target_use() -> None:
    memorization_method_cases = [
        case
        for case in load_review_corpus()
        if "remember fungus by" in case["sentence"].lower()
        and "flashcard" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in memorization_method_cases
    )


def test_review_answer_corpus_covers_etymology_only_target_use() -> None:
    etymology_only_cases = [
        case
        for case in load_review_corpus()
        if "origin of fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in etymology_only_cases
    )


def test_review_answer_corpus_covers_source_only_target_use() -> None:
    source_only_cases = [
        case
        for case in load_review_corpus()
        if "learned fungus from" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in source_only_cases
    )


def test_review_answer_corpus_covers_confidence_only_target_use() -> None:
    confidence_only_cases = [
        case
        for case in load_review_corpus()
        if "feel confident about fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in confidence_only_cases
    )


def test_review_answer_corpus_covers_comparison_only_target_use() -> None:
    comparison_only_cases = [
        case
        for case in load_review_corpus()
        if "different from bacteria" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in comparison_only_cases
    )


def test_review_answer_corpus_covers_test_strategy_only_target_use() -> None:
    test_strategy_only_cases = [
        case
        for case in load_review_corpus()
        if "eliminate wrong toefl answer choices" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in test_strategy_only_cases
    )


def test_review_answer_corpus_covers_score_goal_only_target_use() -> None:
    score_goal_only_cases = [
        case
        for case in load_review_corpus()
        if "higher toefl score" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in score_goal_only_cases
    )


def test_review_answer_corpus_covers_exam_context_only_target_use() -> None:
    exam_context_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl exam question" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in exam_context_only_cases
    )


def test_review_answer_corpus_covers_passage_prediction_only_target_use() -> None:
    passage_prediction_only_cases = [
        case
        for case in load_review_corpus()
        if "future toefl biology passages" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in passage_prediction_only_cases
    )


def test_review_answer_corpus_covers_reading_skill_only_target_use() -> None:
    reading_skill_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl reading skill" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in reading_skill_only_cases
    )


def test_review_answer_corpus_covers_dictionary_skill_only_target_use() -> None:
    dictionary_skill_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl dictionary" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in dictionary_skill_only_cases
    )


def test_review_answer_corpus_covers_note_taking_only_target_use() -> None:
    note_taking_only_cases = [
        case
        for case in load_review_corpus()
        if "wrote fungus" in case["sentence"].lower()
        and "biology notes" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in note_taking_only_cases
    )


def test_review_answer_corpus_covers_study_list_only_target_use() -> None:
    study_list_only_cases = [
        case
        for case in load_review_corpus()
        if "study-list entry" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in study_list_only_cases
    )


def test_review_answer_corpus_covers_flashcard_deck_only_target_use() -> None:
    flashcard_deck_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl flashcard deck" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in flashcard_deck_only_cases
    )


def test_review_answer_corpus_covers_quiz_prep_only_target_use() -> None:
    quiz_prep_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl quiz preparation" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in quiz_prep_only_cases
    )


def test_review_answer_corpus_covers_practice_schedule_only_target_use() -> None:
    practice_schedule_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl practice schedule" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in practice_schedule_only_cases
    )


def test_review_answer_corpus_covers_word_bank_only_target_use() -> None:
    word_bank_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl word bank" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in word_bank_only_cases
    )


def test_review_answer_corpus_covers_glossary_only_target_use() -> None:
    glossary_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl glossary" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in glossary_only_cases
    )


def test_review_answer_corpus_covers_synonym_list_only_target_use() -> None:
    synonym_list_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl synonym list" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in synonym_list_only_cases
    )


def test_review_answer_corpus_covers_mnemonic_only_target_use() -> None:
    mnemonic_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl mnemonic" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in mnemonic_only_cases
    )


def test_review_answer_corpus_covers_spelling_bee_only_target_use() -> None:
    spelling_bee_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl spelling bee" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in spelling_bee_only_cases
    )


def test_review_answer_corpus_covers_crossword_only_target_use() -> None:
    crossword_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl crossword" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in crossword_only_cases
    )


def test_review_answer_corpus_covers_word_search_only_target_use() -> None:
    word_search_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl word search" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in word_search_only_cases
    )


def test_review_answer_corpus_covers_hangman_only_target_use() -> None:
    hangman_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl hangman game" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in hangman_only_cases
    )


def test_review_answer_corpus_covers_vocabulary_game_only_target_use() -> None:
    vocabulary_game_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl vocabulary game" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in vocabulary_game_only_cases
    )


def test_review_answer_corpus_covers_word_puzzle_only_target_use() -> None:
    word_puzzle_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl word puzzle" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in word_puzzle_only_cases
    )


def test_review_answer_corpus_covers_vocabulary_app_only_target_use() -> None:
    vocabulary_app_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl vocabulary app" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in vocabulary_app_only_cases
    )


def test_review_answer_corpus_covers_study_app_only_target_use() -> None:
    study_app_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl study-app" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in study_app_only_cases
    )


def test_review_answer_corpus_covers_language_app_only_target_use() -> None:
    language_app_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl language app" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in language_app_only_cases
    )


def test_review_answer_corpus_covers_learning_platform_only_target_use() -> None:
    learning_platform_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl learning platform" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in learning_platform_only_cases
    )


def test_review_answer_corpus_covers_e_learning_only_target_use() -> None:
    e_learning_only_cases = [
        case
        for case in load_review_corpus()
        if "toefl e-learning tool" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in e_learning_only_cases
    )


def test_review_answer_corpus_covers_unsupported_certainty_claims() -> None:
    unsupported_certainty_cases = [
        case
        for case in load_review_corpus()
        if "definitely understand fungus" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in unsupported_certainty_cases
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


def test_review_answer_corpus_covers_analogy_only_target_word_use() -> None:
    analogy_cases = [
        case
        for case in load_review_corpus()
        if "like a hidden city" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in analogy_cases
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


def test_review_answer_corpus_covers_tautological_target_word_use() -> None:
    tautological_cases = [
        case
        for case in load_review_corpus()
        if "is a fungus because" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in tautological_cases
    )


def test_review_answer_corpus_covers_shallow_example_label_target_word_use() -> None:
    example_label_cases = [
        case
        for case in load_review_corpus()
        if "example of a biology thing" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in example_label_cases
    )


def test_review_answer_corpus_covers_personal_preference_target_word_use() -> None:
    personal_preference_cases = [
        case
        for case in load_review_corpus()
        if "like fungus because" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in personal_preference_cases
    )


def test_review_answer_corpus_covers_emotional_reaction_target_word_use() -> None:
    emotional_reaction_cases = [
        case
        for case in load_review_corpus()
        if "feel amazed" in case["sentence"].lower()
    ]

    assert any(
        case["category"] == "rejected"
        and case["expected_ai_evaluation"] is True
        and case["expected_active_review_word"] == "fungus"
        and case["expected_xp"] == 16
        for case in emotional_reaction_cases
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
    if "expected_should_quit" in case:
        assert result.should_quit is case["expected_should_quit"]
    if "expected_vocabulary_request_count" in case:
        assert len(provider.vocabulary_requests) == case[
            "expected_vocabulary_request_count"
        ]

    if case["route"] == "deterministic_parser":
        assert parsed.action == case["expected_parser"]["action"]
        assert parsed.target == case["expected_parser"]["target"]
        assert provider.interpretation_requests == []
    else:
        assert parsed.action == "unknown"
        assert len(provider.interpretation_requests) == 1
        assert provider.interpretation_requests[0].player_sentence == case["sentence"]
        if "expected_interpretation_visible_enemies" in case:
            assert provider.interpretation_requests[0].visible_enemies == case[
                "expected_interpretation_visible_enemies"
            ]
        if "expected_interpretation_exits" in case:
            assert provider.interpretation_requests[0].exits == case[
                "expected_interpretation_exits"
            ]

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
