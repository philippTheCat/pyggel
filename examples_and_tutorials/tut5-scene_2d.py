"""tut5-scene_2d.py

This tutorial continues on from the previous, and explains how to load, manipulate and render 2d elements."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480), screen_size_2d=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()

    """Now that you know *how* to make a scene and what to do with them, let's put it to work!
       In this tutorial we will explain how to load, create, mess with and render 2d things, mainly images,
       but also font text, animations, sprite sheets and such."""

    """So, how exactly do we load and mess with images?
       In PYGGEL the image.Image class handles the vast majority or image things, from loading to handling (pos, rotation) to rendering.
       image.Image takes a few args at initiation:
           filename must be a string representing the file to load, a pygame Surface or another image.Image to copy.
           pos is the (x,y) position of the image
           rotation is the (x,y,z) rotation of the image
           scale is either the X or the (x,y,z) scale factor for the image
           colorize is the coloring for the image
       Beyond that there are only a few things you should know about images to use them:
           image.blit(other, pos) - this visually acts like pygame surface blitting,
               but in actuality it merely renders image first, then clips the view to itself and renders other at offset pos
               this method removes any previous blits of other image to this image
           image.blit_again(other, pos) - this is the same as blit, except it allows you to blit the same image multiple times
           get_width/height/size return the dimensions of the image
           get_rect returns a pygame.Rect with the images pos and size
           remove_blit(other) removes any blits of other image to this image
           sub_image(topleft, size) returns a new image that uses the pixels of this image's data from topleft to topleft+size"""

    #so, let's load an image!
    img = pyggel.image.Image("data/ar.png")
    img2 = img.copy() #let's make another! copying is cheaper than loading the image again, because textures don't have to be recompiled or loaded.
    #You can also copy by doing img2 = pyggel.image.Image(img) - but that is just long ;)
    #let's change some attributes here...
    img2.pos = (100,0)
    img2.rotation = (0,0,45)

    #alright, so now let's move on to animated images!
    """Animated images are quite similar to regular Images, there are just a few more/different methods.
       All Image methods are allowed - but they act differently - setting thigns occurs to all frames, getting returns current frame only.
       Creating an Animation is exactly the same as creating an image, except instead of filename a frames arg is supplied.
           frames must be a list of (Image, duration) objects, duration is in seconds
       Rendering an animation will automatically handle flipping frames unless paused or not looping and on last frame.
       The new methods are:
           seek(num) - change current frame of animation to frame[num]
           set_bounds(start, end) - this sets the start/end boundaries for playback - playback will only play inside these bounds
           pause - stops flipping of frames
           rewind - seeks to first frames
           fastforward - seeks to last frame
           length - number of frames
           reverse - reverses order of flipping frames
           reset - rewinds and undoes any reversal
           loop(boolean) - turns on/off looping - if off it will stop at last frame
           current - returns the current frame Image"""

    #loading animations can be doen manually, specifying an image/duration for each frame, but there are some automated tools for that.
    #First, you can load a GIF into an animation:
    img3 = pyggel.image.GIFImage("data/football.gif")
    img3.pos = (10,150)
    #or you can load a spritesheet!
    img4 = pyggel.image.SpriteSheet("data/ar.png", [(0,0,16,16), (16,0,16,16), (32,0,16,16), (16,0,16,16)], 100)
    img4.pos = (10,200)
    #the second argument are the boundaries of each frame in the image, and the third is the duration for each frame.
    #You can also automate this so you don't have to specify the bounds as well:
    img5 = pyggel.image.GridSpriteSheet("data/ar.png", (3, 3), 100)
    img5.pos = (10, 250)
    #with these you simply tell it how many frames in the (x,y) direction there are, and it figures out the rest.

    #ok, so now that we have some images, lets do some text!
    """With text you have 2 different options in PYGGEL, which you choose will depend on the situation.
       Regular Font objects create text that is very fast to render, but changing the text is very slow.
       MEFont objects create text that is quite a bit slower to render, but changing text takes almost no time at all.
       The usage for both fonts is identical:
           font = pyggel.font.Font/MEFont creates the font. It takes two optional arguments, filename and size.
               filename must be None or the filename of the font to load,
               size is the, well, size of the font :)
           font.add_image(name, img) - adds an embedded image for the text to use, like a smiley,
               anytime a text has name in it it is replaced with the image, instead of the text glyph.
               name must be the string used to reference this image, can be any text
               img must be an image.Image, image.Animation or the filename of an image to load.
           font.make_text_image(text) creates a new text image for rendering the text, args are:
               text - a string of text to render - all 'n characters are converted to newlines,
                   and any names of embedded images found are converted into the images
               color - the (r,g,b,a) color of the text, with values bound to 0-1
               linewrap - None or the pixel width for each line of text (text only broken at newlines and spaces, so might overrun
               underline, italic and bold - the attributes of the text, True or False for each"""
    font = pyggel.font.Font(None, 32)
    mefont = pyggel.font.MEFont(None, 32)
    text1 = font.make_text_image("test?", italic=True)
    text1.pos = (10, 350)
    text2 = mefont.make_text_image("test!", color=(1,0,0,1), underline=True)
    text2.pos = (10, 400)

    #Now that we have all our images and fonts, lets add them to the scene and enjoy!
    scene.add_2d(img)
    scene.add_2d(img2)
    scene.add_2d(img3)
    scene.add_2d(img4)
    scene.add_2d(img5)
    scene.add_2d(text1)
    scene.add_2d(text2)

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
