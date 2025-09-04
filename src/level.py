import pygame, sys
from src.settings import *
from src.player import *
from src.particles import spawn_exploding_particles

YELLOW = (255,255,0)
RED = (255,0,0)
WHITE = (255,255,255)


class Level:
    def __init__(self):
        self.playing = False
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_states = ["main_screen", "pause", "loading", "fighting", "settings"]
        self.game_state = self.game_states[0]

        self.intro_count = 3
        self.last_count_update = pygame.time.get_ticks()
        self.score = [0,0]
        self.round_complete = False
        self.round_over_cooldown = 2000
    

        self.countdown_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
        self.score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
        self.menu_font = pygame.font.Font("assets/fonts/turok.ttf", 100)
        self.menu_buttons_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

        # Background Stuff
        self.bgImages = []
        for i in range(1,6):
            image = pygame.image.load(f'assets/images/background/plx-{i}.png').convert_alpha()
            scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bgImages.append(scaled_image)
        self.bgWidth = self.bgImages[0].get_width()
        self.scroll = 0
        # Background movement toggle
        self.auto_scroll = True
        self.scroll_speed = 1

        self.ground_image = pygame.image.load(f'assets/images/background/ground.png').convert_alpha()
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

        # Sprite Sheets
        self.warrior_sheet = pygame.image.load("assets/images/warrior/warrior.png").convert_alpha()
        self.warrior_animation_steps = [10,8,1,7,7,3,7]
        self.sorcerer_sheet = pygame.image.load("assets/images/sorcerer/Sprites/wizard.png").convert_alpha()
        self.sorcerer_animation_steps = [8,8,1,8,8,3,7]


        # Images
        # Victory Image (will change later)
        self.victory_image = pygame.image.load("assets/images/victory.png").convert_alpha()

        # Players
        self.fighter_1 = Fighter2(1, 200, 280, False, WARRIOR_DATA, self.warrior_sheet, self.warrior_animation_steps)
        self.fighter_2 = Fighter2(2, 700, 280, True, SORCERER_DATA, self.sorcerer_sheet, self.sorcerer_animation_steps)
   
        
    def run(self, dt):
        # Handle pause key (Escape)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "fighting":
                        self.game_state = "pause"
                        self.playing = False
                        print("Game paused")
                    elif self.game_state == "pause":
                        self.game_state = "fighting"
                        print("Game resumed")
        
        # Draw background first
        self.drawBg()
        self.drawGround()
        
        # Draw fighters
        self.fighter_1.animation_update()
        self.fighter_2.animation_update()
        self.fighter_1.draw(self.display_surface)
        self.fighter_2.draw(self.display_surface)

        # Draw particles (draw them after fighters so they appear on top)
        self.fighter_1.particle_group.draw(self.display_surface)
        self.fighter_2.particle_group.draw(self.display_surface)

        # Draw countdown if needed
        if self.playing:
            if self.intro_count > 0:
                if (pygame.time.get_ticks() - self.last_count_update) >= 1000:
                    self.intro_count -= 1
                    self.last_count_update = pygame.time.get_ticks()
                    print(self.intro_count)
                # Draw countdown text
                countdown_text = str(self.intro_count) if self.intro_count > 0 else "FIGHT!"
                text_surface = self.countdown_font.render(countdown_text, True, (255,255,255))
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.display_surface.blit(text_surface, text_rect)
            else:
                # Only move fighters when countdown is done
                self.fighter_1.move(target=self.fighter_2)
                self.fighter_2.move(target=self.fighter_2)

        # Draw health bars last (on top of everything)
        self.drawHealthBar(self.fighter_1.health, 20, 20)
        self.drawHealthBar(self.fighter_2.health, 660, 20)

        # check defeat
        if self.round_complete == False:
            if self.fighter_1.is_dead:
                self.score[1] += 1
                self.round_complete = True
                self.round_over_time = pygame.time.get_ticks()
            elif self.fighter_2.is_dead:
                self.score[0] += 1
                self.round_complete = True
                self.round_over_time = pygame.time.get_ticks()
        else:
            # Display Victory Image
            self.display_surface.blit(self.victory_image, (500, 250))
            if pygame.time.get_ticks() - self.round_over_time > self.round_over_cooldown:
                self.round_complete = False
                self.intro_count = 3
                self.fighter_1 = Fighter2(1, 200, 280, False, WARRIOR_DATA, self.warrior_sheet, self.warrior_animation_steps)
                self.fighter_2 = Fighter2(2, 700, 280, True, SORCERER_DATA, self.sorcerer_sheet, self.sorcerer_animation_steps)
   
        # Menu / Options
        if self.game_state == "main_screen":
            self.home_screen()
        elif self.game_state == "pause":
            self.playing = False
            self.pause_menu()
        elif self.game_state == "settings":
            self.settings_menu()
        else:
            self.playing = True
            self.draw_text(f'{self.score[0]} : {self.score[1]}', self.score_font, (255,0,0), 480, 20)

    
    def home_screen(self):
        self.display_surface.fill((255,255,255))
        self.draw_text("Magestic Brawl", self.menu_font, (0,0,0), 130, 20)
        self.menu_buttons(state=self.game_state)

    def pause_menu(self):
        self.menu_buttons(state=self.game_state)

    def settings_menu(self):
        self.display_surface.fill((255,255,255))
        self.draw_text("Settings", self.menu_font, (0,0,0), 130, 20)
        self.menu_buttons(state=self.game_state)

    def menu_buttons(self, state):
        mx, my = pygame.mouse.get_pos()
        play_btn = pygame.Rect(SCREEN_WIDTH / 2 - 100, 150, 200, 50)
        settings_btn = pygame.Rect(SCREEN_WIDTH / 2 - 100 , 250, 200, 50)
        exit_btn = pygame.Rect(SCREEN_WIDTH / 2 - 100, 350, 200, 50)

        if state == "main_screen" or state == "pause":
            pygame.draw.rect(self.display_surface, (255,0,0), play_btn, width=2, border_radius=2)
            if state == "main_screen": 
                play_text = self.menu_buttons_font.render("Play", True, (0,0,0))
                play_text_rect = play_text.get_rect(center=play_btn.center)
                self.display_surface.blit(play_text, play_text_rect)
            if state == "pause":
                resume_text = self.menu_buttons_font.render("Resume", True, (0,0,0))
                resume_text_rect = resume_text.get_rect(center=play_btn.center)
                self.display_surface.blit(resume_text, resume_text_rect)

            pygame.draw.rect(self.display_surface, (255,0,0), settings_btn, width=2, border_radius=2)
            settings_text = self.menu_buttons_font.render("Settings", True, (0,0,0))
            settings_text_rect = settings_text.get_rect(center=settings_btn.center)
            self.display_surface.blit(settings_text, settings_text_rect)

            pygame.draw.rect(self.display_surface, (255,0,0), exit_btn, width=2, border_radius=2)
            quit_text = self.menu_buttons_font.render("Quit", True, (0,0,0))
            quit_text_rect = quit_text.get_rect(center=exit_btn.center)
            self.display_surface.blit(quit_text, quit_text_rect)

        elif state == "settings":
            pygame.draw.rect(self.display_surface, (255,0,0), settings_btn, width=2, border_radius=2)
            volume_text = self.menu_buttons_font.render("Volume", True, (0,0,0))
            volume_text_rect = volume_text.get_rect(center=settings_btn.center)
            self.display_surface.blit(volume_text, volume_text_rect)

            pygame.draw.rect(self.display_surface, (255,0,0), exit_btn, width=2, border_radius=2)
            back_text = self.menu_buttons_font.render("Back", True, (0,0,0))
            back_text_rect = back_text.get_rect(center=exit_btn.center)
            self.display_surface.blit(back_text, back_text_rect)
            

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check button collisions directly in the event loop
                    if play_btn.collidepoint((mx, my)):
                        if state == "main_screen":
                            print("Starting game...")
                            self.game_state = "fighting"
                            self.playing = True
                            self.intro_count = 3  # Reset countdown
                            self.last_count_update = pygame.time.get_ticks()
                        else:
                            print("Resuming game...")
                            self.game_state = "fighting"
                            self.playing = True
                    elif settings_btn.collidepoint((mx, my)):
                        if state == "main_screen" or state == "pause":
                            print("Opening settings...")
                            self.game_state = "settings"
                        elif state == "settings":
                            print("Volume clicked")
                    elif exit_btn.collidepoint((mx, my)):
                        if state == "settings":
                            print("Going back...")
                            self.game_state = "main_screen"
                        else:
                            print("exiting")
                            pygame.quit()
                            sys.exit() 				
                
    def drawBg(self):
        for x in range(3):
            speed = 1
            for i in self.bgImages:
                self.display_surface.blit(i, ((x * self.bgWidth) - self.scroll * speed, 0))
                speed += 0.05

    def draw_text(self, text, font, colour, x, y):
        img = font.render(text, True, colour)
        self.display_surface.blit(img, (x,y))

    def drawGround(self):
        for x in range(15):
            self.display_surface.blit(self.ground_image, ((x * self.ground_width - self.scroll * 2), SCREEN_HEIGHT - self.ground_height))

    def moveScreen(self):
        key = pygame.key.get_pressed()
        
        # Manual movement controls
        if key[pygame.K_LEFT] and self.scroll > 0:
            self.scroll -= 2
        if key[pygame.K_RIGHT] and self.scroll < 1000:
            self.scroll += 2
            
        # Toggle automatic background movement with T key
        if key[pygame.K_y]:
            self.auto_scroll = not self.auto_scroll
            
        # Automatic infinite background movement (only when enabled)
        if self.auto_scroll:
            self.scroll += self.scroll_speed
        
        # Calculate the total width needed for seamless looping
        total_bg_width = self.bgWidth * 3  # Since we draw 3 background images
        
        # Reset scroll when it reaches the width of one background image
        # This creates the infinite loop effect
        if self.scroll >= self.bgWidth:
            self.scroll = 0  

    def lockScreen(self):
        # Ensure scroll doesn't go negative
        if self.scroll < 0:
            self.scroll = 0
        # Reset scroll when it reaches the background width for seamless looping
        if self.scroll >= self.bgWidth:
            self.scroll = 0
               
    def drawHealthBar(self, health, x, y):
        ratio = health / 100
        pygame.draw.rect(self.display_surface, WHITE, (x - 2,y - 2, 304, 34))
        pygame.draw.rect(self.display_surface, RED, (x,y, 300, 30) )
        pygame.draw.rect(self.display_surface, YELLOW, (x,y, 300 * ratio, 30))
    
    def drawText(self):
        # Display auto-scroll status
        font = pygame.font.Font(None, 36)
        status_text = "Auto-scroll: ON" if self.auto_scroll else "Auto-scroll: OFF"
        text_surface = font.render(status_text, True, WHITE)
        self.display_surface.blit(text_surface, (10, SCREEN_HEIGHT - 40))
        
        # Display controls info
        controls_text = "Press T to toggle auto-scroll, Arrow keys for manual control"
        controls_surface = font.render(controls_text, True, WHITE)
        self.display_surface.blit(controls_surface, (10, SCREEN_HEIGHT - 70))

