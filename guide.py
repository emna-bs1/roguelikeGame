import pygame
import Map

vector = pygame.math.Vector2

class Guide(pygame.sprite.Sprite):
    def __init__(self,game):
        self.game = game
        self.groups = game.guide_gr
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        width, height = Map.map_size()
        self.width = width  // 16
        self.height = (height + 128) // 16

        self.image = pygame.Surface((self.width,self.height))
        #self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = self.game.screen_width - self.width - 50
        self.rect.y = 20

    def draw(self):
        if self.game.arm_position != (-1 ,-1):
            arm_pos = [*self.game.arm_position]
            arm_rect = pygame.Rect(arm_pos[0] // 16, arm_pos[1] // 16,10,10)
            pygame.draw.rect(self.game.screen,(255,255,0),self.move(arm_rect))
        for wall in self.game.wall_sprites:
            pygame.draw.rect(self.game.screen,(0,0,255),self.move(wall.guide_rect))
        for sprite in self.game._sprites:
            pygame.draw.rect(self.game.screen,(0,255,255),self.move(sprite.guide_rect))
        for enemy in self.game.sp:
            pygame.draw.rect(self.game.screen,(255,0,0),self.move(enemy.guide_rect))

        for col in self.game.collection:
            if col.type == 'FLAG':
                rect = pygame.Rect(col.rect.x / 16, col.rect.y / 16, col.rect.width / 16, col.rect.height / 16)
                pygame.draw.rect(self.game.screen, (0, 255, 0), self.move(rect))

    def move(self, elem):
        return elem.move(self.rect.topleft)