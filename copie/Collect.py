import pygame
import pytweening as tween
vector = pygame.math.Vector2

class Collect(pygame.sprite.Sprite):
    def __init__(self,game,type, x,y):
        self.groups = game.collection
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vector(x,y)
        self.type = type
        if self.type == 'COIN':
            self.image = self.game.coin_icon
        elif self.type == 'MISSION':
            self.image = self.game.mission_icon
        elif self.type == 'ARM':
            self.image = self.game.weapon_icon
        elif self.type == 'FLAG':
            self.image = self.game.flag_icon
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.tween = tween.easeInOutSine
        self.bob_range = 20
        self.speed = 0.5
        self.step = 0
        self.direction = 1

    def update(self):
        self.motion = self.bob_range * (self.tween(self.step / self.bob_range) - 0.5)
        self.rect.centery = self.pos.y + self.motion * self.direction
        self.step += self.speed
        if self.step > self.bob_range:
            self.step = 0
            self.direction *= -1


