"""
pyggel.image
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The image module contains classes to load and render both 2d and 3d (billboarded) images.
"""
import time

from include import *

import view, data, misc

from scene import BaseSceneObject

class Image(BaseSceneObject):
    """A 2d image object"""
    def __init__(self, filename, pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=(1,1,1,1)):
        """Create the Image
           filename must be a filename to an image file, a pygame.Surface object or an image.Image to copy
           pos is the 2d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        BaseSceneObject.__init__(self)

        if isinstance(filename, data.Texture):
            self.filename = filename.filename
            self.texture = filename
        else:
            self.filename = filename
            self.texture = data.Texture(filename)

        self._compile()

        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize

    def test_on_screen(self):
        """Return whether the image is onscreen or not"""
        return view.screen.rect2d.colliderect(self.get_rect())

    def copy(self):
        """Return a copy of the image"""
        return Image(self.texture, self.pos, self.rotation, self.scale, self.colorize)

    def _compile(self):
        """Compile the Image into a data.DisplayList"""
        off = self.get_width()/2.0, self.get_height()/2.0

        self.display_list = data.DisplayList()
        self.display_list.begin()

        l = -off[0]
        r = off[0]
        t = -off[1]
        b = off[1]

        w, h = self.texture.size_mult

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(l, t, 0)

        glTexCoord2f(0, h)
        glVertex3f(l, b, 0)

        glTexCoord2f(w, h)
        glVertex3f(r, b, 0)

        glTexCoord2f(w, 0)
        glVertex3f(r, t, 0)

        glEnd()

        self.display_list.end()

    def render(self, camera=None):
        """Render the image
           camera can be None or the camera the scene is using"""
        if not self.test_on_screen():
            return None

        ox, oy = self.get_width()/2.0, self.get_height()/2.0

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
        self.texture.bind()
        self.display_list.render()
        glPopMatrix()

    def get_width(self):
        """Return the width in pixels of the image"""
        return self.texture.size[0]

    def get_height(self):
        """Return the height in pixels of the image"""
        return self.texture.size[1]

    def get_size(self):
        """Return the width/height size of the image"""
        return self.texture.size

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        return pygame.Rect(self.pos, self.texture.size)

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
           colorize is the color of the image"""
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
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size, True)
        self.display_list.render()
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        glPopMatrix()

    def test_on_screen(self, *args, **kwargs):
        print "Image3D does not support this function!"

    def copy(self):
        """Return a copy of the Image3D"""
        return Image3D(self.filename, self.pos, self.rotation, self.scale, self.colorize)

    def _compile(self):
        """Compile the rendering data into a data.DisplayList"""
        off = self.get_width()/2, self.get_height()/2

        self.display_list = data.DisplayList()
        self.display_list.begin()

        w, h = self.texture.size_mult

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

def create_empty_image(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image instead"""
    view.require_init()
    i = data.Texture(fill_size=size, fill_color=color, fill_unique=True)
    return Image(i)

def create_empty_image3d(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image3D instead"""
    view.require_init()
    i = data.Texture(fill_size=size, fill_color=color, fill_unique=True)
    return Image3D(i)

class Animation(BaseSceneObject):
    """A simple object used to store, manipulate, animate and render a bunch of frames of 2d Image obejcts."""
    def __init__(self, frames=[], pos=(0,0),
                 rotation=(0,0,0), scale=1,
                 colorize=None):
        """Create the Animation
           frames must be a list/tuple of [Image, duration] objects
           pos is the 2d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        BaseSceneObject.__init__(self)

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

        self.filename = None

    def render(self, camera=None):
        """Render the animation - this also keeps track of swapping frames when they have run for their duration.
           camera must be None or the camera.Camera object used to render the scene."""
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
                    if self.cur > self.breakpoint:
                        if self.looping:
                            self.cur = self.startpoint
                        else:
                            self.cur -= 1

                self.ptime = time.time()

        frame = self.current()
        frame.pos = self.pos
        frame.rotation = self.rotation
        frame.scale = self.scale
        if self.colorize:
            frame.colorize = self.colorize
        frame.render(camera)

    def seek(self, num):
        """'Jump' to a specific frame in the animation."""
        self.cur = num
        if self.cur < 0:
            self.cur = 0
        if self.cur >= len(self.frames):
            self.cur = len(self.frames)-1

        self.ptime = time.time()

    def set_bounds(self, start, end):
        """Set the start/end 'bounds' for playback, ie which range of frames to play."""
        if start < 0:
            start = 0
        if start >= len(self.frames):
            start = len(self.frames)-1
        if end < 0:
            end = 0
        if end >= len(self.frames):
            end = len(self.frames)-1
        if end < start:
            end = start
        self.startpoint = start
        self.breakpoint = end

    def pause(self):
        """Pause the running of the animation, and locks rendering to the current frame."""
        self.running = False

    def play(self):
        """Play the animation - only needed if pause has been called."""
        self.running = True
        self.ptime = time.time()

    def rewind(self):
        """Rewind the playback to first frame."""
        self.seek(0)

    def fastforward(self):
        """Fast forward playback to the last frame."""
        self.seek(self.length()-1)

    def get_width(self):
        """Return the width of the image."""
        return self.current().get_width()

    def get_height(self):
        """Return the height of the image."""
        return self.current().get_height()

    def get_size(self):
        """Return the width/height size of the image."""
        return self.current().get_size()

    def length(self):
        """Return the number of frames of the animation."""
        return len(self.frames)

    def reverse(self):
        """Reverse the playback of the image animation."""
        self.reversed = not self.reversed
    
    def reset(self):
        """Reset the image playback."""
        self.cur = 0
        self.ptime = time.time()
        self.reversed = False

    def loop(self, boolean=True):
        """Set looping of playback on/off - if looping is off animation will continue until the last frame and freeze."""
        self.looping = boolean
        self.ptime = time.time()

    def copy(self):
        """Return a copy of this Animation. Frames are shared..."""
        new = Animation(self.frames, self.pos, self.rotation, self.scale, self.colorize)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        new.looping = self.looping
        return new

    def current(self):
        """Return the current frame Image."""
        return self.frames[self.cur][0]

    def get_rect(self):
        """Return a pygame.Rect of the image"""
        frame = self.current()
        frame.pos = self.pos
        return frame.get_rect()

class Animation3D(Animation):
    """3D version of Animation."""
    def __init__(self, frames=[], pos=(0,0,0), rotation=(0,0,0),
                 scale=1, colorize=(1,1,1,1)):
        """Create the Animation3D
           frames must be a list/tuple of [frame, duration] objects
           pos is the 3d position of the image
           rotation is the 3d rotation of the image
           scale is the scale factor for the image
           colorize is the color of the image"""
        Animation.__init__(self, frames, pos, rotation, scale, colorize)

    def test_on_screen(self, *args, **kwargs):
        print "Animation3D does not support this function!"

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

    def copy(self):
        """Return a copy of this Animation. Frames are shared..."""
        new = Animation3D(self.frames, self.pos, self.rotation, self.scale, self.colorize)
        new.running = self.running
        new.breakpoint = self.breakpoint
        new.startpoint = self.startpoint
        new.cur = self.cur
        new.ptime = self.ptime
        new.reversed = self.reversed
        return new

def GIFImage(filename, pos=(0,0),
             rotation=(0,0,0), scale=1,
             colorize=(1,1,1,1)):
    """Load a GIF image into an Animation object if PIL is available, otherwise falls back to a static Image.
       filename must be the name of a gif image one disk
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    if not PIL_AVAILABLE:
        return Image(filename, pos, rotation, scale, colorize)
    image = PIL.open(filename)

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
    """Load a GIF image into an Animation3D object.
       filename must be the name of a gif image one disk
       pos is the 3d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    if not PIL_AVAILABLE:
        return Image3D(filename, pos, rotation, scale, colorize)
    image = PIL.open(filename)

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

def SpriteSheet(filename, frames=[], durations=100,
                pos=(0,0), rotation=(0,0,0), scale=1,
                colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of [x,y,width,height] portions of the image that are unique frames
       durations must be a number or list/tuple of numbers representing the duration (in milliseconds) of all/each frame
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    if type(durations) in [type(1), type(1.2)]:
        durations = [durations]*len(frames)
    new = []
    image = pygame.image.load(filename).convert_alpha()

    for (frame, dur) in zip(frames, durations):
        new.append([Image(image.subsurface(*frame)), dur*0.001])

    return Animation(new, pos, rotation, scale, colorize)


def SpriteSheet3D(filename, frames=[], durations=[],
                  pos=(0,0), rotation=(0,0,0), scale=1,
                  colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation3D object.
       filename must be the name of an image on disk
       frames must be a tuple/list of [x,y,width,height] portions of the image that are unique frames
       durations must be a number or list/tuple of numbers representing the duration (in milliseconds) of all/each frame
       pos is the 3d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    if type(durations) in [type(1), type(1.2)]:
        durations = [durations]*len(frames)
    new = []
    image = pygame.image.load(filename).convert_alpha()

    for (frame, dur) in zip(frames, durations):
        new.append([Image3D(image.subsurface(*frame)), dur*0.001])

    return Animation3D(new, pos, rotation, scale, colorize)

def GridSpriteSheet(filename, frames=(1,1), duration=100,
                    pos=(0,0), rotation=(0,0,0), scale=1,
                    colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of two ints, indicating the number of frames in the x/y axis
       duration must be a number representing the duration (in milliseconds) of all frames
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    new = []

    image = pygame.image.load(filename).convert_alpha()

    x_size = int(image.get_width() / frames[0])
    y_size = int(image.get_height() / frames[1])

    for x in xrange(frames[0]):
        for y in xrange(frames[1]):
            new.append([Image(image.subsurface(x*x_size, y*y_size, x_size, y_size)),
                        duration*0.001])
    return Animation(new, pos, rotation, scale, colorize)

def GridSpriteSheet3D(filename, frames=(1,1), duration=100,
                    pos=(0,0,0), rotation=(0,0,0), scale=1,
                    colorize=(1,1,1,1)):
    """Load a "spritesheet" (basically, a flat 2d image that holds a lot of different images) into an Animation object.
       filename must be the name of an image on disk
       frames must be a tuple/list of two ints, indicating the number of frames in the x/y axis
       duration must be a number representing the duration (in milliseconds) of all frames
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor for the image
       colorize is the color of the image"""
    view.require_init()
    new = []

    image = pygame.image.load(filename).convert_alpha()

    x_size = int(image.get_width() / frames[0])
    y_size = int(image.get_height() / frames[1])

    for x in xrange(frames[0]):
        for y in xrange(frames[1]):
            new.append([Image3D(image.subsurface(x*x_size, y*y_size, x_size, y_size)),
                        duration*0.001])
    return Animation3D(new, pos, rotation, scale, colorize)

def load_and_tile_resize_image(filename, size, pos=(0,0),
                               rotation=(0,0,0), scale=1,
                               colorize=(1,1,1,1), border_size=None):
    """Load an image, resize it by tiling
           (ie, each image is 9 tiles, and then the parts are scaled so that it fits or greator than size)
       filename must be the filename of the image to load
       size must be the (x, y) size of the image (may be larger)
       pos is the 2d position of the image
       rotation is the 3d rotation of the image
       scale is the scale factor of the image
       colorize is the color of the image
       Returns Image, tile_size"""
    view.require_init()
    image = pygame.image.load(filename).convert_alpha()
    x, y = size
    if x < image.get_width(): x = image.get_width()
    if y < image.get_height(): y = image.get_height()
    size = x, y
    if border_size:
        if border_size > int(min(image.get_size())/3):
            border_size = int(min(image.get_size())/3)
        x1=min((border_size, int(image.get_width()/3)))
        y1=min((border_size, int(image.get_height()/3)))
        x2 = image.get_width()-x1*2
        y2 = image.get_height()-y1*2
    else:
        x1=x2=int(image.get_width()/3)
        y1=y2=int(image.get_height()/3)

    topleft = image.subsurface((0, 0), (x1, y1))
    top = pygame.transform.scale(image.subsurface((x1, 0), (x2, y1)), (size[0]-x1*2, y1))
    topright = image.subsurface((x1+x2, 0), (x1,y1))

    left = pygame.transform.scale(image.subsurface((0, y1), (x1, y2)), (x1, size[1]-y1*2))
    middle = pygame.transform.scale(image.subsurface((x1, y1), (x2,y2)), (size[0]-x1*2, size[1]-y1*2))
    right = pygame.transform.scale(image.subsurface((x1+x2, y1), (x1,y2)), (x1, size[1]-y1*2))

    botleft = image.subsurface((0, y1+y2), (x1,y1))
    bottom = pygame.transform.scale(image.subsurface((x1, y1+y2), (x2, y1)), (size[0]-x1*2, y1))
    botright = image.subsurface((x1+y1, y1+y2), (x1,y1))

    new = pygame.Surface(size).convert_alpha()
    new.fill((0,0,0,0))
    new.blit(topleft, (0, 0))
    new.blit(top, (x1, 0))
    new.blit(topright, (size[0]-x1, 0))

    new.blit(left, (0, y1))
    new.blit(middle, (x1,y1))
    new.blit(right, (size[0]-x1, y1))

    new.blit(botleft, (0, size[1]-y1))
    new.blit(bottom, (x1, size[1]-y1))
    new.blit(botright, (size[0]-x1, size[1]-y1))
    return Image(new, pos, rotation, scale, colorize), (x1,y1)
