"""tut1-setup_view.py

This tutorial shows you how to setup a basic view, start a loop, limit FPS and quit when events are grabbed."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    """pyggel.view.init can take several args that handle how the view is set up.
       screen_size is the 2d size of the screen to create
       screen_size_2d is the 2d size of the screen that the 2d uses,
           the 2d elements are handled as if this is the real screen size,
           and then scaled to fit the real screen size at render time,
           this allows multiple screen resolutions without resorting to hacking the 2d or,
           like some 3d engines do, make the 2d elements really 3d that are projected funny.
       use_psyco indicates whether to try and use psyco if it is available, for a speed boost.
       icon_image must be a string indicating the image to load from disk, or a pygame Surface to use for the window icon.
       full_screen indicates whether the render screen is fullscreen or not
       hwrender indicates whether hwrendering should be used for pygame operations
       decorated indicates whether the display window should have a border and top bar or not"""
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view.init...

    event_handler = pyggel.event.Handler()

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
        pyggel.view.refresh_screen() #flip the display buffer so anything drawn now appears

main()
