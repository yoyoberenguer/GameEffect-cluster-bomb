# encoding: utf-8
#
# from Sprites import HALO_SPRITE11, HALO_SPRITE13, HALO_SPRITE14, CRATER_MASK, CRATER_COLD, CRATER_SMOKE
# from Weapons import CLUSTER_BOMB_1
# from Enemy_ import GroundEnemyTurretSentinel, GroundEnemyDroneClass, ShieldGeneratorClass
from math import floor
from os import urandom
from random import seed, randint, uniform

try:
    from BindSprite import BindSprite
except ImportError:
    raise ImportError("\n<BindSprite> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from Sounds import EXPLOSION_SOUND
except ImportError:
    raise ImportError("\n<Sounds> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
try:
    from Textures import EXPLOSIONS, SMOKE, EXPLOSION_DEBRIS, CRATER, \
        CRATER_MASK, CRATER_COLD, HALO_SPRITE11, HALO_SPRITE13, LIGHT
except ImportError:
    raise ImportError("\n<Textures> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")
# from libc.stdlib cimport abs
from libc.math cimport cos, sin, atan2, sqrt, round, nearbyint, exp

cdef extern from 'vector.c':

    struct vector2d:
       float x;
       float y;

    struct rect_p:
        int x;
        int y;

    struct mla_pack:
        vector2d vector;
        vector2d collision;


    cdef float M_PI;
    cdef float M_PI2;
    cdef float M_2PI
    cdef float RAD_TO_DEG;
    cdef float DEG_TO_RAD;

try:
    cimport cython
    from cython.parallel cimport prange
    from cpython cimport PyObject_CallFunctionObjArgs, PyObject, \
        PyList_SetSlice, PyObject_HasAttr, PyObject_IsInstance, \
        PyObject_CallMethod, PyObject_CallObject
    from cpython.dict cimport PyDict_DelItem, PyDict_Clear, PyDict_GetItem, PyDict_SetItem, \
        PyDict_Values, PyDict_Keys, PyDict_Items
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size, PyList_SetItem
    from cpython.object cimport PyObject_SetAttr

except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

try:
    import pygame
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL, BLEND_RGB_MAX
    from pygame import Surface, SRCALPHA, mask
    from pygame.transform import rotate, scale, smoothscale

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

try:
   from Sprites cimport Sprite
   from Sprites import Group, collide_mask, collide_rect, LayeredUpdates, spritecollideany, collide_rect_ratio
except ImportError:
    raise ImportError("\n<Sprites> library is missing on your system or not cynthonized."
                      "\nTry: \n   C:\\python setup_Project.py build_ext --inplace")

# TODO ELASTIC COLLISION


tmp_rect   = CRATER.get_rect()
SURFACE    = Surface((tmp_rect.w, tmp_rect.h), pygame.SRCALPHA)
DUMMY_RECT = Rect(0, 0, 0, 0)
cdef:
    list COS_TABLE  = [cos(a * DEG_TO_RAD) for a in range(0, 360)]
    list SIN_TABLE  = [sin(a * DEG_TO_RAD) for a in range(0, 360)]


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef float damped_oscillation(double t)nogil:
    return <float>(exp(-t) * cos(M_PI * t))


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class Halo(Sprite):

    cdef:
        object gl_, images_copy
        public object image, rect, _name
        tuple center
        int index
        float dt, timing, timer
        public int _blend

    def __init__(self,
                 gl_,
                 containers_,
                 images_,
                 int x,
                 int y,
                 float timing_=60.0,
                 int layer_   =-3,
                 int _blend   =0
                 ):

        Sprite.__init__(self, containers_)

        if PyObject_IsInstance(gl_.All, LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy = images_ # .copy()
        self.image       = images_[0]
        self.center      = (x, y)
        self.rect        = self.image.get_rect(center=(x, y))
        self._blend      = _blend
        self.dt          = 0
        self.index       = 0
        self.gl          = gl_

        # IF THE FPS IS ABOVE SELF.TIMING THEN
        # SLOW DOWN THE PARTICLE ANIMATION
        self.timing = 1000.0 / timing_

        if gl_.MAX_FPS > timing_:
            self.timer = self.timing
        else:
            self.timer = 0.0

        self.length1 = len(self.images_copy) - 1
        self._name = 'HALO'

    cpdef update(self, args=None):

        cdef:
            int index = self.index
            int length1   = self.length1

        if self.dt > self.timer:
            self.image = self.images_copy[index]
            self.rect  = self.image.get_rect(center=(self.center[0], self.center[1]))
            if index < length1:
                index += 1
            else:
                self.kill()
            self.dt = 0

        self.dt += self.gl.TIME_PASSED_SECONDS
        self.index = index


INVENTORY = []

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class GenericAnimation(Sprite):

    cdef:
        int index, start, stop
        object gl, image_copy
        public object image, rect
        public int _blend, layer_
        float dt, timing, timer

    def __init__(self,
                 gl_,
                 images_,
                 containers_,
                 float timing_,
                 int x,
                 int y,
                 int layer_=-1
                 ):



        Sprite.__init__(self, containers_)

        self.gl = gl_
        self.layer_ = layer_
        self._blend = 0

        if isinstance(self.gl.All, LayeredUpdates):
                self.gl.All.change_layer(self, layer_)

        self.image      = images_[0]
        self.image_copy = images_.copy()
        self.dt         = 0
        self.rect       = self.image.get_rect(center=(x, y))
        self.index      = 0
        self.start      = gl_.FRAME
        self.length1    = len(SMOKE) - 1
        self.rc         = Rect(0, 0, 0, 0).center
        seed(urandom(100))
        self.stop       = randint(50, 1000)

        if spritecollideany(self, INVENTORY):
            self.kill()
        else:
            INVENTORY.append(self)

        # IF THE FPS IS ABOVE SELF.TIMING THEN
        # SLOW DOWN THE PARTICLE ANIMATION
        self.timing = 1000.0 / timing_

        if gl_.MAX_FPS > timing_:
            self.timer = self.timing
        else:
            self.timer = 0.0


    cpdef update(self, args=None):

        cdef:
            int index = self.index
            gl        = self.gl

        if self.dt > self.timer:

            if gl.SCREENRECT.colliderect(self.rect):

                if gl.FRAME - self.start < self.stop:

                    surface    = SMOKE[self.index % self.length1]
                    self.image = self.image_copy.copy()

                    self.image.blit(surface, (0, 0), special_flags=BLEND_RGB_ADD)
                    # PyObject_CallFunctionObjArgs(self.image.blit,
                    #                             <PyObject*>surface,             # image
                    #                             <PyObject*>self.rc,             # destination
                    #                             <PyObject*>NULL,                # Area
                    #                             <PyObject*>0,                   # special_flags
                    #                             NULL)

                else:
                    self.image = CRATER_COLD

                self.rect.move_ip(gl.BACKGROUND_VECTOR)

            else:
                if self in INVENTORY:
                    INVENTORY.remove(self)
                self.kill()

            self.dt = 0
            self.index += 1

        else:
            self.dt += gl.TIME_PASSED_SECONDS


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef void show_debris(gl_, float timing_=60.0):
    """
    UPDATE THE DEBRIS POSITION ON THE GAME DISPLAY 
    
    This method replace the sprite class update method (convenient hook)
    The function requires to be called from the main loop of your game every frames
    such as:
    
    if len(DEBRIS_CONTAINER) > 0:
            show_debris(GL)
            
    This function update the debris movement, it does not draw the 
    debris onto your game display. If the debris is still not moving 
    after inserting the above line of codes into your main loop, 
    ask yourself is the sprite belongs to Gl.All group?
    The draw is guarantee by the sprite group GL.All (Layerupdates) 
    
    :param gl_: Global variables/Constants 
    :return: None
    """
    cdef:
        float timer  = 0.0
        float timing = 1000.0 / timing_

    if gl_.MAX_FPS > timing_:
        timer = timing
    else:
        timer = 0.0

    cdef:
        list debris_container = list(gl_.DEBRIS_CONTAINER)
        int w, h, w_, h_
        int debris_index
        float acceleration = 0
        float c

    for debris in debris_container:

        debris_image = debris.image
        debris_index = debris.index

        w  = debris_image.get_width()
        h  = debris_image.get_height()
        c  = <float>floor(debris_index / 20.0)
        w_ = <int>(w - c)
        h_ = <int>(h - c)
        if w > 1 and h >1:
            debris_image = scale(debris_image, (w_, h_))
        else:
            debris.kill()
            # if debris in debris_container:
            #     debris_container.remove(debris)

        # ADJUST SPEED ACCORDING TO FPS
        if debris.dt >= timer:
            acceleration = 1.0 / (1.0 + 0.001 * debris_index * debris_index)
            debris.vector *= acceleration
            debris.dt = 0
            debris.index += 1
            debris.image = debris_image
            debris.rect.move_ip(debris.vector)

        debris.dt += gl_.TIME_PASSED_SECONDS

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class XBomb(Sprite):
    """
    XBOMB CLASS
    """

    cdef:
        public object rect, image, mask
        public int _blend, layer_
        object image_copy, vector, position
        int angle
        float index, timer, timing, dt


    def __init__(self, gl_, dict surface_, int layer_, float timing_=60.0, collision_=True):
        """

        :param gl_        : instance; Contains all the variables / constants
        :param surface_   : dict;  dict {angle:surface}, Contains all pre-calculated rotations of the bomb surface
        :param layer_     : integer; layer to display sprite.
        :param timing_    : float; FPS rate default is 60 fps
        :param collision_ : bool; Detect object collision at layer level (Bomb triggers only when touching the ground)
        """

        Sprite.__init__(self, gl_.All)

        if isinstance(gl_.All, LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        seed(urandom(100))

        cdef:
            float angle_
            int x, y, angle_deg

        rect_            = gl_.player.rect
        x                = rect_.centerx
        y                = rect_.centery
        self._layer      = layer_

        angle_deg        = randint(0, 359)
        # TODO BELOW CAN BE BUFFERED
        self.image       = surface_[angle_deg]

        self.image_copy  = self.image
        self.rect        = self.image.get_rect(center=(x, y))
        self.vector      = Vector2(COS_TABLE[angle_deg], -SIN_TABLE[angle_deg]) * uniform(0.2, 4)
        self._blend      = 0
        self.position    = Vector2(x, y)
        self.index       = 0
        self.mask        = CRATER_MASK

        self.gl          = gl_

        self.timing      = 1000.0 / timing_
        self.dt          = 0

        if gl_.MAX_FPS > timing_:
            self.timer = self.timing
        else:
            self.timer = 0.0

        # NUMBER OF DEBRIS AFTER EXPLOSION
        self.DEBRIS_NUMBER = 5
        self.collision     = collision_

        gl_.BOMB_CONTAINER.add(self)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef void debris(self, int layer_=-2):
        """
        CREATE A SINGLE DEBRIS 
        
        This method is called from XBOMB update() when the bomb hit the ground.
        It creates a sprite (surface and rect attributes) with unique velocity and angle.
        Note: The debris sprite does not have customize update method yet, in fact the sprite 
        inherit the classic update method (empty hook). So if we were just adding the sprite 
        to GL.AlL sprite group, the debris will be idle on the current display.
        - show_debris is the implementation of the update methods and needs to be called from 
          the main loop every frames.
        We could have created a sprite class to avoid the extra steps that seems un-necessary 
        since an update method is already implemented by default by the sprite class.
        Therefore instantiating multiple class object is time consuming and memory inefficient.
           
        The sprite will be assigned to two different sprite groups 
        1) GL.All (containing all the sprite that will be update and draw from the main loop)
        2) GL.DEBRIS_CONTAINER containing only debris sprites that needs to be updated separately
         by show_debris
         
        IF YOUR SPRITE IS NOT MOVING:
        Don't forget to add the following lines in your main loop 
        
        if len(DEBRIS_CONTAINER) > 0:
            show_debris(GL)
            
        * and before draw
        GL.All.draw(SCREEN)
        ....
        :param layer_: 
        :return: 
        """

        # VAR DECLARATION AND TWEAKS
        cdef:
            int x = self.rect.centerx
            int y = self.rect.centery
            gl_All = self.gl.All

        # CREATE A SPRITE
        debris_sprite = Sprite()

        # ADD THE SPRITE TO GL.ALL (UPDATE FROM MAIN LOOP)
        # IN ORDER TO SEE YOU SPRITE MOVING (GL.All WILL DRAW
        # THE SPRITE)
        self.gl.All.add(debris_sprite)

        if isinstance(gl_All, LayeredUpdates):
            gl_All.change_layer(debris_sprite, layer_)

        cdef:
            int w, h

        # POPULATE SPRITE
        debris_sprite._layer   = layer_
        image                  = EXPLOSION_DEBRIS[randint(0, len(EXPLOSION_DEBRIS) - 1)]
        debris_sprite.position = Vector2(x, y)
        w                      = image.get_width()
        h                      = image.get_height()
        debris_sprite._blend   = BLEND_RGB_ADD

        # RANDOM DEBRIS SIZE
        debris_sprite.image    = scale(image, (<int>(w * <float>uniform(0.1, 0.3)),
                                               <int>(h * <float>uniform(0.1, 0.3))))
        debris_sprite.rect     = debris_sprite.image.get_rect(center=(x, y))
        # UNIQUE ANGLE AND VELOCITY
        debris_sprite.vector   = Vector2(<float>uniform(-15, 15),
                                         <float>uniform(-15, 15))
        debris_sprite.index    = 0
        debris_sprite.dt       = 0
        debris_sprite.name     = id(debris_sprite)

        # ADD THE SPRITE TO A SEPARATE GROUP DEBRIS_CONTAINER
        self.gl.DEBRIS_CONTAINER.add(debris_sprite)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef bint bomb_collision(self):
        """
        CHECK BOMB COLLISION WITH THE GROUND 
        
        NOTE: This method is called when the sprite surface 
        width and height (self.image) are < 1.0
        
        :return: True | False
        """

        crater_sprite       = Sprite()
        crater_sprite.image = CRATER
        crater_sprite.mask  = CRATER_MASK

        gl_                 = self.gl
        center_x            = self.rect.centerx
        center_y            = self.rect.centery
        crater_sprite.rect  = CRATER.get_rect(center=(center_x, center_y))

        cdef:
            list sprite_pos
            list layers             = []
            gl_All                  = gl_.All
            get_sprites_at          = gl_All.get_sprites_at
            get_layer_of_sprite     = gl_All.get_layer_of_sprite
            int get_bottom_layer    = gl_All.get_bottom_layer()
            get_sprites_from_layer  = gl_All.get_sprites_from_layer
            layers_append           = layers.append
            bint collide            = False
            int w, h
            crater_sprite_rect      = crater_sprite.rect
            list level_minus_8_group = []
            bint point


        sprite_pos = get_sprites_at(crater_sprite.rect.center)

        for sprite in sprite_pos:
            layers_append(get_layer_of_sprite(sprite))

        if get_bottom_layer not in layers:
            return False

        level_minus_8_group = get_sprites_from_layer(-8)

        w = crater_sprite_rect.w
        h = crater_sprite_rect.h

        surface = Surface((w, h), pygame.SRCALPHA)
        cdef:
            surface_blit = surface.blit

            # todo below can be done global
            # r            = Rect(0, 0, 0, 0)
            tuple rc     = DUMMY_RECT.center  # r.center

        if level_minus_8_group and len(level_minus_8_group) != 0:

            for sprite in level_minus_8_group:
                image = sprite.image
                # TODO THIS IS NOT WORKING WITH PYGAME VER 2.00
                # if image.get_alpha() != 255:
                if image.get_flags() & pygame.SRCALPHA == pygame.SRCALPHA:

                    point = collide_mask(sprite, crater_sprite)

                    if point:
                        # new_rect = surface_blit(image, rc, crater_sprite_rect)
                        # new_rect = surface.get_bounding_rect()
                        new_rect = PyObject_CallFunctionObjArgs(surface_blit,
                            <PyObject*>image,               # image
                            <PyObject*>rc,                  # destination
                            <PyObject*>crater_sprite_rect,  # Area
                            <PyObject*>0,                   # special_flags
                            NULL)

                        if (new_rect.w != w) and (new_rect.h != h):
                            continue
                        else:
                            collide = True
                            break
                else:

                    if collide_rect(crater_sprite, sprite):
                        collide = True
                        break
        return collide


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef update(self, args=None):
        """
        UPDATE METHOD FOR SPRITE BOMB 
        
        This method is called every frame from the main loop. 
        Sprite refreshing time will be equal to self.timer value.
        The sprite is destroyed as soon has it gets outside the display 
        limits (checking for rectangle collision). 
        - method bomb_collision Check for collision with the ground. 
        - BindSprite create a single instance of an explosion 
        - Halo create a single instance 
        - Create 5 debris after collision with the ground 
        * If no collision with the ground is detected the bomb will continue 
        its descent and eventually be destroyed when its surface width and height 
        get <1 
        
        NOTE: 
            Debris are placed into a separate sprite container (GL.DEBRIS_CONTAINER)
        
        :param args: None 
        :return: None 
        """

        # VAR DECLARATION AND TWEAKS
        cdef:
            gl                  = self.gl
            list bomb_container = list(gl.BOMB_CONTAINER)
            screenrect          = gl.SCREENRECT
            int w, h, center_x, center_y
            int w_, h_
            float vector_x, vector_y
            int length1         = len(EXPLOSION_SOUND) - 1
            int length2         = len(EXPLOSIONS) - 1
            int r

        # LIMIT THE FPS TO self.timer value
        if self.dt > self.timer:

            # CHECK BOUNDARIES
            if self.rect.colliderect(screenrect):

                # TWEAKS
                sprite_bomb_image_copy = self.image_copy
                center_x               = self.rect.centerx
                center_y               = self.rect.centery
                vector_x               = self.vector.x
                vector_y               = self.vector.y

                # RECT SIZE KEEPS CHANGING
                self.rect = self.image.get_rect(center=self.position)

                w = sprite_bomb_image_copy.get_width()
                h = sprite_bomb_image_copy.get_height()
                w_ = <int>(round(w - self.index))
                h_ = <int>(round(h - self.index))

                # SURFACE SIZE
                if w_ > 1.0 and h_ > 1.0:
                    self.image = scale(sprite_bomb_image_copy, (w_, h_))
                else:

                    # CHECK COLLISION WITH THE GROUND TRUE | FALSE
                    if self.collision:
                        if not self.bomb_collision():
                            self.kill()
                            return

                    # ALLOW SCREEN DAMPENING (SCREEN SHACKING)
                    gl.SHOCK_WAVE = True

                    BindSprite(
                               EXPLOSIONS[randint(0, length2)],
                               self,
                               gl,
                               timing_    =60.0,
                               layer_     =-3,
                               blend_     =BLEND_RGB_ADD,
                               event_     =None
                               )
                    # SAME THAN ABOVE
                    # Halo(gl, gl.All, EXPLOSIONS[randint(0, length2)],
                    #      center_x, center_y, 60.0, layer_=-4, _blend=BLEND_RGB_ADD)

                    # LIGHT EFFECT
                    Halo(gl, gl.All, LIGHT, center_x, center_y, 60.0, layer_=-4, _blend=BLEND_RGB_ADD)


                    # EXPLOSION SOUND (STEREO MODE)
                    gl.SC_explosion.play(EXPLOSION_SOUND[randint(0, length1)],
                                         False, 0, 1, 0, True, 'BOOM', x_=center_x)

                    # A BOMB INSTANCE WILL CREATE 5 DEBRIS AFTER EXPLOSION
                    for r in range(self.DEBRIS_NUMBER):
                        self.debris(layer_=-2)

                    # CREATE A SINGLE INSTANCE (HALO)
                    # HALO IS A SPRITE CLASS AND WILL BE UPDATED FROM THE MAIN
                    # LOOP.IF SELF IS KILLED, THE HALO SPRITE WILL STILL BE UPDATED)
                    Halo(gl, gl.All, [HALO_SPRITE11, HALO_SPRITE13][randint(0, 1)],
                         center_x, center_y, 60.0, layer_=-4, _blend=0)

                    self.kill()


                self.rect.move_ip(vector_x, vector_y)
                self.position.x += vector_x
                self.position.y += vector_y

                self.index += uniform(0.15, 0.16)

            # SPRITE OUTSIDE THE SCREEN
            else:
                self.kill()

            self.dt = 0

        self.dt += gl.TIME_PASSED_SECONDS