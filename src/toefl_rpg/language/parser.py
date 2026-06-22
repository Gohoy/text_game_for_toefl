from __future__ import annotations

from dataclasses import dataclass

from toefl_rpg.engine.actions import DeterministicAction


@dataclass(frozen=True)
class ParsedIntent:
    action: DeterministicAction
    target: str = ""


def parse_intent(text: str) -> ParsedIntent:
    normalized = " ".join(text.lower().strip().split()).strip(".,!?")
    if normalized in {"quit", "exit"}:
        return ParsedIntent("quit")
    if normalized in {"help", "commands"}:
        return ParsedIntent("help")
    if normalized in {"inventory", "items", "bag"}:
        return ParsedIntent("inventory")
    if normalized in {"status", "stats", "progress"}:
        return ParsedIntent("status")
    if normalized in {"review", "review vocabulary", "start review"}:
        return ParsedIntent("review")
    if normalized.startswith("review "):
        return ParsedIntent("review", normalized.removeprefix("review ").strip())
    for prefix in ("explain ", "define "):
        if normalized.startswith(prefix):
            return ParsedIntent("explain", normalized.removeprefix(prefix).strip())
        marker = f" {prefix}"
        if marker in normalized:
            return ParsedIntent("explain", normalized.split(marker, 1)[1].strip())
    if normalized.startswith("what does ") and normalized.rstrip("?").endswith(" mean"):
        target = normalized.rstrip("?").removeprefix("what does ").removesuffix(" mean")
        return ParsedIntent("explain", target.strip())
    if normalized in {"look", "look around"}:
        return ParsedIntent("look")

    padded = f" {normalized} "
    negative_markers = (" do not ", " don't ", " dont ", " never ")
    if any(marker in padded for marker in negative_markers):
        return ParsedIntent("unknown", normalized)

    broad_destination_markers = (
        " take me to ",
        " bring me to ",
        " lead me to ",
    )
    if any(marker in padded for marker in broad_destination_markers):
        return ParsedIntent("unknown", normalized)

    movement_text = " ".join(
        normalized.translate(str.maketrans({",": " ", ";": " ", ":": " "})).split()
    )
    movement_padded = f" {movement_text} "
    for direction in ("north", "south", "east", "west"):
        if movement_text == direction or movement_text.endswith(f" go {direction}"):
            return ParsedIntent("move", direction)
        if (
            movement_text.startswith(f"go {direction}")
            or f" to the {direction}" in movement_text
        ):
            return ParsedIntent("move", direction)
        if (
            f" go {direction} " in movement_padded
            or f" walk {direction} " in movement_padded
            or f" move {direction} " in movement_padded
        ):
            return ParsedIntent("move", direction)

    for verb in ("inspect", "examine", "study", "look at"):
        if normalized.startswith(verb):
            return ParsedIntent("inspect", normalized.removeprefix(verb).strip())
        marker = f" {verb} "
        if marker in normalized:
            return ParsedIntent("inspect", normalized.split(marker, 1)[1].strip())

    for verb in ("collect", "take", "pick up", "gather"):
        if normalized.startswith(verb):
            return ParsedIntent("collect", normalized.removeprefix(verb).strip())
        marker = f" {verb} "
        if marker in normalized:
            return ParsedIntent("collect", normalized.split(marker, 1)[1].strip())

    if normalized.startswith("use "):
        return ParsedIntent("use", normalized.removeprefix("use ").strip())
    if " use " in normalized:
        return ParsedIntent("use", normalized.split(" use ", 1)[1].strip())

    if normalized.startswith("talk to "):
        return ParsedIntent("talk", normalized.removeprefix("talk to ").strip())
    if " talk to " in normalized:
        return ParsedIntent("talk", normalized.split(" talk to ", 1)[1].strip())

    for verb in ("attack", "strike", "hit", "fight"):
        if normalized.startswith(verb):
            return ParsedIntent("attack", normalized.removeprefix(verb).strip())
        marker = f" {verb} "
        if marker in normalized:
            return ParsedIntent("attack", normalized.split(marker, 1)[1].strip())

    return ParsedIntent("unknown", normalized)
