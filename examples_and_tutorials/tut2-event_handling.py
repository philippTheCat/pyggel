"""tut2-event_handling.py

This tutorial continues from the last one, and shows how to handle more kinds of events."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

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

        """In PYGGEL, events are registered and handled automatically, you simply have to look up the current state of keys or the mouse.
           You can use Pygame to get events instead, if you prefer that - but note, the GUI will only work with PYGGEL's event handler.

           The event handler currently handles these kinds of events:
           KEY press, release, hold
           MOUSE button press, release, hold
           MOUSE motion
           QUIT

           Anything not caught by the event handler is stuffed is stuffed into an uncaught_events list.

           There are two ways to handle input with PYGGEL's event handler.
           You can quarry for the status of the keyboard, mouse, quit or uncaught_events,
           or you can attach a function callback to events.

           In this tutorial, we will show you how to use the direct quarry method, the next tut will explain the callback binding.


           Now, you already know how to create and event handler, update it, and get a couple of events from it.
           The event handler has 4 attributes you should pay attention to - the others handle internal functionality of the handler,
           and you will never need to touch them (generally).
           The attributes are:
               keyboard, mouse, quit and uncaught_events

           NOTE: when a gui is present, it will supress events, so they will not appear in the event handler as you might guess.
                 If you want to get events regardless of if the gui used them,
                 the gui events are stored in the same place as the regular ones, except the access names are preceeded with gui_*:
                     gui_keyboard, gui_mouse and gui_uncaught_events
                 The only exception is quit - which is only held by regular events, the GUI won't catch it.
                 
           keyboard is where all key states are stored, it has 3 attributes you should watch:
               active, hit and held

               active is a list of all keys that were either hit or held
               hit is a list of all keys that were hit just this last check
               held is a list of all keys that were hit but not this last check, ie they have been held

               To check if a key is in any of the storage areas, you do:
                   if <key> in keyboard.active #or whatever you are checking, replace <key> with the key you are looking for.
               Keys you can check for are listed here:
                   Any Pygame key constants:
                       K_ESCAPE, K_a, K_1, K_LEFT, etc.
                   And, if the key is printable, a string representing it:
                       " " - for space, "a" - for a, "A" for a if shift and/or caps lock are on

           mouse is where all mouse states are stored, it has 4 atributes you should watch:
               active, hit, held and motion

               active, hit and held are identacle to keyboard, except for mouse buttons, instead of keys
               mouse is a list of the [x,y] movement of the mouse since last update

               You check for mouse states the same way as with the keyboard, except you use these constants:
                   Pygame events buttons - 1=left, 2=middle, 3=right, 4=wheelup, 5=wheeldown, rest are extra...

                   or with these string names:
                       "left", "middle", "right", "wheel-up", "wheel-down" and "extra-#" - replacing # with whatever pygame event button it was

           quit you already know about, it simply is a boolean that is true if QUIT (or the X button on the window) was clicked or not

           uncaught_events is a list of pygame events that the handler didn't catch.
           You should use these the same way you would handle pygame.event.get() events:

           for event in event_handler.uncaught_events:
               etc..."""

        #Alrighty, so now that you know what to do, let's handle some input:

        if " " in event_handler.keyboard.hit: #was space bar hit?
            print "space bar!"
        for i in xrange(10): #get all numbers from 0-9
            if str(i) in event_handler.keyboard.hit: #a number was hit...
                print "number", i

        for i in event_handler.mouse.hit: #get all mouse press events
            if not type(i) is type(1): #only get the button names, not the button numbers
                print "mouse", i

        pyggel.view.clear_screen() #clear screen for new drawing...
        pyggel.view.refresh_screen() #flip the display buffer so anything drawn now appears

main()
