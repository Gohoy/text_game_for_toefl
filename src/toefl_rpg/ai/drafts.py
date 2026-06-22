from __future__ import annotations

from pydantic import ValidationError

from toefl_rpg.ai.contract import AIProvider
from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import StructuredContentDraft
from toefl_rpg.ai.contract import require_ai_provider
from toefl_rpg.content.schema import WorldPack


class ContentDraftValidationError(RuntimeError):
    """Raised when an AI-authored content draft cannot enter typed content."""


def validate_world_pack_draft(draft: StructuredContentDraft) -> WorldPack:
    if draft.draft_type != "world_pack":
        raise ContentDraftValidationError(
            f"Unsupported AI draft type for world-pack validation: {draft.draft_type}"
        )

    try:
        return WorldPack.model_validate(draft.payload)
    except ValidationError as exc:
        raise ContentDraftValidationError(f"Invalid AI world_pack draft: {exc}") from exc


def draft_world_pack(provider: AIProvider, request: ContentDraftRequest) -> WorldPack:
    if request.purpose != "world_pack":
        raise ContentDraftValidationError(
            "World-pack draft validation requires request purpose 'world_pack'."
        )

    try:
        draft = StructuredContentDraft.model_validate(
            require_ai_provider(provider).draft_content(request)
        )
    except ValidationError as exc:
        raise ContentDraftValidationError(f"Invalid AI content draft: {exc}") from exc
    return validate_world_pack_draft(draft)
