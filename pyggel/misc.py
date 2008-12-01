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

        self.compile()

    def add_object(self, obj):
        """Add an object to the group - if called then group.compile() must be called afterwards, to recreate the display list"""
        self.objects.append(obj)

    def compile(self):
        """Compile everything into a data.DisplayList"""
        self.gl_list.begin()
        for i in self.objects:
            i.render()
        self.gl_list.end()

    def render(self, camera=None):
        """Render the group.
           camera should be None or the camera the scene is using - only here for compatability"""
        self.gl_list.render()

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

    def collide(self, other):
        """Returns whether this VolumeStore is colliding with another VolumeStore or math3d collision object."""
        self.update()
        if other.ctype == "VolumeStore":
            return self.collision_geom.collide(other.collision_geom)
        else:
            return other.collide(self.collision_geom)
