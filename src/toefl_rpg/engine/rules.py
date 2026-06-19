from __future__ import annotations

from toefl_rpg.content.schema import World
from toefl_rpg.engine.quests import (
    ANALYZE_FUNGUS_SAMPLE,
    COLLECT_FUNGUS_SAMPLE,
    quest_summary,
    step_for_task,
)
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
            return TurnResult(True, "Progress saved. Goodbye.", feedback, True)
        if intent.action == "help":
            return TurnResult(
                True,
                (
                    "Try full sentences: I want to go north; I want to inspect the microscope; "
                    "I want to collect the fungus sample; I want to use the microscope; "
                    "talk to Dr. Lin."
                ),
                feedback,
            )
        if intent.action == "inventory":
            return TurnResult(True, self._inventory_summary(), feedback)
        if intent.action == "status":
            return TurnResult(True, self._status_summary(), feedback)
        if intent.action == "look":
            return TurnResult(True, "You take a careful look around.", feedback)
        if intent.action == "move":
            return self._move(intent, feedback)
        if intent.action == "inspect":
            return self._inspect(intent, feedback)
        if intent.action == "collect":
            return self._collect(intent, feedback)
        if intent.action == "use":
            return self._use(intent, feedback)
        if intent.action == "talk":
            return self._talk(intent, feedback)
        return TurnResult(
            False,
            "I could not turn that sentence into a game action yet. Try: go north, inspect microscope, collect sample, or talk to Dr. Lin.",
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
            gained_xp = self._practice_words([matched_word], 5)
            xp_text = f" XP +{gained_xp}." if gained_xp else " You already practiced this word."
            return TurnResult(
                True,
                f"You study {matched_word}. It is now marked as practiced.{xp_text}",
                feedback,
            )
        return TurnResult(True, f"You inspect {matched_word}.", feedback)

    def _collect(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target or "item"
        item = self._find_visible_word(target, room.items)
        if not item:
            return TurnResult(False, f"You cannot collect {target} here.", feedback)

        room.items.remove(item)
        self.state.player.inventory.append(item)
        practiced = self._core_words_in_text(item)
        gained_xp = self._practice_words(practiced, 5)
        practice_text = (
            f" Practiced words: {', '.join(practiced)}. XP +{gained_xp}."
            if practiced and gained_xp
            else ""
        )
        quest_text = ""
        if item == "fungus sample":
            quest_text = self._complete_task(COLLECT_FUNGUS_SAMPLE)
        return TurnResult(True, f"You collect {item}.{practice_text}{quest_text}", feedback)

    def _use(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target or "item"
        visible_or_carried = room.items + self.state.player.inventory + room.target_words
        item = self._find_visible_word(target, visible_or_carried)
        if not item:
            return TurnResult(False, f"You cannot use {target} here.", feedback)

        if "microscope" in item.lower():
            if room.id != "microscope_tent":
                return TurnResult(False, "The microscope is in the Microscope Tent.", feedback)
            if "fungus sample" not in self.state.player.inventory:
                return TurnResult(
                    False,
                    "You need a fungus sample before the microscope can reveal anything useful.",
                    feedback,
                )
            words = ["microscope", "bacteria", "strain"]
            gained_xp = self._practice_words(words, 5)
            quest_text = self._complete_task(ANALYZE_FUNGUS_SAMPLE)
            return TurnResult(
                True,
                (
                    "Under the microscope, the fungus sample shows a bacterial strain "
                    f"around the cells. Practiced words: {', '.join(words)}. XP +{gained_xp}."
                    f"{quest_text}"
                ),
                feedback,
            )

        return TurnResult(True, f"You use {item}, but nothing changes yet.", feedback)

    def _talk(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target
        npc = self._find_visible_word(target, room.npcs)
        if not npc:
            return TurnResult(False, f"{target or 'That person'} is not here.", feedback)
        return TurnResult(
            True,
            (
                f"{npc} says: Start by collecting a fungus sample in the grove. "
                "Then bring it back to the microscope tent and describe what you observe."
            ),
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

    def _practice_words(self, words: list[str], xp_each: int) -> int:
        gained_xp = 0
        for word in words:
            if word in self.state.mastered_words:
                continue
            self.state.mastered_words.add(word)
            self.state.player.xp += xp_each
            gained_xp += xp_each
        return gained_xp

    def _core_words_in_text(self, text: str) -> list[str]:
        lowered = text.lower()
        return [word for word in self.state.world.core_words if word.lower() in lowered]

    def _inventory_summary(self) -> str:
        if not self.state.player.inventory:
            return "Your inventory is empty."
        return "Inventory: " + ", ".join(self.state.player.inventory)

    def _status_summary(self) -> str:
        mastered = len(self.state.mastered_words)
        total = len(self.state.world.core_words)
        return (
            f"HP {self.state.player.hp}/{self.state.player.max_hp}. XP {self.state.player.xp}. "
            f"Vocabulary {mastered}/{total} practiced. Quest: {quest_summary(self.state.completed_tasks)}"
        )

    def _complete_task(self, task_id: str) -> str:
        if task_id in self.state.completed_tasks:
            return ""
        step = step_for_task(task_id)
        if step is None:
            return ""
        self.state.completed_tasks.add(task_id)
        self.state.player.xp += step.xp
        return f" Quest updated: {step.title}. XP +{step.xp}."
