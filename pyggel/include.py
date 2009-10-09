"""
pyggel.include
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The include module imports all necessary libraries,
as well as creates a blank, white texture for general use on non-textured objects.
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

try:
    from OpenGL.GL.EXT.framebuffer_object import *
    FBO_AVAILABLE = True
except:
    FBO_AVAILABLE = False

try:
    from OpenGL.arrays import vbo
    VBO_AVAILABLE = bool(vbo.get_implementation())
except:
    VBO_AVAILABLE = False

try:
    from OpenGL.GL.EXT.texture_filter_anisotropic import *
    ANI_AVAILABLE = True
except:
    ANI_AVAILABLE = False

already_warned = []
def DepWarn(obj, reason):
    if not obj.__class__.__name__ in already_warned:
        print "Deprecation Warning (%s)\n\treason(s): %s"%(obj.__class__.__name__,
                                                           reason)
        already_warned.append(obj.__class__.__name__)
