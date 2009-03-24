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

    scene.add_3d(img) #these images don't have perpixel alpha, so they are ok to go in base 3d class
    scene.add_3d(img2)
    scene.add_3d(img3)
    scene.add_3d(img4)
    scene.add_3d(img5)
    scene.add_3d_blend(text1) #unfortunately, this one does have perpixel alpha,
                              #you can either put it in 3d and deal with the funny blending,
                              #or stick it in 3d_blend!


    """Alright, so now that we know that most 2d elements have a sister element to render in 3d, let's extend into 3d only territory.
       So let's start with some geometry. Now, regardless of 2d or 3d, PYGGEL allows the user to call any OpenGL stuff they want,
       Either by putting it into a class that scene can handle, or just calling gl render code between screen clear and refresh.
       But we've written a few classes to help with basic geometry so you don't have to reinvent the wheel all the time.
       These objects support all the features of other 3d objects (textures, colorize, pos, rotation, etc.):
           Cube - a cube simply makes a cube, that can be textured and positioned like a lego."""

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
