from include import *

import view

_all_images = {}
_all_textures = {}
_all_3d_images = {}

class Texture(object):
    def __init__(self, filename, flip=0, unique=False):
        self.filename = filename
        self.flip = 0
        self.unique = False

        self.gl_tex = glGenTextures(1)

        self._load_file()

    def _get_next_biggest(self, x, y):
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        if not self.unique:
            if self.filename in _all_textures:
                glDeleteTextures(self.gl_tex)
                x = _all_textures[self.filename]
                self.gl_tex = x.gl_tex
            else:
                image = pygame.image.load(self.filename)

                size = self._get_next_biggest(*image.get_size())

                image = pygame.transform.scale(image, size)

                tdata = pygame.image.tostring(image, "RGBA", self.flip)
                
                glBindTexture(GL_TEXTURE_2D, self.gl_tex)

                xx, xy = size

                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                             GL_UNSIGNED_BYTE, tdata)
                _all_textures[self.filename] = self
        else:
            image = pygame.image.load(self.filename)

            size = self._get_next_biggest(*image.get_size())

            image = pygame.transform.scale(image, size)

            tdata = pygame.image.tostring(image, "RGBA", self.flip)
            
            glBindTexture(GL_TEXTURE_2D, self.gl_tex)

            xx, xy = size

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                         GL_UNSIGNED_BYTE, tdata)

class Image(object):
    def __init__(self, filename, pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 dont_load=False, unique=False):
        self.filename = filename
        self.unique = unique

        self.pos = pos

        self.gl_tex = glGenTextures(1)

        if not dont_load:
            self._load_file()

        self.to_be_blitted = []
        self.rotation = list(rotation)
        self.scale = scale
        self.colorize = (1,1,1,1)

        self.textured = True

    def rotate(self, amount):
        r = self.rotation
        r[0] += amount[0]
        r[1] += amount[1]
        r[2] += amount[2]
        for i in r:
            if i < 0:
                i += 360
            if i >= 360:
                i -= 360
        self.rotation = r

    def copy(self):
        new = Image(self.filename, True)
        new._pimage2 = self._pimage2.copy()
        new._pimage = new._pimage2.subsurface(0,0,*self.get_size())

        new._image_size = self._image_size
        new._altered_image_size = self._altered_image_size

        new.to_be_blitted = list(self.to_be_blitted)

        new.rect = self.rect

        new._texturize(new._pimage2)
        new.rotation = list(self.rotation)
        new.unique = self.unique
        new.pos = self.pos
        new.rotation = self.rotation
        new.scale = self.scale
        new.colorize = self.colorize

        return new

    def _get_next_biggest(self, x, y):
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def resize(self, size):
        self._pimage = pygame.transform.scale(self._pimage, size)
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

    def test_on_screen(self):
        r = pygame.rect.Rect(self.pos, self._image_size)
        return view.screen.rect.colliderect(r)

    def _load_file(self):
        if not self.unique:
            if self.filename in _all_images:
                glDeleteTextures(self.gl_tex)
                x = _all_images[self.filename]
                self.gl_tex = x
                self._pimage = x._pimage
                self._pimage2 = x._pimage2
                self._image_size = x._image_size
                self._altered_image_size = x._altered_image_size
                self.offset = x.offset
                self.gl_list = x.gl_list
                self.rect = self._pimage.get_rect()
            else:
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
                _all_images[self.filename] = self
        else:
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

        self.unique = True

        self.rect = self._pimage.get_rect()

        self._texturize(self._pimage2)
        self._compile()

    def _texturize(self, image):
        tdata = pygame.image.tostring(image, "RGBA", 0)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

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

        view.set_render_image_2d()

        glPushMatrix()
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)

        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glColor4f(*self.colorize)
        glCallList(self.gl_list)
        glPopMatrix()
        view.unset_render_image_2d()
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

    def __del__(self):
        try:
            glDeleteTextures(self.gl_tex)
        except:
            pass


class Image3D(Image):
    def __init__(self, filename, pos=(0,0,0),
                 rotation=(0,0,0), scale=1,
                 dont_load=False):
        Image.__init__(self, filename, pos, rotation,
                       scale, dont_load, False)

        self.cant_hide = False

    def render(self, camera=None):
        h, w = self.get_size()

        pos = self.pos
        if self.cant_hide:
            view.set_render_image_2d() #this is the same as 3d except disables depth testing
        else:
            view.set_render_image_3d()

        glPushMatrix()
        glScalef(self.scale, self.scale, self.scale)
        glTranslatef(pos[0], pos[1], pos[2])
        if camera:
            camera.set_facing_matrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glColor4f(*self.colorize)
        glCallList(self.gl_list)
        glPopMatrix()
        if self.cant_hide:
            view.unset_render_image_2d()
        else:
            view.unset_render_image_3d()

    def blit(self, *args, **kwargs):
        print "Image3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def copy(self):
        n = Image3D(self.filename, self.pos, self.rotation, self.scale, True)
        n._image_size = self._image_size
        n._altered_image_size = self._altered_image_size
        n.gl_list = self.gl_list
        n.gl_tex = self.gl_tex
        n._pimage = self._pimage
        n._pimage2 = self._pimage2
        n.offset = self.offset
        return n

    def _load_file(self):
        if self.filename in _all_3d_images:
            glDeleteTextures(self.gl_tex)
            x = _all_3d_images[self.filename]
            self.gl_tex = x.gl_tex
            self._pimage = x._pimage
            self._pimage2 = x._pimage2
            self._image_size = x._image_size
            self._altered_image_size = x._altered_image_size
            self.offset = x.offset
            self.gl_list = x.gl_list
        else:
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
            _all_3d_images[self.filename] = self
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

        self.unique = True

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

    def __del__(self):
        try:
            glDeleteTextures(self.gl_tex)
        except:
            pass
