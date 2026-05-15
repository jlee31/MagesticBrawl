# ! Load Character Data
from dataclasses import dataclass, field
from pygame.locals import K_a, K_d, K_w, K_r, K_t, K_j, K_l, K_i, K_o, K_p, K_s, K_k

@dataclass
class CHARACTER_DATA:
    size: int
    scale: int
    offset: list
    speed: int
    jump_height: int
    attack_1_range: list
    attack_2_range: list
    attack_offset: list
    cell_width: int = 0  # 0 means square (same as size)
    attack_2_offset: list = field(default_factory=lambda: [0, 0])
    # Frame indices (into the attack animation) on which the hitbox is
    # live. Empty list = every attack frame is active (legacy behaviour).
    # Deterministic by design: hit outcome depends only on frame_index,
    # never on per-pixel sprite content or wall-clock timing.
    attack_1_active_frames: list = field(default_factory=list)
    attack_2_active_frames: list = field(default_factory=list)

P1_CONTROLS = {"left": K_a, "right": K_d, "jump": K_w, "attack1": K_r, "attack2": K_t, "block": K_s}
P2_CONTROLS = {"left": K_j, "right": K_l, "jump": K_i, "attack1": K_o, "attack2": K_p, "block": K_k}

# Warrior 
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_SPEED = 10
WARRIOR_JUMP_HEIGHT = 30
WARRIOR_ATTACK1_RANGE = [200,200] # [x, y, damage] <- add damage after
WARRIOR_ATTACK2_RANGE = [200,150]
WARRIOR_ATTACK_OFFSET = [0,0]
WARRIOR_DATA = CHARACTER_DATA(WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET, WARRIOR_SPEED, WARRIOR_JUMP_HEIGHT, WARRIOR_ATTACK1_RANGE, WARRIOR_ATTACK2_RANGE, WARRIOR_ATTACK_OFFSET)
# Sorcerer SORCERER
SORCERER_SIZE = 250
SORCERER_SCALE = 3
SORCERER_OFFSET = [112, 110]
SORCERER_SPEED = 5
SORCERER_JUMP_HEIGHT = 30
SORCERER_ATTACK1_RANGE = [100,300]
SORCERER_ATTACK2_RANGE = [250,400]
SORCERER_ATTACK_OFFSET = [0,0]
# attack1 = 8 frames (sorcerer_animation_steps[3]); the blast is visible
# ~frames 5-6. Tune these here if the active window feels off.
SORCERER_ATTACK1_ACTIVE_FRAMES = [5, 6]
SORCERER_ATTACK2_ACTIVE_FRAMES = [5, 6]
SORCERER_DATA = CHARACTER_DATA(SORCERER_SIZE, SORCERER_SCALE, SORCERER_OFFSET, SORCERER_SPEED, SORCERER_JUMP_HEIGHT, SORCERER_ATTACK1_RANGE, SORCERER_ATTACK2_RANGE, SORCERER_ATTACK_OFFSET, attack_1_active_frames=SORCERER_ATTACK1_ACTIVE_FRAMES, attack_2_active_frames=SORCERER_ATTACK2_ACTIVE_FRAMES)
# Huntress
HUNTRESS_SIZE = 150
HUNTRESS_SCALE = 4
# Centred on the idle-frame opaque bbox (measured from huntress.png).
# Best-effort: the fixed 80px box is narrower than the ~128px scaled
# body and this bbox includes the spear. Proper fix tracked in issue.
HUNTRESS_OFFSET = [67, 52]
HUNTRESS_SPEED = 12
HUNTRESS_JUMP_HEIGHT = 30
HUNTRESS_ATTACK1_RANGE = [200,200]
HUNTRESS_ATTACK2_RANGE = [300,300]
HUNTRESS_ATTACK_OFFSET = [0,0]
HUNTRESS_DATA = CHARACTER_DATA(HUNTRESS_SIZE, HUNTRESS_SCALE, HUNTRESS_OFFSET, HUNTRESS_SPEED, HUNTRESS_JUMP_HEIGHT, HUNTRESS_ATTACK1_RANGE, HUNTRESS_ATTACK2_RANGE, HUNTRESS_ATTACK_OFFSET)
# Old Wizard
OLD_WIZARD_SIZE = 190
OLD_WIZARD_CELL_WIDTH = 231
OLD_WIZARD_SCALE = 2
# Centred on the idle-frame opaque bbox (measured from old-wizard.png).
# Best-effort: the fixed 80px box is narrower than the ~114px scaled
# body and this bbox includes the staff. Proper fix tracked in issue.
OLD_WIZARD_OFFSET = [90, 51]
OLD_WIZARD_SPEED = 8
OLD_WIZARD_JUMP_HEIGHT = 30
OLD_WIZARD_ATTACK1_RANGE = [200,150]
OLD_WIZARD_ATTACK2_RANGE = [250,200]
OLD_WIZARD_ATTACK_OFFSET = [0,0]
OLD_WIZARD_DATA = CHARACTER_DATA(OLD_WIZARD_SIZE, OLD_WIZARD_SCALE, OLD_WIZARD_OFFSET, OLD_WIZARD_SPEED, OLD_WIZARD_JUMP_HEIGHT, OLD_WIZARD_ATTACK1_RANGE, OLD_WIZARD_ATTACK2_RANGE, OLD_WIZARD_ATTACK_OFFSET, OLD_WIZARD_CELL_WIDTH)
