import pygame
import Map
import player
import sys
import arm
import vision_field
from os import path
import guide
import csv
import random
import Collect
import constants

class Game(object):
    def __init__(self):
        self.alter_en = True
        pygame.init()
        pygame.font.init()

        self.player_img = pygame.image.load('topdown-shooter/PNG/Man Brown/manBrown_stand.png')
        pygame.key.set_repeat(10, 100)
        self.mission_icon = pygame.image.load('basic/PNG/Props/Dot_A.png')
        self.coin_icon = pygame.image.load('coin.png')
        self.weapon_icon = pygame.image.load('topdown-shooter/PNG/weapon_machine.png')
        self.flag_icon = pygame.image.load('basic/PNG/Props/Flag_A.png')
        self.enemies_number = 20
        self.collect_number = 10

        self.sp = pygame.sprite.Group()
        self.guide_gr = pygame.sprite.Group()
        self.collection = pygame.sprite.Group()
        self._sprites = pygame.sprite.Group()
        self.enemy_pos = []
        self.mission_pos = []

        self.dt = 0
        self.screen_width = 1400
        self.screen_height = 1200
        self.generate_map()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.wall_sprites = Map.sprite_walls
        self.floor_sprites = Map.sprite_floors
        self.guide = guide.Guide(self)
        self.guide_gr.draw(self.screen)
        self.camera = vision_field.Vision_field(self.hero,Map.map_size())
        #self.gen.prepare_room(self.screen)
        self.game_over = True
        self.dark = pygame.Surface((self.screen_width, self.screen_height))
        self.dark.fill((0,0,0))
        self.light = pygame.image.load('light_350_hard.png')
        self.light = pygame.transform.scale(self.light,(700,700))
        self.light_rect = self.light.get_rect()
        #self._sprites.add(self.hero)

    def generate_map(self):
            self.gen = Map.Generator()
            self.gen.gen_level()
            self.gen.gen_tiles_level()
            self.gen.parse_level()
            self.pos_x, self.pos_y = Map.generate_hero_initial_pos(self.screen_width, self.screen_height)
            self.arm_position = self.gen.arm_position

            Collect.Collect(self,'ARM',*self.arm_position)
            self.hero = player.Player(self, self.pos_x, self.pos_y)

            for i in range(self.enemies_number) :
                floor = Map.floor_pos[random.randint(0, len(Map.floor_pos) - 1)]
                player.Enemy(self,*floor)
                self.enemy_pos.append(floor)
                self.alter_en = False

            for i in range(self.collect_number):
                floor = Map.floor_pos[random.randint(0, len(Map.floor_pos))]
                self.mission_pos.append(floor)
                Collect.Collect(self,'MISSION',*floor)

    def load_data(self):
        missing = True
        if_corrupted = 0
        if path.exists('game.csv'):
            missing = False
            load_game = open("game.csv","r")
            reader = csv.reader(load_game)
            for row in reader:
                if_corrupted += 1
                if row[0] == 'p':
                    self.pos_x = float(row[1])
                    self.pos_y = float(row[2])
                    self.hero = player.Player(self, self.pos_x, self.pos_y)
                if row[0] == 'w':
                    Map.Wall((int(row[1]),int(row[2])))
                elif row[0] == 'o':
                    Map.Obstacle((int(row[1]),int(row[2])))
                elif row[0] == 'f':
                    Map.Floor((int(row[1]),int(row[2])))
                elif row[0] == 'b':
                    Map.Background((int(row[1]),int(row[2])))
                elif row[0] == 'e':
                    player.Enemy(self,float(row[1]),float(row[2]))
                elif row[0] == 'a':
                    self.arm_position = int(row[1]) , int(row[2])
                    Collect.Collect(self, 'ARM', *self.arm_position)
                    if self.arm_position == (-1, -1):
                        self.hero.arm_collected = True
                        self.hero.swap_image(pygame.image.load('topdown-shooter/PNG/Man Brown/manBrown_machine.png'))
                elif row[0] == 'm':
                    self.mission_pos.append((int(row[1]),int(row[2])))
                    Collect.Collect(self, 'MISSION', int(row[1]),int(row[2]))

            load_game.close()

            nbLines = open('nbLines.txt','r')
            nbLines.seek(0)
            var = nbLines.readline()
            try:
                int(var)
            except ValueError:
                return True
            else:
                if int(var) != if_corrupted:
                    return True
        return missing


    def save_data(self):
        game_state = open("game.csv","w",newline="")
        nbLines = 1
        writer = csv.writer(game_state)
        #writer.writerow(['object','x','y'])
        writer.writerow(['p',str(self.hero.position.x),str(self.hero.position.y)])

        elements = [{'name':'w','ref':Map.wall_pos},
                    {'name':'f','ref':Map.floor_pos},
                    {'name':'b','ref':Map.background_pos},
                    {'name':'o','ref':Map.obstacle_pos},
                    {'name':'e','ref':self.enemy_pos},
                    {'name':'a','ref':[self.arm_position]},
                    {'name':'m','ref':self.mission_pos}]
        for element in elements:
            for pos in element['ref']:
                writer.writerow([element['name'], str(pos[0]), str(pos[1])])
                nbLines += 1
        save_nbLines = open("nbLines.txt",'w')
        save_nbLines.write(str(nbLines))
        save_nbLines.close()
        game_state.close()


    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                if not self.game_over:
                    self.save_data()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.game_over:
                        self.save_data()
                    pygame.quit()
                    sys.exit()

    def draw(self):
        self.screen.fill((0, 0, 0))
        #self.wall_sprites.draw(self.screen)
        for floor in self.floor_sprites:
            self.screen.blit(floor.image,self.camera.move(floor))
        for wall in self.wall_sprites:
            self.screen.blit(wall.image,self.camera.move(wall))
            #pygame.draw.rect(self.screen,(255,255,255),self.camera.move_rect(wall.rect),2)
            #pygame.draw.rect(self.screen,(255,255,255),self.camera.move_rect(wall.collide),2)

        #self.floor_sprites.draw(self.screen)

        for sp in self.sp:
            sp.draw_health_bar()

            self.screen.blit(sp.new_image,self.camera.move(sp))
            #pygame.draw.rect(self.screen, (255, 255, 255), self.camera.move(sp),2)

        #pygame.draw.rect(self.screen, (255, 255, 255), self.camera.move_rect(self.hero.rect), 4)

        #pygame.draw.rect(self.screen,(255,255,255),self.camera.move_rect(self.hero.illuminate_rect),4)
        #self._sprites.draw(self.screen)
        for a in self.hero.arms:
            self.screen.blit(a.image,self.camera.move(a))
            #pygame.draw.rect(self.screen, (255, 255, 255), self.camera.move_rect(a.rect), 4)

        for col in self.collection:
            self.screen.blit(col.image,self.camera.move(col))

        self.flush_light()
        self.screen.blit(self.mission_icon,(20,50))

        self.screen.blit(self.mission, (100, 50))
        self.screen.blit(self.coin_icon, (23, 120))
        self.screen.blit(self.coins, (100, 120))


        for sprite in self._sprites:
            sprite.draw_health_bar()
            self.screen.blit(sprite.image,self.camera.move(sprite))
        #self.camera.draw(self.screen)
        #self.guide_gr.draw(self.screen)
        self.guide.draw()
        self.draw_debug()

        pygame.display.flip()


    def flush_light(self):
        self.dark.fill((50,50,50))
        self.light_rect.center = self.camera.move(self.hero).center
        self.dark.blit(self.light,self.light_rect)
        self.screen.blit(self.dark,(0,0), special_flags= pygame.BLEND_MULT)

    def update(self):
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.mission = myfont.render(str(self.hero.collection_mission)+ '/' + str(self.collect_number), False, (255, 255, 255))
        self.coins = myfont.render(str(self.hero.collection_coins), False, (255, 255, 255))

        self.collection.update()
        self._sprites.update()
        #self.sp.update()


        shots = pygame.sprite.groupcollide(self.sp,self.hero.arms,False, True)
        for shot in shots:
            shot.health -= arm.intensity


        collections = pygame.sprite.groupcollide(self.collection,self._sprites,False,False)
        for col in collections :
            if col.type != 'FLAG':
                col.kill()
            if col.type == 'MISSION':
                self.hero.collection_mission += 1
                Collect.Collect(self,'FLAG',*col.pos)
            elif col.type == 'COIN':
                self.hero.collection_coins += 10
            elif col.type == 'ARM':
                self.hero.arm_collected = True
                self.arm_position = -1 ,-1
                self.hero.swap_image(pygame.image.load('topdown-shooter/PNG/Man Brown/manBrown_machine.png'))


        kill_hero = pygame.sprite.groupcollide(self._sprites,self.sp, False,False)
        for killed in kill_hero:
            killed.health -= player.killing_power
        self.sp.update()

        self.enemy_pos = []
        for sp in self.sp:
            self.enemy_pos.append(sp.position)

        self.camera.update(self.screen_width,self.screen_height)

    def launch(self):
        while self.running:
            self.dt = self.clock.tick(32) / 1000
            #self.clock.tick(8)
            self.events()
            self.update()
            self.draw()
    #pygame.display.update()
game = Game()
#Game.game_message('test', constants.COLOR_WHITE)
#Game.game_message('test',constants.COLOR_BLACK)
song_file = '300Violon.mp3'
pygame.mixer.music.load(song_file)
pygame.mixer.music.play(-1)
game.launch()



