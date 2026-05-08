import os
import pygame
import unittest.mock as mock
from src.playerData import WARRIOR_DATA, P1_CONTROLS, P2_CONTROLS

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((960, 500))

def make_fighter(player_num, x, y, flip, controls):
    from src.player import Fighter2
    size = WARRIOR_DATA.size  # 162
    steps = [10, 8, 1, 7, 7, 3, 7]
    # Solid-color sheet so every pixel is opaque and masks are fully filled
    sheet = pygame.Surface((size * max(steps), size * len(steps)))
    sheet.fill((200, 200, 200))
    sound = mock.MagicMock()
    return Fighter2(player_num, x, y, flip, WARRIOR_DATA, sheet, steps, sound, controls)


def test_check_attack_hit_exists():
    """Fighter2 must expose check_attack_hit as a separate method."""
    from src.player import Fighter2
    assert hasattr(Fighter2, "check_attack_hit"), (
        "Fighter2 must have a check_attack_hit() method for per-frame hit detection"
    )


def test_hit_lands_mid_animation():
    """A hit must register when check_attack_hit is called mid-animation (frame > 0)."""
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS)
    target = make_fighter(2, 350, 280, True, P2_CONTROLS)

    # Simulate mid-attack state (as if the attack started a few frames ago)
    attacker.attacking = True
    attacker.attack_type = 1
    attacker.action = 3       # attack1 animation index
    attacker.frame_index = 3  # mid-animation, not frame 0

    initial_health = target.health

    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)

    assert target.health < initial_health, (
        "Hit should register when check_attack_hit() is called mid-animation"
    )


def test_same_attack_cannot_hit_twice():
    """The same attack instance must not deal damage more than once to the same target."""
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS)
    target = make_fighter(2, 350, 280, True, P2_CONTROLS)

    attacker.attacking = True
    attacker.attack_type = 1
    attacker.action = 3
    attacker.frame_index = 2

    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
        health_after_first = target.health
        attacker.check_attack_hit(surface, target)
        health_after_second = target.health

    assert health_after_first == health_after_second, (
        "Same attack must not deal damage twice to the same target"
    )
