# DISCLAIMER: THIS IS NOT MY ORIGINAL CODE
# comes from https://www.youtube.com/watch?v=8SzTzvrWaAA&ab_channel=ClearCode
# i just edited it a bit
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.level import Level
import pygame
gui_font = pygame.font.Font("assets/fonts/turok.ttf",30)
class Button:
	def __init__(self,text,width,height,pos,elevation):
		#Core attributes
		self.pressed = False
		self.elevation = elevation
		self.level: Optional[Level] = None
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
				if self.pressed:
					self.pressed = False
					# Handle button click based on button text and current game state
					self.handle_button_action(game_state)
		else:
			self.dynamic_elecation = self.elevation
			self.top_color = '#4f0c0c'
	
	def handle_button_action(self, game_state):
		print(f'Button "{self.text_surf}" clicked in state: {game_state}')

class PlayButton(Button):
    def handle_button_action(self, game_state):
        if game_state == "main_screen":
            print("Starting game...")
            assert self.level
            self.level.game_state = "fighting"
            self.level.playing = True
            self.level.intro_count = 3
            self.level.last_count_update = pygame.time.get_ticks()

class ResumeButton(Button):
    def handle_button_action(self, game_state):
        if game_state == "pause":
            print("Resuming game...")
            assert self.level
            self.level.game_state = "fighting"
            self.level.playing = True

class SettingsButton(Button):
    def handle_button_action(self, game_state):
        if game_state == "main_screen" or game_state == "pause":
            print("Opening settings...")
            assert self.level
            self.level.game_state = "settings"

class BackButton(Button):
    def handle_button_action(self, game_state):
        if game_state == "settings":
            print("Going back...")
            assert self.level
            self.level.game_state = "main_screen"

class ExitButton(Button):
    def handle_button_action(self, game_state):
        import sys
        print("Exiting...")
        pygame.quit()
        sys.exit()

class VolumeButton(Button):
    def handle_button_action(self, game_state):
        print("Volume clicked")