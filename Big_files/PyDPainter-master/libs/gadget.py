#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#gadget.py
"""
gadget.py
Library for clickable buttons and sliders on the screen

Boolean (or button) gadgets
Proportional gadgets (slider)
String gadgets
Custom gadgets

                      vert sliders
text1:  ___________    | |
text2:  ___________    | |
slider: -----------    | |

buttons: [OK]  [Cancel]
button group: [A~B~C~D~E~F]
"""

import os.path
import re

import pygame
from pygame.locals import *

import pixelfont
from pixelfont import *

fonty = 12
fontx = 8

def imgload(filename, scaleX=0, scaleY=0, scaledown=1):
    imagex1 = pygame.image.load(os.path.join('data', filename))
    ox,oy = imagex1.get_size()

    if scaledown == 1:
        return imagex1
    elif scaledown == 2 or scaledown == 4:
        #convert image to arrays for scaling
        surf_array = pygame.surfarray.array3d(imagex1)
        surf_array_alpha = pygame.surfarray.array_alpha(imagex1)

        #scale image down either by 2 or 4
        if scaledown == 2:
            scaled_array = surf_array[0::2, 0::2, ::]
            scaled_array_alpha = surf_array_alpha[0::2, 0::2]
        else:
            scaled_array = surf_array[1::4, 1::4, ::]
            scaled_array_alpha = surf_array_alpha[1::4, 1::4]

        #unlock original bitmap
        surf_array = None
        surf_array_alpha = None

        #convert array back into image and add alpha placeholder
        display =  pygame.display.get_surface()
        if display == None:
             pygame.display.set_mode((10,10))
        imagexx = pygame.surfarray.make_surface(scaled_array).convert_alpha()

        #copy over scaled alpha component
        imagexx_array_alpha = pygame.surfarray.pixels_alpha(imagexx)
        imagexx_array_alpha[::,::] = scaled_array_alpha[::,::]
        imagexx_array_alpha = None

        #scale image up in X or Y if needed
        ixx_sizeX, ixx_sizeY = imagexx.get_size()
        if scaleX != 0 and scaleX > scaleY:
            #scale up in X
            imagexx = pygame.transform.scale(imagexx, (ixx_sizeX*2, ixx_sizeY))
        elif scaleY != 0 and scaleY > scaleX:
            #scale up in Y
            imagexx = pygame.transform.scale(imagexx, (ixx_sizeX, ixx_sizeY*2))

        return imagexx
    else:
        return imagex1

"""
Actions for gadgets and tools
"""
class Action(object):
    def __init__(self, id=None, gadget=None):
        self.id = id
        self.gadget = gadget

    def selected(self, attrs):
        pass

    def deselected(self, attrs):
        pass

    def move(self, coords):
        pass

    def mousedown(self, coords, button):
        pass

    def drag(self, coords, buttons):
        pass

    def mouseup(self, coords, button):
        pass

    def keydown(self, key, mod, unicode):
        return False

    def keyup(self, key, mod):
        return False


"""
Layers

+window (w*zoom, h*zoom)
  |
  +scanlines (h*2)
    |
    +pixel stack
      |
      +pixel_canvas
      +toolbar/menu
      +(requestor)
      +mouse pointer
"""


class Layer(object):
    """This class composites a stack of bitmaps scaling as necessary"""
    def __init__(self, screen, rect=None, offset=(0,0), scaletype=0, visible=True, req=None, sublayers=[]):
        self.screen = screen
        self.rect = rect
        self.offset = offset
        self.scaletype = scaletype
        self.visible = visible
        self.req = req
        self.sublayers = sublayers
        self.parent = None
        self.parent_screen = None
        for layer in self.sublayers:
            layer.parent = self

    def add(self, layer):
        layer.parent = self
        self.sublayers.append(layer)

    def screen_to_layer_coords(self, screen_coords):
        x, y = screen_coords
        l = self
        while l != None:
            x -= l.offset[0]
            y -= l.offset[1]
            if l.scaletype > 0 and l.parent_screen != None:
                w1, h1 = l.screen.get_size()
                w2, h2 = l.parent_screen.get_size()
                x = x * w1 // w2
                y = y * w1 // w2
            l = l.parent

        return (x, y)

    def process_event(self, screen, event):
        ge = []

        if not self.visible:
            return ge

        if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
            event.newpos = self.screen_to_layer_coords(event.pos)

        for layer in self.sublayers:
            ge.extend(layer.process_event(self.screen, event))

        if self.req != None:
            ge.extend(self.req.process_event(screen, event))

        return ge

    def draw(self, parent_screen):
        self.parent_screen = parent_screen

        if not self.visible:
            return

        if self.req != None:
            self.req.draw(self.screen)

        for layer in self.sublayers:
            layer.draw(self.screen)

        if self.scaletype == 0:
            scaled_image = self.screen
        elif self.scaletype == 1:
            scaled_image = pygame.transform.scale(self.screen, parent_screen.get_size())
        elif self.scaletype == 2:
            if self.screen.get_bitsize() < 24:
                screen_rgb = self.screen.convert()
            else:
                screen_rgb = self.screen
            scaled_image = pygame.transform.smoothscale(screen_rgb, parent_screen.get_size())

        parent_screen.blit(scaled_image, self.offset, self.rect)


class Cursor(Layer):
    """This class renders the mouse pointer as a layer, which acts as a sprite"""
    def set_centers(self, center):
        self.center = center
        self.shape = 0

    def get_mouse_pos(self):
        return self.screen_to_layer_coords(pygame.mouse.get_pos())

    def draw(self, parent_screen):
        #draw mouse cursor
        if not pygame.mouse.get_focused():
            return

        if not self.visible and self.shape != 1:
            return

        mouseX, mouseY = self.get_mouse_pos()
        centerX, centerY = self.center[self.shape]
        parent_screen.blit(self.screen, (mouseX-centerX, mouseY-centerY), (16*self.shape,0,16,self.screen.get_height()))


class GadgetEvent(object):
    TYPE_GADGETDOWN, TYPE_GADGETUP, TYPE_MOUSEMOVE, TYPE_KEY = range(4)
    typearray = ['TYPE_GADGETDOWN', 'TYPE_GADGETUP', 'TYPE_MOUSEMOVE', 'TYPE_KEY']

    def __init__(self, type, event, gadget):
        self.type = type
        self.gadget = gadget
        self.event = event

    def __repr__(self):
        return "type={} gadgetid={} gadgettype={} event={}".format(self.typearray[self.type], self.gadget.id, self.gadget.typearray[self.gadget.type], self.event)

class Gadget(object):
    TYPE_BOOL, TYPE_IMAGE, TYPE_PROP, TYPE_PROP_VERT, TYPE_STRING, TYPE_CUSTOM, TYPE_LABEL = range(7)
    typearray = ['TYPE_BOOL', 'TYPE_IMAGE', 'TYPE_PROP', 'TYPE_PROP_VERT', 'TYPE_STRING', 'TYPE_CUSTOM', 'TYPE_LABEL']

    def __init__(self, type, label, rect, value=None, maxvalue=None, id=None, enabled=True):
        self.type = type
        self.label = label
        self.rect = rect
        self.screenrect = rect
        self.screenrect2 = rect
        self.visible = False
        self.state = 0
        self.pos = 0
        self.value = value
        self.maxvalue = maxvalue
        self.id = id
        self.enabled = enabled
        self.offsetx = 0
        self.offsety = 0
        self.numonly = False
        self.error = False
        self.need_redraw = True
        if value == None:
            if type == self.TYPE_PROP or type == self.TYPE_PROP_VERT:
                self.value = 0
            elif type == self.TYPE_STRING:
                self.value = ""
        if maxvalue == None:
            if type == self.TYPE_PROP or type == self.TYPE_PROP_VERT:
                self.maxvalue = 100
            elif type == self.TYPE_STRING:
                self.maxvalue = 1
        if id == None:
            self.id = str(rect[0]) + "_" + str(rect[1])

    def coords2prop(self, coords):
        x,y,w,h = self.screenrect
        mousex, mousey = coords
        if self.type == Gadget.TYPE_PROP:
            value = (mousex-x) * (self.maxvalue-1) // (w-fontx)
            if value < 0:
                return 0
            elif value >= self.maxvalue:
                return self.maxvalue - 1
            else:
                return value
        elif self.type == Gadget.TYPE_PROP_VERT:
            value = (h-mousey+y) * (self.maxvalue-1) // (h-fontx)
            if value < 0:
                return 0
            elif value >= self.maxvalue:
                return self.maxvalue - 1
            else:
                return value

    def coords2char(self, coords):
        x,y,w,h = self.screenrect
        mousex, mousey = coords
        if self.type == Gadget.TYPE_STRING:
            value = (mousex-x) // fontx
            if value < 0:
                return 0
            elif value >= len(self.value):
                return len(self.value)
            else:
                return value

    def pointin(self, coords, rect):
        gx,gy,gw,gh = rect
        x, y = coords
        if x >= gx and x < gx+gw and \
           y >= gy and y <= gy+gh:
            return True
        else:
            return False

    def draw(self, screen, font, offset=(0,0), fgcolor=(0,0,0), bgcolor=(160,160,160), hcolor=(208,208,224)):
        self.visible = True
        x,y,w,h = self.rect
        xo, yo = offset
        self.offsetx = xo
        self.offsety = yo
        self.screenrect = (x+xo,y+yo,w,h)
        self.fontx = font.xsize
        self.fonty = int(font.ysize * 1.5)
        self.fonth = font.ysize
        if not self.need_redraw:
            return

        self.need_redraw = False

        if self.type == Gadget.TYPE_BOOL:
            strw = font.calcwidth(self.label)
            strxo = (w - strw) // 2
            if self.state == 1:
                pygame.draw.rect(screen, bgcolor, self.screenrect, 0)
                pygame.draw.rect(screen, hcolor, self.screenrect, 1)
                font.blitstring(screen, (x+xo+(strxo)+1,y+yo+2), self.label, fgcolor, bgcolor)
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo+w-2,y+yo))
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo,y+yo+h-1))
            else:
                pygame.draw.rect(screen, bgcolor, self.screenrect, 0)
                pygame.draw.rect(screen, fgcolor, self.screenrect, 1)
                font.blitstring(screen, (x+xo+(strxo),y+yo+1), self.label, fgcolor, bgcolor)
                pygame.draw.line(screen, hcolor, (x+xo,y+yo), (x+xo+w-2,y+yo))
                pygame.draw.line(screen, hcolor, (x+xo,y+yo), (x+xo,y+yo+h-1))
        elif self.type == Gadget.TYPE_PROP:
            propo = (w-self.fontx) * self.value // (self.maxvalue-1)
            self.screenrect2 = (x+xo+propo, y+yo, self.fontx, h)
            px = self.fontx//8
            py = self.fonth//8
            diamond = ((x+xo+(self.fontx//2)-px+propo,y+yo+3*py),
                       (x+xo+self.fontx-3*px+propo, y+yo+1+(self.fonth//2)),
                       (x+xo+(self.fontx//2)-1+propo,y+yo-1+self.fonth),
                       (x+xo+px+propo, y+yo+py+(self.fonth//2)))
            rectx,recty,rectw,recth = self.screenrect

            if self.state == 1:
                pygame.draw.rect(screen, fgcolor, (rectx,recty+2,rectw-1,recth-4), 0)
                pygame.draw.polygon(screen, hcolor, diamond, 0)
            else:
                pygame.draw.rect(screen, fgcolor, (rectx,recty+2,rectw-1,recth-4), 0)
                pygame.draw.polygon(screen, bgcolor, diamond, 0)
                pygame.draw.line(screen, hcolor, diamond[3], diamond[0])
            pygame.draw.line(screen, hcolor, (rectx,recty+recth-2), (rectx+rectw-1,recty+recth-2))
            pygame.draw.line(screen, hcolor, (rectx+rectw-1,recty+recth-3), (rectx+rectw-1,recty+2))
        elif self.type == Gadget.TYPE_PROP_VERT:
            propo = (h-self.fonth) * (self.maxvalue-1-self.value) // (self.maxvalue-1)
            px = self.fontx//8
            py = self.fonth//8
            diamond = ((x+xo+(self.fontx//2)-px,y+yo+py+py+propo),
                       (x+xo+w-(3*px), y+yo+(self.fonth//2)+propo),
                       (x+xo+(self.fontx//2)-px,y+yo+self.fonth-py-py+propo),
                       (x+xo+px, y+yo+(self.fonth//2)+propo))
            self.screenrect2 = (x+xo+1, y+yo+1+propo, self.fontx, self.fonth)
            if self.state == 1:
                pygame.draw.rect(screen, fgcolor, (x+xo,y+yo,w-px,h), 0)
                pygame.draw.polygon(screen, hcolor, diamond, 0)
            else:
                pygame.draw.rect(screen, fgcolor, (x+xo,y+yo,w-px,h), 0)
                pygame.draw.polygon(screen, bgcolor, diamond, 0)
            pygame.draw.line(screen, hcolor, diamond[3], diamond[0])
        elif self.type == Gadget.TYPE_STRING:
            strxo = 0
            if self.state == 0:
                pygame.draw.rect(screen, bgcolor, self.screenrect, 0)
                font.blitstring(screen, (x+xo,y+yo+2), self.value, fgcolor, bgcolor)
                pygame.draw.rect(screen, hcolor, self.screenrect, 1)
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo+w-2,y+yo))
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo,y+yo+h-1))
            else:
                pygame.draw.rect(screen, bgcolor, self.screenrect, 0)
                font.blitstring(screen, (x+xo,y+yo+2), self.value, fgcolor, bgcolor)
                pygame.draw.rect(screen, hcolor, self.screenrect, 1)
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo+w-2,y+yo))
                pygame.draw.line(screen, fgcolor, (x+xo,y+yo), (x+xo,y+yo+h-1))
                if self.pos < len(self.value):
                    c = self.value[self.pos]
                else:
                    c = " "
                font.blitstring(screen, (x+xo+(self.pos*self.fontx),y+yo+2), c, hcolor, (255,0,0))
            if self.numonly and not re.fullmatch('^-?\d*\.?\d+$', self.value):
                #numeric error
                font.blitstring(screen, (x+xo+w-self.fontx,y+yo+2), "!", hcolor, (255,0,0))
                self.error = True
            else:
                self.error = False
        elif self.type == Gadget.TYPE_LABEL:
            font.blitstring(screen, (x+xo,y+yo+2), self.label, fgcolor, bgcolor)
        if not self.enabled:
            for i in range(x+xo, x+xo+w+1, 2):
                for j in range(y+yo, y+yo+h+1, 4):
                    pygame.draw.rect(screen, bgcolor, (i,j,1,1), 0)
            for i in range(x+xo+1, x+xo+w+1, 2):
                for j in range(y+yo+2, y+yo+h+1, 4):
                    pygame.draw.rect(screen, bgcolor, (i,j,1,1), 0)
            fadesurf = pygame.Surface((w,h), SRCALPHA)
            fadesurf.fill((bgcolor[0],bgcolor[1],bgcolor[2],128))
            screen.blit(fadesurf, self.screenrect)

    def process_event(self, screen, event, mouse_pixel_mapper):
        ge = []
        if (event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP) and hasattr(event, "newpos"):
            x,y = event.newpos
        else:
            x,y = mouse_pixel_mapper()
        g = self

        #disabled gadget
        if not g.enabled:
            return ge

        #not selected
        if g.state == 0:
            if g.pointin((x,y), g.screenrect):
                #handle left button
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if g.type == Gadget.TYPE_BOOL:
                        g.need_redraw = True
                        g.state = 1
                    elif g.type == Gadget.TYPE_PROP or g.type == Gadget.TYPE_PROP_VERT:
                        if g.pointin((x,y), g.screenrect2):
                            newvalue = g.coords2prop((x,y))
                            if g.value != newvalue:
                                g.value = newvalue
                            g.need_redraw = True
                            g.state = 1
                            ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETDOWN, event, g))
                        elif g.coords2prop((x,y)) < g.value:
                            g.need_redraw = True
                            g.value -= 1
                            ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
                        elif g.coords2prop((x,y)) > g.value:
                            g.need_redraw = True
                            g.value += 1
                            ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
                    elif g.type == Gadget.TYPE_STRING:
                        g.need_redraw = True
                        g.state = 1
                        g.pos = g.coords2char((x,y))
                        ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETDOWN, event, g))
                    elif g.type == Gadget.TYPE_LABEL:
                        g.state = 1
                        ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETDOWN, event, g))
                #handle scroll up
                elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                    if g.type == Gadget.TYPE_PROP or g.type == Gadget.TYPE_PROP_VERT:
                        if g.value < g.maxvalue-1:
                            g.need_redraw = True
                            g.value += 1
                            ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
                #handle scroll down
                elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                    if g.type == Gadget.TYPE_PROP or g.type == Gadget.TYPE_PROP_VERT:
                        if g.value > 0:
                            g.need_redraw = True
                            g.value -= 1
                            ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))

        #selected
        if g.state == 1:
            if g.type == Gadget.TYPE_BOOL:
                if not g.pointin((x,y), g.screenrect):
                    g.need_redraw = True
                    g.state = 2
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    g.need_redraw = True
                    g.state = 0
                    ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
            elif g.type == Gadget.TYPE_PROP or g.type == Gadget.TYPE_PROP_VERT:
                newvalue = g.coords2prop((x,y))
                if g.value != newvalue:
                    g.need_redraw = True
                    g.value = newvalue
                    ge.append(GadgetEvent(GadgetEvent.TYPE_MOUSEMOVE, event, g))
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    g.need_redraw = True
                    g.state = 0
                    ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
            elif g.type == Gadget.TYPE_STRING:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if g.pointin((x,y), g.screenrect):
                        g.need_redraw = True
                        g.pos = g.coords2char((x,y))
                    else:
                        g.need_redraw = True
                        g.state = 0
                        ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
                elif event.type == KEYDOWN:
                    g.need_redraw = True
                    ge.append(GadgetEvent(GadgetEvent.TYPE_KEY, event, g))
                    if event.key == K_RIGHT:
                        if self.pos < len(self.value):
                            self.pos += 1
                    elif event.key == K_LEFT:
                        if self.pos > 0:
                            self.pos -= 1
                    elif event.key == K_HOME:
                        self.pos = 0
                    elif event.key == K_END:
                        self.pos = len(self.value)
                    elif event.key == K_BACKSPACE:
                        if self.pos > 0:
                            self.value = self.value[:self.pos-1] + self.value[self.pos:]
                            self.pos -= 1
                    elif event.key == K_DELETE:
                        if self.pos < len(self.value):
                            self.value = self.value[:self.pos] + self.value[self.pos+1:]
                    elif event.key == K_RETURN or event.key == K_KP_ENTER or event.key == K_ESCAPE:
                        self.state = 0
                        ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
                    elif len(event.unicode) == 1 and ord(event.unicode) >= 32 and ord(event.unicode) < 128:
                        if len(g.value) < self.maxvalue:
                            self.value = self.value[:self.pos] + event.unicode + self.value[self.pos:]
                            self.pos += 1
            elif g.type == Gadget.TYPE_LABEL:
                g.state = 0
                ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                g.need_redraw = True
                g.state = 0
                ge.append(GadgetEvent(GadgetEvent.TYPE_GADGETUP, event, g))

        #handle misc states
        if g.state == 2:
            if g.type == Gadget.TYPE_BOOL:
                #selected but mouse not in it
                if g.pointin((x,y), g.screenrect):
                    g.need_redraw = True
                    g.state = 1
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    g.need_redraw = True
                    g.state = 0

        return ge

class Requestor(object):
    def __init__(self, label, rect, mouse_pixel_mapper=pygame.mouse.get_pos, fgcolor=(0,0,0), bgcolor=(160,160,160), hcolor=(208,208,224), font=None):
        self.label = label
        self.rect = rect
        self.mouse_pixel_mapper = mouse_pixel_mapper
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.hcolor = hcolor
        self.draggable = False
        self.dragpos = None
        self.gadgets = []
        if font == None:
            self.font = PixelFont("jewel32.png", 8)
        else:
            self.font = font

        self.fontx = self.font.xsize
        self.fonty = int(font.ysize * 1.5)
        self.need_redraw = True
        x,y,w,h = self.rect
        if self.label != "":
            self.gadgets.append(Gadget(Gadget.TYPE_LABEL, "", (x-2, y-2, w+1, self.fonty), id="__reqtitle"))

    def add(self, gadget):
        self.gadgets.append(gadget)

    def process_event(self, screen, event):
        ge = []
        for g in self.gadgets:
            ge.extend(g.process_event(screen, event, self.mouse_pixel_mapper))

        if self.label != "" and self.draggable:
            x,y = self.mouse_pixel_mapper()
            #handle title bar click
            for i in range(len(ge)):
                if ge[i].gadget.id == "__reqtitle":
                    if ge[i].type == GadgetEvent.TYPE_GADGETDOWN:
                        self.dragpos = (x-self.rect[0],y-self.rect[1])
                        ge[i].gadget.value = 1

            g = self.gadget_id("__reqtitle")
            if g.value == 1:
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    g.value = 0
                self.rect = (x-self.dragpos[0], y-self.dragpos[1], self.rect[2], self.rect[3])
                self.need_redraw = True

        #handle tab on string fields
        if event.type == KEYDOWN and event.key == K_TAB:
            found = False
            glist = None
            if event.mod & KMOD_SHIFT:
                glist = self.gadgets[::-1]
            else:
                glist = self.gadgets
            for g in glist:
                if g.type == Gadget.TYPE_STRING:
                    if not found and g.state == 1 and g.type == Gadget.TYPE_STRING:
                        found = True
                        g.state = 0
                    elif found:
                        g.state = 1
                        g.pos = len(g.value)
                        g.need_redraw = True
                        break

        return ge

    def has_error(self):
        for g in self.gadgets:
            if g.error:
                return True
        return False

    def get_screen_rect(self):
        x,y,w,h = self.rect
        return((x-3,y-3,w+6,h+4))

    def center(self, screen):
        (rx,ry,rw,rh) = self.rect
        (sw,sh) = screen.get_size()
        rx = (sw-rw) // 2
        ry = (sh-rh) // 2
        self.rect = (rx,ry,rw,rh)

    def draw(self, screen, offset=(0,0)):
        x,y,w,h = self.rect
        xo, yo = offset
        self.offsetx = xo
        self.offsety = yo

        if self.need_redraw:
            self.need_redraw = False
            pygame.draw.rect(screen, self.fgcolor, (x+xo-3,y+yo-3,w+6,h+4), 0)
            pygame.draw.rect(screen, self.bgcolor, (x+xo-2,y+yo-2,w+4,h+2), 0)
            if self.label != "":
                cx = (w - (len(self.label) * self.fontx)) // 2
                self.font.blitstring(screen, (x+xo+cx,y+yo), self.label, self.fgcolor, self.bgcolor)
                #draw highlight
                pygame.draw.line(screen, self.hcolor, (x+xo-2, y+yo-2), (x+xo+w+1, y+yo-2))
                pygame.draw.line(screen, self.hcolor, (x+xo-2, y+yo-2), (x+xo-2, y+yo+self.fonty-4))
                #draw dividing line
                pygame.draw.line(screen, self.fgcolor, (x+xo-2, y+yo+self.fonty-3), (x+xo+w+1, y+yo+self.fonty-3))
                pygame.draw.line(screen, self.hcolor, (x+xo-2, y+yo+self.fonty-2), (x+xo+w+1, y+yo+self.fonty-2))
            for g in self.gadgets:
                g.need_redraw = True

        for g in self.gadgets:
            g.draw(screen, self.font, (x+xo, y+yo), self.fgcolor, self.bgcolor, self.hcolor)

    def is_inside(self, coords):
        gx,gy,gw,gh = self.rect
        gx += self.offsetx
        gy += self.offsety
        x, y = coords
        if x >= gx and y >= gy and x <= gx+gw and y <= gy+gh:
            return True
        else:
            return False

    def gadget_id(self, id):
        for g in self.gadgets:
            if g.id == id:
                return g
        return None

def str2req(title, reqstring, custom="", mouse_pixel_mapper=pygame.mouse.get_pos, custom_gadget_type=Gadget, font=None):
    #Split into lines
    reqlines = reqstring.splitlines()

    #Remove first line if nothing on it
    if len(reqlines) > 0 and len(reqlines[0].strip()) == 0:
        reqlines = reqlines[1:]

    if font == None:
        fontx = 8
        fonty = 12
    else:
        fontx = font.xsize
        fonty = int(font.ysize * 1.5)

    #Find X/Y size
    yo = 0
    ysize = len(reqlines) * fonty
    if title != "":
        yo = fonty
        ysize += yo
    maxlen = 0
    for line in reqlines:
        linelen = len(line)
        if linelen > 0 and line[linelen-1] == "]":
            linelen -= 1
        if linelen > maxlen:
            maxlen = linelen
    xsize = maxlen * fontx

    for lineno in range(0,len(reqlines)):
        if len(reqlines[lineno]) < maxlen:
            reqlines[lineno] += " " * (maxlen - len(reqlines[lineno]))

    #print("xsize = {}, ysize = {}".format(xsize, ysize))
    req = Requestor(title, (0,0, xsize,ysize), mouse_pixel_mapper=mouse_pixel_mapper, font=font)

    #Find buttons
    for lineno in range(0,len(reqlines)):
        line = reqlines[lineno]
        bstart = line.find("[")
        bend = line.find("]")
        while bend > bstart and bstart >= 0 and bend >= 0:
            text = line[bstart+1:bend]
            #print("{} - lineno={} bstart={} bend={}".format(text, lineno, bstart, bend))
            bgroup_text = text.split("~")
            bgroup_len = 0
            for s in bgroup_text:
                req.add(Gadget(Gadget.TYPE_BOOL, s, ((bstart+bgroup_len)*fontx,yo+lineno*fonty, (len(s)+1)*fontx,fonty-1), id=str(bstart+bgroup_len)+"_"+str(lineno)))
                bgroup_len += len(s) + 1
            if bstart == 0:
                reqlines[lineno] = (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]
            else:
                reqlines[lineno] = reqlines[lineno][:bstart] + (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]
            bstart = line.find("[",bend)
            bend = line.find("]",bstart)

    #Find horizontal sliders
    for lineno in range(0,len(reqlines)):
        line = reqlines[lineno]
        bstart = line.find("-")
        bend = bstart + 1
        while bstart >= 0:
            while bend < len(line) and line[bend] == "-":
                bend += 1
            bend -= 1

            if bstart == 0:
                reqlines[lineno] = (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]
            else:
                reqlines[lineno] = reqlines[lineno][:bstart] + (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]

            req.add(custom_gadget_type(Gadget.TYPE_PROP, "-", (bstart*fontx,yo+lineno*fonty, (bend-bstart+1)*fontx,fonty-1), maxvalue=(bend-bstart+1)*2, id=str(bstart)+"_"+str(lineno)))
            #print("slider lineno={} bstart={} bend={}".format(lineno, bstart, bend))
            bstart = line.find("-", bend+1)
            bend = bstart + 1

    #Find vertical sliders
    for lineno in range(0,len(reqlines)):
        line = reqlines[lineno]
        col = line.find("|")
        while col >= 0:
            lstart = lineno
            lend = lineno
            while lend < len(reqlines) and reqlines[lend][col] == "|":
                if col == 0:
                    reqlines[lend] = " " + reqlines[lend][col+1:]
                else:
                    reqlines[lend] = reqlines[lend][:col] + " " + reqlines[lend][col+1:]
                lend += 1

            lend -= 1
            req.add(custom_gadget_type(Gadget.TYPE_PROP_VERT, "|", (col*fontx,yo+lstart*fonty, fontx,(lend-lstart+1)*fonty-1), maxvalue=(lend-lstart+1)*2, id=str(col)+"_"+str(lstart)))
            #print("vert slider col={} lstart={} lend={}".format(col, lstart, lend))
            col = line.find("|", col+1)

    #Find string gadgets
    for lineno in range(0,len(reqlines)):
        line = reqlines[lineno]
        bstart = line.find("_")
        bend = bstart + 1
        while bstart >= 0:
            while bend < len(line) and line[bend] == "_":
                bend += 1
            bend -= 1

            if bstart == 0:
                reqlines[lineno] = (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]
            else:
                reqlines[lineno] = reqlines[lineno][:bstart] + (" " * (bend-bstart+1)) + reqlines[lineno][bend+1:]

            req.add(custom_gadget_type(Gadget.TYPE_STRING, "-", (bstart*fontx,yo+lineno*fonty, (bend-bstart+1)*fontx,fonty-1), maxvalue=bend-bstart, id=str(bstart)+"_"+str(lineno)))
            #print("slider lineno={} bstart={} bend={}".format(lineno, bstart, bend))
            bstart = line.find("_", bend+1)
            bend = bstart + 1

    #Find custom chars
    for i in range(0,len(custom)):
        c = custom[i]
        #print("custom c={}".format(c))
        for lineno in range(0,len(reqlines)):
            line = reqlines[lineno]
            col = line.find(c)
            while col >= 0:
                #print("custom col={}".format(col))
                lstart = lineno
                colend = col
                while colend < len(line) and line[colend] == c:
                    if colend == 0:
                        reqlines[lineno] = " " + reqlines[lineno][colend+1:]
                    else:
                        reqlines[lineno] = reqlines[lineno][:colend] + " " + reqlines[lineno][colend+1:]
                    colend += 1
                colend -= 1
                lend = lineno + 1
                #print("custom lend={} reqlines[lend][col]={}".format(lend, reqlines[lend][col]))
                while lend < len(reqlines) and reqlines[lend][col] == c:
                    #print("custom lend={}".format(lend))
                    if col == 0:
                        reqlines[lend] = (" "*(colend+1)) + reqlines[lend][colend+1:]
                    else:
                        reqlines[lend] = reqlines[lend][:col] + (" "*(colend-col+1)) + reqlines[lend][colend+1:]
                    lend += 1

                req.add(custom_gadget_type(Gadget.TYPE_CUSTOM, c, (col*fontx,yo+lstart*fonty, (colend-col+1)*fontx,(lend-lstart)*fonty-1), id=str(col)+"_"+str(lstart)))
                #print(e"custom c={} col={} colend={} lstart={} lend={}".format(c, col, colend, lstart, lend))
                col = line.find(c, colend+1)

    #Find remaining text
    for lineno in range(0,len(reqlines)):
        line = reqlines[lineno].rstrip()
        tstart = 0
        while tstart < len(line):
            while tstart < len(line) and line[tstart] == " ":
                tstart += 1
            tend = tstart
            while tend < len(line) and line[tend] != " ":
                tend += 1
            tend -= 1
            text = line[tstart:tend+1]

            req.add(custom_gadget_type(Gadget.TYPE_LABEL, text, (tstart*fontx,yo+lineno*fonty, len(text)*fontx,fonty-1), id=str(tstart)+"_"+str(lineno)))
            tstart = tend + 1

    #for line in reqlines:
    #    print("'" + line + "'")

    return req

def main():

    #Initialize the configuration settings
    pygame.init()
    clock = pygame.time.Clock()

    req = str2req("Color Palette", """
             %%%%%%
 R G B H S V ______
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
:|:|:|:|:|:| ######
[SPREAD]   [Ex~COPY]
[RANGE][1~2~3~4~5~6]
SPEED------------[v]
[Cancel] [Undo] [OK]
""", "%#:")

    sx,sy = 200,200

    scaled_screen = pygame.display.set_mode((sx*3,sy*3), RESIZABLE)
    screen = pygame.Surface((sx,sy),0,8)
    req_screen = pygame.Surface((sx,sy),0,8)
    cursor_images = pygame.image.load(os.path.join('data', 'cursors8.png'))
    cursor_layer = Cursor(cursor_images)
    cursor_layer.set_centers([(7,7), (1,1), (7,15), (0,15)])
    #layer = Layer(screen, offset=(10,10), scaletype=1, req=req, sublayers=[cursor_layer])
    layer = Layer(screen, scaletype=1, sublayers=[Layer(req_screen, req=req), cursor_layer])

    pygame.display.set_caption('gadget test')

    strg = req.gadget_id("13_1")
    rg = req.gadget_id("1_2")
    gg = req.gadget_id("3_2")
    bg = req.gadget_id("5_2")
    strg.value = hex(rg.value)[2] + hex(gg.value)[2] + hex(bg.value)[2]

    running = 1

    while running:
        
        #screen.fill((0,0,0))

        event = pygame.event.wait()
        if event.type == QUIT:
            running = 0

        gevents = layer.process_event(screen, event)

        for ge in gevents:
            #print(ge)
            if ge.gadget.type == Gadget.TYPE_PROP or ge.gadget.type == Gadget.TYPE_PROP_VERT:
                strg.value = hex(rg.value)[2] + hex(gg.value)[2] + hex(bg.value)[2]

        #req.draw(screen)
        #cursor_layer.offset = pygame.mouse.get_pos()
        layer.draw(scaled_screen)

        pygame.display.flip()
        #clock.tick(60)
        

if __name__ == '__main__': main()

