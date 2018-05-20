import pygame, textwrap

LEVEL_ANIMATION_DEFAULT = 0
LEVEL_ANIMATION_UPDATESPRITES = 1
LEVEL_ANIMATION_DRAWSPRITES = 2
LEVEL_ANIMATION_DRAWTEXT = 3
LEVEL_ANIMATION_UPDATESPRITESONLY = 4

def z_sort(obj1, obj2):
    try:
        if obj1.z_order > obj2.z_order:
            return 1
        elif obj2.z_order > obj1.z_order:
            return -1
        return 0
    except AttributeError:
        try:
            z1 = obj1.z_order
        except AttributeError:
            z1 = 0

        try:
            z2 = obj1.z_order
        except AttributeError:
            z2 = 0

        if z1 > z2:
            return 1
        elif z2 > z1:
            return -1
        return 0
            
# Base class for Level objects
class Level(pygame.sprite.Sprite):
    """
Base class for Levels, or layers of objects, in the game
    """
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        
        self.background_color = [150,150,150]
        self.name = name
        self.sprites = []
        self.groups = {}
        self.texts = []  # Text = (font, text, color, position)
        self.sounds = {}
        self.paused = False # Pauses the Level (freezes it in time)
        self.stopped_flag = False # For when the Level is done with its work
        self.temp_variable = None

    def set_background(self, color):
        self.background_color = color

    def add_sprite(self, sprite):
        mod = -1
        for sp in self.sprites:
            try:
                if sprite.id == sp.id:
                    mod += 1

                if mod > -1 and sprite.id + str(mod) == sp.id:
                    mod += 1
            except AttributeError:
                continue

        if mod > -1:
            sprite.id = sprite.id.replace('0','').replace('1','').replace('2','').replace('3','').replace('4','').replace('5','').replace('6','').replace('7','').replace('8','').replace('9','') + str(mod)
            
        self.sprites.append(sprite)
        sprite.parent = self

        try:
            sprite.initialize()
        except AttributeError:
            pass

    def remove_sprite(self, sprite):
        if sprite in self.sprites: # Checks if the given sprite is in the Sprite group (error checker)
            sprite.parent = None
            self.sprites.remove(sprite) # If it is, it removes it

            del sprite

    def find_sprite(self, name):
        for sprite in self.sprites:
            try:
                if sprite.id == name:
                    return sprite
            except AttributeError:
                continue
        return None

    def add_group(self, group, name):
        self.groups[name] = group

    def find_text(self, name):
        for text in self.texts:
            if text['id'] == name:
                return text
        return None

    def remove_group(self, name):
        self.groups[name] = pygame.sprite.Group()

    def add_text(self, text):
        mod = -1
        for tx in self.texts:
            try:
                if text['id'] == tx['id']:
                    mod += 1

                if mod > -1 and text['id'] + str(mod) == tx['id']:
                    mod += 1
            except AttributeError:
                continue

        if mod > -1:
            text['id'] = text['id'] + str(mod)
            
        self.texts.append(text)

    def remove_text(self, text):
        if text in self.texts:
            self.texts.remove(text)

    def add_sound(self, sound, name):
        self.sounds[name] = sound

    def colliderect(self, sprite):
        lst = []
        try:
            for spr in self.sprites.sprites():
                if spr.collide_rect != None:
                    if sprite.collide_rect.colliderect(spr) and spr != sprite:
                        lst.append(spr)

            return lst
        except AttributeError:
            return []

# Draws just the sprites
    def draw_sprites(self, screen):
        sprites = self.sprites
        sprites.sort(z_sort)
        layer_0 = []
        layer_x = []
        for sprite in sprites:
            try:
                if sprite.z_order < 1:
                    layer_0.append(sprite)
                else:
                    layer_x.append(sprite)
            except AttributeError:
                layer_0.append(sprite)

        # Renders all of the sprites on the first layer
        for sprite in layer_0:
            try:
                if sprite.visible:
                    try:
                        sprite.render(sprite.parent)
                    except Exception:
                        try:
                            sprite.render(screen)
                        except AttributeError:
                            screen.blit(sprite.image, sprite.rect)
            except AttributeError:
                try:
                    sprite.render(sprite.parent)
                except Exception:
                    try:
                        sprite.render(screen)
                    except AttributeError:
                        screen.blit(sprite.image, sprite.rect)

        # Renders all of the sprites in Spritegroups
        for group in self.groups.values():
            if len(group) > 0:
                for sprite in iter(group):
                    try:
                        if sprite.visible:
                            try:
                                sprite.render(sprite.parent)
                            except Exception:
                                try:
                                    sprite.render(screen)
                                except AttributeError:
                                    screen.blit(sprite.image, sprite.rect)
                    except AttributeError:
                        try:
                            sprite.render(sprite.parent)
                        except Exception:
                            try:
                                sprite.render(screen)
                            except AttributeError:
                                screen.blit(sprite.image, sprite.rect)

        self.draw_text(screen)

        # Renders all sprites above layer 0
        for sprite in layer_x:
            try:
                if sprite.visible:
                    try:
                        sprite.render(sprite.parent)
                    except Exception:
                        try:
                            sprite.render(screen)
                        except AttributeError:
                            screen.blit(sprite.image, sprite.rect)
            except AttributeError:
                try:
                    sprite.render(sprite.parent)
                except Exception:
                    try:
                        sprite.render(screen)
                    except AttributeError:
                        screen.blit(sprite.image, sprite.rect)

    def update_sprites(self, variables = {}):
        if not self.paused:
            sprites = self.sprites
            sprites.sort(z_sort)
            sprites.reverse()
            
            # Updates all of the sprites
            for sprite in sprites:
                try:
                    sprite.update(variables=variables)
                except TypeError:
                    sprite.update()

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        if not self.paused:
                            try:
                                sprite.update(variables=variables)
                            except TypeError:
                                sprite.update()

            for text in self.texts:
                if "update" in text.keys():
                    var_dict = globals()
                    var_dict['self'] = text

                    if 'vars' in text.keys():
                        other_vars = text['vars'].copy()
                        var_dict.update(other_vars)
                    
                    exec(text['update'], var_dict)

# Draws just the text on the screen
    def draw_text(self, screen):
        for text in self.texts:
            if type(text['font']) == str:
                f = pygame.font.Font(text['font'], text['size'])
            else:
                f = text['font']

            if 'aliased' in text.keys():
                antialiased = not text['aliased']
            else:
                antialiased = True

            bg = None
            if 'background' in text.keys():
                bg = text['background']

            if 'char_wrap' in text.keys():
                lines = textwrap.wrap(text['text'], text['char_wrap'])
                text_surface = []
                text_widths = []
                for line in lines:
                    if 'alpha' in text.keys():
                        surf = f.render(line, antialiased, text['color'])
                        text_surf = pygame.Surface([surf.get_width(),
                                                    surf.get_height()])
                        text_surf.blit(surf, [0, 0])

                        text_surf.set_alpha(text['alpha'])
                        text_surface.append(text_surf)
                    else:
                        text_surface.append(f.render(line, antialiased, text['color'], bg))
                    text_widths.append(f.size(line)[0])
            else:
                text_surface = f.render(text['text'], antialiased, text['color'], bg)
                
                if 'alpha' in text.keys():
                    temp_surf = pygame.Surface([text_surface.get_rect().w,
                                                text_surface.get_rect().h])
                    if text['color'] != [255, 0, 255]:
                        temp_surf.fill([255, 0, 255])
                        temp_surf.set_colorkey([255, 0, 255])
                    else:
                        temp_surf.fill([0, 0, 0])
                        temp_surf.set_colorkey([0, 0, 0])
                    temp_surf.blit(text_surface, [0, 0])
                    text_surface = temp_surf

                    
                    text_surface.set_alpha(text['alpha'])
                    
                text_widths = None
                lines = None

            if type(text_surface) == list:
                x_diff = 0
                y_diff = 0
                
                if type(text['alignment']) == str:
                    if text['alignment'].lower() in ['l', 'left', 'left-hand']:
                        x_diff = 0
                    elif text['alignment'].lower() in ['c', 'center', 'centered']:
                        x_diff = 0.5
                    elif text['alignment'].lower() in ['r', 'right', 'right-hand']:
                        x_diff = 1
                    
                elif type(text['alignment']) == list or type(text['alignment']) == tuple:
                    if text['alignment'][0] in ['l', 'L', 'left', 'left-hand', 0]:
                        x_diff = 0
                    elif text['alignment'][0] in ['c', 'C', 'center', 'centered', 0.5]:
                        x_diff = 0.5
                    elif text['alignment'][0] in ['r', 'R', 'right', 'right-hand', 1]:
                        x_diff = 1

                    if text['alignment'][1] in ['l', 'L', 'lowered', 'low', 0,
                                                'd', 'D', 'down']:
                        y_diff = 0
                    elif text['alignment'][1] in ['c', 'C', 'center', 'centered', 0.5]:
                        y_diff = 0.5
                    elif text['alignment'][1] in ['u', 'U' 'up', 'r', 'R', 'raised', 1]:
                        y_diff = 1

                y = int(float(text['position'][1]))
                if y_diff > 0:
                    y -= int((f.size(text['text'])[1] * len(text_surface)) / y_diff)
                index = 0
                
                for surf in text_surface:
                    screen.blit(surf, [text['position'][0] - (f.size(lines[index])[0] * x_diff), y])
                    y += f.size(text['text'])[1]
                    index += 1
            
            else:
                if type(text['alignment']) == str:
                    if text['alignment'].lower() in ['l', 'left', 'left-hand']:
                        screen.blit(text_surface, text['position'])
                    elif text['alignment'].lower() in ['c', 'center', 'centered']:
                        screen.blit(text_surface, [text['position'][0] - (f.size(text['text'])[0] / 2),
                                                   text['position'][1]])
                    elif text['alignment'].lower() in ['r', 'right', 'right-hand']:
                        screen.blit(text_surface, [text['position'][0] - f.size(text['text'])[0],
                                                   text['position'][1]])
                elif type(text['alignment']) == list or type(text['alignment']) == tuple:
                    x_diff = 0
                    y_diff = 0
                    if text['alignment'][0] in ['l', 'L', 'left', 'left-hand', 0]:
                        x_diff = 0
                    elif text['alignment'][0] in ['c', 'C', 'center', 'centered', 0.5]:
                        x_diff = 0.5
                    elif text['alignment'][0] in ['r', 'R', 'right', 'right-hand', 1]:
                        x_diff = 1

                    if text['alignment'][1] in ['l', 'L', 'lowered', 'low', 0,
                                                'd', 'D', 'down']:
                        y_diff = 0
                    elif text['alignment'][1] in ['c', 'C', 'center', 'centered', 0.5]:
                        y_diff = 0.5
                    elif text['alignment'][1] in ['u', 'U' 'up', 'r', 'R', 'raised', 1]:
                        y_diff = 1

                    screen.blit(text_surface, [text['position'][0] - (f.size(text['text'])[0] * x_diff),
                                               text['position'][1] - (f.size(text['text'])[1] * y_diff)])

# Draws everything on the Level
#   SPECIAL_FLAGS: 0 = Default, 1 = Draw & update just the sprites
#                  2 = Only draw the sprites, 3 = Only draw the text
    def animate(self, screen, clock, draw_background = True, special_flags = 0):
        if draw_background:
            # Fills the screen
            screen.fill(self.background_color)

        if special_flags != LEVEL_ANIMATION_DRAWTEXT and special_flags != LEVEL_ANIMATION_UPDATESPRITESONLY:
            self.draw_sprites(screen)
##        if special_flags != LEVEL_ANIMATION_UPDATESPRITES and special_flags != LEVEL_ANIMATION_DRAWSPRITES and special_flags != LEVEL_ANIMATION_UPDATESPRITESONLY:
##            self.draw_text(screen)
        if special_flags != LEVEL_ANIMATION_DRAWSPRITES and special_flags != LEVEL_ANIMATION_DRAWTEXT:
            self.update_sprites()

    def keydown(self, key, unicode):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.keydown(key, unicode)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.keydown(key, unicode)
                        except AttributeError:
                            pass

    def keyup(self, key):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.keyup(key)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.keyup(key)
                        except AttributeError:
                            pass

    def mousebuttondown(self, pos):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.mousebuttondown(pos)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.mousebuttondown(pos)
                        except AttributeError:
                            pass

    def mousebuttonup(self, pos):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.mousebuttonup(pos)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.mousebuttonup(pos)
                        except AttributeError:
                            pass

    def mousemotion(self, pos, rel, buttons):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.mousemotion(pos, rel, buttons)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.mousemotion(pos, rel, buttons)
                        except AttributeError:
                            pass

    def joybuttondown(self, joy, button):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.joybuttondown(joy, button)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.joybuttondown(joy, button)
                        except AttributeError:
                            pass

    def joybuttonup(self, joy, button):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.joybuttonup(joy, button)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.joybuttonup(joy, button)
                        except AttributeError:
                            pass

    def joyaxismotion(self, joy, axis, value):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.joyaxismotion(joy, axis, value)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.joyaxismotion(joy, axis, value)
                        except AttributeError:
                            pass

    def joyballmotion(self, joy, ball, rel):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.joyballmotion(joy, ball, rel)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.joyballmotion(joy, ball, rel)
                        except AttributeError:
                            pass

    def joyhatmotion(self, joy, hat, value):
        if not self.paused:
            for sprite in self.sprites:
                try:
                    sprite.joyhatmotion(joy, hat, value)
                except AttributeError:
                    pass

            # Updates all of the sprites in Spritegroups
            for group in self.groups.values():
                if len(group) > 0:
                    for sprite in iter(group):
                        try:
                            sprite.joyhatmotion(joy, hat, value)
                        except AttributeError:
                            pass
