import sys, os
BUILD_VERSION = '0.0.1'

# Command line arguments
if len(sys.argv) > 1:
    args = sys.argv[1:]

# Import everything else
import pygame, sys, time, traceback
from screeninfo import get_monitors
from level import *
from intro_level import IntroLevel
from smap import load_map

pygame.init()
pygame.mixer.pre_init(22050, -16, 1, 2048)
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
FULLSCREEN = False
KEYS = {'fullscreen': pygame.K_F11}

# INITIALIZE THE SCREEN
if FULLSCREEN:
    m = get_monitors()[0]
    screen = pygame.display.set_mode([m.width, m.height], pygame.FULLSCREEN|pygame.HWACCEL|pygame.DOUBLEBUF)
else:
    screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)
pygame.display.init()
pygame.display.set_caption("Nothing & the Black Moon")

# EVENT LOOP
running = True
level = IntroLevel()

FPS = 60
ELAPSED = time.time()

# Error catching
EXC = None

while running:
    if EXC == None:
        try:
            screen.fill([0, 0, 0])

            game_screen = pygame.Surface([640, 360])
            if level != None:
                # Blit game to screen
                level.animate(game_screen, FPS)
                
                # Scale the screen to fit resolution
                ## figure out resolution first
                if screen.get_width() / 16.0 <= screen.get_height() / 9.0: # taller than wide; preserve width
                    c = screen.get_width() / float(game_screen.get_width())
                else: # wider than tall; preserve height
                    c = screen.get_height() / float(game_screen.get_height())
                game_screen = pygame.transform.scale(game_screen, [int(game_screen.get_width()*c), int(game_screen.get_height()*c)])
                screen.blit(game_screen, [(screen.get_width()  / 2) - (game_screen.get_width()  / 2),
                                          (screen.get_height() / 2) - (game_screen.get_height() / 2)])
            try:
                FPS = 1 / (time.time() - ELAPSED)
            except ZeroDivisionError: pass
            ELAPSED = time.time()
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if level != None:
                        level.keydown(event.key, event.unicode)
                    if event.key == KEYS['fullscreen']:
                        FULLSCREEN = not FULLSCREEN

                        if FULLSCREEN:
                            m = get_monitors()[0]
                            screen = pygame.display.set_mode([m.width, m.height], pygame.FULLSCREEN|pygame.HWACCEL|pygame.DOUBLEBUF)
                        else:
                            screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)
                if event.type == pygame.KEYUP:
                    if level != None:
                        level.keyup(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if level != None:
                        level.mousebuttondown(event.pos)
                if event.type == pygame.MOUSEBUTTONUP:
                    if level != None:
                        level.mousebuttonup(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    if level != None:
                        level.mousemotion(event.pos, event.rel, event.buttons)
                if event.type == pygame.JOYBUTTONDOWN:
                    if level != None:
                        level.joybuttondown(event.joy, event.button)
                if event.type == pygame.JOYBUTTONUP:
                    if level != None:
                        level.joybuttonup(event.joy, event.button)
                if event.type == pygame.JOYAXISMOTION:
                    if level != None:
                        level.joyaxismotion(event.joy, event.axis, event.value)
                if event.type == pygame.JOYBALLMOTION:
                    if level != None:
                        level.joyballmotion(event.joy, event.ball, event.rel)
                if event.type == pygame.JOYHATMOTION:
                    if level != None:
                        level.joyhatmotion(event.joy, event.hat, event.value)
                if event.type == pygame.VIDEORESIZE:
                    if not FULLSCREEN:
                        WIDTH, HEIGHT = event.w, event.h
                        screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            EXC = e
            level = Level("Error Handler")

            level.add_text({'id': "Error Title",
                            'font': 'res/fonts/consolas.ttf',
                            'text': "%s has crashed" % (pygame.display.get_caption()[0]),
                            'size': 42,
                            'color': [0, 0, 0],
                            'alignment': [0.5, 0.5],
                            'position': [WIDTH / 2, 35],
                            'vars': {'screen': screen},
                            'update':  "self['position'][0] = screen.get_rect().w / 2"})
            level.add_text({'id': "Error",
                            'font': 'res/fonts/consolas.ttf',
                            'text': type(EXC).__name__ + ": " + str(EXC),
                            'size': 18,
                            'color': [0, 0, 0],
                            'alignment': [0.5, 0],
                            'position': [WIDTH / 2, 80],
                            'char_wrap': 85,
                            'vars': {'screen': screen},
                            'update': "self['position'][0] = screen.get_rect().w / 2"})
            level.add_text({'id': "Build",
                            'font': 'res/fonts/consolas.ttf',
                            'text': "Version %s" % BUILD_VERSION,
                            'size': 18,
                            'color': [0, 0, 0],
                            'alignment': [0.5, 0],
                            'position': [WIDTH / 2, 58],
                            'char_wrap': 85,
                            'vars': {'screen': screen},
                            'update': "self['position'][0] = screen.get_rect().w / 2"})

            tb = traceback.format_exc()
            y = 120
            i = 0
            for line in tb.split('\n'):
                level.add_text({'id': "ErrorTracebackShadow" + str(i),
                                'font': 'res/fonts/consolas.ttf',
                                'text': line,
                                'size': 14,
                                'color': [0, 0, 0],
                                'alignment': [0, 0],
                                'position': [WIDTH / 8 + 1, y + 1]})
                level.add_text({'id': "ErrorTraceback" + str(i),
                                'font': 'res/fonts/consolas.ttf',
                                'text': line,
                                'size': 14,
                                'color': [255, 0, 0],
                                'alignment': [0, 0],
                                'position': [WIDTH / 8, y]})
                y += 16
                i += 1

            level.add_text({'id': "ErrorReporter1",
                            'font': 'res/fonts/consolas.ttf',
                            'text': "Take a screenshot of this error, then send it in for us to debug. Thank you!",
                            'size': 18,
                            'color': [225, 225, 225],
                            'alignment': [0.5, 0.5],
                            'position': [WIDTH / 2, HEIGHT - 60]})
            level.add_text({'id': "ErrorReporter2",
                            'font': 'res/fonts/consolas.ttf',
                            'text': "~ Republic of Simon, NBM Team",
                            'size': 18,
                            'color': [225, 225, 225],
                            'alignment': [0.5, 0.5],
                            'position': [WIDTH / 2 + 200, HEIGHT - 40]})
    else:
        pygame.display.flip()
        screen.fill([128,128,128])
        pygame.draw.rect(screen, [0, 0, 0], [0, HEIGHT - 100, WIDTH, 100])
        level.animate(screen, False)

        level.find_text("ErrorReporter1")['position'] = [WIDTH / 2, HEIGHT - 60]
        level.find_text("ErrorReporter2")['position'] = [WIDTH / 2 + 200, HEIGHT - 40]

        i = 0
        y = 120
        while True:
            if level.find_text("ErrorTraceback" + str(i)) != None:
                level.find_text("ErrorTracebackShadow" + str(i))['position'] = [WIDTH / 8 + 1, y + 1]
                level.find_text("ErrorTraceback" + str(i))['position'] = [WIDTH / 8, y]
                i += 1
                y += 16
            else:
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.VIDEORESIZE:
                if not FULLSCREEN:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key == KEYS['fullscreen']:
                    FULLSCREEN = not FULLSCREEN

                    if FULLSCREEN:
                        m = get_monitors()[0]
                        screen = pygame.display.set_mode([m.width, m.height], pygame.FULLSCREEN|pygame.HWACCEL|pygame.DOUBLEBUF)
                    else:
                        screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.RESIZABLE)

# CLOSE GAME
pygame.quit()
sys.exit()
