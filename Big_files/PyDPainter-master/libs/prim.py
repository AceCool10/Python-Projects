#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import math
import numpy as np
from operator import itemgetter
import os.path
import random
import copy

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

config = None

def prim_set_config(config_in):
    global config
    config = config_in

symm_mat = None
symm_mat_num = 0
symm_center = [0,0]
vlines = {}

def onscreen(coords):
    w = config.pixel_width
    h = config.pixel_height
    x,y = coords
    if x >= 0 and x < w and \
       y >= 0 and y < h:
        return True
    else:
        return False

#Check if rectangle is at least partially on screen
def rect_onscreen(rect):
    w = config.pixel_width
    h = config.pixel_height

    lx = rect[0]
    ly = rect[1]
    rx = lx + rect[2]
    ry = ly + rect[3]

    #rectangle is to the left or right of the screen
    if lx > w or rx < 0:
        return False

    #rectangle is above or below the screen
    if ly > h or ry < 0:
        return False

    return True

def add_bounds(coords):
    x,y = coords

    if x < config.fillmode.bounds[0]:
        config.fillmode.bounds[0] = x
    if y < config.fillmode.bounds[1]:
        config.fillmode.bounds[1] = y
    if x > config.fillmode.bounds[2]:
        config.fillmode.bounds[2] = x
    if y > config.fillmode.bounds[3]:
        config.fillmode.bounds[3] = y

def start_shape():
    global vlines
    vlines = {}

def end_shape(screen, color, primprops=None, interrupt=False):
    global vlines
    drawvlines(screen, color, primprops=primprops, interrupt=interrupt)
    vlines = {}

def symm_coords_list(coords, handlesymm=True, interrupt=False):
    n = len(coords)
    coords_symm = np.array([],dtype=np.int)
    symm_len = 0
    last_symm_coords = None
    for i in range(n):
        if interrupt and config.has_event(8) and last_symm_coords != None:
            coords_symm = np.append(coords_symm, last_symm_coords)
        else:
            last_symm_coords = symm_coords(coords[i], handlesymm=handlesymm, interrupt=interrupt)
            coords_symm = np.append(coords_symm, last_symm_coords)
        if i == 0:
            symm_len = len(coords_symm)//2

    coords_symm = coords_symm.reshape(n,symm_len,2).transpose(1,0,2)
    return coords_symm


def symm_coords(coords, handlesymm=True, interrupt=False):
    global symm_mat
    global symm_mat_num
    global symm_center
    x,y = coords
    newcoords = []
    newcoords.append(coords)
    if not handlesymm:
        return newcoords

    if config.symm_on:
        if config.symm_mode == 0:
            c = config.symm_center
 
            if config.symm_num > 0:
                if config.symm_type == 1:
                    x1 = (c[0]*2) - x
                    newcoords.append((x1, y))
                if symm_mat_num != config.symm_num or symm_center != c:
                    symm_mat_num = config.symm_num
                    symm_center = c
                    q = 2.0 * math.pi / config.symm_num
                    #recalculate matrix
                    trans1   = np.matrix([[    1,     0, 0],
                                          [    0,     1, 0],
                                          [-c[0], -c[1], 1]])
                    rot      = np.matrix([[ math.cos(q), math.sin(q), 0],
                                          [-math.sin(q), math.cos(q), 0],
                                          [           0,           0, 1]])
                    trans2   = np.matrix([[    1,     0, 0],
                                          [    0,     1, 0],
                                          [ c[0],  c[1], 1]])
                    symm_mat = trans1 @ rot @ trans2
                xf,yf = x,y
                for i in range(config.symm_num-1):
                    if interrupt and config.has_event(8):
                        newcoords.append((int(round(x)), int(round(y))))
                    else:
                        xyvect = np.matmul(np.matrix([[xf,yf,1]]),symm_mat)
                        xf = xyvect[0,0]
                        yf = xyvect[0,1]
                        newcoords.append((int(round(xf)),int(round(yf))))

                        #mirror
                        if config.symm_type == 1:
                            x1 = (c[0]*2) - xf
                            newcoords.append((int(round(x1)), int(round(yf))))
        #tiled
        elif config.symm_mode == 1:
            numcols = (config.pixel_width // config.symm_width) + 1
            numrows = (config.pixel_height // config.symm_height) + 1
            newcoords = []
            x0 = x
            for xr in range(numcols):
                y0 = y
                for yr in range(numrows):
                    newcoords.append((x0,y0))
                    y0 = y0 + config.symm_height
                x0 = x0 + config.symm_width
            x0 = x
            for xr in range(numcols):
                y0 = y
                x0 = x0 - config.symm_width
                for yr in range(numrows):
                    newcoords.append((x0,y0))
                    y0 = y0 + config.symm_height
            x0 = x
            for xr in range(numcols):
                y0 = y
                for yr in range(numrows):
                    y0 = y0 - config.symm_height
                    newcoords.append((x0,y0))
                x0 = x0 + config.symm_width
            x0 = x
            for xr in range(numcols):
                y0 = y
                x0 = x0 - config.symm_width
                for yr in range(numrows):
                    y0 = y0 - config.symm_height
                    newcoords.append((x0,y0))
    return newcoords

class BrushCache:
    """This class models brush images that are ready to stamp on the screen"""
    def __init__(self):
        self.image = []
        self.type = []
        self.bgcolor = []
        for i in range(256):
            self.image.append(None)
            self.type.append(-1)
            self.bgcolor.append(-1)

class Brush:
    """This class models a brush that can be stamped on the screen"""
    CUSTOM = 0
    CIRCLE = 1
    SQUARE = 2
    SPRAY = 3

    def __init__(self, type=CIRCLE, size=1, screen=None, bgcolor=0, coordfrom=None, coordto=None):
        if type == Brush.CUSTOM:
            x1,y1 = coordfrom
            x2,y2 = coordto

            if x1 > x2:
                x1, x2 = x2, x1

            if y1 > y2:
                y1, y2 = y2, y1

            w = x2-x1+1
            h = y2-y1+1

            self.image = pygame.Surface((w, h),0, config.pixel_canvas)
            self.image.set_palette(config.pal)
            self.image.blit(screen, (0,0), (x1,y1,x2,y2))
            self.image.set_colorkey(bgcolor)
            self.__type = type
            self.bgcolor = bgcolor
            self.image_orig = self.image.copy()
            self.bgcolor_orig = bgcolor
            self.handle = [w//2, h//2]
            self.__size = (w + h) // 2
            self.rect = [-self.handle[0], -self.handle[1], w, h]
        else:
            self.image = None
            self.rect = [0,0,size,size]
            self.__type = type
            self.bgcolor = bgcolor
            self.image_orig = None
            self.bgcolor_orig = bgcolor
            self.__size = size
            self.handle = [size//2, size//2]
            self.rect = [-self.handle[0], -self.handle[1],
                         size, size]

        self.cache = BrushCache()

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        if size < 1:
            size = 1
            if self.type == Brush.SQUARE or self.type == Brush.SPRAY:
                self.__type = Brush.CIRCLE
        elif size > 100:
            size = 100
        self.__size = size
        self.cache = BrushCache()
        if self.type == Brush.SQUARE:
            self.handle = [(size+1)//2, (size+1)//2]
            self.rect = [-self.handle[0], -self.handle[1],
                         size, size]
        elif self.type == Brush.CIRCLE or self.type == Brush.SPRAY:
            if size == 1:
                self.handle = [0,0]
                self.rect = [0,0,1,1]
            else:
                self.handle = [size, size]
                self.rect = [-self.handle[0], -self.handle[1],
                             size*2, size*2]

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        if type != self.__type:
            self.__type = type
            self.size = self.__size  #recalc handle and wipe cache

    def render_image(self, color):
        if self.type == Brush.CUSTOM:
            #convert brush image to single color
            image = self.image_orig.copy()
            image.set_palette(config.pal)
            surf_array = pygame.surfarray.pixels2d(image)
            bgcolor = self.bgcolor_orig
            if bgcolor == color:
                bgcolor = (color+1) % config.NUM_COLORS
                tfarray = np.not_equal(surf_array, self.bgcolor_orig)
                surf_array[tfarray] = color
                surf_array[np.logical_not(tfarray)] = bgcolor
            else:
                surf_array[np.not_equal(surf_array, bgcolor)] = color
            surf_array = None
            self.color = color
            image.set_colorkey(bgcolor)
            return image
        elif self.type == Brush.CIRCLE:
            if self.size == 1:
                image = pygame.Surface((1,1),0, config.pixel_canvas)
                image.set_palette(config.pal)
                image.fill(color)
            else:
                image = pygame.Surface((self.size*2+1, self.size*2+1),0, config.pixel_canvas)
                image.set_palette(config.pal)
                if color == 0:
                    image.fill(1)
                    image.set_colorkey(1)
                else:
                    image.set_colorkey(0)
                primprops = PrimProps()
                fillcircle(image, color, (self.size, self.size), self.size-1, primprops=primprops)
            return image
        elif self.type == Brush.SQUARE:
            image = pygame.Surface((self.size+1, self.size+1),0, config.pixel_canvas)
            image.set_palette(config.pal)
            if color == 0:
                image.set_colorkey(1)
            else:
                image.set_colorkey(0)
            image.fill(color)
            return image
        elif self.type == Brush.SPRAY:
            image = pygame.Surface((self.size*3+1, self.size*3+1),0, config.pixel_canvas)
            self.handle = [image.get_width()//2, image.get_height()//2]
            image.set_palette(config.pal)
            
            if color == 0:
                image.set_colorkey(1)
                image.fill(1)
            else:
                image.set_colorkey(0)

            if self.size == 1:
                image.set_at((0,1), color)
                image.set_at((2,0), color)
                image.set_at((2,2), color)
            elif self.size == 2:
                image.set_at((3,0), color)
                image.set_at((0,2), color)
                image.set_at((3,3), color)
                image.set_at((6,3), color)
                image.set_at((3,5), color)
            elif self.size > 2:
                old_state = random.getstate()
                random.seed(self.size)
                for i in range(0, self.size * 3):
                    image.set_at(config.airbrush_coords(self.handle[0], self.handle[1], size=self.size*1.5), color)
                random.setstate(old_state)

            return image

    def draw(self, screen, color, coords, handlesymm=True, primprops=None):
        if not rect_onscreen([coords[0]+self.rect[0],
                              coords[1]+self.rect[1],
                              self.rect[2],
                              self.rect[3]]):
            return

        image = None
        if primprops == None:
            primprops = config.primprops
        drawmode = primprops.drawmode.value

        #handle matte drawing with background
        if drawmode == DrawMode.MATTE and color == self.bgcolor:
            drawmode = DrawMode.COLOR

        if drawmode == DrawMode.MATTE:
            if self.image != None:
                image = self.image
                image.set_colorkey(self.bgcolor_orig)
        elif drawmode == DrawMode.REPLACE:
            if self.image != None:
                if color == self.bgcolor:
                    image = pygame.Surface(self.image.get_size(), 0, self.image)
                    image.set_palette(config.pal)
                    image.fill(color)
                else:
                    image = self.image
                    image.set_colorkey(None)
        elif drawmode == DrawMode.COLOR or drawmode == DrawMode.CYCLE:
            if self.cache.image[color] == None:
                self.cache.image[color] = self.render_image(color)
            image = self.cache.image[color]

        if config.cycling and not image is None:
            image.set_palette(config.pal)

        for coord in symm_coords(coords, handlesymm=handlesymm):
            x,y = coord
            if not image is None:
                screen.blit(image, (x - self.handle[0], y - self.handle[1]))

class CoordList:
    """This class stores a list of coordinates and renders it in the selected drawmode"""
    def __init__(self, numlists):
        self.numlists = numlists
        self.coordlist = []
        for i in range(0,numlists):
            self.coordlist.append([])

    def append(self, listnum, coord):
        self.coordlist[listnum].append(coord)

    def prepend(self, listnum, coord):
        self.coordlist[listnum].insert(0, coord)

    def draw(self, screen, color, drawmode=-1, xormode=-1, handlesymm=-1, interrupt=-1, primprops=None):
        numpoints = 0
        numcolors = 0
        pointspercolor = 0
        cyclemode = False
        cur_crange = None
        if primprops == None:
            drawmode = config.drawmode.value if drawmode == -1 else drawmode
            if xormode == True:
                primprops = PrimProps()
            else:
                primprops = config.primprops
        else:
            drawmode = primprops.drawmode.value if drawmode == -1 else drawmode

        xormode = primprops.xor if xormode == -1 else xormode
        handlesymm = primprops.handlesymm if handlesymm == -1 else handlesymm
        interrupt = primprops.interrupt if interrupt == -1 else interrupt

        #handle color cycling
        arange = []
        if drawmode == DrawMode.CYCLE: 
            for crange in config.cranges:
                if crange.is_active() and color >= crange.low and color <= crange.high:
                    cyclemode = True
                    arange = crange.get_range()
                    numcolors = len(arange)
                    cur_crange = crange
                    color = arange[0]

        for i in range(0,self.numlists):
            numpoints += len(self.coordlist[i])
        numpoints += 1

        if cyclemode:
            pointspercolor = numpoints / numcolors

        currpoint = -1
        for i in range(0,self.numlists):
            for c in self.coordlist[i]:
                currpoint += 1
                if cyclemode and pointspercolor > 0:
                    color = arange[int(currpoint / pointspercolor)]
                if primprops.continuous and primprops.drawmode.spacing == DrawMode.N_TOTAL and numpoints > 1 and currpoint != 0 and int(currpoint / ((numpoints-1) / primprops.drawmode.n_total_value)) == int((currpoint-1) / ((numpoints-1) / primprops.drawmode.n_total_value)):
                    continue
                if not primprops.continuous and primprops.drawmode.spacing == DrawMode.N_TOTAL and numpoints > 1 and currpoint != 0 and currpoint != numpoints-1 and int(currpoint / ((numpoints-1) / (primprops.drawmode.n_total_value-1))) == int((currpoint+1) / ((numpoints-1) / (primprops.drawmode.n_total_value-1))):
                    continue
                if primprops.drawmode.spacing == DrawMode.EVERY_N and currpoint % primprops.drawmode.every_n_value != 0:
                    continue

                if xormode:
                    if c[0] >= 0 and c[0] < screen.get_width() and \
                       c[1] >= 0 and c[1] < screen.get_height():
                        screen.set_at(c, screen.map_rgb(config.pixel_canvas.get_at(c))^(config.NUM_COLORS-1))
                else:
                    if primprops.drawmode.spacing == DrawMode.AIRBRUSH:
                        for j in range(primprops.drawmode.airbrush_value):
                            config.brush.draw(screen, color, config.airbrush_coords(c[0],c[1]), handlesymm=handlesymm, primprops=PrimProps(drawmode=drawmode))
                    else:
                        config.brush.draw(screen, color, c, handlesymm=handlesymm, primprops=PrimProps(drawmode=drawmode))

                if interrupt and config.has_event():
                    return

                config.try_recompose()


class DrawMode:
    """This class describes the drawing modes for line drawing"""
    MATTE = 1
    COLOR = 2
    REPLACE = 3
    SMEAR = 4
    SHADE = 5
    BLEND = 6
    CYCLE = 7
    SMOOTH = 8
    TINT = 9
    HBRITE = 10
    LABEL_STR = ["","Matte","Color","Repl","Smear","Shade","Blend","Cycle","Smooth","Tint","HBrite"]

    CONTINUOUS = 0
    N_TOTAL = 1
    EVERY_N = 2
    AIRBRUSH = 3

    def __init__(self, value=2):
        self.value = value
        self.n_total_value = 20
        self.every_n_value = 8
        self.airbrush_value = 16
        self.spacing = DrawMode.CONTINUOUS

    def __str__(self):
        return DrawMode.LABEL_STR[self.value]


class FillMode:
    """This class describes the fill modes for solid shapes"""
    SOLID = 0
    TINT = 1
    BRUSH = 2
    WRAP = 3
    PERSPECTIVE = 4
    PATTERN = 5
    VERTICAL = 6
    VERT_FIT = 7
    HORIZONTAL = 8
    HORIZ_FIT = 9
    LABEL_STR = ["Solid","Tint","Brush","Wrap","Perspective","Pattern",
                 "\x88\x89","\x8a\x8b","\x8c\x8d","\x8e\x8f"]
    NOBOUNDS = [65535,65535,-1,-1]
    ORDER4 = np.matrix([[ 0, 8, 2,10],
                        [12, 4,14, 6],
                        [ 3,11, 1, 9],
                        [15, 7,13, 5]], dtype="int8")

    def __init__(self, value=0):
        self.brush = None
        self.value = value
        self.gradient_dither = 4
        self.bounds = copy.copy(FillMode.NOBOUNDS)
        self.predraw = True
    def __str__(self):
        return FillMode.LABEL_STR[self.value]


class PrimProps:
    """This class stores properties for drawing and filling objects"""
    def __init__(self, drawmode=2, fillmode=0):
        self.color = 1
        self.drawmode = DrawMode(drawmode)
        self.fillmode = FillMode(fillmode)
        self.xor = False
        self.coordsonly = False
        self.handlesymm = False
        self.interrupt = False
        self.continuous = False


def calc_ellipse_curves(coords, width, height, handlesymm=True):
    ccoords = []

    #Calculate curve segment coords
    xc,yc = coords
    controlw = width*716//1000
    controlh = height*716//1000
    ccoords = [(xc+width,yc),(xc,yc+height),(xc+controlw,yc+controlh),
               (xc,yc+height),(xc-width,yc),(xc-controlw,yc+controlh),
               (xc-width,yc),(xc,yc-height),(xc-controlw,yc-controlh),
               (xc,yc-height),(xc+width,yc),(xc+controlw,yc-controlh)]

    #run curve coords through symmetry calulations
    coords_out = symm_coords_list(ccoords, handlesymm=handlesymm)
    return coords_out

def drawellipse (screen, color, coords, width, height, filled=0, drawmode=-1, interrupt=False):
    if filled == 1:
        fillellipse(screen, color, coords, width, height, interrupt=interrupt)
        return

    ecurves = calc_ellipse_curves(coords, width, height)
    for i in range(len(ecurves)):
        cl = CoordList(12)
        for j in range (0,12,3):
            if interrupt and config.has_event():
                return
            coordfrom = (ecurves[i][j][0], ecurves[i][j][1])
            coordto = (ecurves[i][j+1][0], ecurves[i][j+1][1])
            coordcontrol = (ecurves[i][j+2][0], ecurves[i][j+2][1])
            cl.coordlist[j:j+3] = drawcurve(screen, color, coordfrom, coordto, coordcontrol, coordsonly=True, handlesymm=False)
        primprops = copy.copy(config.primprops)
        primprops.continuous = True
        cl.draw(screen, color, drawmode=drawmode, handlesymm=False, interrupt=interrupt, primprops=primprops)


def fillellipse (screen, color, coords, width, height, interrupt=False, primprops=None):
    if primprops == None:
        primprops = config.primprops
        handlesymm = True
    else:
        handlesymm = primprops.handlesymm

    xc,yc = coords

    if width == 0 and height == 0:
        fillrect(screen, color, (xc,yc), (xc,yc))
        return

    ecurves = calc_ellipse_curves(coords, width, height, handlesymm=handlesymm)
    for i in range(len(ecurves)):
        cl = CoordList(12)
        for j in range (0,12,3):
            coordfrom = (ecurves[i][j][0], ecurves[i][j][1])
            coordto = (ecurves[i][j+1][0], ecurves[i][j+1][1])
            coordcontrol = (ecurves[i][j+2][0], ecurves[i][j+2][1])
            cl.coordlist[j:j+3] = drawcurve(screen, color, coordfrom, coordto, coordcontrol, coordsonly=True, handlesymm=False)
            cl0 = [item for sublist in cl.coordlist for item in sublist]
            npcl = np.array(cl0, dtype=np.int)
            sl = {}
            for j in range(0,npcl.shape[0]):
                x,y = npcl[j]
                if y in sl:
                    if sl[y][0] > x:
                        sl[y][0] = x
                    elif sl[y][1] < x:
                        sl[y][1] = x
                else:
                    sl[y] = [x,x]

        #find maxima
        config.fillmode.bounds = copy.copy(FillMode.NOBOUNDS)
        sslk = sorted(sl.keys())
        config.fillmode.bounds[1] = sslk[0]
        config.fillmode.bounds[3] = sslk[-1]
        for sly in sslk:
            if sl[sly][0] < config.fillmode.bounds[0]:
                config.fillmode.bounds[0] = sl[sly][0]
            if sl[sly][1] > config.fillmode.bounds[2]:
                config.fillmode.bounds[2] = sl[sly][1]

        start_shape()
        for sly in sslk:
            hline(screen, color, sly, sl[sly][0], sl[sly][1], primprops=primprops)
            if interrupt and config.has_event():
                return
            config.try_recompose()
        end_shape(screen, color, interrupt=interrupt, primprops=primprops)
        

def drawcircle(screen, color, coords_in, radius, filled=0, drawmode=-1, interrupt=False):
    if filled == 1:
        fillcircle(screen, color, coords_in, radius, interrupt=interrupt)
        return

    coords_list = symm_coords(coords_in)
    for coords in coords_list:
        cl = CoordList(8)

        #midpoint circle algorithm
        x0,y0 = coords;
        x = 0
        y = radius
        err = (5 - radius*4)/4

        cl.append(0, (x0 + y, y0    ))
        cl.append(2, (x0    , y0 + y))
        cl.append(4, (x0 - y, y0    ))
        cl.append(6, (x0    , y0 - y))

        while x < y:
            if interrupt and config.has_event():
                return
            x = x + 1
            if err < 0:
                err += 2*x + 1
            else:
                y -= 1
                err += 2*(x-y) + 1

            cl.append (0, (x0 + y, y0 + x))
            cl.prepend(1, (x0 + x, y0 + y))
            cl.append (2, (x0 - x, y0 + y))
            cl.prepend(3, (x0 - y, y0 + x))
            cl.append (4, (x0 - y, y0 - x))
            cl.prepend(5, (x0 - x, y0 - y))
            cl.append (6, (x0 + x, y0 - y))
            cl.prepend(7, (x0 + y, y0 - x))

        primprops = copy.copy(config.primprops)
        primprops.continuous = True
        cl.draw(screen, color, drawmode=drawmode, handlesymm=False, interrupt=interrupt, primprops=primprops)

def fillcircle(screen, color, coords_in, radius, interrupt=False, primprops=None):
    handlesymm = True
    if primprops != None:
        handlesymm = primprops.handlesymm

    coords_list = symm_coords(coords_in, handlesymm)
    for coords in coords_list:
        if interrupt and config.has_event():
            return
        x0,y0 = coords;
        x = 0
        y = radius
        err = (5 - radius*4)//4
        config.fillmode.bounds = [x0-radius, y0-radius, x0+radius, y0+radius]

        start_shape()
        hline(screen, color, y0, x0-y, x0+y, interrupt=interrupt, primprops=primprops)

        while x < y:
            x = x + 1
            if err < 0:
                err += 2*x + 1
            else:
                y -= 1
                err += 2*(x-y) + 1

            hline(screen, color, y0 + y, x0 - x, x0 + x, interrupt=interrupt, primprops=primprops)
            hline(screen, color, y0 - y, x0 - x, x0 + x, interrupt=interrupt, primprops=primprops)
            hline(screen, color, y0 + x, x0 - y, x0 + y, interrupt=interrupt, primprops=primprops)
            hline(screen, color, y0 - x, x0 - y, x0 + y, interrupt=interrupt, primprops=primprops)
            if interrupt and config.has_event():
                return
            config.try_recompose()
        end_shape(screen, color, interrupt=interrupt, primprops=primprops)


def drawline_symm(screen, color, coordfrom, coordto, xormode=False, drawmode=-1, coordsonly=False, handlesymm=False, interrupt=False, skiplast=False):
    if (xormode and not handlesymm):
        coordfrom_list = [coordfrom]
        coordto_list = [coordto]
    else:
        coordfrom_list = symm_coords(coordfrom)
        coordto_list = symm_coords(coordto)
    for i in range(len(coordfrom_list)):
        if interrupt and config.has_event():
            return
        drawline(screen, color, coordfrom_list[i], coordto_list[i], xormode=xormode, drawmode=drawmode, coordsonly=False, handlesymm=False, interrupt=interrupt, skiplast=skiplast)


def drawline(screen, color, coordfrom, coordto, xormode=False, drawmode=-1, coordsonly=False, handlesymm=False, interrupt=False, skiplast=False):
    x,y = coordfrom
    x2,y2 = coordto

    cl = CoordList(1)

    #Bresenham line drawing algorithm thanks to:
    # http://tech-algorithm.com/articles/drawing-line-using-bresenham-algorithm/

    w = x2 - x
    h = y2 - y
    dx1 = 0
    dy1 = 0
    dx2 = 0
    dy2 = 0

    if w<0:
        dx1 = -1
    elif w>0:
        dx1 = 1
    if h<0:
        dy1 = -1
    elif h>0:
        dy1 = 1
    if w<0:
        dx2 = -1
    elif w>0:
        dx2 = 1

    longest = abs(w)
    shortest = abs(h)
    if not (longest > shortest):
        longest = abs(h)
        shortest = abs(w)
        if (h<0):
            dy2 = -1
        elif h>0:
            dy2 = 1
        dx2 = 0

    numerator = longest // 2
    if skiplast:
        rangehi = longest
    else:
        rangehi = longest+1
    for i in range(0, rangehi):
        cl.append(0, (x,y))
        numerator += shortest
        if not (numerator<longest):
            numerator -= longest
            x += dx1
            y += dy1
        else:
            x += dx2
            y += dy2

    if coordsonly:
        return cl.coordlist[0]

    cl.draw(screen, color, drawmode=drawmode, xormode=xormode, handlesymm=handlesymm, interrupt=interrupt)


#Bresenham Quardric Bezier curve algorithm from:
#http://members.chello.at/easyfilter/bresenham.html
def drawcurveseg(screen, color, coordfrom, coordcontrol, coordto):
    x0,y0 = coordfrom
    x1,y1 = coordcontrol
    x2,y2 = coordto
    sx = x2-x1
    sy = y2-y1
    xx = x0-x1
    yy = y0-y1
    xy = 0
    dx = 0.0
    dy = 0.0
    err = 0.0
    cur = float(xx*sy-yy*sx)
    coordlist = []

    if not (xx*sx <= 0 and yy*sy <= 0):
        return coordlist

    if sx*sx+sy*sy > xx*xx+yy*yy:
        x2 = x0
        x0 = sx+x1
        y2 = y0
        y0 = sy+y1
        cur = -cur

    if cur != 0:
        xx += sx

        if x0 < x2:
            sx = 1
        else:
            sx = -1

        xx *= sx
        yy += sy

        if y0 < y2:
            sy = 1
        else:
            sy = -1

        yy *= sy
        xy = 2*xx*yy
        xx *= xx
        yy *= yy

        if cur*sx*sy < 0:
            xx = -xx
            yy = -yy
            xy = -xy
            cur = -cur

        dx = 4.0*sy*cur*(x1-x0)+xx-xy
        dy = 4.0*sx*cur*(y0-y1)+yy-xy
        xx += xx
        yy += yy
        err = dx+dy+xy

        while True:
            coordlist.append((x0,y0))
            if x0 == x2 and y0 == y2:
                return coordlist
            y1 = 2.0*err < dx
            if 2.0*err > dy:
                x0 += sx
                dx -= float(xy)
                dy += float(yy)
                err += float(dy)
            if y1:
                y0 += sy
                dy -= float(xy)
                dx += float(xx)
                err += float(dx)
            if dy >= dx:
                break

    #drawline(screen, color, (x0,y0), (x2,y2))
    coordlist.extend(drawline(screen, color, (x0,y0), (x2,y2), coordsonly=True))
    
    return coordlist


def convert_curve_control(coordfrom, coordto, coordcontrol):
    #make coordcontrol a point on the curve
    x0,y0 = coordfrom
    x1,y1 = coordcontrol
    x2,y2 = coordto
    mx = (x0+x2) // 2
    my = (y0+y2) // 2
    dx = (x1-mx) * 2
    dy = (y1-my) * 2
    xout = dx + mx
    yout = dy + my
    return int(xout), int(yout)


#from: http://stackoverflow.com/questions/31757501/pixel-by-pixel-b%C3%A9zier-curve
def drawcurve(screen, color, coordfrom, coordto, coordcontrol, drawmode=-1, coordsonly=False, handlesymm=True, interrupt=False):
    coordfrom_list = symm_coords(coordfrom, handlesymm)
    coordcontrol_list = symm_coords(coordcontrol, handlesymm)
    coordto_list = symm_coords(coordto, handlesymm)
    for j in range(len(coordfrom_list)):
        if interrupt and config.has_event():
            if coordsonly:
                return []
            else:
                return
        x0,y0 = coordfrom_list[j]
        x1,y1 = convert_curve_control(coordfrom_list[j], coordto_list[j], coordcontrol_list[j])
        x2,y2 = coordto_list[j]
        x = x0-x1
        y = y0-y1
        t = float(x0-2*x1+x2)
        r = 0.0

        cl = CoordList(3)

        if x*(x2-x1) > 0:
            if y*(y2-y1) > 0:
                if abs((y0-2*y1+y2)/t*x) > abs(y):
                    x0 = x2
                    x2 = x+x1
                    y0 = y2
                    y2 = y+y1

            t = (x0-x1)/t
            r = (1-t)*((1-t)*y0+2.0*t*y1)+t*t*y2
            t = (x0*x2-x1*x1)*t/(x0-x1)
            x = int(round(t))
            y = int(round(r))
            r = (y1-y0)*(t-x0)/(x1-x0)+y0
            cl.coordlist[0] = drawcurveseg(screen, color, (x0,y0), (x,int(round(r))), (x,y))
            r = (y1-y2)*(t-x2)/(x1-x2)+y2
            x0 = x
            x1 = x
            y0 = y
            y1 = int(round(r))

        if (y0-y1)*(y2-y1) > 0:
            t = float(y0-2*y1+y2)
            t = (y0-y1)/t
            r = (1-t)*((1-t)*x0+2.0*t*x1)+t*t*x2
            t = (y0*y2-y1*y1)*t/(y0-y1)
            x = int(round(r))
            y = int(round(t))
            r = (x1-x0)*(t-y0)/(y1-y0)+x0
            cl.coordlist[2] = drawcurveseg(screen, color, (x0,y0), (int(round(r)),y), (x,y))
            r = (x1-x2)*(t-y2)/(y1-y2)+x2
            x0 = x
            x1 = int(round(r))
            y0 = y
            y1 = y

        cl.coordlist[1] = drawcurveseg(screen, color, (x0,y0), (x1,y1), (x2,y2))

        #sort curve segments

        #find "from" point
        for i in range(0,3):
            if len(cl.coordlist[i]) > 0:
                if cl.coordlist[i][0] == coordfrom_list[j]:
                    cl.coordlist[i], cl.coordlist[0] = cl.coordlist[0], cl.coordlist[i]
                    break
                elif cl.coordlist[i][-1] == coordfrom_list[j]:
                    cl.coordlist[i], cl.coordlist[0] = cl.coordlist[0], list(reversed(cl.coordlist[i]))
                    break

        #find "to" point
        for i in range(0,3):
            if len(cl.coordlist[i]) > 0:
                if cl.coordlist[i][0] == coordto_list[j]:
                    cl.coordlist[i], cl.coordlist[2] = cl.coordlist[2], list(reversed(cl.coordlist[i]))
                    break
                elif cl.coordlist[i][-1] == coordto_list[j]:
                    cl.coordlist[i], cl.coordlist[2] = cl.coordlist[2], cl.coordlist[i]
                    break

        #swap center if needed
        if len(cl.coordlist[1]) > 0:
            if len(cl.coordlist[0]) > 0:
                if cl.coordlist[0][-1] != cl.coordlist[1][0]:
                    cl.coordlist[1].reverse()

        if coordsonly:
            return cl.coordlist

        cl.draw(screen, color, drawmode=drawmode, handlesymm=False, interrupt=interrupt)


def drawrect(screen, color, coordfrom, coordto, filled=0, xormode=False, drawmode=-1, handlesymm=True, interrupt=False):
    if filled:
        if handlesymm:
            fillrect_symm(screen, color, coordfrom, coordto, xormode=xormode, interrupt=interrupt)
        else:
            fillrect(screen, color, coordfrom, coordto, interrupt=interrupt)
        return
    x1,y1 = coordfrom
    x2,y2 = coordto

    drawpoly(screen, color, [(x1,y1), (x2,y1), (x2,y2), (x1,y2), (x1,y1)], xormode=xormode, drawmode=drawmode, handlesymm=handlesymm, interrupt=interrupt, skiplast=True)


def fillrect_symm(screen, color, coordfrom, coordto, xormode=False, handlesymm=True, interrupt=False):
    fillrect(screen, color, coordfrom, coordto, interrupt=interrupt)
    x1,y1 = coordfrom
    x2,y2 = coordto

    rectlist = [[x1,y1],[x2,y1],[x2,y2],[x1,y2],[x1,y1]]
    rectlist_symm = symm_coords_list(rectlist, handlesymm)

    for i in range(1,len(rectlist_symm)):
        fillpoly(screen, color, rectlist_symm[i], handlesymm=False, interrupt=interrupt)
        if interrupt and config.has_event():
            return
        config.try_recompose()

def add_vline(y, xs1, xs2):
    for x in range(xs1,xs2+1):
        # append coords to vertical line lists
        if x in vlines:
            vlfound = False
            for vlx in vlines[x]:
                if y >= vlx[0] and y <= vlx[1]:
                    #fragment already in list
                    vlfound = True
                    break
                elif vlx[0]-1 == y:
                    #extend fragment up
                    vlx[0] = y
                    vlfound = True
                    break
                elif vlx[1]+1 == y:
                    #extend fragment down
                    vlx[1] = y
                    vlfound = True
                    break
            if not vlfound:
                #new fragment
                vlines[x].append([y,y])
        else:
            vlines[x] = [[y,y]]

def hline_SOLID(surf_array, color, y, xs1, xs2):
    if surf_array.dtype == np.uint8:
        #indexed color
        surf_array[xs1:xs2+1,y] = color
    else:
        #true color
        surf_array[xs1:xs2+1,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])

def hline_BRUSH(surf_array, y, x1, x2, xs1, xs2):
    if config.brush.image == None:
        hline_SOLID(surf_array, config.color, y, xs1, xs2)
        return

    brush_array = pygame.surfarray.pixels2d(config.brush.image)
    bw,bh = config.brush.image.get_size()
    y1 = config.fillmode.bounds[1]
    y2 = config.fillmode.bounds[3]
    h = y2-y1+1
    w = x2-x1+1
    bgcolor = config.brush.bgcolor
    for x in range(xs1, xs2+1):
        color = brush_array[(x-x1)*bw//w, (y-y1)*bh//h]
        if color != bgcolor:
            if surf_array.dtype == np.uint8:
                #indexed color
                surf_array[x,y] = color
        if surf_array.dtype != np.uint8:
            #true color
            surf_array[x,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])

#precalc array for WRAP
MAXCALC = 1024
wrap_calc = []
f=-1.0
while f < 1.0:
    wrap_calc.append(MAXCALC//2 + int(math.asin(f) * MAXCALC / math.pi))
    f += 2.0/MAXCALC

def wrap_func(c, maxc):
    if c < 0:
        return c
    if c <= maxc:
        return wrap_calc[MAXCALC*c//maxc] * maxc // MAXCALC
    else:
        return maxc

def hline_WRAP(surf_array, y, x1, x2, xs1, xs2):
    if config.brush.image == None:
        hline_SOLID(surf_array, config.color, y, xs1, xs2)
        return

    brush_array = pygame.surfarray.pixels2d(config.brush.image)
    bw,bh = config.brush.image.get_size()
    y1 = config.fillmode.bounds[1]
    y2 = config.fillmode.bounds[3]
    h = y2-y1+1
    w = x2-x1+1
    bgcolor = config.brush.bgcolor
    for x in range(xs1, xs2+1):
        color = brush_array[wrap_func((x-x1)*bw//w, bw), wrap_func((y-y1)*bh//h, bh)]
        if color != bgcolor:
            if surf_array.dtype == np.uint8:
                #indexed color
                surf_array[x,y] = color
        if surf_array.dtype != np.uint8:
            #true color
            surf_array[x,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])

def hline_PATTERN(surf_array, y, x1, x2, xs1, xs2):
    if config.brush.image == None:
        hline_SOLID(surf_array, config.color, y, xs1, xs2)
        return

    brush_array = pygame.surfarray.pixels2d(config.brush.image)
    bw,bh = config.brush.image.get_size()
    y1 = config.fillmode.bounds[1]
    y2 = config.fillmode.bounds[3]
    h = y2-y1+1
    w = x2-x1+1
    bgcolor = config.brush.bgcolor
    for x in range(xs1, xs2+1):
        color = brush_array[x%bw, y%bh]
        if color != bgcolor:
            if surf_array.dtype == np.uint8:
                #indexed color
                surf_array[x,y] = color
        if surf_array.dtype != np.uint8:
            #true color
            surf_array[x,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])

def hline(screen, color_in, y, x1, x2, primprops=None, interrupt=False):
    if primprops == None:
        primprops = config.primprops

    #don't draw if off screen
    size = screen.get_size()
    if y<0 or y>=size[1]:
        return
    if x1<0 and x2<0:
        return
    if x1>size[0] and x2>size[0]:
        return

    color = copy.copy(color_in)

    #make sure ascending coords
    if x1 > x2:
        x1,x2 = (x2,x1)
    xs1,xs2 = (x1,x2)

    #clip to edges of screen
    if xs1<0:
        xs1=0
    if xs2>size[0]-1:
        xs2=size[0]-1

    #create array from the surface.
    surf_array = pygame.surfarray.pixels2d(screen)

    if primprops.fillmode.value == FillMode.SOLID or color == config.bgcolor:
        hline_SOLID(surf_array, color, y, xs1, xs2)
    elif primprops.fillmode.value == FillMode.BRUSH:
        hline_BRUSH(surf_array, y, x1, x2,xs1, xs2)
    elif primprops.fillmode.value == FillMode.WRAP:
        hline_WRAP(surf_array, y, x1, x2, xs1, xs2)
    elif primprops.fillmode.value == FillMode.PATTERN:
        hline_PATTERN(surf_array, y, x1, x2, xs1, xs2)
    elif primprops.fillmode.value == FillMode.VERT_FIT:
        if primprops.fillmode.predraw:
            hline_SOLID(surf_array, color, y, xs1, xs2)
        add_vline(y, xs1, xs2)
    elif primprops.fillmode.value >= FillMode.VERTICAL:
        #get color range
        cyclemode = False
        for crange in config.cranges:
            if crange.is_active() and color >= crange.low and color <= crange.high:
                cyclemode = True
                arange = crange.get_range()
                numcolors = len(arange)
                cur_crange = crange
                color = arange[0]
        if cyclemode:
            if primprops.fillmode.value == FillMode.VERTICAL:
                y1 = config.fillmode.bounds[1]
                y2 = config.fillmode.bounds[3]
                numpoints = y2-y1+1
            elif primprops.fillmode.value == FillMode.HORIZONTAL:
                x1 = config.fillmode.bounds[0]
                x2 = config.fillmode.bounds[2]
                numpoints = x2-x1+1
            else:
                numpoints = x2-x1+1
            if primprops.fillmode.gradient_dither >= 0:
                pointspercolor = numpoints / (numcolors)
            else:
                pointspercolor = numpoints / (numcolors-.9)
            ditherfactor = primprops.fillmode.gradient_dither/3.0 * pointspercolor
            for x in range(xs1,xs2+1):
                if primprops.fillmode.gradient_dither >= 0:
                    dither = int((random.random()*ditherfactor)-(ditherfactor/2))
                else:
                    dither = 0
                if pointspercolor > 0:
                    if primprops.fillmode.value >= FillMode.HORIZONTAL:
                        colori = int(int(x2-(x+dither)) / pointspercolor)
                    elif primprops.fillmode.value == FillMode.VERTICAL:
                        colori = int(int(y2-(y+dither)) / pointspercolor)
                    if primprops.fillmode.gradient_dither < 0:
                        if primprops.fillmode.value >= FillMode.HORIZONTAL:
                            if FillMode.ORDER4[x%4, y%4] > (16 - (16 * (x2-x) / pointspercolor)%16):
                                colori += 1
                        elif primprops.fillmode.value == FillMode.VERTICAL:
                            if FillMode.ORDER4[x%4, y%4] > (16 - (16 * (y2-y) / pointspercolor)%16):
                                colori += 1
                    if colori >= len(arange):
                        colori = len(arange) - 1
                    elif colori < 0:
                        colori = 0
                    color = arange[colori]
                if screen.get_bytesize() == 1:
                    #indexed color
                    surf_array[x,y] = color
                else:
                    #true color
                    surf_array[x,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])
        else:
            hline_SOLID(surf_array, color, y, xs1, xs2)

    #free array and unlock surface
    surf_array = None


def drawvlines(screen, color, primprops=None, interrupt=False):
    global vlines
    if primprops == None:
        primprops = config.primprops

    if primprops.fillmode.value == FillMode.VERT_FIT:
        for x in vlines:
            vlines[x].sort()
            #collapse scanline fragments
            i = 0
            while i < len(vlines[x]):
                j = i+1
                while j < len(vlines[x]):
                    y1i,y2i = vlines[x][i]
                    y1j,y2j = vlines[x][j]
                    if y1i+1 == y2j or y2i-1 == y1j or y2i+1 == y1j or y1i-1 == y2j or \
                       y1i == y2j or y2i == y1j or y2i == y1j or y1i == y2j:
                        #merge fragment
                        vlines[x][i] = [min(y1i,y1j,y2i,y2j),max(y1i,y1j,y2i,y2j)]
                        vlines[x].pop(j)
                        j = i+1
                    else:
                        j += 1
                i += 1
        #get color range
        cyclemode = False
        for crange in config.cranges:
            if crange.is_active() and color >= crange.low and color <= crange.high:
                cyclemode = True
                arange = crange.get_range()
                numcolors = len(arange)
                cur_crange = crange
                color = arange[0]
        size = screen.get_size()
        if cyclemode:
            for x in sorted(vlines.keys()):
                surf_array = pygame.surfarray.pixels2d(screen)  # Create an array from the surface.
                for frag in vlines[x]:
                    y1,y2 = frag
                    if x<0 or x>=size[0]:
                        continue
                    if y1 > y2:
                        y1,y2 = (y2,y1)
                    ys1,ys2 = (y1,y2)
                    if ys1<0:
                        ys1=0
                    if ys2>size[1]-1:
                        ys2=size[1]-1
                    numpoints = y2-y1+1
                    if primprops.fillmode.gradient_dither >= 0:
                        pointspercolor = numpoints / (numcolors)
                    else:
                        pointspercolor = numpoints / (numcolors-.9)
                    ditherfactor = primprops.fillmode.gradient_dither/3.0 * pointspercolor
                    for y in range(ys1,ys2+1):
                        if primprops.fillmode.gradient_dither >= 0:
                            dither = int((random.random()*ditherfactor)-(ditherfactor/2))
                        else:
                            dither = 0
                        if pointspercolor > 0:
                            colori = int(int(y2-(y+dither)) / pointspercolor)
                            if primprops.fillmode.gradient_dither < 0:
                                if FillMode.ORDER4[x%4, y%4] > (16 - (16 * (y2-y) // pointspercolor)%16):
                                    colori += 1
                            if colori >= len(arange):
                                colori = len(arange) - 1
                            elif colori < 0:
                                colori = 0
                            color = arange[colori]
                        if screen.get_bytesize() == 1:
                            surf_array[x,y] = color
                        else:
                            surf_array[x,y] = (config.pal[color][0] << 16) | (config.pal[color][1] << 8) | (config.pal[color][2])
                surf_array = None
                if interrupt and config.has_event():
                    return
                config.try_recompose()

def drawxorcross(screen, x, y):
    #don't draw if off screen
    size = screen.get_size()
    if y<0 or y>=size[1] or x<0 or x>=size[0]:
        return

    #create array from the surface.
    surf_array = pygame.surfarray.pixels2d(screen)

    if surf_array.dtype == np.uint8:
        #indexed color
        surf_array[0:size[0],y] ^= config.NUM_COLORS-1
        surf_array[x,0:size[1]] ^= config.NUM_COLORS-1
    else:
        #true color
        surf_array[0:size[0],y] ^= 0x00ffffff
        surf_array[x,0:size[1]] ^= 0x00ffffff

    #free array and unlock surface
    surf_array = None



def fillrect(screen, color, coordfrom, coordto, interrupt=False, primprops=None):
    if primprops == None:
        primprops = config.primprops

    x1,y1 = coordfrom
    x2,y2 = coordto

    if x1 > x2:
        x1, x2 = x2, x1

    if y1 > y2:
        y1, y2 = y2, y1

    if not rect_onscreen([x1,y1,x2-x1+1,y2-y1+1]):
        return

    if interrupt and config.has_event():
        return

    if primprops.fillmode.value == FillMode.SOLID:
        pygame.draw.rect(screen, color, (x1,y1,x2-x1+1,y2-y1+1))
    else:
        config.fillmode.bounds = [x1,y1,x2,y2]
        start_shape()
        for y in range(y1, y2+1):
            hline(screen, color, y, x1, x2, primprops=primprops)
            if interrupt and config.has_event():
                return
            config.try_recompose()
        end_shape(screen, color, interrupt=interrupt, primprops=primprops)

def floodfill(surface, fill_color, position):
    for x,y in symm_coords(position):
        #Create scanline hash
        sl = {}
        config.fillmode.bounds = copy.copy(FillMode.NOBOUNDS)
        if onscreen((x,y)):
            surf_array = pygame.surfarray.pixels2d(surface)  # Create an array from the surface.
            maxx, maxy = surface.get_size()
            current_color = surf_array[x,y]
            if fill_color == current_color:
                if config.fillmode.value == FillMode.SOLID:
                    continue
                else:
                    for crange in config.cranges:
                        if crange.is_active() and fill_color >= crange.low and fill_color <= crange.high:
                            fill_color = crange.next_color(fill_color)

            if surf_array[x,y] == fill_color:
                continue

            frontier = [(x,y)]
            while len(frontier) > 0:
                x, y = frontier.pop()
                if x >= 0 and x < maxx and y >= 0 and y < maxy:
                    if surf_array[x, y] != current_color:
                        continue
                else:
                    continue
                surf_array[x, y] = fill_color
                add_bounds((x,y))

                # append coords to scanline lists
                if y in sl:
                    slfound = False
                    for sly in sl[y]:
                        if x >= sly[0] and x <= sly[1]:
                            #fragment already in list
                            slfound = True
                            break
                        elif sly[0]-1 == x:
                            #extend fragment left
                            sly[0] = x
                            slfound = True
                            break
                        elif sly[1]+1 == x:
                            #extend fragment right
                            sly[1] = x
                            slfound = True
                            break
                    if not slfound:
                        #new fragment
                        sl[y].append([x,x])
                else:
                    sl[y] = [[x,x]]

                # Then we append the neighbors of the pixel in the current position to our 'frontier' list.
                frontier.append((x + 1, y))  # Right.
                frontier.append((x - 1, y))  # Left.
                frontier.append((x, y + 1))  # Down.
                frontier.append((x, y - 1))  # Up.

            surf_array = None

            for y in sl:
                #collapse scanline fragments
                for i in range(0,len(sl[y])):
                    j = i+1
                    while j < len(sl[y]):
                        x1i,x2i = sl[y][i]
                        x1j,x2j = sl[y][j]
                        if x1i+1 == x2j or x2i-1 == x1j or x2i+1 == x1j or x1i-1 == x2j:
                            #merge fragment
                            sl[y][i] = [min(x1i,x1j,x2i,x2j),max(x1i,x1j,x2i,x2j)]
                            sl[y].pop(j)
                            j = i+1
                        else:
                            j += 1

            start_shape()
            if config.fillmode.value != FillMode.SOLID:
                for y in sorted (sl.keys()):
                    #draw scanline fragments
                    for frag in sl[y]:
                        hline(surface, fill_color, y, frag[0], frag[1])
                    config.try_recompose()
            end_shape(surface, fill_color)

#from pygame: https://github.com/atizo/pygame/blob/master/src/draw.c
def fillpoly(screen, color, coords, handlesymm=True, interrupt=False):
    n = len(coords)
    if n == 0:
        return

    coords_symm = symm_coords_list(coords, handlesymm=handlesymm)

    for i in range(len(coords_symm)):
        newcoords = coords_symm[i]

        # Determine maxima
        minx = min(newcoords,key=itemgetter(0))[0];
        maxx = max(newcoords,key=itemgetter(0))[0];
        miny = min(newcoords,key=itemgetter(1))[1];
        maxy = max(newcoords,key=itemgetter(1))[1];
        config.fillmode.bounds = [minx,miny,maxx,maxy]

        # Eliminate last coord if equal to first
        if n > 1 and newcoords[0][0] == newcoords[n-1][0] and newcoords[0][1] == newcoords[n-1][1]:
            n -= 1

        start_shape()
        # Draw, scanning y
        for y in range(miny, maxy+1):
            if interrupt and config.has_event():
                return
            polyints = []
            for i in range(0, n):
                if i == 0:
                    ind1 = n-1
                    ind2 = 0
                else:   
                    ind1 = i-1
                    ind2 = i

                y1 = newcoords[ind1][1]
                y2 = newcoords[ind2][1]

                if y1 < y2:
                    x1 = newcoords[ind1][0]
                    x2 = newcoords[ind2][0]
                elif y1 > y2:
                    y2 = newcoords[ind1][1]
                    y1 = newcoords[ind2][1]
                    x2 = newcoords[ind1][0]
                    x1 = newcoords[ind2][0]
                else:
                    continue

                if y >= y1 and y < y2:
                    polyints.append((y-y1) * (x2-x1) // (y2-y1) + x1)
                elif y == maxy and y > y1 and y <= y2:
                    polyints.append((y-y1) * (x2-x1) // (y2-y1) + x1)

            polyints.sort()

            for i in range(0, len(polyints), 2):
                hline(screen, color, y, polyints[i], polyints[i+1])
                if interrupt and config.has_event():
                    return
                config.try_recompose()
        end_shape(screen, color, interrupt=interrupt)


def drawpoly(screen, color, coords, filled=0, xormode=False, drawmode=-1, handlesymm=True, interrupt=False, skiplast=False):
    if filled:
        fillpoly(screen, color, coords, handlesymm=handlesymm, interrupt=interrupt)
    else:
        coords_symm = symm_coords_list(coords, handlesymm=handlesymm)

        for i in range(len(coords_symm)):
            newcoords = coords_symm[i]
            lastcoord = []
            for coord in newcoords:
                if interrupt and config.has_event():
                    return
                if len(lastcoord) != 0:
                    drawline(screen, color, lastcoord, coord, xormode, drawmode=drawmode, handlesymm=False, interrupt=interrupt, skiplast=(xormode or skiplast))
                lastcoord = coord


