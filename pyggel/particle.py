from include import *
import data, image, misc, data

import random
import numpy

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

    def get_dimensions(self):
        return self.behavior.get_dimensions()

    def get_pos(self):
        return self.pos

    def update(self):
        self.behavior.emitter_update()

    def render(self, camera):
        self.update()
        for i in self.particles:
            i.render(camera)


class Behavior3D(object):
    def __init__(self, emitter):
        self.emitter = emitter

        self.particle_lifespan = 1
        self.image = misc.create_empty_image3d((8,8))
        self.image.pos = self.emitter.pos

    def get_dimensions(self):
        #calculate max width, height and depth of particles...
        return 1, 1, 1

    def emitter_update(self):
        pass

    def particle_update(self, part):
        part.age += 1
        if part.age >= self.particle_lifespan:
            part.kill()

    def register_particle(self, part):
        pass

class Fire3D(Behavior3D):
    def __init__(self, emitter):
        Behavior3D.__init__(self, emitter)

        self.image = misc.create_empty_image3d((8,8), (1,.5,0,1))
        self.image.scale = .25
        self.image.pos = self.emitter.pos
        self.particle_lifespan = 20

    def get_dimensions(self):
        return 2, 6, 2 #max/abs(min) directions(x,y,z) * particle_lifespan

    def emitter_update(self):
        for i in xrange(5):
            self.emitter.particle_type(self.emitter, self)

    def register_particle(self, part):
        dx = randfloat(-.1, .1)
        dy = randfloat(.15, .3)
        dz = randfloat(-.1, .1)

        rot = random.randint(-25, 25)

        part.extra_data["dir"] = (dx, dy, dz)
        part.extra_data["rot"] = rot

        x, y, z = self.emitter.pos

        part.image.pos = x+dx*randfloat(1, 2), y, z+dz*randfloat(1, 2)

    def particle_update(self, part):
        Behavior3D.particle_update(self, part)
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


class ParticlePoint(object):
    def __init__(self, parent, behavior):
        self.parent = parent
        self.pos = self.parent.pos
        self.colorize = (1,1,1,1)

        self.index = self.parent.add_particle(self)

        self.extra_data = {}

        self.behavior = behavior
        self.behavior.register_particle(self)

        self.age = 0

    def get_vertex_index(self):
        return self.parent.particles.index(self)

    def kill(self):
        self.parent.remove_particle(self)

    def update(self):
        self.behavior.particle_update(self)
        x, y, z = self.pos
        r, g, b, a = self.colorize

        self.parent.vertex_array.verts[self.index][0] = x
        self.parent.vertex_array.verts[self.index][1] = y
        self.parent.vertex_array.verts[self.index][2] = z

        self.parent.vertex_array.colors[self.index][0] = r
        self.parent.vertex_array.colors[self.index][1] = g
        self.parent.vertex_array.colors[self.index][2] = b
        self.parent.vertex_array.colors[self.index][3] = a

class EmitterPoint(object):
    def __init__(self, behavior, pos=(0,0,0)):
        self.pos = pos
        self.behavior = behavior(self)
        self.particles = numpy.empty(self.behavior.max_particles, dtype=object)
        self.empty_spaces = []
        self.last_number = 0

        self.vertex_array = data.VertexArray(GL_POINTS, self.behavior.max_particles)

        self.visible = True
        self.particle_type = ParticlePoint

    def get_dimensions(self):
        return self.behavior.get_dimensions()

    def get_pos(self):
        return self.pos

    def add_particle(self, part):
        if self.empty_spaces:
            x = self.empty_spaces.pop(0)
            self.particles[x] = part
            return x
        else:
            self.particles[self.last_number] = part
            self.last_number += 1
            return self.last_number - 1

    def remove_particle(self, part):
        if part.index+1 == self.last_number:
            self.last_number -= 1
        else:
            self.empty_spaces.append(part.index)
        self.particles[part.index] = None

    def update(self):
        self.behavior.emitter_update()

    def render(self, camera):
        self.update()
        glPointSize(self.behavior.point_size)
        for i in self.particles:
            if i:
                i.update()
        self.vertex_array.render()


class BehaviorPoint(object):
    def __init__(self, emitter):
        self.emitter = emitter

        self.particle_lifespan = 1
        self.max_particles = 2

    def get_dimensions(self):
        return 1,1,1

    def emitter_update(self):
        pass

    def particle_update(self, part):
        part.age += 1
        if part.age >= self.particle_lifespan:
            part.kill()

    def register_particle(self, part):
        pass

class FirePoint(BehaviorPoint):
    def __init__(self, emitter):
        BehaviorPoint.__init__(self, emitter)

        self.particle_lifespan = 20
        self.point_size = 15
        self.max_particles = 105 #self.particle_lifespan * emit rate (5) + 1 cycle of give space - as the emitter runs before the particles die...

    def get_dimensions(self):
        return 2, 6, 2 #max/abs(min) directions (x,y,z) of particles * particle_lifespan

    def emitter_update(self):
        for i in xrange(5):
            self.emitter.particle_type(self.emitter, self)

    def register_particle(self, part):
        dx = randfloat(-.1, .1)
        dy = randfloat(.15, .3)
        dz = randfloat(-.1, .1)

        part.extra_data["dir"] = (dx, dy, dz)
        part.colorize = (1, 0, 0, 1)

        x, y, z = self.emitter.pos

        part.pos = x + dx * randfloat(1, 1.2), y, z + dz * randfloat(1, 1.2)

        part.colorize = random.choice(((1, 0, 0, 1),
                                       (1, .25, 0, 1),
                                       (1, 1, 0, 1)))

    def particle_update(self, part):
        BehaviorPoint.particle_update(self, part)

        r, g, b, a = part.colorize
        g += .01
        a -= 1.0/20
        part.colorize = r, g, b, a

        x, y, z = part.pos

        a, b, c = part.extra_data["dir"]
        x += a
        y += b
        z += c

        b -= .01
        part.extra_data["dir"] = a, b, c
        part.pos = x, y, z
