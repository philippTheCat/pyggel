"""
pyggle.include
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


from image import Texture
blank_texture = Texture(None, dont_load=True)
image = pygame.Surface((8,8))
image.fill((255,255,255,255))
blank_texture._compile(image)
