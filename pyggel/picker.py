from include import *

def Pick512Objects(x, y, group, camera):
    '''Based on PyOpenGL-2.0.2.01 glSelectWithCallback
       https://svn.red-bean.com/pyobjc/trunk/pyobjc/PyOpenGL-2.0.2.01/src/shadow/GL.GL__init__.0100.py'''

    viewport = glGetIntegerv(GL_VIEWPORT)
    glSelectBuffer(512)
    glRenderMode(GL_SELECT)

    glInitNames()
    glMatrixMode(GL_PROJECTION)
    previousviewmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    glLoadIdentity()
    gluPickMatrix(x, viewport[3] - y, 1, 1, viewport)
    glMultMatrixd(previousviewmatrix)
    camera.push()
    for i in group:
        glPushName(i[1])
        i[0].render(camera)
        glPopName()
    camera.pop()
    glFlush()
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(previousviewmatrix)

    return glRenderMode(GL_RENDER)


class Storage(object):
    def __init__(self):
        self.number = 0

_s = Storage()

def getPickName():
    _s.number += 1
    return _s.number - 1

class Group(object):
    def __init__(self):
        self.objects = [[]] #cur obj = -1

    def add_obj(self, obj):
        self.objects[-1].append((obj, getPickName()))
        if len(self.objects[-1]) >= 512:
            self.objects.append([])

    def pick(self, mouse_pos, camera=None):
        x, y = mouse_pos

        near = []
        far = []
        names = []
        for objgroup in self.objects:
            _n = Pick512Objects(x, y, objgroup, camera)
            for i in _n:
                near.append(i.near)
                far.append(i.far)
                names.append(i.names)
        print near, far, names
##            near.append(_n)
##            far.append(_f)
##            names.append(_na)

##        print near, far, names
