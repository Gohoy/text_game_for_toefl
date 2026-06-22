import pytest

from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import FakeAIProvider
from toefl_rpg.ai.contract import StructuredContentDraft
from toefl_rpg.ai.drafts import ContentDraftValidationError
from toefl_rpg.ai.drafts import draft_world_pack
from toefl_rpg.ai.drafts import validate_world_pack_draft
from toefl_rpg.content.schema import WorldPack
from tests.test_world_schema import minimal_world_pack_data


def test_validate_world_pack_draft_returns_typed_world_pack() -> None:
    draft = StructuredContentDraft(
        draft_type="world_pack",
        payload=minimal_world_pack_data(),
    )

    pack = validate_world_pack_draft(draft)

    assert isinstance(pack, WorldPack)
    assert pack.world_id == "test_world"


def test_validate_world_pack_draft_rejects_wrong_draft_type() -> None:
    draft = StructuredContentDraft(
        draft_type="room_draft",
        payload=minimal_world_pack_data(),
    )

    with pytest.raises(ContentDraftValidationError, match="Unsupported AI draft type"):
        validate_world_pack_draft(draft)


def test_validate_world_pack_draft_rejects_invalid_references() -> None:
    payload = minimal_world_pack_data()
    payload["rooms"][0]["exits"]["east"] = "missing_room"
    draft = StructuredContentDraft(draft_type="world_pack", payload=payload)

    with pytest.raises(ContentDraftValidationError, match="missing_room"):
        validate_world_pack_draft(draft)


def test_draft_world_pack_uses_fake_provider_and_validates_schema() -> None:
    provider = FakeAIProvider()
    request = ContentDraftRequest(
        theme="biology",
        required_words=["organism"],
        purpose="world_pack",
    )

    pack = draft_world_pack(provider, request)

    assert pack.world_id == "fake_biology_world"
    assert pack.core_words == ["organism"]
    assert provider.content_requests == [request]


def test_draft_world_pack_rejects_malformed_provider_payload() -> None:
    class MalformedDraftProvider(FakeAIProvider):
        def draft_content(self, request):
            self.content_requests.append(request)
            return StructuredContentDraft(
                draft_type="world_pack",
                payload={
                    "schema_version": 1,
                    "world_id": "malformed_world",
                    "title": "Malformed World",
                },
            )

    provider = MalformedDraftProvider()
    request = ContentDraftRequest(
        theme="biology",
        required_words=["organism"],
        purpose="world_pack",
    )

    with pytest.raises(ContentDraftValidationError, match="Invalid AI world_pack draft"):
        draft_world_pack(provider, request)

    assert provider.content_requests == [request]


def test_draft_world_pack_requires_world_pack_purpose() -> None:
    provider = FakeAIProvider()
    request = ContentDraftRequest(
        theme="biology",
        required_words=["organism"],
        purpose="room_draft",
    )

    with pytest.raises(ContentDraftValidationError, match="purpose 'world_pack'"):
        draft_world_pack(provider, request)
