"""tut6-scene_3d.py

This tutorial continues on from the previous, and explains how to load, manipulate and render 3d elements."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()

    """Now, handling 3d elements is a lot like handling 2d ones, in fact there are 3d fonts and images,
           with exactly the same api just having a 3d position instead of 2d!
       For 3d, you basically have Meshes, geometric shapes and 3d images/fonts.

       So, let's make all those same 2d elements from the last tutorial into 3d!"""

    #first, let's load an image!
    img = pyggel.image.Image3D("data/ar.png")
    img2 = img.copy() #let's make another! copying is cheaper than loading the image again, because textures don't have to be recompiled or loaded.
    #You can also copy by doing img2 = pyggel.image.Image(img) - but that is just long ;)
    #let's change some attributes here...
    img2.pos = (10, 3, 20) # new slot here, for "z" position
    img2.rotation = (0,0,45)

    #Woot, animations too!
    img3 = pyggel.image.GIFImage3D("data/smiley.gif")
    img3.pos = (2, 3, 20)

    img4 = pyggel.image.SpriteSheet3D("data/ar.png", [(0,0,16,16), (16,0,16,16), (32,0,16,16), (16,0,16,16)], 100)
    img4.pos = (4,3,20)

    img5 = pyggel.image.GridSpriteSheet3D("data/ar.png", (3, 3), 100)
    img5.pos = (6, 3, 20)

    #now the fonts
    font = pyggel.font.Font3D(None, 32) #sorry, no mefonts for 3d, and no embedded images/linewraps either, though newlines still work
    text1 = font.make_text_image("test?", italic=True)
    text1.pos = (-2, 3, 20)

    scene.add_3d((img, img2, img3, img4, img5)) #these images don't have perpixel alpha, so they are ok to go in base 3d class
    scene.add_3d_blend(text1) #unfortunately, this one does have perpixel alpha,
                              #you can either put it in 3d and deal with the funny blending,
                              #or stick it in 3d_blend!


    """Alright, so now that we know that most 2d elements have a sister element to render in 3d, let's extend into 3d only territory.
       So let's start with some geometry. Now, regardless of 2d or 3d, PYGGEL allows the user to call any OpenGL stuff they want,
       Either by putting it into a class that scene can handle, or just calling gl render code between screen clear and refresh.
       But we've written a few classes to help with basic geometry so you don't have to reinvent the wheel all the time.
       These objects support all the features of other 3d objects (textures, colorize, pos, rotation, etc.):
           geometry.Cube(size, pos, rotation, colorize, texture)
               size is the length of each side of the cube
               pos is the (x,y,z) position of the object - defaults to (0,0,0)
               rotation is the (x,y,z) rotation of the object - defaults to (0,0,0)
               colorize is the (r,g,b,a) color, bound to range 0-1, of the object
               texture can be None, a single data.Texture object which will be mapped as cube map,
                   or a list of 6 data.Texture objects - each for it's own face
               mirror indicates whether the texture is the same for each face (like [tex]*6, if mirror is True)
                   or if it is used as a cube map (if False)
                   defaults to True

           geometry.Quad(size, pos, rotation, colorize, texture, facing)
               A Quad is a simple 3d square
               All the args are the same as for Cube, except:
                   texture can be None or a single data.Texture for the face
           geometry.Plane(size, pos, rotation, colorize, texture, facing, tile)
               A Plane is exactly the same as a Quad, except that you can tile the texture so that it repeats,
               which is much faster than having a ton of quads...
               Args are the same as for Quad with one addition:
                   tile is the number of times to repeat the image in the (x,y) surface of the plane
           geometry.Sphere(size, pos, rotation, colorize, texture, detail)
               The Args for a Sphere are virtually identacle to a Cube, only differences are:
                   texture can be None or a single texture mapped to the Sphere
                   size is the radius of the sphere
                   detail is smoothness of the sphere - higher is more smooth - defaults to 30

       Alrighty, so now you know how to add 4 kinds of geometry into your scene.
       The interface for each of these is pretty simple - there aren't really any methods you need to use,
       all you do is change the position/rotation/scale/colorize of the object..."""

    #OK, let's make some stuff!
    a = pyggel.geometry.Cube(1, pos=(-10, 6, 20)) #this one is untextured
    #first, a texture to use...
    tex = pyggel.data.Texture("data/ar.png")
    b = pyggel.geometry.Cube(1, pos=(-8, 6, 20), texture=tex, mirror=False) #this one is textured as a cubemap
    c = pyggel.geometry.Cube(1, pos=(-6, 6, 20), texture=tex) #this one copies the texture for each face

    d = pyggel.geometry.Quad(1, pos=(-4, 6, 20), texture=tex) #this will look exactly like the cubes, because it is facing us...
    d.rotation=(90,0,0) #so it faces us
    e = pyggel.geometry.Plane(10, pos=(-6, -6, 20), texture=tex, tile=10)
    e.rotation=(90,0,0)
    f = pyggel.geometry.Sphere(1, pos=(2, 6, 20), texture=tex)

    scene.add_3d((a,b,c,d,e,f))

    #Woah, so why are all these new 3d elements so dark and bland and everything?
    #Because we have no light in the scene.
    #The 3d image types are pseudo - they don't use lights, and they always face the camera (unless specifically rotated away)
    #we will get to lights in the next lesson - for now, let's add a mesh and then we're done here :)

    """Ok, so you want more than just blocks and balls?
       Good, now we'll show you how you can import 3d models into PYGGEL.
       NOTE: for now there is only a loader for OBJ files, but more loaders are planned for the next release(s)...

       Loading a mesh is quite simple:
           mesh = mesh.OBJ(filename, pos, rotation, colorize)
               the pos, rotation and colorize args are the same as for geometry
               filename is the filename of the .obj object to load
       mesh.OBJ returns a mesh.BasicMesh object, which has the exact same usage as geometry objects do."""

    #lets make a mesh!
    mesh = pyggel.mesh.OBJ("data/bird_plane.obj", pos=(4, 6, 20))
    #this OBJ file is actually in PYGGEL coords, so no swapping is needed
    scene.add_3d(mesh)

    """Alright, so a static mesh isn't gonna do you a lot of good now is it?
       So, let's animate it!
       NOTE: the animation uses the named objects in an OBJ file.
       Creating an animation is fairly straight forward:
           First, you have to create the skeleton representing the mesh parts
           Second you need to defeine the animation
           Lastly you create the animation object itself."""

    #ok, so let's define the names of our mesh parts:
    root = mesh.get_obj_by_name("cylinder1")
    tail = mesh.get_obj_by_name("sphere2")
    head = mesh.get_obj_by_name("sphere2_copy3")
    wings = mesh.get_obj_by_name("cube4")
    #Normally you will want to name the parts something more generic, like root, head, etc.

    #Now create the skeleton:
    skel = pyggel.mesh.Skeleton()
    #let's add some the bones to it then!
    #add_bone requires at least 3 arguments:
    #   name - the name of the mesh objext this bone represents
    #   start - the xyz start position of the bone
    #   end - the xyz end position of the bone
    #Also, the add_bone can take two optional arguments:
    #   root_name - any bone other than root must be attached to another bone,
    #               this can be the root bone or another child
    #   anchor - a value ranging from 0 to 1,
    #            indicating where the rotate point between the start/end of the bone is
    #            0 equals the start point, 1 equals the end point and 0.5 equals the center
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

    #Alrighty, now for our action!
    #actions are incredibly simple to understand
    #the first argument is the duration (in seconds) the entire action takes
    #the second is a list of command objects
    #There are three kinds of action commands:
    #   RotateTo, MoveTo and ScaleTo
    #each one works on an interpolation scheme, by the end of the commands run-time,
    #the bone values will match the command.
    #Each takes 3 arguments:
    #   name - the name of the bone and mesh object this action affects
    #   val - the ending value of the action - ie, rotation for RotateTo, movement for MoveTo, etc.
    #   start_time - how many seconds into the action this command starts
    #   end_time - how many seconds into the action this command ends
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

    #Alright, now for the animation object
    ani = pyggel.mesh.Animation(mesh, skel, {"move":action})
    ani.pos=(1,-2,10)
    ani.rotation = (0,180,0) #so it faces us!
    ani.do("move") #do takes two args: name of action, and loop = True/False
    scene.add_3d(ani)

    """And there we go, you have some geometry, a mesh, some 3d images/text and that is the basis for almost every scene in PYGGEL!"""

    clock = pygame.time.Clock() #pyggel automatically imports OpenGL/Pygame
                                #for a full list of everything included,
                                #look in pyggel/include.py

    while 1:
        clock.tick(60) #limit FPS
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update() #get the events!

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit() #close the window and clean up everything
           return None #close the loop

        pyggel.view.clear_screen() #clear screen for new drawing...
        scene.render() #render the scene
        pyggel.view.refresh_screen() #flip the display buffer so anything drawn now appears

main()
