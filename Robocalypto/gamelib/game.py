#! /usr/bin/env python

#Python imports
import sys, os
import math, random

#Import le pygame
import pygame
from pygame.locals import *

#Import the best gl library ever :-D
import pyggel
from pyggel import *

#Import local modules
from objects import *

#You're on the GRID! :-O
GRID = [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[1,1,0,0,0,0,0,0,2,0,1,0,0,2,0,1,0,2,0,2,0,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[1,1,0,0,0,1,0,1,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[1,0,0,2,0,1,0,1,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[1,0,0,0,0,0,0,1,1,0,1,0,1,1,0,1,0,2,0,2,0,1],
[1,0,0,0,0,1,0,1,0,0,1,0,1,0,0,1,0,2,0,2,0,1],
[1,1,0,0,1,1,0,1,0,0,1,0,1,0,0,1,0,2,0,2,0,1],
[0,1,0,0,0,1,0,0,0,0,1,1,1,0,1,1,0,2,0,2,0,1],
[0,1,0,0,0,1,0,0,2,0,0,0,0,0,0,1,0,2,0,2,0,1],
[0,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,2,0,2,0,1],
[0,1,0,0,0,0,1,0,1,1,1,0,0,2,0,1,0,2,0,2,0,1],
[1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1],
[1,1,0,2,0,1,0,0,0,0,1,0,1,1,1,1,1,1,0,1,1,1],
[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

#Level parsing function parsing levels
def level_parse(game, scene):
    
    #Static objects. Woo woo, built for speeeeeeed
    static = []
    walls = []
    x = y = 0 #OMGZ!
    height = len(GRID)
    width = len(GRID[0])
    mx = width/2*5
    my = height/2*5
    mwh = max((width, height))
    quad = pyggel.geometry.Plane(mwh*5,pos=[mx,0,my],facing="bottom",texture=pyggel.data.Texture("data/floor.png"),tile=mwh)
    static.append(quad)
    quad = pyggel.geometry.Plane(mwh*5,pos=[mx,0,my],facing="top",texture=pyggel.data.Texture("data/ceiling.png"),tile=mwh)
    static.append(quad)
    for row in GRID:
        for column in row:
            
##            #Floor tiles
##            quad = pyggel.geometry.Quad(4.55, pos=[x*5, 0, y*5], facing="bottom", texture=pyggel.data.Texture("data/floor.png"), tile=2)
##            static.append(quad)
##            
##            #Ceiling tiles
##            quad = pyggel.geometry.Quad(4.55, pos=[x*5, 0, y*5], facing="top", texture=pyggel.data.Texture("data/ceiling.png"), tile=2)
##            static.append(quad)
            
            #Walls
            if column == 1:
                box = pyggel.geometry.Cube(4.55, texture=[data.Texture("data/%s" % random.choice(["wall.png", "door.png", "wall.png", "wall.png"]))]*6)
                box.pos=(x*5,0,y*5)
                static.append(box)
                walls.append(Wall(game, [box.pos[0], box.pos[2]]))
            
            #Robo Baddies. OoOoOoOoOo...
            if column == 2:
                RoboBaddie(game, [x*5, y*5])
        
        #Positioning
            x += 1
        y += 1
        x = 0
    return static, walls

class Game(object):
    
    def __init__(self):

        #Vee must handle ze FPS for ze FPS!
        self.clock = pygame.time.Clock()
        
        #Disable fog. We ain't in a blasted harbor, RB[0]!
        #pyggel.view.set_fog(False)
        pyggel.view.set_fog_color((0, .6, .5, .5))
        pyggel.view.set_fog_depth(1, 60)
        
        #Create a First Person camera
        self.camera = pyggel.camera.LookFromCamera((0,0,-10))
        
        #Create a light. All good little GL apps should have light.
        light = pyggel.light.Light((50,300,50), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)
        
        #Create the scene, and apply the light to it.
        self.scene = pyggel.scene.Scene()
        self.scene.add_light(light)

        #Keep the mouse in the window, and make it disssssappear! Mwahahaha!
        self.grabbed = 1
        pygame.event.set_grab(self.grabbed)
        pygame.mouse.set_visible(0)
        
        #Create starting objects
        self.objects = Group()
        self.shots = Group()
        self.baddies = Group()
        self.walls = Group()
        Player.groups = [self.objects]
        Gun.groups = [self.objects]
        Shot.groups = [self.objects, self.shots]
        RoboBaddie.groups = [self.objects, self.baddies]
        Explosion.groups = [self.objects]
        Wall.groups = [self.objects, self.walls]
        GunFlash.groups = [self.objects]
        
        self.player = Player(self)
        self.overlay = pyggel.image.Image("data/screen.png", pos=[0, 0])
        self.overlay.scale = 1.5
        self.overlay.colorize = [0, 1, 1, 0.1]
        self.scene.add_2d(self.overlay)
        self.hudmask = pyggel.image.Image("data/hud.png", pos=[0, 0])
        self.scene.add_2d(self.hudmask)
        self.targeter = pyggel.image.Image("data/target.png", pos=[400-32, 300-32])
        self.scene.add_2d(self.targeter)
        self.font = pyggel.font.MEFont("data/DS-DIGI.ttf", 32)
        self.text1 = self.font.make_text_image("", (0, 255, 0))
        self.text1.pos = (50, 10)
        self.scene.add_2d(self.text1)
        
        #self.sky = pyggel.geometry.Skyball(texture=pyggel.image.Texture("data/ceiling.png")) #
        #self.scene.add_skybox(self.sky)
        
        #parse ze level
        static, self.walls._objects = level_parse(self, self.scene)
        self.scene.add_3d(pyggel.misc.StaticObjectGroup(static))
        
        #Used for bobbing up and down. No I will not be less vague.
        self.frame = 0
    
    def update_camera_pos(self):
        amt = pygame.mouse.get_rel()
        self.player.rotation += amt[0]/8.0
        self.camera.roty = self.player.rotation
        self.camera.posz = self.player.pos[1]
        self.camera.posx = self.player.pos[0]
    
    def do_input(self):
        
        #Get input
        for e in pyggel.get_events():
            
            #OMGZ! YOU QUIT! You disappoint me... >(
            if e.type == QUIT:
                self.running = False
            
            if e.type == KEYDOWN:
                
                #YOU'RE AT IT AGAIN!! AUGGH!
                if e.key == K_ESCAPE:
                    self.running = False
                
                #Release the mouse from the window if you press space
                if e.key == K_SPACE:
                    self.grabbed ^= 1
                    pygame.event.set_grab(self.grabbed)

                if e.key == K_RETURN:
                    pyggel.misc.save_screenshot("test.png")

    def do_update(self):
        
        #Loop the frame at 360.
        self.frame += 1
        if self.frame > 360:
            self.frame = 0
        
        #Cap the FPS so the FPS runs smoothly. DOUBLE MEANING! Bwahaha!
        self.clock.tick(999)
##        print self.clock.get_fps()

        s = "AMMO: %s\nScore: %s\nLives: %s\nFPS: %s"%(self.player.ammo, self.player.score,
                                                       self.player.lives, int(self.clock.get_fps()))
        self.text1.text = s
        
        self.update_camera_pos()
        for o in self.objects:
            o.update()
        for w in self.walls:
            r = [w.pos[0]-3.0, w.pos[1]-3.0, 6.0, 6.0]
            self.player.collide(r) 
        for s in self.shots:
            collidables = []
            for w in self.walls:
                area = [s.pos[0]-10, s.pos[1]-10, 20, 20]
                if collidepoint(w.pos, area):
                    collidables.append(w)
            for i in xrange(5):
                s.move_increment()
                for w in collidables:
                    r = [w.pos[0]-3.0, w.pos[1]-3.0, 6.0, 6.0]
                    s.collide(r)
            for b in self.baddies:
                if b.collide(s.pos):
                    s.kill()
        for b in self.baddies:
            r = [b.pos[0] - 20, b.pos[1] - 20, 40, 40]
            line = [b.pos[0], b.pos[1]]
            home_in = False
            collidables = []
            wr = [b.pos[0] - 15, b.pos[1] - 15, 30, 30]
            for w in self.walls:
                if collidepoint(w.pos, wr):
                    collidables.append(w)
            for i in xrange(10):
                line[0] += math.sin(math.radians(b.obj.rotation[2]))*1
                line[1] += math.cos(math.radians(b.obj.rotation[2]))*1
                r2 = [self.player.pos[0] - 5, self.player.pos[1] - 5, 10, 10]
                if collidepoint(line, r2):
                    home_in = True
                    break
            if collidepoint(self.player.pos, r) or home_in:
                x = self.player.pos[0] - b.pos[0]
                y = self.player.pos[1] - b.pos[1]
                angle = math.atan2(-y, x)
                angle = 270.0 - (angle * 180.0)/math.pi
                b.obj.rotation = (b.obj.rotation[0], b.obj.rotation[1], angle)
            for w in collidables:
                r = [w.pos[0]-3.0, w.pos[1]-3.0, 6.0, 6.0]
                b.wall_collide(r)

    def do_draw(self):
        
        #And pyggel doth draw.
        pyggel.view.clear_screen()
        self.scene.render(self.camera)
        pyggel.view.refresh_screen()

    def main_loop(self):
        
        #Loop de loop
        self.running = True
        while self.running:
            self.do_input()
            self.do_update()
            self.do_draw()

        pygame.event.set_grab(False)

    def run(self):
        self.main_loop()
