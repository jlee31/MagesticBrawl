# DISCLAIMER: THIS IS NOT MY ORIGINAL CODE
# comes from https://www.youtube.com/watch?v=8SzTzvrWaAA&ab_channel=ClearCode
# i just edited it a bit
import pygame
gui_font = pygame.font.Font("assets/fonts/turok.ttf",30)
class Button:
	def __init__(self,text,width,height,pos,elevation):
		#Core attributes 
		self.pressed = False
		self.elevation = elevation
		self.dynamic_elecation = elevation
		self.original_y_pos = pos[1]

		# top rectangle 
		self.top_rect = pygame.Rect(pos,(width,height))
		self.top_color = (0,0,0)

		# bottom rectangle 
		self.bottom_rect = pygame.Rect(pos,(width,height))
		self.bottom_color = (0,0,0)
		#text
		self.text_surf = gui_font.render(text,True,'#FFFFFF')
		self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

	def draw(self, screen, game_state):
		# elevation logic 
		self.top_rect.y = self.original_y_pos - self.dynamic_elecation
		self.text_rect.center = self.top_rect.center 

		self.bottom_rect.midtop = self.top_rect.midtop
		self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

		pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
		pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
		screen.blit(self.text_surf, self.text_rect)
		self.check_click(game_state)

	def check_click(self, game_state):
		mouse_pos = pygame.mouse.get_pos()
		if self.top_rect.collidepoint(mouse_pos):
			self.top_color = '#2b2b28'
			if pygame.mouse.get_pressed()[0]:
				self.dynamic_elecation = 0
				self.pressed = True
			else:
				self.dynamic_elecation = self.elevation
				if self.pressed == True:
					self.pressed = False
					# Handle button click based on button text and current game state
					self.handle_button_action(game_state)
		else:
			self.dynamic_elecation = self.elevation
			self.top_color = '#4f0c0c'
	
	def handle_button_action(self, game_state):
		# This method will be overridden by each button instance
		# For now, just print the button text
		print(f'Button "{self.text_surf}" clicked in state: {game_state}')