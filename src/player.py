import pygame
from src.settings import *
from src.playerData import *

class Fighter2():
    def __init__(self, player, start_x, start_y, flip, data, sprite_sheet, sprite_animation_sheet):
        self.player = player

        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.animation_list = self.loadImages(sprite_sheet=sprite_sheet, sprite_animation_sheet=sprite_animation_sheet)
        self.action = 0 # 0 is idle, 1 is run, 2 is jump, 3 is attack, 4 is attack2, 5 is hit, 6 is death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
  
        self.rect = pygame.Rect((start_x,start_y,80,180))
        self.vel_y = 0
        self.is_jumping = False
        self.is_running = False
        self.attack_type = 0
        self.attacking = False
        self.flip = flip
        self.health = 100

        self.attack_cooldown = 0
        self.is_hit = False

        self.is_dead = False

        self.update_time = pygame.time.get_ticks()

    def loadImages(self, sprite_sheet, sprite_animation_sheet):
        animation_list = []
        for y, animation in enumerate(sprite_animation_sheet):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                # Scale the huge image down to a reasonable size
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
                # Movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.is_running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.is_running = True
                # Jump - only allow jumping when on ground
                if key[pygame.K_w] and not self.is_jumping:
                    self.vel_y = -30
                    self.is_jumping = True
                # Attacks
                if key[pygame.K_r]:
                    self.attack_type = 1 
                    self.attack(pygame.display.get_surface(), target)
                if key[pygame.K_t]:
                    self.attack_type = 2
                    self.attack(pygame.display.get_surface(), target)
            if self.player == 2:
                # Movement
                if key[pygame.K_j]:
                    dx = -SPEED
                    self.is_running = True
                if key[pygame.K_l]:
                    dx = SPEED
                    self.is_running = True
                # Jump - only allow jumping when on ground
                if key[pygame.K_i] and not self.is_jumping:
                    self.vel_y = -30
                    self.is_jumping = True
                # Attacks
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

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.is_hit = True

    def animation_update(self):
        # check which action - Fixed: use self.is_running instead of self.running
        if self.health <= 0:
            self.is_dead = True
            self.update_action(6)
        elif self.is_hit:
            self.update_action(5)
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3) 
            if self.attack_type == 2:
                self.update_action(4)
        elif self.is_jumping:
            self.update_action(2)
        elif self.is_running:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        # clock timer
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()  # Update the timer
            if self.frame_index >= len(self.animation_list[self.action]):
                # checking if dead
                if self.action == 6 and self.is_dead:
                    self.frame_index = len(self.animation_list[self.action]) - 1

                # Resetting the Frames
                self.frame_index = 0
                # checking attacks
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 50
                # checking if hit
                if self.action == 5:
                    self.is_hit = False
                    # stopping player if hes in the middle of an attack
                    self.attacking = False
                    self.attack_cooldown = 20


    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()