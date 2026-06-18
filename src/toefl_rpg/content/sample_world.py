from __future__ import annotations

from toefl_rpg.content.schema import Room, World


def build_biology_realm() -> World:
    rooms = {
        "research_camp": Room(
            id="research_camp",
            name="Research Camp",
            description=(
                "A quiet camp beside the forest. Dr. Lin studies how organisms adapt "
                "when a strange fungus spreads through the valley."
            ),
            exits={"east": "microscope_tent", "north": "fungus_grove"},
            items=["field notebook"],
            npcs=["Dr. Lin"],
            target_words=["organism", "adapt", "fungus"],
        ),
        "microscope_tent": Room(
            id="microscope_tent",
            name="Microscope Tent",
            description=(
                "Glass slides and a microscope sit on a clean table. A note asks you "
                "to compare bacteria with the unknown strain."
            ),
            exits={"west": "research_camp"},
            items=["microscope", "glass slide"],
            target_words=["microscope", "bacteria", "strain"],
        ),
        "fungus_grove": Room(
            id="fungus_grove",
            name="Fungus Grove",
            description=(
                "Pale mushrooms cover old roots. Some trees look weak, but others "
                "seem to live in symbiosis with the fungus."
            ),
            exits={"south": "research_camp"},
            items=["fungus sample"],
            target_words=["symbiosis", "fungus", "vital"],
        ),
    }
    return World(
        world_id="biology_realm_01",
        title="Biology Realm",
        source_category="生物",
        difficulty="A2-B1",
        start_room_id="research_camp",
        core_words=[
            "organism",
            "adapt",
            "fungus",
            "microscope",
            "bacteria",
            "strain",
            "symbiosis",
            "vital",
        ],
        rooms=rooms,
    )

