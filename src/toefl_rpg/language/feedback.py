from __future__ import annotations


def evaluate_english(text: str) -> str:
    normalized = " ".join(text.strip().split())
    lowered = normalized.lower()

    if not normalized:
        return ""
    if _is_short_command(lowered):
        return "Short command accepted. Try a full sentence for better practice."
    if "want collect" in lowered:
        return "Better English: I want to collect ..."
    if "want go" in lowered:
        return "Better English: I want to go ..."
    if lowered.startswith("talk ") and not lowered.startswith("talk to "):
        return "Better English: Use 'talk to someone', for example: talk to Dr. Lin."
    if len(normalized.split()) >= 4:
        return "Good: you used a full sentence."
    return "Understood. Try adding more detail in a full sentence."


def _is_short_command(text: str) -> bool:
    return text in {
        "help",
        "look",
        "look around",
        "inventory",
        "items",
        "bag",
        "status",
        "stats",
        "progress",
        "quit",
        "exit",
        "north",
        "south",
        "east",
        "west",
    } or text.startswith(
        (
            "go ",
            "use ",
            "inspect ",
            "examine ",
            "study ",
            "collect ",
            "take ",
            "gather ",
            "talk to ",
        )
    )
