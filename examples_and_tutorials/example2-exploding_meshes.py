"""example2-exploding_meshes.py

This example shows how to explode a mesh object"""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480))

    pyggel.view.set_debug(False)

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()

    scene.camera = pyggel.camera.LookAtCamera((0,0,0), distance=35)

    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1), (1,1,1,1),
                               (50,50,50,10), (0,0,0), True)

    scene.add_light(light)

    #let's load a mesh
    #NOTE: this does not work for animations!
    obj = pyggel.mesh.OBJ("data/bird_plane.obj")

    #now let's make the exploder object
    #The object takes 4 arguments:
    #mesh - the mesh object to explode,
    #       generally you will use a copy as it modifies the values of the object directly!
    #speed - how fast the pieces move each frame
    #frame_duration - how many frames this animation lasts...
    #kill_when_finished - if True will remove from scene when finished
    exp = pyggel.mesh.Exploder(obj.copy(), .05, 125, False)
    scene.add_3d(exp)

    skybox = pyggel.geometry.Skybox("data/skybox.png")
    scene.add_skybox(skybox)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(60)
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update()

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit()
           return None

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

        if exp.dead:
            exp.reset()

        pyggel.view.clear_screen()
        scene.render()
        pyggel.view.refresh_screen()

main()
