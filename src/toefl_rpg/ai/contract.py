from __future__ import annotations

from typing import Literal, Optional, Protocol

from pydantic import BaseModel, ConfigDict, Field


class AIProviderUnavailable(RuntimeError):
    """Raised when required player-facing AI is not configured."""


class TurnFeedbackRequest(BaseModel):
    player_sentence: str = Field(min_length=1)
    location_id: str = Field(min_length=1)
    deterministic_action: str = Field(min_length=1)
    deterministic_result: str = Field(min_length=1)
    target_words: list[str] = Field(default_factory=list)
    practiced_words: list[str] = Field(default_factory=list)


class TurnFeedback(BaseModel):
    narration: str = Field(min_length=1)
    sentence_feedback: str = Field(min_length=1)
    suggested_sentence: str = Field(min_length=1)
    vocabulary_notes: list[str] = Field(default_factory=list)


class VocabularyExplanationRequest(BaseModel):
    word: str = Field(min_length=1)
    theme: str = Field(min_length=1)
    learner_sentence: str = ""


class VocabularyExplanation(BaseModel):
    word: str = Field(min_length=1)
    plain_meaning: str = Field(min_length=1)
    example_sentence: str = Field(min_length=1)
    memory_hint: str = Field(min_length=1)


class ReviewAnswerEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    word: str = Field(min_length=1)
    learner_sentence: str = Field(min_length=1)
    theme: str = Field(min_length=1)
    review_stage: int = Field(ge=0)


class ReviewAnswerEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uses_target_meaningfully: bool
    explanation: str = Field(min_length=1)
    suggested_sentence: str = Field(min_length=1)


class ContentDraftRequest(BaseModel):
    theme: str = Field(min_length=1)
    required_words: list[str] = Field(min_length=1)
    purpose: str = Field(min_length=1)


class StructuredContentDraft(BaseModel):
    draft_type: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)


DeterministicAction = Literal[
    "move",
    "look",
    "inspect",
    "collect",
    "use",
    "talk",
    "attack",
    "review",
    "explain",
    "inventory",
    "status",
    "quit",
    "unknown",
]


class PlayerSentenceInterpretationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_sentence: str = Field(min_length=1)
    location_id: str = Field(min_length=1)
    room_name: str = Field(min_length=1)
    exits: dict[str, str] = Field(default_factory=dict)
    visible_items: list[str] = Field(default_factory=list)
    visible_npcs: list[str] = Field(default_factory=list)
    visible_enemies: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class PlayerSentenceInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: DeterministicAction
    target: str = ""
    confidence: float = Field(ge=0, le=1)
    reason: str = ""


class NPCDialogueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    npc_name: str = Field(min_length=1)
    location_id: str = Field(min_length=1)
    room_name: str = Field(min_length=1)
    quest_progress: str = Field(min_length=1)
    visible_items: list[str] = Field(default_factory=list)
    visible_npcs: list[str] = Field(default_factory=list)
    visible_enemies: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class NPCDialogue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker: str = Field(min_length=1)
    line: str = Field(min_length=1)
    vocabulary_notes: list[str] = Field(default_factory=list)


class RoomNarrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: str = Field(min_length=1)
    room_name: str = Field(min_length=1)
    room_description: str = Field(min_length=1)
    quest_progress: str = Field(min_length=1)
    exits: dict[str, str] = Field(default_factory=dict)
    visible_items: list[str] = Field(default_factory=list)
    visible_npcs: list[str] = Field(default_factory=list)
    visible_enemies: list[str] = Field(default_factory=list)
    target_words: list[str] = Field(default_factory=list)


class RoomNarration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    narration: str = Field(min_length=1)
    focus_hint: str = Field(min_length=1)
    vocabulary_notes: list[str] = Field(default_factory=list)


class AIProvider(Protocol):
    def generate_turn_feedback(self, request: TurnFeedbackRequest) -> TurnFeedback:
        raise NotImplementedError

    def interpret_player_sentence(
        self, request: PlayerSentenceInterpretationRequest
    ) -> PlayerSentenceInterpretation:
        raise NotImplementedError

    def generate_npc_dialogue(self, request: NPCDialogueRequest) -> NPCDialogue:
        raise NotImplementedError

    def generate_room_narration(self, request: RoomNarrationRequest) -> RoomNarration:
        raise NotImplementedError

    def explain_vocabulary(
        self, request: VocabularyExplanationRequest
    ) -> VocabularyExplanation:
        raise NotImplementedError

    def evaluate_review_answer(
        self, request: ReviewAnswerEvaluationRequest
    ) -> ReviewAnswerEvaluation:
        raise NotImplementedError

    def draft_content(self, request: ContentDraftRequest) -> StructuredContentDraft:
        raise NotImplementedError


def require_ai_provider(provider: Optional[AIProvider]) -> AIProvider:
    if provider is None:
        raise AIProviderUnavailable(
            "A configured AI provider is required for player-facing TOEFL RPG gameplay."
        )
    return provider


class FakeAIProvider:
    def __init__(self) -> None:
        self.turn_feedback_requests: list[TurnFeedbackRequest] = []
        self.interpretation_requests: list[PlayerSentenceInterpretationRequest] = []
        self.dialogue_requests: list[NPCDialogueRequest] = []
        self.room_narration_requests: list[RoomNarrationRequest] = []
        self.vocabulary_requests: list[VocabularyExplanationRequest] = []
        self.review_evaluation_requests: list[ReviewAnswerEvaluationRequest] = []
        self.content_requests: list[ContentDraftRequest] = []

    def generate_turn_feedback(self, request: TurnFeedbackRequest) -> TurnFeedback:
        self.turn_feedback_requests.append(request)
        practiced = ", ".join(request.practiced_words) or "no target word"
        return TurnFeedback(
            narration=f"AI narration for {request.deterministic_action}.",
            sentence_feedback="AI feedback: your sentence is understandable.",
            suggested_sentence=request.player_sentence,
            vocabulary_notes=[f"Practiced: {practiced}."],
        )

    def interpret_player_sentence(
        self, request: PlayerSentenceInterpretationRequest
    ) -> PlayerSentenceInterpretation:
        self.interpretation_requests.append(request)
        return PlayerSentenceInterpretation(
            action="unknown",
            target="",
            confidence=0,
            reason="Fake provider does not infer gameplay actions.",
        )

    def generate_npc_dialogue(self, request: NPCDialogueRequest) -> NPCDialogue:
        self.dialogue_requests.append(request)
        return NPCDialogue(
            speaker=request.npc_name,
            line=(
                "Start by collecting a fungus sample, then analyze it under "
                "the microscope and clear the invasive vine."
            ),
            vocabulary_notes=[
                "fungus: a growth that can affect an ecosystem.",
                "microscope: a tool for seeing tiny details.",
            ],
        )

    def generate_room_narration(self, request: RoomNarrationRequest) -> RoomNarration:
        self.room_narration_requests.append(request)
        return RoomNarration(
            narration=f"AI room narration for {request.room_name}.",
            focus_hint="Notice the visible entities before choosing your next action.",
            vocabulary_notes=[f"Target words: {', '.join(request.target_words)}."],
        )

    def explain_vocabulary(
        self, request: VocabularyExplanationRequest
    ) -> VocabularyExplanation:
        self.vocabulary_requests.append(request)
        return VocabularyExplanation(
            word=request.word,
            plain_meaning=f"{request.word} explained for {request.theme}.",
            example_sentence=f"The {request.theme} example uses {request.word}.",
            memory_hint=f"Connect {request.word} to {request.theme}.",
        )

    def evaluate_review_answer(
        self, request: ReviewAnswerEvaluationRequest
    ) -> ReviewAnswerEvaluation:
        self.review_evaluation_requests.append(request)
        uses_word = request.word.lower() in request.learner_sentence.lower()
        is_full_sentence = len(request.learner_sentence.split()) >= 4
        return ReviewAnswerEvaluation(
            uses_target_meaningfully=uses_word and is_full_sentence,
            explanation="Fake AI review evaluation checks sentence length and target word use.",
            suggested_sentence=request.learner_sentence,
        )

    def draft_content(self, request: ContentDraftRequest) -> StructuredContentDraft:
        self.content_requests.append(request)
        if request.purpose == "world_pack":
            first_word = request.required_words[0]
            return StructuredContentDraft(
                draft_type="world_pack",
                payload={
                    "schema_version": 1,
                    "world_id": "fake_biology_world",
                    "title": f"Fake {request.theme.title()} World",
                    "source_category": request.theme,
                    "difficulty": "A2",
                    "start_room_id": "start_room",
                    "core_words": list(request.required_words),
                    "items": ["field notebook"],
                    "npcs": ["Guide"],
                    "rooms": [
                        {
                            "id": "start_room",
                            "name": "Start Room",
                            "description": "A fake AI-authored room for tests.",
                            "exits": {},
                            "items": ["field notebook"],
                            "npcs": ["Guide"],
                            "enemies": [],
                            "target_words": [first_word],
                        }
                    ],
                    "enemies": [],
                    "quest_task_ids": [],
                    "quest_steps": [],
                },
            )
        return StructuredContentDraft(
            draft_type=request.purpose,
            payload={"theme": request.theme, "required_words": request.required_words},
        )
