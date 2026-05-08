import os
from src.playerData import CHARACTER_DATA, WARRIOR_DATA, SORCERER_DATA, HUNTRESS_DATA, OLD_WIZARD_DATA

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def test_character_data_has_attack_2_offset_field():
    """CHARACTER_DATA must expose a separate offset for attack2."""
    assert hasattr(CHARACTER_DATA, "__dataclass_fields__")
    assert "attack_2_offset" in CHARACTER_DATA.__dataclass_fields__


def test_attack_2_offset_defaults_to_zero():
    """Existing characters without an explicit attack_2_offset get [0, 0]."""
    data = CHARACTER_DATA(
        size=100, scale=1, offset=[0, 0], speed=5, jump_height=10,
        attack_1_range=[100, 100], attack_2_range=[150, 150], attack_offset=[10, 5]
    )
    assert data.attack_2_offset == [0, 0]


def test_attack_2_offset_can_be_set():
    """attack_2_offset can be independently configured from attack_offset."""
    data = CHARACTER_DATA(
        size=100, scale=1, offset=[0, 0], speed=5, jump_height=10,
        attack_1_range=[100, 100], attack_2_range=[200, 200],
        attack_offset=[10, 5], attack_2_offset=[30, 20]
    )
    assert data.attack_2_offset == [30, 20]
    assert data.attack_offset == [10, 5]


def test_existing_characters_are_not_broken():
    """All existing character definitions still construct without error."""
    for data in [WARRIOR_DATA, SORCERER_DATA, HUNTRESS_DATA, OLD_WIZARD_DATA]:
        assert data.attack_2_offset == [0, 0]
