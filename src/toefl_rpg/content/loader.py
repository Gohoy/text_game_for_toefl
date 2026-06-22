from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from toefl_rpg.content.schema import WorldPack


class WorldPackLoadError(RuntimeError):
    """Raised when a world pack file cannot be loaded or validated."""


def load_world_pack(path: Path) -> WorldPack:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise WorldPackLoadError(f"World pack file not found: {path}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise WorldPackLoadError(
            f"Invalid JSON in world pack {path}: line {exc.lineno}, column {exc.colno}"
        ) from exc

    try:
        return WorldPack.model_validate(payload)
    except ValidationError as exc:
        raise WorldPackLoadError(f"Invalid world pack schema in {path}: {exc}") from exc
