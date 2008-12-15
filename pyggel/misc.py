"""
pyggle.misc
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The misc module contains various functions and classes that don't fit anywhere else.
"""

from include import *
import image, view, data, math3d

import random

def randfloat(a, b):
    """Returns a random floating point number in range(a,b)."""
    a = int(a*100000000)
    b = int(b*100000000)
    x = random.randint(a, b)
    return x * 0.00000001

def create_empty_texture(size=(2,2), color=(1,1,1,1)):
    """Create an empty data.Texture
       size must be a two part tuple representing the pixel size of the texture
       color must be a four-part tuple representing the (RGBA 0-1) color of the texture"""
    i = pygame.Surface(size)
    if len(color) == 4:
        r, g, b, a = color
    else:
        r, g, b = color
        a = 1
    r *= 255
    g *= 255
    b *= 255
    a *= 255
    i.fill((r,g,b,a))
    return data.Texture(i)

def create_empty_image(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image instead"""
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return image.Image(i, colorize=color)

def create_empty_image3d(size=(2,2), color=(1,1,1,1)):
    """Same as create_empty_texture, except returns an image.Image3D instead"""
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return image.Image3D(i, colorize=color)

class ObjectGroup(object):
    def __init__(self):
        self._objects = []

    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        return len(self._objects)

    def add(self, o):
        self._objects.append(o)

    def remove(self, o):
        if o in self._objects:
            self._objects.remove(o)

class ObjectInstance(object):
    def __init__(self, groups):
        for g in groups:
            g.add(self)
        self._groups = groups

    def kill(self):
        for g in self._groups:
            g.remove(self)

    def update(self):
        pass

    def alive(self):
        l = []; [l.extend(i) for i in self._groups]
        return self in l

class StaticObjectGroup(object):
    """A class that takes a list of renderable objects (that won't ever change position, rotation, etc.
           This includes Image3D's - as they require a dynamic look-up of the camera to billboard correctly)
       and compiles them into a single data.DisplayList so that rendering is much faster."""
    def __init__(self, objects=[]):
        """Create the group.
           objects must be a list of renderable objects"""
        self.objects = objects
        self.gl_list = data.DisplayList()

        self.visible = True
        self.pos = (0,0,0)

        self.compile()

        self.volume = VolumeStore(self)

    def add_object(self, obj):
        """Add an object to the group - if called then group.compile() must be called afterwards, to recreate the display list"""
        self.objects.append(obj)

    def compile(self):
        """Compile everything into a data.DisplayList"""
        self.gl_list.begin()
        for i in self.objects:
            i.render()
        self.gl_list.end()

        self.compile_bounding_data = []
        x = []
        y = []
        z = []
        for i in self.objects:
            a, b, c = i.get_dimensions()
            x.append(a)
            y.append(b)
            z.append(c)

        self.compile_bounding_data.append([max(x), max(y), max(z)])
        self.compile_bounding_data.append([1,1,1])

    def render(self, camera=None):
        """Render the group.
           camera should be None or the camera the scene is using - only here for compatability"""
        self.gl_list.render()

    def get_dimensions(self):
        """Return the width/height/depth of the mesh"""
        return self.compile_bounding_data[0]

    def get_pos(self):
        """Return the position of the mesh"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        return self.compile_bounding_data[1]

def save_screenshot(filename):
    """Save a screenshot to filename"""
    pygame.image.save(pygame.display.get_surface(), filename)

class VolumeStore(object):
    """A class that is used by objects, that stores a Vector, a Sphere and an AABox representing the object.
       Used for collision detection, the quadtree, and eventually frustum culling."""
    ctype = "VolumeStore"
    def __init__(self, parent):
        """Create the VolumeStore.
           parent must be the renderable object that is creating/using the store"""
        self.parent = parent

        self.vector = math3d.Vector((0,0,0))
        self.sphere = math3d.Sphere((0,0,0), max(parent.get_dimensions()))
        x, y, z = parent.get_dimensions()
        self.box = math3d.AABox((0,0,0), (x*2, y*2, z*2))

        self.collision_geom = self.sphere

    def update(self):
        """Update the position of the object to match our parent object."""
        self.vector.set_pos(self.parent.get_pos())
        self.sphere.set_pos(self.parent.get_pos())
        self.box.set_pos(self.parent.get_pos())
        self.sphere.scale = max(self.parent.get_scale())
        self.box.scale = self.parent.get_scale()

    def collide(self, other):
        """Returns whether this VolumeStore is colliding with another VolumeStore or math3d collision object."""
        self.update()
        if other.ctype == "VolumeStore":
            return self.collision_geom.collide(other.collision_geom)
        else:
            return other.collide(self.collision_geom)

class SpaceTreeObject(object):
    def __init__(self, tree, obj): #obj should be a VolumeStore object...
        self.tree = tree
        self.obj = obj
        self.in_nodes = []

    def norm_node(self, pos):
        return ((int(pos[0] / self.size) if pos[0] else 0),
                (int(pos[1] / self.size) if pos[1] else 0),
                (int(pos[2] / self.size) if pos[2] else 0))

    def update(self):
        #clear current nodes:
        for i in self.in_nodes:
            self.tree.nodes[i].remove(self.obj)
        self.in_nodes = []

        #get current obj pos
        self.obj.update()
        sphere = math3d.Sphere(self.norm_node(self.obj.sphere.get_pos()),
                               self.obj.sphere.radius) #get a sphere bounding volume for the object...
        sphere.radius = sphere.radius / self.tree.size if sphere.radius else 0

        #update nodes...
        c = math3d.AABox((0,0,0), self.tree.size)
        for n in self.tree.get_possible_nodes((x, y, z), sphere.radius):
            c.set_pos(n)
            if c.collide(sphere):
                self.tree.add_node(n)
                self.tree.nodes[n].append(self.obj)
                self.in_nodes.append(n)

class SpaceTree(object):
    def __init__(self, size=10):
        self.size = size
        self.nodes = {}
        self.objs = {}

    def add_node(self, pos): #should never need to be removed - just add slowly...
        if not pos in self.nodes:
            self.nodes[pos] = []

    def get_possible_nodes(self, pos, radius):
        r = radius + 1
        n = []
        xr = xrange(-r, r)
        for x in xr:
            for y in xr:
                for z in xr:
                    n.append((x, y, z))
        return n

    def add_object(self, obj):
        self.objs[obj] = SpaceTreeObject(self, obj)
        self.objs[obj].update()

    def get_nodes_object_is_in(self, obj):
        return self.objs[obj].in_nodes

    def update_object(self, obj):
        self.objs[obj].update()

    def remove_object(self, obj):
        sobj = self.objs[obj]
        for i in sobj.in_nodes:
            self.nodes[i].remove(obj)
        del self.objs[obj]
