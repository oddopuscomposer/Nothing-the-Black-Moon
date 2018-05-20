# -*- coding: cp1252 -*-
import pygame, time, copy

class GameSprite(pygame.sprite.Sprite):
    """
img - IMAGE USED
img_width, img_height - DIMENSIONS OF SINGLE IMAGE
spr_width, spr_height - DIMENSIONS OF SPRITESHEET FRAMES
    """
    def __init__(self, img, pos, img_width, img_height, spr_width, spr_height, initial_frame = 0, collide_rect = None, name = ""):
        if type(img) == str:
            self.image = pygame.image.load(img)
        else:
            self.image = img
        self.rect = self.image.get_rect()
        self.rect.w /= img_width
        self.rect.h /= img_height
        self.rect.midbottom = pos

        self.pos = pos

        self.img_width, self.img_height = img_width, img_height
        self.spr_width, self.spr_height = spr_width, spr_height

        self.animations = {}
        self.animation_lengths = {}
        self.frame = initial_frame
        self.frames = []
        for frameY in range(self.spr_height):
            for frameX in range(self. spr_width):
                surf = pygame.Surface([self.img_width, self.img_height])
                surf.fill([255, 0, 255])
                surf.set_colorkey([255, 0, 255])
                mask = pygame.Surface([self.img_width, self.img_height], pygame.SRCALPHA)
                
                surf.blit(self.image, [0, 0, 0, 0],
                          [self.img_width * frameX, self.img_height * frameY, self.img_width, self.img_height])
                self.frames.append(surf)
        
        self.animation = None
        self.animation_frame = 0
        self.animation_counter = 0
        self.main_img = True
        self.playing  = False
        self.paused   = False

        if collide_rect != None:
            self.collide_rect = pygame.Rect(collide_rect)
        else:
            self.collide_rect = None
        self.scale = 1
        self.flip = [False, False]
        self.move_vector = [0, 0]
        self.movement_speed = 1
        self.dest = None
        self.opacity = 255

        self.animation_state = 0
        self.animation_states = []

        self.id = name

        self.visible = True

        self.parent = None
        self.z_order = 0

        self.timer = time.time()
        self.elapsed = 0

        self.temp_variable = {}

        self.update_func = None

    def __str__(self):
        return "Sprite " + str([self.img_width, self.img_height, self.spr_width,
                                self.spr_height]) + ", ID: " + self.id

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        img = pygame.Surface([self.image.get_width(), self.image.get_height()], self.image.get_flags())

        if img.get_flags() & pygame.SRCALPHA:
            img.blit(self.image, [0, 0])
        else:
            if self.image.get_colorkey() == None:
                img.fill([255, 0, 255])
                img.blit(self.image, [0, 0])
            else:
                img.fill([255, 0, 255])
                img.blit(self.image, [0, 0])
        spr = GameSprite(img, self.pos[:], copy.deepcopy(self.img_width), copy.deepcopy(self.img_height), copy.deepcopy(self.spr_width), copy.deepcopy(self.spr_height))

        if self.collide_rect != None:
            spr.collide_rect = self.collide_rect.copy()

        for key in self.temp_variable.keys():
            spr.temp_variable[key] = self.temp_variable.copy()[key]

        spr.visible = self.visible
        spr.id = copy.deepcopy(self.id)
        spr.update_func = self.update_func

        for animation in self.animations.keys():
            spr.add_animation(animation, self.animations[animation], self.animation_lengths[animation] * 1000)

        spr.z_order = self.z_order
        spr.opacity = copy.copy(self.opacity)
        spr.flip = self.flip[:]
        spr.scale = copy.copy(self.scale)

        spr.main_img = copy.copy(self.main_img)
        spr.playing  = copy.copy(self.playing)
        spr.paused   = copy.copy(self.paused)

        return spr

    def __deepcopy__(self, memo = None):
        spr = self.__copy__()
        spr.dest = copy.deepcopy(self.dest)
        spr.move_vector = self.move_vector[:]

        return spr

    def copy(self):
        return self.__copy__()

    def add_animation(self, anim_name, anim_frames, anim_length = 1):
        self.animations[anim_name] = anim_frames
        self.animation_lengths[anim_name] = anim_length / 1000.0

    def play_animation(self, anim_name):
        if anim_name in self.animations.keys():
            self.animation = anim_name
            self.animation_frame = 0
            self.animation_counter = 0
            self.playing = True
            self.frame = self.animations[anim_name][0]
            self.paused = False
            self.timer = time.time()

    def pause_animation(self):
        self.paused = True
        self.elapsed = time.time()

    def unpause_animation(self):
        self.paused = False
        self.timer -= time.time() - self.elapsed
        self.elapsed = 0

    def stop_animation(self, anim_name = ""):
        self.animation_state = 0
        self.animation_states = []
        
        self.animation = None
        self.animation_frame = 0
        self.animation_counter = 0
        self.playing = False
        self.paused = False

    def render(self, screen, offset = [0, 0]):
        if self.visible:
            surf = pygame.Surface([1, 1])
            img_width, img_height = self.img_width, self.img_height
            if self.playing:
                if type(self.animations[self.animation][0]) == int:
                    if type(self.frame) != int:
                        self.frame = 0
                    surf = self.frames[self.frame]
                    img_width, img_height = self.img_width, self.img_height
                elif type(self.animations[self.animation][0]) == pygame.Surface:
                    surf = self.animations[self.animation][self.animation_frame]
                    rect = surf.get_rect()
                    img_width, img_height = rect.w, rect.h
            else:
                if type(self.frame) != int:
                    self.frame = 0
                surf = self.frames[self.frame]
                img_width, img_height = self.img_width, self.img_height
            
            nova_surf = pygame.transform.scale(surf, [int(img_width  * self.scale),
                                                      int(img_height * self.scale)])
            nova_surf = pygame.transform.flip(nova_surf, self.flip[0], self.flip[1])
            nova_surf.set_colorkey(surf.get_colorkey())
            nova_rect = nova_surf.get_rect()
            nova_rect.midbottom = self.pos
            nova_surf.set_alpha(self.opacity)
            nova_rect.x += offset[0]
            nova_rect.y += offset[1]
            screen.blit(nova_surf, nova_rect)
            return [nova_surf, nova_rect]

    def update(self, variables = {}):
        self.pos[0] += self.move_vector[0]
        self.pos[1] += self.move_vector[1]
        
        if self.dest != None:
            if self.dest[0] - self.pos[0] > self.movement_speed + 1:
                self.move_vector[0] = self.movement_speed
            elif self.dest[0] - self.pos[0] < -(self.movement_speed + 1):
                self.move_vector[0] = -self.movement_speed
            else:
                self.move_vector[0] = 0
            if self.dest[1] - self.pos[1] > self.movement_speed + 1:
                self.move_vector[1] = self.movement_speed
            elif self.dest[1] - self.pos[1] < -(self.movement_speed + 1):
                self.move_vector[1] = -self.movement_speed
            else:
                self.move_vector[1] = 0

            if self.move_vector[0] == 0 and self.move_vector[1] == 0:
                self.pos = self.dest[:]
                self.dest = None
        
        if self.playing and not self.paused:
            if time.time() - self.timer > self.animation_lengths[self.animation]:
                self.timer = time.time()
                self.animation_frame += 1
                if self.animation_frame == len(self.animations[self.animation]):
                    self.animation_frame = 0
                if type(self.animations[self.animation][0]) == int:
                    self.frame = self.animations[self.animation][self.animation_frame]
                elif type(self.animations[self.animation][0]) == pygame.Surface:
                    self.frame = 0

        if self.update_func != None:
            glob = globals()
            for key in variables.keys():
                glob[key] = variables[key]
            exec(self.update_func, glob, locals())

# Load sprite from file, lines, or pre-existing sprite
def load_sprite(filename, pos = [0, 0]):
    if type(filename) == GameSprite:
        return filename.copy()
    else:
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
        except Exception:
            lines = filename

        sprite_dict = {'initialframe': 0, 'class': "GameSprite"}
        temp_variable = {}
    for line in lines:
        if len(line.split('=')) > 1:
            key = line.split('=')[0]
            val = line.split('=')[1]

            if val[-1] == '\n':
                val = val[0:len(val) - 1]

            if key == 'animation':
                args = val.split(',')
                anim = {}
                anim['id'] = args[0]
                anim['frames'] = args[1:len(args) - 1]
                frames = []
                for frame in anim['frames']:
                    try:
                        frames.append(int(frame))
                    except ValueError:
                        if frame.find('spritesheet<') == 0:
                            frame = frame.replace('spritesheet<','')
                            frame = frame.replace('>','')
                            frame = frame.split('|')

                            sheet_img = pygame.image.load('res/sprites/' + frame[0])
                            sheet_w, sheet_h = sheet_img.get_rect().w, sheet_img.get_rect().h
                            image_w, image_h = sheet_w / int(frame[1]), sheet_h / int(frame[2])
                            
                            frames = frames + create_spritesheet_animation('res/sprites/' + frame[0],
                                                                           image_w, image_h,
                                                                           int(frame[1]), int(frame[2]))
                        else:
                            frames.append(pygame.image.load('res/sprites/' + frame))
                            
                anim['frames'] = frames
                anim['time'] = int(args[-1])
                            
                if 'animations' in sprite_dict.keys():
                    sprite_dict['animations'].append(anim)
                else:
                    sprite_dict['animations'] = [anim]
            else:
                if key in ['spritewidth', 'spriteheight', 'initialframe', 'movespeed']:
                    val = int(val)
                if key in ['colliderect', 'collide_rect', 'interactrect', 'interact_rect']:
                    try:
                        val = [int(val.split(',')[0]), int(val.split(',')[1]), int(val.split(',')[2]), int(val.split(',')[3])]
                    except Exception:
                        pass
                if key in ['hardcollision', 'hidden']:
                    val = val in ['True', 't', 'Yes', 'yes', 'y', 'T', 'Y', 'true', "TRUE", "YES"]
                if key == 'temp_variable':
                    temp_variable[val.split('|')[0]] = val.split('|')[1]
                    
                sprite_dict[key] = val
        
    surfrect = pygame.image.load('res/sprites/' + sprite_dict['img']).get_rect()
    spr = GameSprite('res/sprites/' + sprite_dict['img'], pos,
                     surfrect.w / sprite_dict['spritewidth'], surfrect.h / sprite_dict['spriteheight'],
                     sprite_dict['spritewidth'], sprite_dict['spriteheight'],
                     name=sprite_dict['id'])
    spr.temp_variable = {}
    if 'animations' in sprite_dict.keys():
        for anim in sprite_dict['animations']:
            spr.add_animation(anim['id'], anim['frames'], anim['time'])

    if 'movespeed' in sprite_dict.keys():
        spr.movement_speed = sprite_dict['movespeed']

    if 'colliderect' in sprite_dict.keys():
        spr.collide_rect = pygame.Rect(sprite_dict['colliderect'])
    if 'collide_rect' in sprite_dict.keys():
        spr.collide_rect = pygame.Rect(sprite_dict['colliderect'])

    if 'interactrect' in sprite_dict.keys():
        spr.temp_variable['interact_rect'] = pygame.Rect(sprite_dict['interactrect'])
    if 'interact_rect' in sprite_dict.keys():
        spr.temp_variable['interact_rect'] = pygame.Rect(sprite_dict['interactrect'])

    if 'hidden' in sprite_dict.keys():
        spr.visible = not sprite_dict['hidden']

    if 'zorder' in sprite_dict.keys():
        spr.z_order = sprite_dict['zorder']
        
    if 'update' in sprite_dict.keys() or 'update_function' in sprite_dict.keys():
        if 'update' in sprite_dict.keys():
            loc = sprite_dict['update']
        else:
            loc = sprite_dict['update_function']
        f = open(loc, 'r')
        l = f.readlines()
        f.close()
        spr.update_func = ''.join(l)

    for k in temp_variable.keys():
        spr.temp_variable[k] = temp_variable[k]

    return spr
