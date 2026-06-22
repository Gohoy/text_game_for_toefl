import json

from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.rules import GameEngine
from toefl_rpg.engine.storage import load_game, save_game


def new_test_engine() -> GameEngine:
    return GameEngine.new_game(
        build_biology_realm(),
        use_deterministic_feedback=True,
    )


def test_save_and_load_restores_progress(tmp_path) -> None:
    save_path = tmp_path / "slot1.json"
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("I want to collect the fungus sample")
    engine.handle("go south")

    save_game(engine.state, save_path)
    loaded = load_game(build_biology_realm(), save_path)

    assert loaded is not None
    assert loaded.current_room_id == "research_camp"
    assert loaded.player.xp == engine.state.player.xp
    assert loaded.player.inventory == ["fungus sample"]
    assert "fungus" in loaded.mastered_words
    assert "collect_fungus_sample" in loaded.completed_tasks
    assert "fungus sample" not in loaded.world.room("fungus_grove").items


def test_new_save_contains_versioned_mastery_data(tmp_path) -> None:
    save_path = tmp_path / "slot1.json"
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("The fungus is vital for the old forest.")

    save_game(engine.state, save_path)

    payload = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload["mastery"]["version"] == 1
    assert set(payload["mastery"]["words"]) == {"fungus", "vital"}
    fungus_record = payload["mastery"]["words"]["fungus"]
    assert fungus_record == {
        "word": "fungus",
        "status": "learning",
        "mastery_points": 1,
        "encounter_count": 0,
        "correct_use_count": 1,
        "incorrect_use_count": 0,
        "review_stage": 0,
        "last_practiced_at": None,
        "next_review_at": None,
        "distinct_context_ids": [],
        "recent_response_fingerprints": [],
    }


def test_load_legacy_save_without_mastery_uses_safe_defaults(tmp_path) -> None:
    save_path = tmp_path / "slot1.json"
    save_path.write_text(
        json.dumps(
            {
                "version": 1,
                "world_id": "biology_realm_01",
                "current_room_id": "fungus_grove",
                "player": {
                    "hp": 30,
                    "max_hp": 30,
                    "xp": 8,
                    "inventory": [],
                },
                "mastered_words": ["fungus"],
                "completed_tasks": [],
                "enemy_hp": {},
                "defeated_enemies": [],
                "room_items": {},
            }
        ),
        encoding="utf-8",
    )

    loaded = load_game(build_biology_realm(), save_path)

    assert loaded is not None
    assert loaded.mastered_words == {"fungus"}
    assert set(loaded.vocabulary_mastery) == {"fungus"}
    record = loaded.vocabulary_mastery["fungus"]
    assert record.word == "fungus"
    assert record.status == "learning"
    assert record.mastery_points == 1
    assert record.correct_use_count == 1
    assert record.distinct_context_ids == set()
    assert record.recent_response_fingerprints == []


def test_save_and_load_restores_combat_progress(tmp_path) -> None:
    save_path = tmp_path / "slot1.json"
    engine = new_test_engine()
    engine.handle("go north")
    engine.handle("go north")
    engine.handle("I attack the invasive vine")
    engine.handle("I attack the invasive vine")
    engine.handle("I attack the invasive vine")

    save_game(engine.state, save_path)
    loaded = load_game(build_biology_realm(), save_path)

    assert loaded is not None
    assert loaded.enemy_hp["invasive_vine"] == 0
    assert "invasive_vine" in loaded.defeated_enemies
    assert loaded.live_enemy_ids_in_current_room() == []


def test_load_missing_save_returns_none(tmp_path) -> None:
    loaded = load_game(build_biology_realm(), tmp_path / "missing.json")

    assert loaded is None
