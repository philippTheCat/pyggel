"""
pyggle.image
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *

import view

class Texture(object):
    def __init__(self, filename, flip=0):
        self.filename = filename
        self.flip = 0

        self.size = (0,0)

        self.gl_tex = glGenTextures(1)

        if type(filename) is type(""):
            self._load_file()
        else:
            self._compile(filename)

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

class Image(object):
    def __init__(self, filename, pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        view.require_init()
        self.filename = filename

        self.pos = pos

        if type(filename) is type(""):
            self._load_file()
        else:
            self.compile_from_surface(filename)

        self.to_be_blitted = []
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize
        self.visible = True

    def copy(self, shallow=True):
        new = Image(self._pimage)

        if not shallow:
            new.rotation = list(self.rotation)
            new.pos = self.pos
            new.rotation = self.rotation
            new.scale = self.scale
            new.colorize = self.colorize
            new.to_be_blitted = list(self.to_be_blitted)
            new.clear_mem()
            new.gl_list = self.gl_list
            new.gl_tex = self.gl_tex
        return new

    def _get_next_biggest(self, x, y):
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def test_on_screen(self):
        r = pygame.rect.Rect(self.pos, self._image_size)
        return view.screen.rect.colliderect(r)

    def _load_file(self):
        self._pimage = pygame.image.load(self.filename)

        sx, sy = self._pimage.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._pimage, (0,0))

        self._pimage = self._pimage2.subsurface(0,0,sx,sy)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self.rect = self._pimage.get_rect()
        self._compile()

    def compile_from_surface(self, surf):
        self._pimage = surf
        sx, sy = self._pimage.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._pimage, (0,0))

        self._pimage = self._pimage2.subsurface(0,0,sx,sy)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self.rect = self._pimage.get_rect()

        self._texturize(self._pimage2)
        self._compile()

    def _texturize(self, image):
        self.gl_tex = glGenTextures(1)
        tdata = pygame.image.tostring(image, "RGBA", 0)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        xx, xy = self._altered_image_size

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

    def _compile(self):
        self.offset = self.get_width()/2, self.get_height()/2
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        off = self.offset
        l = -off[0]
        r = off[0]
        t = -off[1]
        b = off[1]

        w = self.get_width()*1.0/self._altered_image_size[0]
        h = self.get_height()*1.0/self._altered_image_size[1]

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(l, t, 0)

        glTexCoord2f(w, 0)
        glVertex3f(r, t, 0)

        glTexCoord2f(w, h)
        glVertex3f(r, b, 0)

        glTexCoord2f(0, h)
        glVertex3f(l, b, 0)
        glEnd()

        glEndList()

    def blit(self, other, pos):
        self.remove_blit(other)
        self.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        self.to_be_blitted.append([other, pos])

    def render(self, camera=None):
        if not self.test_on_screen():
            return None

        ox, oy = self.offset
        h, w = self.get_size()

        pos = self.pos

        glPushMatrix()
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)

        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        glColor(*self.colorize)
        glCallList(self.gl_list)
        glPopMatrix()
        if self.to_be_blitted:
            view.screen.push_clip((pos[0], view.screen.screen_size[1]-pos[1]-h,w,h))
            for i in self.to_be_blitted:
                x, y = i[1]
                x += pos[0]
                y += pos[1]
                o = i[0].pos
                i[0].pos = (x, y)
                i[0].render()
                i[0].pos = o
            view.screen.pop_clip()

    def get_width(self):
        return self._image_size[0]

    def get_height(self):
        return self._image_size[1]

    def get_size(self):
        return self._image_size

    def get_rect(self):
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]
        return self.rect

    def clear_blits(self):
        self.to_be_blitted = []

    def remove_blit(self, obj):
        for i in self.to_be_blitted:
            if i[0] == obj:
                self.to_be_blitted.remove(i)

    def clear_mem(self):
        try:
            glDeleteTextures([self.gl_tex])
        except:
            pass #already cleared
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared

    def __del__(self):
        self.clear_mem()


class Image3D(Image):
    def __init__(self, filename, pos=(0,0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        Image.__init__(self, filename, pos, rotation,
                       scale, colorize)

    def render(self, camera=None):
        h, w = self.get_size()

        pos = self.pos

        glPushMatrix()
        glTranslatef(pos[0], pos[1], -pos[2])
        if camera:
            camera.set_facing_matrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        glColor(*self.colorize)
        glDisable(GL_LIGHTING)
        glCallList(self.gl_list)
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        glPopMatrix()

    def blit(self, *args, **kwargs):
        print "Image3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def copy(self, shallow=True):
        n = Image3D(self._pimage)
        
        if not shallow:
            n.pos = self.pos
            n.rotation = self.rotation
            n.scale = self.scale
            n.colorize = self.colorize
            n.clear_mem()
            n.gl_list = self.gl_list
            n.gl_tex = self.gl_tex
        return n

    def _load_file(self):
        self._pimage = pygame.image.load(self.filename)

        sx, sy = self._pimage.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._pimage, (0,0))

        self._pimage = self._pimage2.subsurface(0,0,sx,sy)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self._compile()
        self.rect = self._pimage.get_rect()

    def compile_from_surface(self, surf):
        self._pimage = surf
        sx, sy = self._pimage.get_size()
        xx, xy = self._get_next_biggest(sx, sy)

        self._pimage2 = pygame.Surface((xx, xy)).convert_alpha()
        self._pimage2.fill((0,0,0,0))

        self._pimage2.blit(self._pimage, (0,0))

        self._pimage = self._pimage2.subsurface(0,0,sx,sy)

        self._image_size = (sx, sy)
        self._altered_image_size = (xx, xy)

        self._texturize(self._pimage2)
        self._compile()

    def _compile(self):
        self.offset = self.get_width()/2, self.get_height()/2
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        w = self.get_width()*1.0/self._altered_image_size[0]
        h = self.get_height()*1.0/self._altered_image_size[1]

        gw, gh = self.get_size()

        if gw < gh:
            uw = gw * 1.0 / gh
            uh = 1
        elif gh < gw:
            uw = 1
            uh = gh * 1.0 / gw
        else:
            uw = uh = 1

        glBegin(GL_QUADS)
        glTexCoord2f(0, h)
        glVertex3f(-uw, -uh, 0)

        glTexCoord2f(w, h)
        glVertex3f(uw, -uh, 0)

        glTexCoord2f(w, 0)
        glVertex3f(uw, uh, 0)

        glTexCoord2f(0, 0)
        glVertex3f(-uw, uh, 0)
        glEnd()

        glEndList()
