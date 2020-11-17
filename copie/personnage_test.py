import pygame
import Map
vector = pygame.math.Vector2
#class player
class Player(pygame.sprite.Sprite):
    def __init__(self,game,x,y,width,height):
        self.groups = game._sprites
        pygame.sprite.Sprite.__init__(self,self.groups)
        #sprite attributes
        self.image = game.player_img
        self.game = game
        self.height = height
        self.width = width
        self.rect = self.image.get_rect()

        self.last_up = False
        self.last_down = False
        self.speed = 32
        self.up = False
        self.down = False
        self.left = True
        self.right = False
        self.walkCount = 0
        self.last_right = False
        self.last_left = False

        self.rotation_speed = 32

        self.position = vector(x,y)
        self.move_speed = vector(0,0)

    def press_keys_event(self):
        self.move_speed = vector(0,0)
        keys = pygame.key.get_pressed()
        # presssing keys events

        if keys[pygame.K_LEFT]:
            self.move_speed.x = -self.speed
            self.move_speed.y = 0
        elif keys[pygame.K_RIGHT]:
            self.move_speed.x = self.speed
            self.move_speed.y = 0
        elif keys[pygame.K_UP]:
            self.move_speed.x = 0
            self.move_speed.y = -self.speed
        elif keys[pygame.K_DOWN]:
            self.move_speed.x = 0
            self.move_speed.y = self.speed

    def update(self):
        self.move(*self.move_speed)

        self.rect.x = self.position.x
        self.collide_with_wall(1)
        self.rect.y = self.position.y
        self.collide_with_wall(0)
        self.move_speed = (0,0)

    def draw_rect(self,window):
        pygame.draw.rect(window,(0,255,255),self.rect,4)

    def move(self,move_x = 0 ,move_y = 0):
        self.position.x += move_x * self.game.dt
        self.position.y += move_y * self.game.dt


    def collide_with_wall(self, direction):

        collision = pygame.sprite.spritecollide(self, Map.sprite_walls,False)
        if(direction and collision):
            print(collision[0].rect[0])
            print(self.position.x + self.width)

            if self.move_speed.x > 0:
                self.position.x = collision[0].rect.left - self.rect.width
            else:
                self.position.x = collision[0].rect.right
            self.rect.x = self.position.x
            self.rect.y = self.position.y

        if(not direction and collision):
            if self.move_speed.y < 0:
                self.position.y = collision[0].rect.bottom
            else:
                self.position.y = collision[0].rect.top - self.rect.height
            self.rect.x = self.position.x
            self.rect.y = self.position.y


        """if pygame.sprite.spritecollideany(self,Map.sprite_walls,False):
            self.move(-self.move_x, -self.move_y)
            self.rect.x = self.x
            self.rect.y = self.y
"""


        """keys = pygame.key.get_pressed()
            # presssing keys events
    
            if keys[pygame.K_LEFT] and self.x > self.speed and Map.detect_wall_horizental(self.x, self.y, self.width,self.height, 0):
                #self.x -= self.speed / 2
                self.map_move_x = self.speed
                self.left = True
                self.right = False
                self.up = False
                self.down = False
            elif keys[pygame.K_RIGHT] and Map.detect_wall_horizental(self.x, self.y, self.width, self.height, 1):
                #self.x += self.speed /2
                self.map_move_x = -self.speed
                self.up = False
                self.down = False
                self.left = False
                self.right = True
    
            elif keys[pygame.K_UP] and self.y > self.speed and Map.detect_wall_vertical(self.x, self.y, self.width, self.height, 1):
                self.map_move_y = self.speed
                #self.y -= self.speed / 2
                self.up = True
                self.down = False
                self.left = False
                self.right = False
    
            elif keys[pygame.K_DOWN] and Map.detect_wall_vertical(self.x, self.y, self.width, self.height, 0):
                self.map_move_y = -self.speed
                #self.y += self.speed /2
                self.up = False
                self.down = True
                self.left = False
                self.right = False
            else:
                if self.left:
                    self.last_right = False
                    self.last_left = True
                    self.last_up = False
                    self.last_down = False
                elif self.right:
                    self.last_right = True
                    self.last_left = False
                    self.last_up = False
                    self.last_down = False
                elif self.up:
                    self.last_right = False
                    self.last_left = False
                    self.last_up = True
                    self.last_down = False
                elif self.down:
                    self.last_right = False
                    self.last_left = False
                    self.last_up = False
                    self.last_down = True
    
                self.up = False
                self.down = False
                self.left = False
                self.right = False"""




