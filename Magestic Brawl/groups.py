from settings import * 

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - screenWidth / 2) / 4
        self.offset.y = -(target_pos[1] - screenHeight / 2) / 4

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)