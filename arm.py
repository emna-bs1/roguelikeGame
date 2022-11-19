import pygame
import Map
from random import uniform
vector = pygame.math.Vector2

intensity =10
bullet_rate = 150
spread_range = 4
push_back = 200
pos_param = vector(20 ,15)

class Arm(pygame.sprite.Sprite):
    def __init__(self,position,palyer_speed_vec,user):
        pygame.sprite.Sprite.__init__(self)
        self.bullet_rate = 150
        self.user = user
        self.image = pygame.image.load('shoot/PNG/Effects/Light_Shell.png')
        self.rect = self.image.get_rect()
        self.position = vector(position)
        self.rect.center = self.position
        self.speed = 500
        self.rotation = self.user.rotation
        self.shooting_time = pygame.time.get_ticks()
        spread = uniform(-spread_range, spread_range)
        self.speed_vec = vector(self.speed, 0).rotate(-self.rotation + spread)


    def update(self,speed):
        self.position += self.speed_vec * self.user.game.dt
        self.rotated_image = pygame.transform.rotate(self.image,self.rotation + 90 )
        self.rect = self.rotated_image.get_rect()
        self.rect.center = self.position
        #print('after',self.rect)

        #pygame.time.get_ticks() : returns number of milliseconds since pygame.init() was called
        if pygame.time.get_ticks() - self.shooting_time > 1500:
            self.kill()
        if self.collide():
            self.kill()

    def collide(self):
        return pygame.sprite.spritecollideany(self, Map.sprite_walls, None)

