from include import *
import image, view

def create_empty_texture(size=(128,128)):
    blank_texture = image.Texture(None, dont_load=True)
    i = pygame.Surface(size)
    i.fill((255,255,255,255))
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
