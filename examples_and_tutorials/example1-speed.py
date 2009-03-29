"""example1-speed.py

This example shows how to use some of the built-in speed increasers in PYGGEL"""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    #Alright, the first thing you can do, is tell pyggel to use psyco
    #doing this will make the init try and locate psyco and then run it
    #if it doesn't find it psyco it will ignore this
    #By default, pyggel.init/pyggel.view.init will set use_psyco to True
    #but, this can be a bit of a mermoy hog, so if you don't need it to get decent framerates
    #then it is suggested that you disable it...
    pyggel.init(screen_size=(640,480))

    #Now, OpenGL does a ton of debug testing, which can really slow things down, so you can disable that for a speed boost
    #NOTE, tracebacks won't be as complete anymore ;)
    pyggel.view.set_debug(False)

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=20)

    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1), (1,1,1,1),
                               (50,50,50,10), (0,0,0), True)

    scene.add_light(light)

    #OK, let's make some stuff!
    a = pyggel.geometry.Cube(1, pos=(-5, 0, 0))
    a.rotation = (45, 45, 0)

    tex = pyggel.data.Texture("data/ar.png")
    b = pyggel.geometry.Cube(1, pos=(-3, 0, 0), texture=tex)
    b.rotation = (0,45,45)
    c = pyggel.geometry.Cube(1, pos=(-1, 0, 0), texture=["data/ar.png"]*6)

    d = pyggel.geometry.Quad(1, pos=(1, 0, 0), texture=tex)
    d.rotation=(90,0,0)
    e = pyggel.geometry.Plane(10, pos=(0, -7.5, 0), texture=tex, tile=10)
    e.rotation=(90,0,0)
    f = pyggel.geometry.Sphere(1, pos=(3, 0, 0), texture=tex)

    mesh = pyggel.mesh.OBJ("data/bird_plane.obj", pos=(5, 0, 0), swapyz=False)

    #Now look at this.
    #suppose we never wanted to modify these objects again? Their position, color, rotation, etc are all exactly where they need to be
    #and they won't ever need to change.
    #IE, we have scenery, they just need to render fast, we don't need to be constantly changing them.
    #So instead of adding them each to the scene and rendering them slowly (more or less), let's stick them into one big object
    #that compiles them up to runs fast, but be cemented, ie you can't change anything.

    #Introducing the StaticObjectGroup
    #This object takes a whole bunch of 3d objects and pre-renders them into a display list, so we don't have to do so
    #much to render them.
    #NOTE: nothing even semi-dynamic will work with this, ie Images (which are billboarded and need to updated to the
    #camera every render.
    #Another note - objects in here are considered one big object,
    #so picking will return the group, not any individual object.
    sog = pyggel.misc.StaticObjectGroup((a, b, c, d, e, f, mesh))
    scene.add_3d(sog)

    skybox = pyggel.geometry.Skybox("data/skybox.png")
    scene.add_skybox(skybox)

    clock = pygame.time.Clock() #pyggel automatically imports OpenGL/Pygame
                                #for a full list of everything included,
                                #look in pyggel/include.py

    #Those are the primary ways to boost speed in pyggel.
    #Another way is not to use one big scene, but instead several smaller, and swap between them for the active one...

    while 1:
        clock.tick(60) #limit FPS
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update() #get the events!

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit() #close the window and clean up everything
           return None #close the loop

        if K_LEFT in event_handler.keyboard.active: #rotate view!
            camera.roty -= .5
        if K_RIGHT in event_handler.keyboard.active:
            camera.roty += .5
        if K_UP in event_handler.keyboard.active:
            camera.rotx -= .5
        if K_DOWN in event_handler.keyboard.active:
            camera.rotx += .5
        if K_1 in event_handler.keyboard.active:
            camera.rotz -= .5
        if "2" in event_handler.keyboard.active: #just to throw you off ;)
            camera.rotz += .5

        if "=" in event_handler.keyboard.active: #move closer/farther out
            camera.distance -= .1
        if "-" in event_handler.keyboard.active:
            camera.distance += .1

        if "a" in event_handler.keyboard.active: #move the camera!
            camera.posx -= .1
        if K_d in event_handler.keyboard.active:
            camera.posx += .1
        if K_s in event_handler.keyboard.active:
            camera.posz -= .1
        if K_w in event_handler.keyboard.active:
            camera.posz += .1

        pyggel.view.clear_screen()
        scene.render(camera)
        pyggel.view.refresh_screen()

main()
