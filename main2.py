from settings import * 
from sprites import * 
from groups import AllSprites

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

        # load game 
        self.setup()

    def setup(self):
        tmx_map = load_pygame(join('assets', 'data', 'maps', 'world.tmx'))

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * tileSize,y * tileSize), image, (self.all_sprites, self.collision_sprites))
        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player 1':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)

    def run(self):
        while self.running:
            dt = self.clock.tick(frameRate) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
            # update
            self.all_sprites.update(dt)

            # draw 
            self.display_surface.fill(bgColour)
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run() 
