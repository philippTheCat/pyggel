"""
pyggle.picker
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *

def Pick512Objects(x, y, objs, camera):
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
    for i in objs:
        glPushName(i[1])
        if i[0].visible: i[0].render(camera)
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
        self.obj_dict = {}
        self.all_objs = []
        self.all_names = []

    def add_obj(self, obj):
        name = getPickName()
        self.objects[-1].append((obj, name))
        if len(self.objects[-1]) >= 512:
            self.objects.append([])
        self.obj_dict[name] = obj
        self.all_objs.append(obj)
        self.all_names.append(name)

    def rem_obj(self, obj):
        try:
            o = self.all_objs.index(obj)
            name = self.all_names[o]

            del self.obj_dict[name]
            for i in self.objects:
                for x in i:
                    if x[0] == obj and x[1] == name:
                        i.remove(x)
            self.all_objs.remove(obj)
            self.all_names.remove(name)
        except:
            pass

    def pick(self, mouse_pos, camera=None):
        x, y = mouse_pos

        near = []
        far = []
        names = []
        for objgroup in self.objects:
            if not objgroup:
                self.objects.remove(objgroup)
                continue
            _n = Pick512Objects(x, y, objgroup, camera)
            for i in _n:
                near.append(i.near)
                far.append(i.far)
                names.append(i.names)

        if near:
            best = names[near.index(min(near))][0]
            return self.obj_dict[best], min(near)
        return None
