from __future__ import annotations

from copy import deepcopy
from typing import Optional

from toefl_rpg.ai.contract import AIProvider
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import require_ai_provider
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
    def __init__(
        self,
        state: GameState,
        ai_provider: Optional[AIProvider] = None,
        use_deterministic_feedback: bool = False,
    ) -> None:
        self.state = state
        self.ai_provider = ai_provider
        self.use_deterministic_feedback = use_deterministic_feedback

    @classmethod
    def new_game(
        cls,
        world: World,
        ai_provider: Optional[AIProvider] = None,
        use_deterministic_feedback: bool = False,
    ) -> "GameEngine":
        return cls(
            GameState(world=world, current_room_id=world.start_room_id),
            ai_provider=ai_provider,
            use_deterministic_feedback=use_deterministic_feedback,
        )

    def handle(self, text: str) -> TurnResult:
        intent = parse_intent(text)
        feedback = ""
        before_state = deepcopy(self.state)
        if intent.action == "quit":
            result = TurnResult(True, "Progress saved. Goodbye.", feedback, True)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "help":
            result = TurnResult(
                True,
                (
                    "Try full sentences: I want to go north; I want to inspect the microscope; "
                    "I want to collect the fungus sample; I want to use the microscope; "
                    "talk to Dr. Lin; The fungus is vital for the forest."
                ),
                feedback,
            )
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "inventory":
            result = TurnResult(True, self._inventory_summary(), feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "status":
            result = TurnResult(True, self._status_summary(), feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "look":
            result = TurnResult(True, "You take a careful look around.", feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "move":
            result = self._move(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "inspect":
            result = self._inspect(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "collect":
            result = self._collect(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "use":
            result = self._use(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "talk":
            result = self._talk(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "attack":
            result = self._attack(intent, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        practice_result = self._practice_sentence(text, feedback)
        if practice_result is not None:
            return self._with_turn_feedback(text, intent, practice_result, before_state)
        result = TurnResult(
            False,
            "I could not turn that sentence into a game action yet. Try: go north, inspect microscope, collect sample, attack the invasive vine, talk to Dr. Lin, or write a sentence using this room's vocabulary.",
            feedback,
        )
        return self._with_turn_feedback(text, intent, result, before_state)

    def _with_turn_feedback(
        self,
        text: str,
        intent: ParsedIntent,
        result: TurnResult,
        before_state: GameState,
    ) -> TurnResult:
        if self.use_deterministic_feedback:
            return TurnResult(
                result.success,
                result.message,
                evaluate_english(text),
                result.should_quit,
            )

        provider = require_ai_provider(self.ai_provider)
        request = TurnFeedbackRequest(
            player_sentence=text,
            location_id=before_state.current_room_id,
            deterministic_action=intent.action,
            deterministic_result=result.message,
            target_words=before_state.current_room.target_words,
            practiced_words=sorted(self.state.mastered_words - before_state.mastered_words),
        )
        try:
            feedback = provider.generate_turn_feedback(request)
        except Exception:
            self.state = before_state
            raise

        return TurnResult(
            result.success,
            result.message,
            self._format_ai_feedback(
                feedback.narration,
                feedback.sentence_feedback,
                feedback.suggested_sentence,
                feedback.vocabulary_notes,
            ),
            result.should_quit,
        )

    def _format_ai_feedback(
        self,
        narration: str,
        sentence_feedback: str,
        suggested_sentence: str,
        vocabulary_notes: list[str],
    ) -> str:
        lines = [
            f"Narration: {narration}",
            f"Feedback: {sentence_feedback}",
            f"Try: {suggested_sentence}",
        ]
        lines.extend(f"Vocabulary: {note}" for note in vocabulary_notes)
        return "\n".join(lines)

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
