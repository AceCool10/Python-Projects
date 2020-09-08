import pygame as py
import random
import os
import math
vec = py.math.Vector2
from os import path
from threading import Thread
import time

# define constants
WIDTH = 1000
HEIGHT = 600
FPS = 70
ANGLE = 90
ENEMY_ANGLE = 0
POWER = 5
GRAVITY = 0.07 * 1
PLAYER_FRICTION = -0.12 * 1
BULLETS = 100
EMPTY_GUN_FLASH = False
LEVEL = 1
# define colors
BLACK = (0 , 0 , 0)
RED = (255 , 0 , 0)
GREEN = (0 , 255 , 0)
BLUE = (0 , 0 , 255)
WHITE = (255 , 255 , 255)
YELLOW = (255 , 255 , 0)
BG_COLOR = (190, 224, 143)
#BG_COLOR = (255, 255, 255)
colors =[ (249, 4, 4) , (252, 95, 5) , (54, 193, 149) , (150, 19, 102) ,
           (5, 66, 252) , (144, 5, 252) ,(33, 109, 85) , (214, 96, 153) ,
            (119, 57, 113) ,(96, 44, 30), (83, 92, 94) , (99, 163, 242) ,
            (138, 120, 186) , (198, 166, 127)
        ]

def exit():
    time.sleep(5)
    global running
    running = False

def display_level(surf , text , size , x , y):
    font = py.font.Font(py.font.match_font('arial') , size)
    text_surface = font.render(str(text) , True , BLACK) #True for Anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x , y)
    surf.blit(text_surface , text_rect)

def draw_shield_bar(surf , x , y , w , h, pct):
    if pct < 0:
        pct = 0
    fill = (pct / 100) * w
    outline_rect = py.Rect(x , y ,w , h)
    fill_rect = py.Rect(x , y ,fill ,h)
    py.draw.rect(surf , GREEN if pct > 20 else RED ,fill_rect)
    py.draw.rect(surf , WHITE ,outline_rect , 2)

def display_angle(surf , text , size , x , y):
    font = py.font.Font(py.font.match_font('arial') , size)
    text_surface = font.render(str(text) , True , BLACK) #True for Anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x , y)
    surf.blit(text_surface , text_rect)

def display_power(surf , text , size , x , y):
    font = py.font.Font(py.font.match_font('arial') , size)
    text_surface = font.render(str(int(text)) + '%'  , True , BLACK) #True for Anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x , y)
    surf.blit(text_surface , text_rect)

def display_bullets(surf , text , size , x , y):
    global EMPTY_GUN_FLASH
    if not EMPTY_GUN_FLASH:
        draw_bullet(surf , x , y)
    font = py.font.Font(py.font.match_font('arial') , size)
    text_surface = font.render(str(text) , True , BLACK) #True for Anti-aliased
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x + 40 , y - 25)
    surf.blit(text_surface , text_rect)

def draw_bullet(surf, x, y):
    py.draw.rect(surf , RED , py.Rect(x , y  ,10 , 10))
    py.draw.rect(surf , RED , py.Rect(x-1 , y - 15  ,12 , 12))
    py.draw.rect(surf , RED , py.Rect(x + 1 , y - 26  ,8 , 8))
    py.draw.circle(surf , RED , (x+5 , y-27) , 4 )


class Powerups(py.sprite.DirtySprite):
    def __init__(self , x , y , speed):
        py.sprite.DirtySprite.__init__(self)
        self._layer = 3
        self.image_orig = py.Surface((12 , 45)).convert()
        #self.image_orig.fill(WHITE)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.type = 'add_bullet'
        self.born = py.time.get_ticks()
        self.opacity = 200
        self.vel = vec(0 , 0)
        self.acc = vec(0 , GRAVITY)
        self.pos = vec(x , y)
        self.rot = 0
        self.rot_speed = random.randint(-speed - 1,speed + 1)
        if self.rot_speed == 0:
            self.rot_speed = 1
        elif speed - abs(self.rot_speed) > 8:
            self.rot_speed *= 3
        elif speed - abs(self.rot_speed) > 5:
            self.rot_speed *= 1.5
        elif speed - abs(self.rot_speed) > 3:
            self.rot_speed *= 1.2
        self.rot_acc = 0
        draw_bullet(self.image_orig , 1 ,33)


    def update(self):
        self.dirty = 1
        # apply rotating friction
        #self.rot_acc += self.rot_speed * PLAYER_FRICTION * 0.01
        self.rot_speed += self.rot_acc
        self.rot = (self.rot + self.rot_speed + 0.5 * self.rot_acc) % 360
        if self.rect.bottom >= HEIGHT - 2:
            if self.rot < 90 :
                self.rot_acc = 0.35
            elif self.rot < 180 :
                self.rot_acc = -0.35
            elif self.rot < 270:
                self.rot_acc = 0.35
            elif self.rot < 360:
                self.rot_acc = -0.35

            if self.rot > 88 and self.rot < 92:
                #self.rot = 90
                self.rot_speed *= 0.3
            elif self.rot > 268 and self.rot < 272:
                #self.rot = 270
                self.rot_speed *= 0.3

            if abs(self.rot_speed) < 0.1:
                if self.rot > 89 and self.rot < 91:
                    self.rot = 90
                    self.rot_speed = 0
                    self.rot_acc = 0
                elif self.rot > 269 and self.rot < 271:
                    self.rot = 270
                    self.rot_speed = 0
                    self.rot_acc = 0

        old_center = self.rect.center
        new_image = py.transform.rotate(self.image_orig , self.rot).convert()
        self.rect = new_image.get_rect()
        self.image = new_image
        self.rect.center = old_center
        now = py.time.get_ticks()
        if now - self.born > 10000:
            self.kill()

        # equation of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.rect.bottom >= HEIGHT:
            self.pos.y = HEIGHT - self.rect.height / 2

        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y


class Player_Tank(py.sprite.DirtySprite):
    def __init__(self):
        py.sprite.DirtySprite.__init__(self)
        self._layer = 1
        self.image_orig = py.Surface((70 , 40)).convert()
        self.color = GREEN
        self.image_orig.fill(self.color)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (10 , HEIGHT - 10)
        self.vel = vec(0 , 0)
        self.acc = vec(0 , GRAVITY)
        self.pos = vec(self.rect.centerx , self.rect.centery)
        self.rot = 0
        self.rot_speed = 0
        self.last_press = py.time.get_ticks()
        self.health = 100
        self.forcex = 0
        self.forcey = 0
        self.last_hit = 0
        class Gun(py.sprite.DirtySprite):
            def __init__(self , game):
                py.sprite.DirtySprite.__init__(self)
                self._layer = 2
                self.rot = 0
                self.rot_speed = 1
                self.power = POWER
                self.image_orig = py.Surface((20 , 80)).convert()
                self.image_orig.set_colorkey(BLACK)
                #self.image_orig.fill(WHITE)
                #self.rectangle = py.draw.rect(self.image_orig , BLACK , game.rect , 10)
                self.image = self.image_orig.copy()
                #self.image.fill(BLACK)
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.midbottom = (game.rect.centerx , game.rect.centery + 30)
                self.game = game
                self.rectangle = py.draw.rect(self.image_orig , BLUE ,py.Rect(5, 0, 10, 40))
                self.last_shot = py.time.get_ticks()
                self.empty_gun = py.time.get_ticks()
                self.vel = vec(0 , 0)




            def update(self):
                self.dirty = 1
                if self.game.health > 0:
                    self.rect.center = (self.game.rect.centerx , self.game.rect.centery - 10 )
                    global ANGLE , POWER
                    self.rot_speed = 0
                    keystate = py.key.get_pressed()
                    if keystate[py.K_LEFT]:
                        self.rot_speed = 1
                        ANGLE =(ANGLE + 1) % 360
                        py.display.update( WIDTH - 100 , 5 ,WIDTH  , 100)
                    elif keystate[py.K_RIGHT]:
                        self.rot_speed = -1
                        ANGLE =(ANGLE - 1) % 360
                        py.display.update( WIDTH - 100 , 5 ,WIDTH  , 100)
                    if keystate[py.K_UP] and self.power < 15:
                        self.power += 0.05
                        py.display.update( 0 , 0 ,100  , 120)
                    elif keystate[py.K_DOWN] and self.power > 0:
                        self.power -= 0.05
                        py.display.update( 0 , 0 ,100  , 120)
                    if self.power < 0:
                        self.power = 0
                    elif self.power > 15:
                        self.power = 15
                    POWER = self.power
                    if keystate[py.K_SPACE]:
                        global EMPTY_GUN_FLASH
                        now = py.time.get_ticks()
                        if now - self.last_shot > 200:
                            self.last_shot = now
                            shoot_sound.play()
                            self.fire()
                            py.display.update( 10 ,100 ,100  , 100)
                        if BULLETS == 0 and py.time.get_ticks() - self.empty_gun > 1000:
                            self.empty_gun = py.time.get_ticks()
                            EMPTY_GUN_FLASH = False
                        elif BULLETS == 0 and py.time.get_ticks() - self.empty_gun > 500:
                            EMPTY_GUN_FLASH = True
                    else:
                        EMPTY_GUN_FLASH = False
                else:
                    self.rect.x += self.vel.x
                    self.rect.y += self.vel.y
                old_center = self.rect.center
                self.rot = (self.rot + self.rot_speed) % 360
                new_image = py.transform.rotate(self.image_orig , self.rot)
                self.image = new_image
                self.rect = self.image.get_rect()
                self.rect.center = old_center


            def fire(self):
                class Bullet(py.sprite.DirtySprite):
                    def __init__(self , game):
                        py.sprite.DirtySprite.__init__(self)
                        self.game = game
                        self.image = py.Surface((5 + LEVEL , 5 + LEVEL )).convert()
                        self.image.set_colorkey(BLACK)
                        #self.image.fill(RED)
                        self.rect = self.image.get_rect()
                        py.draw.circle(self.image , RED , (self.rect.centerx, self.rect.centery), self.rect.height // 2 )
                        self.rect.midtop = self.game.rect.midtop
                        self.power = self.game.power
                        self.born = py.time.get_ticks()

                        # placing bullet at the top of the gun
                        if ANGLE < 180:
                            self.rect.top = self.game.rect.top + 120 / (30 if ANGLE < 15 else 25 if ANGLE > 140 else ANGLE)
                            if ANGLE < 90:
                                self.rect.x = self.game.rect.x + self.game.rect.width - 10
                            elif ANGLE < 130:
                                self.rect.x = self.game.rect.x + 8
                            else:
                                self.rect.x = self.game.rect.x
                        else:
                            self.rect.bottom = self.game.rect.bottom - 3
                            if ANGLE > 270:
                                self.rect.x = self.game.rect.x + self.game.rect.width - ANGLE / 30
                            else:
                                self.rect.x = self.game.rect.x + 8

                        self.acc = vec(0 , GRAVITY)
                        self.vel = vec(self.power * math.cos(ANGLE * math.pi / 180) , - self.power * math.sin(ANGLE * math.pi / 180) )
                        self.pos = vec(self.rect.x , self.rect.y)

                    def update(self):
                        self.dirty = 1
                        self.acc = vec(0 , GRAVITY)


                        if self.rect.bottom >= HEIGHT and self.rect.top< HEIGHT + 2:
                            self.vel.y = -self.vel.y / 2
                            self.acc.x += self.vel.x * PLAYER_FRICTION / 4
                            #self.vel.x += self.vel.x * PLAYER_FRICTION / 8
                            self.acc.y = 0
                            if self.vel.x > -0.1 and self.vel.x < 0.1:
                                self.vel.x = 0
                            if abs(self.vel.y) < 0.01:
                                self.rect.bottom = HEIGHT
                            #self.acc.x += self.vel.x * PLAYER_FRICTION
                        else:
                            self.acc.y = GRAVITY
                        self.vel += self.acc
                        self.pos += self.vel + 0.5 * self.acc

                        self.rect.x = self.pos.x
                        self.rect.y = self.pos.y


                        if self.rect.x > WIDTH or self.rect.x < 0 or self.rect.y < -1000 or py.time.get_ticks() - self.born > 10000:
                            self.kill()

                global BULLETS
                if BULLETS > 0:
                    BULLETS -= 1
                    bullet = Bullet(self)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        self.gun = Gun(self)
        all_sprites.add(self.gun)

    def update(self):
        self.dirty = 1
        if py.time.get_ticks() - self.last_hit < 500:
            self.acc = vec(self.forcex , GRAVITY + self.forcey )
        else:
            self.acc = vec(0 , GRAVITY )
            self.forcex = 0
            self.forcey = 0
        self.rot_acc = 0

        keys = py.key.get_pressed()
        #now = py.time.get_ticks()
        if keys[py.K_a] and self.rect.left > 0:
            # ground motion
            self.acc.x = -0.5
            # air motion
            if self.rect.bottom < HEIGHT:
                self.acc.x = -0.25
                #self.rot_speed = 0.5
                self.rot_acc = 0.1

        if keys[py.K_d] and self.rect.right < WIDTH:
            # ground motion
            self.acc.x = 0.5
            # air motion
            if self.rect.bottom < HEIGHT:
                self.acc.x = 0.25
                #self.rot_speed = -0.5
                self.rot_acc = -0.1
        if keys[py.K_w] and self.rect.top > 10:
            self.vel.y = -1.5
        if keys[py.K_s]:
            self.vel.y = 4

        # .............tank rotation in air....................................

        if not keys[py.K_a] and not keys[py.K_d]:
            if self.rot > 0 and self.rot < 20:
                self.rot_acc = -0.2
            if self.rot > 330 and self.rot < 360:
                self.rot_acc = 0.2
            if abs(self.rot) <= 1:
                self.rot = 0
                self.rot_speed = 0
                self.rot_acc = 0
        old_center = self.rect.center
        x = self.rect.x
        y = self.rect.y
        self.rot_acc += self.rot_speed * PLAYER_FRICTION
        self.rot_speed += self.rot_acc
        self.rot = (self.rot + self.rot_speed + 0.5 * self.rot_acc) % 360
        if self.rot > 10 and self.rot < 20 :
            self.rot = 10
        if self.rot < 350 and self.rot > 320 :
            self.rot = 350

        new_image = py.transform.rotate(self.image_orig , self.rot)
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center



        #if not keys[py.K_w]:
        #    self.acc.y = GRAVITY
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.01:
            self.vel.y = 0

        # ..................ground motion.......................................
        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equation of motion
        self.vel.x += self.acc.x
        if self.rect.bottom < HEIGHT:
            self.vel.y += self.acc.y
        self.pos += self.vel + 0.5 * self.acc

        #if self.rect.bottom < HEIGHT:
        #    self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y
        # ........stop tank going outside the screen...............
        if self.rect.bottom >= HEIGHT:
            if self.vel.y > 0.5:
                self.vel.y *= -0.5
                self.acc.y = 0
            else:
                self.pos.y = HEIGHT - self.rect.height / 2

        if self.rect.left < 0:
            self.pos.x = self.rect.width / 2
        elif self.rect.right > WIDTH:
            self.pos.x = WIDTH - self.rect.width / 2

    def draw_health_bar(self):
        draw_shield_bar(screen , 10 , 170 , 100 , 15 , self.health)

    def explode(self , vx , vy):
            for i in range(50):
                breaks = Break(self.rect.left , self.rect.top ,self.rect.right , self.rect.bottom , self.rect.width // 5 , self.rect.height // 5 , self.color , vx * 2 , min(-12 ,-abs(vy) * 2) ,'bullet')
                all_sprites.add(breaks)
            self.gun.rot_acc = max(vx * vy * 1.5 , 0.5 if vx * vy > 0 else -0.5)
            self.gun.rot_speed = 10 if self.gun.rot_acc > 0 else -10
            self.gun.vel = vec(vx * 3 , - abs(vy * 3))
            self.kill()
            Thread(target = exit).start()





class Target(py.sprite.DirtySprite):
    def __init__(self):
        py.sprite.DirtySprite.__init__(self)
        w = random.randrange(20 ,100)
        self.image = py.Surface((w , w)).convert()
        self.rect = self.image.get_rect()
        self.color = random.choice(colors)
        self.image.fill(self.color)
        self.rect.center = vec(random.randrange(WIDTH / 2 , WIDTH - self.rect.width) , random.randrange(0 , HEIGHT- self.rect.height))
        self.vel = vec(0 , 0.5 if random.random() > 0.5 else -0.5)
        self.acc = vec(0 , GRAVITY)
        self.pos = vec(self.rect.centerx , self.rect.centery)
        #self.last_update = py.time.get_ticks()

    def update(self):
        self.dirty = 1
        # apply friction
        self.acc += self.vel * PLAYER_FRICTION
        # equation of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y


class Break(py.sprite.DirtySprite):
    def __init__(self , x1  , y1  , x2  , y2  ,width = 15 , height = 15 , color = (255 , 255 , 255) , vx = 0 , vy = 0 , hit_type = 'target'):
        py.sprite.DirtySprite.__init__(self)
        self.image = py.Surface((random.randrange(1 ,width) , random.randrange(1 ,height))).convert()
        self.image.fill(color)
        #self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(x1 , x2)
        self.rect.centery = random.randrange(y1 , y2)
        if hit_type == 'target':
            self.vel = vec(vx * random.random(), vy * random.random())
        else:
            self.vel = vec(vx * random.random() if random.random() > 0.5 else -vx * random.random() , vy * random.random())
        self.acc = vec(0 , GRAVITY)
        self.pos = vec(self.rect.centerx , self.rect.centery)
        self.born =  py.time.get_ticks()


    def update(self):
        self.dirty = 1
        #self.rect.y += self.speedY
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        if self.rect.bottom >= HEIGHT:
            self.pos.y = HEIGHT - self.rect.height / 2
            self.vel.y = 0
            self.vel.x *= 0.9
            #self.acc.x += self.vel.x * PLAYER_FRICTION
            if abs(self.vel.x) < 0.01:
                self.vel.x = 0
        if py.time.get_ticks() - self.born > 10000:
            self.kill()

class Enemy_tank(py.sprite.DirtySprite):
    def __init__(self , player ,locx = 'left' if random.random() > 0.5 else 'right' , locy = 'up' if random.random() > 0.5 else 'down'):
        py.sprite.DirtySprite.__init__(self)
        self._layer = 1
        self.image_orig = py.Surface((70 , 40)).convert()
        self.color = (73, 26, 17)
        self.image_orig.fill(self.color)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.loc = locx
        self.force = -0.008 * random.randrange(4 , 20) if self.loc == 'left' else 0.008 * random.randrange(4 , 20)
        self.rect.bottomleft = (-100 if self.loc == 'left' else WIDTH + self.rect.width + 10 ,random.random() * HEIGHT)
        if locy == 'up':
            self.fly = 0
        else:
            self.fly = 1

        self.forcex = 0
        self.forcey = 0
        self.vel = vec(0 , 0)
        self.acc = vec(self.force, GRAVITY)
        self.pos = vec(self.rect.centerx , self.rect.centery)
        self.rot = 0
        self.rot_speed = 0
        self.player = player
        self.health = 100
        self.last_hit = py.time.get_ticks()
        self.born = py.time.get_ticks()
        class Health_Bar(py.sprite.DirtySprite):
            def __init__(self ,game):
                py.sprite.DirtySprite.__init__(self)
                self._layer = 2
                self.image_orig = py.Surface((100 , 10))
                self.image_orig.set_colorkey(BLACK)
                self.image = self.image_orig.copy()
                self.rect = self.image.get_rect()
                self.rect.centerx = game.rect.centerx
                self.rect.centery = game.rect.centery - 70
                self.game = game
                self.health = self.game.health
                self.rot = 0
                self.rot_speed = 0
                self.vel = vec(0 , 0)

            def update(self):
                if self.health > 0:
                    self.rect.centerx = self.game.rect.centerx
                    self.rect.centery = self.game.rect.centery - 70
                    self.draw_shield_bar(self.health)
                else:
                    self.rot += self.rot_speed
                    self.rect.x += self.vel.x
                    self.rect.y += self.vel.y
                    old_center = self.rect.center
                    new_image = py.transform.rotate(self.image_orig , self.rot)
                    new_image.set_colorkey(BLACK)
                    self.image = new_image
                    self.rect = self.image.get_rect()
                    self.rect.center = old_center
                self.dirty = 1
                '''
                if self.game.health > 0:
                    if self.game.player.rect.left < self.game.rect.left and self.game.player.rect.right > self.game.rect.left:
                        self.draw_shield_bar( self.game.rect.left + self.game.player.rect.right - self.game.rect.left , self.game.rect.top - 40 , self.game.rect.width, 10 , self.game.health)
                    elif self.game.player.rect.right >= self.game.rect.right and self.game.player.rect.left <= self.game.rect.right:
                        self.draw_shield_bar( self.game.rect.left + self.game.player.rect.left - self.game.rect.right , self.game.rect.top - 40 , self.game.rect.width, 10 , self.game.health)
                    else:
                        self.draw_shield_bar( self.game.rect.left , self.game.rect.top - 40 , self.game.rect.width, 10 , self.game.health)
                '''


            def draw_shield_bar(self , pct):
                if pct < 0:
                    pct = 0
                fill = (pct/ 100) * self.rect.width
                outline_rect = py.Rect(0 , 0, self.rect.width , self.rect.height)
                fill_rect = py.Rect(0 , 0 ,fill ,self.rect.height)
                py.draw.rect(self.image , BG_COLOR ,py.Rect(0 , 0 ,self.rect.width ,self.rect.height))
                py.draw.rect(self.image , GREEN if pct > 20 else RED ,fill_rect)
                py.draw.rect(self.image , WHITE ,outline_rect , 2)



        self.health_bar = Health_Bar(self)
        all_sprites.add(self.health_bar)

        #self.last_press = py.time.get_ticks()
        class Gun(py.sprite.DirtySprite):
            def __init__(self , game):
                py.sprite.DirtySprite.__init__(self)
                self.game = game
                self._layer = 2
                self.player = game.player
                self.rot = 80
                self.rot_speed = 0
                self.rot_acc = 0
                self.image_orig = py.Surface((80 , 20)).convert()
                self.image_orig.set_colorkey(BLACK)
                #self.image_orig.fill(WHITE)
                self.image = self.image_orig.copy()
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.midbottom = (game.rect.centerx , game.rect.centery + 30)
                self.rectangle = py.draw.rect(self.image_orig , YELLOW ,py.Rect(40, 5, 40, 10))
                self.last_shot = py.time.get_ticks()
                self.shot_time = random.randrange(500 , 2000)
                self.player = game.player
                self.self_explode = 0
                self.vel = vec(0 , 0)



            def update(self):
                self.dirty = 1
                # if enemy died
                if self.game.health <= 0:
                    self.rectangle = py.draw.rect(self.image_orig , YELLOW ,py.Rect(5, 20, 10, 40))
                    self.rot_acc += self.rot_speed * PLAYER_FRICTION * 0.005
                    self.rect.x += self.vel.x
                    self.rect.y += self.vel.y
                if self.game.health > 0:
                    self.rect.center = (self.game.rect.centerx , self.game.rect.centery - 10 )

                    #global ENEMY_ANGLE
                    #ENEMY_ANGLE = (self.rot + 90) % 360
                    #self.rot += 1

                    if self.game.player.rect.centerx >= self.game.rect.centerx and self.game.player.rect.centery <= self.game.rect.centery:
                        self.quad = 'first'
                    elif self.game.player.rect.centerx <= self.game.rect.centerx and self.game.player.rect.centery <= self.game.rect.centery:
                        self.quad = 'second'
                    elif self.game.player.rect.centerx <= self.game.rect.centerx and self.game.player.rect.centery >= self.game.rect.centery:
                        self.quad = 'third'
                    elif self.game.player.rect.centerx >= self.game.rect.centerx and self.game.player.rect.centery >= self.game.rect.centery:
                        self.quad = 'fourth'

                    x = abs(abs(self.game.player.rect.centerx) - abs(self.rect.centerx))
                    y = abs(abs(self.game.player.rect.centery) - abs(self.rect.centery))
                    self.range = (x ** 2 + y ** 2) ** 0.5
                    if self.game.rect.bottom > HEIGHT - 2 and self.game.player.rect.bottom > HEIGHT - 2:
                        self.gap = 45
                    else:
                        self.gap = 0
                    #range = (x ** 2 + y ** 2) ** 0.5
                    if self.quad == 'first':
                        self.angle = (math.asin(y / self.range)) * 180 / math.pi + self.gap
                    elif self.quad == 'second':
                        self.angle = 180 - (math.asin(y / self.range)) * 180 / math.pi - self.gap
                    elif self.quad == 'third':
                        self.angle = 180 + (math.asin(y / self.range)) * 180 / math.pi
                    elif self.quad == 'fourth':
                        self.angle = 360 - (math.asin(y / self.range)) * 180 / math.pi
                    #global ENEMY_ANGLE
                    #ENEMY_ANGLE = self.rot + 90

                    if self.rot > self.angle + 1   :
                        self.rot_acc = -0.2
                    elif self.rot < self.angle - 1:
                        self.rot_acc = 0.2
                    else:
                        self.rot_acc = 0

                    self.rot_acc += self.rot_speed * PLAYER_FRICTION

                self.rot_speed += self.rot_acc

                if abs(self.rot_speed) < 0.1:
                    self.rot_speed = 0
                old_center = self.rect.center
                x = self.rect.x
                y = self.rect.y
                self.rot = (self.rot + self.rot_speed + 0.5 * self.rot_acc) % 360
                new_image = py.transform.rotate(self.image_orig , self.rot)
                self.image = new_image
                self.rect = self.image.get_rect()
                self.rect.center = old_center

                now = py.time.get_ticks()
                if now - self.last_shot > self.shot_time and self.game.health > 0 and self.game.player.health > 0:
                    self.last_shot = now
                    self.shot_time = random.randrange(5000 // LEVEL , 20000 // LEVEL)
                    self.fire()

                # kill turret if enemy died and it move off the screen
                if self.game.health <= 0 and (self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT or py.time.get_ticks() - self.self_explode > 5000):
                    self.kill()


            def fire(self):
                class Bullet(py.sprite.DirtySprite):
                    def __init__(self , game):
                        py.sprite.DirtySprite.__init__(self)
                        self.game = game
                        self.image = py.Surface((5 , 7)).convert()
                        self.image.set_colorkey(BLACK)
                        self.image.fill(RED)
                        self.rect = self.image.get_rect()
                        self.rect.midtop = self.game.rect.midtop
                        self.born = py.time.get_ticks()
                        self.rot =  game.rot % 360
                        if self.rot == 0:
                            self.rot = 0.1
                        # range =  2 * speed * speed * cos(angle) * sin(angle) / gravity

                        range = ((self.rect.centerx - self.game.player.rect.centerx) ** 2 + (self.rect.centery - self.game.player.rect.centery) **2) ** 0.5
                        self.power = 15
                        if self.game.game.rect.bottom > HEIGHT - 2 and self.game.player.rect.bottom > HEIGHT - 2:
                            self.power = (abs((range * GRAVITY ) / ( 2 * math.cos(self.rot * math.pi / 180) *  math.sin((self.rot ) * math.pi / 180))) ** 0.5) * 0.9
                        if self.power > 15:
                            self.power = 15

                        #global ENEMY_ANGLE
                        #ENEMY_ANGLE = self.rot
                        # placing bullet at the top of the gun
                        if self.rot < 180:
                            self.rect.top = self.game.rect.top + 120 / (30 if self.rot < 15 else 25 if self.rot > 140 else self.rot)
                            if self.rot < 90:
                                self.rect.x = self.game.rect.x + self.game.rect.width - 10
                            elif self.rot < 130:
                                self.rect.x = self.game.rect.x + 8
                            else:
                                self.rect.x = self.game.rect.x
                        else:
                            self.rect.bottom = self.game.rect.bottom - 3
                            if self.rot > 270:
                                self.rect.x = self.game.rect.x + self.game.rect.width - self.rot / 30
                            else:
                                self.rect.x = self.game.rect.x + 8

                        self.acc = vec(0 , GRAVITY)
                        self.vel = vec(self.power * math.cos(self.rot * math.pi / 180) , - self.power * math.sin(self.rot * math.pi / 180) )
                        self.pos = vec(self.rect.x , self.rect.y)

                    def update(self):
                        self.dirty = 1
                        self.acc = vec(0 , GRAVITY)


                        if self.rect.bottom >= HEIGHT and self.rect.top< HEIGHT + 2:
                            self.vel.y = -self.vel.y / 2
                            self.acc.x += self.vel.x * PLAYER_FRICTION / 4
                            #self.vel.x += self.vel.x * PLAYER_FRICTION / 8
                            self.acc.y = 0
                            if self.vel.x > -0.1 and self.vel.x < 0.1:
                                self.vel.x = 0
                            if abs(self.vel.y) < 0.01:
                                self.rect.bottom = HEIGHT
                            #self.acc.x += self.vel.x * PLAYER_FRICTION
                        else:
                            if self.game.game.rect.bottom < HEIGHT - 2 and self.game.player.rect.bottom < HEIGHT - 2:
                                self.acc.y = GRAVITY * 0
                        self.vel += self.acc
                        self.pos += self.vel + 0.5 * self.acc

                        self.rect.x = self.pos.x
                        self.rect.y = self.pos.y


                        if self.rect.x > WIDTH or self.rect.x < 0 or self.rect.y < -1000 or py.time.get_ticks() - self.born > 10000:
                            self.kill()





                bullet = Bullet(self)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)

        self.gun = Gun(self)
        all_sprites.add(self.gun)

    def update(self):
        self.dirty = 1
        if py.time.get_ticks() - self.last_hit < 500:
            self.acc = vec((self.force + self.forcex) * self.fly , (self.forcey - abs(self.force)))
        else:
            if self.player.rect.centerx < self.rect.centerx - 100:
                self.acc = vec(-abs(self.force) , GRAVITY * self.fly)
            elif self.player.rect.centerx > self.rect.centerx + 100:
                self.acc = vec(abs(self.force) , GRAVITY * self.fly)
            self.forcex = 0
            self.forcey = 0
        #self.pos = vec(WIDTH // 2 , HEIGHT)
        if self.rect.bottom >= HEIGHT :
            self.pos.y = HEIGHT - self.rect.height / 2
            self.vel.y = 0
        elif self.rect.top <= 50 :
            self.pos.y = 50 + self.rect.height / 2
            self.vel.y *= -0.5
        if self.rect.right >= WIDTH and py.time.get_ticks() - self.born > 10000:
            #self.pos.x = WIDTH - self.rect.width / 2 - 1
            #self.vel.x *= -0.5
            self.acc.x = -0.5
        elif self.rect.left <= 0 and py.time.get_ticks() - self.born > 10000:
            #self.pos.x =  self.rect.width / 2 + 1
            #self.vel.x *= -0.5
            self.acc.x = 0.5
        #self.pos.y =  HEIGHT / 2
        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equation of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc



        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

    def explode(self , vx , vy):
            for i in range(50):
                breaks = Break(self.rect.left , self.rect.top ,self.rect.right , self.rect.bottom , self.rect.width // 5 , self.rect.height // 5 , self.color , vx * 2 , min(-12 ,-abs(vy) * 2) ,'bullet')
                all_sprites.add(breaks)
            self.gun.rot_acc = max(vx * vy * 1.5 , 0.5 if vx * vy > 0 else -0.5)
            self.gun.rot_speed = 3 if self.gun.rot_acc > 0 else -3
            self.gun.vel = vec(vx * 3 , - abs(vy * 3))
            self.kill()
            explode_sound.play()
            #self.game.kill() ....kills automatically..
            self.gun.self_explode = py.time.get_ticks()
            if len(enemies) == 0:
                global LEVEL
                LEVEL += 1
                next_level()
                py.display.update(WIDTH // 2 - 60 , 0 , WIDTH // 2 + 60 , 50)


    def draw_health_bar(self):
        pass







def next_level():
    if LEVEL == 1 or LEVEL == 2 or LEVEL == 3:
        enemy_tank = Enemy_tank(player_tank)
        all_sprites.add(enemy_tank)
        enemies.add(enemy_tank)

    elif LEVEL == 4 or LEVEL == 5:
        for i in range(2):
            enemy_tank = Enemy_tank(player_tank , 'right' if i % 2 == 0 else 'left')
            all_sprites.add(enemy_tank)
            enemies.add(enemy_tank)
    else:
        for i in range(LEVEL // 2):
            enemy_tank = Enemy_tank(player_tank , 'right' if i % 2 == 0 else 'left')
            all_sprites.add(enemy_tank)
            enemies.add(enemy_tank)





# initialize and create screen
os.environ['SDL_VIDEO_CENTERED'] = '1'
py.init()
py.mixer.init()
screen = py.display.set_mode((WIDTH , HEIGHT))
# Create The Backgound
background = py.Surface(screen.get_size())
background = background.convert()
background.fill(BG_COLOR)
clock = py.time.Clock()

# load game sounds
tile_break_sound =[]
for snd in ['tile_break1.wav' , 'tile_break2.wav' , 'tile_break3.wav']:
    tile_break_sound.append(py.mixer.Sound(path.join(snd)))
shoot_sound = py.mixer.Sound(path.join('popcorn.wav'))
explode_sound = py.mixer.Sound(path.join('expmedium2.wav'))

# adding sprites
all_sprites = py.sprite.LayeredDirty()
player_tank = Player_Tank()
all_sprites.add(player_tank)
bullets = py.sprite.Group()
enemies = py.sprite.Group()
enemy_bullets = py.sprite.Group()
targets = py.sprite.Group()
powerups = py.sprite.Group()
for i in range(3):
    target = Target()
    targets.add(target)
    all_sprites.add(target)
all_sprites.clear(screen, background)
'''
enemy_tank = Enemy_tank(player_tank)
all_sprites.add(enemy_tank)
enemies.add(enemy_tank)
'''
next_level()

running = True
# game loop
while running:
    clock.tick(FPS)
    # process
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    # ........................update............................................
    # check player tank bullet hits enemy tank
    hits = py.sprite.groupcollide(enemies , bullets , False , False)
    for hit in hits:
        #print(len(hit))
        hit.health -= 10
        hit.health_bar.health =  hit.health
        hit.health_bar.rot_speed = hits[hit][0].vel.x * hits[hit][0].vel.y
        hit.health_bar.vel = vec(hits[hit][0].vel.x , hits[hit][0].vel.y)

        if hit.health <= 0:
            hit.health = 0
            hit.explode(hits[hit][0].vel.x , hits[hit][0].vel.y)
            hit.kill()
            BULLETS += 10
            player_tank.health += 20
            if player_tank.health >100:
                player_tank.health = 100


        # opposite force on enemy tank after collision
        hit.forcex = hit.forcex + hits[hit][0].vel.x / 2 * 0.007
        hit.forcey = hit.forcey + hits[hit][0].vel.y / 2 * 0.01
        hit.last_hit = py.time.get_ticks()
        # opposite force on bullet after collision
        if hits[hit][0].rect.left <= hit.rect.left + 4   or hits[hit][0].rect.right >= hit.rect.right - 4 :
            hits[hit][0].vel.x *= -0.35
        if hits[hit][0].rect.top <= hit.rect.top or hits[hit][0].rect.bottom >= hit.rect.bottom:
            hits[hit][0].vel.y *= -0.35
        bullets.remove(hits[hit][0])


    # check enemy bullet hits player tank
    if player_tank.health > 0:
        hits = py.sprite.spritecollide(player_tank , enemy_bullets , False)
        for hit in hits:
            player_tank.health -= 10

            py.display.update(10 ,100 ,100 , 100)
            player_tank.draw_health_bar()
            if player_tank.health <= 0:
                player_tank.health = 0
                player_tank.explode(hit.vel.x , hit.vel.y)
                player_tank.kill()
                py.display.update()
            # opposite force on player tank after collision
            player_tank.forcex = player_tank.forcex +  hit.vel.x / 2 * 0.02
            player_tank.forcey = player_tank.forcey + hit.vel.y / 2 * 0.01
            player_tank.last_hit = py.time.get_ticks()
            # opposite force on bullet after collision
            if hit.rect.left <= player_tank.rect.left + 4 or hit.rect.right >= player_tank.rect.right - 4:
                hit.vel.x *= -0.35
            if hit.rect.top <= player_tank.rect.top or hit.rect.bottom >= player_tank.rect.bottom:
                hit.vel.y *= -0.35
            enemy_bullets.remove(hit)


    # check player_tank hit Powerups
    hit = py.sprite.spritecollide(player_tank , powerups , True)
    if hit:
        BULLETS += 1

    # check bullet collision with the targets
    hits = py.sprite.groupcollide(targets ,  bullets , True , False)
    for hit in hits:
        for i in range(5 + hit.rect.width // 2):
            breaks = Break(hit.rect.left , hit.rect.top ,hit.rect.right , hit.rect.bottom , hit.rect.width // 10 , hit.rect.height // 10 , hit.color , hits[hit][0].vel.x , hits[hit][0].vel.y )
            all_sprites.add(breaks)
        #print(abs(hits[hit][0].vel.x) + abs(hits[hit][0].vel.y))
        #print(hit.color)
        # opposite force on bullet after collision
        if hits[hit][0].rect.left < hit.rect.left or hits[hit][0].rect.right > hit.rect.right:
            hits[hit][0].vel.x *= -0.35
        if hits[hit][0].rect.top < hit.rect.top or hits[hit][0].rect.bottom > hit.rect.bottom:
            hits[hit][0].vel.y *= -0.35
        random.choice(tile_break_sound).play()
        target = Target()
        all_sprites.add(target)
        targets.add(target)
        powerup = Powerups(hit.rect.centerx , hit.rect.centery , int(abs(hits[hit][0].vel.x) + abs(hits[hit][0].vel.y)))
        all_sprites.add(powerup)
        powerups.add(powerup)
    all_sprites.update()

    # draw
    screen.fill(BG_COLOR)
    rects = all_sprites.draw(screen)
    display_angle(screen , ANGLE , 60 , WIDTH - 50 , 10)
    display_power(screen ,(POWER / 15) * 100  , 60 , 60 , 10)
    display_bullets(screen ,BULLETS , 25 , 20 , 140)
    display_level(screen ,'Level' + str(LEVEL) , 25 , WIDTH // 2  , 10)
    if player_tank.health == 0:
        display_level(screen , 'You Lose' , 100 , WIDTH // 2 , 200)
    for enemy in enemies:
        enemy.draw_health_bar()
    player_tank.draw_health_bar()
    #display_bullets(screen ,ENEMY_ANGLE , 20, WIDTH - 100  , 100)

    if player_tank.health <= 0:
        py.display.flip()
    else:
        py.display.update(rects)


py.quit()