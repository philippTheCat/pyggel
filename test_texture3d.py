import pyggel
from pyggel import *

class Texture3D(pyggel.data.Texture):
    """An object to load and store an OpenGL texture"""
    bound = None
    _all_loaded_3d = {}
    def __init__(self, filename=None):
        """Create a texture
           filename can be be a filename for an image, or a pygame.Surface object"""
        pyggel.data.Texture.__init__(self, filename)

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
        if not self.filename in self._all_loaded_3d:
            image = pygame.image.load(self.filename)

            self._compile(image)
            if self.filename:
                self._all_loaded_3d[self.filename] = [self]
        else:
            tex = self._all_loaded_3d[self.filename][0]

            self.size = tex.size
            self.gl_tex = tex.gl_tex
            self._all_loaded_3d[self.filename].append(self)

    def _compile(self, image):
        """Compiles image data into texture data"""

        self.gl_tex = glGenTextures(1)

        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", 1)
        
        glBindTexture(GL_TEXTURE_3D, self.gl_tex)

        xx, xy = size
        xz = 8
        self.size = size
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA, xx, xy, xz, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata*xz)

        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def bind(self):
        """Binds the texture for usage"""
        if not pyggel.data.Texture.bound == self:
            glBindTexture(GL_TEXTURE_3D, self.gl_tex)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
            pyggel.data.Texture.bound = self

    def __del__(self):
        """Clear the texture data"""
        if self.filename in self._all_loaded_3d and\
           self in self._all_loaded_3d[self.filename]:
            self._all_loaded_3d[self.filename].remove(self)
            if not self._all_loaded_3d[self.filename]:
                del self._all_loaded_3d[self.filename]
                try:
                    glDeleteTextures([self.gl_tex])
                except:
                    pass #already cleared...

class Cube(pyggel.scene.BaseSceneObject):
    """A geometric cube that can be colored and textured"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, mirror=True):
        """Create a cube
           size is the absolute size of the cube
           pos is the position of the cube
           rotation is the rotation of the cube
           colorize is the color of the cube (0-1 RGBA)
           texture can be None, a data.Texture object or a string representing the filename of a texture to load
           mirror indicates whether each face of the cube has the full texture on it (so each is identicle) or
               if True, each face will have the entire texture mapped to it
               if False, the Texture is considered a cube map, like this:
                   blank, blank, top, blank,
                   back, left, front, right,
                   blank, blank, bottom, blank"""
        pyggel.scene.BaseSceneObject.__init__(self)

        self.size = size
        self.pos = pos
        self.rotation = rotation
        if type(texture) is type(""):
            texture = Texture(texture)
        if texture:
            self.texture = texture
        self.colorize = colorize

        self.mirror = mirror

        self.corners = ((-1, -1, 1),#topleftfront
                      (1, -1, 1),#toprightfront
                      (1, 1, 1),#bottomrightfront
                      (-1, 1, 1),#bottomleftfront
                      (-1, -1, -1),#topleftback
                      (1, -1, -1),#toprightback
                      (1, 1, -1),#bottomrightback
                      (-1, 1, -1))#bottomleftback

        self.sides = ((7,4,0,3, 2, 2, 5),#left
                      (2,1,5,6, 3, 4, 4),#right
                      (7,3,2,6, 5, 0, 3),#top
                      (0,4,5,1, 4, 5, 2),#bottom
                      (3,0,1,2, 0, 1, 0),#front
                      (6,5,4,7, 1, 3, 1))#back
        self.normals = ((0, 0, 1), #front
                        (0, 0, -1), #back
                        (0, -1, 0), #top
                        (0, 1, 0), #bottom
                        (1, 0, 0), #right
                        (-1, 0, 0)) #left

        self.split_coords = ((2,2),#top
                             (0,1),#back
                             (1,1),#left
                             (2,1),#front
                             (3,1),#right
                             (2,0))#bottom

        self.scale = 1

        self.display_list = data.DisplayList()

        self._compile()

    def get_dimensions(self):
        """Return a tuple of the size of the cube - to be used by the quad tree and collision testing"""
        return self.size, self.size, self.size

    def get_pos(self):
        """Return the position of the quad"""
        return self.pos

    def _compile(self):
        """Compile the cube's rendering into a data.DisplayList"""
        self.display_list.begin()

        if isinstance(self.texture, Texture3D):
            tex3 = True
        else:
            tex3 = False

        ox = .25
        oy = .33
        last_tex = None
        for i in self.sides:
            ix = 0
            x, y = self.split_coords[i[5]]
            x *= ox
            y *= oy
            if self.mirror:
                coords = ((1,1), (1,0), (0,0), (0,1))
            else:
                coords = ((x+ox, y+oy), (x+ox, y), (x, y), (x, y+oy))


            glBegin(GL_QUADS)

            glNormal3f(*self.normals[i[6]])

            for x in i[:4]:
                ifglTexCoord2fv(coords[ix])
                a, b, c = self.corners[x]
                glVertex3f(a,b,c)
                ix += 1
            glEnd()
        self.display_list.end()

    def render(self, camera=None):
        """Render the cube
           camera is None or the camera object the scene is using to render this object"""
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glScalef(.5*self.size,.5*self.size,.5*self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size)
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        """Return a copy of the quad - uses the same display list"""
        n = Cube(self.size, self.pos, self.rotation, self.colorize, self.texture)
        n.display_list = self.display_list
        n.scale = self.scale
        return n

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

def main():
    pyggel.view.init(screen_size=(800,600), screen_size_2d=(640, 480))
    pyggel.view.set_debug(False)

    glEnable(GL_TEXTURE_3D)
    glDisable(GL_CULL_FACE)

    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    img = pyggel.image.Image("data/tile_example.png", pos=(50, 50))

    test = Tex3DRenderable(Texture3D("data/tile_example.png"))

    my_scene = pyggel.scene.Scene()
    my_scene.add_2d(img)
    my_scene.add_3d(test)

    my_scene.add_light(my_light)

    clock = pygame.time.Clock()

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        meh.update()

        if meh.quit:
            pyggel.quit()
            return None

        camera.roty += .5

        pyggel.view.clear_screen()

        my_scene.render(camera)

        pyggel.view.refresh_screen()
main()
