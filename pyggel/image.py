from include import *

import view

_all_images = {}
def load(filename, fast=False):
    nf = filename+str(fast)
    if nf in _all_images:
        return _all_images[nf]
    if fast:
        new = FastImage(filename)
    else:
        new = Image(filename)
    _all_images[nf] = new
    return new

def load_unique(filename, fast=False):
    if fast:
        return FastImage(filename)
    return Image(filename)

_all_textures = {}
def load_texture(filename, flip=0):
    nf = filename+":"+str(flip)
    if nf in _all_textures:
        return _all_textures[nf]
    new = Texture(filename, flip)
    _all_textures[nf] = new
    return new

class Texture(object):
    def __init__(self, filename, flip=0):
        self.filename = filename
        self.flip = 0

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
        image = pygame.image.load(self.filename)

        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", self.flip)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = size

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

class Image(object):
    def __init__(self, filename, dont_load=False):
        self.filename = filename

        self.gl_tex = glGenTextures(1)

        if not dont_load:
            self._load_file()

        self.to_be_blitted = []
        self.rotation = [0,0,0]

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

        new._texturize(new._pimage2)
        new.rotation = list(self.rotation)

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

        self._texturize(self._pimage2)

    def test_on_screen(self, pos):
        r = pygame.rect.Rect(pos, self._image_size)
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
        self._compile()

    def _texturize(self, image):
        tdata = pygame.image.tostring(image, "RGBA", 0)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = self._altered_image_size

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

    def _compile(self):
        self.offset = self.get_width()/2, self.get_height()/2
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        dep_return=glGetBooleanv(GL_DEPTH_TEST)
        ble_return=glGetBooleanv(GL_BLEND)
        lig_return=glGetBooleanv(GL_LIGHTING)

        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        off = self.offset
        l = -off[0]
        r = off[0]
        t = -off[1]
        b = off[1]

        w = self.get_width()*1.0/self._altered_image_size[0]
        h = self.get_height()*1.0/self._altered_image_size[1]

        glBegin(GL_QUADS)
        glColor4f(1,1,1,1)
        glTexCoord2f(0, 0)
        glVertex3f(l, t, 0)

        glTexCoord2f(w, 0)
        glVertex3f(r, t, 0)

        glTexCoord2f(w, h)
        glVertex3f(r, b, 0)

        glTexCoord2f(0, h)
        glVertex3f(l, b, 0)
        glEnd()

        if dep_return:glEnable(GL_DEPTH_TEST)
        if not ble_return:glDisable(GL_BLEND)
        if lig_return:glEnable(GL_LIGHTING)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)

        glEndList()

    def blit(self, other, pos):
        self.remove_blit(other)
        self.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        self.to_be_blitted.append([other, pos])

    def render(self, pos):
        if not self.test_on_screen(pos):
            return None
        ox, oy = self.offset
        h, w = self.get_size()

        glPushMatrix()
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glCallList(self.gl_list)
        glPopMatrix()
        if self.to_be_blitted:
            view.screen.push_clip((pos[0], view.screen.screen_size[1]-pos[1]-h,w,h))
            for i in self.to_be_blitted:
                x, y = i[1]
                x += pos[0]
                y += pos[1]
                i[0].render((x, y))
            view.screen.pop_clip()

    def render3d(self, pos):
        ox, oy = self.offset
        h, w = self.get_size()

        glPushMatrix()
        glTranslatef(pos[0]+ox, pos[1]+oy, pos[1])
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glCallList(self.gl_list)
        glPopMatrix()
        if self.to_be_blitted:
            view.screen.push_clip((pos[0], view.screen.screen_size[1]-pos[1]-h,w,h))
            for i in self.to_be_blitted:
                x, y = i[1]
                x += pos[0]
                y += pos[1]
                i[0].render((x, y))
            view.screen.pop_clip()

    def get_width(self):
        return self._image_size[0]

    def get_height(self):
        return self._image_size[1]

    def get_size(self):
        return self._image_size

    def get_rect(self):
        return self._pimage.get_rect()

    def clear_blits(self):
        self.to_be_blitted = []

    def remove_blit(self, obj):
        for i in self.to_be_blitted:
            if i[0] == obj:
                self.to_be_blitted.remove(i)

class SceneImage(object):
    def __init__(self, image, pos):
        self.image = image
        self.pos = pos

    def render(
