"""
pyggle.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import image, view

class Font(object):
    def __init__(self, filename=None, fsize=32):
        view.require_init()
        self.filename = filename
        self.fsize = fsize
        self.fontname = str(self.filename) + ":" + str(self.fsize)

        self._load_font()

    def _load_font(self):
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

    def make_text_image(self, text="", color=(1,1,1,1)):
        return image.Image(self.pygame_font.render(text, True, (255,255,255)),
                           colorize=color)

    def make_text_image3D(self, text="", color=(1,1,1,1)):
        return image.Image3D(self.pygame_font.render(text, True, (255,255,255)),
                             colorize=color)

class MEFontImage(object):
    def __init__(self, fontobj, text="", colorize=(1,1,1,1)):
        self.text = text
        self.fontobj = fontobj
        self.colorize = colorize
        self.pos = (0,0)
        self.rotation = (0,0,0)
        self.scale = 1
        self.visible = True

    def render(self, camera=None):
        fo = self.fontobj
        glPushMatrix()
        indent = 0
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        for c in self.text:
            o = fo.glyphs[ord(c)]
            x, y = self.pos
            x += indent
            o.pos = (x, y)
            o.render(camera)
            indent += o.get_width()
        glPopMatrix()

    def copy(self):
        n = MEFontImage(self.fontobj, self.text, self.colorize)
        n.pos = self.pos
        n.rotation = self.rotation
        n.scale = self.scale
        n.visible = self.visible
        return n

    def get_width(self):
        fo = self.fontobj
        x = 0
        for c in self.text:
            x += fo.glyphs[ord(c)].get_width()
        return x

    def get_height(self):
        fo = self.fontobj
        x = 0
        for c in self.text:
            n = fo.glyphs[ord(c)].get_height()
            if n > x: x = n
        return x

    def get_size(self):
        return (self.get_width, self.get_height)

class MEFont(object):
    """Only works for 2d images!!!!!!!"""
    def __init__(self, filename=None, fsize=32):
        view.require_init()
        self.filename = filename
        self.fsize = fsize

        self._load_font()

    def _load_font(self):
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

        L = {}
        for i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;',./<>?:\"{}| ":
            o = ord(i)
            L[o] = image.Image(self.pygame_font.render(i, True, (255,255,255)))

        self.glyphs = L

    def make_text_image(self, text="", color=(1,1,1,1)):
        return MEFontImage(self, text, color)
