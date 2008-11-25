"""
pyggle.include
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


from data import Texture
import view
x = view.require_init #bypass the textures not wanting to load before init, blank texture doesn't require it...
view.require_init = lambda: None
image = pygame.Surface((2,2))
image.fill((255,255,255,255))
blank_texture = Texture(image)
view.require_init = x
