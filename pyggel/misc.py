from include import *
import image, view, data, math3d

def create_empty_texture(size=(2,2), color=(1,1,1,1)):
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
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return image.Image(i, colorize=color)

def create_empty_image3d(size=(2,2), color=(1,1,1,1)):
    i = pygame.Surface(size)
    if len(color) == 3:
        color = color + (1,)
    i.fill((255,255,255,255))
    return image.Image3D(i, colorize=color)

class StaticObjectGroup(object):
    def __init__(self, objects=[]):
        self.objects = objects
        self.gl_list = glGenLists(1)

        self.visible = True

        self.compile()

    def add_object(self, obj):
        self.objects.append(obj)

    def compile(self):
        glNewList(self.gl_list, GL_COMPILE)
        for i in self.objects:
            i.render()
        glEndList()

    def render(self, camera=None):
        glCallList(self.gl_list)

def save_screenshot(filename):
    pygame.image.save(pygame.display.get_surface(), filename)

class VolumeStore(object):
    ctype = "VolumeStore"
    def __init__(self, parent):
        self.parent = parent

        self.vector = math3d.Vector((0,0,0))
        self.sphere = math3d.Sphere((0,0,0), max(parent.get_dimensions()))
        self.box = math3d.AABox((0,0,0), parent.get_dimensions())

        self.collision_geom = self.sphere

    def collide(self, other):
        if other.ctype == "VolumeStore":
            return self.collision_geom.collide(other.collision_geom)
        else:
            return other.collide(self.collision_geom)
