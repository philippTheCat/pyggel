"""tut9-particles.py

This tutorial introduces PYGGEL's particle effect system."""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *
from pyggel.misc import randfloat #this grabs a function that generates random decimal numbers

import random

"""Alrighty, so simple 3d objects are enough, eh? You want flashy particles?
   We've got just the thing(s)...

   There are two kinds of Particles/Emitters in PYGGEL.
   One is based on 3d Images and looks more realistic.
   And the other uses individual dots of color, but is much faster.

   The interface for both is quite simple, and to see how to make your own particles,
   I have copied/modified the Fire example effect for both the Image3D and the Point emitters,
   from pyggel/particle.py"""

class Fire3D(pyggel.particle.Behavior3D):
    """This very simple class controls how our emitter works and what kind of particles it makes.
       This behavior uses the Image3D particles..."""
    def __init__(self, emitter):
        pyggel.particle.Behavior3D.__init__(self, emitter) #first, we initialize the base Behavior

        self.image = image.Image3D("data/fire1.png") #here we load our image for the particles
        self.image.scale = .5 #scale the image down a bit
        self.image.pos = self.emitter.pos #set it's starting position
        self.image.colorize = (1,1,1,.5) #starting colorize
        self.particle_lifespan = 20 #this is how long each particle will live
        #considering our emitter_update call generates 5 particles a frame, and they each last 20 frames
        #we will have about 100 particles once the emitter gets going...

    def get_dimensions(self):
        #You can ignore this, basically this calculates the maximum bounds of the emitter effect.
        return 2, 6, 2 #max/abs(min) directions(x,y,z) * particle_lifespan

    def emitter_update(self):
        #this gets called every frame by the emitter, so we can generate new particles
        for i in xrange(5):
            self.emitter.particle_type(self.emitter, self) #self.emitter.particle_type is simply the particle class to use

    def register_particle(self, part):
        #This gets called by every particle when it is created
        #here we set up it's attributes to make it "work" correctly
        dx = randfloat(-.08, .08)
        dy = randfloat(.15, .3)
        dz = randfloat(-.08, .08)

        rot = random.randint(-25, 25)

        #beyond the basic pos, rot, colorize attributes that all Images have
        #each particle also has an extra_data dictionary, where you can put things specific
        #to your particles.
        #here we put things like rot and direction into extra_data
        part.extra_data["dir"] = (dx, dy, dz)
        part.extra_data["rot"] = rot

        x, y, z = self.emitter.pos

        part.image.pos = x+dx*randfloat(1, 2), y, z+dz*randfloat(1, 2)

    def particle_update(self, part):
        #this is called every frame for each particle to update theme
        pyggel.particle.Behavior3D.particle_update(self, part)
        x, y, z = part.image.pos
        #here we move the particle based on it's direction:
        a, b, c = part.extra_data["dir"]
        x += a
        y += b
        z += c

        b -= .015
        part.extra_data["dir"] = a, b, c
        part.image.pos = x, y, z

        x, y, z = part.image.rotation
        #here we rotate the image around...
        z -= part.extra_data["rot"]
        part.image.rotation = x, y, z

        #fade the image
        r, g, b, a = part.image.colorize
        a -= .5/20
        part.image.colorize = r, g, b, a

        part.image.scale -= .025

class FirePoint(pyggel.particle.BehaviorPoint):
    """This behavior uses the point particles..."""
    def __init__(self, emitter):
        pyggel.particle.BehaviorPoint.__init__(self, emitter)

        self.particle_lifespan = 20 #lifespan of particles
        self.point_size = 10 #size of points
        #This is needed because we are using an array for our points, so we don't want to overflow!!!
        self.max_particles = 105 #self.particle_lifespan * emit rate (5) + 1 cycle of give space - as the emitter runs before the particles die...

    def get_dimensions(self):
        return 2, 6, 2 #max/abs(min) directions (x,y,z) of particles * particle_lifespan

    def emitter_update(self):
        for i in xrange(5):
            self.emitter.particle_type(self.emitter, self)

    def register_particle(self, part):
        #This is a lot like the Fire3D one, except note there is no rotation...
        dx = randfloat(-.04, .04)
        dy = randfloat(.08, .125)
        dz = randfloat(-.04, .04)

        part.extra_data["dir"] = (dx, dy, dz)
        part.colorize = (randfloat(.75,1), randfloat(0,.75), 0, .5)

        x, y, z = self.emitter.pos

        part.pos = x + dx * randfloat(1, 3), y, z + dz * randfloat(1, 3)

        part.colorize = random.choice(((1, 0, 0, 1),
                                       (1, .25, 0, 1),
                                       (1, 1, 0, 1)))

    def particle_update(self, part):
        #again, this is really close to the other one, but no rotations, and we deal with the particle attributes
        #not the image ones here...
        pyggel.particle.BehaviorPoint.particle_update(self, part)

        r, g, b, a = part.colorize
        g += .01
        a -= 0.5/20
        part.colorize = r, g, b, a

        x, y, z = part.pos

        a, b, c = part.extra_data["dir"]
        x += a
        y += b
        z += c

        b -= .0025
        part.extra_data["dir"] = a, b, c
        part.pos = x, y, z

"""OK, so we know how to make our own particle emitter behaviors, so how do we use them?
   There are three parts to a particle effect in PYGGEL:
       The emitter, this object takes care of allocating resources for the particles,
           keeping track of them and killing them when they are too old,
           but follows the "rules" in it's behavior to do so correctly.
       The behavior, this object is what controls the emitter and tells it what to do.
       The particles, these objects are what we really go for, created and controlled by the emitter.

   Creating an emitter is pretty simple:
       emitter = particle.Emitter3D(behavior, pos) #behavior needs to be your behavior, in this case Fire3D
                                                   #pos is the 3d position of the emitter, defaults to (0,0,0)
       emitter = particle.EmitterPoint(behavior, pos) #behavior is FirePoint in this case

   And that is it - you simply add them to the scene, and they take care of the rest for you..."""

def main():
    pyggel.init(screen_size=(640,480))

    event_handler = pyggel.event.Handler()

    scene = pyggel.scene.Scene()

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1), (1,1,1,1),
                               (50,50,50,10), (0,0,0), True)

    scene.add_light(light)

    skybox = pyggel.geometry.Skybox("data/skybox.png")
    scene.add_skybox(skybox)

    #So, you know how to make particle behaviors and emitters now, so lets make a couple:
    emitter1 = pyggel.particle.Emitter3D(Fire3D, pos=(-2.5, 0, 0))
    emitter2 = pyggel.particle.EmitterPoint(FirePoint, pos=(2.5, 0, 0))

    scene.add_3d_blend((emitter1, emitter2))

    clock = pygame.time.Clock()

    while 1:
        clock.tick(60) #limit FPS
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update() #get the events!

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit() #close the window and clean up everything
           return None #close the loop

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

        pyggel.view.clear_screen()
        scene.render(camera)
        pyggel.view.refresh_screen()

main()
