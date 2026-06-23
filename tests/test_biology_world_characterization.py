from toefl_rpg.content.sample_world import build_biology_realm
from toefl_rpg.engine.quests import BIOLOGY_STEPS


def test_biology_world_identity_and_core_words() -> None:
    world = build_biology_realm()

    assert world.world_id == "biology_realm_01"
    assert world.title == "Biology Realm"
    assert world.source_category == "生物"
    assert world.start_room_id == "research_camp"
    assert world.core_words == [
        "organism",
        "fungus",
        "microscope",
        "bacteria",
        "strain",
        "symbiosis",
        "vital",
        "species",
        "evolve",
        "vaccine",
        "immune",
        "respiration",
        "metabolism",
        "mimicry",
        "creature",
        "extinction",
    ]


def test_biology_room_topology_and_content_placement() -> None:
    world = build_biology_realm()

    assert set(world.rooms) == {
        "research_camp",
        "microscope_tent",
        "vaccine_bench",
        "fungus_grove",
        "mimicry_trail",
    }
    assert world.room("research_camp").exits == {
        "east": "microscope_tent",
        "north": "fungus_grove",
    }
    assert world.room("microscope_tent").exits == {
        "west": "research_camp",
        "east": "vaccine_bench",
    }
    assert world.room("vaccine_bench").exits == {"west": "microscope_tent"}
    assert world.room("fungus_grove").exits == {
        "south": "research_camp",
        "north": "mimicry_trail",
    }
    assert world.room("mimicry_trail").exits == {"south": "fungus_grove"}

    assert world.room("research_camp").items == ["field notebook"]
    assert world.room("research_camp").npcs == ["Dr. Lin"]
    assert world.room("microscope_tent").items == ["microscope", "glass slide"]
    assert world.room("vaccine_bench").items == ["vaccine vial"]
    assert world.room("fungus_grove").items == ["fungus sample"]
    assert world.room("mimicry_trail").items == ["creature sketch"]
    assert world.room("mimicry_trail").enemies == ["invasive_vine"]
    assert (
        world.item_descriptions["vaccine vial"]
        == "A small amount of clear liquid moves inside when you shake the sealed vial."
    )


def test_biology_room_target_words() -> None:
    world = build_biology_realm()

    assert world.room("research_camp").target_words == ["organism", "species", "evolve"]
    assert world.room("microscope_tent").target_words == [
        "microscope",
        "bacteria",
        "strain",
    ]
    assert world.room("vaccine_bench").target_words == [
        "vaccine",
        "immune",
        "respiration",
        "metabolism",
    ]
    assert world.room("fungus_grove").target_words == ["symbiosis", "fungus", "vital"]
    assert world.room("mimicry_trail").target_words == [
        "mimicry",
        "creature",
        "extinction",
    ]


def test_biology_enemy_contract() -> None:
    world = build_biology_realm()
    enemy = world.enemy("invasive_vine")

    assert set(world.enemies) == {"invasive_vine"}
    assert enemy.id == "invasive_vine"
    assert enemy.name == "Invasive Vine"
    assert enemy.hp == 13
    assert enemy.attack == 3
    assert enemy.defense == 1
    assert enemy.xp == 12
    assert enemy.target_words == ["mimicry", "creature", "extinction"]


def test_biology_quest_step_contract() -> None:
    assert [(step.id, step.xp) for step in BIOLOGY_STEPS] == [
        ("collect_fungus_sample", 10),
        ("analyze_fungus_sample", 20),
        ("clear_invasive_vine", 15),
    ]
    assert [step.title for step in BIOLOGY_STEPS] == [
        "Collect a fungus sample",
        "Analyze the sample",
        "Clear the invasive vine",
    ]
