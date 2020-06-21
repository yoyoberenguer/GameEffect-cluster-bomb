# encoding: utf-8
from random import random

import pygame
# from math import cos, sin, radians, hypot, degrees, acos, atan, copysign


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
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL
    from pygame import Surface, SRCALPHA, mask
    from pygame.transform import rotate, scale, smoothscale

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

try:
   from Sprites cimport Sprite
   from Sprites import Group, collide_mask, collide_rect, LayeredUpdates, spritecollideany, collide_rect_ratio
except ImportError:
    raise ImportError("\nSprites.pyd missing!.Build the project first.")

from libc.math cimport cos, sin, atan, sqrt, copysignf


cdef extern from 'vector.c':

    cdef float M_PI;
    cdef float M_PI2;
    cdef float M_2PI
    cdef float RAD_TO_DEG;
    cdef float DEG_TO_RAD;


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class BindSprite(Sprite):

    cdef:
        int obj_center_x, obj_center_y, index
        public int _blend , _layer
        object images_copy, obj, gl
        public object rect, image
        float timing, dt, timer
        str event


    def __init__(self,
                 images_,
                 object_,
                 gl_,
                 float timing_    =60.0,
                 int layer_       =0,
                 int blend_       = 0,
                 str event_       =None
                 ):

        self._layer = layer_

        Sprite.__init__(self, gl_.All)

        if PyObject_IsInstance(gl_.All, LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.images_copy  = images_.copy()
        self.image        = images_[0] if PyObject_IsInstance(
            images_, list) else images_
        self.obj          = object_
        self.obj_center_x = object_.rect.centerx
        self.obj_center_y = object_.rect.centery
        self.rect         = self.image.get_rect()
        self.rect.center  = (self.obj_center_x, self.obj_center_y)
        self.dt           = 0
        self.index        = 0
        self.gl           = gl_
        self.event        = event_
        self._blend       = blend_
        self.length       = len(self.images_copy)
        self.length_1     = self.length  - 1

        # IF THE FPS IS ABOVE SELF.TIMING THEN
        # SLOW DOWN THE PARTICLE ANIMATION
        self.timing = 1000.0 / timing_

        if gl_.MAX_FPS > timing_:
            self.timer = self.timing
        else:
            self.timer = 0.0

    @classmethod
    def kill_instance(cls, instance_):
        """ Kill a given instance """
        if PyObject_IsInstance(instance_, BindSprite):
            if PyObject_HasAttr(instance_, 'kill'):
                instance_.kill()


    cpdef update(self, args=None):
        cdef:
            obj              = self.obj
            int obj_center_x = self.obj_center_x
            int obj_center_y = self.obj_center_y
            images_copy      = self.images_copy

        if self.dt > self.timer:

            self.image = images_copy[self.index]

            if self.index >= self.length_1:
                self.kill()

            self.index += 1
            self.dt = 0

        self.dt += self.gl.TIME_PASSED_SECONDS