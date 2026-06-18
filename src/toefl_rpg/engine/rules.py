from __future__ import annotations

from toefl_rpg.content.schema import World
from toefl_rpg.engine.state import GameState, TurnResult
from toefl_rpg.language.parser import ParsedIntent, parse_intent


class GameEngine:
    def __init__(self, state: GameState) -> None:
        self.state = state

    @classmethod
    def new_game(cls, world: World) -> "GameEngine":
        return cls(GameState(world=world, current_room_id=world.start_room_id))

    def handle(self, text: str) -> TurnResult:
        intent = parse_intent(text)
        feedback = self._english_feedback(text)

        if intent.action == "quit":
            return TurnResult(True, "Progress is not saved yet. Goodbye.", feedback, True)
        if intent.action == "look":
            return TurnResult(True, "You take a careful look around.", feedback)
        if intent.action == "move":
            return self._move(intent, feedback)
        if intent.action == "inspect":
            return self._inspect(intent, feedback)
        if intent.action == "talk":
            return self._talk(intent, feedback)
        return TurnResult(
            False,
            "I could not turn that sentence into a game action yet. Try: go north, inspect microscope, or talk to Dr. Lin.",
            feedback,
        )

    def _move(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        if intent.target not in room.exits:
            return TurnResult(False, f"You cannot go {intent.target} from here.", feedback)
        self.state.current_room_id = room.exits[intent.target]
        return TurnResult(True, f"You go {intent.target}.", feedback)

    def _inspect(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target or "room"
        visible = room.items + room.npcs + room.target_words
        matched_word = self._find_visible_word(target, visible)
        if not matched_word:
            return TurnResult(False, f"You do not see {target} here.", feedback)

        if matched_word in self.state.world.core_words:
            self.state.mastered_words.add(matched_word)
            self.state.player.xp += 5
            return TurnResult(
                True,
                f"You study {matched_word}. It is now marked as practiced. XP +5.",
                feedback,
            )
        return TurnResult(True, f"You inspect {matched_word}.", feedback)

    def _talk(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target
        npc = self._find_visible_word(target, room.npcs)
        if not npc:
            return TurnResult(False, f"{target or 'That person'} is not here.", feedback)
        return TurnResult(
            True,
            f"{npc} says: Use complete English sentences to describe what you observe.",
            feedback,
        )

    def _english_feedback(self, text: str) -> str:
        lowered = text.lower()
        if "want collect" in lowered:
            return "Better English: I want to collect ..."
        if len(text.split()) >= 4:
            return "Good: you used a full sentence."
        return "Short command accepted. Try a full sentence for better practice."

    def _find_visible_word(self, target: str, candidates: list[str]) -> str:
        target = target.lower()
        for candidate in candidates:
            if candidate.lower() in target or target in candidate.lower():
                return candidate
        return ""

