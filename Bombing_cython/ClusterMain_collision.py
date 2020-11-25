
try:
    from constants import CONSTANTS
except ImportError:
    raise ImportError("\n<constants> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")


try:
    from matplotlib import pyplot as plt
except ImportError:
    raise ImportError("\n<matplotlib> library is missing on your system."
          "\nTry: \n   C:\\pip install matplotlib on a window command prompt.")


try:
    import pygame
    from pygame.event import pump, get
    from pygame.image import tostring
    from pygame.key import get_pressed
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL, BLEND_RGB_MAX, BLEND_RGB_MULT
    from pygame import Surface, SRCALPHA, mask, event
    from pygame.transform import rotate, scale, smoothscale

except ImportError as e:
    print(e)
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

GL            = CONSTANTS()
pygame.display.init()
SCREEN        = pygame.display.set_mode(GL.SCREENRECT.size)
GL.screen     = SCREEN

try:
    from SoundServer import SoundControl
except ImportError:
    raise ImportError("\n<SoundServer> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from Sounds import *
except ImportError:
    raise ImportError("\n<Sounds> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from Textures import *
except ImportError:
    raise ImportError("\n<Textures> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from Player import Player
except ImportError:
    raise ImportError("\n<Player> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from ClusterBomb import XBomb, show_debris, damped_oscillation
except ImportError:
    raise ImportError("\n<ClusterBomb> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")

try:
   from Sprites import Sprite, LayeredUpdatesModified
   from Sprites import Group, collide_mask, collide_rect, \
       LayeredUpdates, spritecollideany, collide_rect_ratio
except ImportError:
    raise ImportError("\n<Sprites> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")

try:
    from numpy import array, fromstring, uint8
except ImportError:
    raise ImportError("\n<numpy> library is missing on your system."
                      "\nTry: \n   C:\\pip install numpy on a window command prompt.")


if __name__ == '__main__':

    pygame.init()
    # PYGAME >= 2.0
    # VERSION 2.0 MIXER INDUCE A CLACK WHEN THE SOUND IS PLAY (GAIN TO HIGH WHEN PLAYED AND STOPPED)
    if int(pygame.version.ver[0]) >= 2:
        pygame.mixer.init(frequency=24800, size=-16, channels=2, buffer=2048, allowedchanges=0)
    # ANY OTHER PYGAME VERSION
    else:
        pygame.mixer.init(frequency=24800, size=-16, channels=2, buffer=2048)

    # from SpriteSheet import sprite_sheet_fs8, sprite_sheet_fs8_numpy
    # print(timeit.timeit("sprite_sheet_fs8_numpy('Assets\\Explosion8_256x256_.png',  256, 6, 6)",
    #                     "from __main__ import sprite_sheet_fs8_numpy", number=10))
    # print(timeit.timeit("sprite_sheet_fs8('Assets\\Explosion8_256x256_.png',  256, 6, 6)",
    #                     "from __main__ import sprite_sheet_fs8", number=10))

    clock = pygame.time.Clock()
    GL.TIME_PASSED_SECONDS = clock.tick(GL.MAX_FPS)

    All = LayeredUpdatesModified()
    GL.All = All

    # SPACE BACKGROUND
    bck1 = Sprite()
    bck1.image = BACKGROUND1
    bck1.rect = BACKGROUND1.get_rect(topleft=(0, 0))
    # No mask
    bck1._layer = -9
    # bck1._blend = 0
    GL.All.add(bck1)

    # ASTEROID
    bck = Sprite()
    bck.image = BACKGROUND
    bck.rect  = BACKGROUND.get_rect(topleft=(0, 0))
    # GET THE ASTEROID MASK
    bck.mask  = mask.from_surface(bck.image)
    bck._layer = -8
    # bck._blend = 0
    GL.All.add(bck)

    BOMB_CONTAINER      = Group()
    GL.BOMB_CONTAINER   = BOMB_CONTAINER
    DEBRIS_CONTAINER    = Group()
    GL.DEBRIS_CONTAINER = DEBRIS_CONTAINER

    GL.PLAYER_GROUP = Group()
    GL.GROUP_UNION  = Group()
    GL.enemy_group  = Group()
    GL.SC_spaceship = SoundControl(GL.SCREENRECT, 60)
    GL.SC_explosion = SoundControl(GL.SCREENRECT, 60)
    GL.SOUND_LEVEL  = 1.0

    GL.player = Player([GL.All, GL.PLAYER_GROUP], COBRA,
                       pos_x=GL.SCREENRECT.centerx, pos_y=GL.SCREENRECT.centery,
                       gl_=GL, timing_=0, layer_=0, _blend=0)

    STOP_GAME = False
    QUIT = False
    GL.PAUSE = False
    em = Group()
    hm = Group()

    RECORDING = False  # allow RECORDING video
    VIDEO = []         # Capture frames
    FPS_AVG = []
    CONSTANT_AVG = []
    DT = 0

    # TWEAKS
    gl_all_draw      = GL.All.draw
    gl_all_update    = GL.All.update
    py_display_flip  = pygame.display.flip
    py_mouse_get_pos = pygame.mouse.get_pos
    gl_sc_spaceship_update = GL.SC_spaceship.update
    gl_sc_explosion_update = GL.SC_explosion.update
    clock_tick = clock.tick_busy_loop
    clock_get_fps = clock.get_fps

    while not STOP_GAME:

        # TODO ONLY ON FULLSCREEN
        # SCREEN.fill((0, 0, 0, 0))

        pump()

        keys = get_pressed()

        for event in get():

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = py_mouse_get_pos()
                ...

        # if any(keys):

        if keys[pygame.K_ESCAPE]:
            STOP_GAME = True

        # TODO MOVE THE PLAYER FROM CLASS PLAYER INSTEAD
        if keys[pygame.K_RIGHT]:
            GL.player.rect.centerx += 6

        if keys[pygame.K_LEFT]:
            GL.player.rect.centerx -= 6

        if keys[pygame.K_UP]:
            GL.player.rect.centery -= 6

        if keys[pygame.K_DOWN]:
            GL.player.rect.centery += 6

        if keys[pygame.K_F8]:
            pygame.image.save(SCREEN, 'Screendump' + str(GL.FRAME) + '.png')

        # TODO MOVE BELOW TO CLASS PLAYER
        if keys[pygame.K_SPACE]:
            if len(BOMB_CONTAINER) == 0:
                if not GL.SC_spaceship.get_identical_sounds(BOMB_RELEASE):
                    GL.SC_spaceship.play(sound_=BOMB_RELEASE, loop_=False, priority_=2,
                                         volume_=1, fade_out_ms=0, panning_=False,
                                         name_='BOMB_RELEASE', x_=0)
                x = GL.player.rect.centerx
                y = GL.player.rect.centery
                # TODO ENCODE 40 (GLOBAL VAR?)
                for r in range(30):
                    XBomb(gl_=GL, surface_=BOMB_ROTATE_BUFFER, layer_=-4, timing_=60.0)

        if keys[pygame.K_PAUSE]:
            GL.PAUSE = True

        gl_all_update()

        # if len(BOMB_CONTAINER) > 0:
        #     display_bombing(gl_=GL, screen=SCREEN)

        if len(DEBRIS_CONTAINER) > 0:
            show_debris(GL)

        gl_all_draw(SCREEN)

        if GL.SHOCK_WAVE:
            # shake the screen
            SCREEN.blit(SCREEN, (int(damped_oscillation(GL.SHOCK_WAVE_RANGE[GL.SHOCK_WAVE_INDEX]) * 10), 0))
            GL.SHOCK_WAVE_INDEX += 1
            if GL.SHOCK_WAVE_INDEX > GL.SHOCK_WAVE_LEN:
                GL.SHOCK_WAVE = False
                GL.SHOCK_WAVE_INDEX = 0

        # Cap the speed at 60 FPS
        GL.TIME_PASSED_SECONDS = clock_tick(GL.MAX_FPS)

        py_display_flip()

        if RECORDING:
            if GL.MAX_FPS > 60:
                if DT >= 1000/60:
                    VIDEO.append(tostring(SCREEN, 'RGB', False))
                    DT = 0
            else:
                VIDEO.append(tostring(SCREEN, 'RGB', False))

        gl_sc_spaceship_update()
        gl_sc_explosion_update()

        # print(clock_get_fps(), GL.FRAME)
        if clock.get_fps() != 0:
            FPS_AVG.append(clock.get_fps())
            if len(FPS_AVG)!= 0:
                avg = sum(FPS_AVG)/len(FPS_AVG)
            CONSTANT_AVG.append(avg)

        GL.FRAME += 1

        DT += GL.TIME_PASSED_SECONDS

    # *** Record the video
    if RECORDING:
        print(GL.SCREENRECT.w, GL.SCREENRECT.h)
        import cv2
        from cv2 import COLOR_RGBA2BGR
        import numpy

        video = cv2.VideoWriter('Bombing_cython.avi',
                                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 60,
                                (GL.SCREENRECT.w, GL.SCREENRECT.h), True)

        for event in pygame.event.get():
            pygame.event.clear()

        for image in VIDEO:
            image = fromstring(image, uint8).reshape(GL.SCREENRECT.h, GL.SCREENRECT.w, 3)
            image = cv2.cvtColor(image, COLOR_RGBA2BGR)
            video.write(image)

        cv2.destroyAllWindows()
        video.release()

    plt.plot(FPS_AVG)
    plt.plot(CONSTANT_AVG)
    AVG = []
    avg = sum(FPS_AVG)/len(FPS_AVG)
    for r in range(len(FPS_AVG)):
        AVG.append(avg)

    plt.plot(AVG)
    plt.title("FPS AVG")
    plt.draw()
    plt.show()

    pygame.quit()

