"""
pyggle.camera
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The camera module defines a Base camera class other cameras should inherit from, and two common cameras:
LookFromCamera - which is basically a FPS camera,
and the LookAtCamera - which is basically a third-person camera
"""
from include import *
import numpy
from math import sqrt

class Base(object):
    """camera.Base camera object all other inherit from..."""
    def __init__(self, pos=[0,0,0], rotation=[0,0,0]):
        """create the camera
           pos = position of the camera
           rotation = rotation of camera"""
        self.posx, self.posy, self.posz = pos
        self.rotx, self.roty, self.rotz = rotation
        self.frustum = None

    def get_frustum(self):
        proj = glGetFloatv(GL_PROJECTION_MATRIX).ravel()
        modl = glGetFloatv(GL_MODELVIEW_MATRIX).ravel()

        clip = numpy.empty(16, dtype=float)

        clip[0] = modl[0] * proj[0] + modl[1] * proj[4] + modl[2] * proj[8] + modl[3] * proj[12]
        clip[1] = modl[0] * proj[1] + modl[1] * proj[5] + modl[2] * proj[9] + modl[3] * proj[13]
        clip[2] = modl[0] * proj[2] + modl[1] * proj[6] + modl[2] * proj[10] + modl[3] * proj[14]
        clip[3] = modl[0] * proj[3] + modl[1] * proj[7] + modl[2] * proj[11] + modl[3] * proj[15]

        clip[4] = modl[4] * proj[0] + modl[5] * proj[4] + modl[6] * proj[8] + modl[7] * proj[12]
        clip[5] = modl[4] * proj[1] + modl[5] * proj[5] + modl[6] * proj[9] + modl[7] * proj[13]
        clip[6] = modl[4] * proj[2] + modl[5] * proj[6] + modl[6] * proj[10] + modl[7] * proj[14]
        clip[7] = modl[4] * proj[3] + modl[5] * proj[7] + modl[6] * proj[11] + modl[7] * proj[15]

        clip[8] = modl[8] * proj[0] + modl[9] * proj[4] + modl[10] * proj[8] + modl[11] * proj[12]
        clip[9] = modl[8] * proj[1] + modl[9] * proj[5] + modl[10] * proj[9] + modl[11] * proj[13]
        clip[10] = modl[8] * proj[2] + modl[9] * proj[6] + modl[10] * proj[10] + modl[11] * proj[14]
        clip[11] = modl[8] * proj[3] + modl[9] * proj[7] + modl[10] * proj[11] + modl[11] * proj[15]

        clip[12] = modl[12] * proj[0] + modl[13] * proj[4] + modl[14] * proj[8] + modl[15] * proj[12]
        clip[13] = modl[12] * proj[1] + modl[13] * proj[5] + modl[14] * proj[9] + modl[15] * proj[13]
        clip[14] = modl[12] * proj[2] + modl[13] * proj[6] + modl[14] * proj[10] + modl[15] * proj[14]
        clip[15] = modl[12] * proj[3] + modl[13] * proj[7] + modl[14] * proj[11] + modl[15] * proj[15]

        frustum = numpy.empty([6, 4], dtype=float)

        frustum[0][0] = clip[3] - clip[0]
        frustum[0][1] = clip[7] - clip[4]
        frustum[0][2] = clip[11] - clip[8]
        frustum[0][3] = clip[15] - clip[12]

        t = sqrt(frustum[0][0] * frustum[0][0] + frustum[0][1] * frustum[0][1] + frustum[0][2] * frustum[0][2])
        frustum[0][0] /= t
        frustum[0][1] /= t
        frustum[0][2] /= t
        frustum[0][3] /= t

        frustum[1][0] = clip[3] + clip[0]
        frustum[1][1] = clip[7] + clip[4]
        frustum[1][2] = clip[11] + clip[8]
        frustum[1][3] = clip[15] + clip[12]

        t = sqrt(frustum[1][0] * frustum[1][0] + frustum[1][1] * frustum[1][1] + frustum[1][2] * frustum[1][2])
        frustum[1][0] /= t
        frustum[1][1] /= t
        frustum[1][2] /= t
        frustum[1][3] /= t

        frustum[2][0] = clip[3] + clip[1]
        frustum[2][1] = clip[7] + clip[5]
        frustum[2][2] = clip[11] + clip[9]
        frustum[2][3] = clip[15] + clip[13]

        t = sqrt(frustum[2][0] * frustum[2][0] + frustum[2][1] * frustum[2][1] + frustum[2][2] * frustum[2][2])
        frustum[2][0] /= t
        frustum[2][1] /= t
        frustum[2][2] /= t
        frustum[2][3] /= t

        frustum[3][0] = clip[3] - clip[1]
        frustum[3][1] = clip[7] - clip[5]
        frustum[3][2] = clip[11] - clip[9]
        frustum[3][3] = clip[15] - clip[13]

        t = sqrt(frustum[3][0] * frustum[3][0] + frustum[3][1] * frustum[3][1] + frustum[3][2] * frustum[3][2])
        frustum[3][0] /= t
        frustum[3][1] /= t
        frustum[3][2] /= t
        frustum[3][3] /= t

        frustum[4][0] = clip[3] - clip[2]
        frustum[4][1] = clip[7] - clip[6]
        frustum[4][2] = clip[11] - clip[10]
        frustum[4][3] = clip[15] - clip[14]

        t = sqrt(frustum[4][0] * frustum[4][0] + frustum[4][1] * frustum[4][1] + frustum[4][2] * frustum[4][2])
        frustum[4][0] /= t
        frustum[4][1] /= t
        frustum[4][2] /= t
        frustum[4][3] /= t

        frustum[5][0] = clip[3] + clip[2]
        frustum[5][1] = clip[7] + clip[6]
        frustum[5][2] = clip[11] + clip[10]
        frustum[5][3] = clip[15] + clip[14]

        t = sqrt(frustum[5][0] * frustum[5][0] + frustum[5][1] * frustum[5][1] + frustum[5][2] * frustum[5][2])
        frustum[5][0] /= t
        frustum[5][1] /= t
        frustum[5][2] /= t
        frustum[5][3] /= t

        self.frustum = frustum


    def push(self):
        """Activate the camera - anything rendered after this uses the cameras transformations.
           Also resets frustum data."""
        self.get_frustum()
        glPushMatrix()

    def pop(self):
        """Deactivate the camera - must be called after push or will raise an OpenGL error"""
        glPopMatrix()

    def get_pos(self):
        """Return the position of the camera as a tuple"""
        return self.posx, self.posy, self.posz

    def get_rotation(self):
        """Return the rotation of the camera as a tuple"""
        return self.rotx, self.roty, self.rotz

    def set_facing_matrix(self):
        """Transforms the matrix so that all objects are facing camera - used in Image3D (billboard sprites)"""
        pass

    def set_skybox_data(self):
        """Transforms the view only for a skybox, ie only rotation is taken into account, not position"""
        pass

class LookFromCamera(Base):
    """camera.LookFromCamera is a FPS camera"""
    def __init__(self, pos=(0,0,0), rotation=(0,0,0)):
        Base.__init__(self, pos, rotation)
    __init__.__doc__ = Base.__init__.__doc__

    def push(self):
        self.get_frustum()
        glPushMatrix()
        glRotatef(self.rotx, 1, 0, 0)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)
        glTranslatef(-self.posx, -self.posy, self.posz)
    push.__doc__ = Base.push.__doc__

    def pop(self):
        glPopMatrix()
    pop.__doc__ = Base.pop.__doc__

    def get_pos(self):
        return self.posx, self.posy, self.posz
    get_pos.doc = Base.get_pos.__doc__

    def get_rotation(self):
        return self.rotx, self.roty, self.rotz
    get_rotation.__doc__ = Base.get_rotation.__doc__

    def set_facing_matrix(self):
        glRotatef(-self.rotz, 0, 0, 1)
        glRotatef(-self.roty, 0, 1, 0)
        glRotatef(-self.rotx, 1, 0, 0)
    set_facing_matrix.__doc__ = Base.set_facing_matrix.__doc__

    def set_skybox_data(self):
        glRotatef(self.rotx, 1, 0, 0)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)
    set_skybox_data.__doc__ = Base.set_skybox_data.__doc__

class LookAtCamera(Base):
    """camera.LookAtCamera is a third-person camera"""
    def __init__(self, pos=[0,0,0], rotation=[0,0,0],
                 distance=0):
        """create the camera
           pos is the position the camera is looking at
           rotation is how much we are rotated around the object
           distance is how far back from the object we are"""
        Base.__init__(self, pos, rotation)
        self.distance = distance

    def push(self):
        self.get_frustum()
        glPushMatrix()
        glTranslatef(0, 0, -self.distance)
        glRotatef(-self.rotx, 1, 0, 0)
        glRotatef(-self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)
        glTranslatef(-self.posx, -self.posy, self.posz)
    push.__doc__ = Base.push.__doc__

    def set_facing_matrix(self):
        glRotatef(-self.rotz, 0, 0, 1)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(self.rotx, 1, 0, 0)
    set_facing_matrix.__doc__ = Base.set_facing_matrix.__doc__

    def set_skybox_data(self):
        glRotatef(-self.rotx, 1, 0, 0)
        glRotatef(-self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)
    set_skybox_data.__doc__ = Base.set_skybox_data.__doc__
