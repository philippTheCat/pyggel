from include import *
import data, image, misc

import random

def randfloat(a, b):
    a = int(a*10000)
    b = int(b*10000)
    x = random.randint(a, b)
    return x * 0.0001

class Particle3D(object):
    def __init__(self, parent, behavior):
        self.parent = parent
        self.parent.particles.append(self)

        self.extra_data = {}

        self.behavior = behavior
        self.image = self.behavior.image.copy()
        self.behavior.register_particle(self)

        self.age = 0

    def update(self):
        self.behavior.particle_update(self)

    def render(self, camera):
        self.update()
        self.image.render(camera)

    def kill(self):
        self.parent.particles.remove(self)

class Emitter3D(object):
    def __init__(self, behavior, pos=(0,0,0)):
        self.pos = pos
        self.behavior = behavior(self)
        self.particles = []
        self.particle_type = Particle3D

        self.visible = True

    def update(self):
        self.behavior.emitter_update()

    def render(self, camera):
        self.update()
        for i in self.particles:
            i.render(camera)


class Behavior(object):
    def __init__(self, emitter):
        self.emitter = emitter
        self.particles = []

        self.particle_lifespan = 1
        self.image = misc.create_empty_image3d((8,8))
        self.image.pos = self.emitter.pos

    def emitter_update(self):
        pass

    def particle_update(self, part):
        part.age += 1
        if part.age >= self.particle_lifespan:
            part.kill()

    def register_particle(self, part):
        self.particles.append(part)

class Fire(Behavior):
    def __init__(self, emitter):
        Behavior.__init__(self, emitter)

        self.image = misc.create_empty_image3d((8,8), (1,.5,0,1))
        self.image.scale = .25
        self.image.pos = self.emitter.pos
        self.particle_lifespan = 20

    def emitter_update(self):
        for i in xrange(5):
            self.emitter.particle_type(self.emitter, self)

    def register_particle(self, part):
        Behavior.register_particle(self, part)
        dx = randfloat(-.1, .1)
        dy = randfloat(.15, .3)
        dz = randfloat(-.1, .1)

        rot = random.randint(-25, 25)

        part.extra_data["dir"] = (dx, dy, dz)
        part.extra_data["rot"] = rot

        x, y, z = self.emitter.pos

        part.image.pos = x+dx, y, z+dz

    def particle_update(self, part):
        Behavior.particle_update(self, part)
        x, y, z = part.image.pos
        a, b, c = part.extra_data["dir"]
        x += a
        y += b
        z += c

        b -= .025
        part.extra_data["dir"] = a, b, c
        part.image.pos = x, y, z

        x, y, z = part.image.rotation
        z -= part.extra_data["rot"]
        part.image.rotation = x, y, z

        r, g, b, a = part.image.colorize
        a -= .075
        part.image.colorize = r, g, b, a

        part.image.scale -= .025
