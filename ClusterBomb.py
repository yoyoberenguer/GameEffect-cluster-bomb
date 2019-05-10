# encoding: utf-8
"""

                   GNU GENERAL PUBLIC LICENSE

                       Version 3, 29 June 2007


 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>

 Everyone is permitted to copy and distribute verbatim copies

 of this license document, but changing it is not allowed.
 """
from math import radians, cos, sin, degrees, ceil, floor
from random import uniform, randint

import numpy as numpy

from BindSprite import *
from SpriteSheet import spread_sheet_fs8, load_per_pixel, spread_sheet_per_pixel
from Surface import reshape, add_transparency_all

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"

import pygame
from SoundServer import SoundControl
from BindSprite import BindSprite

MAXFPS = 60


class Halo(pygame.sprite.Sprite):
    """
    Create a Halo sprite after a bomb explosion
    """

    images = []
    containers = None

    def __init__(self,
                 rect_,
                 timing_,
                 layer_: int = -3
                 ):
        """
        :param rect_: pygame.Rect representing the coordinates and sprite center
        :param timing_: integer representing the sprite refreshing time in ms
        :param layer_: Layer to use, default -3
        """
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(GL.All, pygame.sprite.LayeredUpdates):
            GL.All.change_layer(self, layer_)

        self.images_copy = self.images.copy()
        self.image = self.images_copy[0]
        self.center = rect_.center
        self.rect = self.image.get_rect(center=self.center)
        self._blend = None      # No blend mode
        self.dt = 0             # time constant
        self.index = 0          # list index
        self.timing = timing_

    def update(self):

        if self.dt > self.timing:

            self.image = self.images_copy[self.index]
            self.rect = self.image.get_rect(center=self.center)
            if self.index < len(self.images_copy) - 1:
                self.index += 1
            else:
                self.kill()

            self.dt = 0

        self.dt += GL.TIME_PASSED_SECONDS


class GenericAnimation(pygame.sprite.Sprite):
    """
        Display generic sprites such as craters etc
        Not used in our example
    """
    images = None
    containers = None
    inventory = []

    def __init__(self,
                 timing_,
                 gl_,
                 center_,
                 layer_: int = -1
                 ):
        """
        :param timing_: Refreshing time (integer)
        :param gl_: Global variable (class)
        :param center_: tuple representing the sprite center
        :param layer_: layer to use
        """

        self._layer = layer_
        self._blend = None
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.GL = gl_

        if isinstance(self.GL.All, pygame.sprite.LayeredUpdates):
                self.GL.All.change_layer(self, layer_)

        self.timing = timing_
        self.image = self.images    # the sprite surface should be converted_alpha()
        self.image_copy = self.image
        self.dt = 0
        self.rect = self.image.get_rect(center=center_)
        self.index = 0
        self.start = gl_.FRAME          # FRAME number when the sprite is instantiated
        self.stop = randint(50, 1000)   # Random integer (frames)

        # Avoid putting sprite on the top of each other
        if pygame.sprite.spritecollideany(self, self.inventory):
            self.kill()
        else:
            self.inventory.append(self)

    def update(self):

        if self.dt > self.timing:

            if self.GL.SCREENRECT.colliderect(self.rect):

                if self.GL.FRAME - self.start < self.stop:

                    surface = SMOKE[int(self.index) % (len(SMOKE) - 1)]
                    self.image = self.image_copy.copy()
                    self.image.blit(surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                else:
                    # Display inactive crater
                    self.image = CRATER_COLD

                # Crater follow background speed
                self.rect.move_ip(self.GL.BACKGROUND_VECTOR)

            else:
                # clean the inventory
                if self in self.inventory:
                    self.inventory.remove(self)
                self.kill()

            self.dt = 0
            self.index += 1

        self.dt += self.GL.TIME_PASSED_SECONDS


def show_debris(screen_):
    """
    Display all the flying debris / fragments
    :param screen_:  pygame.display.get_surface() Get a reference to the currently set display surface
    """
    # All debris are slowing down after explosion
    # Display all the debris onto the game screen and refresh sprite position every frames.
    # This method has to be called every frame from the main loop after the method debris.
    # Each debris will be display full speed after blast, but will follow a deceleration
    # over the time.
    for p_ in VERTEX_DEBRIS:
        # move the rectangle in the vector direction
        p_.rect.move_ip(p_.vector)
        # calculate the sprite size
        w, h = p_.image.get_size()
        # display the sprite (debris) with the blend additive mode
        screen_.blit(p_.image, (p_.rect.centerx - (w / 2),
                                p_.rect.centery - (h / 2)),
                     special_flags=p_._blend if p_._blend is not None else 0)

        try:
            # decrease the sprite size
            p_.image = pygame.transform.scale(p_.image, (w - floor(p_.index / 20),
                                                         floor(h - p_.index / 20)))

        except:
            # Cannot be decrease anymore
            p_.kill()

        # debris deceleration
        p_.vector *= 1 / (1 + 0.0001 * p_.index ** 2)

        p_.index += 1


def debris(rect_):
    """
    Create debris / fragments flying around after an explosion.
    :param rect_: pygame.Rect that represent the debris size and shapes
    """
    # Choose debris randomly from the list EXPLOSION_DEBRIS.
    # This method is adding debris sprites into the group VERTEX_DEBRIS
    # the sprites need to have following attributes
    # _blend : choose additive mode
    # image  : pygame.Surface (texture used)
    # rect   : pygame.Rect (rectangle)
    # vector : pygame.math.Vector2, velocity vector (sprite direction)
    # index  : index position into the sprite animation
    # position : sprite starting position
    # NOTE : cannot display more than 500 debris onto the screen at once
    #        over 500 sprite no more sprites will be added to the group VERTEX_DEBRIS
    # To display every particles onto the screen, you need to implement the method
    # show_debris in the game main loop in order to refresh the sprites positions and
    # control the lifetime for each sprites.

    # Cap the number of debris to avoid lag
    if len(VERTEX_DEBRIS) > 500:
        return

    sprite_ = pygame.sprite.Sprite()

    image = EXPLOSION_DEBRIS[randint(0, len(EXPLOSION_DEBRIS) - 1)]
    sprite_.position = pygame.math.Vector2(rect_.centerx, rect_.centery)
    w, h = image.get_size()
    sprite_._blend = None
    sprite_.image = pygame.transform.scale(image, (int(w * uniform(0.1, 0.3)),
                                                   int(h * uniform(0.1, 0.3))))
    sprite_.rect = sprite_.image.get_rect(center=sprite_.position)
    sprite_.vector = pygame.math.Vector2(uniform(-15, 15), uniform(-15, 15))
    sprite_.index = 0
    VERTEX_DEBRIS.add(sprite_)


def check_background(gl_, center_):
    """
    Check if a sprite can or cannot be display.
    Goes through the entire list of sprites in the group <All> and keep only the sprite(s) colliding
    at the position (center_), then determine their layer number.
    This function avoid to display bomb explosions and craters into deep space.

    :param gl_: Global variable (class)
    :param center_: (Tuple representing the sprite center)
    """
    crater_sprite = pygame.sprite.Sprite()
    crater_sprite.image = CRATER
    crater_sprite.mask = CRATER_MASK
    crater_sprite.rect = CRATER.get_rect(center=center_)

    # get all the sprite from the same location.
    sprite_pos = gl_.All.get_sprites_at(crater_sprite.rect.center)
    layers = []
    # fetch all the layers values
    for sprite in sprite_pos:
        layers.append(gl_.All.get_layer_of_sprite(sprite))
    # check if the ground sprite is present otherwise we can't display the crater.
    if gl_.All.get_bottom_layer() not in layers:
        return False

    # Get all the sprite belonging to the layer -8 (background sprites)
    level_minus_8_group = gl_.All.get_sprites_from_layer(-8)

    collide = False
    w, h = crater_sprite.rect.size
    if level_minus_8_group is not None and len(level_minus_8_group) != 0:
        for sprite in level_minus_8_group:
            # Checking the surface to determine if the texture is convert_alpha() or
            # convert(). We can only check the masks for surface with per-pixel information.
            # Otherwise skip the mask check and check for rect collision instead
            if sprite.image.get_alpha() != 255:
                point = pygame.sprite.collide_mask(sprite, crater_sprite)

                if point is not None:
                    # empty surface
                    surface = pygame.Surface((w, h), pygame.SRCALPHA)
                    # filled up the empty surface with the background texture
                    surface.blit(sprite.image, (0, 0), crater_sprite.rect)
                    # find the bounding rect containing data min_alpha = 1
                    # compare the bounding rect to what a full size rectangle should be
                    # and determine if the rectangle is cropped
                    new_rect = surface.get_bounding_rect()

                    if new_rect.size != (w, h):
                        continue
                    else:
                        collide = True
                        break
            else:
                # check on rectangle collision instead of mask collision.
                # The surface is possibly a 32bit with per-pixel info but has been converted to fast blit
                # get_alpha() returning the value 255 (most likely to be converted).
                # Checking for rect collision and stop to the first collision (break)
                if pygame.sprite.collide_rect(crater_sprite, sprite):
                    collide = True
                    break

    return collide


def display_bombing(screen):
    """
    Display the bomb dropping from the aircraft.
    :param screen: pygame.display.get_surface()
    """
    # 1) Show the bombs on the screen and decrease their sizes with time to simulate bomb dropping
    # 2) when bomb texture size is null or negative, show an explosion sprite using BindSprite class
    # 3) Create debris flying around after explosions
    # 4) Create a crater texture following the background speed using the class GenericAnimation
    # 5) Create a blast effect for each bomb using the class Halo
    # display the sprite onto the screen and kill the sprite whenever it goes outside the screen limits.
    # When the sprite is killed, it is automatically removed from the group VERTEX_BOMB.
    # A sprite is killed only in two cases :
    # 1) it goes outside the screen and cannot be display
    # 2) Bomb texture size is null or negative.
    # As you can see, we are using the method blit to represent the sprite onto the screen. It means that
    # we need to call this method every iteration from the game main loop. Calling the pygame method update()
    # from the main loop will have no effect.

    for sprite in VERTEX_BOMB:

        # Checking if the sprite collide with the display, otherwise it will
        # be killed
        if sprite.rect.colliderect(screen.get_rect()):

            sprite.rect = sprite.image.get_rect(center=sprite.position)
            w, h = sprite.image_copy.get_size()

            try:
                # decrease texture size each iteration until ValueError (null or negative size)
                sprite.image = pygame.transform.scale(sprite.image_copy,
                                        (round(w - sprite.index), round(h - sprite.index)))
            except ValueError:

                if not check_background(GL, sprite.rect.center):
                    sprite.kill()
                    continue

                # Explosion sprite
                global bomb_
                bomb_ = True
                BindSprite.images = EXPLOSIONS[randint(0, len(EXPLOSIONS) - 1)]
                BindSprite.containers = GL.All
                BindSprite(sprite,
                           GL,                              # Global variable
                           offset_=None,                    # no offset from center
                           timing_=15,                      # 60 FPS
                           layer_=-3,                       # layer -3
                           loop_=False,                     # no loops, will be killed at the end
                           dependency_=False,               # no dependency
                           follow_=False,                   # does not follow parent vector
                           blend_=pygame.BLEND_RGB_ADD,     # additive mode
                           event_=None                      # not needed
                           )

                # Place a crater on the screen for each bomb (use additive mode)
                # GenericAnimation.images = CRATER
                # GenericAnimation.containers = GL.All
                # generic = GenericAnimation(timing_=1, gl_=GL, center_=sprite.rect.center, layer_=-1)
                # if generic is not None:
                #    generic._blend = pygame.BLEND_RGB_ADD

                # choose an explosion sound from a list, use the stereo panning mode for realistic sound effect
                GL.SC_explosion.play(EXPLOSION_SOUND[randint(0, len(EXPLOSION_SOUND) - 1)],
                                     False, 0, 1, 0, True, 'BOOM', x_=sprite.rect.w)

                # create flying debris for each bomb (5 debris)
                for r in range(10):
                    debris(sprite.rect)

                """
                BindSprite.images = RADIAL
                BindSprite.containers = GL.All
                bind = BindSprite(object_=sprite, gl_=GL,
                                  offset_=None, timing_=1,
                                  layer_=-4, loop_=False, dependency_=False,
                                  follow_=False, event_='FLASH', blend_=pygame.BLEND_RGB_ADD)
                """
                # Create a halo explosion for each bomb (blast)
                Halo.images = [HALO_SPRITE11, HALO_SPRITE13][randint(0, 1)]     # surface(s) to use
                Halo.containers = GL.All                                        # pygame group
                Halo(sprite.rect, 10, layer_=-4)                                # adjust the layer level if you want to
                # see the blast on the top of the explosion
                sprite.kill()
            # Blending effect & center the sprite (blit always display the sprite from the left corner)
            # screen.blit(sprite.image_, (sprite.rect.centerx - sprite.rect.w / 2,
            #                            sprite.rect.centery - sprite.rect.h / 2 - 2),
            #            special_flags=sprite._blend)

            sprite.rect.move_ip(sprite.vector)
            sprite.position += sprite.vector

            # Adjust the value to obtain the desired effect
            # small values e.g 0.08 gives a bigger spread
            # Nevertheless, if the spread is too big the projectile might go outside
            # the screen limits and be killed before exploding...
            # Add random values using math.uniform for a better effect
            # If the missile texture is scale to a bigger size, you will need to change these
            # values.
            # If you change the FPS of your game you will still need to adjust
            sprite.index += uniform(0.15, 0.16)


        else:
            sprite.kill()


def bombing(rect_,
            surface_: pygame.Surface,
            layer_: int
            ):
    """
    Create a bomb and put it into the VERTEX_BOMB group
    :param rect_:       pygame.Rect
    :param surface_:    bomb sprite (pygame.Surface)
    :param layer_:      Layer to use
    """

    # Create bomb sprite and add it to VERTEX_BOMB (pygame group)
    # Each sprite are set with specific attributes
    # angle : angle the bomb will follow, e.g 180 degrees will mean that the bomb is shot at 180 degrees from the
    # player center position.
    # vector: vector corresponding to the angle direction and set to a unique speed ( * uniform(0.2, 3))
    #         uniform will determine the bomb spread velocity. 0.2 to allow bomb to drop nearby the spaceship and 3
    #         for a larger spread.
    # _blend : use additive mode
    # image  : texture to use (pygame.Surface)
    # rect   : rectangle (pygame.Rect), for positioning
    # mask   : for mask collision checks
    # This method is use prior using the method display_bombing.
    # All bomb sprites are passed into the VERTEX_BOMB for head counting and display.
    # Use the method display_bombing inside the main loop to refresh the sprite onto the screen, calling the classic
    # pygame method update() from the main loop will have no effect.
    # This method does not control the sprite bomb population, in fact it keep adding sprite to VERTEX_BOMB.
    # The method display_bombing will display the sprite and adjust the position onto the screen and control
    # its lifetime.
    bombsprite = pygame.sprite.Sprite()
    pygame.sprite.Sprite.__init__(bombsprite, GL.All)

    GL.All.add(bombsprite)
    if isinstance(GL.All, pygame.sprite.LayeredUpdates):
        GL.All.change_layer(bombsprite, layer_)

    bombsprite._layer = layer_
    angle_ = radians(randint(0, 360))
    bombsprite.angle = degrees(angle_) - 90
    bombsprite.image = pygame.transform.rotate(surface_, bombsprite.angle)
    bombsprite.image_copy = bombsprite.image.copy()
    bombsprite.rect = bombsprite.image.get_rect(center=(rect_.x, rect_.y))
    bombsprite.vector = pygame.math.Vector2(cos(angle_), -sin(angle_)) * uniform(0.2, 4)
    bombsprite._blend = None
    bombsprite.position = rect_
    bombsprite.index = 0
    bombsprite.mask = CRATER_MASK
    VERTEX_BOMB.add(bombsprite)


if __name__ == '__main__':

    class GL:
        FRAME = 0


    class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

        def __init__(self):
            pygame.sprite.LayeredUpdates.__init__(self)

        def draw(self, surface_):
            """draw all sprites in the right order onto the passed surface

            LayeredUpdates.draw(surface): return Rect_list

            """
            spritedict = self.spritedict
            surface_blit = surface_.blit
            dirty = self.lostsprites
            self.lostsprites = []
            dirty_append = dirty.append
            init_rect = self._init_rect
            for spr in self.sprites():
                rec = spritedict[spr]

                if hasattr(spr, '_blend') and spr._blend is not None:
                    newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)
                else:
                    newrect = surface_blit(spr.image, spr.rect)

                if rec is init_rect:
                    dirty_append(newrect)
                else:
                    if newrect.colliderect(rec):
                        dirty_append(newrect.union(rec))
                    else:
                        dirty_append(newrect)
                        dirty_append(rec)
                spritedict[spr] = newrect
            return dirty


    class Player(pygame.sprite.Sprite):

        images = None
        containers = None

        def __init__(self, pos_, gl_, timing_=15, layer_=0):
            pygame.sprite.Sprite.__init__(self, Player.containers)

            self.image = Player.images
            self.rect = self.image.get_rect(center=pos_)

            self.mask = pygame.mask.from_surface(self.image)
            self.gl = gl_
            self.layer = layer_
            self.timing = timing_
            self.angle = 0
            self.life = 1000
            self.max_life = 1000
            self._rotation = 0

        def update(self):
            self.rect = self.rect.clamp(SCREENRECT)


    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.SCREENRECT = SCREENRECT
    pygame.display.init()
    SCREEN = pygame.display.set_mode(SCREENRECT.size, pygame.HWACCEL, 32)
    GL.screen = SCREEN
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4095)

    bomb = pygame.image.load('Assets\\MISSILE3.png').convert_alpha()
    w, h = bomb.get_size()
    bomb = pygame.transform.smoothscale(bomb, (int(w / 30), int(h / 30)))
    EXPLOSION1 = spread_sheet_fs8('Assets\\Explosion8_256x256_.png', 256, 6, 6)
    EXPLOSION2 = spread_sheet_fs8('Assets\\Explosion9_256x256_.png', 256, 6, 8)
    EXPLOSION3 = spread_sheet_fs8('Assets\\Explosion10_256x256_.png', 256, 6, 7)
    EXPLOSION4 = spread_sheet_fs8('Assets\\Explosion11_256x256_.png', 256, 6, 7)
    EXPLOSION5 = spread_sheet_fs8('Assets\\Explosion12_256x256_.png', 256, 6, 7)
    TRY = spread_sheet_fs8('Assets\\Explosion12_256x256_.png', 256, 6, 7)
    TRY = reshape(TRY, (256, 256))
    rnd = randint(128, 256)
    EXPLOSION1 = reshape(EXPLOSION1, (rnd, rnd))
    rnd = randint(128, 256)
    EXPLOSION2 = reshape(EXPLOSION2, (rnd, rnd))
    rnd = randint(128, 256)
    EXPLOSION3 = reshape(EXPLOSION3, (rnd, rnd))
    rnd = randint(128, 256)
    EXPLOSION4 = reshape(EXPLOSION4, (rnd, rnd))
    rnd = randint(128, 256)
    EXPLOSION5 = reshape(EXPLOSION5, (rnd, rnd))
    # EXPLOSIONS = [EXPLOSION1, EXPLOSION2, EXPLOSION3, EXPLOSION4, EXPLOSION5]
    EXPLOSIONS = [TRY]
    EXPLOSION_SOUND1 = pygame.mixer.Sound('Assets\\boom3.ogg')
    EXPLOSION_SOUND2 = pygame.mixer.Sound('Assets\\boom1.ogg')
    EXPLOSION_SOUND3 = pygame.mixer.Sound('Assets\\boom2.ogg')
    EXPLOSION_SOUND4 = pygame.mixer.Sound('Assets\\boom2.ogg')
    EXPLOSION_SOUND = [EXPLOSION_SOUND1, EXPLOSION_SOUND2, EXPLOSION_SOUND3, EXPLOSION_SOUND4]
    CRATER_COLD = pygame.image.load('Assets\\Crater3_.png').convert()
    CRATER_COLD = pygame.transform.smoothscale(CRATER_COLD, (32, 32))
    CRATER = pygame.image.load('Assets\\Crater2_.png')
    CRATER = pygame.transform.smoothscale(CRATER, (32, 32)).convert_alpha()
    CRATER_MASK = pygame.mask.from_surface(CRATER)
    BOMB_RELEASE = pygame.mixer.Sound('Assets\\sd_bomb_release1.ogg')
    SMOKE = spread_sheet_fs8('Assets\\Laval1_256_6x6_.png', 256, 6, 6)
    SMOKE = reshape(SMOKE, (32, 32))

    clock = pygame.time.Clock()
    GL.TIME_PASSED_SECONDS = clock.tick(60)

    All = LayeredUpdatesModified()
    # globalisation
    GL.All = All

    BACKGROUND = pygame.image.load('Assets\\A0.png').convert_alpha()
    bck = pygame.sprite.Sprite()
    bck.image = BACKGROUND
    bck.rect = BACKGROUND.get_rect(topleft=(0, 0))
    bck.mask = pygame.mask.from_surface(bck.image)
    bck._layer = -8
    GL.All.add(bck)

    BACKGROUND1 = pygame.image.load('Assets\\nightsky.jpg').convert()
    BACKGROUND1 = pygame.transform.smoothscale(BACKGROUND1, SCREENRECT.size)
    bck1 = pygame.sprite.Sprite()
    bck1.image = BACKGROUND1
    bck1.rect = BACKGROUND1.get_rect(topleft=(0, 0))
    # No mask
    bck1._layer = -9
    GL.All.add(bck1)


    VERTEX_BOMB = pygame.sprite.Group()
    VERTEX_DEBRIS = pygame.sprite.Group()

    GL.PLAYER_GROUP = pygame.sprite.Group()
    GL.GROUP_UNION = pygame.sprite.Group()
    GL.enemy_group = pygame.sprite.Group()
    SoundControl.SCREENRECT = SCREENRECT
    GL.SC_spaceship = SoundControl(60)
    GL.SC_explosion = SoundControl(60)
    GL.SOUND_LEVEL = 1.0

    G5V200_DEBRIS = [
        pygame.image.load('Assets\\Boss7Debris\\Boss7Debris1.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\Boss7Debris2.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\Boss7Debris3.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\Boss7Debris4.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\Boss7Debris5.png').convert_alpha()
    ]

    G5V200_DEBRIS_HOT = [
        pygame.image.load('Assets\\Boss7Debris\\debris1.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\debris2.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\debris3.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\debris4.png').convert_alpha(),
        pygame.image.load('Assets\\Boss7Debris\\debris5.png').convert_alpha()
    ]
    G5V200_DEBRIS = reshape(G5V200_DEBRIS, factor_=(64, 64))
    G5V200_DEBRIS_HOT = reshape(G5V200_DEBRIS_HOT, factor_=(64, 64))
    EXPLOSION_DEBRIS = [*G5V200_DEBRIS_HOT, *G5V200_DEBRIS]

    SPACE_FIGHTER_SPRITE = pygame.image.load('Assets\\illumDefault11.png').convert_alpha()
    SPACE_FIGHTER_SPRITE = pygame.transform.smoothscale(SPACE_FIGHTER_SPRITE, (80, 55))
    MISSILE_FLIGHT_SOUND = pygame.mixer.Sound('Assets\\sd_weapon_missile_heavy_01.ogg')
    STINGER_MISSILE_SPRITE = pygame.image.load('Assets\\MISSILE0.png').convert_alpha()
    COBRA = pygame.image.load('Assets\\SpaceShip.png').convert_alpha()

    steps = numpy.array([0., 0.03333333, 0.06666667, 0.1, 0.13333333,
                         0.16666667, 0.2, 0.23333333, 0.26666667, 0.3,
                         0.33333333, 0.36666667, 0.4, 0.43333333, 0.46666667,
                         0.5, 0.53333333, 0.56666667, 0.6, 0.63333333,
                         0.66666667, 0.7, 0.73333333, 0.76666667, 0.8,
                         0.83333333, 0.86666667, 0.9, 0.93333333, 0.96666667])
    HALO_SPRITE11 = [pygame.transform.smoothscale(
        load_per_pixel('Assets\\Halo11.png'), (64, 64))] * 30
    for number in range(len(HALO_SPRITE11)):
        rgb = pygame.surfarray.array3d(HALO_SPRITE11[number])
        alpha = pygame.surfarray.array_alpha(HALO_SPRITE11[number])
        # Remove excess pixels (contour pixels)
        # The resulting image is a surface with alpha transparency layer (convert_alpha())
        image = add_transparency_all(rgb, alpha, int(255 * steps[number]))
        # image size is x2 (last sprite)
        surface1 = pygame.transform.smoothscale(image, (
            int(image.get_width() * (1 + (number / 10))),
            int(image.get_height() * (1 + (number / 10)))))
        # Do not convert surface to fast blit
        HALO_SPRITE11[number] = surface1.convert_alpha()

    HALO_SPRITE13 = [pygame.transform.smoothscale(
        load_per_pixel('Assets\\Halo13.png'), (64, 64))] * 30
    for number in range(len(HALO_SPRITE13)):
        rgb = pygame.surfarray.array3d(HALO_SPRITE13[number])
        alpha = pygame.surfarray.array_alpha(HALO_SPRITE13[number])
        image = add_transparency_all(rgb, alpha, int(255 * steps[number]))
        # image size is x2 (last sprite)
        surface1 = pygame.transform.smoothscale(image, (
            int(image.get_width() * (1 + (number / 10))),
            int(image.get_height() * (1 + (number / 10)))))
        # Do not convert surface to fast blit
        HALO_SPRITE13[number] = surface1.convert_alpha()

    # RADIAL, create a light effect during explosion,
    # use a radial bitmap with blend additive mode
    RAD = pygame.image.load("Assets\\Radial5_.png").convert()
    RAD = pygame.transform.smoothscale(RAD, (128, 128))
    RADIAL = [RAD] * 10
    w, h = RADIAL[0].get_size()
    i = 0
    j = 0
    for surface in RADIAL:
        if j != 0:
            RADIAL[j] = pygame.transform.smoothscale(surface, (int(w / i), int(h / i)))
        else:
            RADIAL[0] = surface
        i += 0.5
        j += 1

    Player.images = COBRA
    Player.containers = GL.All, GL.PLAYER_GROUP

    GL.player = Player(pos_=(SCREENRECT.centerx, SCREENRECT.centery), gl_=GL, timing_=0, layer_=0)
    Player._blend = None

    vibration = 10
    bomb_ = False

    STOP_GAME = False
    QUIT = False
    GL.PAUSE = False
    em = pygame.sprite.Group()
    hm = pygame.sprite.Group()

    recording = False  # allow recording video
    VIDEO = []  # Capture frames
    trumble = 2
    while not STOP_GAME:

        background_v = pygame.math.Vector2(0, 0)

        pygame.event.pump()

        keys = pygame.key.get_pressed()

        while GL.PAUSE:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                # print(keys)
                if keys[pygame.K_PAUSE]:
                    GL.PAUSE = False
                    pygame.event.clear()

        for event in pygame.event.get():

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                ...

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            STOP_GAME = True

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

        if keys[pygame.K_SPACE]:
            trumble = 10
            vibration = 0
            if not GL.SC_spaceship.get_identical_sounds(BOMB_RELEASE):
                GL.SC_spaceship.play(sound_=BOMB_RELEASE, loop_=False, priority_=2,
                                     volume_=1, fade_out_ms=0, panning_=False,
                                     name_='BOMB_RELEASE', x_=0)  # x = 0 not using the panning mode
            if len(VERTEX_BOMB) < 50:
                for r in range(50):
                    bombing(pygame.math.Vector2(GL.player.rect.center), bomb, -4)

        if keys[pygame.K_PAUSE]:
            GL.PAUSE = True

        if len(VERTEX_BOMB) == 0:
            bomb_ = False
        else:
            if 0 < vibration <= 10:
                vibration = -2
            elif 0 >= vibration > -10:
                vibration = 2

        # background_v += pygame.math.Vector2(vibration, 0) if bomb_ else (0, 0)
        GL.BACKGROUND_VECTOR = background_v
        bck.rect.left = background_v.x if bomb_ else 0
        GL.All.update()

        GL.All.draw(SCREEN)

        if len(VERTEX_BOMB) > 0:
            display_bombing(SCREEN)

        if len(VERTEX_DEBRIS) > 0:
            show_debris(SCREEN)

        # Cap the speed at 60 FPS
        GL.TIME_PASSED_SECONDS = clock.tick(60)

        pygame.display.flip()

        if recording:
            VIDEO.append(pygame.image.tostring(SCREEN, 'RGB', False))

        GL.SC_spaceship.update()
        GL.SC_explosion.update()

        # print(clock.get_fps(), GL.FRAME)

        GL.FRAME += 1
        pygame.event.clear()

    if recording:
        import cv2
        from cv2 import COLOR_RGBA2BGR
        import numpy

        video = cv2.VideoWriter('Bombing.avi',
                                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                                (SCREENRECT.w, SCREENRECT.h), True)

        for event in pygame.event.get():
            pygame.event.clear()

        for image in VIDEO:
            image = numpy.fromstring(image, numpy.uint8).reshape(SCREENRECT.h, SCREENRECT.w, 3)
            image = cv2.cvtColor(image, COLOR_RGBA2BGR)
            video.write(image)

        cv2.destroyAllWindows()
        video.release()

    pygame.quit()
