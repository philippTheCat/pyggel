"""
pyggle.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import image


_all_fonts = {}

class Font(object):
    def __init__(self, filename=None, fsize=32):
        self.filename = filename
        self.fsize = fsize
        self.fontname = str(self.filename) + ":" + str(self.fsize)

        self._load_font()

    def _load_font(self):
        if self.fontname in _all_fonts:
            self.pygame_font = _all_fonts[self.fontname]
        else:
            self.pygame_font = pygame.font.Font(self.filename, self.fsize)
            _all_fonts[self.fontname] = self.pygame_font

    def make_text_image(self, text="", color=(255,255,255), antialias=True):
        return image.Image(self.pygame_font.render(text, antialias, color))

    def make_text_image3D(self, text="", color=(255,255,255), antialias=True):
        return image.Image3D(self.pygame_font.render(text, antialias, color))
