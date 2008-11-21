from include import *
import image, view

def create_empty_texture(size=(128,128), color=(1,1,1,1)):
    blank_texture = image.Texture(None, dont_load=True)
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
    blank_texture._compile(i)
    return blank_texture

class StaticObjectGroup(object):
    def __init__(self, objects=[]):
        self.objects = objects
        self.gl_list = glGenLists(1)

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
