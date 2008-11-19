from include import *
import image

class Cube(object):
    def __init__(self, size, pos=(0,0,0), color=(1,1,1,1),
                 texture=None, interpolate=True):
        self.size = size
        self.pos = pos
        if not texture:
            texture = blank_texture
        self.texture = texture
        self.color = color

        self.corners = ((-1, -1, 1),#topleftfront
                      (1, -1, 1),#toprightfront
                      (1, 1, 1),#bottomrightfront
                      (-1, 1, 1),#bottomleftfront
                      (-1, -1, -1),#topleftback
                      (1, -1, -1),#toprightback
                      (1, 1, -1),#bottomrightback
                      (-1, 1, -1))#bottomleftback
        self.sides = ((3,0,1,2, 0, 1),#front
                      (7,4,5,6, 1, 3),#back
                      (7,4,0,3, 2, 2),#left
                      (6,5,1,2, 3, 4),#right
                      (1,5,4,0, 4, 5),#bottom
                      (6,2,3,7, 5, 0))#top

        self.split_coords = ((2,0),#top
                             (0,1),#back
                             (1,1),#left
                             (2,1),#front
                             (3,1),#right
                             (2,2))#bottom

        self.gl_list = glGenLists(1)

        self._compile(interpolate)

    def _compile(self, inter):
        if inter: inter = GL_LINEAR
        else: inter = GL_NEAREST
        glNewList(self.gl_list, GL_COMPILE)
        if isinstance(self.texture, image.Texture):
            self.texture.bind()
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, inter)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, inter)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            reg_type = 0
        else:
            reg_type = 1

        ox = .25
        oy = .33
        for i in self.sides:
            ix = 0
            x, y = self.split_coords[i[5]]
            x *= ox
            y *= oy
            if reg_type == 0:
                coords = ((x, y), (x, y+oy), (x+ox, y+oy), (x+ox, y))
            else:
                coords = ((0,0), (0,1), (1,1), (1,0))
                self.texture[i[4]].bind()
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, inter)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, inter)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

            print coords

            glBegin(GL_QUADS)

            for x in i[:4]:
                glTexCoord2fv(coords[ix])
                a, b, c = self.corners[x]
                a *= 1.1
                b *= 1.1
                c *= 1.1
                glVertex3f(a,b,c)
                ix += 1
            glEnd()
        glEndList()

    def render(self, camera=None):
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(.5*self.size,.5*self.size,.5*self.size)
        glColor4f(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()

    def copy(self):
        n = Cube(self.size, self.pos, self.color, self.texture)
        glDeleteTextures(n.gl_list)
        n.gl_list = self.gl_list
        return n

class Skybox(Cube):
    def __init__(self, texture, colorize=(1,1,1,1)):
        Cube.__init__(self, 1, color=colorize, texture=texture)
        self.sides = ((2,1,0,3, 0, 1),#front
                      (7,4,5,6, 1, 3),#back
                      (3,0,4,7, 2, 2),#left
                      (6,5,1,2, 3, 4),#right
                      (4,0,1,5, 4, 5),#bottom
                      (3,7,6,2, 5, 0))#top
        self._compile(False)

    def render(self, camera):
        glDepthMask(GL_FALSE)
        glPushMatrix()
        camera.set_skybox_data()
        Cube.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)

class Sphere(object):
    def __init__(self, size, pos=(0,0,0), color=(1,1,1,1),
                 texture=None, detail=30):
        self.size = size
        self.pos = pos
        self.color = color
        if not texture:
            texture = blank_texture
        self.texture = texture
        self.detail = detail

        self.gl_list = glGenLists(1)

        self._compile()

    def _compile(self):
        glNewList(self.gl_list, GL_COMPILE)
        self.texture.bind()
        Sphere = gluNewQuadric()
        gluQuadricTexture(Sphere, GLU_TRUE)
        gluSphere(Sphere, self.size, self.detail, self.detail)
        glEndList()

    def render(self, camera=None):
        glPushMatrix()
        glTranslatef(*self.pos)
        glColor4f(*self.color)
        glCallList(self.gl_list)
        glPopMatrix()

class Skyball(Sphere):
    def __init__(self, texture=None, colorize=(1,1,1,1), detail=30):
        Sphere.__init__(self, 1, color=colorize,
                        texture=texture, detail=detail)

    def render(self, camera):
        glDepthMask(GL_FALSE)
        glPushMatrix()
        camera.set_skybox_data()
        glRotatef(90, 1, 0, 0)
        Sphere.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)
