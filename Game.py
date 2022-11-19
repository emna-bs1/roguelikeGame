import pygame
import Map
import player
import sys
import arm
import vision_field
import os
import guide
import csv
import random
import Collect
import constants

class Game(object):
    def __init__(self):
        global GAME_MESSAGES
        self.GAME_MESSAGES = []
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
        self.missionDone_pos = []

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
        self.game_over = False
        self.dark = pygame.Surface((self.screen_width, self.screen_height))
        self.dark.fill((0,0,0))
        self.light = pygame.image.load('light_350_hard.png')
        self.light = pygame.transform.scale(self.light,(700,700))
        self.light_rect = self.light.get_rect()
        #self._sprites.add(self.hero)


    def generate_map(self):
        if self.load_data():
            self.game_message('welcome,you are about to start a new adventure', constants.COLOR_WHITE)
            self.game_message('collect mission points try to survive', constants.COLOR_WHITE)
            self.game_message('BUT...', constants.COLOR_WHITE)
            self.game_message('be CAREFUL! your enemies won\'t stop catching you', constants.COLOR_WHITE)
            self.gen = Map.Generator()
            self.gen.gen_level()
            self.gen.gen_tiles_level()
            self.gen.parse_level()
            self.pos_x, self.pos_y = Map.generate_hero_initial_pos(self.screen_width, self.screen_height)
            self.arm_position = self.gen.arm_position
            Collect.Collect(self,'ARM',*self.arm_position)
            self.hero = player.Player(self, self.pos_x, self.pos_y)

            for i in range(self.enemies_number) :
                floor = Map.floor_pos[random.randint(0, len(Map.floor_pos) -1 )]
                e = player.Enemy(self,*floor)
                self.enemy_pos.append((floor,e.health))
                self.alter_en = False

            for i in range(self.collect_number):
                floor = Map.floor_pos[random.randint(0, len(Map.floor_pos) - 1)]
                self.mission_pos.append(floor)
                Collect.Collect(self,'MISSION',*floor)

        try:
            money = open('money.txt', 'r')
        except FileNotFoundError:
            pass
        else:
            money =  open('money.txt', 'r')
            amount = money.readline()
            money.close()
            self.hero.collection_coins = float(amount)



    def load_data(self):
        missing = True
        if os.path.exists('game.csv'):
            missing = False
            load_game = open("game.csv","r")
            row_count = sum(1 for row in load_game)

            nbLines = open('nbLines.txt','r')
            nbLines.seek(0)
            var = nbLines.readline()
            try:
                int(var)
            except ValueError:
                return True
            else:
                print(int(var))
                print(row_count)
                if int(var)  != row_count:
                    return True

            if row_count == 0 :
                return True
            load_game.seek(0)
            reader = csv.reader(load_game)
            missionDone = 0
            mission = 0
            for row in reader:
                if row[0] == 'p':
                    self.pos_x = float(row[1])
                    self.pos_y = float(row[2])
                    self.hero = player.Player(self, self.pos_x, self.pos_y)
                    self.hero.health = float(row[3])
                    self.hero.collection_coins = float(row[4])
                if row[0] == 'w':
                    Map.Wall((float(row[1]),float(row[2])))
                elif row[0] == 'o':
                    Map.Obstacle((int(row[1]),int(row[2])))
                elif row[0] == 'f':
                    Map.Floor((float(row[1]),float(row[2])))
                elif row[0] == 'b':
                    Map.Background((float(row[1]),float(row[2])))
                elif row[0] == 'e':
                    e = player.Enemy(self,float(row[1]),float(row[2]))
                    e.health = float(row[3])
                elif row[0] == 'a':
                    self.arm_position = float(row[1]) , float(row[2])
                    Collect.Collect(self, 'ARM', *self.arm_position)
                    if self.arm_position == (-1, -1):
                        self.hero.arm_collected = True
                        self.hero.swap_image(pygame.image.load('topdown-shooter/PNG/Man Brown/manBrown_machine.png'))
                elif row[0] == 'm':
                    mission += 1
                    self.mission_pos.append((float(row[1]),float(row[2])))
                    Collect.Collect(self, 'MISSION', float(row[1]),float(row[2]))
                elif row[0] == 'md':
                    missionDone += 1
                    self.missionDone_pos.append((float(row[1]),float(row[2])))
                    Collect.Collect(self,'FLAG',float(row[1]),float(row[2]))
                self.hero.collection_mission = missionDone
            load_game.close()

        return missing


    def save_data(self):
        game_state = open("game.csv","w",newline="")
        nbLines = 1
        writer = csv.writer(game_state)
        #writer.writerow(['object','x','y'])
        writer.writerow(['p',str(self.hero.position.x),str(self.hero.position.y), str(self.hero.health), str(self.hero.collection_coins)])

        elements = [{'name':'w','ref':Map.wall_pos},
                    {'name':'f','ref':Map.floor_pos},
                    {'name':'b','ref':Map.background_pos},
                    {'name':'o','ref':Map.obstacle_pos},
                    {'name':'e','ref':self.enemy_pos},
                    {'name':'a','ref':[self.arm_position]},
                    {'name':'m','ref':self.mission_pos},
                    {'name':'md','ref':self.missionDone_pos}]
        for element in elements:
            for pos in element['ref']:
                if element['name'] == 'e':
                    position, health = pos
                    writer.writerow([element['name'], str(position[0]), str(position[1]), str(health)])
                else:
                    writer.writerow([element['name'], str(pos[0]), str(pos[1])])
                nbLines += 1
        save_nbLines = open("nbLines.txt",'w')
        save_nbLines.write(str(nbLines))
        save_nbLines.close()
        game_state.close()
        if not os.path.exists('money.txt'):
            open('money.txt', 'w+')

        money = open('money.txt', 'w')
        money.write(str(self.hero.collection_coins))
        money.close()

    def game_won(self):
        if self.hero.collection_mission == self.collect_number:
            self.game_over = True

            self.draw_text(self.screen,
                      "CONGRATULATIONS! YOU WON",
                      constants.FONT_TITLE_SCREEN,
                      (self.screen_width / 2, self.screen_height / 2),
                      constants.COLOR_WHITE, center=True)
            pygame.display.update()
            pygame.time.wait(2000)


    def death_player(self):
        if self.hero.health <= 0:
            self.game_over = True
            self.screen.fill(constants.COLOR_BLACK)
            #screen_center = (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2)
            self.draw_text(self.screen,
                      "GAME OVER",
                      constants.FONT_TITLE_SCREEN,
                      (self.screen_width / 2, self.screen_height / 2),
                      constants.COLOR_WHITE, center=True)
            pygame.display.update()
            pygame.time.wait(2000)

    def events(self):
        if self.game_over :
            if not os.path.exists('money.txt'):
                open('money.txt','w+')

            money = open('money.txt','w')
            money.write(str(self.hero.collection_coins))
            money.close()

            try:
                os.remove('game.csv')
            except FileNotFoundError:
                pass
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                if self.hero.collection_mission != self.collect_number:
                    self.save_data()
                else:
                    os.remove('game.csv')
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE :
                    if self.hero.collection_mission != self.collect_number:
                        self.save_data()
                    else:
                        os.remove('game.csv')
                    pygame.quit()
                    sys.exit()
        self.death_player()
        self.game_won()


    def game_message(self, game_msg, msg_color):
        self.GAME_MESSAGES.append((game_msg, msg_color))

    def draw_messages(self):
        if len(self.GAME_MESSAGES) <= constants.NUM_MESSAGES:
            to_draw = self.GAME_MESSAGES
        else:
            to_draw = self.GAME_MESSAGES[-(constants.NUM_MESSAGES):]
        text_height = self.helper_text_height(constants.FONT_MESSAGE_TEXT)
        start_y = (self.screen_height -
                   (constants.NUM_MESSAGES * text_height)) - 1000
        i = 0
        for message, color in to_draw:
            self.draw_text(self.screen,
                      message,
                      constants.FONT_MESSAGE_TEXT,
                        (self.screen_width / 3  ,start_y + (i * text_height) ),color)
            i += 1
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
            self.screen.blit(a.rotated_image,self.camera.move(a))

            #pygame.draw.rect(self.screen, (255, 255, 255), self.camera.move_rect(a.rect), 4)

        for col in self.collection:
            self.screen.blit(col.image,self.camera.move(col))

        self.flush_light()
        self.screen.blit(self.mission_icon,(20,50))

        self.screen.blit(self.mission, (100, 50))
        self.screen.blit(self.coin_icon, (23, 120))
        self.screen.blit(self.coins, (100, 120))
        self.draw_messages()


        for sprite in self._sprites:
            sprite.draw_health_bar()
            self.screen.blit(sprite.image,self.camera.move(sprite))
        #self.camera.draw(self.screen)
        #self.guide_gr.draw(self.screen)
        self.guide.draw()
        pygame.display.flip()

    def draw_text(self,screen, text_to_display, font,
                  coords, text_color, back_color=None, center=False):
        # get both the surface and rectangle of the desired message
        text_surf, text_rect = self.helper_text_objects(text_to_display, font, text_color, back_color)

        # adjust the location of the surface based on the coordinates
        if not center:
            text_rect.midtop = coords
        else:
            text_rect.center = coords

        # draw the text onto the display surface.
        screen.blit(text_surf, text_rect)


    def helper_text_objects(self, incoming_text, incoming_font, incoming_color, incoming_bg):
        if incoming_bg:
            Text_surface = incoming_font.render(incoming_text,
                                                False,
                                                incoming_color,
                                                incoming_bg)
        else:  # otherwise, render without a background.

            Text_surface = incoming_font.render(incoming_text,
                                        False,
                                        incoming_color)
        return Text_surface, Text_surface.get_rect()


    def helper_text_height(self,font):
        # render the font out
        font_rect = font.render('a', False, (0, 0, 0)).get_rect()
        return font_rect.height

    def helper_text_width(self,font):
        # render the font out
        font_rect = font.render('a', False, (0, 0, 0)).get_rect()
        return font_rect.width

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
                self.mission_pos.remove(col.pos)
                Collect.Collect(self,'FLAG',*col.pos)
                self.missionDone_pos.append(col.pos)
                self.game_message('good job, you earned a mission object',constants.COLOR_WHITE)
            elif col.type == 'COIN':
                self.hero.collection_coins += 10
                self.game_message('YES,MONEY !',constants.COLOR_WHITE)

            elif col.type == 'ARM':
                self.hero.arm_collected = True
                self.arm_position = -1 ,-1
                self.hero.swap_image(pygame.image.load('topdown-shooter/PNG/Man Brown/manBrown_machine.png'))
                self.game_message('it\'s an arm, time for party!',constants.COLOR_WHITE)



        kill_hero = pygame.sprite.groupcollide(self._sprites,self.sp, False,False)
        for killed in kill_hero:
            killed.health -= player.killing_power
            self.game_message('OH NO! CAREFUL!!', constants.COLOR_WHITE)

        self.sp.update()

        self.enemy_pos = []
        for sp in self.sp:
            self.enemy_pos.append((sp.position, sp.health))

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
song_file = '300Violon.mp3'
pygame.mixer.music.load(song_file)
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
game.launch()


