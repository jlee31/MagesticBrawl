from settings import *
from sprites import *
from groups import AllSprites
from os.path import join
import pygame

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((screenWidth, screenHeight))
        pygame.display.set_caption('Magestic Brawl')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        # Fighting game variables
        self.introCount = 3
        self.lastCountUpdate = pygame.time.get_ticks()
        self.score = [0, 0]  # [p1, p2]
        self.roundOver = False
        self.roundOverCooldown = 2000
        self.victory = pygame.image.load(join('MainAssets', 'images', 'icons', 'victory.png')).convert_alpha()

        # Load sounds
        self.bgMusic = pygame.mixer.Sound(join('MainAssets', 'audio', 'music.mp3'))
        self.bgMusic.set_volume(0.5)
        self.bgMusic.play(loops=-1)

        self.swordSound = pygame.mixer.Sound(join('MainAssets', 'audio', 'sword.wav'))
        self.swordSound.set_volume(0.5)
        self.magicSound = pygame.mixer.Sound(join('MainAssets', 'audio', 'magic.wav'))
        self.magicSound.set_volume(0.5)

        # Fighter data
        self.warriorData = [162, 4, [72, 56]]
        self.wizardData = [250, 3, [112, 107]]

        # Load spritesheets
        self.warriorSheet = pygame.image.load(join('MainAssets', 'images', 'warrior', 'Sprites', 'warrior.png')).convert_alpha()
        self.warriorFrames = [10, 8, 1, 7, 7, 3, 7]
        self.wizardSheet = pygame.image.load(join('MainAssets', 'images', 'wizard', 'Sprites', 'wizard.png')).convert_alpha()
        self.wizardFrames = [8, 8, 1, 8, 8, 3, 7]

        # Initialize fighters
        self.fighterA = Player(1, 200, 430, False, self.warriorData, self.warriorSheet, self.warriorFrames, self.swordSound)
        self.fighterB = Player(2, 700, 430, True, self.wizardData, self.wizardSheet, self.wizardFrames, self.magicSound)

        # Load game
        self.setup()

    def setup(self):
        try:
            # Load the TMX map
            tmx_map = load_pygame(join('assets', 'data', 'maps', 'world.tmx'))
            print("TMX file loaded successfully!")

            # Load tiles from the 'Main' layer
            for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
                Sprite((x * tileSize, y * tileSize), image, (self.all_sprites, self.collision_sprites))

            # Load entities from the 'Entities' layer
            for obj in tmx_map.get_layer_by_name('Entities'):
                if obj.name == 'Player 1':
                    self.player = self.fighterA
                    print("Player 1 loaded successfully!")

        except FileNotFoundError:
            print("Error: TMX file or assets not found. Check the file paths.")
        except Exception as e:
            print(f"Error loading TMX file: {e}")

    def drawBg(self):
        self.display_surface.blit(pygame.image.load(join('assets', 'images', 'background', 'background.jpg')).convert_alpha(), (0, 0))

    def drawHealthBar(self, health, x, y):
        ratio = health / 100
        pygame.draw.rect(self.display_surface, (255, 255, 255), (x - 2, y - 2, 404, 34))
        pygame.draw.rect(self.display_surface, (255, 0, 0), (x, y, 400, 30))
        pygame.draw.rect(self.display_surface, (0, 128, 0), (x, y, 400 * ratio, 30))

    def drawText(self, text, font, color, x, y):
        img = font.render(text, True, color)
        self.display_surface.blit(img, (x, y))

    def run(self):
        while self.running:
            dt = self.clock.tick(frameRate) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update platformer game
            self.all_sprites.update(dt)

            # Update fighting game
            if self.introCount <= 0:
                self.fighterA.move(self.display_surface, self.fighterB, self.roundOver)
                self.fighterB.move(self.display_surface, self.fighterA, self.roundOver)
            else:
                self.drawText(str(self.introCount), pygame.font.Font(join('MainAssets', 'fonts', 'turok.ttf'), 100), (255, 0, 0), screenWidth / 2, screenHeight / 2)
                if (pygame.time.get_ticks() - self.lastCountUpdate) >= 1000:
                    self.introCount -= 1
                    self.lastCountUpdate = pygame.time.get_ticks()

            self.fighterA.update()
            self.fighterB.update()

            # Check for round over
            if not self.roundOver:
                if not self.fighterA.alive:
                    self.score[1] += 1
                    self.roundOver = True
                    self.roundOverTime = pygame.time.get_ticks()
                elif not self.fighterB.alive:
                    self.score[0] += 1
                    self.roundOver = True
                    self.roundOverTime = pygame.time.get_ticks()
            else:
                self.display_surface.blit(self.victory, (360, 150))
                if pygame.time.get_ticks() - self.roundOverTime > self.roundOverCooldown:
                    self.roundOver = False
                    self.introCount = 3
                    self.fighterA = Player(1, 200, 430, False, self.warriorData, self.warriorSheet, self.warriorFrames, self.swordSound)
                    self.fighterB = Player(2, 700, 430, True, self.wizardData, self.wizardSheet, self.wizardFrames, self.magicSound)

            # Draw everything
            self.display_surface.fill(bgColour)
            self.all_sprites.draw(self.player.rect.center)

            # Draw fighting game elements
            # self.drawBg()
            self.drawHealthBar(self.fighterA.health, 20, 20)
            self.drawHealthBar(self.fighterB.health, 580, 20)
            self.drawText("P1: " + str(self.score[0]), pygame.font.Font(join('MainAssets', 'fonts', 'turok.ttf'), 30), (255, 0, 0), 20, 60)
            self.drawText("P2: " + str(self.score[1]), pygame.font.Font(join('MainAssets', 'fonts', 'turok.ttf'), 30), (255, 0, 0), 580, 60)
            self.fighterA.draw(self.display_surface)
            self.fighterB.draw(self.display_surface)

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()