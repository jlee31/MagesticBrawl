import pygame

from src.level import Level
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Magestic Brawl")
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.FPS = 60

    def run(self):
        while True:
            dt = self.clock.tick(self.FPS) / 1000.0
            events = pygame.event.get()

            self.level.moveScreen()
            self.level.drawBg()
            self.level.drawGround()
            self.level.run(dt, events)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
