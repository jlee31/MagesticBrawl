import pygame
from settings import *
from playerData import *

class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scaling = data[1]
        self.offset = data[2]
        self.speed = data[3]
        self.jump_height = data[4]
        self.flip = flip
        self.sprite_animation_sheet = self.loadImages(sprite_sheet, animation_steps)
        self.action = 0 
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
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
    
        

    def loadImages(self, sprite_sheet, sprite_animation_sheet):
        animation_list = []
        for y, animation in enumerate(sprite_animation_sheet):
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
            if keys[pygame.K_UP]:
                self.direction.y = -1
                dy -= self.speed
                self.jump -= self.jump_height
            if keys[pygame.K_DOWN]:
                self.direction.y = -1
                dy += self.speed
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                dx -= self.speed
                self.running = True
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                dx += self.speed
                self.running = True
            if keys[pygame.K_m]:
                self.attack(target=target)
                self.attack_type = 1
            if keys[pygame.K_n]:
                self.attack(target=target)
                self.attack_type = 2

        if self.player == 2:
            if keys[pygame.K_w]:
                self.direction.y = -1
                dy -= self.speed
                self.jump -= self.jump_height
            if keys[pygame.K_s]:
                self.direction.y = -1
                dy += self.speed
            if keys[pygame.K_a]:
                self.direction.x = -1
                dx -= self.speed
                self.running = True
            if keys[pygame.K_d]:
                self.direction.x = 1
                dx += self.speed
                self.running = True
            if keys[pygame.K_e]:
                self.attack(target=target)
                self.attack_type = 1
            if keys[pygame.K_r]:
                self.attack(target=target)
                self.attack_type = 2

        # Gravity

        self.jump += GRAVITY
        dy += self.jump

        # Ensuring players stay within the screen
        if self.rect.bottom + dy > SCREEN_HEIGHT - 110:
            self.jump = 0
            self.jumping = False
            dy = SCREEN_HEIGHT - 110 - self.rect.bottom

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
        pass

    def attack(self, target):
        pass

    def updateAction(self):
        pass

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
