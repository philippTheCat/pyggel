"""
pyggel.data
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The data module holds all classes used to create, store and access OpenGL data,
like textures, display lists and vertex arrays.
"""

from include import *
import view

class Texture(object):
    """An object to load and store an OpenGL texture"""
    bound = None
    _all_loaded = {}
    def __init__(self, filename=None):
        """Create a texture
           filename can be be a filename for an image, or a pygame.Surface object"""
        view.require_init()
        self.filename = filename
        self.unique = False

        self.gl_tex = glGenTextures(1)

        self.size = (0,0)

        if type(filename) is type(""):
            self._load_file()
        else:
            self.filename = "UniqueTexture: %s"%self.gl_tex
            self.unique = True
            self._compile(filename)

    def _get_next_biggest(self, x, y):
        """Get the next biggest power of two x and y sizes"""
        if x == y == 1:
            return x, y
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        """Loads file"""
        if not self.filename in Texture._all_loaded:
            image = pygame.image.load(self.filename)

            self._compile(image)
            if self.filename:
                Texture._all_loaded[self.filename] = self.size, self.gl_tex
        else:
            self.size, self.gl_tex = Texture._all_loaded[self.filename]

    def _compile(self, image):
        """Compiles image data into texture data"""

        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", 1)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = size
        self.size = size
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

        if ANI_AVAILABLE:
            try:
                glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAX_ANISOTROPY_EXT,glGetFloat(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))
            except:
                pass

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def bind(self):
        """Binds the texture for usage"""
        if not Texture.bound == self.gl_tex:
            glBindTexture(GL_TEXTURE_2D, self.gl_tex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
            Texture.bound = self.gl_tex

    def release_gl(self):
        try:
            glDeleteTextures([self.gl_tex])
        except:
            pass

        try:
            del Texture._all_loaded[self.filename]
        except:
            pass

class ModifiableTexture(Texture):
    def __init__(self):
        view.require_init()

        self.gl_tex = glGenTextures(1)
        self.size = 0,0
        self.unique = True
        self.filename = "UniqueTexture: %s"%self.gl_tex

    def update_image(self, image):
        if type(image) is type(""):
            image = pygame.image.load(image)
        self._compile(image)


class BlankTexture(Texture):
    """A cached, blank texture."""
    _all_loaded = {}
    def __init__(self, size=(1,1), color=(1,1,1,1), unique=False):
        """Create an empty data.Texture
           size must be a two part tuple representing the pixel size of the texture
           color must be a four-part tuple representing the (RGBA 0-1) color of the texture
           unique controls whether this texture is cached and reused or not"""
        view.require_init() # It seems to need init on python2.6
        
        self.size = size
        self.filename = repr(size)+repr(color)
        self.gl_tex = None
        self.unique = unique
        if (not unique) and self.filename in BlankTexture._all_loaded:
            self.size, self.gl_tex = BlankTexture._all_loaded[self.filename]
        else:
            i = pygame.Surface(size)
            if len(color) == 4:
                r, g, b, a = color
            else:
                r, g, b = color
                a = 1
            r *= 255
            g *= 255
            b *= 255
            a *= 255
            i.fill((r,g,b,a))
            
            self.gl_tex = glGenTextures(1)
            self._compile(i)

            if not unique:
                BlankTexture._all_loaded[self.filename] = self.size, self.gl_tex

class DisplayList(object):
    """An object to compile and store an OpenGL display list"""
    def __init__(self):
        """Creat the list"""
        self.gl_list = glGenLists(1)

    def begin(self):
        """Begin recording to the list - anything rendered after this will be compiled into the list and not actually rendered"""
        glNewList(self.gl_list, GL_COMPILE)

    def end(self):
        """End recording"""
        glEndList()

    def render(self):
        """Render the display list"""
        glCallList(self.gl_list)

    def __del__(self):
        """Clear the display list data"""
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared!

class VertexArray(object):
    """An object to store and render an OpenGL vertex array of vertices, colors and texture coords"""
    def __init__(self, render_type=None, max_size=100):
        """Create the array
           render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
           max_size is the size of the array"""
        if render_type is None:
            render_type = GL_QUADS
        self.render_type = render_type
        self.texture = BlankTexture()

        self.max_size = max_size

        self.verts = numpy.zeros((max_size, 3), "f")
        self.colors = numpy.zeros((max_size, 4), "f")
        self.texcs = numpy.zeros((max_size, 2), "f")
        self.norms = numpy.array([[0,1,0]]*max_size, "f")

    def render(self):
        """Render the array"""
        self.texture.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointerf(self.verts)
        glColorPointerf(self.colors)
        glTexCoordPointerf(self.texcs)
        glNormalPointerf(self.norms)

        glDrawArrays(self.render_type, 0, self.max_size)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

    def reset_verts(self, data):
        self.verts = numpy.array(data, "f")
        self.max_size = len(data)

    def reset_colors(self, data):
        self.colors = numpy.array(data, "f")
        self.max_size = len(data)

    def reset_texcs(self, data):
        self.texcs = numpy.array(data, "f")
        self.max_size = len(data)

    def reset_norms(self, data):
        self.norms = numpy.array(data, "f")
        self.max_size = len(data)

    def update_verts(self, index, new):
        self.verts[index] = new

    def update_colors(self, index, new):
        self.colors[index] = new

    def update_texcs(self, index, new):
        self.texcs[index] = new

    def update_norms(self, index, new):
        self.norms[index] = new

    def resize(self, max_size):
        self.verts = numpy.resize(self.verts, (max_size, 3))
        self.colors = numpy.resize(self.colors, (max_size, 4))
        self.norms = numpy.resize(self.norms, (max_size, 3))
        self.texcs = numpy.resize(self.texcs, (max_size, 2))
        self.max_size = max_size

class VBOArray(object):
    def __init__(self, render_type=None, max_size=100, usage="static", cache_changes=False):
        """Create the array
           render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
           max_size is the size of the array
           usage can be static, dynamic or stream (affecting render vs. modify speeds)
           cache_changes makes any changes between renderings be stored,
               and then only one modification is performed.
               NOTE: doing this actually modifies the entire buffer data, just efficiently
                     so this is only recommended if you are modifying a tremendous amount of points each frame!"""

        if not VBO_AVAILABLE:
            raise AttributeError("Vertex buffer objects not available!")

        self.usage = ("GL_"+usage+"_DRAW").upper()
        uses = {"GL_STATIC_DRAW":GL_STATIC_DRAW,
                "GL_DYNAMIC_DRAW":GL_DYNAMIC_DRAW,
                "GL_STREAM_DRAW":GL_STREAM_DRAW}
        self.usage_gl = uses[self.usage]

        self.cache_changes = cache_changes
        self._cached_cv = []
        self._cached_cc = []
        self._cached_ct = []
        self._cached_cn = []

        if render_type is None:
            render_type = GL_QUADS
        self.render_type = render_type
        self.texture = BlankTexture()

        self.max_size = max_size

        self.verts = vbo.VBO(numpy.zeros((max_size, 3), "f"), self.usage)
        self.colors = vbo.VBO(numpy.zeros((max_size, 4), "f"), self.usage)
        self.texcs = vbo.VBO(numpy.zeros((max_size, 2), "f"), self.usage)
        self.norms = vbo.VBO(numpy.array([[0,1,0]]*max_size, "f"), self.usage)

    def render(self):
        """Render the array"""
        if self.cache_changes:
            if self._cached_cv or self._cached_cc or self._cached_ct:
                for i in self._cached_cv:
                    self.verts.data[i[0]] = i[1]
                self.verts.bind()
                glBufferData(GL_ARRAY_BUFFER, self.verts.data, self.usage_gl)
                self._cached_cv = []

                for i in self._cached_cc:
                    self.colors.data[i[0]] = i[1]
                self.colors.bind()
                glBufferData(GL_ARRAY_BUFFER, self.colors.data, self.usage_gl)
                self._cached_cc = []

                for i in self._cached_ct:
                    self.texcs.data[i[0]] = i[1]
                self.texcs.bind()
                glBufferData(GL_ARRAY_BUFFER, self.texcs.data, self.usage_gl)
                self._cached_ct = []

                for i in self._cached_cn:
                    self.norms.data[i[0]] = i[1]
                self.norms.bind()
                glBufferData(GL_ARRAY_BUFFER, self.norms.data, self.usage_gl)
                self._cached_cn = []
        self.texture.bind()

        self.verts.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(self.verts)

        self.colors.bind()
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointerf(self.colors)

        self.texcs.bind()
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointerf(self.texcs)

        self.norms.bind()
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointerf(self.norms)

        glDrawArrays(self.render_type, 0, self.max_size)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

    def reset_verts(self, data):
        self.verts.set_array(numpy.array(data, "f"))
        self.max_size = len(data)

    def reset_colors(self, data):
        self.colors.set_array(numpy.array(data, "f"))
        self.max_size = len(data)

    def reset_texcs(self, data):
        self.texcs.set_array(numpy.array(data, "f"))
        self.max_size = len(data)

    def reset_norms(self, data):
        self.norms.set_array(numpy.array(data, "f"))
        self.max_size = len(data)

    def update_verts(self, index, new):
        if self.cache_changes:
            self._cached_cv.append([index, new])
        else:
            self.verts.bind()
            #index multiplier is
            #4*len(new) - so since verts have 3 points, we get 12
            glBufferSubData(GL_ARRAY_BUFFER, 12*index, numpy.array(new, "f"))
            self.verts.data[index] = new

    def update_colors(self, index, new):
        if self.cache_changes:
            self._cached_cc.append([index, new])
        else:
            self.colors.bind()
            glBufferSubData(GL_ARRAY_BUFFER, 16*index, numpy.array(new, "f"))
            self.colors.data[index] = new

    def update_texcs(self, index, new):
        if self.cache_changes:
            self._cached_ct.append([index, new])
        else:
            self.texcs.bind()
            glBufferSubData(GL_ARRAY_BUFFER, 8*index, numpy.array(new, "f"))
            self.texcs.data[index] = new

    def update_norms(self, index, new):
        if self.cache_changes:
            self._cached_cn.append([index, new])
        else:
            self.norms.bind()
            glBufferSubData(GL_ARRAY_BUFFER, 12*index, numpy.array(new, "f"))
            self.norms.data[index] = new

    def __del__(self):
        bufs = []
        for i in (self.verts, self.colors, self.texcs, self.norms):
            try:
                i.delete()
            except:
                pass #pyggel.quit() was called and we can no longer access the functions!

    def resize(self, max_size):
        self.max_size = max_size
        d = numpy.resize(self.verts.data, (max_size, 3))
        self.verts.set_array(d)

        d = numpy.resize(self.colors.data, (max_size, 4))
        self.colors.set_array(d)

        d = numpy.resize(self.texcs.data, (max_size, 2))
        self.texcs.set_array(d)

        d = numpy.resize(self.norms.data, (max_size, 3))
        self.norms.set_array(d)

def get_best_array_type(render_type=None, max_size=10,
                        opt=0):
    """This function returns the best possible array type for what you need.
       render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
       max_size is the number of individual points in the array
       opt is how the array is optimized, starting at 0 for fast access to 5 for fast rendering
           5 also makes use of a cached VBO (if possible) - so it is very fast rendering and modifying
           *if* you are modifying a very large number of points - otherwise it is slower at modifying"""

    assert opt >= 0 and opt <= 5

    if not VBO_AVAILABLE:
        return VertexArray(render_type, max_size)

    if opt == 0:
        return VertexArray(render_type, max_size)
    elif opt == 1:
        return VBOArray(render_type, max_size, "stream")
    elif opt == 2:
        return VBOArray(render_type, max_size, "dynamic")
    elif opt == 3:
        return VBOArray(render_type, max_size, "static")
    else:
        return VBOArray(render_type, max_size, "static", True)

class FrameBuffer(object):
    """An object contains functions to render to a texture instead of to the main display.
       This object renders using FBO's, which are not available to everyone, but they are far faster and more versatile."""
    def __init__(self, size=(512,512), clear_color=(0,0,0,0)):
        """Create the FrameBuffer.
           size must be the (x,y) size of the buffer, will round up to the next power of two
           clear_color must be the (r,g,b) or (r,g,b,a) color of the background of the texture"""
        view.require_init()
        if not (FBO_AVAILABLE and bool(glGenRenderbuffersEXT)):
            raise AttributeError("Frame buffer objects not available!")

        _x, _y = size
        x = y = 2
        while x < _x:
            x *= 2
        while y < _y:
            y *= 2
        size = x, y

        self.size = size
        self.clear_color = clear_color

        self.texture = BlankTexture(self.size, self.clear_color)

        self.rbuffer = glGenRenderbuffersEXT(1)
        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT,
                              self.rbuffer)
        glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT,
                                 GL_DEPTH_COMPONENT,
                                 size[0],
                                 size[1])

        self.fbuffer = glGenFramebuffersEXT(1)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT,
                             self.fbuffer)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT,
                                  GL_COLOR_ATTACHMENT0_EXT,
                                  GL_TEXTURE_2D,
                                  self.texture.gl_tex,
                                  0)
        glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT,
                                     GL_DEPTH_ATTACHMENT_EXT,
                                     GL_RENDERBUFFER_EXT,
                                     self.rbuffer)

        self.worked = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT) == GL_FRAMEBUFFER_COMPLETE_EXT

        glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, 0)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

    def enable(self):
        """Turn this buffer on, swaps rendering to the texture instead of the display."""
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbuffer)
        r,g,b = self.clear_color[:3]
        glClearColor(r, g, b, 1)
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

        glPushAttrib(GL_VIEWPORT_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*self.size)
        gluPerspective(45, 1.0*self.size[0]/self.size[1], 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        
    def disable(self):
        """Turn off the buffer, swap rendering back to the display."""
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
        glClearColor(*view.screen.clear_color)
        glPopAttrib()

    def __del__(self):
        """Clean up..."""
        try:
            glDeleteFramebuffersEXT(1, [self.fbuffer])
        except:
            pass

        try:
            glDeleteRenderbuffersEXT(1, [self.rbuffer])
        except:
            pass

class TextureBuffer(object):
    """An object contains functions to render to a texture, using the main display.
       This object renders using the main display, copying to the texture, and then clearing.
       This object is considerably slower than teh FrameBuffer object, and less versatile,
       because you cannot use these objects mid-render, if you do you will lose whatever was rendered before them!"""
    def __init__(self, size=(512,512), clear_color=(0,0,0,0)):
        """Create the FrameBuffer.
           size must be the (x,y) size of the buffer, will round up to the next power of two
               if size is greater than the display size, it will be rounded down to the previous power of two
           clear_color must be the (r,g,b) or (r,g,b,a) color of the background of the texture"""
        _x, _y = size
        x = y = 2
        while x < _x:
            x *= 2
        while y < _y:
            y *= 2
        while x > view.screen.screen_size[0]:
            x /= 2
        while y > view.screen.screen_size[1]:
            y /= 2
        size = x, y

        self.size = size
        self.clear_color = clear_color

        self.texture = BlankTexture(self.size, self.clear_color)
        self.worked = True

    def enable(self):
        """Turn on rendering to this buffer, clears display buffer and preps it for this object."""
        r,g,b = self.clear_color[:3]

        glClearColor(r, g, b, 1)
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)
        glClearColor(*view.screen.clear_color)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*self.size)
        gluPerspective(45, 1.0*self.size[0]/self.size[1], 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)

    def disable(self):
        """Turn of this buffer, and clear the display."""
        self.texture.bind()
        glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 0,0,self.size[0], self.size[1], 0)

        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

def RenderBuffer(*args, **kwargs):
    """Returns FrameBuffer if available, or texture buffer if not."""
    if FBO_AVAILABLE:
        return FrameBuffer(*args, **kwargs)
    return TextureBuffer(*args, **kwargs)

class Material(object):
    """A simple class to store a color and texture for an object."""
    def __init__(self, name):
        """Create the material
           name is the name of the material"""
        self.name = name
        self.color = (1,1,1,1)
        self.texture = BlankTexture()

    def set_color(self, color):
        """Set color of material."""
        if len(color) == 3:
            color += (1,)
        self.color = color

    def copy(self):
        """Copy material."""
        a = Material(self.name)
        a.color = self.color
        a.texture = self.texture
        return a
