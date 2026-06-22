from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Callable, Optional

from toefl_rpg.ai.contract import AIProvider
from toefl_rpg.ai.contract import AIProviderUnavailable
from toefl_rpg.ai.contract import NPCDialogue
from toefl_rpg.ai.contract import NPCDialogueRequest
from toefl_rpg.ai.contract import PlayerSentenceInterpretation
from toefl_rpg.ai.contract import PlayerSentenceInterpretationRequest
from toefl_rpg.ai.contract import ReviewAnswerEvaluation
from toefl_rpg.ai.contract import ReviewAnswerEvaluationRequest
from toefl_rpg.ai.contract import RoomNarration
from toefl_rpg.ai.contract import RoomNarrationRequest
from toefl_rpg.ai.contract import TurnFeedback
from toefl_rpg.ai.contract import TurnFeedbackRequest
from toefl_rpg.ai.contract import VocabularyExplanation
from toefl_rpg.ai.contract import VocabularyExplanationRequest
from toefl_rpg.ai.contract import require_ai_provider
from toefl_rpg.content.schema import World
from toefl_rpg.engine.combat import PLAYER_ATTACK, PLAYER_DEFENSE, calculate_damage
from toefl_rpg.engine.mastery import LearningEvent
from toefl_rpg.engine.mastery import record_learning_event
from toefl_rpg.engine.mastery import record_rewardable_usage
from toefl_rpg.engine.mastery import record_room_encounter
from toefl_rpg.engine.mastery import review_context_id
from toefl_rpg.engine.mastery import response_fingerprint
from toefl_rpg.engine.mastery import room_context_id
from toefl_rpg.engine.mastery import schedule_initial_review
from toefl_rpg.engine.mastery import select_due_vocabulary
from toefl_rpg.engine.quests import (
    ANALYZE_FUNGUS_SAMPLE,
    CLEAR_INVASIVE_VINE,
    COLLECT_FUNGUS_SAMPLE,
    quest_summary,
    step_for_task,
)
from toefl_rpg.engine.state import GameState, TurnResult, VocabularyMastery
from toefl_rpg.language.feedback import evaluate_english
from toefl_rpg.language.parser import ParsedIntent, parse_intent


class GameEngine:
    def __init__(
        self,
        state: GameState,
        ai_provider: Optional[AIProvider] = None,
        use_deterministic_feedback: bool = False,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.state = state
        self.ai_provider = ai_provider
        self.use_deterministic_feedback = use_deterministic_feedback
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @classmethod
    def new_game(
        cls,
        world: World,
        ai_provider: Optional[AIProvider] = None,
        use_deterministic_feedback: bool = False,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> "GameEngine":
        state = GameState(world=world, current_room_id=world.start_room_id)
        record_room_encounter(state)
        return cls(
            state,
            ai_provider=ai_provider,
            use_deterministic_feedback=use_deterministic_feedback,
            clock=clock,
        )

    def handle(self, text: str) -> TurnResult:
        intent = parse_intent(text)
        feedback = ""
        before_state = deepcopy(self.state)
        if intent.action == "unknown" and not self.use_deterministic_feedback:
            interpreted_intent, rejection = self._interpret_unknown_intent(text, before_state)
            if rejection is not None:
                return self._with_turn_feedback(text, intent, rejection, before_state)
            if interpreted_intent is not None:
                intent = interpreted_intent

        if intent.action == "quit":
            result = TurnResult(True, "Progress saved. Goodbye.", feedback, True)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "help":
            result = TurnResult(
                True,
                (
                    "Try full sentences: I want to go north; I want to inspect the microscope; "
                    "I want to collect the fungus sample; I want to use the microscope; "
                    "explain fungus; talk to Dr. Lin; The fungus is vital for the forest."
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
        if intent.action == "explain":
            result = self._explain_vocabulary(intent, text, feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "review":
            result = self._review_prompt(feedback)
            return self._with_turn_feedback(text, intent, result, before_state)
        if intent.action == "look":
            result = self._look(feedback)
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
        if self.state.active_review_word:
            review_result = self._review_sentence(text, feedback)
            return self._with_turn_feedback(text, intent, review_result, before_state)
        practice_result = self._practice_sentence(text, feedback)
        if practice_result is not None:
            return self._with_turn_feedback(text, intent, practice_result, before_state)
        result = TurnResult(
            False,
            "I could not turn that sentence into a game action yet. Try: go north, inspect microscope, collect sample, attack the invasive vine, talk to Dr. Lin, or write a sentence using this room's vocabulary.",
            feedback,
        )
        return self._with_turn_feedback(text, intent, result, before_state)

    def _interpret_unknown_intent(
        self,
        text: str,
        before_state: GameState,
    ) -> tuple[Optional[ParsedIntent], Optional[TurnResult]]:
        provider = require_ai_provider(self.ai_provider)
        room = before_state.current_room
        request = PlayerSentenceInterpretationRequest(
            player_sentence=text,
            location_id=before_state.current_room_id,
            room_name=room.name,
            exits=dict(room.exits),
            visible_items=list(room.items),
            visible_npcs=list(room.npcs),
            visible_enemies=[
                before_state.world.enemy(enemy_id).name
                for enemy_id in before_state.live_enemy_ids_in_current_room()
            ],
            target_words=list(room.target_words),
        )
        try:
            interpretation = PlayerSentenceInterpretation.model_validate(
                provider.interpret_player_sentence(request)
            )
        except Exception as exc:
            raise AIProviderUnavailable(
                f"AI sentence interpretation failed: {exc}"
            ) from exc

        if interpretation.action == "unknown":
            return None, None
        if interpretation.confidence < 0.5:
            return None, TurnResult(
                False,
                (
                    "I could not confidently turn that sentence into a game action. "
                    f"Try a clearer sentence for {interpretation.action}."
                ),
            )
        return ParsedIntent(interpretation.action, interpretation.target), None

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
            practiced_words=self._changed_mastery_words(before_state),
        )
        try:
            feedback = TurnFeedback.model_validate(
                provider.generate_turn_feedback(request)
            )
        except Exception as exc:
            self.state = before_state
            raise AIProviderUnavailable(f"AI turn feedback failed: {exc}") from exc

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

    def _changed_mastery_words(self, before_state: GameState) -> list[str]:
        changed_words = set(self.state.mastered_words - before_state.mastered_words)
        for word, record in self.state.vocabulary_mastery.items():
            before_record = before_state.vocabulary_mastery.get(word)
            if before_record is None:
                continue
            if (
                record.mastery_points != before_record.mastery_points
                or record.correct_use_count != before_record.correct_use_count
                or record.review_stage != before_record.review_stage
            ):
                changed_words.add(word)
        return sorted(changed_words)

    def _move(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        if intent.target not in room.exits:
            return TurnResult(False, f"You cannot go {intent.target} from here.", feedback)
        self.state.current_room_id = room.exits[intent.target]
        record_room_encounter(self.state)
        return TurnResult(True, f"You go {intent.target}.", feedback)

    def _look(self, feedback: str) -> TurnResult:
        room = self.state.current_room
        provider = require_ai_provider(self.ai_provider)
        request = RoomNarrationRequest(
            location_id=self.state.current_room_id,
            room_name=room.name,
            room_description=room.description,
            quest_progress=quest_summary(self.state.completed_tasks),
            exits=dict(room.exits),
            visible_items=list(room.items),
            visible_npcs=list(room.npcs),
            visible_enemies=[
                self.state.world.enemy(enemy_id).name
                for enemy_id in self.state.live_enemy_ids_in_current_room()
            ],
            target_words=list(room.target_words),
        )
        try:
            narration = RoomNarration.model_validate(
                provider.generate_room_narration(request)
            )
        except Exception as exc:
            raise AIProviderUnavailable(f"AI room narration failed: {exc}") from exc

        vocabulary_text = ""
        if narration.vocabulary_notes:
            vocabulary_text = "\nRoom vocabulary: " + "; ".join(
                narration.vocabulary_notes
            )
        return TurnResult(
            True,
            (
                f"{narration.narration}\n"
                f"Focus: {narration.focus_hint}"
                f"{vocabulary_text}"
            ),
            feedback,
        )

    def _inspect(self, intent: ParsedIntent, feedback: str) -> TurnResult:
        room = self.state.current_room
        target = intent.target or "room"
        visible = room.items + room.npcs + room.target_words
        matched_word = self._find_visible_word(target, visible)
        if not matched_word:
            return TurnResult(False, f"You do not see {target} here.", feedback)

        if matched_word in self.state.world.core_words:
            gained_xp = self._practice_words(
                [matched_word],
                5,
                context_id=self._context_id("inspect", matched_word),
            )
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
        gained_xp = self._practice_words(
            practiced,
            5,
            context_id=self._context_id("collect", item),
        )
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
            gained_xp = self._practice_words(
                words,
                5,
                context_id="quest:biology_investigation:analyze_fungus_sample",
            )
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

        provider = require_ai_provider(self.ai_provider)
        request = NPCDialogueRequest(
            npc_name=npc,
            location_id=self.state.current_room_id,
            room_name=room.name,
            quest_progress=quest_summary(self.state.completed_tasks),
            visible_items=list(room.items),
            visible_npcs=list(room.npcs),
            visible_enemies=[
                self.state.world.enemy(enemy_id).name
                for enemy_id in self.state.live_enemy_ids_in_current_room()
            ],
            target_words=list(room.target_words),
        )
        try:
            dialogue = NPCDialogue.model_validate(provider.generate_npc_dialogue(request))
            if dialogue.speaker.lower() != npc.lower():
                raise ValueError("AI NPC dialogue returned a different speaker.")
        except Exception as exc:
            raise AIProviderUnavailable(f"AI NPC dialogue failed: {exc}") from exc

        vocabulary_text = ""
        if dialogue.vocabulary_notes:
            vocabulary_text = "\nDialogue vocabulary: " + "; ".join(dialogue.vocabulary_notes)
        return TurnResult(
            True,
            f"{dialogue.speaker} says: {dialogue.line}{vocabulary_text}",
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
            vocab_xp = self._practice_words(
                enemy.target_words,
                5,
                context_id=f"combat:{enemy_id}",
            )
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

    def _practice_words(
        self,
        words: list[str],
        xp_each: int,
        context_id: str,
        sentence: str = "",
    ) -> int:
        gained_xp = 0
        reward_sentence = sentence or context_id
        for word in words:
            if not record_rewardable_usage(
                self.state,
                word,
                context_id,
                reward_sentence,
            ):
                continue
            schedule_initial_review(self.state.vocabulary_mastery[word], self._clock())
            self.state.mastered_words.add(word)
            self.state.player.xp += xp_each
            gained_xp += xp_each
        return gained_xp

    def _core_words_in_text(self, text: str) -> list[str]:
        lowered = text.lower()
        return [word for word in self.state.world.core_words if word.lower() in lowered]

    def _resolve_world_word(self, target: str) -> str:
        normalized = target.lower().strip()
        for prefix in ("the word ", "word ", "vocabulary word ", "vocabulary "):
            if normalized.startswith(prefix):
                normalized = normalized.removeprefix(prefix).strip()
                break
        return self._find_visible_word(normalized, self.state.world.core_words)

    def _practice_sentence(self, text: str, feedback: str) -> Optional[TurnResult]:
        if len(text.split()) < 4:
            return None

        room_words = self.state.current_room.target_words
        practiced = self._core_words_in_text(text)
        contextual_words = [word for word in practiced if word in room_words]
        if not contextual_words:
            self._record_incorrect_practice(text, practiced)
            return None

        gained_xp = self._practice_words(
            contextual_words,
            8,
            context_id=room_context_id(self.state.current_room_id),
            sentence=text,
        )
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

    def _review_prompt(self, feedback: str) -> TurnResult:
        due_words = select_due_vocabulary(self.state, self._clock(), limit=5)
        if not due_words:
            self.state.active_review_word = None
            return TurnResult(
                True,
                "No vocabulary is due for review yet. Use target words in context to schedule review.",
                feedback,
            )

        review_word = due_words[0]
        self.state.active_review_word = review_word
        due_text = ", ".join(due_words)
        return TurnResult(
            True,
            (
                f"Review due: {due_text}. Write a full English sentence using "
                f"'{review_word}' to complete the next review."
            ),
            feedback,
        )

    def _explain_vocabulary(
        self,
        intent: ParsedIntent,
        original_text: str,
        feedback: str,
    ) -> TurnResult:
        requested_word = self._resolve_world_word(intent.target)
        if not requested_word:
            return TurnResult(
                False,
                f"'{intent.target or 'that'}' is not a {self.state.world.title} vocabulary word.",
                feedback,
            )

        explainable_words = (
            set(self.state.current_room.target_words) | self.state.mastered_words
        )
        if requested_word not in explainable_words:
            return TurnResult(
                False,
                (
                    f"'{requested_word}' is in {self.state.world.title}, but it is not visible "
                    "here or practiced yet."
                ),
                feedback,
            )

        provider = require_ai_provider(self.ai_provider)
        request = VocabularyExplanationRequest(
            word=requested_word,
            theme=self.state.world.title,
            learner_sentence=original_text,
        )
        try:
            explanation = VocabularyExplanation.model_validate(
                provider.explain_vocabulary(request)
            )
            if explanation.word.lower() != requested_word.lower():
                raise ValueError("AI vocabulary explanation returned a different word.")
        except Exception as exc:
            raise AIProviderUnavailable(
                f"AI vocabulary explanation failed: {exc}"
            ) from exc

        return TurnResult(
            True,
            (
                f"{explanation.word}: {explanation.plain_meaning}\n"
                f"Example: {explanation.example_sentence}\n"
                f"Memory hint: {explanation.memory_hint}"
            ),
            feedback,
        )

    def _review_sentence(self, text: str, feedback: str) -> TurnResult:
        word = self.state.active_review_word
        if not word:
            return TurnResult(False, "No review word is active.", feedback)

        record = self.state.vocabulary_mastery.setdefault(word, VocabularyMastery(word=word))
        context_id = review_context_id(self.state.world.world_id, word, record.review_stage)
        fingerprint = response_fingerprint(text, word, context_id)
        is_full_sentence = len(text.split()) >= 4
        uses_word = word.lower() in text.lower()
        if not is_full_sentence or not uses_word:
            record_learning_event(
                self.state,
                LearningEvent.REVIEW_INCORRECT,
                word,
                context_id,
                fingerprint,
                practiced_at=self._clock(),
            )
            return TurnResult(
                False,
                (
                    f"Review needs another try: write a full sentence that uses '{word}' "
                    "clearly in context."
                ),
                feedback,
            )

        if fingerprint in record.recent_response_fingerprints:
            self.state.active_review_word = None
            return TurnResult(
                True,
                f"You already completed this review for '{word}' with that sentence.",
                feedback,
            )

        review_advice = ""
        if not self.use_deterministic_feedback:
            provider = require_ai_provider(self.ai_provider)
            request = ReviewAnswerEvaluationRequest(
                word=word,
                learner_sentence=text,
                theme=self.state.world.title,
                review_stage=record.review_stage,
            )
            try:
                evaluation = ReviewAnswerEvaluation.model_validate(
                    provider.evaluate_review_answer(request)
                )
            except Exception as exc:
                raise AIProviderUnavailable(
                    f"AI review evaluation failed: {exc}"
                ) from exc

            review_advice = self._format_review_advice(evaluation)
            if not evaluation.uses_target_meaningfully:
                record_learning_event(
                    self.state,
                    LearningEvent.REVIEW_INCORRECT,
                    word,
                    context_id,
                    fingerprint,
                    practiced_at=self._clock(),
                )
                return TurnResult(
                    False,
                    (
                        f"{review_advice}\n"
                        "Result: Review needs another try. "
                        f"No XP awarded; '{word}' remains active for review."
                    ),
                    feedback,
                )

        record_learning_event(
            self.state,
            LearningEvent.REVIEW_CORRECT,
            word,
            context_id,
            fingerprint,
            practiced_at=self._clock(),
        )
        self.state.mastered_words.add(word)
        self.state.player.xp += 10
        self.state.active_review_word = None
        result_summary = (
            f"Result: Review complete for '{word}'. "
            f"Review stage {record.review_stage}. XP +10."
        )
        return TurnResult(
            True,
            f"{review_advice}\n{result_summary}" if review_advice else result_summary,
            feedback,
        )

    def _format_review_advice(self, evaluation: ReviewAnswerEvaluation) -> str:
        return (
            f"AI advice: {evaluation.explanation}\n"
            f"Try: {evaluation.suggested_sentence}"
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

    def _record_incorrect_practice(self, text: str, words: list[str]) -> None:
        context_id = room_context_id(self.state.current_room_id)
        for word in words:
            record_learning_event(
                self.state,
                LearningEvent.USAGE_INCORRECT,
                word,
                context_id,
                response_fingerprint(text, word, context_id),
            )

    def _context_id(self, kind: str, value: str) -> str:
        stable_value = value.lower().replace(" ", "_")
        return f"{kind}:{stable_value}"
