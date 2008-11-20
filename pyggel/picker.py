from include import *

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

    def pick(self, mouse_pos):
        x, y = mouse_pos

        viewport = glGetIntegerv(GL_VIEWPORT)
        glSelectBuffer(512)
        glRenderMode(GL_SELECT)
        near = []
        far = []
        all = []

        glInitNames()
        glMatrixMode(GL_PROJECTION)
        previousviewmatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        glLoadIdentity()
        gluPickMatrix(x, viewport[3]-y, 1, 1, viewport)
