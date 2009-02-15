"""
pyggle.image
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The image module contains classes to load and render both 2d and 3d (billboarded) images.
"""
import time

from include import *

import view, data

import Image as pilImage

class Image(object):
    """A 2d image object"""
    def __init__(self, filename, pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        """Create the Image
           filename must be a filename to an image file, or a pygame.Surface object
           pos is the 2d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the Image"""
        view.require_init()
        self.filename = filename

        self.pos = pos

        if type(filename) is type(""):
            self._load_file()
        else:
            self.compile_from_surface(filename)
            self.filename = None

        self.to_be_blitted = []
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize
        self.visible = True

    def copy(self):
        """Return a copy of the image - sharing the same data.DisplayList"""
        new = Image(self.filename, self.pos, self.rotation, self.scale,
                    self.colorize, True)
        new._pimage = self._pimage
        new._pimage2 = self._pimage2
        new._image_size = self._image_size
        new._altered_image_size = self._altered_image_size
        new.rect = new._pimage.get_rect()
        new.to_be_blitted = list(self.to_be_blitted)
        new.display_list = self.display_list
        new.texture = self.texture
        new.offset = self.offset
        return new

    def _get_next_biggest(self, x, y):
        """Return next largest power of 2 size for an image"""
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def test_on_screen(self):
        """Return whether the image is onscreen or not"""
        r = pygame.rect.Rect(self.pos, self._image_size)
        return view.screen.rect2d.colliderect(r)

    def _load_file(self):
        """Load an image file"""
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
        """Prepare surf to be stored in a Texture and DisplayList"""
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
        """Bind image to a data.Texture"""
        self.texture = data.Texture(image)

    def _compile(self):
        """Compile the Image into a data.DisplayList"""
        self.offset = self.get_width()/2, self.get_height()/2
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]

        self.display_list = data.DisplayList()
        self.display_list.begin()
        self.texture.bind()
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

        self.display_list.end()

    def blit(self, other, pos):
        """Blit another image to this one at pos offset - ONLY allowing an image to blitted once
           other is another image.Image
           pos is the x,y offset of the blit"""
        self.remove_blit(other)
        self.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        """Same as blit, except you can blit the same image multiple times"""
        self.to_be_blitted.append([other, pos])

    def render(self, camera=None):
        """Render the image
           camera can be None or the camera the scene is using"""
        if not self.test_on_screen():
            return None

        ox, oy = self.offset
        h, w = self.get_size()

        pos = self.pos

        glPushMatrix()
        rx = 1.0 * view.screen.screen_size[0] / view.screen.screen_size_2d[0]
        ry = 1.0 * view.screen.screen_size[1] / view.screen.screen_size_2d[1]
        glScalef(rx, ry, 1)
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)

        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)

        glColor(*self.colorize)
        self.display_list.render()
        glPopMatrix()
        if self.to_be_blitted:
            view.screen.push_clip((int(pos[0]*rx), view.screen.screen_size[1]-int(pos[1]*ry)-int(h*ry), int(w*rx), int(h*ry)))
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
        """Return the width in pixels of the image"""
        return self._image_size[0]

    def get_height(self):
        """Return the height in pixels of the image"""
        return self._image_size[1]

    def get_size(self):
        """Return the width/height size of the image"""
        return self._image_size

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        self.rect.center = self.offset[0] + self.pos[0], self.offset[1] + self.pos[1]
        return self.rect

    def clear_blits(self):
        """Remove all blits from the image"""
        self.to_be_blitted = []

    def remove_blit(self, image):
        """Remove all blits of image from the Image"""
        for i in self.to_be_blitted:
            if i[0] == image:
                self.to_be_blitted.remove(i)

    def sub_image(self, topleft, size):
        """Return a new Image object representing a smaller region of this Image."""
        image = self._pimage.subsurface(topleft, size)
        return Image(image, self.pos, self.rotation, self.scale, self.colorize)


class Image3D(Image):
    """A billboarded 3d image"""
    def __init__(self, filename, pos=(0,0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        """Create the Image3D
           filename must be a filename to an image file, or a pygame.Surface object
           pos is the 3d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the Image
           dont_load forces the Image not to load a filename and compile
               Deprecated - used to create an image from a surface instead of loading"""
        Image.__init__(self, filename, pos, rotation,
                       scale, colorize)

    def get_dimensions(self):
        """Return a tuple of (1,1,1) signifying the 3d dimensions of teh image - used by the quad tree"""
        return 1, 1, 1

    def get_pos(self):
        """Return the position of the Image3D"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

    def render(self, camera=None):
        """Render the Image3D
           camera can be None or the camera the scene is using to render from"""
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
        self.display_list.render()
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        glPopMatrix()

    def blit(self, *args, **kwargs):
        print "Image3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def copy(self):
        """Return a copy og the Image - sharing the same data.DisplayList"""
        new = Image3D(self.filename, self.pos, self.rotation, self.scale,
                      self.colorize, True)
        new._pimage = self._pimage
        new._pimage2 = self._pimage2
        new._image_size = self._image_size
        new._altered_image_size = self._altered_image_size
        new.rect = new._pimage.get_rect()
        new.display_list = self.display_list
        new.texture = self.texture
        new.offset = self.offset
        return new

    def _load_file(self):
        """Load an image file"""
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
        """Prepare a pygame.Surface object for 3d rendering"""
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
        """Compile the rendering data into a data.DisplayList"""
        self.offset = self.get_width()/2, self.get_height()/2

        self.display_list = data.DisplayList()
        self.display_list.begin()
        self.texture.bind()

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

        self.display_list.end()

    def sub_image(self, topleft, size):
        """Return a new Image3D object representing a smaller region of this Image3D."""
        image = self._pimage.subsurface(topleft, size)
        return Image3D(image, self.pos, self.rotation, self.scale, self.colorize)

def create_empty_image(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image instead"""
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return Image(i, colorize=color)

def create_empty_image3d(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image3D instead"""
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return Image3D(i, colorize=color)

class Animation(object):
    def __init__(self, frames=[], pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        self.frames = frames

        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize

        self.cur = 0
        self.ptime = time.time()
        self.running = True
        self.breakpoint = len(self.frames)-1
        self.startpoint = 0
        self.reversed = False
        self.looping = True

        self.visible = True
        self.filename = None

    def render(self, camera=None):
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                if self.reversed:
                    self.cur -= 1
                    if self.cur < self.startpoint:
                        if self.looping:
                            self.cur = self.breakpoint
                        else:
                            self.cur += 1
                else:
                    self.cur += 1
                    if self.cur >= self.breakpoint:
                        if self.looping:
                            self.cur = self.startpoint
                        else:
                            self.cur -= 1

                self.ptime = time.time()

        frame = self.current()
        frame.pos = self.pos
        frame.rotation = self.rotation
        frame.scale = self.scale
        frame.colorize = self.colorize
        frame.render(camera)

    def seek(self, num):
        self.cur = num
        if self.cur < 0:
            self.cur = 0
        if self.cur >= len(self.frames):
            self.cur = len(self.frames)-1

        self.ptime = time.time()

    def set_bounds(self, start, end):
        if start < 0:
            start = 0
        if start >= len(self.frames):
            start = len(self.frames) - 1
        if end < 0:
            end = 0
        if end >= len(self.frames):
            end = len(self.frames) - 1
        if end < start:
            end = start
        self.startpoint = start
        self.breakpoint = end

    def pause(self):
        self.running = False

    def play(self):
        self.running = True
        self.ptime = time.time()

    def rewind(self):
        self.seek(0)
        self.ptime = time.time()

    def fastforward(self):
        self.seek(self.length()-1)
        self.ptime = time.time()

    def get_width(self):
        return self.current().get_width()

    def get_height(self):
        return self.current().get_height()

    def get_size(self):
        return self.current().get_size()

    def length(self):
        return len(self.frames)

    def reverse(self):
        self.reversed = not self.reversed
    
    def reset(self):
        self.cur = 0
        self.ptime = time.time()
        self.reversed = False

    def loop(self, boolean=True):
        self.looping = boolean
        self.ptime = time.time()

    def copy(self):
        new = Animation(self.frames, self.pos, self.rotation, self.scale, self.colorize)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        return new

    def current(self):
        return self.frames[self.cur][0]

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        frame = self.current()
        frame.pos = self.pos
        return frame.get_rect()

    def clear_blits(self):
        """Remove all blits from all frames of the image"""
        for i in self.frames:
            i[0].to_be_blitted = []

    def remove_blit(self, image):
        """Remove all blits of image from the Image"""
        for frame in self.frames:
            frame = frame[0]
            for i in frame.to_be_blitted:
                if i[0] == image:
                    frame.to_be_blitted.remove(i)

    def sub_image(self, topleft, size):
        """Return a new Image object representing a smaller region of the current frame of this Image."""
        return self.current().sub_image(topleft, size)

    def blit(self, other, pos):
        """Blit another image to this one at pos offset - ONLY allowing an image to blitted once
           other is another image.Image
           pos is the x,y offset of the blit"""
        for frame in self.frames:
            frame = frame[0]
            frame.remove_blit(other)
            frame.to_be_blitted.append([other, pos])

    def blit_again(self, other, pos):
        """Same as blit, except you can blit the same image multiple times"""
        for frame in self.frames:
            frame = frame[0]
            frame.to_be_blitted.append([other, pos])

class Animation3D(Animation):
    def __init__(self, frames=[], pos=(0,0,0), rotation=(0,0,0),
                 scale=1, colorize=(1,1,1,1)):
        Animation.__init__(self, frames, pos, rotation, scale, colorize)

    def blit(self, *args, **kwargs):
        print "Animation3D does not support this function!"

    clear_blits = blit
    remove_blit = blit
    blit_again = blit
    test_on_screen = blit

    def get_dimensions(self):
        """Return a tuple of (1,1,1) signifying the 3d dimensions of teh image - used by the quad tree"""
        return 1, 1, 1

    def get_pos(self):
        """Return the position of the Image3D"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

def GIFImage(filename, pos=(0,0),
             rotation=(0,0,0), scale=1,
             colorize=(1,1,1,1)):
    view.require_init()
    image = pilImage.open(filename)

    frames = []

    pal = image.getpalette()
    base_palette = []
    for i in range(0, len(pal), 3):
        rgb = pal[i:i+3]
        base_palette.append(rgb)

    all_tiles = []
    try:
        while 1:
            if not image.tile:
                image.seek(0)
            if image.tile:
                all_tiles.append(image.tile[0][3][0])
            image.seek(image.tell()+1)
    except EOFError:
        image.seek(0)

    all_tiles = tuple(set(all_tiles))

    try:
        while 1:
            try:
                duration = image.info["duration"]
            except:
                duration = 100

            duration *= .001 #convert to milliseconds!
            cons = False

            x0, y0, x1, y1 = (0, 0) + image.size
            if image.tile:
                tile = image.tile
            else:
                image.seek(0)
                tile = image.tile
            if len(tile) > 0:
                x0, y0, x1, y1 = tile[0][1]

            if all_tiles:
                if all_tiles in ((6,), (7,)):
                    cons = True
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i+3]
                        palette.append(rgb)
                elif all_tiles in ((7, 8), (8, 7)):
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i+3]
                        palette.append(rgb)
                else:
                    palette = base_palette
            else:
                palette = base_palette

            pi = pygame.image.fromstring(image.tostring(), image.size, image.mode)
            pi.set_palette(palette)
            if "transparency" in image.info:
                pi.set_colorkey(image.info["transparency"])
            pi2 = pygame.Surface(image.size, SRCALPHA)
            if cons:
                for i in frames:
                    pi2.blit(i[0], (0,0))
            pi2.blit(pi, (x0, y0), (x0, y0, x1-x0, y1-y0))

            frames.append([pi2, duration])
            image.seek(image.tell()+1)
    except EOFError:
        pass

    new_frames = []
    for i in frames:
        new_frames.append([Image(i[0]), i[1]])
    return Animation(new_frames, pos, rotation, scale, colorize)

def GIFImage3D(filename, pos=(0,0,0),
             rotation=(0,0,0), scale=1,
             colorize=(1,1,1,1)):
    view.require_init()
    image = pilImage.open(filename)

    frames = []

    pal = image.getpalette()
    base_palette = []
    for i in range(0, len(pal), 3):
        rgb = pal[i:i+3]
        base_palette.append(rgb)

    all_tiles = []
    try:
        while 1:
            if not image.tile:
                image.seek(0)
            if image.tile:
                all_tiles.append(image.tile[0][3][0])
            image.seek(image.tell()+1)
    except EOFError:
        image.seek(0)

    all_tiles = tuple(set(all_tiles))

    try:
        while 1:
            try:
                duration = image.info["duration"]
            except:
                duration = 100

            duration *= .001 #convert to milliseconds!
            cons = False

            x0, y0, x1, y1 = (0, 0) + image.size
            if image.tile:
                tile = image.tile
            else:
                image.seek(0)
                tile = image.tile
            if len(tile) > 0:
                x0, y0, x1, y1 = tile[0][1]

            if all_tiles:
                if all_tiles in ((6,), (7,)):
                    cons = True
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i+3]
                        palette.append(rgb)
                elif all_tiles in ((7, 8), (8, 7)):
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i+3]
                        palette.append(rgb)
                else:
                    palette = base_palette
            else:
                palette = base_palette

            pi = pygame.image.fromstring(image.tostring(), image.size, image.mode)
            pi.set_palette(palette)
            if "transparency" in image.info:
                pi.set_colorkey(image.info["transparency"])
            pi2 = pygame.Surface(image.size, SRCALPHA)
            if cons:
                for i in frames:
                    pi2.blit(i[0], (0,0))
            pi2.blit(pi, (x0, y0), (x0, y0, x1-x0, y1-y0))

            frames.append([pi2, duration])
            image.seek(image.tell()+1)
    except EOFError:
        pass

    new_frames = []
    for i in frames:
        new_frames.append([Image3D(i[0]), i[1]])
    return Animation3D(new_frames, pos, rotation, scale, colorize)
