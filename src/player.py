import pygame
from src.settings import SCREEN_HEIGHT
from src.settings import SCREEN_WIDTH
from src.particles import spawn_exploding_particles

class Fighter2():
    def __init__(self, player, start_x, start_y, flip, data, sprite_sheet, sprite_animation_sheet, swing_sound, controls):
        # Player Creation
        self.player = player
        
        # Masks 
        self.player_mask = None
        self.mask_image = None           

        # Character properties
        self.size = data.size
        self.image_scale = data.scale
        self.offset = data.offset
        self.player_speed = data.speed
        self.player_jump_height = data.jump_height
        self.cell_width = data.cell_width if data.cell_width else data.size
        self.attack_one_data = data.attack_1_range
        self.attack_two_data = data.attack_2_range
        self.attack_one_offset = data.attack_offset
        self.attack_two_offset = data.attack_2_offset
        self.attack_one_active_frames = data.attack_1_active_frames
        self.attack_two_active_frames = data.attack_2_active_frames
        
        # Animation system
        self.animation_list = self.loadImages(sprite_sheet, sprite_animation_sheet)
        self.action = 0  # 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:hit, 6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        
        # Set up initial mask after image is loaded
        self.updateMask()
        
        # Physics & movement
        self.rect = pygame.Rect((start_x, start_y, 80, 180))
        self.vel_y = 0
        self.flip = flip
        
        # State flags
        self.is_jumping = False
        self.is_running = False
        self.attacking = False
        self.is_hit = False
        self.is_dead = False
        self.is_blocking = False
        
        # Combat system
        # attack_type is a per-frame keypress signal (reset to 0 every
        # move()). active_attack_type persists for the whole swing so
        # hit detection works on the active frames, not just frame 0.
        self.attack_type = 0
        self.active_attack_type = 0
        self.attack_cooldown = 0
        self.health = 100
        self.heavy_attack_cooldown = 180
        self.heavy_attack_max_cooldown = 180

        self.hitstop_frames = 0
        
        # Attack hit tracking - NEW: Track which attacks have already hit
        self.current_attack_id = 0  # Unique ID for each attack
        self.attack_hit_targets = set()  # Set of targets hit by current attack

        # Effects
        self.clock = pygame.time.Clock()
        self.particle_group = pygame.sprite.Group()
        self.floating_particle_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.floating_particle_timer, 10)

        # music / audio
        self.swing_sound = swing_sound

        # controls
        self.controls = controls

        # knockback
        self.knockback_velocity = 0
        self.knockback_frames = 0

        # screen shake
        self.screen_shake_trigger = False
    
    def loadImages(self, sprite_sheet, sprite_animation_sheet):
        animation_list = []
        for y, animation in enumerate(sprite_animation_sheet):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.cell_width, y * self.size, self.cell_width, self.size)
                scaled_image = pygame.transform.scale(temp_img, (self.cell_width * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(scaled_image)
            animation_list.append(temp_img_list)

        return animation_list
    
    def move(self, target, virtual_keys=None):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.is_running = False
        self.is_blocking = False
        self.attack_type = 0

        # Resolve inputs: real keyboard for humans, virtual_keys for the AI.
        # Both produce the same {action: bool} shape so the rest of move()
        # (gravity, flip, bounds clamping) runs identically for either.
        if virtual_keys is None:
            key = pygame.key.get_pressed()
            pressed = {action: bool(key[keycode]) for action, keycode in self.controls.items()}
        else:
            pressed = virtual_keys

        if self.hitstop_frames > 0:
            self.hitstop_frames -= 1
            return

        if self.attacking is False and not self.is_dead:
            # Movement
            if pressed.get("left"):
                dx = -SPEED
                self.is_running = True
            if pressed.get("right"):
                dx = SPEED
                self.is_running = True
            if pressed.get("jump") and not self.is_jumping:
                self.vel_y = -30
                self.is_jumping = True

            # Attacking
            if pressed.get("attack1"):
                self.attack_type = 1
                self.attack()
            if pressed.get("attack2"):
                self.attack_type = 2
                self.attack()

            # Blocking
            if pressed.get("block"):
                self.is_blocking = True

        # Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        # Keeping Players on the Ground
        if self.rect.bottom + dy > SCREEN_HEIGHT - 45:
            self.vel_y = 0
            dy = SCREEN_HEIGHT - 45 - self.rect.bottom
            self.is_jumping = False

        # Facing Each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.heavy_attack_cooldown < self.heavy_attack_max_cooldown:
            self.heavy_attack_cooldown += 1
        
        # Update Position
        self.rect.x += dx
        self.rect.y += dy

        # Applying Knockback Frames
        if self.knockback_frames > 0:
            self.rect.x += self.knockback_velocity
            self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
            self.knockback_frames -= 1
   
    def attack(self):
        if self.attack_type == 2 and self.heavy_attack_cooldown < self.heavy_attack_max_cooldown:
            return
        if self.attack_cooldown == 0 and not self.attacking:
            self._start_attack()

    def _start_attack(self):
        self.attacking = True
        # Capture the attack type now (keypress frame); attack_type gets
        # cleared next frame, so the swing relies on this persistent copy.
        self.active_attack_type = self.attack_type
        self.attack_cooldown = 50
        if self.attack_type == 2:
            self.heavy_attack_cooldown = 0
        self.swing_sound.play()
        self.current_attack_id += 1
        self.attack_hit_targets.clear()

    def check_attack_hit(self, surface, target):
        if not self.attacking:
            return

        if self.active_attack_type == 1:
            attack_data = self.attack_one_data
            active_frames = self.attack_one_active_frames
        elif self.active_attack_type == 2:
            attack_data = self.attack_two_data
            active_frames = self.attack_two_active_frames
        else:
            return

        # Hitbox is live only on the designated attack frames. An empty
        # list means "every attack frame" (legacy characters). This gate
        # is the heart of RL-stable hit detection: the outcome depends
        # only on (attack_type, frame_index), never on sprite pixels or
        # wall-clock timing.
        if self.action not in (3, 4):
            return
        if active_frames and self.frame_index not in active_frames:
            return

        attack_width, attack_height = attack_data
        offset = self.attack_one_offset if self.active_attack_type == 1 else self.attack_two_offset

        # Anchor the hitbox at the attacker's FRONT EDGE, extending away
        # from the body in the facing direction. This makes attack_*_range
        # mean actual forward reach (no half-box wasted inside the body).
        # offset[0] adds extra forward reach; offset[1] nudges it
        # vertically (positive = down).
        if self.flip:  # facing left -> extend left from the left edge
            attack_x = self.rect.left - attack_width - offset[0]
        else:           # facing right -> extend right from the right edge
            attack_x = self.rect.right + offset[0]
        attack_y = self.rect.centery - attack_height // 2 + offset[1]

        attacking_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)

        pygame.draw.rect(surface, (255, 0, 0), attacking_rect, 2)

        # Deterministic rect-vs-rect collision: O(1), reproducible, and
        # independent of per-pixel sprite content. No mask overlap.
        if not attacking_rect.colliderect(target.rect):
            return

        target_id = id(target)
        if target_id in self.attack_hit_targets:
            return

        # Hit point = centre of the overlap region, so particles spawn at
        # the contact area (deterministic, no head-spawn fallback).
        hit_point = attacking_rect.clip(target.rect).center

        if target.is_blocking:
            target.takeDamage(1)
            target.is_hit = True
        else:
            target.takeDamage(2)
            target.is_hit = True

        if self.active_attack_type == 2:
            self.screen_shake_trigger = True

        spawn_exploding_particles(n=1000, particle_group=self.particle_group, pos=hit_point)

        knockback = -15 if self.flip else 15
        target.knockback_velocity = knockback
        target.knockback_frames = 5

        self.hitstop_frames = 15
        target.hitstop_frames = 15

        self.attack_hit_targets.add(target_id)

    def takeDamage(self, type):
        if type == 1:
            self.health -= 10 * 0.3
        if type == 2:
            self.health -= 10 #50 for testing, 10 regular
                
    def draw(self, surface, shake_offset=(0, 0)):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.x - (self.offset[0] * self.image_scale) + shake_offset[0]
        draw_y = self.rect.y - (self.offset[1] * self.image_scale) + shake_offset[1]
        if self.is_blocking:
            img = img.copy()
            img.fill((0, 80, 255, 0), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(img, (draw_x, draw_y))
        
        # Draw hitbox (for debugging)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw Mask
        if self.mask_image:
            mask_surface = pygame.transform.flip(self.mask_image, self.flip, False)
            surface.blit(mask_surface, (draw_x, draw_y))
    
    def animation_update(self):
        self.updateAction()
        self.updateFrame()
        self.handleAnimationComplete()
    
    def updateAction(self):
        if self.health <= 0:
            self.is_dead = True
            self.update_action(6)  # Death
        elif self.is_hit:
            self.update_action(5)  # Hit
        elif self.attacking:
            if self.active_attack_type == 1:
                self.update_action(3)  # Attack 1
            elif self.active_attack_type == 2:
                self.update_action(4)  # Attack 2
        elif self.is_jumping:
            self.update_action(2)  # Jump
        elif self.is_running:
            self.update_action(1)  # Run
        else:
            self.update_action(0)  # Idle
    
    def updateFrame(self):
        animation_cooldown = 50
        # Get current frame image
        self.image = self.animation_list[self.action][self.frame_index]
        
        # Update mask for current frame
        self.updateMask()
        
        # Check for attack collisions during attack animations
        if self.attacking and self.action in [3, 4]:  # Attack 1 or Attack 2
            pass  # We'll handle collisions in a separate method
        
        # Update frame index based on time
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
    
    def handleAnimationComplete(self):
        """Handle what happens when an animation completes"""
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 6 and self.is_dead:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
            if self.action in [3, 4]:  # Attack animations
                self.attacking = False
                self.active_attack_type = 0
                # Reset cooldown when attack animation completes
                self.attack_cooldown = 0
                # NEW: Reset hit tracking when attack animation ends
                self.attack_hit_targets.clear()
            if self.action == 5:  # Hit animation
                self.is_hit = False
                self.attacking = False
                # Reset cooldown when hit animation completes
                self.attack_cooldown = 0
            if self.action == 6:
                self.is_dead = True
    
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def updateMask(self):
        if self.image is not None:
            # Create mask from current frame image
            self.player_mask = pygame.mask.from_surface(self.image)
            # Create a surface representation of the mask (useful for debugging)
            # self.mask_image = self.player_mask.to_surface(setcolor=(255, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
    
    def getMask(self):
        return self.player_mask

    def rectOverlapMask(self, rect, mask, mask_x, mask_y):
        # Create a mask from the attacking rectangle
        attack_mask = pygame.mask.Mask((rect.width, rect.height))
        attack_mask.fill()  # Fill the entire attack mask
        
        # Calculate offset between attack rect and target mask
        offset_x = rect.x - mask_x
        offset_y = rect.y - mask_y
        
        # Use pygame's built-in mask collision detection.
        # overlap() returns the collision point in the target mask's
        # local coordinate space (or None if there is no overlap).
        collision_point = mask.overlap(attack_mask, (offset_x, offset_y))

        # Convert the local collision point back to screen coordinates so
        # particles spawn at the actual pixel that was hit.
        if collision_point:
            return (mask_x + collision_point[0], mask_y + collision_point[1])
        # No collision occured
        return None

