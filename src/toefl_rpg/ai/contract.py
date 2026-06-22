from __future__ import annotations

from typing import Protocol, Optional

from pydantic import BaseModel, Field


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


class ContentDraftRequest(BaseModel):
    theme: str = Field(min_length=1)
    required_words: list[str] = Field(min_length=1)
    purpose: str = Field(min_length=1)


class StructuredContentDraft(BaseModel):
    draft_type: str = Field(min_length=1)
    payload: dict[str, object] = Field(default_factory=dict)


class AIProvider(Protocol):
    def generate_turn_feedback(self, request: TurnFeedbackRequest) -> TurnFeedback:
        raise NotImplementedError

    def explain_vocabulary(
        self, request: VocabularyExplanationRequest
    ) -> VocabularyExplanation:
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
        self.vocabulary_requests: list[VocabularyExplanationRequest] = []
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

    def draft_content(self, request: ContentDraftRequest) -> StructuredContentDraft:
        self.content_requests.append(request)
        return StructuredContentDraft(
            draft_type=request.purpose,
            payload={"theme": request.theme, "required_words": request.required_words},
        )
