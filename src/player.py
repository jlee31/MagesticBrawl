import pygame
from src.settings import *
from src.playerData import *

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
            
            # NEW: Generate new attack ID and reset hit tracking
            self.current_attack_id += 1
            self.attack_hit_targets.clear()

        # Create attack hitbox rectangle
        attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)

        # Get target mask
        target_mask = target.getMask()

        if target_mask:
            # Check if the attacking rectangle overlaps with the target mask
            if self._rectOverlapsMask(attacking_rect, target_mask, target.rect.x, target.rect.y):
                # Check if this target has already been hit by the current attack
                target_id = id(target)
                if target_id not in self.attack_hit_targets:
                    # Hit occurred! Deal damage and set hit state
                    target.health -= 10
                    target.is_hit = True
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
            self.mask_image = self.player_mask.to_surface(setcolor=(255, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
    
    def getMask(self):
        """Get the current collision mask"""
        return self.player_mask

    def _rectOverlapsMask(self, rect, mask, mask_x, mask_y):
        """
        Check if a rectangle overlaps with a mask
        This is a simple collision check between rect and mask
        """
        # Get the mask's bounding rectangle
        mask_rect = pygame.Rect(mask_x, mask_y, mask.get_size()[0], mask.get_size()[1])
        
        # First check if rectangles overlap (fast check)
        if not rect.colliderect(mask_rect):
            return False
        
        # If rectangles overlap, check if any pixels in the rect area are solid in the mask
        # Calculate the overlap area
        overlap_left = max(rect.left, mask_rect.left)
        overlap_top = max(rect.top, mask_rect.top)
        overlap_right = min(rect.right, mask_rect.right)
        overlap_bottom = min(rect.bottom, mask_rect.bottom)
        
        # Check if there's any overlap
        if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
            return False
        
        # For simplicity, if rectangles overlap, consider it a hit
        # This is a basic collision - you can make it more precise if needed
        return True

'''
HIT ANIMATION CALL STACK:

1. ATTACK TRIGGERED:
   - Player presses attack key (R/T for Player 1, O/P for Player 2)
   - move() method calls attack() method
   - attack() sets self.attacking = True and self.attack_type = 1 or 2

2. ATTACK ANIMATION STARTS:
   - updateAction() detects self.attacking = True
   - Calls update_action(3) for Attack 1 or update_action(4) for Attack 2
   - Animation changes to attack pose (action 3 or 4)

3. COLLISION DETECTION (EVERY FRAME):
   - level.py run() method calls checkAttackCollision() every frame
   - checkAttackCollision() checks if masks overlap
   - If collision occurs: target.health -= 10 and target.is_hit = True

4. HIT ANIMATION TRIGGERED:
   - Target's updateAction() detects self.is_hit = True
   - Calls update_action(5) to start hit animation
   - Animation changes to hit pose (action 5)

5. HIT ANIMATION PLAYS:
   - updateFrame() shows hit animation frames
   - handleAnimationComplete() waits for hit animation to finish

6. HIT ANIMATION ENDS:
   - When frame_index reaches end of hit animation
   - handleAnimationComplete() sets self.is_hit = False
   - Character returns to normal state (idle, run, etc.)

KEY FUNCTIONS IN ORDER:
   move() → attack() → updateAction() → update_action(3/4) → 
   checkAttackCollision() → target.is_hit = True → 
   target.updateAction() → target.update_action(5) → 
   target.handleAnimationComplete() → target.is_hit = False
'''