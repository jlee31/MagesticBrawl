import pygame
from src.settings import *
from src.playerData import *
from src.particles import * 
from random import randint 
class Fighter2():
    def __init__(self, player, start_x, start_y, flip, data, sprite_sheet, sprite_animation_sheet):
        # Player Creation
        self.player = player
        
        # Masks 
        self.player_mask = None
        self.mask_image = None           

        # Character properties
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.player_speed = data[3]
        self.player_jump_height = data[4]
        self.attack_one_data = data[5]
        self.attack_two_data = data[6]
        self.attack_one_offset = data[7]
        
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
        
        # Combat system
        self.attack_type = 0
        self.attack_cooldown = 0
        self.health = 100
        
        # Attack hit tracking - NEW: Track which attacks have already hit
        self.current_attack_id = 0  # Unique ID for each attack
        self.attack_hit_targets = set()  # Set of targets hit by current attack

        # Effects
        self.clock = pygame.time.Clock()
        self.particle_group = pygame.sprite.Group()
        self.floating_particle_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.floating_particle_timer, 10)

        # music / audio
        self.sword_swing = pygame.mixer.Sound("assets/audio/sword_swing.wav")
        self.magic_swing = pygame.mixer.Sound("assets/audio/magic_swing.mp3")
    
    def loadImages(self, sprite_sheet, sprite_animation_sheet):
        animation_list = []
        for y, animation in enumerate(sprite_animation_sheet):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                scaled_image = pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(scaled_image)
            animation_list.append(temp_img_list)
        
        return animation_list
    
    def move(self, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.is_running = False
        self.attack_type = 0

        key = pygame.key.get_pressed()
        if self.attacking is False and not self.is_dead:
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.is_running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.is_running = True
                if key[pygame.K_w] and not self.is_jumping:
                    self.vel_y = -30
                    self.is_jumping = True
                if key[pygame.K_r]:
                    self.attack_type = 1 
                    self.attack(pygame.display.get_surface(), target)
                if key[pygame.K_t]:
                    self.attack_type = 2
                    self.attack(pygame.display.get_surface(), target)
            if self.player == 2:
                if key[pygame.K_j]:
                    dx = -SPEED
                    self.is_running = True
                if key[pygame.K_l]:
                    dx = SPEED
                    self.is_running = True
                if key[pygame.K_i] and not self.is_jumping:
                    self.vel_y = -30
                    self.is_jumping = True
                if key[pygame.K_o]:
                    self.attack_type = 1 
                    self.attack(pygame.display.get_surface(), target)
                if key[pygame.K_p]:
                    self.attack_type = 2
                    self.attack(pygame.display.get_surface(), target)
            
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
        
        # Update Position
        self.rect.x += dx
        self.rect.y += dy
       
    def attack(self, surface, target):
        # Only allow attack if not already attacking and cooldown is ready
        if self.attack_cooldown == 0 and not self.attacking:
            self.attacking = True
            # Set a short cooldown to prevent immediate re-attack
            self.attack_cooldown = 50
            if self.player == 1:
                self.sword_swing.play()
            else:
                self.magic_swing.play()
            
            # Generate new attack ID and reset hit tracking
            self.current_attack_id += 1
            self.attack_hit_targets.clear()

        # Create attack hitbox rectangle
        if self.attack_type == 1:
            attack_data = self.attack_one_data
        elif self.attack_type == 2:
            attack_data = self.attack_two_data
        else:
            return  # No valid attack type
       
        attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip + self.attack_one_offset[0]),  
                self.rect.y - self.attack_one_offset[1],
                attack_data[0],
                attack_data[1]
        )

        # Debug: Draw attack hitbox
        # pygame.draw.rect(surface, (255, 0, 0), attacking_rect, 2)
        
        # Get target mask and position
        target_mask = target.getMask()
        if target_mask:
            # Calculate target's actual position on screen (accounting for offset)
            target_draw_x = target.rect.x - (target.offset[0] * target.image_scale)
            target_draw_y = target.rect.y - (target.offset[1] * target.image_scale)
            
            # Check if the attacking rectangle overlaps with the target mask
            hit_point = self._rectOverlapsMask(attacking_rect, target_mask, target_draw_x, target_draw_y)
            if hit_point:
                # Check if this target has already been hit by the current attack
                target_id = id(target)
                if target_id not in self.attack_hit_targets:
                    # Hit occurred! Deal damage and set hit state
                    target.health -= 10
                    target.is_hit = True
                    # spawn_exploding_particles(n=1000, particle_group=self.particle_group, pos=hit_point)
                    print("HIT")
                    # Mark this target as hit by the current attack
                    self.attack_hit_targets.add(target_id)

    def takeDamage(self):
        self.health -= 10
                
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.x - (self.offset[0] * self.image_scale)
        draw_y = self.rect.y - (self.offset[1] * self.image_scale)
        surface.blit(img, (draw_x, draw_y))
        
        # Draw hitbox (for debugging)
        # pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
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
            if self.attack_type == 1:
                self.update_action(3)  # Attack 1
            elif self.attack_type == 2:
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
        """Update the collision mask for the current frame"""
        if self.image is not None:
            # Create mask from current frame image
            self.player_mask = pygame.mask.from_surface(self.image)
            # Create a surface representation of the mask (useful for debugging)
            # self.mask_image = self.player_mask.to_surface(setcolor=(255, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
    
    def getMask(self):
        """Get the current collision mask"""
        return self.player_mask

    def _rectOverlapsMask(self, rect, mask, mask_x, mask_y):
        """
        FIXED: Proper collision check between rectangle and mask
        """
        # Create a mask from the attacking rectangle
        attack_mask = pygame.mask.Mask((rect.width, rect.height))
        attack_mask.fill()  # Fill the entire attack mask
        
        # Calculate offset between attack rect and target mask
        offset_x = rect.x - mask_x
        offset_y = rect.y - mask_y
        
        # Use pygame's built-in mask collision detection
        collision_point = mask.overlap(attack_mask, (offset_x, offset_y))
        
        # Return True if there was a collision, False otherwise
        return collision_point

