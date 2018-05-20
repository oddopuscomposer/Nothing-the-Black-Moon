from sprite import GameSprite
import copy, pygame
import os, sys

def create_spritesheet_animation(img, img_width, img_height, spr_width, spr_height):
    img_surf = pygame.image.load(img)

    return_list = []
    for y in range(spr_height):
        for x in range(spr_width):
            surf = pygame.Surface([img_width, img_height])
            surf.fill([255, 0, 255])
            surf.set_colorkey([255, 0, 255])
            surf.blit(img_surf, [0, 0, img_width, img_height], [x*img_width, y*img_height,
                                                                img_width, img_height])
            return_list.append(surf)

    return return_list

def load_sprite(spritename, pos = [0, 0]):
    if type(spritename) == GameSprite:
        return spritename
    else:
        try:
            f = open('res/sprites/' + spritename + '.srsf', 'r')
            lines = f.readlines()
            f.close()
        except Exception:
            lines = spritename

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
                            sheet_surf = pygame.image.load('res/sprites/' + frame)
                            sheet_img = pygame.Surface(sheet_surf.get_size())
                            sheet_img.fill([255, 0, 255])
                            sheet_img.set_colorkey([255, 0, 255])
                            sheet_img.blit(sheet_surf, [0, 0])
                            frames.append(sheet_img)
                            
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
                if key in ['hardcollision', 'hard_collision', 'hidden']:
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
        spr.collide_rect = pygame.Rect(sprite_dict['collide_rect'])

    if 'interactrect' in sprite_dict.keys():
        spr.temp_variable['interact_rect'] = pygame.Rect(sprite_dict['interactrect'])
    if 'interact_rect' in sprite_dict.keys():
        spr.temp_variable['interact_rect'] = pygame.Rect(sprite_dict['interact_rect'])

    if 'hardcollision' in sprite_dict.keys():
        spr.temp_variable['hardcollision'] = sprite_dict['hardcollision']
    if 'hard_collision' in sprite_dict.keys():
        spr.temp_variable['hardcollision'] = sprite_dict['hard_collision']

    if 'hidden' in sprite_dict.keys():
        spr.visible = not sprite_dict['hidden']

    if 'zorder' in sprite_dict.keys():
        spr.z_order = sprite_dict['zorder']
        
    if 'update' in sprite_dict.keys() or 'update_function' in sprite_dict.keys():
        if 'update' in sprite_dict.keys():
            loc = sprite_dict['update']
        else:
            loc = sprite_dict['update_function']
        f = open('res/sprites/updatefunctions/' + loc, 'r')
        l = f.readlines()
        f.close()
        spr.update_func = ''.join(l)

    for k in temp_variable.keys():
        spr.temp_variable[k] = temp_variable[k]

    return spr

# LOAD ALL SPRITES FROM res/sprites INTO A DICTIONARY
def load_all_sprites():
    spritedir = os.getcwd() + '\\res\\sprites'
    spritefiles = [f for f in os.listdir(spritedir) if os.path.isfile(os.path.join(spritedir, f))]
    spritenames = []
    for f in spritefiles:
        if f.find('.srsf') != -1:
            spritenames.append(f.replace('.srsf', ''))

    # Now that there are no other filetypes...
    sprites = {}
    for name in spritenames:
        sp = load_sprite(name)
        sprites[sp.id] = sp
    return sprites

SPRITE_LIBRARY = load_all_sprites()

def parse_lines(lines, splitter=','):
    d = {}
    for line in lines:
        key = line.split('=')[0]
        val = line.split('=')[1]

        if val[-1] == '\n':
            val = val[0:len(val) - 1]
        if len(val.split(splitter)) < 2:
            try:
                val = int(val)
            except ValueError:
                pass
        else:
            lst = []
            for value in val.split(splitter):
                try:
                    value = int(value)
                except ValueError:
                    pass
                if value == 'None':
                    value = None

                if value not in ['', '\n']:
                    lst.append(value)
            val = lst[:]

        if val == 'None':
            val = None
        
        d[key] = val
    return d

# Party
def load_party(party_strings):
    party = []
    for member in party_strings:
        member_string = member
        
        member_file = open('res/party/' + member, 'r')
        memberlines = member_file.readlines()
        member_id = member.split('.')[0]
        member_file.close()

        member = parse_lines(memberlines)
        member['sprite_id'] = copy.copy(member['sprite'])
        if member['sprite'] in SPRITE_LIBRARY.keys():
            member['sprite'] = copy.copy(SPRITE_LIBRARY[member['sprite']])
        else:
            member['sprite'] = load_sprite(member['sprite'])

        equip = []
        for equipment in member['equipment']:
            if equipment not in ["None", None, '']:
                equip.append(ITEM_LIBRARY[equipment])
            else:
                equip.append(None)
        member['equipment'] = equip

        try:
            levelup_file = open('res/party/' + member_id + '_levelup.txt', 'r')
            levelup_lines = levelup_file.readlines()
            levelup_file.close()
            member['levelup'] = parse_lines(levelup_lines)
        except IOError:
            member['levelup'] = None

        member['id'] = member_string.split('.')[0]

        party.append(member)

    return party

def import_party(filename = 'default.party'):
    global SPRITE_LIBRARY
    party_file = open('res/party/' + filename, 'r')
    party_members = party_file.readlines()
    party_file.close()

    party_strings = []
    for member in party_members:
        if member[-1] == '\n':
            party_strings.append(member[0:len(member)-1])
        else:
            party_strings.append(member)

    return load_party(party_strings)

DEFAULT_PARTY = import_party()

# Leveling up
def LEVEL_UP(char):
    char['LVL'] += 1
    char['NLV'] *= 1.25
    char['NLV'] = (int(char['NLV']) // 5) * 5

    if char['LVL'] in [10, 25, 50]:
        char['bag_size'] += 1

    # Up HP
    change = char['levelup']['HP'][0] + (float(char['levelup']['HP'][1]) *
                                          char['LVL'] ** (float(char['levelup']['HP'][2]) / char['levelup']['HP'][3]))
    change -= char['levelup']['HP'][0] + (float(char['levelup']['HP'][1]) *
                                           (char['LVL'] - 1) ** (float(char['levelup']['HP'][2]) / char['levelup']['HP'][3]))
    char['HP'][1] += int(round(change * random.uniform(0.7, 1.5)))

    # Up SP
    change = char['levelup']['SP'][0] + (float(char['levelup']['SP'][1]) *
                                          char['LVL'] ** (float(char['levelup']['SP'][2]) / char['levelup']['SP'][3]))
    change -= char['levelup']['SP'][0] + (float(char['levelup']['SP'][1]) *
                                           (char['LVL'] - 1) ** (float(char['levelup']['SP'][2]) / char['levelup']['SP'][3]))
    char['SP'][1] += int(round(change * random.uniform(0.7, 1.5)))

    # Up STR
    if 'STR' in char['levelup'].keys():
        change = char['levelup']['STR'][0] + (float(char['levelup']['STR'][1]) *
                                              char['LVL'] ** (float(char['levelup']['STR'][2]) / char['levelup']['STR'][3]))
        change -= char['levelup']['STR'][0] + (float(char['levelup']['STR'][1]) *
                                               (char['LVL'] - 1) ** (float(char['levelup']['STR'][2]) / char['levelup']['STR'][3]))
        char['STR'] += int(round(change * random.uniform(0.7, 1.5)))

    # Up EVA
    if 'EVA' in char['levelup'].keys():
        change = char['levelup']['EVA'][0] + (float(char['levelup']['EVA'][1]) *
                                              char['LVL'] ** (float(char['levelup']['EVA'][2]) / char['levelup']['EVA'][3]))
        change -= char['levelup']['EVA'][0] + (float(char['levelup']['EVA'][1]) *
                                               (char['LVL'] - 1) ** (float(char['levelup']['EVA'][2]) / char['levelup']['EVA'][3]))
        char['EVA'] += change * random.uniform(0.7, 1.5)
        char['EVA'] = round(char['EVA'], 1)

    # Up ACC
    if 'ACC' in char['levelup'].keys():
        char['ACC'] += float(char['levelup']['ACC'][0]) / char['levelup']['ACC'][1]
        if char['ACC'] >= 100:
            char['ACC'] = 100
    # Up WIS
    if 'WIS' in char['levelup'].keys():
        change = char['levelup']['WIS'][0] + (float(char['levelup']['WIS'][1]) *
                                          char['LVL'] ** (float(char['levelup']['WIS'][2]) / char['levelup']['WIS'][3]))
        change -= char['levelup']['WIS'][0] + (float(char['levelup']['WIS'][1]) *
                                               (char['LVL'] - 1) ** (float(char['levelup']['WIS'][2]) / char['levelup']['WIS'][3]))
        char['WIS'] += int(round(change * random.uniform(0.7, 1.5)))

    # Up INT
    if 'INT' in char['levelup'].keys():
        change = char['levelup']['INT'][0] + (float(char['levelup']['INT'][1]) *
                                          char['LVL'] ** (float(char['levelup']['INT'][2]) / char['levelup']['INT'][3]))
        change -= char['levelup']['INT'][0] + (float(char['levelup']['INT'][1]) *
                                               (char['LVL'] - 1) ** (float(char['levelup']['INT'][2]) / char['levelup']['INT'][3]))
        char['INT'] += int(round(change * random.uniform(0.7, 1.5)))

    # Up SPD
    if 'SPD' in char['levelup'].keys():
        change = char['levelup']['SPD'][0] + (float(char['levelup']['SPD'][1]) *
                                          char['LVL'] ** (float(char['levelup']['SPD'][2]) / char['levelup']['SPD'][3]))
        change -= char['levelup']['SPD'][0] + (float(char['levelup']['SPD'][1]) *
                                               (char['LVL'] - 1) ** (float(char['levelup']['SPD'][2]) / char['levelup']['SPD'][3]))
        char['SPD'] += change * random.uniform(0.7, 1.5)
        char['SPD'] = round(char['SPD'], 1)

    return char
