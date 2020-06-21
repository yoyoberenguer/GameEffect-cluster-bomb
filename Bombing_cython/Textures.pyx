###cython: boundscheck=False, wraparound=False, nonecheck=False, optimize.use_switch=True

from numpy import array, asarray
from constants import CONSTANTS

cdef extern from 'vector.c':

    float randRangeFloat(float lower, float upper)  nogil;
    int randRange(int lower, int upper)             nogil;

try:
    import pygame
    from pygame import Rect
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL
    from pygame import Surface, SRCALPHA, mask, RLEACCEL
    from pygame.transform import rotate, scale, smoothscale, rotozoom
    from pygame.surfarray import array3d, pixels3d, array_alpha, pixels_alpha

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

from Surface_tools import reshape, make_transparent
from random import randint

# *** BOMB SPRITE
from SpriteSheet import sprite_sheet_fs8

BOMB = pygame.image.load('Assets\\MISSILE3.png').convert_alpha()
cdef:
    int w = BOMB.get_width()
    int h = BOMB.get_height()

BOMB = smoothscale(BOMB, (<int>(w / 30.0), <int>(h / 30.0)))
BOMB_ROTATE_BUFFER = {}
for a in range(360):
    BOMB_ROTATE_BUFFER[a] = rotozoom(BOMB, a - 90, 1.0)


# *** EXPLOSIONS SPRITES
cdef list EXPLOSION1 = sprite_sheet_fs8('Assets\\Explosion8_256x256_.png',  256, 6, 6)
cdef list EXPLOSION2 = sprite_sheet_fs8('Assets\\Explosion9_256x256_.png',  256, 6, 8)
cdef list EXPLOSION3 = sprite_sheet_fs8('Assets\\Explosion10_256x256_.png', 256, 6, 7)
cdef list EXPLOSION4 = sprite_sheet_fs8('Assets\\Explosion11_256x256_.png', 256, 6, 7)
cdef list EXPLOSION5 = sprite_sheet_fs8('Assets\\Explosion12_256x256_.png', 256, 6, 7)
cdef list EXPLOSION6 = sprite_sheet_fs8('Assets\\Explosion12_256x256_.png', 256, 6, 7)
EXPLOSION6 = reshape(EXPLOSION6, (256, 256))
cdef int rnd
rnd = randint(128, 256)
EXPLOSION1 = reshape(EXPLOSION1, (rnd, rnd))
rnd = randint(128, 300)
EXPLOSION2 = reshape(EXPLOSION2, (rnd, rnd))
rnd = randint(128, 256)
EXPLOSION3 = reshape(EXPLOSION3, (rnd, rnd))
rnd = randint(128, 300)
EXPLOSION4 = reshape(EXPLOSION4, (rnd, rnd))
rnd = randint(128, 256)
EXPLOSION5 = reshape(EXPLOSION5, (rnd, rnd))
EXPLOSIONS = [EXPLOSION1, EXPLOSION2, EXPLOSION3, EXPLOSION4, EXPLOSION5]

# *** CRATERS (WITH MAGMA AND COLD)
CRATER_COLD = pygame.image.load('Assets\\Crater3_.png').convert(32, RLEACCEL)
CRATER_COLD = smoothscale(CRATER_COLD, (32, 32))

CRATER      = pygame.image.load('Assets\\Crater2_.png')
CRATER      = smoothscale(CRATER, (32, 32)).convert_alpha()
CRATER_MASK = pygame.mask.from_surface(CRATER)

SMOKE       = sprite_sheet_fs8('Assets\\Laval1_256_6x6_.png', 256, 6, 6)
SMOKE       = reshape(SMOKE, (32, 32))

# *** BACKGROUND ASTEROID
BACKGROUND = pygame.image.load('Assets\\A0.png').convert_alpha()
# BACKGROUND.set_colorkey((0, 0, 0, 0))

# **** BACKGROUND MARS
# BACKGROUND1 = pygame.image.load('Assets\\a2.png').convert(32, pygame.RLEACCEL)

# **** BACKGROUND SPACE
BACKGROUND1 = pygame.image.load('Assets\\nightsky.jpg').convert(32, pygame.RLEACCEL)
gl = CONSTANTS()
BACKGROUND1 = smoothscale(BACKGROUND1, gl.SCREENRECT.size)


# *** DEBRIS SPRITES
cdef list G5V200_DEBRIS = [
    pygame.image.load('Assets\\Boss7Debris_\\Boss7Debris1.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\Boss7Debris2.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\Boss7Debris3.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\Boss7Debris4.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\Boss7Debris5.png').convert(32, pygame.RLEACCEL)
]

cdef list G5V200_DEBRIS_HOT = [
    pygame.image.load('Assets\\Boss7Debris_\\debris1.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\debris2.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\debris3.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\debris4.png').convert(32, pygame.RLEACCEL),
    pygame.image.load('Assets\\Boss7Debris_\\debris5.png').convert(32, pygame.RLEACCEL)
]
G5V200_DEBRIS     = reshape(G5V200_DEBRIS, factor_=(64, 64))
G5V200_DEBRIS_HOT = reshape(G5V200_DEBRIS_HOT, factor_=(64, 64))
EXPLOSION_DEBRIS  = [*G5V200_DEBRIS_HOT, *G5V200_DEBRIS]

COBRA                  = pygame.image.load('Assets\\SpaceShip.png').convert_alpha()


# *** HALO SPRITES
cdef double [::1] steps = array([0., 0.03333333, 0.06666667, 0.1, 0.13333333,
                                   0.16666667, 0.2, 0.23333333, 0.26666667, 0.3,
                                   0.33333333, 0.36666667, 0.4, 0.43333333, 0.46666667,
                                   0.5, 0.53333333, 0.56666667, 0.6, 0.63333333,
                                   0.66666667, 0.7, 0.73333333, 0.76666667, 0.8,
                                   0.83333333, 0.86666667, 0.9, 0.93333333, 0.96666667]) * 255.0

image = smoothscale(pygame.image.load('Assets\\Halo11.png').convert_alpha(), (32, 32))

cdef:
    int n = 30
    unsigned char [:, :, :] rgb
    unsigned char [:, :] alpha
    int i
    float c1 = 0;

HALO_SPRITE11 = [image] * n
w = image.get_width()
h = image.get_height()

i = 0
for image in HALO_SPRITE11:
    image = make_transparent(image, <int>steps[i])
    c1 = 1.0 + (<float>i / 10.0)
    HALO_SPRITE11[i] = smoothscale(image, (<int>(w * c1), <int>(h * c1))).convert_alpha()
    i += 1

HALO_SPRITE13 = [smoothscale(pygame.image.load('Assets\\Halo13.png').convert_alpha(), (32, 32))] * 30
i = 0
for image in HALO_SPRITE13:
    image = make_transparent(image, <int>steps[i])
    c1 = 1.0 + (<float>i / 10.0)
    surface1 = smoothscale(image, (<int>(w * c1), <int>(h * c1)))
    HALO_SPRITE13[i] = surface1.convert_alpha()
    i += 1

#
# image = smoothscale(pygame.image.load('Assets\\Halo11_.png').convert(32, RLEACCEL), (32, 32))
# cdef:
#     int n = 30
#     unsigned char [:, :, :] rgb
#     unsigned char [:, :] alpha
#     int i
#     float c1 = 0;
#
# HALO_SPRITE11 = [image] * n
# w = image.get_width()
# h = image.get_height()
#
# i = 0
# for image in HALO_SPRITE11:
#     # image = make_transparent(image, <int>steps[i])
#     c1 = 1.0 + (<float>i / 5.0)
#     HALO_SPRITE11[i] = smoothscale(image, (<int>(w * c1), <int>(h * c1))).convert(32, RLEACCEL)
#     i += 1
#
# HALO_SPRITE13 = [smoothscale(pygame.image.load('Assets\\Halo13_.png').convert(32, RLEACCEL), (32, 32))] * 30
# i = 0
# for image in HALO_SPRITE13:
#     # image = make_transparent(image, <int>steps[i])
#     c1 = 1.0 + (<float>i / 5.0)
#     surface1 = smoothscale(image, (<int>(w * c1), <int>(h * c1)))
#     HALO_SPRITE13[i] = surface1.convert(32, RLEACCEL)
#     i += 1


FLASH_LIGHT = pygame.image.load("Assets\\Radial5_.png").convert(32, RLEACCEL)
LIGHT = [smoothscale(FLASH_LIGHT, (128, 128))] * 10

w = LIGHT[0].get_width()
h = LIGHT[0].get_height()

cdef:
    float ii = 0.0
    int j = 0

for surface in LIGHT:
    if j != 0:
        LIGHT[j] = smoothscale(surface, (<int>(w / ii), <int>(h / ii)))
    else:
        LIGHT[0] = surface

    ii += 0.5
    j += 1
