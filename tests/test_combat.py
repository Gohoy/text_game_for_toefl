from toefl_rpg.engine.combat import calculate_damage


def test_damage_subtracts_defense() -> None:
    assert calculate_damage(7, 2) == 5


def test_damage_always_does_at_least_one_point() -> None:
    assert calculate_damage(2, 9) == 1
