
try:
    import pygame
    from pygame import mixer
except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

pygame.init()
mixer.pre_init(44100, 16, 2, 4095)

# *** EXPLOSIONS SOUNDS
EXPLOSION_SOUND1 = mixer.Sound('Assets\\boom3.ogg')
EXPLOSION_SOUND2 = mixer.Sound('Assets\\boom1.ogg')
EXPLOSION_SOUND3 = mixer.Sound('Assets\\boom2.ogg')
EXPLOSION_SOUND4 = mixer.Sound('Assets\\boom2.ogg')
EXPLOSION_SOUND  = [EXPLOSION_SOUND1, EXPLOSION_SOUND2, EXPLOSION_SOUND3, EXPLOSION_SOUND4]

# *** BOMB RELEASE SOUND
BOMB_RELEASE = pygame.mixer.Sound('Assets\\sd_bomb_release1.ogg')


MISSILE_FLIGHT_SOUND   = pygame.mixer.Sound('Assets\\sd_weapon_missile_heavy_01.ogg')