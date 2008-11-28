"""
pyggle.geometry
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import view, data

class Cube(object):
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None):
        view.require_init()
        self.size = size
        self.pos = pos
        self.rotation = rotation
        if not texture:
            texture = blank_texture
        self.texture = texture
        self.colorize = colorize

        self.corners = ((-1, -1, 1),#topleftfront
                      (1, -1, 1),#toprightfront
                      (1, 1, 1),#bottomrightfront
                      (-1, 1, 1),#bottomleftfront
                      (-1, -1, -1),#topleftback
                      (1, -1, -1),#toprightback
                      (1, 1, -1),#bottomrightback
                      (-1, 1, -1))#bottomleftback

        self.sides = ((7,4,0,3, 2, 2, 5),#left
                      (6,5,1,2, 3, 4, 4),#right
                      (6,2,3,7, 5, 0, 2),#top
                      (1,5,4,0, 4, 5, 3),#bottom
                      (3,0,1,2, 0, 1, 0),#front
                      (7,4,5,6, 1, 3, 1))#back
        self.normals = ((0, 0, 1), #front
                        (0, 0, -1), #back
                        (0, 1, 0), #top
                        (0, -1, 0), #bottom
                        (1, 0, 0), #right
                        (-1, 0, 0)) #left

        self.split_coords = ((2,0),#top
                             (0,1),#back
                             (1,1),#left
                             (2,1),#front
                             (3,1),#right
                             (2,2))#bottom

        self.scale = 1

        self.display_list = data.DisplayList()

        self.visible = True

        self._compile()

    def get_dimensions(self):
        return self.size, self.size, self.size

    def get_pos(self):
        return self.pos

    def _compile(self):
        self.display_list.begin()
        if isinstance(self.texture, data.Texture):
            self.texture.bind()
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

            glBegin(GL_QUADS)

            glNormal3f(*self.normals[i[6]])

            for x in i[:4]:
                glTexCoord2fv(coords[ix])
                a, b, c = self.corners[x]
                a *= 1.1
                b *= 1.1
                c *= 1.1
                glVertex3f(a,b,c)
                ix += 1
            glEnd()
        self.display_list.end()

    def render(self, camera=None):
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
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        n = Cube(self.size, self.pos, self.rotation, self.color, self.texture)
        n.display_list = self.display_list
        n.scale = self.scale
        return n

class Quad(Cube):
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, facing=0):

        f = {"left":0,
             "right":1,
             "top":2,
             "bottom":3,
             "front":4,
             "back":5}
        if type(facing) is type(""):
            facing = f[facing]
        self.facing = facing

        self.xnorms = [1,0,3,2,5,4]

        Cube.__init__(self, size, pos, rotation, colorize, texture)

    def _compile(self):
        self.display_list.begin()
        self.texture.bind()

        ox = .25
        oy = .33
        i = self.sides[self.facing]
        ix = 0
        x, y = self.split_coords[i[5]]
        x *= ox
        y *= oy

        glBegin(GL_QUADS)
        coords = ((0,0), (0,1), (1,1), (1,0))

        glNormal3f(*self.normals[self.xnorms[i[6]]])

        for x in i[:4]:
            glTexCoord2fv(coords[ix])
            a, b, c = self.corners[x]
            a *= 1.1
            b *= 1.1
            c *= 1.1
            glVertex3f(a,b,c)
            ix += 1
        glEnd()
        self.display_list.end()

    def copy(self):
        n = Quad(self.size, self.pos, self.rotation, self.colorize, self.texture, self.facing)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Plane(Quad):
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, facing=0,
                 tile=1):

        f = {"left":0,
             "right":1,
             "top":2,
             "bottom":3,
             "front":4,
             "back":5}
        if type(facing) is type(""):
            facing = f[facing]
        self.facing = facing

        self.xnorms = [1,0,3,2,5,4]
        self.tile = tile

        Quad.__init__(self, size, pos, rotation, colorize, texture, facing)

    def _compile(self):
        self.display_list.begin()
        self.texture.bind()

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_REPEAT)

        ox = .25
        oy = .33
        i = self.sides[self.facing]
        ix = 0
        x, y = self.split_coords[i[5]]
        x *= ox
        y *= oy

        glBegin(GL_QUADS)
        coords = ((0,0), (0,self.tile),
                  (self.tile,self.tile),
                  (self.tile,0))

        glNormal3f(*self.normals[self.xnorms[i[6]]])

        for x in i[:4]:
            glTexCoord2fv(coords[ix])
            a, b, c = self.corners[x]
            a *= 1.1
            b *= 1.1
            c *= 1.1
            glVertex3f(a,b,c)
            ix += 1
        glEnd()
        self.display_list.end()

    def render(self, camera=None):
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        s = self.size / self.tile if (self.size and self.tile) else self.size
        glScalef(.5*self.size,.5*s,.5*self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        n = Plane(self.size, self.pos, self.rotation, self.colorize, self.texture, self.facing, self.tile)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Skybox(Cube):
    def __init__(self, texture, colorize=(1,1,1,1)):
        Cube.__init__(self, 1, colorize=colorize, texture=texture)
        self.sides = ((3,0,4,7, 2, 2, 5),#left
                      (6,5,1,2, 3, 4, 4),#right
                      (3,7,6,2, 5, 0, 2),#top
                      (4,0,1,5, 4, 5, 3),#bottom
                      (2,1,0,3, 0, 1, 0),#front
                      (7,4,5,6, 1, 3, 1))#back
        self._compile()

    def render(self, camera):
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glPushMatrix()
        camera.set_skybox_data()
        Cube.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)
        if view.screen.lighting:
            glEnable(GL_LIGHTING)

    def copy(self):
        n = Skybox(self.texture, self.colorize)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Sphere(object):
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, detail=30):
        view.require_init()
        self.size = size
        self.pos = pos
        self.rotation = rotation
        self.colorize = colorize
        if not texture:
            texture = blank_texture
        self.texture = texture
        self.detail = detail
        self.scale = 1

        self.display_list = data.DisplayList()
        self.visible = True

        self._compile()

    def get_dimensions(self):
        return self.size, self.size, self.size

    def get_pos(self):
        return self.pos

    def _compile(self):
        self.display_list.begin()
        self.texture.bind()
        Sphere = gluNewQuadric()
        gluQuadricTexture(Sphere, GLU_TRUE)
        gluSphere(Sphere, 1, self.detail, self.detail)
        self.display_list.end()

    def render(self, camera=None):
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glScalef(self.size, self.size, self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        n = Sphere(self.size, self.pos, self.colorize, self.texture, self.detail)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Skyball(Sphere):
    def __init__(self, texture=None, colorize=(1,1,1,1), detail=30):
        Sphere.__init__(self, 1, colorize=colorize,
                        texture=texture, detail=detail)

    def get_pos(self):
        return 0,0,0

    def render(self, camera):
        glDepthMask(GL_FALSE)
        glPushMatrix()
        camera.set_skybox_data()
        glRotatef(90, 1, 0, 0)
        Sphere.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)

    def copy(self):
        n = Skyball(self.texture, self.colorize, self.detail)
        n.scale = self.scale
        n.display_list = self.display_list
        return n
