"""
pyggle.light
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
from math3d import get_distance

all_lights = []
for i in xrange(8):
    exec "all_lights.append(GL_LIGHT%s)"%i

class Light(object):
    def __init__(self, pos=(0,0,0), ambient=(0,0,0,0),
                 diffuse=(1,1,1,1), specular=(1,1,1,1),
                 spot_direction=(0,0,0), directional=True,
                 priority=1):
        self.pos = pos
        self.directional = directional
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.spot_direction = spot_direction
        try:
            self.gl_light = all_lights.pop()
        except:
            self.gl_light = None

    def shine(self):
        if not self.gl_light == None:
            gl_light = self.gl_light
            glLightfv(gl_light, GL_AMBIENT, self.ambient)
            glLightfv(gl_light, GL_DIFFUSE, self.diffuse)
            glLightfv(gl_light, GL_SPECULAR, self.specular)
            glLightfv(gl_light, GL_POSITION, self.pos+(int(not self.directional),))
            glLightfv(gl_light, GL_SPOT_DIRECTION, self.spot_direction+(0,))
            glEnable(gl_light)
