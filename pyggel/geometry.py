from include import *

class Cube(object):
    def __init__(self, size, pos=(0,0,0), texture=None):
        self.size = size
        self.pos = pos
        self.texture = texture

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

    def render(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(.5*self.size,.5*self.size,.5*self.size)
        for i in self.sides:
            glBegin(GL_QUADS)
            glColor4f(*i)
            for x in i:
                glVertex3f(*self.corners[x])
            glEnd()
        glPopMatrix()
