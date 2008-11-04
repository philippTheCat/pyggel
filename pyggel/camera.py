from include import *

class LookFromCamera(object):
    def __init__(self, pos=[0,0,0], rotation=[0,0,0]):
        self.posx, self.posy, self.posz = pos
        self.rotx, self.roty, self.rotz = rotation

    def push(self):
        glPushMatrix()
        glRotatef(self.rotx, 1, 0, 0)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)
        glTranslatef(-self.posx, -self.posy, -self.posz)

    def pop(self):
        glPopMatrix()

    def get_pos(self):
        return self.posx, self.posy, self.posz

    def get_rotation(self):
        return self.rotx, self.roty, self.rotz

    def set_facing_matrix(self):
        glRotatef(-self.rotz, 0, 0, 1)
        glRotatef(-self.roty, 0, 1, 0)
        glRotatef(-self.rotx, 1, 0, 0)

class LookAtCamera(LookFromCamera):
    def __init__(self, pos=[0,0,0], rotation=[0,0,0],
                 distance=0):
        LookFromCamera.__init__(self, pos, rotation)
        self.distance = distance

    def push(self):
        glPushMatrix()
        glTranslatef(0, 0, -self.distance)
        glRotatef(self.rotx, 1, 0, 0)
        glRotatef(-self.roty, 0, 1, 0)
        glRotatef(-self.rotz, 0, 0, 1)
        glTranslatef(-self.posx, -self.posy, -self.posz)

    def set_facing_matrix(self):
        glRotatef(self.rotz, 0, 0, 1)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(-self.rotx, 1, 0, 0)
