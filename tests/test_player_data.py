import os
from src.playerData import HUNTRESS_DATA, OLD_WIZARD_DATA

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

MIN_ATTACK_RANGE = 100  # minimum pixels for a hitbox to be functional


def test_huntress_attack1_range_nonzero():
    w, h = HUNTRESS_DATA.attack_1_range
    assert w >= MIN_ATTACK_RANGE and h >= MIN_ATTACK_RANGE, (
        f"Huntress attack1 range {[w, h]} is too small to land hits"
    )


def test_huntress_attack2_range_nonzero():
    w, h = HUNTRESS_DATA.attack_2_range
    assert w >= MIN_ATTACK_RANGE and h >= MIN_ATTACK_RANGE, (
        f"Huntress attack2 range {[w, h]} is too small to land hits"
    )


def test_old_wizard_attack1_range_nonzero():
    w, h = OLD_WIZARD_DATA.attack_1_range
    assert w >= MIN_ATTACK_RANGE and h >= MIN_ATTACK_RANGE, (
        f"Old Wizard attack1 range {[w, h]} is too small to land hits"
    )


def test_old_wizard_attack2_range_nonzero():
    w, h = OLD_WIZARD_DATA.attack_2_range
    assert w >= MIN_ATTACK_RANGE and h >= MIN_ATTACK_RANGE, (
        f"Old Wizard attack2 range {[w, h]} is too small to land hits"
    )
