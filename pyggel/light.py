from include import *
from math3d import get_distance

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

        self._on = False
        self.priority = priority
        self.enabled = False
        self.gl_light = None

    def on(self):
        self._on = True

    def off(self):
        self._on = False

    def get_on(self):
        return self._on

    def doGL(self, gl_light):
        self.gl_light = gl_light
        glLightfv(gl_light, GL_AMBIENT, self.ambient)
        glLightfv(gl_light, GL_DIFFUSE, self.diffuse)
        glLightfv(gl_light, GL_SPECULAR, self.specular)
        glLightfv(gl_light, GL_POSITION, self.pos+(int(not self.directional),))
        glLightfv(gl_light, GL_SPOT_DIRECTION, self.spot_direction+(0,))
        glEnable(gl_light)

    def enable(self, gl_light):
        self.enabled = True
        self.doGL(gl_light)

    def disable(self):
        self.enabled = False

class LightGroup(object):
    def __init__(self):
        self.lights = []
        self.used_lights = []

    def add_light(self, light):
        self.lights.append(light)

    def enable_by_proximity(self, pos):
        dist = []
        if len(self.lights) <= 8:
            for i in self.lights:
                if i.get_on():
                    dist.append(i)
        for i in xrange(len(dist)):
            exec "dist[i].doGL(GL_LIGHT%s)"%i
