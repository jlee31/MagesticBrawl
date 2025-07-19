import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self):
		pygame.init() 
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Magestic Brawl')
		self.clock = pygame.time.Clock()
		self.level = Level()

	def run(self):
		while True:
			self.level.moveScreen()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
  
			dt = self.clock.tick() / 1000
			self.level.drawBg()
			self.level.run(dt)
			pygame.display.update()
			
if __name__ == '__main__':
	game = Game()
	game.run()

