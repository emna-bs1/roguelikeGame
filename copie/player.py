import pygame
import Map
import arm
import Collect
bullet_rate = 150
vector = pygame.math.Vector2
from copy import copy

done = False
killing_power = 10

def collide_sprite(ob1, ob2):
    return ob1.collide_rect.colliderect(ob2.collide)

def collide_with_wall(who,direction):
    collision = pygame.sprite.spritecollide(who, Map.sprite_walls, False, collide_sprite)
    if (direction and collision):
        if who.move_speed.x > 0:
            who.position.x = collision[0].collide.left - who.collide_rect.width / 2
        else:
            who.position.x = collision[0].collide.right + who.collide_rect.width / 2
        who.collide_rect.centerx = who.position.x
        # self.collide_rect.centery = self.position.y

    if (not direction and collision):
        if who.move_speed.y < 0:
            who.position.y = collision[0].collide.bottom + who.collide_rect.height / 2
        else:
            who.position.y = collision[0].collide.top - who.collide_rect.height / 2
        # self.collide_rect.centerx = self.position.x
        who.collide_rect.centery = who.position.y
    if (not direction and collision):
        if who.move_speed.y < 0:
            who.position.y = collision[0].collide.bottom + who.collide_rect.height / 2
        else:
            who.position.y = collision[0].collide.top - who.collide_rect.height / 2
        # self.collide_rect.centerx = self.position.x
        who.collide_rect.centery = who.position.y

#class player
class Player(pygame.sprite.Sprite):
    def __init__(self,game,x,y):
        self.groups = game._sprites , game.guide_gr
        pygame.sprite.Sprite.__init__(self,self.groups)
        #sprite attributes
        self.image = game.player_img
        self.game = game
        self.rect = self.image.get_rect()
        self.speed = 500

        self.rotation_speed = 500
        self.rotation = 0

        self.position = vector(x,y)
        self.move_speed = vector(0,0)

        self.collide_rect = pygame.Rect(*self.position,30,30)
        self.collide_rect.center = self.rect.center

        self.arms = pygame.sprite.Group()

        self.arm_collected = False

        self.last = 0

        self.guide_rect = pygame.Rect(self.position.x / 16 , self.position.y / 16 , (self.collide_rect.width + 20) / 16 + 2, (self.collide_rect.height + 20) / 16 + 2)
        self.health = 100

        self.health_bar = pygame.Rect(20, 20, self.health * 200 /100, 20)
        self.health_bar_boundaries = self.health_bar.copy()
        #self.health_bar_boundaries.width =
        self.collection_mission = 0
        self.collection_coins = 0


    def draw_health_bar(self):
        good = 70
        well = 50
        medium = 30

        if self.health >= good:
            color = (0,255,0)
        elif self.health >= well :
            color = (150,255,150)
        elif self.health >= medium :
            color = (255,150,150)
        else :
            color = (255,0,0)
        if self.health <= 100 :
            bar_width = self.health / 100 * 200
            self.health_bar = pygame.Rect(20,20, bar_width, 20)
            pygame.draw.rect(self.game.screen, color,self.health_bar)
            pygame.draw.rect(self.game.screen,(255,255,255),self.health_bar_boundaries,2)


    def press_keys_event(self):
        global done

        self.rotation_speed = 0
        self.move_speed = vector(0,0)
        keys = pygame.key.get_pressed()
        # presssing keys events

        if keys[pygame.K_LEFT]:
            self.rotation_speed = 500

        if keys[pygame.K_RIGHT]:
            self.rotation_speed = - 500
        if keys[pygame.K_UP]:
            self.move_speed = vector(self.speed,0).rotate(-self.rotation)
        if keys[pygame.K_DOWN]:
            self.move_speed = vector(-self.speed ,0).rotate(-self.rotation)

        if keys[pygame.K_SPACE] and self.arm_collected:
            current = pygame.time.get_ticks()
            if current - self.last <= arm.bullet_rate and not done:
                self.move_speed = vector(arm.push_back, 0).rotate(-self.rotation)
                done = True
            if current - self.last > arm.bullet_rate:
                parametered_arm_pos = self.position + arm.pos_param.rotate(-self.rotation)
                a = arm.Arm(parametered_arm_pos , self.move_speed, self)
                self.last = current
                self.arms.add(a)
                self.move_speed = vector(- arm.push_back, 0).rotate(-self.rotation)
                hitSound = pygame.mixer.Sound('hit.wav')
                hitSound.play()

                done = False

    def update(self):
        self.press_keys_event()
        self.rotation = (self.rotation + self.rotation_speed * self.game.dt) % 360
        self.image = pygame.transform.rotate(self.game.player_img,self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.move(*self.move_speed)
        self.collide_rect.centerx = self.position.x
        collide_with_wall(self,1)
        self.collide_rect.centery = self.position.y
        collide_with_wall(self,0)
        self.rect.center = self.collide_rect.center
        self.move_bullet()
        self.move_speed = (0,0)
        self.guide_rect = pygame.Rect(self.position.x / 16 - 4 , self.position.y / 16 - 4 , (self.collide_rect.width + 20) / 16 + 4, (self.collide_rect.height + 20) / 16 + 4)

        if self.health <= 0:
            self.health  = 100

    def move_bullet(self):
        self.arms.update(self.move_speed)

    def draw_rect(self,window):
        pygame.draw.rect(window,(0,0,0),self.rect,4)
        pygame.draw.rect(window,(0,0,0), self.illuminate_rect, 2)

    def move(self,move_x = 0 ,move_y = 0):
        self.position.x += move_x * self.game.dt
        self.position.y += move_y * self.game.dt
    def swap_image(self,image):
        self.game.player_img = image

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sp , game.guide_gr
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.image = pygame.image.load('topdown-shooter/PNG/Hitman 1/hitman1_hold.png')
        self.rect = self.image.get_rect()
        self.position = vector(x,y)
        self.game = game
        self.rect.topleft = self.position
        self.target = self.game.hero
        self.move_speed = vector(0,0)
        self.acceleration = vector(0,0)
        self.rotate = 0
        self.speed = 150
        self.health = 100
        self.collide_rect = pygame.Rect(*self.position,30,30)
        self.collide_rect.center = self.rect.center
        self.guide_rect = pygame.Rect(self.position.x / 16 - 4 , self.position.y / 16 - 4 , (self.collide_rect.width + 20) / 16 + 4, (self.collide_rect.height + 20) / 16 + 4)
        self.killing_power = 10

    def update(self):
        self.rotation = (self.game.hero.position - self.position).angle_to(vector(1,0))
        self.new_image = pygame.transform.rotate(self.image,self.rotation)
        self.rect = self.new_image.get_rect()
        self.rect.center = self.position
        self.acceleration = vector(self.speed,0).rotate(-self.rotation)
        self.acceleration += self.move_speed * -1
        self.move_speed += self.acceleration * self.game.dt
        self.position += self.move_speed * self.game.dt + 0.5 * self.acceleration * self.game.dt ** 2
        self.collide_rect.centerx = self.position.x
        collide_with_wall(self,1)
        self.collide_rect.centery = self.position.y
        collide_with_wall(self,0)
        self.guide_rect = pygame.Rect(self.position.x / 16 - 4 , self.position.y / 16 - 4 , (self.collide_rect.width + 20) / 16 + 4, (self.collide_rect.height + 20) / 16 + 4)
        self.draw_health_bar()
        if self.health <= 0:
                Collect.Collect(self.game,'COIN',*self.position)
                self.kill()

    def draw_health_bar(self):
        good = 70
        well = 50
        medium = 30

        if self.health >= good:
            color = (0,255,0)
        elif self.health >= well :
            color = (150,255,150)
        elif self.health >= medium :
            color = (255,150,150)
        else :
            color = (255,0,0)

        if self.health <= 100 :
            bar_width = self.rect.width * self.health / 100
            self.health_bar = pygame.Rect(0, 0, bar_width, 6)
            pygame.draw.rect(self.new_image, color,self.health_bar)

        """
        self.rect.center = self.position"""
        """if pygame.sprite.spritecollideany(self,Map.sprite_walls,False):
            self.move(-self.move_x, -self.move_y)
            self.rect.x = self.x
            self.rect.y = self.y
        """


