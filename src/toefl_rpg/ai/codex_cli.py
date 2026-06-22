from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import ContentDraftRequest
from toefl_rpg.ai.contract import NPCDialogue
from toefl_rpg.ai.contract import NPCDialogueRequest
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.ai.contract import PlayerSentenceInterpretationRequest
from toefl_rpg.ai.contract import ReviewAnswerEvaluation
from toefl_rpg.ai.contract import ReviewAnswerEvaluationRequest
from toefl_rpg.ai.contract import RoomNarration
from toefl_rpg.ai.contract import RoomNarrationRequest
from toefl_rpg.ai.contract import StructuredContentDraft
from toefl_rpg.ai.contract import TurnFeedback
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanation
from toefl_rpg.ai.contract import VocabularyExplanationRequest


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
Runner = Callable[..., subprocess.CompletedProcess[str]]


class CodexCliProviderError(RuntimeError):
    """Raised when Codex CLI returns unusable structured output."""


class CodexCliProvider:
    def __init__(
        self,
        executable: str = "codex",
        timeout_seconds: int = 180,
        cwd: Optional[Path] = None,
        runner: Runner = subprocess.run,
    ) -> None:
        self.executable = executable
        self.timeout_seconds = timeout_seconds
        self.cwd = cwd
        self._runner = runner

    def generate_turn_feedback(self, request: TurnFeedbackRequest) -> TurnFeedback:
        return self._invoke(
            response_model=TurnFeedback,
            purpose="turn feedback",
            payload=request.model_dump(),
        )

    def interpret_player_sentence(
        self, request: PlayerSentenceInterpretationRequest
    ) -> PlayerSentenceInterpretation:
        return self._invoke(
            response_model=PlayerSentenceInterpretation,
            purpose="structured player sentence interpretation",
            payload=request.model_dump(),
        )

    def generate_npc_dialogue(self, request: NPCDialogueRequest) -> NPCDialogue:
        return self._invoke(
            response_model=NPCDialogue,
            purpose="NPC dialogue",
            payload=request.model_dump(),
        )

    def generate_room_narration(self, request: RoomNarrationRequest) -> RoomNarration:
        return self._invoke(
            response_model=RoomNarration,
            purpose="room narration",
            payload=request.model_dump(),
        )

    def explain_vocabulary(
        self, request: VocabularyExplanationRequest
    ) -> VocabularyExplanation:
        return self._invoke(
            response_model=VocabularyExplanation,
            purpose="vocabulary explanation",
            payload=request.model_dump(),
        )

    def evaluate_review_answer(
        self, request: ReviewAnswerEvaluationRequest
    ) -> ReviewAnswerEvaluation:
        return self._invoke(
            response_model=ReviewAnswerEvaluation,
            purpose="review answer evaluation",
            payload=request.model_dump(),
        )

    def draft_content(self, request: ContentDraftRequest) -> StructuredContentDraft:
        return self._invoke(
            response_model=StructuredContentDraft,
            purpose="structured content draft",
            payload=request.model_dump(),
        )

    def _invoke(
        self,
        response_model: Type[ResponseModel],
        purpose: str,
        payload: dict[str, object],
    ) -> ResponseModel:
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / "response_schema.json"
            output_path = Path(temp_dir) / "last_message.json"
            schema_path.write_text(
                json.dumps(self._build_response_schema(response_model)),
                encoding="utf-8",
            )

            command = self._build_command(schema_path, output_path)
            prompt = self._build_prompt(purpose, payload)
            try:
                result = self._runner(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=self.timeout_seconds,
                    cwd=str(self.cwd) if self.cwd is not None else None,
                    check=False,
                )
            except FileNotFoundError as exc:
                raise AIProviderUnavailable(
                    f"Required Codex CLI executable not found: {self.executable}"
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise CodexCliProviderError(
                    f"Codex CLI timed out after {self.timeout_seconds} seconds."
                ) from exc

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                raise CodexCliProviderError(
                    f"Codex CLI failed with exit code {result.returncode}: {stderr}"
                )

            raw_output = self._read_output(output_path, result.stdout)
            try:
                return response_model.model_validate_json(raw_output)
            except ValidationError as exc:
                raise CodexCliProviderError("Codex CLI returned invalid structured output.") from exc

    def _build_command(self, schema_path: Path, output_path: Path) -> list[str]:
        return [
            self.executable,
            "exec",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "-",
        ]

    def _build_response_schema(
        self,
        response_model: Type[ResponseModel],
    ) -> dict[str, object]:
        schema = response_model.model_json_schema()
        properties = schema.get("properties")
        if isinstance(properties, dict):
            schema["additionalProperties"] = False
            schema["required"] = list(properties)
        return schema

    def _build_prompt(self, purpose: str, payload: dict[str, object]) -> str:
        return (
            "You are the required AI agent for a TOEFL text RPG.\n"
            "Return only JSON matching the provided output schema.\n"
            "Do not decide game-state changes, rewards, HP, inventory, quest completion, "
            "or save data. Deterministic code owns those rules.\n"
            f"Task: {purpose}.\n"
            f"Input JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        )

    def _read_output(self, output_path: Path, stdout: str) -> str:
        if output_path.exists():
            return output_path.read_text(encoding="utf-8").strip()
        if stdout.strip():
            return stdout.strip()
        raise CodexCliProviderError("Codex CLI did not produce a structured response.")
