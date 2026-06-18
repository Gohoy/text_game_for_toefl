from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedIntent:
    action: str
    target: str = ""


def parse_intent(text: str) -> ParsedIntent:
    normalized = " ".join(text.lower().strip().split())
    if normalized in {"quit", "exit"}:
        return ParsedIntent("quit")
    if normalized in {"help", "commands"}:
        return ParsedIntent("help")
    if normalized in {"inventory", "items", "bag"}:
        return ParsedIntent("inventory")
    if normalized in {"status", "stats", "progress"}:
        return ParsedIntent("status")
    if normalized in {"look", "look around"}:
        return ParsedIntent("look")

    for direction in ("north", "south", "east", "west"):
        if normalized == direction or normalized.endswith(f" go {direction}"):
            return ParsedIntent("move", direction)
        if normalized.startswith(f"go {direction}") or f" to the {direction}" in normalized:
            return ParsedIntent("move", direction)
        if f"walk {direction}" in normalized or f"move {direction}" in normalized:
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

    return ParsedIntent("unknown", normalized)
