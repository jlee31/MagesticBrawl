import pygame 
from src.settings import *
from src.player import *

YELLOW = (255,255,0)
RED = (255,0,0)
WHITE = (255,255,255)

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

        # Sprite Sheets
        self.warrior_sheet = pygame.image.load("assets/images/warrior/warrior.png").convert_alpha()
        self.warrior_animation_steps = [10,8,1,7,7,3,7]
        self.sorcerer_sheet = pygame.image.load("assets/images/sorcerer/Sprites/wizard.png").convert_alpha()
        self.sorcerer_animation_steps = [8,8,1,8,8,3,7]

        # Players
        self.fighter_1 = Fighter2(1, 200,280, False, WARRIOR_DATA, self.warrior_sheet, self.warrior_animation_steps)
        self.fighter_2 = Fighter2(2, 400,280, True, SORCERER_DATA, self.sorcerer_sheet, self.sorcerer_animation_steps)

    
    def run(self, dt):
        self.fighter_1.move(target=self.fighter_2)
        self.fighter_2.move(target=self.fighter_1)
        self.fighter_1.animation_update()
        self.fighter_2.animation_update()
        self.fighter_1.draw(self.display_surface)
        self.fighter_2.draw(self.display_surface)

        # Player Stats
        self.drawHealthBar(self.fighter_1.health, 20, 20)
        self.drawHealthBar(self.fighter_2.health, 410,20)

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
        if key[pygame.K_LEFT] and self.scroll > 0:
            self.scroll -= 2
        if key[pygame.K_RIGHT] and self.scroll < 1000:
            self.scroll += 2

    def lockScreen(self):
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > 1000:
            self.scroll = 0
               
    def drawHealthBar(self, health, x, y):
        ratio = health / 100
        pygame.draw.rect(self.display_surface, WHITE, (x - 2,y - 2, 304, 34))
        pygame.draw.rect(self.display_surface, RED, (x,y, 300, 30) )
        pygame.draw.rect(self.display_surface, YELLOW, (x,y, 300 * ratio, 30))
    
    def drawText(self):
        pass

