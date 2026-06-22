from __future__ import annotations

from pathlib import Path

from toefl_rpg.content.loader import load_world_pack
from toefl_rpg.content.schema import World


BIOLOGY_WORLD_PACK_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "worlds" / "biology_realm_01.json"
)


def build_biology_realm() -> World:
    return load_world_pack(BIOLOGY_WORLD_PACK_PATH).to_world()
