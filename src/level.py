import pygame 
from src.settings import *
from src.player import *

class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # Background Stuff
        self.bgImages = []
        for i in range(1,6):
            image = pygame.image.load(f'assets/images/background/plx-{i}.png').convert_alpha()
            scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bgImages.append(scaled_image)
        self.bgWidth = self.bgImages[0].get_width()
        self.scroll = 0

        self.ground_image = pygame.image.load(f'assets/images/background/ground.png').convert_alpha()
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

        # Load sprite sheets
        self.warrior_sheet = pygame.image.load('assets/images/warrior/warrior.png').convert_alpha()
        self.sorcerer_sheet = pygame.image.load('assets/images/sorcerer/Sprites/wizard.png').convert_alpha()
        self.huntress_sheet = pygame.image.load('assets/images/huntress/Idle.png').convert_alpha()
        self.old_wizard_sheet = pygame.image.load('assets/images/old-wizard/Idle.png').convert_alpha()

        # Animation steps for each character (number of frames in each animation)
        # [idle, run, jump, attack1, attack2, hit, death]
        self.warrior_animation_steps = [8, 8, 2, 6, 6, 4, 6]
        self.sorcerer_animation_steps = [8, 8, 2, 6, 6, 4, 6]
        self.huntress_animation_steps = [8, 8, 2, 6, 6, 4, 6]
        self.old_wizard_animation_steps = [8, 8, 2, 6, 6, 4, 6]

        # Create fighters
        self.fighter_1 = Fighter(1, 200, 1800, False, WARRIOR_DATA, self.warrior_sheet, self.warrior_animation_steps, None)
        self.fighter_2 = Fighter(2, 700, 1800, True, SORCERER_DATA, self.sorcerer_sheet, self.sorcerer_animation_steps, None)
        ground_level = SCREEN_HEIGHT - self.ground_height
        self.fighter_1.rect.bottom = ground_level
        self.fighter_2.rect.bottom = ground_level


    def run(self, dt):
        # Update fighters
        self.fighter_1.update()
        self.fighter_2.update()
        
        # Move fighters
        self.fighter_1.move(self.display_surface, self.fighter_2)
        self.fighter_2.move(self.display_surface, self.fighter_1)
        
        # Draw fighters
        self.fighter_1.draw(self.display_surface)
        self.fighter_2.draw(self.display_surface)

    def drawBg(self):
        for x in range(3):
            speed = 1
            for i in self.bgImages:
                self.display_surface.blit(i, ((x * self.bgWidth) - self.scroll * speed, 0))
                speed += 0.05

    def drawGround(self):
        for x in range(15):
            self.display_surface.blit(self.ground_image, ((x * self.ground_width - self.scroll * 2), SCREEN_HEIGHT - self.ground_height))

    def moveScreen(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.scroll -= 2
        if key[pygame.K_RIGHT]:
            self.scroll += 2
               
    def drawHealthBar(self):
        pass
    
    def drawText(self):
        pass

