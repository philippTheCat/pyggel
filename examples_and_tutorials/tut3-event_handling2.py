"""tut2-event_handling2.py

This tutorial continues from the last one, and continues event handling, showing how to attach callback functions to events."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def handle_mouse_press(button_number, button_name):
    #we've moved all mouse functionality into here
    print "mouse", button_name

def handle_keyboard_press(key_constant, key_name):
    #we've moved all keyboard functionality into here
    if key_name == " ": #was space bar hit?
        print "space bar!"
        return
    for i in xrange(10): #get all numbers from 0-9
        if str(i) == key_name: #a number was hit...
            print "number", i
            return

    print "None of the above!", key_constant, [key_name]

def handle_quit():
    #handle the quit!
    print "quit was hit - but we still handle it in main-loop so it can return and end with out throwing an error quit liek sys.exit"

def main():
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

    event_handler = pyggel.event.Handler()
    """Now that you understand how to handle keys by directly quarring their state,
       now we'll show you how to bind callbacks for events.

       You attach a callback to an event like this:
           event_handler.bind_to_event("event-name", function) #where event-name is the constant event name used to fire events,
                                                               #and function is the function to be called when this event is fired
                                                               #NOTE: you can bind multiple events to each event
                                                               #if you want to ensure function is the only one bound, you can use:
                                                               #event_handler.replace_event("event-name", function) instead
       There are several events you can bind callbacks for, listed here:
           "keydown" - fired for any events put in keyboard.hit
               #takes two args, key_constant and key_name
           "keyup" - fired for any key that is released
               #takes two args, key_constant and key_name
           "keyhold" - fired for any events put in keyboard.held
               #takes two args, key_constant and key_name
           "keyactive" - fired for any events put in keyboard.active
               #takes two args, key_constant and key_name

           "mousedown" - fired for any events put in mouse.hit
               #takes two args, button_number and button_name
           "mouseup" - fired for any mouse button that is released
               #takes two args, button_number and button_name
           "mousehold" - fired for any events put in mouse.held
               #takes two args, button_number and button_name
           "mouseactive" - fired for any events put in mouse.active
               #takes two args, button_number and button_name

           "quit" - fired for any QUIT events

           "uncaught-event" - fired for any uncaught events
               #takes one arg, pygame_event

           "update" - fired at end of event_handler.update() when all events are processed and fired."""

    #Now that you know how to attach callbacks to events, let's add our new mouse and keyboard handlers:
    event_handler.bind_to_event("mousedown", handle_mouse_press)
    event_handler.bind_to_event("keydown", handle_keyboard_press)
    event_handler.bind_to_event("quit", handle_quit)

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
