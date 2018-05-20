import os, pygame
from constants import SPRITE_LIBRARY, DEFAULT_PARTY
from level import Level
from sprite import GameSprite
from smap import *

RECTS = {}
ENTRANCES = {}

# Map Level class for game maps
class MapLevel(Level):
    def __init__(self, map_id, entrance_id, previous_music_info = {}, prev_vars = {'maps': {},
                                                                                   'custom_names': {},
                                                                                   'played_maps': []}, party = DEFAULT_PARTY, maps = {}, money = 0, keys = 'default'):
        global RECTS, ENTRANCES, PLAYER_SPRITE
        self.sprites = []
        Level.__init__(self, "Map")

        # Import sounds
        self.add_sound("Run", pygame.mixer.Sound('res/sound/run.wav'))

        ## Set up vars
        self.id = map_id
        self.vars = prev_vars
        self.temp_vars = {}
        self.draw_black_surf = True
        self.vars['entrance'] = entrance_id
        self.party = party
        self.trigger_active = False

        if self.id not in self.vars['maps'].keys():
            self.vars['maps'][self.id] = []

        self.playback_state = 1

        self.draw_mode = 'default'
        self.tile_anims = {}

        self.encounter_rate = 1.0

        self.music = []

        if 'times' not in self.vars.keys():
            self.vars['times'] = [[time.time()]]
        elif len(self.vars['times'][len(self.vars['times']) - 1]) == 2:
            self.vars['times'].append([time.time()])

        if self.id not in maps.keys():
            try:
                loaded_map = load_map('res/maps/' + map_id)
                map_id = ''.map_id.split('.')[0:len(map_id.split('.'))-1]
            except Exception:
                try:
                    loaded_map = load_map('res/maps/' + map_id + '.srm')
                except Exception:
                    loaded_map = load_map('res/maps/' + map_id + '.srmf')

            self.tileset = pygame.image.fromstring(loaded_map['tileset'][0], loaded_map['tileset'][1], 'RGBA')
            self.tiles = []
            for t in loaded_map['tiles']:
                self.tiles.append([self.tileset.subsurface(t[0] * 32, 0, 32, 32), t[1], t[2], t[0]])
            self.tiles.sort(tilesort)
            
            self.entrances = loaded_map['entrances'][:]

            if 'music_names' in loaded_map.keys():
                self.music_names = loaded_map['music_names'][:]
                if previous_music_info != {}:
                    if self.music_names != previous_music_info['music_names']:
                        MUSIC_CHANNEL.fadeout(800)
                        self.music = [pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][0])]
                        if len(loaded_map['music_names']) == 2:
                            self.music.append(pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][1]))
                        self.music_timer = time.time()
                        self.music_elapsed = time.time()
                        self.playback_state = 2 - len(self.music)
                        self.music_paused = False
                        self.wait_flag = True
                    else:
                        self.music_timer = previous_music_info['timer']
                        self.music_elapsed = previous_music_info['elapsed']
                        self.playback_state = previous_music_info['state']
                        self.music_paused = False
                        self.wait_flag = False
                else:
                    self.music = [pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][0])]
                    if len(loaded_map['music_names']) == 2:
                        self.music.append(pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][1]))

                    self.music_timer = time.time()
                    self.music_elapsed = time.time()
                    self.playback_state = 2 - len(self.music)
                    self.music_paused = False
                    self.wait_flag = True
            else:
                if previous_music_info != {}:
                    self.music_timer = previous_music_info['timer']
                    self.music_elapsed = previous_music_info['elapsed']
                    self.playback_state = previous_music_info['state']
                    self.music = previous_music_info['music']
                    self.music_paused = False
                    self.wait_flag = False
                else:
                    self.wait_flag = True
                    self.music_timer = time.time()

            if 'triggers' in loaded_map.keys():
                loaded_trigs = loaded_map['triggers']
                for trigger in loaded_trigs:
                    for step in loaded_trigs[trigger].keys():
                        if step not in ['id', 'active_once']:
                            for arg in loaded_trigs[trigger][step]:
                                if type(loaded_trigs[trigger][step][arg]) == tuple and len(loaded_trigs[trigger][step][arg]) == 2:
                                    loaded_trigs[trigger][step][arg] = pygame.image.fromstring(loaded_trigs[trigger][step][arg][0], loaded_trigs[trigger][step][arg][1], "RGBA")
                self.triggers = loaded_trigs.copy()
            else:
                self.triggers = {}

            if 'sprites' in loaded_map.keys():
                pass

            if 'formations' in loaded_map.keys():
                self.random_formations = loaded_map['formations'][:]
            else:
                self.random_formations = []

            if 'background' in loaded_map.keys():
                if type(loaded_map['background']) == list:
                    self.background = loaded_map['background'][:]
                    bgs = []
                    for background in self.background:
                        bgs.append(pygame.image.load('res/maps/backgrounds/' + background))
                    self.background = bgs[:]
                else:
                    self.background = pygame.image.fromstring(loaded_map['background'][0], loaded_map['background'][1], 'RGBA')
            else:
                self.background = None

            if 'tileanims' in loaded_map.keys():
                self.tile_anims = loaded_map['tileanims']
            if 'encounter_rate' in loaded_map.keys():
                self.encounter_rate = loaded_map['encounter_rate']

        else:
            loaded_map = maps[self.id]
            self.tileset = loaded_map['tileset'].copy()
            self.tiles = loaded_map['tiles'][:]
            self.entrances = loaded_map['entrances'][:]

            if 'triggers' in loaded_map.keys():
                self.triggers = loaded_map['triggers'].copy()
            else:
                self.triggers = {}

            if 'sprites' in loaded_map.keys():
                pass

            if 'formations' in loaded_map.keys():
                self.random_formations = loaded_map['formations'][:]
            else:
                self.random_formations = []

            if 'background' in loaded_map.keys():
                if type(loaded_map['background']) == list:
                    self.background = loaded_map['background'][:]
                    bgs = []
                    for background in self.background:
                        bgs.append(pygame.image.load('res/maps/backgrounds/' + background))
                    self.background = bgs[:]
                else:
                    self.background = pygame.image.fromstring(loaded_map['background'][0], loaded_map['background'][1], 'RGBA')
            else:
                self.background = None

            if 'music_names' in loaded_map.keys():
                self.music_names = loaded_map['music_names'][:]
                if previous_music_info != {}:
                    if self.music_names != previous_music_info['music_names']:
                        MUSIC_CHANNEL.fadeout(800)
                        self.music = [pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][0])]
                        if len(loaded_map['music_names']) == 2:
                            self.music.append(pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][1]))

                        self.music_timer = time.time()
                        self.music_elapsed = time.time()
                        self.playback_state = 2 - len(self.music)
                        self.music_paused = False
                        self.wait_flag = True
                    else:
                        self.music_timer = previous_music_info['timer']
                        self.music_elapsed = previous_music_info['elapsed']
                        self.playback_state = previous_music_info['state']
                        self.music = previous_music_info['music']
                        self.music_paused = False
                        self.wait_flag = False
                else:
                    self.music = [pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][0])]
                    if len(loaded_map['music_names']) == 2:
                        self.music.append(pygame.mixer.Sound('res/sound/' + loaded_map['music_names'][1]))
                    
                    self.music_timer = time.time()
                    self.music_elapsed = time.time()
                    self.playback_state = 2 - len(self.music)
                    self.music_paused = False
                    self.wait_flag = True
            else:
                if previous_music_info != {}:
                    self.music_timer = previous_music_info['timer']
                    self.music_elapsed = previous_music_info['elapsed']
                    self.playback_state = previous_music_info['state']
                    self.music = previous_music_info['music']
                    self.music_paused = False
                    self.wait_flag = False
                else:
                    self.wait_flag = True
                    self.music_timer = time.time()

            if 'tileanims' in loaded_map.keys():
                self.tile_anims = loaded_map['tileanims']
            if 'encounter_rate' in loaded_map.keys():
                self.encounter_rate = loaded_map['encounter_rate']

        self.regions = {}
        self.current_region = None
        if 'regions' in loaded_map.keys():
            self.regions = loaded_map['regions']
        
        # Camera set up
        if 'camera' in loaded_map.keys():
            self.camera_pos = [loaded_map['camera'][0], loaded_map['camera'][1]]
            self.camera_pos[1] -= 360
        else:
            self.camera_pos = [0, 0]

        # Money
        self.money = money

        self.current_trigger = None
        self.current_step = 0
        if 'on_start' in self.triggers.keys():
            if ((self.triggers['on_start']['active_once'] and 'on_start' not in self.vars['maps'][self.id]) or
                not self.triggers['on_start']['active_once']):
                if self.triggers['on_start']['active_once']:
                    self.vars['maps'][self.id].append('on_start')
                self.current_trigger = self.triggers['on_start']
                self.current_step = 0
                self.trigger_active = True
        else:
            # Adding level to played maps
            if self.id not in self.vars['played_maps']:
                self.vars['played_maps'].append(self.id)

        ## Find the dimensions of the map
        self.dims = [0, 0]
        mins = [0, 0]
        maxs = [0, 0]

        self.animated_tiles = []

        i = 0
        ti = time.time()
        for t in self.tiles:
            if self.id not in maps.keys(): t[1][1] = 720 - t[1][1]
            
            if min(mins[0], t[1][0]) == t[1][0]: mins[0] = t[1][:][0]
            if max(maxs[0], t[1][0]) == t[1][0]: maxs[0] = t[1][:][0]
            if min(mins[1], t[1][1]) == t[1][1]: mins[1] = t[1][:][1]
            if max(maxs[1], t[1][1]) == t[1][1]: maxs[1] = t[1][:][1]

            if t[3] in self.tile_anims.keys():
                self.animated_tiles.append(i)
                self.tiles[i].append(ti)                                # Personal timer
                self.tiles[i].append(self.tile_anims[t[3]][0])          # Next tile in tileset
                self.tiles[i].append(self.tile_anims[t[3]][1] / 1000.0) # Time to next tile
            
            i += 1
            
        self.dims = [maxs[0] - mins[0], maxs[1] - mins[1]]

        # Camera set up
        self.camera_pos[1] = self.dims[1] - self.camera_pos[1]

        # Prep for rendering of the tiles
        self.layers = {}
        for t in self.tiles:
            if t[2] not in self.layers.keys():
                self.layers[t[2]] = []
            self.layers[t[2]].append(t)

        layer_nums = self.layers.keys()
        layer_nums.sort()

        # Rendering the tiles
        self.layer_surfs = {}
        self.layer_subsurfs = {}
        surf = pygame.Surface(self.dims, pygame.SRCALPHA)
        for ln in layer_nums:
            self.layer_surfs[ln] = surf.copy()
        
        for ln in layer_nums:
            for t in self.layers[ln]:
                self.layer_surfs[ln].blit(t[0], [t[1][0], self.dims[1] - t[1][1]])

        en = []
        for entrance in self.entrances:
            entrance[1] = self.dims[1] - entrance[1]

        if self.id not in RECTS.keys():
            if 'rects' in loaded_map.keys():
                self.rects = loaded_map['rects'].copy()
                for rect_id in self.rects.keys():
                    self.rects[rect_id]['rect'][1] = self.dims[1] - self.rects[rect_id]['rect'][1]
            else:
                self.rects = {}

            RECTS[self.id] = self.rects
        else:
            self.rects = RECTS[self.id]

        if self.id not in ENTRANCES.keys():
            ENTRANCES[self.id] = copy.deepcopy(self.entrances)
        else:
            self.entrances = ENTRANCES[self.id]

        self.wait_timer = time.time()
        self.millisec_wait = None

        self.say_box = None
        self.say_state = 0
        self.say_image = None
        self.say_arrow = None

        # Collision
        try:
            self.collision = pygame.image.load('res/maps/collision/' + self.id + '.png')
        except Exception:
            self.collision = pygame.Surface(self.dims)
            self.collision.fill([255,255,255])
        
        # Fade in and out
        self.fade = 'in'
        self.fade_in  = None
        self.fade_out = None 
        self.black_surf = pygame.Surface([640, 360])
        self.black_surf.fill([0,0,0])

        # Whether or not the camera is locked in place
        self.camera_locked = False
        self.camera_moveto = None
        self.camera_movespeed = 2

        # Set up player sprite
        if 'player_id' not in self.vars.keys():
            self.player = self.party[0]['sprite'].copy()
            if type(self.player) == str:
                s = self.player[:]
                self.player = SPRITE_LIBRARY.copy()[s]
                
            self.vars['player_id'] = copy.deepcopy(self.player.id)
        else:
            self.player = SPRITE_LIBRARY[self.vars['player_id']].copy()

        self.player.id = 'player'
        self.player.pos = self.entrances[entrance_id][:]
        self.player.parent = self
        self.player.movement_speed = 2
        self.moving_in_cutscene = False
        self.party_in_field = False
        self.last_direction_moved = [None, None]

        for member in self.party:
            if type(member['battle_sprite']) == str:
                member['battle_sprite'] = SPRITE_LIBRARY.copy()[member['battle_sprite']]

        # Menu navigation
        self.menu = None
        self.selected = []

        # Finish battle
        self.battle_finished = False
        self.battle_transition = -1
        self.temp_variable = None

        # Music fade out/in
        self.music_fade = None
        self.already_paused = False

        # Entrance ID
        self.entered_from = entrance_id

        # Random encounters
        self.battlecounter = 0

        # Transitioning to another stage
        self.goingtonewmap = False

        self.caps_lock = False

        self.battle_setup = False

        # Previous maps
        self.loaded_maps = maps

        self.section_times = []
        self.interacting = False

        self.quit = False # For when one quits out of the game

        if keys == 'default':
            self.keys = {'left': [pygame.K_LEFT, pygame.K_a],
                         'right': [pygame.K_RIGHT, pygame.K_d],
                         'up': [pygame.K_UP, pygame.K_w],
                         'down': [pygame.K_DOWN, pygame.K_s],
                         'a': [pygame.K_SPACE, pygame.K_RETURN],
                         'b': [pygame.K_z, pygame.K_x]}
        else:
            self.keys = keys

        self.debug = False
        self.debug_font = pygame.font.Font('res/fonts/coderscrux.ttf', 32)
        self.debug_font.set_italic(True)
        self.debug_font_rect = pygame.font.Font('res/fonts/coderscrux.ttf', 16)

        # Player moving
        self.restrict_player = True
        self.vertical        = 1

        self.menu_items = ['Inventory', 'Key Items', 'Specials', 'Equipment', 'Augments', 'Party', 'Status', 'Quit']

        self.delta = 1

        # Key items
        if 'key_items' not in self.vars.keys():
            self.vars['key_items'] = []

        # Disable menu option
        self.disable_menu = False

        # Music channel
        self.music_channel = MUSIC_CHANNEL

    def save_file(self, filename = 'save0.sv'):
        f = open('saves/' + filename, 'w')

        # Set time used
        self.vars['times'][len(self.vars['times']) - 1].append(time.time())

        m = self.id
        p = self.player.pos[:]
        if 'next_map' in self.vars.keys():
            if self.vars['next_map'] not in [None, "None"]:
                m = copy.copy(self.vars['next_map'])

                try:
                    loaded_map = load_map('res/maps/' + m)
                    map_id = ''.m.split('.')[0:len(m.split('.'))-1]
                except Exception:
                    try:
                        loaded_map = load_map('res/maps/' + m + '.srm')
                    except Exception:
                        loaded_map = load_map('res/maps/' + m + '.srmf')

                p = loaded_map['entrances'][0]
                del loaded_map
                mf.close()
        
        savefile = {'party': [],
                    'map': m,
                    'position': p,
                    'vars': self.vars.copy(),
                    'names': [],
                    'money': self.money}

        for member in self.party:
            savefile['party'].append(member.copy())

        p = []
        i = 0
        for member in savefile['party']:
            m = {}
            for key in member.keys():
                try:
                    m[key] = member[key].copy()
                except AttributeError:
                    m[key] = copy.copy(member[key])
            p.append(m)

            bag = []
            for item in p[i]['bag']:
                bag.append(item['id'])
            p[i]['bag'] = bag

            equip = []
            for item in p[i]['equipment']:
                if item == None:
                    equip.append(None)
                else:
                    equip.append(item['id'])
            p[i]['equipment'] = equip
                
            if type(p[i]['battle_sprite']) != str:
                p[i]['battle_sprite'] = p[i]['battle_sprite'].id
            if type(p[i]['sprite']) != str:
                if p[i]['sprite'] == 'player':
                    p[i]['sprite'] = member['sprite_id']
                else:
                    p[i]['sprite'] = p[i]['sprite'].id
            else:
                if p[i]['sprite'] == 'player':
                    p[i]['sprite'] = member['sprite_id']

            if member['name'] in self.vars['custom_names'].keys():
                savefile['names'].append(self.vars['custom_names'][member['name']])
            else:
                savefile['names'].append(member['name'])
            i += 1
        savefile['party'] = p[:]

        savefile['keyitems'] = []
        for item in savefile['vars']['key_items']:
            savefile['keyitems'].append(item['id'])
        del savefile['vars']['key_items']
        
        pickle.dump(savefile, f)
        f.close()
        savefile = None

        # Adds in new time marker
        self.vars['times'].append([time.time()])

    def draw_menu(self, SURF, allow_save = False):
        if allow_save and "Save" not in self.menu_items:
            self.menu_items.insert(len(self.menu_items) - 1, 'Save')
        elif 'Save' in self.menu_items:
            if not allow_save:
                self.menu_items.remove('Save')
        menu_items = self.menu_items
        
        # Menu boxes
        if self.menu != None:
            f = pygame.font.Font('res/fonts/coderscrux.ttf', 16)
            
            pygame.draw.rect(SURF, [0, 0, 0], [520, 12, 80, 4 + (18 * len(menu_items))])
            pygame.draw.rect(SURF, [255, 255, 255], [520, 12, 80, 4 + (18 * len(menu_items))], 1)

            pygame.draw.rect(SURF, [0, 0, 0], [520, 330, 80, 20])
            pygame.draw.rect(SURF, [255, 255, 255], [520, 330, 80, 20], 1)
            SURF.blit(f.render(str(self.money) + ' coins', False, [255, 255, 255]), [600 - f.size(str(self.money) + ' coins')[0] - 3, 336])

            i = 0
            for char in self.party:
                offset = 0
                
                # Char profile tab
                if self.menu.find("Inventory") > -1 or self.menu.find("Specials") > -1 or self.menu.find("Equipment") > -1 or self.menu.find("Status") > -1 or self.menu.find("Party") > -1 or self.menu.find("Augments") > -1:
                    if int(self.selected[1]) == i:
                        clr = [32, 32, 32]
                    elif len(self.menu.split(',')) > 1:
                        if int(self.menu.split(',')[1]) == i and not self.menu.find("Party") > -1:
                            clr = [32, 32, 32]
                        else:
                            clr = [0, 0, 0]
                    else:
                        clr = [0, 0, 0]

                    if ((len(self.selected) > 3 and self.menu.find("Inventory") > -1 and self.menu.split(',')[2] == 'Move') or (len(self.selected) > 3 and self.menu.find("Equipment") > -1)):
                        if self.selected[3] == i:
                            if clr != [32, 32, 32]:
                                clr = [16, 16, 16]
                            else:
                                clr = [64, 64, 64]
                    elif len(self.selected) > 3 and self.menu.find("Inventory") > -1 and self.menu.split(',')[2] == 'Use':
                        if self.selected[3] == i:
                            clr = [15, 51, 109]
                        else:
                            if clr == [32, 32, 32]:
                                clr = [16, 16, 16]
                elif self.menu not in ["Inventory", "Specials", "Equipment", "Status", "Augments"]:
                    clr = [0, 0, 0]
                
                if self.menu.find("Party") > -1 and len(self.selected) > 2 and clr == [32, 32, 32]:
                    offset = 20
                
                pygame.draw.rect(SURF, clr, [25 + offset, 19 + (64 * i), 265, 60])

                clr = [255, 255, 255]
                if char['HP'][0] == 0:
                    clr = [255, 0, 0]
                elif char['HP'][0] < char['HP'][1] / 6.9:
                    clr = [255, 255, 255]
                self.find_text('character' + str(i))['color'] = clr
                self.find_text('character' + str(i))['position'][0] = 86 + offset
                    
                pygame.draw.rect(SURF, clr, [25 + offset, 19 + (64 * i), 265, 60], 1)
                
                # Char LVL
                SURF.blit(f.render('LVL ' + str(char['LVL']), False, clr), [86 + offset, 42 + (64 * i)])
                # Char EXP
                SURF.blit(f.render('EXP ' + str(char['EXP']) + '/' + str(char['NLV']), False, clr), [86 + offset, 54 + (64 * i)])
                # Char HP
                SURF.blit(f.render('HP ' + str(char['HP'][0]) + '/' + str(char['HP'][1]), False, clr), [86 + offset, 66 + (64 * i)])
                # Char SP
                SURF.blit(f.render('SP ' + str(char['SP'][0]) + '/' + str(char['SP'][1]), False, clr), [156 + offset, 42 + (64 * i)])
                # Char INV
                SURF.blit(f.render('BAG ' + str(len(char['bag'])) + '/' + str(char['bag_size']), False, clr), [156 + offset, 54 + (64 * i)])
                # Char ALIGNMENT
                alignment_chart = [("chaotic evil", "neutral evil", "lawful evil"), ("chaotic neutral", "true neutral", "lawful neutral"), ("chaotic good", "neutral good", "lawful good")]
                f.set_bold(True)
                SURF.blit(f.render(alignment_chart[char['alignment'][1] + 1][char['alignment'][0] + 1], True, clr), [156 + offset, 66 + (64 * i)])
                f.set_bold(False)
                
                i += 1

            # Draw inventory
            if self.menu.find("Inventory") > -1 and len(self.selected) > 2:
                if len(self.party[self.selected[1]]['bag']) < 1:
                    items = 1
                else:
                    items = len(self.party[self.selected[1]]['bag'])

                # Draw inventory rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, (items * 16) + 1])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, (items * 16) + 1], 1)

                # Draw items
                if len(self.party[self.selected[1]]['bag']) < 1:
                    SURF.blit(f.render('Inventory empty!', False, [128, 128, 128]), [320, 23])
                else:
                    i = 0
                    for item in self.party[self.selected[1]]['bag']:
                        clr = [255, 255, 255]
                        set_color = True

                        if item['consumable'].lower() in ["yes", 'y', 't', 'true']:
                            if i == self.selected[2]:
                                clr = [40, 122, 255]
                        else:
                            clr = [128, 128, 128]
                            if i == self.selected[2]:
                                clr = [128 + 32, 128 + 32, 128 + 32]

                        offset = 0
                        if len(self.selected) > 3:
                            if i == self.selected[3] and self.menu.split(',')[2] == 'Sort':
                                offset = 10
                        
                        SURF.blit(f.render(item['name'], False, clr), [320 + offset, 23 + (16 * i)])
                        i += 1

                # Draw lore
                if len(self.party[self.selected[1]]['bag']) > 0:
                    l = self.party[self.selected[1]]['bag'][self.selected[2]]['lore'][:]
                    lo = []
                    for lore in l:
                        new_lore = textwrap.wrap(lore, 26)
                        if len(new_lore) == 1:
                            lo.append(lore)
                        else:
                            for item in new_lore:
                                lo.append(item)

                    lo.append('')
                    lo.append("[<-] move item to other inv")
                    lo.append("[->] move item inside inv")
                    lo.append("[-> ->] toss item")
                    lo.append("[SPC] use item")
                    lo.append("[Z/X] back")

                    l = len(lo)
                    
                    pygame.draw.rect(SURF, [0, 0, 0], [315, 29 + (items * 16), 180, (l * 11) + 4])
                    pygame.draw.rect(SURF, [255, 255, 255], [315, 29 + (items * 16), 180, (l * 11) + 4], 1)
                    y = 33 + (items * 16)
                    
                    for lore in lo:
                        SURF.blit(f.render(lore, False, [255, 255, 255]), [320, y])
                        y += 11

            # Draw key items
            if self.menu.find("Key Items") > -1 and len(self.selected):
                items = len(self.vars['key_items'])

                # Draw inventory rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, (items * 16) + 1])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, (items * 16) + 1], 1)

                # Draw items
                i = 0
                for item in self.vars['key_items']:
                    clr = [255, 255, 255]
                    set_color = True

                    if item['consumable'].lower() in ["yes", 'y', 't', 'true']:
                        if i == self.selected[1]:
                            clr = [40, 122, 255]
                    else:
                        clr = [128, 128, 128]
                        if i == self.selected[1]:
                            clr = [128 + 32, 128 + 32, 128 + 32]
                    
                    SURF.blit(f.render(item['name'], False, clr), [320, 23 + (16 * i)])
                    i += 1

                # Draw lore
                l = self.vars['key_items'][self.selected[1]]['lore'][:]
                lo = []
                for lore in l:
                    new_lore = textwrap.wrap(lore, 26)
                    if len(new_lore) == 1:
                        lo.append(lore)
                    else:
                        for item in new_lore:
                            lo.append(item)

                l = len(lo)
                pygame.draw.rect(SURF, [0, 0, 0], [315, 29 + (items * 16), 180, (l * 11) + 4])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 29 + (items * 16), 180, (l * 11) + 4], 1)
                y = 33 + (items * 16)
                
                for lore in lo:
                    SURF.blit(f.render(lore, False, [255, 255, 255]), [320, y])
                    y += 11

            # Draw special attacks/moves
            if self.menu.find("Specials") > -1 and len(self.selected) > 2:
                if len(self.party[self.selected[1]]['specials']) < 1:
                    items = 2
                else:
                    items = len(self.party[self.selected[1]]['specials']) + 1

                # Draw specials rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, (items * 14) + 1])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, (items * 14) + 1], 1)

                # Draw current SP
                SURF.blit(f.render('SP ' + str(self.party[self.selected[1]]['SP'][0]) + '/' + str(self.party[self.selected[1]]['SP'][1]), False, [255, 255, 255]), [320, 23])

                if len(self.party[self.selected[1]]['specials']) < 1:
                    SURF.blit(f.render('No specials', False, [128, 128, 128]), [320, 37])
                else:
                    i = 0
                    for special in self.party[self.selected[1]]['specials']:
                        spc = SPECIAL_ATTACKS[special]
                        
                        clr = [255, 255, 255]
                        if spc[3].lower() == 'player':
                            if self.party[self.selected[1]]['SP'][0] >= spc[2]:
                                if i == self.selected[2]:
                                    clr = [40, 122, 255]
                            else:
                                clr = [128, 128, 128]
                                if i == self.selected[2]:
                                    clr = [128 + 32, 128 + 32, 128 + 32]
                        else:
                            clr = [128, 128, 128]
                            if i == self.selected[2]:
                                clr = [128 + 32, 128 + 32, 128 + 32]
                        SURF.blit(f.render(spc[1] + ' <' + str(spc[2]) + ' SP>', False, clr), [320, 36 + (14 * i)])
                        i += 1

            if self.menu.find("Equipment") > -1 and len(self.selected) > 2:
                # Draw equipment rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, 46])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, 46], 1)

                SURF.blit(f.render("RH", False, [255, 255, 255]), [320, 23])
                if self.selected[2] == 0: # right hand
                    if self.party[self.selected[1]]['equipment'][0] != None:
                        clr = [40, 122, 255]
                        txt = self.party[self.selected[1]]['equipment'][0]['name']
                    else:
                        clr = [192, 192, 192]
                        txt = 'Empty'
                else:
                    if self.party[self.selected[1]]['equipment'][0] != None:
                        clr = [255, 255, 255]
                        txt = self.party[self.selected[1]]['equipment'][0]['name']
                    else:
                        clr = [64, 64, 64]
                        txt = 'Empty'
                SURF.blit(f.render(txt, False, clr), [345, 23])

                SURF.blit(f.render("LH", False, [255, 255, 255]), [320, 33])
                if self.selected[2] == 1: # left hand
                    if self.party[self.selected[1]]['equipment'][1] != None:
                        clr = [40, 122, 255]
                        txt = self.party[self.selected[1]]['equipment'][1]['name']
                    else:
                        clr = [192, 192, 192]
                        txt = 'Empty'
                else:
                    if self.party[self.selected[1]]['equipment'][1] != None:
                        clr = [255, 255, 255]
                        txt = self.party[self.selected[1]]['equipment'][1]['name']
                    else:
                        clr = [64, 64, 64]
                        txt = 'Empty'
                SURF.blit(f.render(txt, False, clr), [345, 33])

                SURF.blit(f.render("HD", False, [255, 255, 255]), [320, 43])
                if self.selected[2] == 2: # head
                    if self.party[self.selected[1]]['equipment'][2] != None:
                        clr = [40, 122, 255]
                        txt = self.party[self.selected[1]]['equipment'][2]['name']
                    else:
                        clr = [192, 192, 192]
                        txt = 'Empty'
                else:
                    if self.party[self.selected[1]]['equipment'][2] != None:
                        clr = [255, 255, 255]
                        txt = self.party[self.selected[1]]['equipment'][2]['name']
                    else:
                        clr = [64, 64, 64]
                        txt = 'Empty'
                SURF.blit(f.render(txt, False, clr), [345, 43])

                SURF.blit(f.render("BD", False, [255, 255, 255]), [320, 53])
                if self.selected[2] == 3: # body
                    if self.party[self.selected[1]]['equipment'][3] != None:
                        clr = [40, 122, 255]
                        txt = self.party[self.selected[1]]['equipment'][3]['name']
                    else:
                        clr = [192, 192, 192]
                        txt = 'Empty'
                else:
                    if self.party[self.selected[1]]['equipment'][3] != None:
                        clr = [255, 255, 255]
                        txt = self.party[self.selected[1]]['equipment'][3]['name']
                    else:
                        clr = [64, 64, 64]
                        txt = 'Empty'
                SURF.blit(f.render(txt, False, clr), [345, 53])

                # Draw stats rect
                pygame.draw.rect(SURF, [0, 0, 0], [425, 67, 70, 55])
                pygame.draw.rect(SURF, [255, 255, 255], [425, 67, 70, 55], 1)

                # Draw current ATK
                if self.party[self.selected[1]]['equipment'][0] != None and bool(self.party[self.selected[1]]['right_handed']):
                    atk = self.party[self.selected[1]]['equipment'][0]['ATK'] # right hand
                elif self.party[self.selected[1]]['equipment'][1] != None and not bool(self.party[self.selected[1]]['right_handed']):
                    atk = self.party[self.selected[1]]['equipment'][1]['ATK'] # left hand
                else:
                    atk = 0
                SURF.blit(f.render('ATK ' + str(atk), False, [255, 255, 255]), [429, 71])

                # Draw current DEF
                defense = self.party[self.selected[1]]['DEF']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'DEF' in item.keys():
                            defense += item['DEF']
                SURF.blit(f.render('DEF ' + str(defense), False, [255, 255, 255]), [429, 81])

                # Draw current MDF
                mdf = self.party[self.selected[1]]['MDF']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'MDF' in item.keys():
                            mdf += item['MDF']
                SURF.blit(f.render('MDF ' + str(mdf), False, [255, 255, 255]), [429, 91])

                # Draw current EVA
                eva = self.party[self.selected[1]]['EVA']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'EVA' in item.keys():
                            eva += item['EVA']
                SURF.blit(f.render('EVA ' + str(eva), False, [255, 255, 255]), [429, 101])

                # Draw current SPD
                spd = self.party[self.selected[1]]['SPD']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'SPD' in item.keys():
                            spd += item['SPD']
                SURF.blit(f.render('SPD ' + str(spd), False, [255, 255, 255]), [429, 111])

                if len(self.selected) == 4 and self.menu.split(',')[-1] == "Del": # Ask user which player to give item to
                    i = 4
                    y = 71 + (i * 11)
                    y -= 11
                    if y <= 124:
                        y = 124

                    pygame.draw.rect(SURF, [0, 0, 0], [315, y, 180, 15])
                    pygame.draw.rect(SURF, [255, 255, 255], [315, y, 180, 15], 1)
                    y += 3

                    SURF.blit(f.render("Who to give item to?", False, [255, 255, 255]), [320, y])

                if len(self.selected) == 5:
                    # Draw inv rect
                    pygame.draw.rect(SURF, [0, 0, 0], [315, 67, 105, 5 + (10*len(self.party[self.selected[3]]['bag']))])
                    pygame.draw.rect(SURF, [255, 255, 255], [315, 67, 105, 5 + (10*len(self.party[self.selected[3]]['bag']))], 1)

                    i = 0
                    for item in self.party[self.selected[3]]['bag']:
                        valid = False
                        if bool(item['equipable']):
                            if 'slot' in item.keys():
                                if self.selected[2] in item['slot']:
                                    valid = True

                            if 'equipped_by' in item.keys():
                                valid = (self.party[self.selected[1]]['id'] in item['equipped_by'] or self.party[self.selected[1]]['name'] in item['equipped_by']) and valid

                            if 'valid_alignments' in item.keys():
                                valid = '<%i,%i>' % (self.party[self.selected[1]]['alignment'][0], self.party[self.selected[1]]['alignment'][1]) in item['valid_alignments'] and valid

                        if valid:
                            clr = [255, 255, 255]
                            if self.selected[4] == i:
                                clr = [40, 122, 255]
                        else:
                            clr = [128, 128, 128]
                            if self.selected[4] == i:
                                clr = [196, 196, 196]
                        
                        SURF.blit(f.render(item['name'], False, clr), [320, 71 + (10 * i)])

                        if self.selected[4] == i and valid: # Changed stats if equipped & valid
                            # Draw added/lost ATK for selected item
                            if 'ATK' in self.party[self.selected[3]]['bag'][self.selected[4]].keys():
                                comparison = self.party[self.selected[3]]['bag'][self.selected[4]]['ATK']

                                # Penalty if weapon equipped in wrong hand
                                if not ((self.selected[2] == 0 and bool(self.party[self.selected[1]]['right_handed'])) or (self.selected[2] == 1 and not bool(self.party[self.selected[1]]['right_handed']))):
                                    comparison /= 8

                                # Add in left hand if selecting right and right hand if selecting left for comparison
                                if self.selected[2] == 0 and self.party[self.selected[1]]['equipment'][1] != None:
                                    if bool(self.party[self.selected[1]]['right_handed']):
                                        comparison += self.party[self.selected[1]]['equipment'][1]['ATK'] / 8
                                    else:
                                        comparison += self.party[self.selected[1]]['equipment'][1]['ATK']
                                if self.selected[2] == 1 and self.party[self.selected[1]]['equipment'][0] != None:
                                    if not bool(self.party[self.selected[1]]['right_handed']):
                                        comparison += self.party[self.selected[1]]['equipment'][0]['ATK'] / 8
                                    else:
                                        comparison += self.party[self.selected[1]]['equipment'][0]['ATK']

                                if comparison > atk:
                                    clr, sign = [0, 255, 0], '+'
                                else:
                                    clr, sign = [255, 0, 0], '-'
                                SURF.blit(f.render(sign + str(comparison - atk), False, clr), [469, 71])

                            # Draw added/lost DEF for selected item
                            if 'DEF' in self.party[self.selected[3]]['bag'][self.selected[4]].keys():
                                comparison = self.party[self.selected[3]]['bag'][self.selected[4]]['DEF']

                                # Add in additional defense items already equipped
                                j = 0
                                for item in self.party[self.selected[1]]['equipment']:
                                    if item != None and j != self.selected[4]:
                                        if 'DEF' in item.keys():
                                            comparison += item['DEF']
                                    j += 1

                                if comparison > defense:
                                    clr, sign = [0, 255, 0], '+'
                                else:
                                    clr, sign = [255, 0, 0], '-'
                                SURF.blit(f.render(sign + str(comparison - defense), False, clr), [469, 81])

                            # Draw added/lost MDF for selected item
                            if 'MDF' in self.party[self.selected[3]]['bag'][self.selected[4]].keys():
                                comparison = self.party[self.selected[3]]['bag'][self.selected[4]]['MDF']

                                # Add in additional defense items already equipped
                                j = 0
                                for item in self.party[self.selected[1]]['equipment']:
                                    if item != None and j != self.selected[4]:
                                        if 'MDF' in item.keys():
                                            comparison += item['MDF']
                                    j += 1

                                if comparison > mdf:
                                    clr, sign = [0, 255, 0], '+'
                                else:
                                    clr, sign = [255, 0, 0], '-'
                                SURF.blit(f.render(sign + str(comparison - mdf), False, clr), [469, 91])

                            # Draw added/lost EVA for selected item
                            if 'EVA' in self.party[self.selected[3]]['bag'][self.selected[4]].keys():
                                comparison = self.party[self.selected[3]]['bag'][self.selected[4]]['EVA']

                                # Add in additional defense items already equipped
                                j = 0
                                for item in self.party[self.selected[1]]['equipment']:
                                    if item != None and j != self.selected[4]:
                                        if 'EVA' in item.keys():
                                            comparison += item['EVA']
                                    j += 1

                                if comparison > eva:
                                    clr, sign = [0, 255, 0], '+'
                                else:
                                    clr, sign = [255, 0, 0], '-'
                                SURF.blit(f.render(sign + str(comparison - eva), False, clr), [469, 101])

                            # Draw added/lost SPD for selected item
                            if 'SPD' in self.party[self.selected[3]]['bag'][self.selected[4]].keys():
                                comparison = self.party[self.selected[3]]['bag'][self.selected[4]]['SPD']

                                # Add in additional defense items already equipped
                                j = 0
                                for item in self.party[self.selected[1]]['equipment']:
                                    if item != None and j != self.selected[4]:
                                        if 'SPD' in item.keys():
                                            comparison += item['SPD']
                                    j += 1

                                if comparison > spd:
                                    clr, sign = [0, 255, 0], '+'
                                else:
                                    clr, sign = [255, 0, 0], '-'
                                SURF.blit(f.render(sign + str(comparison - spd), False, clr), [469, 111])
                            
                        i += 1

                    # Item lore
                    l = self.party[self.selected[3]]['bag'][self.selected[4]]['lore'][:]
                    lo = []
                    for lore in l:
                        new_lore = textwrap.wrap(lore, 26)
                        if len(new_lore) == 1:
                            lo.append(lore)
                        else:
                            for item in new_lore:
                                lo.append(item)

                    l = len(lo)

                    y = 71 + (i * 11)
                    y -= 11
                    if y <= 124:
                        y = 124
                    
                    pygame.draw.rect(SURF, [0, 0, 0], [315, y, 180, (l * 11) + 4])
                    pygame.draw.rect(SURF, [255, 255, 255], [315, y, 180, (l * 11) + 4], 1)
                    y += 3
                    
                    for lore in lo:
                        SURF.blit(f.render(lore, False, [255, 255, 255]), [320, y])
                        y += 11

            # Draw augments screen
            if self.menu.find("Augments") > -1 and len(self.selected) > 2:
                # Draw equipment rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, 46])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, 46], 1)

                i = 0
                for aug in self.party[self.selected[1]]['augments']:
                    if aug == None:
                        if self.selected[2] == i:
                            clr = [64, 64, 64]
                        else:
                            clr = [0, 0, 0]
                    else:
                        if self.selected[2] == i:
                            clr = [int(aug['color'][0] + ((255 - aug['color'][0]) * 0.2)), int(aug['color'][1] + ((255 - aug['color'][1]) * 0.2)), int(aug['color'][2] + ((255 - aug['color'][2]) * 0.2))]
                        else:
                            clr = aug['color']

                    if i % 2 == 0 and i < len(self.party[self.selected[1]]['augments']) - 1:
                        pygame.draw.line(SURF, [255, 255, 255], [315 + 23 + (25 * i), 19 + 23], [315 + 23 + (25 * (i + 1)), 19 + 23], 1)
                        
                    pygame.draw.circle(SURF, clr, [315 + 23 + (25 * i), 19 + 23], 10)
                    pygame.draw.circle(SURF, [255, 255, 255], [315 + 23 + (25 * i), 19 + 23], 10, 1)
                    i += 1

            # Draw status screen
            if self.menu.find("Status") > -1 and len(self.selected) > 2:
                # Draw status rect
                pygame.draw.rect(SURF, [0, 0, 0], [315, 19, 180, 172 + (10*len(self.party[self.selected[1]]['bag']))])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 19, 180, 172 + (10*len(self.party[self.selected[1]]['bag']))], 1)

                if self.party[self.selected[1]]['name'] in self.vars['custom_names']:
                    txt = self.party[self.selected[1]]['name'].replace(self.party[self.selected[1]]['name'], self.vars['custom_names'][self.party[self.selected[1]]['name']])
                else:
                    txt = self.party[self.selected[1]]['name']
                SURF.blit(f.render(txt + "'s Status", False, [255, 255, 255]), [315 + 90 - (f.size(txt + "'s Status")[0] / 2), 23])

                # Draw current LVL, EXP, NLV
                SURF.blit(f.render('LVL ' + str(self.party[self.selected[1]]['LVL']), False, [255, 255, 255]), [320, 40])
                SURF.blit(f.render('EXP ' + str(self.party[self.selected[1]]['EXP']) + '/' + str(self.party[self.selected[1]]['NLV']), False, [255, 255, 255]), [320, 50])

                SURF.blit(f.render('HP ' + str(self.party[self.selected[1]]['HP'][0]) + '/' + str(self.party[self.selected[1]]['HP'][1]), False, [255, 255, 255]), [410, 40])
                SURF.blit(f.render('SP ' + str(self.party[self.selected[1]]['SP'][0]) + '/' + str(self.party[self.selected[1]]['SP'][1]), False, [255, 255, 255]), [410, 50])

                # Draw current ATK
                if self.party[self.selected[1]]['equipment'][0] != None and bool(self.party[self.selected[1]]['right_handed']):
                    atk = self.party[self.selected[1]]['equipment'][0]['ATK'] # right hand
                elif self.party[self.selected[1]]['equipment'][1] != None and not bool(self.party[self.selected[1]]['right_handed']):
                    atk = self.party[self.selected[1]]['equipment'][1]['ATK'] # left hand
                else:
                    atk = 0
                SURF.blit(f.render('ATK ' + str(atk), False, [255, 255, 255]), [320, 70])

                # Draw current DEF
                defense = self.party[self.selected[1]]['DEF']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'DEF' in item.keys():
                            defense += item['DEF']
                SURF.blit(f.render('DEF ' + str(defense), False, [255, 255, 255]), [320, 80])

                # Draw current MDF
                defense = self.party[self.selected[1]]['MDF']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'MDF' in item.keys():
                            defense += item['MDF']
                SURF.blit(f.render('MDF ' + str(defense), False, [255, 255, 255]), [320, 90])

                # Draw current EVA
                atk = self.party[self.selected[1]]['EVA']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'EVA' in item.keys():
                            atk += item['EVA']
                SURF.blit(f.render('EVA ' + str(atk), False, [255, 255, 255]), [320, 100])

                # Draw current STR
                atk = self.party[self.selected[1]]['STR']
                SURF.blit(f.render('STR ' + str(atk), False, [255, 255, 255]), [390, 70])

                # Draw current WIS
                atk = self.party[self.selected[1]]['WIS']
                SURF.blit(f.render('WIS ' + str(atk), False, [255, 255, 255]), [390, 80])

                # Draw current INT
                atk = self.party[self.selected[1]]['INT']
                SURF.blit(f.render('INT ' + str(atk), False, [255, 255, 255]), [390, 90])

                # Draw current SPD
                atk = self.party[self.selected[1]]['SPD']
                for item in self.party[self.selected[1]]['equipment']:
                    if item != None:
                        if 'SPD' in item.keys():
                            atk += item['SPD']
                SURF.blit(f.render('SPD ' + str(atk), False, [255, 255, 255]), [390, 100])

                # Draw bag/inventory
                SURF.blit(f.render('BAG ' + str(len(self.party[self.selected[1]]['bag']))  + '/' + str(self.party[self.selected[1]]['bag_size']), False, [255, 255, 255]), [320, 120])
                i = 0
                for item in self.party[self.selected[1]]['bag']:
                    SURF.blit(f.render(item['name'], False, [192, 192, 192]), [326, 130 + (10 * i)])
                    i += 1

                # Draw equipment
                SURF.blit(f.render('EQIUP', False, [255, 255, 255]), [320, 140 + (10 * i)])
                
                SURF.blit(f.render('RH', False, [255, 255, 255]), [326, 150 + (10 * i)])
                if self.party[self.selected[1]]['equipment'][0] != None: # right hand
                    SURF.blit(f.render(self.party[self.selected[1]]['equipment'][0]['name'], False, [192, 192, 192]), [350, 150 + (10 * i)])
                    
                SURF.blit(f.render('LH', False, [255, 255, 255]), [326, 160 + (10 * i)])
                if self.party[self.selected[1]]['equipment'][1] != None: # left hand
                    SURF.blit(f.render(self.party[self.selected[1]]['equipment'][1]['name'], False, [192, 192, 192]), [350, 160 + (10 * i)])
                
                SURF.blit(f.render('HD', False, [255, 255, 255]), [326, 170 + (10 * i)])
                if self.party[self.selected[1]]['equipment'][2] != None: # head
                    SURF.blit(f.render(self.party[self.selected[1]]['equipment'][2]['name'], False, [192, 192, 192]), [350, 170 + (10 * i)])
                
                SURF.blit(f.render('BD', False, [255, 255, 255]), [326, 180 + (10 * i)])
                if self.party[self.selected[1]]['equipment'][3] != None: # body
                    SURF.blit(f.render(self.party[self.selected[1]]['equipment'][3]['name'], False, [192, 192, 192]), [350, 180 + (10 * i)])

            if self.menu.find("Save") > -1 and len(self.selected) > 1:
                pygame.draw.rect(SURF, [0, 0, 0], [315, 20, 180, 20])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 20, 180, 20], 1)

                SURF.blit(f.render("Select save file:", False, [255, 255, 255]), [321, 26])

                if self.selected[1] == 0:
                    clr = [15, 51, 109]
                else:
                    clr = [0, 0, 0]
                pygame.draw.rect(SURF, clr, [315, 45, 48, 20])
                pygame.draw.rect(SURF, [255, 255, 255], [315, 45, 48, 20], 1)
                SURF.blit(f.render("File 1", False, [255, 255, 255]), [321, 51])

                if self.selected[1] == 1:
                    clr = [15, 51, 109]
                else:
                    clr = [0, 0, 0]
                pygame.draw.rect(SURF, clr, [381, 45, 48, 20])
                pygame.draw.rect(SURF, [255, 255, 255], [381, 45, 48, 20], 1)
                SURF.blit(f.render("File 2", False, [255, 255, 255]), [387, 51])

                if self.selected[1] == 2:
                    clr = [15, 51, 109]
                else:
                    clr = [0, 0, 0]
                pygame.draw.rect(SURF, clr, [447, 45, 48, 20])
                pygame.draw.rect(SURF, [255, 255, 255], [447, 45, 48, 20], 1)
                SURF.blit(f.render("File 3", False, [255, 255, 255]), [453, 51])

    def draw_world(self, SURF, fps):
        # Rendering the backgrounds
        if self.background != None:
            pos = [-self.camera_pos[0], -self.dims[1] + self.camera_pos[1] + 328]
            if type(self.background) == list:
                i = len(self.background) + 1
                self.background.reverse()

                for background in self.background:
                    mod = self.dims[1] + (360 - background.get_rect().h + pos[1])

                    z = 0
                    while (pos[0] / i) + z <SURF.get_width():
                        SURF.blit(background, [(pos[0] / i) + z, 360 - background.get_rect().h + (mod / i)])
                        z += background.get_width()
                        i -= 1
                self.background.reverse()
            else:
                SURF.blit(self.background, [pos[0], -background.get_rect().h + pos[1]])

        # Rendering the layers
        layer_keys = self.layer_surfs.keys()
        if 1 not in layer_keys:
            layer_keys.append(1)
        layer_keys.sort()

        ti = time.time()
        for i in self.animated_tiles:
            t = self.tiles[i]
            if ti - t[4] > t[6]:
                self.tiles[i][4] = ti
                self.tiles[i][0] = self.tileset.subsurface(t[5] * 32, 0, 32, 32)
                self.tiles[i][3] = t[5]

                if self.tiles[i][3] in self.tile_anims.keys():
                    self.tiles[i][5] = self.tile_anims[self.tiles[i][3]][0]
                    self.tiles[i][6] = self.tile_anims[self.tiles[i][3]][1] / 1000.0

                self.layer_surfs[self.tiles[i][2]].blit(self.tiles[i][0], [t[1][0], self.dims[1] - t[1][1]])

        pos = [-self.camera_pos[0], -self.dims[1] + self.camera_pos[1] + 328]
        sp = []
        for layer_num in layer_keys:
            try: SURF.blit(self.layer_surfs[layer_num], [0, 0], [-pos[0], -pos[1], SURF.get_width(), SURF.get_height()])
            except KeyError: pass

            if layer_num == 1: # All sprites are drawn at Z-order 1, thus Z-order 2+ tiles are foreground
                sp = self.sprites[:]
                if self.player != None:
                    sp.append(self.player)

                sp.sort(z_sort)
                
                for sprite in sp:
                    if sprite == self.player:
                        sprite.render(SURF, pos)
                        sprite.update()
                    else:
                        chp = pos[:] # Account for a Pygame bug where sprites rendered at Y <= -1 on the screen are one pixel off their correct position
                        chp[1] = -self.dims[1] + self.camera_pos[1] + 328
                        if sprite.pos[1] + chp[1] - sprite.img_height < 0:
                            chp[1] -= 1
                        
                        sprite.render(SURF, chp)

                        sprite.movement_speed *= 60 / fps
                        sprite.update({"ITEM_LIBRARY": ITEM_LIBRARY, "SPRITE_LIBRARY": SPRITE_LIBRARY,
                                       "AI_LIBRARY": AI_LIBRARY, "SPECIAL_ATTACKS": SPECIAL_ATTACKS,
                                       "FORMATION_LIBRARY": FORMATION_LIBRARY, 'fps': fps, 'math': math})
                        sprite.movement_speed /= 60 / fps

        if self.debug:
            for rect_id in self.rects.keys():
                rect = pygame.Rect(self.rects[rect_id]['rect'])
                rect.x += pos[0]
                rect.y += pos[1]
                
                pygame.draw.rect(SURF, [255, 255, 255], rect, 1)
                SURF.blit(self.debug_font_rect.render(rect_id, False, [255, 255, 255]), [rect[0], rect[1] - self.debug_font_rect.size(rect_id)[1]])

            i = 0
            for entrance in self.entrances:
                e = [entrance[0] + pos[0], entrance[1] + pos[1]]
                pygame.draw.line(SURF, [0, 255, 0], [e[0] - 2, e[1] - 2], [e[0] + 2, e[1] + 2])
                pygame.draw.line(SURF, [0, 255, 0], [e[0] - 2, e[1] + 2], [e[0] + 2, e[1] - 2])
                SURF.blit(self.debug_font_rect.render('E%i (%i, %i)' % (i, entrance[0], entrance[1]), False, [0, 255, 0]), [e[0] + 3, e[1] - (self.debug_font_rect.size('E')[1]/2)])
                i += 1

    def animate(self, screen, fps):
        global DRAW_MODES
        
        self.section_times = []
        self.delta = 60 / fps
        
        SURF = pygame.Surface([640, 360])
        safezone = False

        blit_time = time.time()
        special_vars = {}
        special_vars['cameraX'], special_vars['cameraY'] = self.camera_pos[0], self.camera_pos[1]
        if self.player != None:
            special_vars['playerX'] = self.player.pos[0]
            special_vars['playerY'] = self.player.pos[1]
        else:
            special_vars['playerX'], special_vars['playerY'] = 0, 0

        for sprite in self.sprites:
            special_vars[sprite.id + 'X'] = sprite.pos[0]
            special_vars[sprite.id + 'Y'] = sprite.pos[1]
        special_vars['censored'] = 'fuck' in self.vars['custom_names'].keys()
        special_vars['profanity'] = not special_vars['censored']
        if type(self.draw_mode) == str:
            special_vars['draw_mode'] = ''.join([self.draw_mode])
        else:
            special_vars['draw_mode'] = self.draw_mode.name

        self.section_times.append(time.time() - blit_time) # Time for setting up vars

        if [self.black_surf.get_rect()[2],
            self.black_surf.get_rect()[3]] != [screen.get_rect().w, screen.get_rect().h]:
            self.black_surf = pygame.transform.scale(self.black_surf, [screen.get_rect().w, screen.get_rect().h])

        if self.player != None:
            self.player.movement_speed = 2 * (60 / fps)

        menu_items = self.menu_items

        # Remove menu text if menu isn't active
        if self.menu == None:
            if self.find_text('menuitem0') != None:
                i = 0
                for item in menu_items:
                    self.remove_text(self.find_text('menuitem' + str(i)))
                    i += 1

                i = 0
                for char in self.party:
                    self.remove_text(self.find_text('character' + str(i)))
                    i += 1
        else:
            if self.player != None:
                self.player.move_vector = [0, 0]

        # Dealing with triggers
        if self.trigger_active or self.menu != None:
            if self.menu != None: # DRAW THE MENU
                if self.find_text("menuitem0") == None: # Generate menu
                    i = 0
                    for item in menu_items:
                        self.add_text({'id': 'menuitem' + str(i),
                                       'font': pygame.font.Font('res/fonts/coderscrux.ttf', 16),
                                       'text': item,
                                       'size': 16,
                                       'color': [255, 255, 255],
                                       'alignment': [0.5, 0],
                                       'aliased': True,
                                       'position': [560, 16 + (18 * i)]})
                        i += 1

                    i = 0
                    for char in self.party:
                        if 'custom_name' in char.keys():
                            text = char['custom_name']
                        else:
                            text = char['name']
                        
                        self.add_text({'id': 'character' + str(i),
                                       'font': pygame.font.Font('res/fonts/coderscrux.ttf', 32),
                                       'text': text,
                                       'size': 32,
                                       'color': [255, 255, 255],
                                       'alignment': [0, 0],
                                       'aliased': True,
                                       'position': [86, 24 + (64 * i)]})
                        i += 1
                else:
                    i = 0
                    for item in menu_items:
                        self.find_text('menuitem' + str(i))['color'] = [255, 255, 255]
                        i += 1
                    self.find_text('menuitem' + str(self.selected[0]))['color'] = [40, 122, 255]
                    
            elif self.current_trigger != None:
                try:
                    if self.current_step == 0:
                        self.player.stop_animation('idle')
                        self.player.play_animation('idle')
                    
                    screen_refresh = False

                    while not screen_refresh: # Iterates through steps that are to executed on the same frame
                        step = self.current_trigger[self.current_step]
                        screen_refresh = True
                        
                        if step['type'] == 'goto': #goto room entrance
                            if self.fade not in ['out', '_out']:
                                self.fade = 'out'
                                self.goingtonewmap = True

                                if 'sound' in step.keys():
                                    if step['sound'].split('|')[1] == 'default':
                                        self.sounds['Run'].play()
                                    elif step['sound'].split('|')[1] not in ["", "None"]:
                                        pygame.mixer.Sound('res/sound/%s' % step['sound'].split('|')[1]).play()
                                else:
                                    self.sounds['Run'].play()
                        if step['type'] in ['say', 'prompt', 'promptitem']: #say text rect color image milliseconds
                            if step['rect'] == [0, 0, 0, 0]:
                                saybox = [240, 16, 640 - 240 - 16, 96]
                            else:
                                saybox = step['rect']
                            
                            if self.say_state == 0:
                                self.say_box = [saybox[0], saybox[1], saybox[2], 1]
                                self.say_state = 1

                                if step['type'] == 'promptitem':
                                    step['type'] = 'prompt'
                                    options = []
                                    if step['partymember'].split('|')[1] == 'key_items':
                                        for item in self.vars['key_items']:
                                            options.append(item['name'])
                                    else:
                                        for member in self.party:
                                            if member['id'] in step['partymember'].split('|')[1].split(','):
                                                for item in member['bag']:
                                                    options.append(item['name'])
                                                    
                                    options.append('CANCEL')

                                    step['options'] = options
                            
                            elif self.say_state < 20:
                                self.say_state += 1.5 * (60 / fps)
                                if self.say_state > 20:
                                    self.say_state = 20
                                
                                self.say_box = [saybox[0], saybox[1], saybox[2], int(saybox[3] * (self.say_state / 20.0))]
                                
                            elif self.say_state == 20:
                                self.say_box = saybox

                                if self.find_text('say trigger') == None:
                                    self.add_text({'id': "say trigger",
                                                   'font': pygame.font.Font('res/fonts/coderscrux.ttf', 16),
                                                   'text': "",
                                                   'size': 16,
                                                   'color': step['color'],
                                                   'alignment': [0, 0],
                                                   'position': [saybox[0] + 4, saybox[1] + 4]})

                                    if step['image'] != "#img":
                                        self.say_image = step['image']
                                        self.find_text('say trigger')['position'][0] += self.say_image.get_rect().w
                                        mod = self.say_image.get_rect().w
                                    else:
                                        self.say_image = None
                                        mod = 0
                                    
                                    st = "a"
                                    while pygame.font.Font('res/fonts/coderscrux.ttf', 16).size(st)[0] < self.say_box[2] - 8 - mod:
                                        st = st + 'a'

                                    self.find_text('say trigger')['char_wrap'] = len(st)
                                    
                                    self.temp_variable = [step['text'].split('|')[1]]
                                    for name in self.vars['custom_names'].keys():
                                        self.temp_variable[0] = self.temp_variable[0].replace(name, self.vars['custom_names'][name])

                                    if 'milliseconds' in step.keys() and step['type'] == 'say':
                                        if step['milliseconds'] > 0:
                                            self.temp_variable.append(time.time())

                                    if len(self.temp_variable) == 1:
                                        self.say_arrow = [time.time(), True]
                                        
                                elif len(self.find_text('say trigger')['text']) != len(self.temp_variable[0]):
                                    if self.find_text('say trigger')['text'] == "":
                                        ind = 1
                                    else:
                                        ind = len(self.find_text('say trigger')['text']) + int(60 / fps)

                                        if int(60 / fps) < 1:
                                            ind = len(self.find_text('say trigger')['text']) + 1
                                        if ind >= len(self.temp_variable[0]):
                                            ind = len(self.temp_variable[0])

                                    snd_mod = int(3 * (fps / 60))
                                    if snd_mod < 1:
                                        snd_mod = 1
                                    if len(self.find_text('say trigger')['text']) % snd_mod == 0:
                                        if 'Text' in self.sounds.keys():
                                            self.sounds['Text'].play()

                                    self.find_text('say trigger')['text'] = self.temp_variable[0][0:ind]
                                    
                                elif len(self.find_text('say trigger')['text']) == len(self.temp_variable[0]) and step['type'] == 'prompt':
                                    if len(self.temp_variable) < 2:
                                        self.temp_variable.append(step['options'])
                                        self.temp_variable.append(self.find_text('say trigger')['position'][0])
                                        self.temp_variable.append((16 * len(textwrap.wrap(self.temp_variable[0], self.find_text('say trigger')['char_wrap']))) + saybox[1] + 8)
                                        self.selected = 0

                                if 'milliseconds' in step.keys() and step['type'] == 'say':
                                    if step['milliseconds'] > 0:
                                        if time.time() - self.temp_variable[1] > step['milliseconds'] / 1000.0:
                                            self.say_state = 21

                            elif self.say_state >= 21:
                                self.say_state += 1.5 * (60 / fps)
                                if self.say_state > 40:
                                    self.say_state = 0
                                    self.say_box = None
                                    self.temp_variable = None
                                    self.say_arrow = None
                                    self.current_step += 1

                                    self.remove_text(self.find_text('say trigger'))
                                else:
                                    flag = True
                                    if step['type'] != 'say':
                                        try:
                                            self.vars['prompt'] = step['options'][self.selected][:]
                                        except TypeError:
                                            self.say_state = 20
                                            self.say_box = saybox
                                            flag = False

                                    if flag:
                                        self.say_box = [saybox[0], saybox[1], saybox[2], int(saybox[3] * ((40 - self.say_state) / 20.0))]
                                        self.find_text('say trigger')['text'] = ''
                                        self.say_image = None

                                        if step['type'] != 'say':
                                            pass
                        
                        if step['type'] == 'if' or step['type'] == 'waituntil': #if var predicate value true_cond false_cond
                                                                                #waituntil var predicate value
                            condition_met = False

                            checking_for = step['var'].split('|')[1]
                            if checking_for in special_vars.keys():
                                checking_for = special_vars[checking_for]
                            else:
                                if checking_for in self.vars.keys():
                                    checking_for = self.vars[checking_for]
                                else:
                                    checking_for = None

                            checking_against = step['value'].split('|')[1]

                            if step['var'].split('|')[1].lower() in ['mapid', 'map_id'] and step['value'].split('|')[1] in ['played_before', 'playedbefore']:
                                if step['predicate'].split('|')[1] == '=':
                                    condition_met = self.id in self.vars['played_maps']
                                if step['predicate'].split('|')[1] == '!=':
                                    condition_met = self.id not in self.vars['played_maps']

                                print condition_met
                            else:
                                y_keys = ['cameraY', 'playerY']
                                for sprite in self.sprites:
                                    y_keys.append(sprite.id + 'Y')
                                
                                if step['var'].split('|')[1] in y_keys:
                                    checking_against = str(int(checking_against) - 328)
                                    if step['var'].split('|')[1] != 'cameraY':
                                        checking_for = str(int(checking_for) + 328)

                                if checking_against == None or checking_for == None:
                                    condition_met = False
                                else:
                                    if step['predicate'].split('|')[1] == '=':
                                        condition_met = str(checking_against) == str(checking_for)
                                    if step['predicate'].split('|')[1] == '!=':
                                        condition_met = str(checking_against) != str(checking_for)
                                    if step['predicate'].split('|')[1] == '>=':
                                        condition_met = int(checking_for) >= int(checking_against)
                                    if step['predicate'].split('|')[1] == '>':
                                        condition_met = int(checking_for) > int(checking_against)
                                    if step['predicate'].split('|')[1] == '<=':
                                        condition_met = int(checking_for) <= int(checking_against)
                                    if step['predicate'].split('|')[1] == '<':
                                        condition_met = int(checking_for) < int(checking_against)

                            if condition_met:
                                if step['type'] == 'waituntil':
                                    self.current_step += 1
                                else:
                                    if step['true_cond'].split('|')[1] == 'continue':
                                        self.current_step += 1
                                    elif step['true_cond'].split('|')[1] == 'end':
                                        if self.current_trigger['id'] == 'on_start':
                                            if self.id not in self.vars['played_maps']:
                                                self.vars['played_maps'].append(self.id)
                                        self.current_trigger = None
                                    elif step['true_cond'].split('|')[1][0] in ['s', 'S']:
                                        try:
                                            self.current_step = int(step['true_cond'].split('|')[1][1:len(step['true_cond'].split('|')[1])].replace('s','').replace('S','')) - 1
                                        except ValueError:
                                            self.current_trigger = self.triggers[step['true_cond'].split('|')[1]]
                                            self.current_step = 0
                                    else:
                                        self.current_trigger = self.triggers[step['true_cond'].split('|')[1]]
                                        self.current_step = 0
                            elif step['type'] == 'if':
                                if step['false_cond'].split('|')[1] == 'continue':
                                    self.current_step += 1
                                elif step['false_cond'].split('|')[1] == 'end':
                                    if self.current_trigger['id'] == 'on_start':
                                            if self.id not in self.vars['played_maps']:
                                                self.vars['played_maps'].append(self.id)
                                    self.current_trigger = None
                                elif step['false_cond'].split('|')[1][0] in ['s', 'S']:
                                    try:
                                        self.current_step = int(step['false_cond'].split('|')[1][1:len(step['false_cond'].split('|')[1])].replace('s','').replace('S','')) - 1
                                    except ValueError:
                                        self.current_trigger = self.triggers[step['false_cond'].split('|')[1]]
                                        self.current_step = 0
                                else:
                                    self.current_trigger = self.triggers[step['false_cond'].split('|')[1]]
                                    self.current_step = 0
                                
                        if step['type'] == 'giveitem': #giveitem item keyitem
                            flag = False
                            if 'keyitem' in step.keys():
                                flag = step['keyitem'].split('|')[1].lower() in ['true', 't', 'yes', 'y']

                            if flag: # Key item
                                self.vars['key_items'].append(ITEM_LIBRARY[step['item'].split('|')[1]].copy())
                            else:
                                for player in self.party:
                                    if len(player['bag']) < player['bag_size']:
                                        player['bag'].append(ITEM_LIBRARY[step['item'].split('|')[1]].copy())
                                        break
                            self.current_step += 1
                        if step['type'] == 'removeitem': #removeitem item partymember
                            if step['partymember'].split('|')[1] == 'key_items':
                                for item in self.vars['key_items']:
                                    if item['id'] == step['item'].split('|')[1]:
                                        self.vars['key_items'].remove(item)
                                        break
                            else:
                                member_index, i = -1, 0
                                for member in self.party:
                                    if member['id'] in step['partymember'].split('|')[1].split(','):
                                        member_index = i
                                        break
                                    i += 1
                                    
                                for item in self.party[member_index]['bag']:
                                    if item['id'] == step['item'].split()[1]:
                                        self.party[member_index]['bag'].remove(item)
                                        break
                            self.current_step += 1
                        if step['type'] == 'givemoney': #givemoney amount
                            self.money += int(step['amount'])
                            self.current_step += 1
                        if step['type'] == 'setvar': #setvar var value
                            self.vars[step['var'].split('|')[1]] = step['value'].split('|')[1]
                            self.current_step += 1
                        if step['type'] == 'changevar': #changevar var value
                            if step['var'] in special_vars.keys():
                                pass
                            else:
                                self.vars[step['var']] = int(self.vars[step['var']]) + int(step['value'])
                                self.current_step += 1
                        if step['type'] == 'activate': #activate trigger/rectid
                            if step['trigger'].split('|')[1] not in [None, ""]:
                                if step['trigger'].split('|')[1] in self.triggers.keys():
                                    pass
                            else:
                                if step['rectid'].split('|')[1] not in [None, ""] and step['rectid'].split('|')[1] in self.rects.keys():
                                    self.rects[step['rectid'].split('|')[1]]['active'] = True
                        if step['type'] == 'deactivate': #deactivate rectid
                            if step['rectid'].split('|')[1] not in [None, ""] and step['rectid'].split('|')[1] in self.rects.keys():
                                self.rects[step['rectid'].split('|')[1]]['active'] = False
                        if step['type'] == 'animate': #animate sprite anim_id
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])

                            if sp != None:
                                if step['anim_id'].split('|')[1] in ["None", '']:
                                    sp.stop_animation()
                                else:
                                    sp.stop_animation()
                                    sp.play_animation(step['anim_id'].split('|')[1])
                            self.current_step += 1
                        if step['type'] == 'move': #move sprite x y
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                                self.moving_in_cutscene = True
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                            if sp != None:
                                sp.dest = [step['x'], self.dims[1] - step['y']]
                            self.current_step += 1
                        if step['type'] == 'movecamera': #movecamera x y
                            self.camera_moveto = [step['x'], step['y'] - 328]
                            self.current_step += 1
                        if step['type'] == 'spawn': #spawn sprite x y metadata
                            if step['sprite'].split('|')[1] == 'player':
                                if type(self.party[0]['sprite']) == str:
                                    self.party[0]['sprite'] = SPRITE_LIBRARY[self.party[0]['sprite']].copy()
                                self.player = self.party[:][0]['sprite']
                                self.player.id = 'player'
                                self.player.pos = [step['x'], self.dims[1] - step['y']]
                                self.player.parent = self
                                self.player.movement_speed = 2 * (60 / fps)
                            elif step['sprite'].split('|')[1] == 'party' and not self.party_in_field:
                                self.party_in_field = True
                                dests = [[self.player.pos[0], self.player.pos[1] - 32],
                                         [self.player.pos[0], self.player.pos[1] + 32],
                                         [self.player.pos[0] - 32, self.player.pos[1]],
                                         [self.player.pos[0] + 32, self.player.pos[1]]]
                                if 'metadata' in step.keys():
                                    if len(step['metadata'].split('|')) > 1:
                                        m = step['metadata'].split('|')[1].split(';')
                                        metadata = {}

                                        for data in m:
                                            if data != '':
                                                key = data.split('=')[0]
                                                val = data.split('=')[1]

                                                if len(val.split(',')) < 2:
                                                    try:
                                                        val = int(val)
                                                    except ValueError:
                                                        pass
                                                else:
                                                    lst = []
                                                    for value in val.split(','):
                                                        try:
                                                            value = int(value)
                                                        except ValueError:
                                                            pass

                                                        if value == 'None':
                                                            value = None

                                                        if value != '':
                                                            lst.append(value)
                                                    val = lst[:]

                                                if val == 'None':
                                                    val = None

                                                metadata[key] = val

                                        if 'disable' in metadata.keys():
                                            for item in metadata['disable']:
                                                if item.lower() in ['up', 'u']:
                                                    dests.remove([self.player.pos[0], self.player.pos[1] - 32])
                                                if item.lower() in ['down', 'd']:
                                                    dests.remove([self.player.pos[0], self.player.pos[1] + 32])
                                                if item.lower() in ['left', 'l']:
                                                    dests.remove([self.player.pos[0] - 32, self.player.pos[1]])
                                                if item.lower() in ['right', 'r']:
                                                    dests.remove([self.player.pos[0] + 32, self.player.pos[1]])
                                        if 'prioritize' in metadata.keys():
                                            item = metadata['prioritize']
                                            if item.lower() in ['up', 'u']:
                                                dests.remove([self.player.pos[0], self.player.pos[1] - 32])
                                                dests.insert(0, [self.player.pos[0], self.player.pos[1] - 32])
                                            if item.lower() in ['down', 'd']:
                                                dests.remove([self.player.pos[0], self.player.pos[1] + 32])
                                                dests.insert(0, [self.player.pos[0], self.player.pos[1] + 32])
                                            if item.lower() in ['left', 'l']:
                                                dests.remove([self.player.pos[0] - 32, self.player.pos[1]])
                                                dests.insert(0, [self.player.pos[0] - 32, self.player.pos[1]])
                                            if item.lower() in ['right', 'r']:
                                                dests.remove([self.player.pos[0] + 32, self.player.pos[1]])
                                                dests.insert(0, [self.player.pos[0] + 32, self.player.pos[1]])
                                            
                                for member in self.party:
                                    if self.party.index(member) != 0:
                                        s = self.party[:][self.party.index(member)]['sprite']
                                        if type(s) == str:
                                            self.party[self.party.index(member)]['sprite'] = SPRITE_LIBRARY.copy()[s.replace('p_', '').lower()]
                                            s = self.party[:][self.party.index(member)]['sprite']
                                        s.parent = self
                                        s.pos = self.player.pos[:]
                                        s.id = 'p_' + self.party[:][self.party.index(member)]['name']
                                        s.movement_speed = 2
                                        s.dest = dests[self.party.index(member) - 1]
                                        self.sprites.append(s)
                            else:
                                if step['sprite'].split('|')[1] not in SPRITE_LIBRARY.keys():
                                    spr = load_sprite(step['sprite'].split('|')[1], [step['x'], self.dims[1] - step['y']])
                                else:
                                    spr = copy.copy(SPRITE_LIBRARY.copy()[step['sprite'].split('|')[1]])
                                    spr.pos = [step['x'], self.dims[1] - step['y']]

                                if 'metadata' in step.keys():
                                    if len(step['metadata'].split('|')) > 1:
                                        metadata = step['metadata'].split('|')[1].split(';')

                                        for data in metadata:
                                            if data != '':
                                                key = data.split('=')[0]
                                                val = data.split('=')[1]

                                                if len(val.split(',')) < 2:
                                                    try:
                                                        val = int(val)
                                                    except ValueError:
                                                        pass
                                                else:
                                                    lst = []
                                                    for value in val.split(','):
                                                        try:
                                                            value = int(value)
                                                        except ValueError:
                                                            pass

                                                        if value == 'None':
                                                            value = None

                                                        if value != '':
                                                            lst.append(value)
                                                    val = lst[:]

                                                if val == 'None':
                                                    val = None

                                                if key == 'zorder':
                                                    spr.z_order = val
                                                else:
                                                    spr.temp_variable[key] = val
                                    spr.temp_variable = spr.temp_variable.copy()
                                self.add_sprite(spr)
                                
                            self.current_step += 1
                        if step['type'] == 'spawnat': #spawnat sprite spawnsprite metadata
                            ssp = None
                            if step['spawnsprite'].split('|')[1] == 'player':
                                ssp = self.player
                            else:
                                ssp = self.find_sprite(step['spawnsprite'].split('|')[1])
                            
                            if ssp != None:
                                if step['sprite'].split('|')[1] == 'player':
                                    self.player = self.party[:][0]['sprite']
                                    self.player.id = 'player'
                                    self.player.pos = ssp.pos[:]
                                    self.player.parent = self
                                    self.player.movement_speed = 2 * (60 / fps)
                                elif step['sprite'].split('|')[1] == 'party' and not self.party_in_field:
                                    self.party_in_field = True
                                    dests = [[self.player.pos[0], self.player.pos[1] - 32],
                                             [self.player.pos[0], self.player.pos[1] + 32],
                                             [self.player.pos[0] - 32, self.player.pos[1]],
                                             [self.player.pos[0] + 32, self.player.pos[1]]]
                                    for member in self.party:
                                        if self.party.index(member) != 0:
                                            s = self.party[:][self.party.index(member)]['sprite']
                                            if type(s) == str:
                                                self.party[self.party.index(member)]['sprite'] = SPRITE_LIBRARY[s.replace('p_', '').lower()].copy()
                                                s = self.party[:][self.party.index(member)]['sprite']
                                            s.parent = self
                                            s.pos = self.player.pos[:]
                                            s.id = 'p_' + self.party[:][self.party.index(member)]['name']
                                            s.movement_speed = 2
                                            s.dest = dests[self.party.index(member) - 1]
                                            self.sprites.append(s)
                                else:
                                    if step['sprite'].split('|')[1] not in SPRITE_LIBRARY.keys():
                                        spr = load_sprite(step['sprite'].split('|')[1], ssp.pos[:])
                                    else:
                                        spr = SPRITE_LIBRARY[step['sprite'].split('|')[1]].copy()
                                        spr.pos = ssp.pos[:]

                                    if 'metadata' in step.keys():
                                        if len(step['metadata'].split('|')) > 1:
                                            metadata = step['metadata'].split('|')[1].split(';')

                                            for data in metadata:
                                                if data != '':
                                                    key = data.split('=')[0]
                                                    val = data.split('=')[1]

                                                    if len(val.split(',')) < 2:
                                                        try:
                                                            val = int(val)
                                                        except ValueError:
                                                            pass
                                                    else:
                                                        lst = []
                                                        for value in val.split(','):
                                                            try:
                                                                value = int(value)
                                                            except ValueError:
                                                                pass

                                                            if value == 'None':
                                                                value = None

                                                            if value != '':
                                                                lst.append(value)
                                                        val = lst[:]

                                                    if val == 'None':
                                                        val = None

                                                    if key == 'zorder':
                                                        spr.z_order = val
                                                    else:
                                                        spr.temp_variable[key] = val
                                        spr.temp_variable = spr.temp_variable.copy()
                                    self.add_sprite(spr)
                                
                            self.current_step += 1
                        if step['type'] == 'despawn': #despawn sprite
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                            
                            if sp != None:
                                if sp != self.player:
                                    self.sprites.remove(sp)
                                else:
                                    self.player = None
                            else:
                                if self.party_in_field and step['sprite'].split('|')[1] == 'party':
                                    party_list = []
                                    for member in self.party:
                                        if self.party.index(member) != 0:
                                            party_list.append('p_' + self.party[:][self.party.index(member)]['name'])

                                    for name in party_list:
                                        self.find_sprite(name).dest = self.player.pos[:]

                                    self.party_in_field = False
                                
                            self.current_step += 1
                        if step['type'] == 'settile': #settile tile_x tile_y z_order value
                            tile_coord = [int(step['tile_x'].split('|')[1], 16), int(step['tile_y'].split('|')[1], 16)]
                            if step['z_order'] in self.layers.keys():
                                for t in self.layers[step['z_order']]:
                                    if tile_coord[0] * 32 == t[1][0] and tile_coord[1] * 32 == t[1][1]:
                                        t[0] = self.tiles[int(step['value'].split('|')[1], 16)]
                                        break
                            
                            self.current_step += 1
                        if step['type'] in ['moveto', 'jumpto']: #moveto/jumpto trigger/step
                            print step['trigger']
                            
                            if self.current_trigger['id'] == 'on_start':
                                if self.id not in self.vars['played_maps']:
                                    self.vars['played_maps'].append(self.id)
                                    
                            if step['trigger'].split('|')[1] == 'continue':
                                self.current_step += 1
                            elif step['trigger'].split('|')[1] == 'end':
                                self.current_trigger = None
                            elif step['trigger'].split('|')[1][0] in ['s', 'S']:
                                try:
                                    self.current_step = int(step['trigger'].split('|')[1][1:len(step['trigger'].split('|')[1])].replace('s','').replace('S','')) - 1
                                except ValueError:
                                    self.current_trigger = self.triggers[step['trigger'].split('|')[1]]
                                    self.current_step = 0
                            else:
                                self.current_trigger = self.triggers[step['trigger'].split('|')[1]]
                                self.current_step = 0
                        if step['type'] == 'playsound': #playsound sound
                            if step['sound'] in self.sounds.keys():
                                self[step['sound']].play()
                            else:
                                pygame.mixer.Sound("res/sound/" + step['sound'].split('|')[1]).play()
                            self.current_step += 1
                        if step['type'] == 'wait': #wait milliseconds
                            if self.millisec_wait == None:
                                self.millisec_wait = int(step['milliseconds'])
                                self.wait_timer = time.time()
                            else:
                                if time.time() - self.wait_timer > self.millisec_wait / 1000.0:
                                    self.millisec_wait = None
                                    self.current_step += 1
                        if step['type'] == 'changetrigger': #changetrigger sprite/rectid trigger
                            if step['rectid'].split('|')[1] not in [None, ""] and step['rectid'].split('|')[1] in self.rects.keys():
                                self.rects[step['rectid'].split('|')[1]]['trigger'] = step['trigger'].split('|')[1]
                        if step['type'] == 'lockcamera': #lockcamera
                            self.camera_locked = True
                            self.current_step += 1
                        if step['type'] == 'unlockcamera': #unlockcamera
                            self.camera_locked = False
                            self.current_step += 1
                        if step['type'] == 'fadeout': #fadeout milliseconds
                            self.music_fade = step['milliseconds'] / 1000.0
                            self.current_step += 1
                        if step['type'] == 'resumemusic': #resumemusic
                            if MUSIC_CHANNEL.get_busy():
                                self.music_fade = -1
                            else:
                                if len(self.music) < 2:
                                    if len(self.music) > 0:
                                        MUSIC_CHANNEL.play(self.music[0])
                                else:
                                    MUSIC_CHANNEL.play(self.music[0], -1)
                                MUSIC_CHANNEL.set_volume(1.0)

                            self.current_step += 1
                        if step['type'] == 'changemusic': #changemusic intro loop
                            try:
                                previous_music_info = {'music': self.music[:], 'state': self.playback_state,
                                                       'timer': self.music_timer, 'elapsed': self.music_elapsed,
                                                       'music_names': self.music_names[:]}
                            except AttributeError:
                                previous_music_info = {'music': [], 'music_names': [],
                                                       'state': self.playback_state}

                            try:
                                self.music_names = [step['intro'].split('|')[1]]
                            except IndexError:
                                self.music_names = []
                            if len(step['loop'].split('|')) > 1:
                                self.music_names.append(step['loop'].split('|')[1])
                            
                            if self.music_names != previous_music_info['music_names']:
                                try:
                                    self.music = [pygame.mixer.Sound('res/sound/' + step['intro'].split('|')[1])]
                                    if len(step['loop'].split('|')) > 1:
                                        self.music.append(pygame.mixer.Sound('res/sound/' + step['loop'].split('|')[1]))
                                    self.playback_state = 2 - len(self.music)
                                except IndexError:
                                    self.music = []
                                    self.playback_state = 1

                                self.music_elapsed = time.time()
                                self.music_paused = False
                                self.wait_flag = True
                            else:
                                self.music_timer = previous_music_info['timer'] + 1
                                self.music_elapsed = previous_music_info['elapsed']
                                self.playback_state = previous_music_info['state']
                                self.music = previous_music_info['music']
                                self.music_paused = False
                                self.wait_flag = False

                            MUSIC_CHANNEL.stop()

                            self.current_step += 1
                        if step['type'] == 'flipsprite': #flipsprite sprite x y
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                                
                            if sp != None:
                                if step['x'].split('|')[1] == 'True':
                                    xflip = True
                                else:
                                    xflip = False

                                if step['y'].split('|')[1] == 'True':
                                    yflip = True
                                else:
                                    yflip = False

                                sp.flip = [xflip, yflip]

                            self.current_step += 1

                        if step['type'] == 'moverelative': #moverelative sprite x y
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                                self.moving_in_cutscene = True
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                            if sp != None:
                                sp.dest = [sp.pos[0] + step['x'], sp.pos[1] + step['y']]
                            self.current_step += 1

                        if step['type'] == 'movecamerarelative': #movecamerarelative x y
                            self.camera_moveto = [self.camera_pos[0] + step['x'], self.camera_pos[1] + step['y']]
                            self.current_step += 1

                        if step['type'] == 'teleport': #teleport sprite x y
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                            if sp != None:
                                sp.pos = [step['x'], self.dims[1] - step['y']]
                            self.current_step += 1

                        if step['type'] == 'changemovespeed': #changemovespeed sprite val
                            sp = None
                            if step['sprite'].split('|')[1] == 'player':
                                sp = self.player
                            else:
                                sp = self.find_sprite(step['sprite'].split('|')[1])
                            if sp != None:
                                sp.movement_speed = step['val']
                            self.current_step += 1

                        if step['type'] == 'changecameraspeed': #changecameraspeed val
                            self.camera_movespeed = step['val']
                            self.current_step += 1

                        if step['type'] == 'party':
                            if step['action'].find('#str(') == 0:
                                ind = step['action'].find('(')
                                remove = '('
                                while step['action'][ind] != ')':
                                    ind += 1
                                    remove = remove + step['action'][ind]

                                step['action'].replace(remove, '')

                            if step['action'].split('|')[1] == 'add':
                                pass
                            elif step['action'].split('|')[1] == 'remove':
                                pass

                            self.current_step += 1

                        if step['type'] == 'changedrawmode': #changedrawmode function/levelclassname/default
                            if step['function'].split('|')[1].endswith('.py'):
                                with open('res/modes/' + step['function'].split('|')[1]) as f:
                                    self.draw_mode = f.read()
                            else:
                                self.draw_mode = step['function'].split('|')[1]

                            self.current_step += 1

                        if step['type'] == 'toblack': #toblack
                            if self.fade not in ['out', '_out']:
                                self.fade = 'out'

                        if step['type'] == 'fromblack': #fromblack
                            if self.fade not in ['in', '_in']:
                                self.fade = 'in'

                        if step['type'] == 'healparty': #healparty hp sp
                            for i in xrange(len(self.party)):
                                if step['hp'].split('|')[1] == 'True':
                                    self.party[i]['HP'][0] = self.party[i]['HP'][1]
                                if step['sp'].split('|')[1] == 'True':
                                    self.party[i]['SP'][0] = self.party[i]['SP'][1]
                            self.current_step += 1

                        if step['type'] == 'save': #save savefile
                            self.save_file(step['savefile'].split('|')[1])

                            self.current_step += 1

                        if 'refresh' in step.keys():
                            if step['refresh']:
                                screen_refresh = True
                            else:
                                screen_refresh = False
                        else:
                            screen_refresh = True
                        
                except KeyError:
                    print traceback.format_exc()
                    # Adding level to played maps
                    if self.current_trigger['id'] == 'on_start':
                        if self.id not in self.vars['played_maps']:
                            self.vars['played_maps'].append(self.id)
                            
                    self.current_trigger = None
                    self.trigger_active = False

            if self.current_trigger != None:
                if self.current_step + 2 >= len(self.current_trigger.keys()):
                    self.current_trigger = None
                    self.trigger_active = False

                # Adding level to played maps
                if self.current_trigger == None:
                    if self.id not in self.vars['played_maps']:
                        self.vars['played_maps'].append(self.id)
            else:
                self.trigger_active = False
        else:
            # Collision detection
            if self.player != None:
                player_collision_rect = pygame.Rect(self.player.pos[0] - (self.player.img_width / 2) + self.player.move_vector[0],
                                                    self.player.pos[1] - 6 + self.player.move_vector[1], self.player.img_width, 6)
                collision = False
                
                for sprite in self.sprites:
                    if sprite.collide_rect != None:
                        hard_col = None
                        if 'hardcollision' in sprite.temp_variable.keys():
                            hard_col = sprite.temp_variable['hardcollision']

                        if player_collision_rect.colliderect(sprite.collide_rect.move([sprite.pos[0] - (sprite.img_width / 2), sprite.pos[1]])) and hard_col != None:
                            if hard_col:
                                collision = True
                                break

                if collision:
                    self.player.pos[0] -= self.player.move_vector[0]
                    self.player.pos[1] -= self.player.move_vector[1]
                    self.player.move_vector = [0, 0]
                else:
                    num_black  = 0
                    num_white  = 0
                    num_silver = 0
                    num_reds   = 0
                    for y in xrange(player_collision_rect.y, player_collision_rect.y + player_collision_rect.h):
                        for x in xrange(player_collision_rect.x, player_collision_rect.x + player_collision_rect.w):
                            try:
                                if self.collision.get_at([x, y]) == pygame.Color(0, 0, 0):
                                    num_black += 1
                                if self.collision.get_at([x, y]) == pygame.Color(255, 0, 0):
                                    num_reds += 1
                                if self.collision.get_at([x, y]) == pygame.Color(255, 255, 255):
                                    num_white += 1
                                if self.collision.get_at([x, y]) == pygame.Color(215, 215, 215):
                                    num_silver += 1
                            except IndexError:
                                num_black += 1

                    if num_white != player_collision_rect.w * player_collision_rect.h and num_silver > 0:
                        collision = True
                        self.player.pos[0] -= self.player.move_vector[0]
                        self.player.pos[1] -= self.player.move_vector[1]
                        self.player.move_vector = [0, 0]
                    if num_black + num_reds >= 4:
                        collision = True
                        self.player.pos[0] -= self.player.move_vector[0]
                        self.player.pos[1] -= self.player.move_vector[1]
                        self.player.move_vector = [0, 0]
                            
                    if num_black >= 1:
                        collision = True
                        self.player.pos[0] -= self.player.move_vector[0]
                        self.player.pos[1] -= self.player.move_vector[1]
                        self.player.move_vector = [0, 0]

                    if not collision:
                        try:
                            pos = [int(self.player.pos[0]), int(self.player.pos[1])]
                            if self.collision.get_at(pos) == pygame.Color(0, 0, 0):
                                collision = True
                                self.player.pos[0] -= self.player.move_vector[0]
                                self.player.pos[1] -= self.player.move_vector[1]
                                self.player.move_vector = [0, 0]
                            if self.collision.get_at(pos) in pygame.Color(215, 215, 215):
                                collision = True
                                self.player.pos[0] -= self.player.move_vector[0]
                                self.player.pos[1] -= self.player.move_vector[1]
                                self.player.move_vector = [0, 0]
                                
                        except IndexError:
                            collision = True
                            self.player.pos[0] -= self.player.move_vector[0]
                            self.player.pos[1] -= self.player.move_vector[1]
                            self.player.move_vector = [0, 0]
            
            # Player movement
            if self.player != None:
                self.player.move_vector = [0, 0]
                if (((not self.quit) and (type(self.draw_mode) == str))):
                    l, r, u, d = False, False, False, False
                    for key in self.keys['left']:
                        if pygame.key.get_pressed()[key]:
                            l = True
                            break
                    for key in self.keys['right']:
                        if pygame.key.get_pressed()[key]:
                            r = True
                            break
                    for key in self.keys['up']:
                        if pygame.key.get_pressed()[key]:
                            u = True
                            break
                    for key in self.keys['down']:
                        if pygame.key.get_pressed()[key]:
                            d = True
                            break
                    if l:
                        self.player.move_vector[0] -= self.player.movement_speed
                    if r:
                        self.player.move_vector[0] += self.player.movement_speed
                    if u:
                        self.player.move_vector[1] -= self.player.movement_speed * self.vertical
                    if d:
                        self.player.move_vector[1] += self.player.movement_speed * self.vertical

                    if self.player.pos[0] + self.player.move_vector[0] < 0:
                        self.player.move_vector[0] = 0

                    if self.player.move_vector[0] != 0 and self.player.move_vector[1] != 0:
                        self.player.move_vector[0] /= 2**0.2
                        self.player.move_vector[1] /= 2**0.2
                else:
                    if self.quit:
                        self.player.move_vector = [0, 0]

        # Despawn party
        if not self.party_in_field and self.player != None:
            party_list = []
            for member in self.party:
                if self.party.index(member) != 0:
                    party_list.append('p_' + self.party[:][self.party.index(member)]['name'])

            for name in party_list:
                if self.find_sprite(name) != None:
                    s = self.find_sprite(name)
                    if s.dest == None or math.sqrt((s.pos[0] - self.player.pos[0])**2 + (s.pos[1] - self.player.pos[1])**2) < 3:
                        self.remove_sprite(s)

        # Player animation
        if self.player != None:
            if self.trigger_active and self.moving_in_cutscene and self.player.dest == None:
                self.moving_in_cutscene = False

                self.player.stop_animation()
                if self.current_step - 1 in self.current_trigger.keys():
                    if self.current_trigger[self.current_step - 1]['type'] == 'animate' and self.current_trigger[self.current_step - 1]['sprite'].split('|')[1] == 'player':
                        self.player.play_animation(self.current_trigger[self.current_step - 1]['anim_id'].split('|')[1])
                    elif self.current_trigger[self.current_step - 2]['type'] == 'animate' and self.current_trigger[self.current_step - 2]['sprite'].split('|')[1] == 'player':
                        self.player.play_animation(self.current_trigger[self.current_step - 2]['anim_id'].split('|')[1])
                    else:
                        if self.last_direction_moved[1] != None:
                            if self.last_direction_moved[0] not in [0, None]:
                                self.player.play_animation('idle')
                            else:
                                if self.last_direction_moved[1] > 0:
                                    self.player.play_animation('idle_front')
                                else:
                                    self.player.play_animation('idle_back')
                else:
                    if self.last_direction_moved[1] != None:
                        if self.last_direction_moved[0] not in [0, None]:
                            self.player.play_animation('idle')
                        else:
                            if self.last_direction_moved[1] > 0:
                                self.player.play_animation('idle_front')
                            else:
                                self.player.play_animation('idle_back')
                
            if self.player.move_vector[1] < 0 and 'walk_back' in self.player.animations.keys():
                if self.player.animation != 'walk_back':
                    self.player.stop_animation('walk_back')
                    self.player.play_animation('walk_back')
            elif self.player.move_vector[1] > 0 and 'walk_forward' in self.player.animations.keys():
                if self.player.animation != 'walk_forward':
                    self.player.stop_animation('walk_forward')
                    self.player.play_animation('walk_forward')
            elif self.player.move_vector[0] != 0:
                if self.player.animation != 'walk':
                    self.player.stop_animation('walk')
                    self.player.play_animation('walk')

                self.player.flip[0] = self.player.move_vector[0] < 0
            elif self.player.move_vector[1] == 0 and self.player.move_vector[0] == 0:
                if ((not self.trigger_active) or (self.trigger_active and self.moving_in_cutscene)):
                    if self.player.animation not in ['idle', 'idle_front', 'idle_back']:
                        self.player.stop_animation()
                        if self.last_direction_moved[1] != None:
                            if self.last_direction_moved[0] not in [0, None]:
                                self.player.play_animation('idle')
                            else:
                                if self.last_direction_moved[1] > 0:
                                    self.player.play_animation('idle_front')
                                else:
                                    self.player.play_animation('idle_back')

        if self.player != None:
            if self.player.move_vector != [0, 0]:
                self.last_direction_moved = self.player.move_vector[:]

        # Camera movement
        moveto = None
        if self.camera_moveto != None and self.camera_locked:
            moveto = self.camera_moveto[:]
        
        elif not self.camera_locked and self.player != None:
            self.camera_pos = [self.player.pos[0] - 320, self.dims[1] - self.player.pos[1] - 180]

        if moveto != None:
            if moveto[0] != None:
                if self.camera_pos[0] < moveto[0]:
                    self.camera_pos[0] += self.camera_movespeed * (60 / fps)
                elif self.camera_pos[0] > moveto[0]:
                    self.camera_pos[0] -= self.camera_movespeed * (60 / fps)

                if self.camera_pos[0] < moveto[0] + (self.camera_movespeed + 1) and self.camera_pos[0] > moveto[0] - (self.camera_movespeed + 1):
                    self.camera_pos[0] = moveto[0]
                    self.camera_moveto[0] = None

            if moveto[1] != None:
                if self.camera_pos[1] < moveto[1] + (self.camera_movespeed + 1):
                    self.camera_pos[1] += self.camera_movespeed * (60 / fps)
                elif self.camera_pos[1] > moveto[1] - (self.camera_movespeed + 1):
                    self.camera_pos[1] -= self.camera_movespeed * (60 / fps)

                if self.camera_pos[1] < moveto[1] + (self.camera_movespeed + 1) and self.camera_pos[1] > moveto[1] - (self.camera_movespeed + 1):
                    self.camera_pos[1] = moveto[1]
                    self.camera_moveto[1] = None

            if self.camera_moveto[0] == None and self.camera_moveto[1] == None:
                self.camera_moveto = None

        if self.restrict_player:
            if self.camera_pos[0] < 0:
                self.camera_pos[0] = 0
            if self.camera_pos[0] > self.dims[0] - 640:
                self.camera_pos[0] = self.dims[0] - 640
            if self.camera_pos[1] < 32:
                self.camera_pos[1] = 32

        # Fade in/out the music
        if self.music_fade != None:
            if self.music_fade > 0: # Fade out
                new_vol = MUSIC_CHANNEL.get_volume() - (1 / ((60 / fps) / self.music_fade)) / fps
                if new_vol < 0:
                    new_vol = 0
                    self.music_fade = None
                    MUSIC_CHANNEL.pause()
                MUSIC_CHANNEL.set_volume(new_vol)
            elif self.music_fade == 0: # Stop music
                if self.playback_state == 0:
                    self.music_paused = True
                    self.music_elapsed = time.time()
                MUSIC_CHANNEL.pause()
                self.music_fade = None
            else: # Fade in
                MUSIC_CHANNEL.unpause()
                if self.music_paused:
                    self.music_paused = False
                    self.music_timer += time.time() - self.music_elapsed

                new_vol = MUSIC_CHANNEL.get_volume() - (1 / ((60 / fps) / self.music_fade)) / fps
                if new_vol > 1:
                    new_vol = 1
                    self.music_fade = None
                MUSIC_CHANNEL.set_volume(new_vol)

        # Music playback
        if not self.wait_flag and len(self.music) != 0:
            if time.time() - self.music_timer > self.music[0].get_length() and len(self.music) > 1 and self.playback_state == 0 and not self.music_paused:
                self.playback_state = 1
                MUSIC_CHANNEL.play(self.music[1], -1)
        else:
            if time.time() - self.music_timer >= 1:
                self.music_timer = time.time()
                self.wait_flag = False
                if len(self.music) != 0:
                    if self.playback_state == 0:
                        MUSIC_CHANNEL.play(self.music[0])
                    else:
                        MUSIC_CHANNEL.play(self.music[0], -1)

        # Rect interaction
        if self.player != None and not self.trigger_active:
            possible_regions = []
            for rect_id in self.rects.keys():
                if self.rects[rect_id]['active']:
                    player_collision_rect = pygame.Rect(self.player.pos[0] - (self.player.img_width / 2) + self.player.move_vector[0],
                                                        self.player.pos[1] - 6, self.player.img_width, 6 + self.player.move_vector[1])

                    if player_collision_rect.colliderect(pygame.Rect(self.rects[rect_id]['rect'])) and self.rects[rect_id]['on_walk']:
                        # Enemy region counting
                        if 'region' in self.rects[rect_id]:
                            possible_regions.append(self.rects[rect_id]['region'])
                        
                        # Safezone & triggers for rects
                        if self.rects[rect_id]['trigger'] == '#sfz':
                            safezone = True
                        elif self.rects[rect_id]['trigger'] != None:
                            if ((self.triggers[self.rects[rect_id]['trigger']]['active_once'] and self.rects[rect_id]['trigger'] not in self.vars['maps'][self.id]) or
                                not self.triggers[self.rects[rect_id]['trigger']]['active_once']):
                                self.current_trigger = self.triggers[self.rects[rect_id]['trigger']]
                                self.current_step = 0
                                self.trigger_active = True
                                self.player.move_vector = [0, 0]

                                if self.rects[rect_id]['trigger'] not in self.vars['maps'][self.id]:
                                    self.vars['maps'][self.id].append(self.rects[rect_id]['trigger'])

                # Select region
                if len(possible_regions) > 0:
                    self.current_region = possible_regions[0]
                else:
                    self.current_region = None
            
        blit_time = time.time()

        pos = [-self.camera_pos[0], -self.dims[1] + self.camera_pos[1] + 328]
        if self.draw_mode == 'default':
            if 'default.py' in os.listdir('res/modes'):
                glob = globals()
                glob['fps'] = fps
                glob['SURF'] = SURF
                exec(compile(self.draw_mode, 'draw_function', 'exec'), glob, locals())
            else:
                try:
                    self.draw_mode = DefaultLevel(self)
                    self.draw_mode.animate(SURF, fps)
                except NameError:
                    self.draw_world(SURF, fps) # draw map to screen

                    if self.debug:
                        for sprite in self.sprites:
                            if sprite.collide_rect != None:
                                pygame.draw.rect(SURF, [196, 196, 196], sprite.collide_rect.move((sprite.pos[0] - (sprite.img_width / 2)) + pos[0], sprite.pos[1] + pos[1]), 1)

                            if 'interact_rect' in sprite.temp_variable.keys():
                                pygame.draw.rect(SURF, [255, 255, 0], sprite.temp_variable['interact_rect'].move((sprite.pos[0] - (sprite.img_width / 2)) + pos[0], sprite.pos[1] + pos[1]), 1)
                            
                            pygame.draw.circle(SURF, [255, 255, 255], [int(sprite.pos[0] + pos[0]), int(sprite.pos[1] + pos[1])], 3)
                            pygame.draw.line(SURF, [255, 128, 0], [int(sprite.pos[0] + pos[0]), int(sprite.pos[1] + pos[1])], [int(sprite.pos[0] + pos[0] + sprite.move_vector[0]), int(sprite.pos[1] + pos[1] + sprite.move_vector[1])])

                        if self.player != None:
                            player_collision_rect = pygame.Rect(self.player.pos[0] - (self.player.img_width / 2), self.player.pos[1] - 6, self.player.img_width, 6)
                            pygame.draw.rect(SURF, [255, 0, 0], player_collision_rect.move(pos[0], pos[1]), 1)
        else:
            glob = globals()
            glob['fps'] = fps
            glob['SURF'] = SURF

            if type(self.draw_mode) == str:
                if len(self.draw_mode.split('\n')) == 1:
                    if 'res/modes/' not in sys.path:
                        sys.path.append('res/modes')

                    try:
                        exec(compile('self.draw_mode = %s(self)' % self.draw_mode, 'draw_mode_set', 'exec'), glob,  locals())
                    except NameError:
                        self.draw_mode = DRAW_MODES[self.draw_mode](self)
                        
                    self.draw_mode.animate(SURF, fps) # If the draw mode is a Level class in modes.py
                else:
                    exec(compile(self.draw_mode, 'draw_function', 'exec'), glob, locals()) # If the draw mode is a function
            else:
                try: self.draw_mode.debug = self.debug
                except AttributeError: pass
                
                self.draw_mode.animate(SURF, fps) # If the draw mode is a Level class in modes.py

        if self.interacting:
            # Default interact action
            pass

        # Say/prompt box
        if self.say_box != None:
            pygame.draw.rect(SURF, [0, 0, 0], self.say_box)
            pygame.draw.rect(SURF, [255, 255, 255], self.say_box, 1)

            if type(self.temp_variable) == list and self.current_trigger[self.current_step]['type'] == 'prompt':
                if len(self.temp_variable) > 1 and self.say_state < 21:
                    f = pygame.font.Font('res/fonts/coderscrux.ttf', 16)

                    i = 0
                    x = 0
                    for option in self.temp_variable[1]:
                        if i == self.selected:
                            clr = [40, 122, 255]
                        else:
                            clr = [192, 192, 192]

                        SURF.blit(f.render(option, False, clr), [self.temp_variable[2] + x, self.temp_variable[3]])

                        x += f.size(option)[0] + 16
                        i += 1

            if self.current_trigger[self.current_step]['type'] == 'say' and self.say_state == 20:
                flag = True
                if 'milliseconds' in self.current_trigger[self.current_step].keys():
                    if self.current_trigger[self.current_step]['milliseconds'] > 0: flag = False

                if flag:
                    i = 0
                    if type(self.say_arrow) == list:
                        if time.time() - self.say_arrow[0] > 0.25:
                            self.say_arrow[0] = time.time()
                            self.say_arrow[1] = not self.say_arrow[1]
                        i = int(self.say_arrow[1])
                    pygame.draw.polygon(SURF, [255, 255,255], ([self.say_box[0] + self.say_box[2] - 12, self.say_box[1] + self.say_box[3] - 9 + i],
                                                               [self.say_box[0] + self.say_box[2] - 6, self.say_box[1] + self.say_box[3] - 9 + i],
                                                               [self.say_box[0] + self.say_box[2] - 9, self.say_box[1] + self.say_box[3] - 6 + i]))

        # Say image
        if self.say_image != None:
            SURF.blit(self.say_image, [self.say_box[0] + 2, self.say_box[1] + 2])

        if self.draw_mode == 'default':
            self.draw_menu(SURF) # Draws the menu
        self.draw_text(SURF)

        # Battle transition
        if self.battle_transition > -1:
            white_surf = pygame.Surface([640, 360])
            white_surf.fill([255,255,255])

            if self.battle_transition < 7:
                white_surf.set_alpha(int(255 * float(self.battle_transition / 7)))
            elif self.battle_transition < 14:
                white_surf.set_alpha(255 - int(255 * float((7 - self.battle_transition) / 7)))
            elif self.battle_transition < 21:
                white_surf.set_alpha(int(255 * float((14 - self.battle_transition) / 7)))

            SURF.blit(white_surf, [0, 0])

        if self.fade != 'set_name':
            screen.blit(pygame.transform.scale(SURF, [screen.get_rect().w, screen.get_rect().h]), [0, 0]) # Scale up
        
        # Fading in and out
        if self.fade == 'in':
            if self.black_surf.get_alpha() != 255:
                self.black_surf.set_alpha(255)
            self.fade = '_in'
        elif self.fade == '_in':
            if self.black_surf.get_alpha() > 0:
                self.black_surf.set_alpha(self.black_surf.get_alpha() - 10)
            else:
                self.fade = None
                self.current_step += 1

                flag = False
                if self.trigger_active:
                    try:
                        if self.current_trigger[self.current_step]['type'] == 'fromblack':
                            flag = True
                    except Exception: pass

                if flag:
                    self.current_step += 1
                    
        if self.fade == 'out':
            if self.black_surf.get_alpha() != 0:
                self.black_surf.set_alpha(0)
            self.fade = '_out'
        elif self.fade == '_out':
            if self.black_surf.get_alpha() < 255:
                self.black_surf.set_alpha(self.black_surf.get_alpha() + (5 * (60 / fps)))

                flag = False
                if self.trigger_active:
                    try:
                        if self.current_trigger[self.current_step]['type'] == 'toblack':
                            flag = True
                    except Exception: pass

            else:
                if self.quit:
                    self.stopped_flag = True
                    self.temp_variable = None
                    pygame.mixer.stop()
                else:
                    flag = False
                    if self.trigger_active:
                        try:
                            if self.current_trigger[self.current_step]['type'] == 'toblack':
                                flag = True
                        except Exception: pass

                    if flag:
                        self.current_step += 1
                    else:
                        try:
                            if self.goingtonewmap:
                                step = self.current_trigger[self.current_step]

                                prev_music = {'music': self.music[:], 'state': self.playback_state,
                                              'timer': self.music_timer, 'elapsed': self.music_elapsed,
                                              'music_names': self.music_names[:]}

                                if type(self.draw_mode) != str:
                                    self.draw_mode.alive = False

                                MapLevel.__init__(self, step['mapname'].split('|')[1], step['entranceid'],
                                                  prev_music, prev_vars = self.vars,
                                                  party = self.party, maps = self.loaded_maps, money = self.money, keys = self.keys)
                            elif not self.goingtonewmap:
                                self.fade = '_in'
                                self.player.pos = self.last_pos_stood[:]
                                self.player.move_vector = [0,0]
                                self.player.update()
                        except Exception:
                            if type(self.draw_mode) != str:
                                self.draw_mode.alive = True

        if self.fade != None:
            if self.draw_black_surf:
                screen.blit(self.black_surf, [0, 0])
        
        self.section_times.append(time.time() - blit_time)

        if self.debug: # Render debug information
            objcount = len(self.sprites)
            if self.player != None: objcount += 1
            screen.blit(self.debug_font.render("OBJ COUNT: %s" % str(objcount), True, [0, 0, 0]), [15, 75])
            screen.blit(self.debug_font.render("OBJ COUNT: %s" % str(objcount), True, [255, 255, 255]), [15, 72])

            y = 92
            for sprite in self.sprites:
                screen.blit(self.debug_font.render("%s, (%i, %i)" % (sprite.id, sprite.pos[0], sprite.pos[1]), True, [0, 0, 0]), [25, y+3])
                screen.blit(self.debug_font.render("%s, (%i, %i)" % (sprite.id, sprite.pos[0], sprite.pos[1]), True, [255, 255, 0]), [25, y])
                y += 20

            y += 20
            numtiles = len(filter(lambda t: pygame.Rect(t[1][0] + pos[0], self.dims[1] - t[1][1] -self.dims[1] + self.camera_pos[1] + 328, t[0].get_width(), t[0].get_height()).colliderect(pygame.Rect(0,0,SURF.get_width(),SURF.get_height())), self.tiles))
            screen.blit(self.debug_font.render("TILES: %i/%i" % (numtiles, len(self.tiles)), True, [0, 0, 0]), [15, y+3])
            screen.blit(self.debug_font.render("TILES: %i/%i" % (numtiles, len(self.tiles)), True, [0, 255, 0]), [15, y])

            y += 40
            screen.blit(self.debug_font.render("BATTLE_COUNTER: %i" % (self.battlecounter), True, [0, 0, 0]), [15, y + 3])
            screen.blit(self.debug_font.render("BATTLE_COUNTER: %i" % (self.battlecounter), True, [255, 128, 0]), [15, y])

    def keydown(self, key):
        if type(self.draw_mode) != str:
            self.draw_mode.keydown(key) # Key input for custom draw modes
            
        if self.trigger_active:
            if self.current_trigger != None:
                step = self.current_trigger[self.current_step]
                if step['type'] in ['say', 'prompt']:
                    try:
                        if key in self.keys['a'] and self.find_text('say trigger') != None:
                            if self.say_state == 20 and self.find_text('say trigger')['text'] != self.temp_variable[0]:
                                self.find_text('say trigger')['text'] = self.temp_variable[0]
                            elif self.say_state == 20:
                                flag = True
                                if 'milliseconds' in step.keys():
                                    if step['milliseconds'] > 0: flag = False

                                if flag:
                                    self.say_state = 21

                        if step['type'] == 'prompt' and self.say_state == 20 and self.find_text('say trigger')['text'] == self.temp_variable[0]:
                            if key in self.keys['left']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.selected -= 1
                                if self.selected < 0:
                                    self.selected = len(self.temp_variable[1]) - 1
                            if key in self.keys['right']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.selected += 1
                                if self.selected > len(self.temp_variable[1]) - 1:
                                    self.selected = 0
                    except TypeError:
                        pass
        else:
            if not self.interacting:
                if key in self.keys['b']:
                    if self.menu == None:
                        if not self.disable_menu:
                            if 'Scroll' in self.sounds.keys():
                                self.sounds['Scroll'].play()
                            self.menu = ""
                            self.selected = [0]
                    elif self.menu == "":
                        if 'Scroll' in self.sounds.keys():
                            self.sounds['Scroll'].play()
                        self.menu = None
                        self.selected = []
                    elif len(self.menu.split(',')) < 2:
                        if 'Scroll' in self.sounds.keys():
                            self.sounds['Scroll'].play()
                        self.menu = ''
                        self.selected = [self.selected[0]]
                    else:
                        if 'Scroll' in self.sounds.keys():
                            self.sounds['Scroll'].play()
                        self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                        self.selected = self.selected[0:len(self.selected) - 1]

            if self.menu != None: # Menu options
                menu_items = self.menu_items
                
                if self.menu == '': # Top menu
                    if key in self.keys['up']:
                        self.selected[0] -= 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[0] < 0:
                            self.selected[0] = len(menu_items) - 1
                    if key in self.keys['down']:
                        self.selected[0] += 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[0] > len(menu_items) - 1:
                            self.selected[0] = 0

                    if key in self.keys['a']:
                        flag = True
                        if menu_items[self.selected[0]] == 'Key Items':
                            if 'key_items' not in self.vars.keys():
                                flag = False
                            elif len(self.vars['key_items']) == 0:
                                flag = False

                        if flag:
                            if 'Scroll' in self.sounds.keys():
                                self.sounds['Scroll'].play()
                            self.menu = menu_items[self.selected[0]]
                            if self.menu == 'Quit':
                                self.menu = None
                                self.selected = []
                                self.fade = 'out'
                                self.quit = True
                            else:
                                self.selected.append(0)
                        else:
                            if 'Wrong' in self.sounds.keys():
                                self.sounds['Wrong'].play()
                elif self.menu == 'Key Items':
                    if key in self.keys['up']:
                        self.selected[1] -= 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] < 0:
                            self.selected[1] = len(self.vars['key_items']) - 1
                    if key in self.keys['down']:
                        self.selected[1] += 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] > len(self.vars['key_items']) - 1:
                            self.selected[1] = 0
                elif self.menu == 'Save':
                    if key in self.keys['left']:
                        self.selected[1] -= 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] < 0: self.selected[1] = 2
                    if key in self.keys['right']:
                        self.selected[1] += 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] > 2: self.selected[1] = 0
                    if key in self.keys['a']:
                        if 'Scroll' in self.sounds.keys():
                            self.sounds['Scroll'].play()
                        self.menu = None
                        self.current_trigger = {'id': 'save_progress', 'active_once': 0,
                                                0: {'type': 'save',
                                                    'savefile': '#str|save%i.sv' % (self.selected[1])},
                                                1: {'type': 'say',
                                                    'text': '#str|Game saved successfully!',
                                                    'rect': [0, 0, 0, 0],
                                                    'color': [255, 128, 0],
                                                    'image': '#img'}
                                                }
                        self.current_step = 0
                        self.trigger_active = True
                        
                        self.selected = None
                    
                elif self.menu in ['Inventory', 'Specials', 'Equipment', 'Status', 'Party', 'Augments']:
                    if key in self.keys['up']:
                        self.selected[1] -= 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] < 0:
                            self.selected[1] = len(self.party) - 1
                    if key in self.keys['down']:
                        self.selected[1] += 1
                        if 'Scroll2' in self.sounds.keys():
                            self.sounds['Scroll2'].play()
                        if self.selected[1] > len(self.party) - 1:
                            self.selected[1] = 0

                    if key in self.keys['a']:
                        if 'Scroll' in self.sounds.keys():
                            self.sounds['Scroll'].play()
                        self.menu = self.menu + ',' + str(self.selected[1])
                        self.selected.append(0)
                elif self.menu.split(',')[0] == 'Inventory':
                    if len(self.menu.split(',')) > 0:
                        items = 1
                        if len(self.party[self.selected[1]]['bag']) > 0:
                            items = len(self.party[self.selected[1]]['bag'])

                        if len(self.menu.split(',')) == 2:
                            if key in self.keys['up']:
                                self.selected[2] -= 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[2] < 0:
                                    self.selected[2] = items - 1
                            if key in self.keys['down']:
                                self.selected[2] += 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[2] > items - 1:
                                    self.selected[2] = 0
                            if key in self.keys['left'] and len(self.party[self.selected[1]]['bag']) > 0:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.menu = self.menu + ',' + "Move"
                                self.selected.append(0)
                            if key in self.keys['right'] and len(self.party[self.selected[1]]['bag']) > 0:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.menu = self.menu + ',' + "Sort"
                                self.selected.append(self.selected[2])
                            if key in self.keys['a'] and len(self.party[self.selected[1]]['bag']) > 0:
                                if self.party[self.selected[1]]['bag'][self.selected[2]]['consumable'] in [True, 'True', 'true', 't', 'yes', 'Yes', 'T', 'y', 'Y']:
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    self.menu = self.menu + ',Use'
                                    self.selected.append(0)
                                else:
                                    if 'Wrong' in self.sounds.keys():
                                        self.sounds['Wrong'].play()
                        elif len(self.menu.split(',')) == 3:
                            if self.menu.split(',')[2] != 'Sort':
                                if self.selected[3] < len(self.party):
                                    if key in self.keys['up']:
                                        self.selected[3] -= 1
                                        if 'Scroll2' in self.sounds.keys():
                                            self.sounds['Scroll2'].play()
                                        if self.selected[3] < 0:
                                            self.selected[3] = len(self.party) - 1
                                    if key in self.keys['down']:
                                        self.selected[3] += 1
                                        if 'Scroll2' in self.sounds.keys():
                                            self.sounds['Scroll2'].play()
                                        if self.selected[3] > len(self.party) - 1:
                                            self.selected[3] = 0
                            else:
                                if len(self.party[self.selected[1]]['bag']) > 1:
                                    if key in self.keys['up']:
                                        old_ind = int(float(self.selected[3]))
                                        
                                        self.selected[3] -= 1
                                        if 'Scroll2' in self.sounds.keys():
                                            self.sounds['Scroll2'].play()
                                        if self.selected[3] < 0:
                                            self.selected[3] = len(self.party[self.selected[1]]['bag']) - 1

                                        new_ind = int(float(self.selected[3]))
                                        self.party[self.selected[1]]['bag'][old_ind], self.party[self.selected[1]]['bag'][new_ind] = self.party[self.selected[1]]['bag'][new_ind], self.party[self.selected[1]]['bag'][old_ind]
                                        self.selected[2] = int(float(self.selected[3]))

                                    if key in self.keys['down']:
                                        old_ind = int(float(self.selected[3]))
                                        
                                        self.selected[3] += 1
                                        if 'Scroll2' in self.sounds.keys():
                                            self.sounds['Scroll2'].play()
                                        if self.selected[3] > len(self.party[self.selected[1]]['bag']) - 1:
                                            self.selected[3] = 0

                                        new_ind = int(float(self.selected[3]))
                                        self.party[self.selected[1]]['bag'][old_ind], self.party[self.selected[1]]['bag'][new_ind] = self.party[self.selected[1]]['bag'][new_ind], self.party[self.selected[1]]['bag'][old_ind]
                                        self.selected[2] = int(float(self.selected[3]))

                            if key in self.keys['left'] and self.menu.split(',')[2] == 'Use':
                                if self.selected[3] < len(self.party):
                                    if 'usable_on_everyone' in self.party[self.selected[1]]['bag'][self.selected[2]].keys():
                                        if self.party[self.selected[1]]['bag'][self.selected[2]]['usable_on_everyone'].lower() in ['y', 'yes', 't', 'true']:
                                            self.selected[3] = len(self.party)

                            if key in self.keys['right'] and self.menu.split(',')[2] == 'Use':
                                if self.selected[3] == len(self.party):
                                    if 'Scroll2' in self.sounds.keys():
                                        self.sounds['Scroll2'].play()
                                    self.selected[3] = 0
                                else:
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                    self.selected = self.selected[0:len(self.selected) - 1]
                            elif key in self.keys['right'] and self.menu.split(',')[2] == 'Move':
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                self.selected = self.selected[0:len(self.selected) - 1]
                            elif key in self.keys['left'] and self.menu.split(',')[2] == 'Sort':
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                self.selected = self.selected[0:len(self.selected) - 1]
                            elif key in self.keys['right'] and self.menu.split(',')[2] == 'Sort':
                                if 'Delete' in self.sounds.keys():
                                    self.sounds['Delete'].play()

                                item = self.party[self.selected[1]]['bag'].pop(self.selected[2])
                                if self.selected[2] > len(self.party[self.selected[1]]['bag']) - 1:
                                    self.selected[2] = 0

                                self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                self.selected = self.selected[0:len(self.selected) - 1]

                            if key in self.keys['a']: # Move item from one inventory to another
                                if self.menu.split(',')[2] == 'Move':
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    if self.selected[3] != self.selected[1]:
                                        item = self.party[self.selected[1]]['bag'].pop(self.selected[2])
                                        
                                        if self.selected[2] > len(self.party[self.selected[1]]['bag']) - 1:
                                            self.selected[2] = 0

                                        self.party[self.selected[3]]['bag'].append(item)
                                        self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                        self.selected = self.selected[0:len(self.selected) - 1]

                                elif self.menu.split(',')[2] == 'Sort':
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                    self.selected = self.selected[0:len(self.selected) - 1]
                                        
                                elif self.menu.split(',')[2] == 'Use':
                                    item_used = True
                                    if 'HP' in self.party[self.selected[1]]['bag'][self.selected[2]].keys():
                                        if self.party[self.selected[3]]['HP'][0] == self.party[self.selected[3]]['HP'][1] or self.party[self.selected[3]]['HP'][0] == 0:
                                            item_used = False
                                        else:
                                            item_used = True
                                            self.party[self.selected[3]]['HP'][0] += self.party[self.selected[1]]['bag'][self.selected[2]]['HP']
                                            if self.party[self.selected[3]]['HP'][0] > self.party[self.selected[3]]['HP'][1]:
                                                self.party[self.selected[3]]['HP'][0] = self.party[self.selected[3]]['HP'][1]

                                    if 'SP' in self.party[self.selected[1]]['bag'][self.selected[2]].keys():
                                        if self.party[self.selected[3]]['SP'][0] == self.party[self.selected[3]]['SP'][1] or self.party[self.selected[3]]['HP'][0] == 0:
                                            item_used = False
                                        else:
                                            item_used = True
                                            self.party[self.selected[3]]['SP'][0] += self.party[self.selected[1]]['bag'][self.selected[2]]['SP']
                                            if self.party[self.selected[3]]['SP'][0] > self.party[self.selected[3]]['SP'][1]:
                                                self.party[self.selected[3]]['SP'][0] = self.party[self.selected[3]]['SP'][1]

                                    if 'revive' in self.party[self.selected[1]]['bag'][self.selected[2]].keys():
                                        if self.party[self.selected[3]]['HP'][0] > 0:
                                            item_used = False
                                        else:
                                            item_used = True
                                            self.party[self.selected[3]]['HP'][0] = int(self.party[self.selected[3]]['HP'][1] * float(self.party[self.selected[1]]['bag'][self.selected[2]]['revive']))

                                    if item_used:
                                        pygame.mixer.Sound('res/sound/' + self.party[self.selected[1]]['bag'][self.selected[2]]['sound']).play()
                                        self.party[self.selected[1]]['bag'].pop(self.selected[2])
                                        
                                        self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                        self.selected = self.selected[0:len(self.selected) - 1]
                                        if self.selected[2] > len(self.party[self.selected[1]]['bag']) - 1:
                                            self.selected[2] = 0
                                    else:
                                        if 'Wrong' in self.sounds.keys():
                                            self.sounds['Wrong'].play()
                            
                elif self.menu.split(',')[0] == 'Specials':
                    if len(self.menu.split(',')) > 0:
                        items = 1
                        if len(self.party[self.selected[1]]['specials']) > 0:
                            items = len(self.party[self.selected[1]]['specials'])

                        if len(self.menu.split(',')) == 2:
                            if key in self.keys['up']:
                                self.selected[2] -= 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[2] < 0:
                                    self.selected[2] = items - 1
                            if key in self.keys['down']:
                                self.selected[2] += 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[2] > items - 1:
                                    self.selected[2] = 0

                elif self.menu.split(',')[0] == 'Augments':
                    if len(self.menu.split(',')) > 0:
                        if len(self.menu.split(',')) == 2:
                            if key in self.keys['left']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.party[self.selected[1]]['augments'][self.selected[2]] != None:
                                    self.selected[2] -= 1
                                elif self.selected[2] % 2 == 1:
                                    self.selected[2] -= 1
                                else:
                                    self.selected[2] -= 2

                                if self.selected[2] < 0:
                                    self.selected[2] = len(self.party[self.selected[1]]['augments']) - 1
                                    if len(self.party[self.selected[1]]['augments']) % 2 == 0:
                                        self.selected[2] -= 1

                            if key in self.keys['right']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.party[self.selected[1]]['augments'][self.selected[2]] != None:
                                    self.selected[2] += 1
                                elif self.selected[2] % 2 == 1:
                                    self.selected[2] += 1
                                else:
                                    self.selected[2] += 2

                                if self.selected[2] > len(self.party[self.selected[1]]['augments']) - 1:
                                    self.selected[2] = 0

                            if key in self.keys['up'] and self.party[self.selected[1]]['augments'][self.selected[2]] != None:
                                if 'Delete' in self.sounds.keys():
                                    self.sounds['Delete'].play()
                                self.vars['key_items'].append(self.party[self.selected[1]]['augments'][self.selected[2]])
                                self.party[self.selected[1]]['augments'][:] = [None if x==self.party[self.selected[1]]['augments'][self.selected[2]] else x for x in self.party[self.selected[1]]['augments']]

                            if key in self.keys['a']:
                                flag = False
                                
                                if 'key_items' in self.vars.keys():
                                    if len(self.vars['key_items']) > 0:
                                        flag = True

                                if flag:
                                    if 'Scroll2' in self.sounds.keys():
                                        self.sounds['Scroll2'].play()
                                    self.selected.append(0)
                                    self.menu = self.menu + ',KeyItem'
                                else:
                                    if 'Wrong' in self.sounds.keys():
                                        self.sounds['Wrong'].play()

                        if len(self.menu.split(',')) == 3:
                            if key in self.keys['up']:
                                self.selected[3] -= 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[3] < 0:
                                    self.selected[3] = len(self.vars['key_items']) - 1
                            if key in self.keys['down']:
                                self.selected[3] += 1
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                if self.selected[3] > len(self.vars['key_items']) - 1:
                                    self.selected[3] = 0
                            if key in self.keys['a']:
                                if 'key_items' in self.vars.keys():
                                    if len(self.vars['key_items']) > 0:
                                        flag = True

                                if flag:
                                    pass 
                                else:
                                    self.sounds['Wrong'].play()
                                    
                elif self.menu.split(',')[0] == 'Equipment':
                    if len(self.menu.split(',')) > 0:
                        if len(self.menu.split(',')) == 2:
                            if key in self.keys['up']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[2] -= 1
                                if self.selected[2] < 0:
                                    self.selected[2] = 3
                            if key in self.keys['down']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[2] += 1
                                if self.selected[2] > 3:
                                    self.selected[2] = 0
                            if key in self.keys['a']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.selected.append(0)
                                self.menu = self.menu + ',Inv'
                            if key in self.keys['left']:
                                if self.party[self.selected[1]]['equipment'][self.selected[2]] != None:
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    self.selected.append(0)
                                    self.menu = self.menu + ',Del'
                        elif len(self.menu.split(',')) == 3:
                            if key in self.keys['up']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[3] -= 1
                                if self.selected[3] < 0:
                                    self.selected[3] = len(self.party) - 1
                            if key in self.keys['down']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[3] += 1
                                if self.selected[3] > len(self.party) - 1:
                                    self.selected[3] = 0

                            if self.menu.split(',')[-1] == "Inv":
                                if key in self.keys['a']:
                                    if len(self.party[self.selected[3]]['bag']) > 0:
                                        if 'Scroll' in self.sounds.keys():
                                            self.sounds['Scroll'].play()
                                        self.selected.append(0)
                                        self.menu = self.menu + ',Item'
                                    else:
                                        self.sounds['Wrong'].play()
                            elif self.menu.split(',')[-1] == "Del":
                                if key in self.keys['right']:
                                    if 'Scroll' in self.sounds.keys():
                                        self.sounds['Scroll'].play()
                                    self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                    self.selected = self.selected[0:len(self.selected) - 1]

                                if key in self.keys['a']:
                                    if len(self.party[self.selected[3]]['bag']) < self.party[self.selected[3]]['bag_size']:
                                        item = self.party[self.selected[1]]['equipment'][self.selected[2]]
                                        self.party[self.selected[1]]['equipment'][self.selected[2]] = None
                                        self.party[self.selected[3]]['bag'].append(item)
                                        if 'Scroll' in self.sounds.keys():
                                            self.sounds['Scroll'].play()
                                        self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                        self.selected = self.selected[0:len(self.selected) - 1]
                                    else:
                                        if 'Wrong' in self.sounds.keys():
                                            self.sounds['Wrong'].play()
                                    
                        elif len(self.menu.split(',')) == 4:
                            if key in self.keys['up']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[4] -= 1
                                if self.selected[4] < 0:
                                    self.selected[4] = len(self.party[self.selected[3]]['bag']) - 1
                            if key in self.keys['down']:
                                if 'Scroll2' in self.sounds.keys():
                                    self.sounds['Scroll2'].play()
                                self.selected[4] += 1
                                if self.selected[4] > len(self.party[self.selected[3]]['bag']) - 1:
                                    self.selected[4] = 0
                            if key in self.keys['a']:
                                valid = False
                                if bool(self.party[self.selected[3]]['bag'][self.selected[4]]['equipable']):
                                    item = self.party[self.selected[3]]['bag'][self.selected[4]]
                                    if 'slot' in item.keys():
                                        if self.selected[2] in self.party[self.selected[3]]['bag'][self.selected[4]]['slot']:
                                            valid = True

                                    if 'equipped_by' in item.keys():
                                        valid = (self.party[self.selected[1]]['id'] in item['equipped_by'] or self.party[self.selected[1]]['name'] in item['equipped_by']) and valid

                                    if 'valid_alignments' in item.keys():
                                        valid = '<%i,%i>' % (self.party[self.selected[1]]['alignment'][0], self.party[self.selected[1]]['alignment'][1]) in item['valid_alignments'] and valid

                                if valid: # Equip item if the player can use it
                                    self.sounds['Scroll'].play()
                                    item = self.party[self.selected[3]]['bag'].pop(self.selected[4])
                                    self.party[self.selected[1]]['equipment'][self.selected[2]] = item

                                    self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                    self.selected = self.selected[0:len(self.selected) - 1]
                                    self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                    self.selected = self.selected[0:len(self.selected) - 1]
                                else:
                                    if 'Wrong' in self.sounds.keys():
                                        self.sounds['Wrong'].play()

                elif self.menu.split(',')[0] == 'Party':
                    if len(self.menu.split(',')) > 0:
                        if len(self.menu.split(',')) == 2:
                            self.selected[2] = self.selected[1]
                            
                            if key in self.keys['up']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.selected[2] -= 1
                                if self.selected[2] < 0:
                                    self.selected[2] = len(self.party) - 1

                                self.party[self.selected[1]], self.party[self.selected[2]] = self.party[self.selected[2]], self.party[self.selected[1]]
                                self.selected[1] = int(float(self.selected[2]))

                                for i in range(len(self.party)):
                                    if 'custom_name' in self.party[i].keys():
                                        self.find_text('character' + str(i))['text'] = self.party[i]['custom_name']
                                    else:
                                        self.find_text('character' + str(i))['text'] = self.party[i]['name']
                            if key in self.keys['down']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()
                                self.selected[2] += 1
                                if self.selected[2] > len(self.party) - 1:
                                    self.selected[2] = 0

                                self.party[self.selected[1]], self.party[self.selected[2]] = self.party[self.selected[2]], self.party[self.selected[1]]
                                self.selected[1] = int(float(self.selected[2]))

                                for i in range(len(self.party)):
                                    if 'custom_name' in self.party[i].keys():
                                        self.find_text('character' + str(i))['text'] = self.party[i]['custom_name']
                                    else:
                                        self.find_text('character' + str(i))['text'] = self.party[i]['name']
                            if key in self.keys['a']:
                                if 'Scroll' in self.sounds.keys():
                                    self.sounds['Scroll'].play()

                                self.menu = ','.join(self.menu.split(',')[0:len(self.menu.split(',')) - 1])
                                self.selected = self.selected[0:len(self.selected) - 1]
