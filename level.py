import pygame 
from settings import *
from player import *

class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        self.bgImages = []
        for i in range(1,6):
            image = pygame.image.load(f'assets/images/background/plx-{i}.png').convert_alpha()
            scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bgImages.append(scaled_image)
        self.bgWidth = self.bgImages[0].get_width()
        self.scroll = 0

    def run(self, dt):
        pass

    def drawBg(self):
        for x in range(5):
            for i in self.bgImages:
                self.display_surface.blit(i, ((x * self.bgWidth) - self.scroll, 0))

    def moveScreen(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.scroll -= 5
        if key[pygame.K_RIGHT]:
            self.scroll += 5
               
    def drawHealthBar(self):
        pass
    

    def drawText(self):
        pass

