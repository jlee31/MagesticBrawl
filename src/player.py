import pygame
from src.settings import *
from src.playerData import *

class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.speed = data[3]
        self.jump_height = data[4]
        self.flip = flip
        self.sprite_animation_sheet = self.loadImages(sprite_sheet, animation_steps)
        self.action = 0 
        self.frame_index = 0
        self.image = self.sprite_animation_sheet[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.jump = 0
        self.running = False
        self.jumping = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

        self.rect = self.image.get_rect(center = (x, y))
        self.direction = pygame.math.Vector2()
        self.position = pygame.math.Vector2(self.rect.center)       

    def loadImages(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, surface, target):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if self.player == 1:
            if keys[pygame.K_UP] and not self.jumping:
                self.jump = -self.jump_height
                self.jumping = True
            if keys[pygame.K_LEFT]:
                dx -= self.speed
                self.running = True
            if keys[pygame.K_RIGHT]:
                dx += self.speed
                self.running = True
            if keys[pygame.K_m] and not self.attacking:
                self.attack(target)
                self.attack_type = 1
            if keys[pygame.K_n] and not self.attacking:
                self.attack(target)
                self.attack_type = 2

        if self.player == 2:
            if keys[pygame.K_w] and not self.jumping:
                self.jump = -self.jump_height
                self.jumping = True
            if keys[pygame.K_a]:
                dx -= self.speed
                self.running = True
            if keys[pygame.K_d]:
                dx += self.speed
                self.running = True
            if keys[pygame.K_e] and not self.attacking:
                self.attack(target)
                self.attack_type = 1
            if keys[pygame.K_r] and not self.attacking:
                self.attack(target)
                self.attack_type = 2

        # Gravity
        self.jump += GRAVITY
        dy += self.jump

        # Ensuring players stay within the screen
        if self.rect.bottom + dy > SCREEN_HEIGHT + 500:
            self.jump = 0
            self.jumping = False

        # Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # Apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        # Check if player is alive
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.updateAction(6)  # Death animation
        elif self.hit:
            self.updateAction(5)  # Hit animation
        elif self.attacking:
            if self.attack_type == 1:
                self.updateAction(3)  # Attack1 animation
            elif self.attack_type == 2:
                self.updateAction(4)  # Attack2 animation
        elif self.jumping:
            self.updateAction(2)  # Jump animation
        elif self.running:
            self.updateAction(1)  # Run animation
        else:
            self.updateAction(0)  # Idle animation

        animation_cooldown = ANIMATION_COOLDOWN
        # Update image
        self.image = self.sprite_animation_sheet[self.action][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Check if the animation has finished
        if self.frame_index >= len(self.sprite_animation_sheet[self.action]):
            # If the player is dead then end the animation
            if self.alive == False:
                self.frame_index = len(self.sprite_animation_sheet[self.action]) - 1
            else:
                self.frame_index = 0
                # Check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # Check if damage was taken
                if self.action == 5:
                    self.hit = False
                    # If the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        pass

    def updateAction(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

