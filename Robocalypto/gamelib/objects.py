import pygame
from pygame.locals import *

import math, random

import pyggel

def colliderect(a, b):
    print a, b
    return a[0] + a[2] > b[0] and b[0] + b[2] > a[0] and a[1] + a[3] > b[1] and b[1] + b[3] > a[1]

def collidepoint(p, r):
    if r[0] < p[0] and p[0] < r[0]+r[2]:
        if r[1] < p[1] and p[1] < r[1]+r[3]:
            return True
    return False

class Group(object):
    
    def __init__(self):
        self._objects = []
    
    def __iter__(self):
        return iter(self._objects)
    
    def __len__(self):
        return len(self._objects)
   
    def add(self, o):
        self._objects.append(o)
   
    def remove(self, o):
        if o in self._objects:
            self._objects.remove(o)

class Object(object):
    
    def __init__(self, groups):
        self.grid_color = [0, 0, 0]
        for g in groups:
            g.add(self)
        self._groups = groups
        
    def kill(self):
        for g in self._groups:
            g.remove(self)
            
    def update(self):
        pass
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def alive(self):
        return self in self._groups[0] #HACK -- need to check to see if its in all groups efficiently

class Player(Object):
    
    def __init__(self, scene):
        Object.__init__(self, self.groups)
        self.scene = scene
        self.pos = [10, 15]
        self.old_pos = list(self.pos)
        self.angle = 0
        self.speed = 0.3
        self.rel_timer = 0
        
        self.gun = pyggel.mesh.OBJ("data/gun.obj", colorize=[0.2, 0.2, 0.2, 1])
        self.gun.scale = 0.65
        self.gun.rotation = list(self.gun.rotation)
        self.gun.pos = list(self.gun.pos)
        self.gun.rotation[0] = 90
        self.scene.add_3d(self.gun)
        self.update_gun_pos()
        self.gun.old_y = self.gun.pos[1]
        self.frame = 0
        
    def update_gun_pos(self):
        offsetx = math.sin(math.radians(self.angle+90))*0.25
        offsetz = math.cos(math.radians(self.angle+90))*0.25
        offsetx2 = math.sin(math.radians(self.angle))*1.1
        offsetz2 = math.cos(math.radians(self.angle))*1.1
        self.gun.pos = [self.pos[0]+offsetx+offsetx2, -0.2, self.pos[1]+offsetz+offsetz2]
        self.gun.rotation[2] = self.angle
        
    def update(self):
        self.frame += 1
        if self.frame > 360:
            self.frame = 0
        self.rel_timer -= 1
        self.old_pos = list(self.pos)
        
        key = pygame.key.get_pressed()
        if key[K_w]:
            self.pos[0] += math.sin(math.radians(self.angle))*self.speed
            self.pos[1] += math.cos(math.radians(self.angle))*self.speed
        if key[K_s]:
            self.pos[0] += math.sin(math.radians(self.angle))*-self.speed
            self.pos[1] += math.cos(math.radians(self.angle))*-self.speed
        if key[K_a]:
            self.pos[0] += math.sin(math.radians(self.angle+90))*-self.speed
            self.pos[1] += math.cos(math.radians(self.angle+90))*-self.speed
        if key[K_d]:
            self.pos[0] += math.sin(math.radians(self.angle+90))*self.speed
            self.pos[1] += math.cos(math.radians(self.angle+90))*self.speed
        if key[K_w] or key[K_s] or key[K_a] or key[K_d]:
            self.gun.pos[1] += math.sin(math.radians(self.frame)*8)/75
        
        mb = pygame.mouse.get_pressed()
        if mb[0]:
            if self.rel_timer <= 0:
              
                #Initial shot position
                shotpos = [self.gun.pos[0], -0.3, self.gun.pos[2]]
                shotpos[0] += math.sin(math.radians(self.angle+90))*.06
                shotpos[2] += math.cos(math.radians(self.angle+90))*.06
                shotpos[0] += math.sin(math.radians(self.angle))*0.75
                shotpos[2] += math.cos(math.radians(self.angle))*0.75
                Shot(self.scene, shotpos, -self.angle)
                self.rel_timer = 8
                GunFlash(self.scene, shotpos)
        
        if self.rel_timer > 5:
            self.gun.pos[1] = self.gun.old_y + 0.025
        elif self.rel_timer == 5:
            self.gun.pos[1] = self.gun.old_y
            self.frame = 0
    
    def collide(self, rect):
        #Collide n' slide.
        if collidepoint(self.pos, rect):
            #print [self.pos[0] - self.old_pos[0], self.pos[1] - self.old_pos[1]]
            if self.old_pos[0] >= rect[0]+rect[2] or self.old_pos[0] <= rect[0]:
                self.pos[0] = self.old_pos[0]
            if self.old_pos[1] >= rect[1]+rect[3] or self.old_pos[1] <= rect[1]:
                self.pos[1] = self.old_pos[1]

class Shot(Object):
    
    def __init__(self, scene, pos, angle):
        Object.__init__(self, self.groups)
        self.scene = scene
        self.obj = pyggel.mesh.OBJ("data/bullet.obj", pos=pos, rotation=[0, angle + 90, 0])
        self.obj.scale = 1.5
        self.scene.add_3d(self.obj)
        self.pos = [pos[0], pos[2]]
        self.angle = angle
        self.speed = 3.0
        self.h = pos[1]
        
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d(self.obj)
        
    def move(self):
        self.obj.pos = (self.pos[0], self.h, self.pos[1])
        self.pos[0] += math.cos(math.radians(self.angle+90))*(self.speed/5)
        self.pos[1] += math.sin(math.radians(self.angle+90))*(self.speed/5)

    def collide(self, rect):
        if collidepoint(self.pos, rect):
            self.kill()

class RoboBaddie(Object):
    
    def __init__(self, scene, pos):
        Object.__init__(self, self.groups)
        self.scene = scene
        self.obj = pyggel.mesh.OBJ("data/robo.obj", pos=pos, rotation=[270, 0, 0], colorize=[0.3, 0.4, 0.5, 1])
        self.obj.scale = 2.0
        self.scene.add_3d(self.obj)
        self.pos = list(pos)
        self.obj.pos = [self.pos[0], -0.2, self.pos[1]]
        self.hp = 5
        self.hit_timer = 0
        self.obj.colorize = [0.3, 0.4, 0.5, 1]
        
    def update(self):
        self.hit_timer -= 1
        if self.hit_timer > 0:
            self.obj.colorize = [1, 0, 0, 1]
        else:
            self.obj.colorize = [0.3, 0.4, 0.5, 1]
        self.obj.pos = [self.pos[0], -0.2, self.pos[1]]
        self.obj.rotation = (270, 0, self.obj.rotation[2]+3)
        self.pos[0] += math.sin(math.radians(-self.obj.rotation[2]))*0.1
        self.pos[1] += math.cos(math.radians(-self.obj.rotation[2]))*0.1
    
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d(self.obj)
            for i in range(3):
                pos = list(self.obj.pos)
                pos[0] += random.choice([-0.5, -0.4, -0.3, -0.2, -0.1])*random.choice([1, -1])
                pos[1] += random.choice([-0.3, -0.2, -0.1])*random.choice([1, -1])
                pos[2] += random.choice([-0.5, -0.4, -0.3, -0.2, -0.1])*random.choice([1, -1])
                Explosion(self.scene, pos)
    
    def collide(self, point):
        r = [self.pos[0] - 1.5, self.pos[1] - 1.5, 3.0, 3.0]
        if collidepoint(point, r) and self.hit_timer <= 0:
            self.hit_timer = 4
            self.hp -= 1
            if self.hp <= 0:
                self.kill()
            return 1

class Explosion(Object):
    
    def __init__(self, scene, pos):
        Object.__init__(self, self.groups)
        self.scene = scene
        self.obj = pyggel.image.Image3D("data/explosion.png", pos=pos)
        self.scene.add_3d_blend(self.obj)
        self.pos = list(pos)
        self.d = 1
        self.alpha = 1.0
        self.obj.scale = 0.25
       
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d_blend(self.obj)
        
    def update(self):
        self.obj.pos = list(self.pos)
        self.obj.scale += 0.1
        self.obj.rotation = [self.obj.rotation[0], self.obj.rotation[1], self.obj.rotation[2]+2]
        self.alpha -= 0.04
        if self.alpha < 0:
            self.kill()
        self.obj.colorize = (1.0, 1.0, 1.0, self.alpha)

class GunFlash(Object):
    
    def __init__(self, scene, pos):
        Object.__init__(self, self.groups)
        self.scene = scene
        self.obj = pyggel.image.Image3D("data/flash.png", pos=pos)
        self.scene.add_3d_blend(self.obj)
        self.pos = list(pos)
        self.alpha = 1.0
        self.obj.scale = 0.1
       
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d_blend(self.obj)
        
    def update(self):
        self.obj.pos = list(self.pos)
        self.obj.scale += 0.05
        self.alpha -= 0.1
        if self.alpha < 0:
            self.kill()
        self.obj.colorize = (1.0, 1.0, 0.5, self.alpha)

class Wall(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.pos = pos
