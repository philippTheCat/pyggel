"Fonts":{ #create all the fonts the gui will use
    "default":{ #font "default"
        "fontfile":None, #None loads the system default, otherwise just make a .ttf file in the same dir
        "fontsize":32, #size
        "images":{"XD":"football.gif"} #embeddable images, must be in same dir
        }
    },
"App":{}, #Theme stuff for Apps, nothing is used ;)
"Widget":{}, #idget, again, uses nothing because on it's own it does nothing!
"Frame":{ #Frame
    "size":(100,100), #default size for frames
    "background-image":"base.png" #background image for the frame
    },
"Label":{ #Label
    "font":"default", #what font to use?
    "text":"label...", #default text
    "background-image":"base.png",
    "font-color":(1,1,1,1), #font color
    "font-color-inactive":(1,1,1,.5), #font color when widget is inactive
    "font-underline":False, #underline text?
    "font-italic":False, #italicize text?
    "font-bold":False #bold text?
    },
"Button":{ #Button
    "font":"default",
    "text":"button...",
    "background-image":"base.png",
    "background-image-hover":"base.png", #different bg image for different states (regular, hover, click)
    "background-image-click":"base.png",
    "font-color":(1,1,1,1),
    "font-color-hover":(0,1,0,1), #different font color for different states
    "font-color-click":(1,0,0,1),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False,
    "font-underline-hover":False, #different font attributes for different states
    "font-italic-hover":False,
    "font-bold-hover":False,
    "font-underline-click":False,
    "font-italic-click":False,
    "font-bold-click":False
    },
"Checkbox":{ #Checkbox
    "background-image":"check_open.png", #image when not checked
    "check-image":"check_closed.png" #image when checked
    },
"Radio":{ #Radio
    "font":"default",
    "background-image":"base.png",
    "option-background-image":"check_open.png", #background image for checkboxes
    "option-check-image":"check_closed.png", #check image for checkboxes
    "font-color":(1,1,1,1),
    "font-color-inactive":(1,1,1,.5),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False
    },
"MultiChoiceRadio":{
    "font":"default",
    "background-image":"base.png",
    "option-background-image":"check_open.png",
    "option-check-image":"check_closed.png",
    "font-color":(1,1,1,1),
    "font-color-inactive":(1,1,1,.5),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False
    },
"Input":{
    "font":"default",
    "text":"input...", #start text
    "width":100, #width of widget
    "background-image":"base.png",
    "font-color":(1,1,1,1),
    "font-color-inactive":(1,1,1,.5),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False
    },
"MoveBar":{
    "font":"default",
    "font-color":(1,1,1,1),
    "font-color-inactive":(1,1,1,.5),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False,
    "title":"Window...", #title of bar
    "width":100, #width of bar
    "background-image":"base.png"
    },
"Window":{
    "font":"default",
    "font-color":(1,1,1,1),
    "font-color-inactive":(1,1,1,.5),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False,
    "size":(100,100), #size of Frame, and [0] is width of MoveBar
    "background-image":"base.png", #Frame background image
    "movebar-background-image":"base.png" #MoveBar background image
    },
"Menu":{
    "name":"menu...",
    "font":"default",
    "font-color":(1,1,1,1), #attributes for Button that activates menu
    "font-color-hover":(0,1,0,1),
    "font-color-click":(1,0,0,1),
    "background-image":"base.png",
    "background-image-hover":"base.png",
    "background-image-click":"base.png",
    "menu-background-image":"base.png", #background for menu frames
    "option-background-image":"base.png", #attributes for each option (not sub-menu) button
    "option-background-image-hover":"base.png",
    "option-background-image-click":"base.png",
    "option-font-color":(1,1,1,1),
    "option-font-color-hover":(0,1,0,1),
    "option-font-color-click":(1,0,0,1),
    "sub-background-image":"base.png", #attributes for each option (only sub-menu) button
    "sub-background-image-hover":"base.png",
    "sub-background-image-click":"base.png",
    "sub-icon":"menu_icon.png", #image for right/left arrows indicating sub-menu
    "sub-font-color":(0,0,1,1),
    "sub-font-color-hover":(0,1,1,1),
    "sub-font-color-click":(1,1,0,1),
    "font-underline":False,
    "font-italic":False,
    "font-bold":False,
    "font-underline-hover":False,
    "font-italic-hover":False,
    "font-bold-hover":False,
    "font-underline-click":False,
    "font-italic-click":False,
    "font-bold-click":False,
    "option-font-underline":False,
    "option-font-italic":False,
    "option-font-bold":False,
    "option-font-underline-hover":False,
    "option-font-italic-hover":False,
    "option-font-bold-hover":False,
    "option-font-underline-click":False,
    "option-font-italic-click":False,
    "option-font-bold-click":False,
    "sub-font-underline":True,
    "sub-font-italic":False,
    "sub-font-bold":False,
    "sub-font-underline-hover":False,
    "sub-font-italic-hover":False,
    "sub-font-bold-hover":False,
    "sub-font-underline-click":False,
    "sub-font-italic-click":False,
    "sub-font-bold-click":False
    }
