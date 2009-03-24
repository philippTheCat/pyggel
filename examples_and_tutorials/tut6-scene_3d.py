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
       For 3d, you basically have Meshes, geometrix shapes and 3d images/fonts.

       So, let's make all those same 2d elements from the last tutorial into 3d!"""

    #first, let's load an image!
    img = pyggel.image.Image3D("data/ar.png")
    img2 = img.copy() #let's make another! copying is cheaper than loading the image again, because textures don't have to be recompiled or loaded.
    #You can also copy by doing img2 = pyggel.image.Image(img) - but that is just long ;)
    #let's change some attributes here...
    img2.pos = (10, 0, 20) # new slot here, for "z" position
    img2.rotation = (0,0,45)

    #Woot, animations too!
    img3 = pyggel.image.GIFImage3D("data/football.gif")
    img3.pos = (2, 2, 20)

    img4 = pyggel.image.SpriteSheet3D("data/ar.png", [(0,0,16,16), (16,0,16,16), (32,0,16,16), (16,0,16,16)], 100)
    img4.pos = (4,2,20)

    img5 = pyggel.image.GridSpriteSheet3D("data/ar.png", (3, 3), 100)
    img5.pos = (6, 2, 20)

    #now the fonts
    font = pyggel.font.Font3D(None, 32) #sorry, no mefonts for 3d, and no embedded images/linewraps either, though newlines still work
    text1 = font.make_text_image("test?", italic=True)
    text1.pos = (-2, -2, 20)

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

           geometry.Quad(size, pos, rotation, colorize, texture, facing)
               A Quad is basically a cube, except it only renders one face...
               All the args are the same as for Cube, except:
                   texture can be None or a single data.Texture for the face
                   facing is the index (0-5) of cube faces to render
                       values are 0-left, 1-right, 2-top, 3-bottom, 4-front, 5-back
                       you can also use the names ("left", "front", etc.) to get the face...
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
    a = pyggel.geometry.Cube(1, pos=(-10, 0, 20)) #this one is untextured
    #first, a texture to use...
    tex = pyggel.data.Texture("data/ar.png")
    b = pyggel.geometry.Cube(1, pos=(-8, 0, 20), texture=tex) #this one is textured as a cubemap
    c = pyggel.geometry.Cube(1, pos=(-6, 0, 20), texture=[tex]*6) #this one copies the texture for each face

    d = pyggel.geometry.Quad(1, pos=(-4, 0, 20), texture=tex, facing="front") #this will look exactly like the cubes, because it is facing us...
    e = pyggel.geometry.Plane(10, pos=(-2, 0, 20), texture=tex, facing="front", tile=10)
    f = pyggel.geometry.Sphere(1, pos=(-6, 6, 20), texture=tex)

    scene.add_3d((a,b,c,d,e,f))

    #Woah, so why are all these new 3d elements so dark and bland and everything?
    #Because we have no light in the scene.
    #The 3d image types are pseudo - they don't use lights, and they always face the camera (unless specifically rotated away)
    #we will get to lights in the next lesson - for now, let's add a mesh and then we're done here :)

    """Ok, so you want more than just blocks and balls?
       Good, now we'll show you how you can import 3d models into PYGGEL.
       NOTE: for now there is only a loader for OBJ files, but more loaders are planned for the next release...

       Loading a mesh is quite simple:
           mesh = mesh.OBJ(filename, swapyz, pos, rotation, colorize)
               the pos, rotation and colorize args are the same as for geometry
               filename is the filename of the .obj object to load
               swapyz indicates whether to swap the y and the z coordinates for the mesh - defaults to True
                   the reason behind this is the way some modellers' environment is set up is different than PYGGEL,
                   so you generally need to convert.
       mesh.OBJ returns a mesh.BasicMesh object, which has the exact same usage as geometry objects do."""

    #lets make a mesh!
    mesh = pyggel.mesh.OBJ("data/carrot.obj", pos=(-8, 6, 20))
    scene.add_3d(mesh)

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
