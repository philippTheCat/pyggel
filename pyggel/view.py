from include import *

class _Screen(object):
    def __init__(self):
        self.screen_size = (640, 480)
        self.rect = pygame.rect.Rect(0,0,*self.screen_size)
        self.fullscreen = False
        self.hwrender = True
        self.decorated = True
        self.shadows = False
        self.lighting = True
        self.fog = True
        self.fog_color = (.5,.5,.5,.5)

        self.clips = [(0,0,self.screen_size[0],self.screen_size[1])]
        glScissor(*self.clips[0])

    def set_size(self, size):
        self.screen_size = size
        self.clips = [] #clear!
        self.clips.append((0,0,size[0],size[1]))
        self.rect = pygame.rect.Rect(0,0,*size)
        glScissor(*self.clips[0])

    def get_params(self):
        params = OPENGL|DOUBLEBUF
        if self.fullscreen:
            params = params|FULLSCREEN
        if self.hwrender:
            params = params|HWSURFACE
        if not self.decorated:
            params = params|NOFRAME
        return params

    def push_clip(self, new):
        if self.clips: #we have an old one to compare to...
            a,b,c,d = new
            e,f,g,h = self.clips[-1] #last
            new = (max((a, e)), max((b, f)), min((c, g)), min((d, h)))
        self.clips.append(new)
        glScissor(*new)

    def pop_clip(self):
        if len(self.clips) == 1:
            return #don't pop the starting clip!
        self.clips.pop()
        glScissor(*self.clips[-1])

screen = _Screen()

def init(screen_size=None):
    if screen_size:
        screen.set_size(screen_size)
    else:
        screen_size = screen.screen_size

    pygame.init()
    build_screen()

    glEnable(GL_TEXTURE_2D)
    glFrontFace(GL_CCW)
    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_SCISSOR_TEST)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)

    clear_screen()
    set_fog_color((.5,.5,.5,.5))
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_DENSITY, .35)
    glHint(GL_FOG_HINT, GL_NICEST)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 50.0)
    set_fog(True)
    glAlphaFunc(GL_GEQUAL, .5)
    set_background_color()

def set_background_color(col=(0,0,0)):
    glClearColor(*col+(0,))

def set_fullscreen(boolean):
    screen.fullscreen = boolean
    build_screen()

def toggle_fullscreen():
    set_fullscreen(not screen.fullscreen)

def set_lighting(boolean):
    screen.lighting = boolean
    if boolean:
        glEnable(GL_LIGHTING)
    else:
        glDisable(GL_LIGHTING)

def toggle_lighting():
    set_lighting(not screen.lighting)

def set_hardware_render(boolean):
    screen.hwrender = boolean
    build_screen()

def toggle_hardware_render():
    set_hardware_render(not screen.hwrender)

def set_decorated(boolean):
    screen.decorated = boolean
    build_screen()

def toggle_decorated():
    set_decorated(not screen.decorated)

def set_shadows(boolean):
    screen.shadows = boolean

def set_fog_color(rgba):
    glFogfv(GL_FOG_COLOR, rgba)
    screen.fog_color = rgba

def set_fog(boolean):
    screen.fog = boolean
    if boolean:
        glEnable(GL_FOG)
    else:
        glDisable(GL_FOG)

def toggle_fog():
    set_fog(not screen.fog)

def build_screen():
    pygame.display.set_mode(screen.screen_size, screen.get_params())

def set2d():
    screen_size = screen.screen_size
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(0, screen_size[0], screen_size[1], 0, -50, 50)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

def set3d():
    screen_size = screen.screen_size
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*screen_size[0]/screen_size[1], 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)

def refresh_screen():
    pygame.display.flip()

def clear_screen(scene=None):
    glDisable(GL_SCISSOR_TEST)
    if scene and scene.graph.skybox:
        glClear(GL_DEPTH_BUFFER_BIT)
    else:
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
    glEnable(GL_SCISSOR_TEST)
