from __future__ import annotations

from typing import Optional

from toefl_rpg.content.schema import World
from toefl_rpg.engine.combat import PLAYER_ATTACK, PLAYER_DEFENSE, calculate_damage
from toefl_rpg.engine.quests import (
    ANALYZE_FUNGUS_SAMPLE,
    CLEAR_INVASIVE_VINE,
    COLLECT_FUNGUS_SAMPLE,
    quest_summary,
    step_for_task,
)
from toefl_rpg.engine.state import GameState, TurnResult
from toefl_rpg.language.feedback import evaluate_english
from toefl_rpg.language.parser import ParsedIntent, parse_intent


class GameEngine:
    def __init__(self, state: GameState) -> None:
        self.state = state

    @classmethod
    def new_game(cls, world: World) -> "GameEngine":
        return cls(GameState(world=world, current_room_id=world.start_room_id))

    def handle(self, text: str) -> TurnResult:
        intent = parse_intent(text)
        feedback = evaluate_english(text)

        if intent.action == "quit":
            return TurnResult(True, "Progress saved. Goodbye.", feedback, True)
        if intent.action == "help":
            return TurnResult(
                True,
                (
                    "Try full sentences: I want to go north; I want to inspect the microscope; "
                    "I want to collect the fungus sample; I want to use the microscope; "
                    "talk to Dr. Lin; The fungus is vital for the forest."
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
        if intent.action == "attack":
            return self._attack(intent, feedback)
        practice_result = self._practice_sentence(text, feedback)
        if practice_result is not None:
            return practice_result
        return TurnResult(
            False,
            "I could not turn that sentence into a game action yet. Try: go north, inspect microscope, collect sample, attack the invasive vine, talk to Dr. Lin, or write a sentence using this room's vocabulary.",
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
                "Then analyze it under the microscope and clear the invasive vine "
                "on the mimicry trail."
            ),
            feedback,
        )

    def _attack(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        if self.state.player.hp <= 0:
            return TurnResult(
                False,
                "You are too weak to fight. Resting is not implemented yet.",
                feedback,
            )

        enemy_id = self._find_enemy_id(intent.target)
        if not enemy_id:
            return TurnResult(False, f"You do not see {intent.target or 'that enemy'} here.", feedback)

        enemy = self.state.world.enemy(enemy_id)
        current_hp = self.state.enemy_hp.get(enemy_id, enemy.hp)
        player_damage = calculate_damage(PLAYER_ATTACK, enemy.defense)
        current_hp = max(0, current_hp - player_damage)
        self.state.enemy_hp[enemy_id] = current_hp

        if current_hp == 0:
            self.state.defeated_enemies.add(enemy_id)
            self.state.player.xp += enemy.xp
            vocab_xp = self._practice_words(enemy.target_words, 5)
            quest_text = ""
            if enemy_id == "invasive_vine":
                quest_text = self._complete_task(CLEAR_INVASIVE_VINE)
            vocab_text = (
                f" Practiced words: {', '.join(enemy.target_words)}. XP +{vocab_xp}."
                if vocab_xp
                else " Its vocabulary was already practiced."
            )
            return TurnResult(
                True,
                (
                    f"You strike {enemy.name} for {player_damage} damage and defeat it. "
                    f"Combat XP +{enemy.xp}.{vocab_text}"
                    f"{quest_text}"
                ),
                feedback,
            )

        enemy_damage = calculate_damage(enemy.attack, PLAYER_DEFENSE)
        self.state.player.hp = max(0, self.state.player.hp - enemy_damage)
        return TurnResult(
            True,
            (
                f"You strike {enemy.name} for {player_damage} damage. "
                f"It has {current_hp}/{enemy.hp} HP left. "
                f"{enemy.name} hits back for {enemy_damage} damage."
            ),
            feedback,
        )

    def _find_enemy_id(self, target: str) -> str:
        target = target.lower()
        for enemy_id in self.state.live_enemy_ids_in_current_room():
            enemy = self.state.world.enemy(enemy_id)
            candidates = [enemy_id.replace("_", " "), enemy.name.lower()]
            if any(candidate in target or target in candidate for candidate in candidates):
                return enemy_id
        live_enemy_ids = self.state.live_enemy_ids_in_current_room()
        if not target and len(live_enemy_ids) == 1:
            return live_enemy_ids[0]
        return ""

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

    def _practice_sentence(self, text: str, feedback: str) -> Optional[TurnResult]:
        if len(text.split()) < 4:
            return None

        room_words = self.state.current_room.target_words
        practiced = self._core_words_in_text(text)
        contextual_words = [word for word in practiced if word in room_words]
        if not contextual_words:
            return None

        gained_xp = self._practice_words(contextual_words, 8)
        words_text = ", ".join(contextual_words)
        if gained_xp:
            return TurnResult(
                True,
                f"You used target vocabulary in context: {words_text}. XP +{gained_xp}.",
                feedback,
            )
        return TurnResult(
            True,
            f"You used already-practiced vocabulary in context: {words_text}.",
            feedback,
        )

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
