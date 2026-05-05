import pygame
import sys
from random import randint

from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.player import Fighter2
from src.button import PlayButton, ResumeButton, SettingsButton, BackButton, ExitButton, VolumeButton, ScreenShakeToggle, CharacterButton
from src.playerData import WARRIOR_DATA, SORCERER_DATA, P1_CONTROLS, P2_CONTROLS, OLD_WIZARD_DATA, HUNTRESS_DATA
from src.assets import Assets

YELLOW = (255,255,0)
RED = (255,0,0)
WHITE = (255,255,255)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 139)


class Level:
    def __init__(self):
        self.playing = False
        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_states = ["main_screen", "character_select","pause", "loading", "fighting", "settings"]
        self.game_state = self.game_states[0]

        self.intro_count = 4
        self.last_count_update = pygame.time.get_ticks()
        self.score = [0,0]
        self.round_complete = False
        self.round_over_cooldown = 5000
    
        self.p1_selection = 0
        self.p2_selection = 0
        self.p1_confirmed = False
        self.p2_confirmed = False
        self.p1_cursor = 0  # which character P1 is hovering over
        self.p2_cursor = 0

        self.countdown_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
        self.score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
        self.menu_font = pygame.font.Font("assets/fonts/turok.ttf", 100)
        self.menu_buttons_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
        self.subtitle_font = pygame.font.Font("assets/fonts/turok.ttf", 50)

        # Background Stuff
        self.bgImages = []
        for i in range(1,6):
            image = Assets.image(f'assets/images/background/plx-{i}.png')
            scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bgImages.append(scaled_image)
        self.bgWidth = self.bgImages[0].get_width()
        self.scroll = 0
        # Background movement toggle
        self.auto_scroll = True
        self.scroll_speed = 1

        self.ground_image = Assets.image('assets/images/background/ground.png')
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

        # Sprite Sheets
        self.warrior_sheet = Assets.image("assets/images/warrior/warrior.png")
        self.warrior_animation_steps = [10,8,1,7,7,3,7]

        self.sorcerer_sheet = Assets.image("assets/images/sorcerer/Sprites/wizard.png")
        self.sorcerer_animation_steps = [8,8,1,8,8,3,7]

        self.huntress_sheet = Assets.image("assets/images/huntress/huntress.png")
        self.huntress_animation_steps = [8,8,2,5,5,3,8]  # Idle,Run,Jump,Attack1,Attack2,Hit,Death

        self.wizard_sheet = Assets.image("assets/images/old-wizard/old-wizard.png")
        self.wizard_animation_steps = [6,8,2,8,8,4,7]  # Idle,Run,Jump,Attack1,Attack2,Hit,Death

        # Images
        # Victory Image (will change later)
        self.victory_image = Assets.image("assets/images/victory.png")
        self.victory_width = self.victory_image.get_width()

        # music / audio

        pygame.mixer.music.load("assets/audio/bg_music.mp3")
        pygame.mixer.music.play(loops=-1)   
        pygame.mixer.music.set_volume(0.3)  

        # player audio files
        self.warrior_swing_audio = Assets.sound("assets/audio/sword_swing.wav")
        self.sorcerer_swing_audio = Assets.sound("assets/audio/magic_swing.mp3")
        self.old_wizard_swing_audio = Assets.sound("assets/audio/magic_swing.mp3")

        # Character roster
        self.roster = [
            {"name": "Warrior",    "data": WARRIOR_DATA,    "sheet": self.warrior_sheet,  "steps": self.warrior_animation_steps,  "audio": self.warrior_swing_audio},
            {"name": "Sorcerer",   "data": SORCERER_DATA,   "sheet": self.sorcerer_sheet, "steps": self.sorcerer_animation_steps, "audio": self.sorcerer_swing_audio},
            {"name": "Huntress",   "data": HUNTRESS_DATA,   "sheet": self.huntress_sheet, "steps": self.huntress_animation_steps, "audio": self.warrior_swing_audio},
            {"name": "Old Wizard", "data": OLD_WIZARD_DATA, "sheet": self.wizard_sheet,   "steps": self.wizard_animation_steps,   "audio": self.old_wizard_swing_audio},
        ]

        self.char_buttons_p1 = []
        self.char_buttons_p2 = []

        # Players
        self.fighter_1 = Fighter2(1, 200, 280, False, HUNTRESS_DATA, self.huntress_sheet, self.huntress_animation_steps, self.warrior_swing_audio, P1_CONTROLS)
        self.fighter_2 = Fighter2(2, 700, 280, True, OLD_WIZARD_DATA, self.wizard_sheet, self.wizard_animation_steps, self.old_wizard_swing_audio, P2_CONTROLS)
   
        # buttons - using custom button classes that handle game state changes
        middle = SCREEN_WIDTH / 2 - 100
        self.play_btn = PlayButton("Start", 200, 40, (middle,200), 5)
        self.pause_btn = ResumeButton("Resume", 200, 40, (middle,200), 5)
        self.settings_btn = SettingsButton("Settings", 200, 40, (middle,280), 5)
        self.exit_btn = ExitButton("Quit", 200, 40, (middle,360), 5)
        self.volume_btn = VolumeButton("Volume", 200, 40, (middle,280), 5)
        self.back_btn = BackButton("Back", 200, 40, (middle,200), 5)
        self.screen_shake_btn = ScreenShakeToggle("Shake: ON", 200, 40, (middle,440), 5)

        # Set level reference for all buttons
        for btn in [self.play_btn, self.pause_btn, self.settings_btn, self.exit_btn, self.volume_btn, self.back_btn, self.screen_shake_btn]:
            btn.level = self

        # Sprite Groups
        self.particle_group = pygame.sprite.Group()

        # Screen Shake
        self.screen_shake_frames = 0
        self.screen_shake_enabled = True
        self.shake_offset = (0,0)
       
    def run(self, dt, events):

        # Determine screenshake value
        if self.screen_shake_enabled and self.screen_shake_frames > 0:
            self.screen_shake_frames -= 1
            self.shake_offset = (randint(-3, 3), randint(-3, 3))
        else:
            self.shake_offset = (0, 0)

        # Handle all events in one place
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "fighting":
                        self.game_state = "pause"
                        self.playing = False
                    elif self.game_state == "pause":
                        self.game_state = "fighting"
                elif self.game_state == "character_select":
                    roster_len = len(self.roster)
                    if event.key == pygame.K_a:
                        self.p1_cursor = (self.p1_cursor - 1) % roster_len
                    elif event.key == pygame.K_d:
                        self.p1_cursor = (self.p1_cursor + 1) % roster_len
                    elif event.key == pygame.K_w:
                        self.p1_selection = self.p1_cursor
                        self.p1_confirmed = True
                    elif event.key == pygame.K_j:
                        self.p2_cursor = (self.p2_cursor - 1) % roster_len
                    elif event.key == pygame.K_l:
                        self.p2_cursor = (self.p2_cursor + 1) % roster_len
                    elif event.key == pygame.K_i:
                        self.p2_selection = self.p2_cursor
                        self.p2_confirmed = True
        
        # Draw background first
        self.drawBg()
        self.drawGround()
        
        # Draw fighters
        self.fighter_1.animation_update()
        self.fighter_2.animation_update()
        self.fighter_1.draw(self.display_surface, self.shake_offset)
        self.fighter_2.draw(self.display_surface, self.shake_offset)

        # Draw particles (draw them after fighters so they appear on top)
        self.fighter_1.particle_group.draw(self.display_surface)
        self.fighter_2.particle_group.draw(self.display_surface)
        self.fighter_1.particle_group.update(dt)
        self.fighter_2.particle_group.update(dt)


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
                self.fighter_2.move(target=self.fighter_1)

        # Screen Shake
        for fighter in [self.fighter_1, self.fighter_2]:
            if fighter.screen_shake_trigger:
                self.screen_shake_frames = 6
                fighter.screen_shake_trigger = False


        # Draw health bars last (on top of everything)
        self.drawHealthBar(self.fighter_1.health, 20, 20)
        self.drawHealthBar(self.fighter_2.health, 660, 20)

        # Draw Player Attack Cooldown Bars
        self.drawHeavyAttackCooldown(self.fighter_1.heavy_attack_cooldown, self.fighter_1.heavy_attack_max_cooldown, 20, 56)
        self.drawHeavyAttackCooldown(self.fighter_2.heavy_attack_cooldown, self.fighter_2.heavy_attack_max_cooldown, 660, 56)

        # check defeat
        if not self.round_complete:
            if self.fighter_1.is_dead:
                self.score[1] += 1
                self.round_complete = True
                self.round_over_time = pygame.time.get_ticks()
                print(self.score)
            elif self.fighter_2.is_dead:
                self.score[0] += 1
                self.round_complete = True
                self.round_over_time = pygame.time.get_ticks()
                print(self.score)
            
        else:
            # Display Victory Image
            
            self.display_surface.blit(self.victory_image, (int(SCREEN_WIDTH / 2 - self.victory_width / 2), 250))
            if pygame.time.get_ticks() - self.round_over_time > self.round_over_cooldown:
                self.round_complete = False
                self.intro_count = 3
                self.fighter_1 = Fighter2(1, 200, 280, False, WARRIOR_DATA, self.warrior_sheet, self.warrior_animation_steps, self.warrior_swing_audio, P1_CONTROLS)
                self.fighter_2 = Fighter2(2, 700, 280, True, SORCERER_DATA, self.sorcerer_sheet, self.sorcerer_animation_steps, self.sorcerer_swing_audio, P2_CONTROLS)

        # Menu / Options
        if self.game_state == "main_screen":
            self.home_screen()
        elif self.game_state == "character_select":
            self.character_select_screen()
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
        self.draw_text("Magestic Brawl", self.menu_font, (0,0,0), 150, 20)
        self.menu_buttons(state=self.game_state)

    def character_select_screen(self):
        if not self.char_buttons_p1:
            button_width, button_height, button_gap = 100, 130, 15
            # P1 buttons start at x=20 (left half), P2 at x=520 (right half)
            p1_start_x, p2_start_x = 20, 520
            button_y = 220  # below the "Player 1/2" labels

            for char_index, char in enumerate(self.roster):
                # Extract first idle frame (row 0, col 0) from sprite sheet as portrait
                data = char["data"]
                sprite_cell_width = data.cell_width if data.cell_width else data.size
                portrait = char["sheet"].subsurface(0, 0, sprite_cell_width, data.size)

                p1_x = p1_start_x + char_index * (button_width + button_gap)
                p2_x = p2_start_x + char_index * (button_width + button_gap)

                p1_btn = CharacterButton(portrait, char["name"], char_index, 1, button_width, button_height, (p1_x, button_y), 5)
                p2_btn = CharacterButton(portrait, char["name"], char_index, 2, button_width, button_height, (p2_x, button_y), 5)
                p1_btn.level = self
                p2_btn.level = self
                self.char_buttons_p1.append(p1_btn)
                self.char_buttons_p2.append(p2_btn)

        self.display_surface.fill((0, 0, 0))
        self.draw_text("Select Character", self.menu_font, WHITE, 100, 20)
        self.draw_text("Player 1", self.subtitle_font, RED, 20, 145)
        self.draw_text("Player 2", self.subtitle_font, RED, SCREEN_WIDTH // 2 + 20, 145)

        for btn in self.char_buttons_p1:
            btn.draw(self.display_surface, self.game_state)
            if btn.was_clicked:
                self.p1_cursor = btn.char_index
                self.p1_selection = btn.char_index
                self.p1_confirmed = True
                btn.was_clicked = False

        for btn in self.char_buttons_p2:
            btn.draw(self.display_surface, self.game_state)
            if btn.was_clicked:
                self.p2_cursor = btn.char_index
                self.p2_selection = btn.char_index
                self.p2_confirmed = True
                btn.was_clicked = False

        # Yellow border on the currently hovered character
        p1_hovered = self.char_buttons_p1[self.p1_cursor]
        p2_hovered = self.char_buttons_p2[self.p2_cursor]
        pygame.draw.rect(self.display_surface, YELLOW, p1_hovered.top_rect, 3, border_radius=12)
        pygame.draw.rect(self.display_surface, YELLOW, p2_hovered.top_rect, 3, border_radius=12)

        # Green border + "READY" on confirmed selection
        if self.p1_confirmed:
            p1_confirmed_btn = self.char_buttons_p1[self.p1_selection]
            pygame.draw.rect(self.display_surface, (0, 220, 0), p1_confirmed_btn.top_rect, 3, border_radius=12)
            self.draw_text("READY", self.menu_buttons_font, (0, 220, 0), p1_confirmed_btn.top_rect.x, p1_confirmed_btn.top_rect.bottom + 4)

        if self.p2_confirmed:
            p2_confirmed_btn = self.char_buttons_p2[self.p2_selection]
            pygame.draw.rect(self.display_surface, (0, 220, 0), p2_confirmed_btn.top_rect, 3, border_radius=12)
            self.draw_text("READY", self.menu_buttons_font, (0, 220, 0), p2_confirmed_btn.top_rect.x, p2_confirmed_btn.top_rect.bottom + 4)

        # Once both confirmed, spawn fighters and start
        if self.p1_confirmed and self.p2_confirmed:
            self._spawn_fighters()
            self.p1_confirmed = False
            self.p2_confirmed = False
            self.game_state = "fighting"
            self.playing = True
            self.intro_count = 3
            self.last_count_update = pygame.time.get_ticks()
                

    def _spawn_fighters(self):
        p1 = self.roster[self.p1_selection]
        p2 = self.roster[self.p2_selection]
        self.fighter_1 = Fighter2(1, 200, 280, False, p1["data"], p1["sheet"], p1["steps"], p1["audio"], P1_CONTROLS)
        self.fighter_2 = Fighter2(2, 700, 280, True,  p2["data"], p2["sheet"], p2["steps"], p2["audio"], P2_CONTROLS)

    def pause_menu(self):
        self.menu_buttons(state=self.game_state)

    def settings_menu(self):
        self.display_surface.fill((255,255,255))
        self.draw_text("Settings", self.menu_font, (0,0,0), SCREEN_WIDTH / 2 - 200, 20)
        self.menu_buttons(state=self.game_state)

    def menu_buttons(self, state):
        if state == "main_screen" or state == "pause":
            if state == "main_screen":
                self.play_btn.draw(self.display_surface, self.game_state)
                self.settings_btn.draw(self.display_surface, self.game_state)
                self.exit_btn.draw(self.display_surface, self.game_state)
            if state == "pause":
                self.pause_btn.draw(self.display_surface, self.game_state)
                self.settings_btn.draw(self.display_surface, self.game_state)
                self.exit_btn.draw(self.display_surface, self.game_state)
        elif state == "settings":
            self.back_btn.draw(self.display_surface, self.game_state)
            self.volume_btn.draw(self.display_surface, self.game_state)
            self.screen_shake_btn.draw(self.display_surface, self.game_state)
            self.exit_btn.draw(self.display_surface, self.game_state)

    def drawBg(self):
        ox, oy = self.shake_offset
        for x in range(10):
            speed = 1
            for i in self.bgImages:
                self.display_surface.blit(i, ((x * self.bgWidth) - self.scroll * speed + ox, oy))
                speed += 0.05

    def draw_text(self, text, font, colour, x, y):
        img = font.render(text, True, colour)
        self.display_surface.blit(img, (x,y))

    def drawGround(self):
        ox, oy = self.shake_offset
        for x in range(15):
            self.display_surface.blit(self.ground_image, ((x * self.ground_width - self.scroll * 2) + ox, SCREEN_HEIGHT - self.ground_height + oy))

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
    
    def drawHeavyAttackCooldown(self, cooldown_time, max_cooldown_time, x, y):
        ratio = cooldown_time / max_cooldown_time
        pygame.draw.rect(self.display_surface, WHITE, (x - 1, y - 1, 152, 10))
        pygame.draw.rect(self.display_surface, DARK_BLUE, (x, y, 150, 8))
        pygame.draw.rect(self.display_surface, PURPLE, (x, y, 150 * ratio, 8))
