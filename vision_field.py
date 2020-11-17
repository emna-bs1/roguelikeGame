import pygame
import Map
class Vision_field():

    def __init__(self,target,game ):
        wall_x = set(map(lambda x : x.rect[0] ,Map.walls))
        max_x = max(wall_x)
        wall_y = set(map(lambda x : x.rect[1] ,Map.walls))
        max_y = max(wall_y)
        self.game = game
        self.height = max_x
        self.width = max_y
        self.target = target
        self.field = pygame.Rect(self.target.rect[1] - self.width / 2,self.target.rect[0] - self.height / 2,self.width,self.height)

    def update(self, width,height):
        self.field = pygame.Rect(- self.target.rect.centerx + height / 2 ,-self.target.rect.centery + width / 2 ,self.width,self.height)

    def move(self,element):
        return element.rect.move(self.field.topleft)

    def move_rect(self,element):
        return element.move(self.field.topleft)

    def draw(self,window):
        pygame.draw.rect(window,(0,255,255),self.field,8)
