"""
pyggle.data
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import view
import numpy

class Texture(object):
    def __init__(self, filename, flip=0):
        view.require_init()
        self.filename = filename
        self.flip = 0

        self.size = (0,0)

        self.gl_tex = glGenTextures(1)

        if type(filename) is type(""):
            self._load_file()
        else:
            self._compile(filename)
            self.filename = None

    def _get_next_biggest(self, x, y):
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        image = pygame.image.load(self.filename)

        self._compile(image)

    def _compile(self, image):
        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", self.flip)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = size
        self.size = size
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def __del__(self):
        try:
            glDeleteTextures([self.gl_tex])
        except:
            pass #already cleared...


class DisplayList(object):
    """So we don't lose the list between copies/kills"""
    def __init__(self):
        self.gl_list = glGenLists(1)

    def begin(self):
        glNewList(self.gl_list, GL_COMPILE)

    def end(self):
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def __del__(self):
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared!

class VertexArray(object):
    def __init__(self, render_type=None, max_size=[]):
        if render_type is None:
            render_type = GL_QUADS
        self.render_type = render_type
        self.texture = None

        self.max_size = max_size

        self.verts = numpy.empty((max_size, 3), dtype=object)
        self.colors = numpy.empty((max_size, 4), dtype=object)
        self.texcs = numpy.empty((max_size, 2), dtype=object)
        self.Nobjs = 0

    def render(self):
        if self.texture:
            self.texture.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        if self.texture:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.verts)
        glColorPointer(4, GL_FLOAT, 0, self.colors)
        if self.texture:
            glTexCoordPointer(2, GL_FLOAT, 0, self.texcs)

        glDrawArrays(self.render_type, 0, self.Nobjs)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        if self.texture:
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
