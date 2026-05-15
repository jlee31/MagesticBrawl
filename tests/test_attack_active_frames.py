"""Deterministic hit-detection tests for the RL-stable attack model.

These pin behaviour that the RL environment depends on:
  * the hitbox is live ONLY on the designated active frames,
  * collision is rect-vs-rect (no per-pixel/timing nondeterminism),
  * the hitbox is placed in front of the attacker for both facings.
"""
import os
import pygame
import unittest.mock as mock

from src.playerData import CHARACTER_DATA, P1_CONTROLS, P2_CONTROLS

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((960, 500))

# WARRIOR-like data, but with an explicit active-frame window on attack 1.
ACTIVE_FRAME = 3
STEPS = [10, 8, 1, 7, 7, 3, 7]  # idle,run,jump,atk1,atk2,hit,death
SIZE = 162


def make_data(active_frames):
    return CHARACTER_DATA(
        size=SIZE, scale=4, offset=[72, 56], speed=10, jump_height=30,
        attack_1_range=[200, 200], attack_2_range=[200, 150],
        attack_offset=[0, 0],
        attack_1_active_frames=active_frames,
    )


def make_fighter(player_num, x, y, flip, controls, active_frames):
    from src.player import Fighter2
    sheet = pygame.Surface((SIZE * max(STEPS), SIZE * len(STEPS)))
    sheet.fill((200, 200, 200))  # fully opaque: irrelevant now (rect-vs-rect)
    sound = mock.MagicMock()
    return Fighter2(player_num, x, y, flip, make_data(active_frames),
                    sheet, STEPS, sound, controls)


def _arm(attacker, frame_index, flip=False):
    # Mirrors the real mid-swing state: attack_type is a per-frame keypress
    # signal (0 after frame 0); active_attack_type persists for the swing.
    attacker.attacking = True
    attacker.attack_type = 0
    attacker.active_attack_type = 1
    attacker.action = 3
    attacker.frame_index = frame_index
    attacker.flip = flip


def test_hit_only_on_active_frame():
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS, [ACTIVE_FRAME])
    target = make_fighter(2, 350, 280, True, P2_CONTROLS, [ACTIVE_FRAME])

    _arm(attacker, ACTIVE_FRAME)
    start = target.health
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
    assert target.health < start, "hit must register on an active frame"


def test_no_hit_on_windup_frame():
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS, [ACTIVE_FRAME])
    target = make_fighter(2, 350, 280, True, P2_CONTROLS, [ACTIVE_FRAME])

    _arm(attacker, ACTIVE_FRAME - 1)  # windup, hitbox not yet live
    start = target.health
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
    assert target.health == start, "no damage during a non-active (windup) frame"


def test_hitbox_is_in_front_when_facing_right():
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS, [ACTIVE_FRAME])
    behind = make_fighter(2, 20, 280, True, P2_CONTROLS, [ACTIVE_FRAME])

    _arm(attacker, ACTIVE_FRAME, flip=False)  # facing right
    start = behind.health
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, behind)
    assert behind.health == start, "facing right must not hit a target behind (left)"


def test_hitbox_is_in_front_when_facing_left():
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, True, P1_CONTROLS, [ACTIVE_FRAME])
    in_front = make_fighter(2, 60, 280, False, P2_CONTROLS, [ACTIVE_FRAME])
    behind = make_fighter(2, 350, 280, False, P2_CONTROLS, [ACTIVE_FRAME])

    _arm(attacker, ACTIVE_FRAME, flip=True)  # facing left
    with mock.patch("src.player.spawn_exploding_particles"):
        s1 = in_front.health
        attacker.check_attack_hit(surface, in_front)
        assert in_front.health < s1, "facing left must hit a target to the left"

        attacker.attack_hit_targets.clear()
        s2 = behind.health
        attacker.check_attack_hit(surface, behind)
        assert behind.health == s2, "facing left must not hit a target behind (right)"


def test_hit_lands_after_keypress_frame_via_full_lifecycle():
    """Regression: the swing must still deal damage on its active frames
    even though attack_type is reset to 0 the frame after the keypress.

    This drives the real lifecycle: set attack_type + _start_attack()
    (keypress frame), then simulate attack_type going back to 0 while the
    animation advances to an active frame.
    """
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS, [ACTIVE_FRAME])
    target = make_fighter(2, 350, 280, True, P2_CONTROLS, [ACTIVE_FRAME])

    # Keypress frame
    attacker.attack_type = 1
    attacker._start_attack()
    attacker.action = 3
    attacker.frame_index = 0

    # Frame after keypress: move() would reset this to 0 in the real loop
    attacker.attack_type = 0

    # Frame 0 is not active -> no damage yet
    start = target.health
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
    assert target.health == start, "no hit on the (inactive) keypress frame"

    # Animation advances to the active frame -> hit must land
    attacker.frame_index = ACTIVE_FRAME
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
    assert target.health < start, (
        "hit must land on the active frame even though attack_type is now 0"
    )


def test_empty_active_frames_is_legacy_all_frames():
    """Characters with no active-frame data keep the old 'always live' behaviour."""
    surface = pygame.display.get_surface()
    attacker = make_fighter(1, 200, 280, False, P1_CONTROLS, [])
    target = make_fighter(2, 350, 280, True, P2_CONTROLS, [])

    _arm(attacker, 5)  # arbitrary frame; empty list => every frame active
    start = target.health
    with mock.patch("src.player.spawn_exploding_particles"):
        attacker.check_attack_hit(surface, target)
    assert target.health < start, "empty active_frames => hitbox live on every frame"
