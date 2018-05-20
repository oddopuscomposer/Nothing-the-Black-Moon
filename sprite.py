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

if __name__ == '__main__': # Sprite test
    from level import Level
    from constants import SPRITE_LIBRARY
    import time, traceback

    try:
        pygame.init()

        screen = pygame.display.set_mode([640, 360])
        pygame.display.set_caption("SGE Sprite Test")

        FPS = 60
        ELAPSED = time.time()

        KEYS = SPRITE_LIBRARY.keys()
        ID = 0

        lv = Level('Sprite Test')
        lv.background_color = [85, 85, 85]
        lv.add_text({'id': "spriteNameShad",
                     'text': "Sprite " + str(ID) + ' <' + KEYS[ID] + '>',
                     'color': [0, 0, 0],
                     'size': 26,
                     'font': 'res/fonts/consolas.ttf',
                     'alignment': [0, 0],
                     'position': [2, 4]})
        lv.add_text({'id': "spriteName",
                     'text': "Sprite " + str(ID) + ' <' + KEYS[ID] + '>',
                     'color': [255, 255, 255],
                     'size': 26,
                     'font': 'res/fonts/consolas.ttf',
                     'alignment': [0, 0],
                     'position': [2, 2]})

        lv.add_text({'id': "spriteFrameShad",
                     'text': "Frame " + str(ID),
                     'color': [0, 0, 0],
                     'size': 26,
                     'font': 'res/fonts/consolas.ttf',
                     'alignment': [0, 0],
                     'position': [2, 28]})
        lv.add_text({'id': "spriteFrame",
                     'text': "Frame " + str(ID),
                     'color': [255, 255, 255],
                     'size': 26,
                     'font': 'res/fonts/consolas.ttf',
                     'alignment': [0, 0],
                     'position': [2, 26]})

        lv.add_sprite(SPRITE_LIBRARY[KEYS[ID]])
        lv.sprites[0].pos = [120, 300]
        lv.sprites[0].scale = 2
        SELECTED = 0
        ANIMS = lv.sprites[0].animations.keys()
        ANIMS.sort()

        for spr in SPRITE_LIBRARY.keys():
            SPRITE_LIBRARY[spr].update_func = None
            SPRITE_LIBRARY[spr].visible = True

        running = True
        while running:
            pygame.display.flip()

            txt = "Sprite " + hex(ID).replace('0x', '').upper() + ' <' + KEYS[ID] + '>'
            lv.find_text('spriteName')['text'] = txt
            lv.find_text('spriteNameShad')['text'] = txt

            txt = "Frame "
            if type(lv.sprites[0].frame) == int:
                txt = txt + str(lv.sprites[0].frame)
            else:
                txt = txt + '0'
            
            if lv.sprites[0].animation != None:
                txt = txt + ' <AF ' + str(lv.sprites[0].animation_frame) + ', T ' + str(int(lv.sprites[0].animation_lengths[lv.sprites[0].animation] * 1000)) + ' ms'
                if lv.sprites[0].paused:
                    txt = txt + ', P>'
                else:
                    txt = txt + '>'
            lv.find_text('spriteFrame')['text'] = txt
            lv.find_text('spriteFrameShad')['text'] = txt
            lv.animate(screen, FPS)
            
            if len(ANIMS) > 0:
                f = pygame.font.Font('res/fonts/consolas.ttf', 26)

                screen.blit(f.render("ANIMATIONS:", True, [0, 0, 0]), [640 - f.size("ANIMATIONS:")[0], 4])
                screen.blit(f.render("ANIMATIONS:", True, [255, 255, 0]), [640 - f.size("ANIMATIONS:")[0], 2])

                y = 26
                for animation in ANIMS:
                    clr = [255, 255, 255]
                    if animation == lv.sprites[0].animation and ANIMS[SELECTED] == animation:
                        clr = [255, 0, 0]
                    elif animation == lv.sprites[0].animation:
                        clr = [255, 128, 0]
                    elif ANIMS[SELECTED] == animation:
                        clr = [40, 122, 255]
                        
                    screen.blit(f.render(animation, True, lv.find_text("spriteNameShad")['color']), [640 - f.size(animation)[0] - 4, y + 2])
                    screen.blit(f.render(animation, True, clr), [640 - f.size(animation)[0] - 4, y])

                    y += 26
            
            try:
                FPS = 1 / (time.time() - ELAPSED)
            except ZeroDivisionError:
                FPS = 100
            ELAPSED = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        lv.remove_sprite(lv.sprites[0])
                        ID += 1
                        if ID > len(KEYS) - 1:
                            ID = 0
                        lv.add_sprite(SPRITE_LIBRARY[KEYS[ID]])
                        lv.sprites[0].pos = [120, 300]
                        lv.sprites[0].scale = 2
                        ANIMS = lv.sprites[0].animations.keys()
                        ANIMS.sort()
                        SELECTED = 0

                    if event.key == pygame.K_LEFT:
                        lv.remove_sprite(lv.sprites[0])
                        ID -= 1
                        if ID < 0:
                            ID = len(KEYS) - 1
                        lv.add_sprite(SPRITE_LIBRARY[KEYS[ID]])
                        lv.sprites[0].pos = [120, 300]
                        lv.sprites[0].scale = 2
                        ANIMS = lv.sprites[0].animations.keys()
                        ANIMS.sort()
                        SELECTED = 0

                    if event.key == pygame.K_UP:
                        SELECTED -= 1
                        if SELECTED < 0:
                            SELECTED = len(ANIMS) - 1

                    if event.key == pygame.K_DOWN:
                        SELECTED += 1
                        if SELECTED > len(ANIMS) - 1:
                            SELECTED = 0

                    if event.key in [pygame.K_SPACE, pygame.K_RETURN] and len(ANIMS) > 0:
                        lv.sprites[0].stop_animation()
                        lv.sprites[0].play_animation(ANIMS[SELECTED])

                    if event.key == pygame.K_ESCAPE:
                        lv.sprites[0].stop_animation()

                    if event.key == pygame.K_TAB:
                        lv.sprites[0].flip[0] = not lv.sprites[0].flip[0]

                    if event.key in [pygame.K_p, pygame.K_PAUSE]:
                        if lv.sprites[0].paused:
                            lv.sprites[0].unpause_animation()
                        else:
                            lv.sprites[0].pause_animation()

        pygame.quit()

    except Exception as e:
        pygame.quit()

        print "The SGE Sprite Viewer has crashed from the following exception:"
        print "----------------------------------------------------------------"
        print traceback.format_exc()
        print "________________________________________________________________"
        raw_input("Press [ENTER] to exit")
