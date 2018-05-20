from level import *
import pygame

def z_sort(obj1, obj2):
    try:
        if obj1.z_order > obj2.z_order: return 1
        elif obj2.z_order > obj1.z_order: return -1
    except AttributeError:
        try:
            z1 = obj1.z_order
        except AttributeError:
            z1 = 0

        try:
            z2 = obj1.z_order
        except AttributeError:
            z2 = 0

        if z1 > z2:   return 1
        elif z2 > z1: return -1

    try:
        y1 = obj1.pos[1]
        y2 = obj2.pos[1]

        if y1 > y2: return 1
        elif y1 < y2: return -1
        return 0
    except AttributeError:
        return 0

    return 0

def collide_rect(rect1, rect2):
    if rect1[1] > rect2[1] + rect2[3] or rect2[1] > rect1[1] + rect1[3]:
        return False
    if rect1[0] > rect2[0] + rect2[2] or rect2[0] > rect1[0] + rect1[2]:
        return False
    return True

class IntroLevel(Level):
    def __init__(self):
        Level.__init__(self, "Intro")

        self.state = 0
        self.anim_counter = 0
        
        self.shing_played = False
        self.shing_image = pygame.image.load('res/intro/shing.png')
        self.shing_image.set_alpha(0)
        self.shing_image.set_colorkey([0, 0, 0])
        self.image_num = -1
        
        self.add_text({'id': "MisterEpicText",
                       'text': "Mister Epic",
                       'font': pygame.font.SysFont('calibri', 65),
                       'size': 65,
                       'position': [0, 0],
                       'color': [255, 255, 255],
                       'alpha': 0,
                       'background': [0, 0, 0],
                       'alignment': [0.5, 1]})
        self.add_text({'id': "PresentsText",
                       'text': "PRESENTS...",
                       'font': pygame.font.SysFont('calibri', 30),
                       'size': 30,
                       'position': [0, 0],
                       'color': [255, 255, 255],
                       'background': [0, 0, 0],
                       'alpha': 0,
                       'alignment': [0.5, 0]})

        self.cr_images = [pygame.image.load('res/intro/prog.png'),
                          pygame.image.load('res/intro/credit1.png'),
                          pygame.image.load('res/intro/credit2.png')]

    def animate(self, screen, fps):
        if self.state == 0:
            if self.image_num == -1:
                self.anim_counter += 60 / fps

                if self.anim_counter < 390:
                    self.draw_text(screen)

                    if self.find_text("MisterEpicText")['size'] != 65 * (screen.get_width() / 640):
                        self.find_text("MisterEpicText")['size'] = 65 * (screen.get_width() / 640)
                        self.find_text("MisterEpicText")['font'] = pygame.font.SysFont('calibri', 65 * (screen.get_width() / 640))
                        
                        self.find_text("PresentsText")['size'] = 30 * (screen.get_width() / 640)
                        self.find_text("PresentsText")['font'] = pygame.font.SysFont('calibri', 30 * (screen.get_width() / 640))
                    
                    self.find_text("MisterEpicText")['position'] = [screen.get_width() / 2, screen.get_height() / 2 + 10]
                    if self.anim_counter > 90 and self.anim_counter < 300:
                        if self.find_text("MisterEpicText")['alpha'] < 255:
                            if 0.8 * (60 / fps) < 0.5:
                                self.find_text("MisterEpicText")['alpha'] += 0.8
                            else:
                                self.find_text("MisterEpicText")['alpha'] += 0.8 * (60 / fps)

                    self.find_text("PresentsText")['position'] = [screen.get_width() / 2, screen.get_height() / 2 + 2]
                    if self.anim_counter > 180 and self.anim_counter < 300:
                        if self.find_text("PresentsText")['alpha'] < 255:
                            if 0.8 * (60 / fps) < 0.5:
                                self.find_text("PresentsText")['alpha'] += 0.8
                            else:
                                self.find_text("PresentsText")['alpha'] += 0.8 * (60 / fps)

                    if self.anim_counter > 60 and self.anim_counter < 120:
                        clr = int((self.anim_counter - 60) * 1.85)
                        if clr > 255:
                            clr = 255
                        pygame.draw.line(screen, [clr, clr, clr],
                                         [screen.get_width() / 4, screen.get_height() / 2],
                                         [screen.get_width() / 4 + ((screen.get_width() / 2) * ((self.anim_counter - 60) / 60.0)), screen.get_height() / 2])
                    if self.anim_counter >= 120:
                        if not self.shing_played:
                            self.shing_played = True
                            pygame.mixer.Sound('res/intro/shing.wav').play()
                        clr = int((self.anim_counter - 60) * 1.85)
                        if clr > 255:
                            clr = 255
                        pygame.draw.line(screen, [clr, clr, clr],
                                         [screen.get_width() / 4, screen.get_height() / 2],
                                         [screen.get_width() / 4 + (screen.get_width() / 2), screen.get_height() / 2])

                        if self.anim_counter < 140:
                            self.shing_image.set_alpha(255 * ((self.anim_counter - 120) / 20.0))
                        elif self.anim_counter < 160:
                            self.shing_image.set_alpha(255)
                        elif self.anim_counter < 180:
                            self.shing_image.set_alpha(255 - (255 * ((self.anim_counter - 160) / 20.0)))
                        else:
                            self.shing_image.set_alpha(0)

                        if self.anim_counter < 180:
                            screen.blit(self.shing_image, [screen.get_width() / 4 + (screen.get_width() / 2) - ((screen.get_width() / 2) * ((self.anim_counter - 120) / 60.0)),
                                                           (screen.get_height() / 2) - (self.shing_image.get_height() / 2)])

                    if self.anim_counter > 330 and self.anim_counter < 390:
                        s = pygame.Surface([screen.get_width(), screen.get_height()])
                        s.set_alpha(255 * ((self.anim_counter - 330) / 60.0))
                        screen.blit(s, [0, 0])

                if self.anim_counter > 450:
                    self.image_num = 0
                    self.anim_counter = 0

            elif self.image_num < len(self.cr_images): # Images
                pyscreen = pygame.Surface(screen.get_size())
                pyscreen.fill([255,255,255])

                img = pygame.transform.scale(self.cr_images[self.image_num], [self.cr_images[self.image_num].get_width()  * (pyscreen.get_width() / 640),
                                                                              self.cr_images[self.image_num].get_height() * (pyscreen.get_width() / 640)])
                pyscreen.blit(img, [screen.get_width()/2 - img.get_width()/2, screen.get_height()/2 - img.get_height()/2])

                self.anim_counter += 120 / fps # x2 fadein/out speed
                
                if self.anim_counter < 60: # Fade in for 1 sec
                    pyscreen.set_alpha(255 * (self.anim_counter / 60.0))
                if self.anim_counter > 240: # Hold for 3 secs, fade out for 1 sec
                    pyscreen.set_alpha(255 - (255 * ((self.anim_counter-240) / 60.0)))

                    if pyscreen.get_alpha() <= 0:
                        self.image_num += 1
                        self.anim_counter = 0
                        pyscreen.set_alpha(0)

                screen.blit(pyscreen, [0, 0])
            else:
                self.state = 1
                self.anim_counter = 0
        elif self.state == 1:
            pass

    def keydown(self, key, uc):
        pass

    def joybuttondown(self, joy, button):
        pass
