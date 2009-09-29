"""tut7-lights_cameras_skyboxes.py

This tutorial continues on from the previous, and explains how to create and use camera, lights and skyboxes"""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()
    scene.pick = True #let's make sure we are picking here, eh?

    """Alrighty, so when we left off in the last tutorial, we had a few 3d elements in,
       but they looked bad because there were no lights!
       Also, each and every object had to be positioned so that it could be seen, ie 20 units in,
       that really is the job of a camera to position for view, not the objects.
       Another thing, that black background is getting annoying, don't you think? Let's change that as well."""

    """So first thing is first, a camera.
       When creating cameras, you can use either of the two builtin camera's
       (LookFromCamera and LookAtCamera, basically first/third person camera)
       or, you can make your own by subclassing camera.Base - if you want something else entirely.
       camera.LookAtCamera(pos, rotation, distance) - this creates a "third-person" camera, it will
           always face pos, and rotate around it, instead of around it's own position.
           distance is how many units back the camera is from pos
       camera.LookFromCamera(pos, rotation) - this creates a "first-person" camera, it will
           always be at pos, any rotation is like turning your head, not like orbitting a planet."""

    #So, for our needs I think a LookAtCamera is best
    camera = pyggel.camera.LookAtCamera((0,0,0), distance=20)


    """Now we need some light in our scene!
       Remember that scenes may each have up to 8 lights, any more are ignored.
       light.Light(pos, ambient, diffuse, specular, spot_direction, directional)
           pos is the 3d position of the light
           ambient, diffuse are the colors of the light
           specular controls how shiny objects are when lit
           spot_direction is the (x,y,z) direction of the light if it is a spot light
           directional (True/False) controls whether this light is a directional or a spot light - defaults to True"""

    #OK, so let's make one, simple light...
    light = pyggel.light.Light((0,100,0),#so this is aobve most the elements
                               (0.5,0.5,0.5,1),#ambient color
                               (1,1,1,1),#diffuse color
                               (50,50,50,10),#specular
                               (0,0,0),#spot position - not used
                               True) #directional, not a spot light

    scene.add_light(light)


    img = pyggel.image.Image3D("data/ar.png")
    img.pos = (3,5,0)

    img4 = pyggel.image.SpriteSheet3D("data/ar.png", [(0,0,16,16), (16,0,16,16), (32,0,16,16), (16,0,16,16)], 100)
    img4.pos = (-3,5,0)

    #now the fonts
    font = pyggel.font.Font3D(None, 32) #sorry, no mefonts for 3d, and no embedded images/linewraps either, though newlines still work
    text1 = font.make_text_image("test?", italic=True)
    text1.pos = (0, 5, 0)

    scene.add_3d((img, img4)) #these images don't have perpixel alpha, so they are ok to go in base 3d class
    scene.add_3d_blend(text1) #unfortunately, this one does have perpixel alpha,
                              #you can either put it in 3d and deal with the funny blending,
                              #or stick it in 3d_blend!

    #OK, let's make some stuff!
    a = pyggel.geometry.Cube(1, pos=(-5, 0, 0)) #this one is untextured
    a.rotation = (45, 45, 0)
    #first, a texture to use...
    tex = pyggel.data.Texture("data/ar.png")
    b = pyggel.geometry.Cube(1, pos=(-3, 0, 0), texture=tex, mirror=False) #this one is textured as a cubemap
    b.rotation = (0,45,45)
    c = pyggel.geometry.Cube(1, pos=(-1, 0, 0), texture=tex) #this one copies the texture for each face

    d = pyggel.geometry.Quad(1, pos=(1, 0, 0), texture=tex) #this will look exactly like the cubes, because it is facing us...
    e = pyggel.geometry.Plane(10, pos=(0, -7.5, 0), texture=tex, tile=10)
    f = pyggel.geometry.Sphere(1, pos=(3, 0, 0), texture=tex, show_inside=True)

    #Hey, those positions for the elements looks a lot nicer now, eh?

    scene.add_3d((a,b,c,d,e,f))

    #lets make a mesh!
    mesh = pyggel.mesh.OBJ("data/bird_plane.obj", pos=(5, 0, 0))
    scene.add_3d(mesh)

    root = mesh.get_obj_by_name("cylinder1")
    tail = mesh.get_obj_by_name("sphere2")
    head = mesh.get_obj_by_name("sphere2_copy3")
    wings = mesh.get_obj_by_name("cube4")

    skel = pyggel.mesh.Skeleton()
    skel.add_bone(root.name,
                  (0,0,root.side("back")),
                  (0,0,root.side("front")))
    skel.add_bone(tail.name,
                  (0,0,tail.side("front")),
                  (0,0,tail.side("back")),
                  root.name)
    skel.add_bone(head.name,
                  (0,0,head.side("back")),
                  (0,0,head.side("front")),
                  root.name,
                  0.25)
    skel.add_bone(wings.name,
                  (wings.side("left"),0,0),
                  (wings.side("right"),0,0),
                  root.name,
                  0.5)

    action = pyggel.mesh.Action(2, [pyggel.mesh.RotateTo(wings.name, (0,0,45),0,.5),
                        pyggel.mesh.RotateTo(wings.name, (0,0,-45),.5,1.5),
                        pyggel.mesh.RotateTo(wings.name, (0,0,0),1.5,2),
                        pyggel.mesh.ScaleTo(tail.name, (1.25,1.25,1.25), 0, 1),
                        pyggel.mesh.ScaleTo(tail.name, (1,1,1), 1, 2),
                        pyggel.mesh.RotateTo(head.name, (0,15,0),0,.25),
                        pyggel.mesh.RotateTo(head.name, (0,-15,0),.25,.75),
                        pyggel.mesh.RotateTo(head.name, (0,0,0),.75,1),

                        #you can also define animations for non-existing mesh parts,
                        #so you can later add those parts
                        pyggel.mesh.RotateTo("weapon_right", (0,0,-45),0,.5), 
                        pyggel.mesh.RotateTo("weapon_right", (0,0,45),.5,1.5),
                        pyggel.mesh.RotateTo("weapon_right", (0,0,0),1.5,2),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,-45),0,.5),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,45),.5,1.5),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,0),1.5,2)])

    ani = pyggel.mesh.Animation(mesh, skel, {"move":action})
    ani.pos=(0,0,8)
    ani.rotation = (0,180,0) #so it faces us!
    ani.do("move")
    scene.add_3d(ani)

    """Alright, now that our 3d scene is lit and looks decent,
       let's add a skybox so we don't have that pesky blackness everywhere...

       Skyboxes/Skyballs functional pretty much identically to Cubes/Spheres,
           they just appear in only one place and are infinitely large.
           geometry.Skybox(texture, colorize)
               both args are exactly the same as for a Cube
           geometry.Skyball(texture, colorize, detail)
               again, exactly the same as a Sphere"""

    skybox = pyggel.geometry.Skybox("data/skybox.png")
    skyball = pyggel.geometry.Skyball("data/skyball.png")
    scene.add_skybox(skybox)

    clock = pygame.time.Clock() #pyggel automatically imports OpenGL/Pygame
                                #for a full list of everything included,
                                #look in pyggel/include.py

    last_obj = None #here we store which object was "picked" in the scene

    while 1:
        clock.tick(60) #limit FPS
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update() #get the events!

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit() #close the window and clean up everything
           return None #close the loop

        """Alrighty, so now that we have everything set up, camera, lights and a skybox,
           lets actually do something!"""

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

        if " " in event_handler.keyboard.hit: #swap the skybox so we can see the different ones in action!
            if scene.graph.skybox == skybox:
                scene.add_skybox(skyball)
            elif scene.graph.skybox == skyball:
                scene.add_skybox()
            else:
                scene.add_skybox(skybox)

        pyggel.view.clear_screen() #clear screen for new drawing...
        """Now, you need to make sure the scene actually uses your camera.
           PYGGEL scenes are very flexible, and allow you to swap cameras on demand,
           just pass whatever camera you want right now to the render call."""

        #all right, let's check if any objects are picked, and work with them here
        #then, if there is a pick, let's make the object turn red...

        #first, we render the scene, this also returns our object
        obj = scene.render(camera) #render the scene
        #Now, since we want to highlight the object the mouse is over, we gotta undo it too
        if last_obj:
            last_obj.colorize = (1,1,1,1)
        last_obj = obj
        if obj: #now we colorize the correct object
            obj.colorize = (1,0,0,1)
        pyggel.view.refresh_screen() #flip the display buffer so anything drawn now appears

        """And there you have all the basics to building a game with PYGGEL. Good luck!"""

main()
