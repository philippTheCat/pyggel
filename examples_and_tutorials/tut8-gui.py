"""tut8-gui.py

This tutorial introduces you to PYGGEL's gui module."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

import random

#Alright - so most of our gui uses callbacks to register events, so let's make a couple:
def test_callback():
    print "woo!"
def test_menu(item):
    print item
def swap_apps(new):
    new.activate()

def main():
    #First, the standard pyggel init stuff
    pyggel.init()

    scene = pyggel.scene.Scene()
    event_handler = pyggel.event.Handler()

    #Now for the gui
    """The PYGGEL gui is quite complex and powerful, but most of it's features can generally be ignored.
       This tutorial will teach the basics, and what args for widgets generally do - you will need to reference
       the doc strings for individual widgets to find their exact usage, in some places.

       At the root of any gui is the app. Apps are integrated into the event handler, and you may have multiple,
       though only one may be active at any one time. The app will catch events from the handler before the user can,
       and block any it uses.
       Creating an app is simple:
           app = gui.App(handler) - this creates the app, handler must be the event handler it is attached to.
       There are a few attributes and methods you should pay attention to with App's:
           theme - this is a gui.Theme object that allows you to load a theme style for your gui.
                    Anywhere that a specific value (that isn't mandatory) is not set by the user (ie, set to gui.tdef),
                    the theme will insert the value needed.
                    Theme's are highly extensible, you will find a basic one in data/gui/theme.py
                    If you create your own widgets, you can add theme components for them to a theme file
                    with no modification to the gui code. Simply put "widget_name" instead of, say "Label",
                    and then any attributes you want. You can see how it is done with any of the widgets in the gui.
                    The theme file is basically a glorified Python dictionary.
                    values are placed like this:
                        "Name":{
                            "variable name":"value"
                            },
                    Now, you will want to pay attention to the Fonts section of the theme.
                    This is not a widget style as the others are, instead this is where you define the fonts for your theme.
                    You then reference those fonts in your widgets later in the theme.
                    look at data/gui/theme.py to see the specific values you can use for each widget.
                    NOTE: all widgets can take a special_name arg that will force them to change their widget name to use a different them value...
            packer - this is a gui.Packer object that is used to position widgets in the scene.
                     This object is used by various widgets besides the App, the only ones you need worry about are frames and windows.
                     Anytime a widget's position is set to None, it uses the packer, otherwise it will use the pos specified.
                     Packer has one attribute you need to pay attention to, packtype.
                     packtype can be:
                     "wrap" - simply pushes widgets one after another, creating a new line when they hit the edge of the screen/widget
                     "center" - centers widgets on their line and from the center of the screen/widget
                     None/"None" - just sticks the widgets one after another - only a NewLine widget can force a new line.

        Now, each individual widget can either use the theme default for their args, or they can be overwritten.
        Some widgets have values you *must* supply, ie, all widgets need app to be set,
        which is the root app or frame/window object they are attached to.
        Check the doc-strings for the args you must supply.
        Now, everything that is not a must, has a default in the theme.
        To overwrite a value, just send a different value than gui.tdef.
        Args for widgets match the names for them in the theme,
        except that "-" are converted into "_" so Python can handle them.

        So now that you know the overall general idea of widgets in the gui, let's make some widgets..."""

    #first the App
    app = pyggel.gui.App(event_handler)
    app.theme.load("data/gui/theme.py") #here we load a theme
    newapp = pyggel.gui.App(event_handler) #why not make another?
    newapp.theme = app.theme #and of course it uses the same theme
    app.activate() #gotta make sure the first app is the active one - since only one can be active, it will be rendered and get input...
    regfont = app.get_regfont("default") #A default font is always created - but our theme also specifies this
                                         #When the gui loads a font, it loads both a font.Font and font.MEFont version
                                         #Here we get the font.Font object
    mefont = app.get_mefont("default") #and here we get the font.MEFont for the "default" font
    #you can also do: regfont, mefont = app.get_font("default")

    #Now let's add a few embeddable images to the fonts
    #NOTE: regular images or GIF's can be specified in theme font declarations, but not SpriteSheet type ones
    regfont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    mefont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))

    #let's center our widgets...
    app.packer.packtype="center"

    #The App is a PYGGEL object like any other, and as such needs to be added to the scene for rendering...
    scene.add_2d(app)
    scene.add_2d(newapp)

    #OK, let's make a frame in our gui to add other widgets to
    #Creating a Frame is a lot like an App, except you have to give it the root app (or another frame/window), a pos and size
    #both pos and size are optional though, they have defaults in the theme...
    #But for now we want a widget with an absolute position, not a relative one...
    frame = pyggel.gui.Frame(app, (500, 0), (140, 300))
    frame.packer.packtype = "wrap" #and this frame's packer wraps, instead of center, widgets

    #Now, let's make some widgets to put in the frame!
    #the Button requires an app to add to (such as an App, Frame or Window)
    #here we are also setting the text to "click!:P" - since we have an embedded image bound to ":P" that is converted into it
    #also, we attach a callback to the button click event.
    #All widgets will fire this event when clicked, but unlike buttons you have to specifically find it
    #simply do this: widget.dispatch.bind("click", function) to attach a callback when one is not allowed in args.
    #we are also overwriting the theme for text underlining
    pyggel.gui.Button(frame, "click!:P", callbacks=[test_callback],
                         font_underline=True)
    #Another button - long text O.o this time we overwrite the background-image-click and set to None,
    #so while we are holding mouse down on the button the background is gone...
    pyggel.gui.Button(frame, "click!124675326745327645762354",
                         callbacks=[test_callback],
                         background_image_click=None)

    #Labels take a lot of what Buttons do, excepting anything having to do with hover/clicking
    #here we attach it to the frame, with text "test:" and underline it
    pyggel.gui.Label(frame, "test:", font_underline=True)
    #And now we want a checkbox next to the previous Label
    #checkbox simply requires the frame, here, since we are content with the theme images for it.
    #the checkboxes state (1=on or 0=off) is stored in checkbox.state
    #unfortunately we aren't checking that here because we just add it to the frame and then forget about it
    #you could, however, assign it to a variable and keep track of it later...
    #You can also attach a function to the dispatch event "change" to get called every time the state changes
    #this function must take one arg, which is the state of the checkbox
    pyggel.gui.Checkbox(frame)

    #Now let's create 10 more labels for this frame
    for i in xrange(10):
        pyggel.gui.Label(frame, "testing456")


    #Now we are done with that frame, and we are adding widget directly to the App...
    #A few Buttons, the first uses the same callback as the previous ones have, but the second
    #contains a callback to swap the active App...
    pyggel.gui.Button(app, "Click me!:PXD", callbacks=[test_callback],
                         background_image_click=None)
    pyggel.gui.Button(app, "Swap Apps!", callbacks=[lambda: swap_apps(newapp)],
                         background_image_click=None)
    #And here is the NewLine widget we talked about before, it simply forces text to a new line in a packer.
    #it can take an optional height arg to specify the minimum height of the line it ends, ie
    #the minimum amount of space between the top of the current line and the top of the new line
    pyggel.gui.NewLine(app)

    #Now let's fill the App with a few lines of Labels
    for i in xrange(2):
        for i in xrange(random.randint(1, 2)):
            pyggel.gui.Label(app, "testing! 123")
        pyggel.gui.NewLine(app, random.choice([0, 15]))

    #Alright, now that you know how to make Labels, Buttons, NewLines and Checkboxes
    #let's make some more complex widgets

    #the Radio widget takes a group of options and makes a checkbox and a label for each, allowing you to click and select one option.
    #the widget requires the standard App arg, but also should be given the options arg
    #here we give it 3 options you can pick.
    #the radio keeps a dict of option:state objects for the state fo each option,
    #just check for which one has a state of 1 for the actual state.
    #like the Checkbox you can attach a function to the dispatch event "change",
    #the function must take one arg, which is the new selected option
    pyggel.gui.Radio(app, options=["test", "34", "56"])

    #The MultiChoiceRadio is exactly the same as the radio, except it allows multipl options to be clicked
    #also, the change event sends a list of all selected options
    pyggel.gui.MultiChoiceRadio(app, options=["mc1", "mc2"])
    pyggel.gui.NewLine(app)

    #The Input widget simply converts keyboard events into text
    #it only catches when active though - so it has to be clicked, like a button, first.
    #to catch you can give a function in args, ie callback=function or attach one manually to the "submit" event
    pyggel.gui.Input(app, "test me...")

    #The MoveBar widget is an interesting widget.
    #Basically, it is a widget that, when clicked and held will follow the mouse around.
    #You can attach any other widget to it as it's child, and it will also move.
    #The move bar will relocate the child widget to be right under it.
    #unique, optional, args are width and child
    pyggel.gui.MoveBar(app, "TestWindow", child=frame)

    #A Window is a widget that basicaly wraps a MoveBar and a Frame, and attaches the Frame to the MoveBar.
    #As such it takes args for both the Frame and the MoveBar
    #Here, the size arg is used for both the Frame, and the x value is the width of the MoveBar
    window = pyggel.gui.Window(app, "P Window-take2!!!", pos=(100,100), size=(100,100))

    #Let's just stick some Label into the window so it isn't lonely...
    pyggel.gui.Label(window, "Woot!:P")

    #Now we are done with the first App
    #So let's add something to the other app, newapp.

    #So, let's make a Menu widget.
    #The menu will take args for a whole host of different things, but basically,
    #it has a button, that when clicked activates a frame with a bunch of options
    #Now, options must be a list of string options, or nested lists of their own options.
    #allows unlimited nesting.
    #when a list option is encountered, a sub menu is created,
    #with a button in the previous option screen that swaps, when clicked, to the new menu
    #the option name for the sub menu is the first option in the list, the options for it are the rest of the strings (or lists) in the list
    #only rule is that first option shouldn't be a list, as it needs a name...
    #you can tell when an option is clicked by attaching a function to the callback arg when creating,
    #or directly to the dispatch event menu-click
    #this function must take one arg, which is the option clicked.
    #If it is a sub-menu option, the name will be <submenu-name>.<option-name>,
    #   where submenu-name is the name of the option for the submenu (or the first option in the list)
    #   and option-name is the option clicked.
    #This applies to sub-sub-widgets as well, ie, hitting one of the numbers in the last widget will submit:
    #   "please work!.subagain!.1 or whatever it was that was clicked.
    pyggel.gui.Menu(newapp, "Menu", options=["help", "test", "quit","2","3","4","Snazzlemegapoof!!!!",
                                             ["please work!", "1", "2", "3", "asfkjhsakfh",
                                              ["subagain!", "1", "2", "3"*10]]],
                       callback=test_menu)

    #now a button to swap the current App back to the first...
    pyggel.gui.Button(newapp, "Swap Back!", callbacks=[lambda: swap_apps(app)],
                         background_image_click=None)
    #Finally, let's add an Icon widget to the newapp, so it isn't so lonely...
    #And Icon does nothing, just shows an image.
    pyggel.gui.Icon(newapp, image="data/gui/smiley.gif")


    #And there you have it, a simple gui is set up, and running.
    #Good luck! :)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        event_handler.update()
        if event_handler.quit:
            pyggel.quit()
            return None

        pyggel.view.clear_screen()
        scene.render()
        pyggel.view.refresh_screen()

main()
