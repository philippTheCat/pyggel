from include import *

class Cube(object):
    def __init__(self, size, pos=(0,0,0), color=(1,1,1,1),
                 texture=None):
        self.size = size
        self.pos = pos
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
        self.sides = ((0,1,2,3),#front
                      (4,5,6,7),#back
                      (0,3,7,4),#left
                      (1,2,6,5),#right
                      (0,1,5,4),#top
                      (2,3,7,6))#bottom

        self.gl_list = glGenLists(1)

        self._compile()

    def _compile(self):
        glNewList(self.gl_list, GL_COMPILE)
        if self.texture:
            glBindTexture(GL_TEXTURE_2D, self.texture.gl_tex)
        else:
            blank_texture.bind()

        coords = ((0,0), (0,1), (1,1), (1,0))
        for i in self.sides:
            glBegin(GL_QUADS)
            ix = 0
            for x in i:
                glTexCoord2fv(coords[ix])
                glVertex3f(*self.corners[x])
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
