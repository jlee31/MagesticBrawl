import pygame, sys
from src.settings import *
from src.level import Level

class Game:
	def __init__(self):
		pygame.init() 
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Magestic Brawl')
		self.clock = pygame.time.Clock()
		self.level = Level()
		self.FPS = 60
		self.dt = self.clock.tick(60) / 1000.0

	def run(self):
		while True:
			self.clock.tick(self.FPS)
			self.level.moveScreen()
  
			dt = self.clock.tick() / 1000
			self.level.drawBg()
			self.level.drawGround()
			self.level.run(self.dt)
			pygame.display.update()
			
if __name__ == '__main__':
	game = Game()
	game.run()

