#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
config.py
Implement the global area of PyDPainter
"""

import sys, math, os.path, random, colorsys

from colorrange import *
from cursor import *
from toolbar import *
from prim import *
from palreq import *
from picio import *
from tools import *
from minitools import *
from menubar import *
from menus import *
from zoom import *

import numpy as np

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from tkinter import *
from tkinter import filedialog

fonty = 12
fontx = 8

config = None

def get_at_mapped(screen, coord):
    if "get_at_mapped" in dir(screen):
        return screen.get_at_mapped(coord)
    else:
        x, y = coord
        surf_array = pygame.surfarray.pixels2d(screen)  # Create an array from the surface.
        return int(surf_array[x,y])

def cycle():
    if config.drawmode.value == DrawMode.CYCLE:
        color = config.color
        for crange in config.cranges:
           color = crange.next_color(color)
        config.color = color

def quantize_palette(pal, color_depth=16):
    if color_depth == 16:
        newpal = []
        for i in range(0,len(pal)):
            r,g,b = pal[i]
            newpal.append((r//16*17, g//16*17, b//16*17))
        return newpal
    else:
        return pal

color_skew=[]
for r in range(2,16):
    for g in range(1,r+1):
        for b in range(1,g+1):
            color_skew.append(((r//2)*((r%2)*2-1), \
                               (g//2)*((g%2)*2-1), \
                               (b//2)*((b%2)*2-1)))

def unique_palette(pal):
    newpal = []
    paldict = {}
    #print("len(pal): " + str(len(pal)))
    for i in range(0,len(pal)):
        col = pal[i]
        j = 0
        out_of_range = False
        #print("color[" + str(i) + "]: " + str(col))
        while out_of_range or str(col) in paldict:
            #print("dup color: " + str(col))
            out_of_range = False
            r = pal[i][0] + color_skew[j][0]
            g = pal[i][1] + color_skew[j][1]
            b = pal[i][2] + color_skew[j][2]
            if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
                out_of_range = True
            col = (r,g,b)
            j = j + 1
        newpal.append(col)
        paldict[str(col)] = 1
    #pal256.extend([pal[0]] * (256-len(pal)))
    return newpal

def setBIBrush():
    brushnames = ["","circle","square","spray"]
    newid = brushnames[config.brush.type] + str(config.brush.size)
    group_list = config.toolbar.tool_id("circle1").group_list
    for g in group_list:
        if g.id == newid:
            g.state = 1
        else:
            g.state = 0
        g.need_refresh = True
    return


class pydpainter:

    def __init__(self):
        global config
        config = self
        prim_set_config(self)
        palreq_set_config(self)
        toolreq_set_config(self)
        menureq_set_config(self)
        picio_set_config(self)
        pygame.init()
        pygame.mixer.quit() #hack to stop 100% CPU ultilization
        
        #initialize system
        self.dinfo = pygame.display.Info()
        self.initialize()

    def closest_scale4(self,maxnum,num):
        if num >= maxnum:
            return maxnum
        if num >= maxnum // 2:
            return maxnum // 2
        return maxnum // 4

    def scale_dec(self):
        if config.scale <= 1:
            config.scale /= 2.0
        else:
            config.scale -= 0.5

    def scale_inc(self):
        if config.scale < 1:
            config.scale *= 2.0
        else:
            config.scale += 0.5

    def set_aspect(self, mode):
        self.pixel_mode = self.pixel_modes[mode]
        self.pixel_aspect = self.pixel_aspects[mode]
        if self.display_mode & self.MODE_LACE:
            self.pixel_aspect *= 2.0
        if self.display_mode & self.MODE_HIRES:
            self.pixel_aspect /= 2.0

    def closest_scale(self, size=None):
        #estimate scale from size
        limit = 20
        if size != None:
            ow, oh = size
        else:
            dinfo = pygame.display.Info()
            ow = dinfo.current_w
            oh = dinfo.current_h
        pw = config.pixel_width
        ph = config.pixel_height
        s = config.scale
        pa = config.pixel_aspect
        while limit > 0 and s > 0.1:
            limit -= 1
            nwd = int(pw*(s-0.5)*pa)
            nhd = int(ph*(s-0.5))
            nw0 = int(pw*(s+0.0)*pa)
            nh0 = int(ph*(s+0.0))
            nwu = int(pw*(s+0.5)*pa)
            nhu = int(ph*(s+0.5))
            dd = abs(ow-nwd) + abs(oh-nhd)
            d0 = abs(ow-nw0) + abs(oh-nh0)
            du = abs(ow-nwu) + abs(oh-nhu)
            if dd == min(dd, d0, du):
                s -= 0.5
            elif d0 == min(dd, d0, du):
                return s
            elif du == min(dd, d0, du):
                s += 0.5
        return config.scale

    def resize_display(self):
        while True:
            new_screen_size = (int(config.pixel_width*config.scale*config.pixel_aspect), int(config.pixel_height*config.scale))
            if (new_screen_size[0] > config.max_width or \
                new_screen_size[1] > config.max_height):
                    config.scale_dec()
            elif (new_screen_size[0] < 290 or \
                  new_screen_size[1] < 200):
                    config.scale_inc()
            else:
                break

        if 'SDL_VIDEO_WINDOW_POS' in os.environ:
            del os.environ['SDL_VIDEO_WINDOW_POS']

        #Resizing the window in only one axis is doesn't work reliably on some
        # versions of Linux so do 2 resizes to force a resize in both X and Y.
        if "screen_size" in dir(config) and \
           (new_screen_size[0] == config.screen_size[0] or \
            new_screen_size[1] == config.screen_size[1]):
                config.screen = pygame.display.set_mode((new_screen_size[0]+1,new_screen_size[1]+1), HWSURFACE|DOUBLEBUF|RESIZABLE)
        config.screen = pygame.display.set_mode(new_screen_size, HWSURFACE|DOUBLEBUF|RESIZABLE)
        config.screen_size = new_screen_size

    def initialize_surfaces(self):
        print("Display mode = %x" % (self.display_mode))
        if self.display_mode & self.PAL_MONITOR_ID == self.PAL_MONITOR_ID:
            self.set_aspect(2)
        else:
            self.set_aspect(1)

        self.pixel_width, self.pixel_height = self.pixel_canvas.get_size()
        self.pixel_req_canvas = pygame.Surface((self.pixel_width, self.pixel_height))
        self.pixel_req_rect = None

        #adjust fonts
        self.fontx = self.closest_scale4(32, self.pixel_width // 40)
        self.fonty = self.closest_scale4(32, self.pixel_height // 25)
        self.font = PixelFont("jewel32.png", sizeX=self.fontx, sizeY=self.fonty)
        self.fonty = int(self.fonty * 1.5)

        config.scale = config.closest_scale()
        config.resize_display()
        config.color = 1
        config.bgcolor = 0

        #Keep spare if same size as new image
        if "pixel_spare_canvas" in dir(self):
            sw, sh = self.pixel_spare_canvas.get_size()
            if sw == self.pixel_width and sh == self.pixel_height:
                self.pixel_spare_canvas.set_palette(self.pal)
            else:
                self.pixel_spare_canvas = pygame.Surface((self.pixel_width, self.pixel_height),0, self.pixel_canvas)
        else:
            self.pixel_spare_canvas = pygame.Surface((self.pixel_width, self.pixel_height),0, self.pixel_canvas)

        self.scaled_image = pygame.Surface((self.pixel_width, self.pixel_height*2))
        cursor_images = pygame.image.load(os.path.join('data', 'cursors.png'))
        self.cursor = cursor(self.scaled_image, self.pixel_width//320, self.pixel_height//200 * 2, self, cursor_images)
        self.toolbar = init_toolbar(config)
        self.menubar = init_menubar(config)
        self.minitoolbar = init_minitoolbar(config)

        self.scanline_canvas = pygame.Surface((self.pixel_width, self.pixel_height*2), SRCALPHA)
        for i in range(0, self.pixel_height*2, 2):
            pygame.draw.line(self.scanline_canvas, Color(0,0,0,100), (0,i), (self.pixel_width,i), 1)

        self.NUM_COLORS = len(self.pal)
        self.set_all_palettes(self.pal)
        self.clear_undo()
        config.toolbar.click(config.toolbar.tool_id("draw"), MOUSEBUTTONDOWN)
        config.toolbar.click(config.toolbar.tool_id("circle1"), MOUSEBUTTONDOWN)
        config.save_undo()


    def initialize(self):
        self.clock = pygame.time.Clock()

        self.MODE_LACE               = 0x0004
        self.MODE_EXTRA_HALFBRIGHT   = 0x0080
        self.MODE_HAM                = 0x0800
        self.MODE_HIRES              = 0x8000
        self.NTSC_MONITOR_ID         = 0x00011000
        self.PAL_MONITOR_ID          = 0x00021000
        self.OCS_MODES = self.MODE_LACE | self.MODE_EXTRA_HALFBRIGHT | self.MODE_HAM | self.MODE_HIRES | self.NTSC_MONITOR_ID | self.PAL_MONITOR_ID

        self.fontx = fontx
        self.fonty = fonty
        self.font = PixelFont("jewel32.png", 8)
        self.last_recompose_timer = 0
        self.max_width = self.dinfo.current_w
        self.max_height = self.dinfo.current_h
        #Setup the pygame screen
        self.pixel_width = 320
        self.pixel_height = 200
        #self.pixel_width = 640
        #self.pixel_height = 400
        self.pixel_modes = ["square","NTSC","PAL"]
        self.pixel_aspects = [1.0, 10.0/11.0, 59.0/54.0]
        self.pixel_mode = "NTSC"
        self.pixel_aspect = 10.0/11.0 #NTSC
        self.color_depth = 16
        self.display_mode = self.NTSC_MONITOR_ID # lores NTSC
        self.scale = 3
        self.scanlines = True
        self.brush = Brush()

        self.primprops = PrimProps()
        self.matte_erase = False
        self.last_drawmode = 2
        self.drawmode = self.primprops.drawmode
        self.fillmode = self.primprops.fillmode
        self.color = 1
        self.bgcolor = 0

        self.NUM_COLORS = 64
        self.filename = ""
        self.filepath = os.path.expanduser("~")
        self.toolmode = 0
        self.tool_selected = 0
        self.subtool_selected = 0
        self.zoom = Zoom(config)
        self.grid_on = False
        self.grid_size = (10,10)
        self.grid_offset = (0,0)
        self.symm_on = False
        self.symm_center = (160,100)
        self.symm_mode = 0
        self.symm_type = 1
        self.symm_num = 6
        self.symm_width = 50
        self.symm_height = 50
        self.constrain_x = -1
        self.constrain_y = -1
        self.help_on = True
        self.polylist = []
        self.airbrush_size = 10
        config.resize_display()
        pygame.display.set_caption("PyDPainter")
        pygame.display.set_icon(pygame.image.load(os.path.join('data', 'icon.png')))
        pygame.key.set_repeat(500, 100)

        self.pixel_canvas = pygame.Surface((self.pixel_width, self.pixel_height),0,8)
        self.pal = [(0,0,0), (224,192,160), (224,0,0), (160,0,0), (208,128,0), (240,224,0),
            (128,240,0), (0,128,0), (0,196,96), (0,208,208), (0,160,240), (0,112,192),
            (0,0,240), (112,0,240), (192,0,224), (198,0,128), (96,32,0), (224,80,32),
            (160,80,32), (240,192,160), (48,48,48), (64,64,64), (80,80,80), (96,96,96),
            (112,112,112), (128,128,128), (144,144,144), (160,160,160), (192,192,192),
            (208,208,208), (224,224,224), (240,240,240)]
        self.pal = quantize_palette(self.pal, self.color_depth)
        self.backuppal = list(self.pal)
        self.truepal = list(self.pal)
        self.pixel_canvas.set_palette(self.pal)

        self.cycling = False
        self.cycle_handled = False
        self.cranges = [colorrange(5120,3,20,31), colorrange(2560,1,3,7), colorrange(2560,1,0,0), colorrange(2560,1,0,0), colorrange(2560,1,0,0), colorrange(2560,1,0,0)]

        self.UNDO_INDEX_MAX = 5
        self.undo_image = []
        self.undo_index = -1
        self.suppress_undo = False
        self.suppress_redraw = False

        self.wait_for_mouseup = [False, False]

        self.initialize_surfaces()
        pygame.mouse.set_visible(False)

    def doKeyAction(self, curr_action=None):
        if curr_action == None:
            curr_action = config.toolbar.tool_id(config.tool_selected).action
        if pygame.mouse.get_pressed() == (0,0,0):
            curr_action.move(config.get_mouse_pixel_pos())
        else:
            curr_action.drag(config.get_mouse_pixel_pos(), pygame.mouse.get_pressed())

    def setDrawMode(self, dm):
        mg = config.menubar.menu_id("mode")
        if config.brush.type == Brush.CUSTOM:
            mg.menug_list[0].enabled = True
            mg.menug_list[2].enabled = True
        else:
            mg.menug_list[0].enabled = False
            mg.menug_list[2].enabled = False

        g = config.menubar.menu_id("mode").menu_id(str(DrawMode(dm)))
        if g != None:
            g.action.selected({})
        return

    def quantize_palette(self, pal, color_depth=16):
        return quantize_palette(pal, color_depth)

    def unique_palette(self, pal):
        return unique_palette(pal)

    def set_all_palettes(config, pal):
        config.pixel_canvas.set_palette(pal)
        config.pixel_spare_canvas.set_palette(pal)

        if config.brush.image != None:
            config.brush.image.set_palette(pal)
        config.brush.cache = BrushCache()

        for img in config.undo_image:
            img.set_palette(pal)

    def get_mouse_pointer_pos(self, event=None):
        mouseX, mouseY = pygame.mouse.get_pos()
        if not event is None and (event.type == MOUSEMOTION or event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN):
            mouseX, mouseY = event.pos
        screenX, screenY = self.screen_size
        mouseX = mouseX * self.pixel_width // screenX
        mouseY = mouseY * self.pixel_height // screenY
        return((mouseX, mouseY))

    def get_mouse_pixel_pos(self, event=None, ignore_grid=False):
        mouseX, mouseY = pygame.mouse.get_pos()

        if not event is None and (event.type == MOUSEMOTION or event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN):
            mouseX, mouseY = event.pos

        screenX, screenY = self.screen_size
        mouseX = mouseX * self.pixel_width // screenX
        mouseY = mouseY * self.pixel_height // screenY

        mouseside = 0

        if self.zoom.on and self.pixel_req_rect == None:
            x0,y0,xw,yh = self.zoom.left_rect
            if (mouseX < x0+xw or self.zoom.mousedown_side == 1) and self.zoom.mousedown_side != 2:
                mouseside = 1
                mouseX += self.zoom.xoffset
                mouseY -= self.zoom.yoffset
            else:
                mouseside = 2
                x0,y0,xw,yh = self.zoom.right_rect
                zx0,zy0, zoom_width,zoom_height = self.zoom.pixel_rect
                if xw + zx0 == 0:
                    mouseX = 0
                else:
                    mouseX = (mouseX - x0) * zoom_width // xw + zx0

                if yh + zy0 == 0:
                    mouseY = 0
                else:
                    if self.menubar.visible:
                        mouseY = (((mouseY - y0 - self.zoom.yoffset + 12) * zoom_height)) // yh + zy0
                    else:
                        mouseY = ((mouseY - y0) * zoom_height) // yh + zy0
        else:
            self.zoom.mousedown_side = 0

        if not event is None and event.type == MOUSEBUTTONDOWN:
            self.zoom.mousedown_side = mouseside
        if not event is None and event.type == MOUSEBUTTONUP:
            self.zoom.mousedown_side = 0

        #turn constrain on or off
        if pygame.key.get_mods() & KMOD_SHIFT:
            if self.constrain_x < 0 and self.constrain_y < 0:
                if "rel" in dir(event):
                    if abs(event.rel[0]) > abs(event.rel[1]):
                        self.constrain_y = mouseY
                    else:
                        self.constrain_x = mouseX
        else:
            self.constrain_x = -1
            self.constrain_y = -1

        #apply constrain
        if self.constrain_x >= 0:
            mouseX = self.constrain_x
        elif self.constrain_y >= 0:
            mouseY = self.constrain_y

        if self.grid_on and self.pixel_req_rect == None and not ignore_grid:
            go = self.grid_offset
            gs = self.grid_size
            mouseX = (mouseX - go[0] + (gs[0]//2)) // gs[0] * gs[0] + go[0]
            mouseY = (mouseY - go[1] + (gs[1]//2)) // gs[1] * gs[1] + go[1]

        return((mouseX, mouseY))

    def has_event(self, timeout=16):
        return pygame.event.peek((KEYDOWN,
                            MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION)) and \
               pygame.time.get_ticks() - self.last_recompose_timer > timeout

    def try_recompose(self):
        if pygame.time.get_ticks() - self.last_recompose_timer > 16:
            config.recompose()

    def recompose(self):
        if self.cycling:
            for crange in config.cranges:
                crange.apply_to_pal(self.pal)
            self.set_all_palettes(self.pal)

        pixel_canvas_rgb = None
        if self.zoom.on:
            pixel_canvas_rgb = pygame.Surface(self.pixel_canvas.get_size(),0)
            w = self.pixel_width // 3
            #pygame.draw.rect(pixel_canvas_rgb, (64,64,64), (w,0,w*2,self.pixel_height))
            zxc,zyc = self.zoom.center
            zoom_width = w*2 // self.zoom.factor
            zoom_height = self.pixel_height // self.zoom.factor
            self.zoom.yoffset = 0
            if self.toolbar.visible:
                zoom_width -= self.toolbar.rect[2] // self.zoom.factor

            self.zoom.xoffset = zxc - (w // 2)
            if self.zoom.xoffset < 0:
                self.zoom.xoffset = 0
            elif self.zoom.xoffset > self.pixel_width - w + 6:
                self.zoom.xoffset = self.pixel_width - w + 6

            menu_bar_height = 0
            if self.menubar.visible:
                menu_bar_height = 12
                self.zoom.yoffset = (zoom_height // 2) - zyc
                if self.zoom.yoffset < 0:
                    self.zoom.yoffset = 0
                elif self.zoom.yoffset > 12:
                    self.zoom.yoffset = 12

            zx0 = zxc-(zoom_width//2)
            zy0 = zyc-(zoom_height//2)
            if zx0 < 0:
                zx0 = 0
            elif zx0+zoom_width > self.pixel_width:
                zx0 = self.pixel_width - zoom_width

            if zy0 < 0:
                zy0 = 0
            elif zy0+zoom_height > self.pixel_height:
                zy0 = self.pixel_height - zoom_height

            #Fix zoom center to be back in range
            zxc = zx0+(zoom_width//2)
            zyc = zy0+(zoom_height//2)-self.zoom.yoffset
            self.zoom.center = (zxc,zyc)

            self.zoom.pixel_rect = (zx0,zy0, zoom_width,zoom_height)

            self.zoom.left_rect = (0,menu_bar_height, w,self.pixel_height)
            self.zoom.border_rect = (w-6,0,6,self.pixel_height)
            #self.zoom.right_rect = (w,0, w*2+2,self.pixel_height)
            self.zoom.right_rect = (w,menu_bar_height, zoom_width*self.zoom.factor,zoom_height*self.zoom.factor)

            pixel_canvas_rgb.blit(self.pixel_canvas, (0,self.zoom.yoffset), (self.zoom.xoffset,0, w,self.pixel_height))
            zoom_canvas = pygame.Surface((zoom_width, zoom_height),0, pixel_canvas_rgb)
            zoom_canvas.blit(pixel_canvas_rgb, (0,0), (zx0-self.zoom.xoffset,zy0+self.zoom.yoffset,zoom_width,zoom_height))
            #zoom_canvas_scaled = pygame.transform.scale(zoom_canvas, (w*2,self.pixel_height))
            zoom_canvas_scaled = pygame.transform.scale(zoom_canvas, (zoom_width*self.zoom.factor,zoom_height*self.zoom.factor))
            pixel_canvas_rgb.blit(zoom_canvas_scaled, (w,self.zoom.yoffset))

            pygame.draw.rect(pixel_canvas_rgb, (0,0,0), (w-6,0,6,self.pixel_height))
            pygame.draw.rect(pixel_canvas_rgb, (128,128,128), (w-5,0,4,self.pixel_height))
        else:
            pixel_canvas_rgb = self.pixel_canvas.convert()

        #blit requestor layer
        if self.pixel_req_rect != None:
            self.cursor.shape = 1
            pixel_canvas_rgb.blit(self.pixel_req_canvas, self.pixel_req_rect, self.pixel_req_rect)
            self.toolbar.tip_canvas = None
            self.minitoolbar.tip_canvas = None

        #blit toolbar layer
        self.toolbar.draw(pixel_canvas_rgb, offset=(self.pixel_width-self.toolbar.rect[2], self.fonty-1 if self.menubar.visible else 0))

        #blit menu layer
        self.menubar.draw(pixel_canvas_rgb)

        #blit minitoolbar layer
        if self.menubar.visible:
            if config.minitoolbar.tool_id("expand").state == 1:
                mtbx = self.pixel_width-self.minitoolbar.rect[2]
            else:
                mtbx = self.pixel_width-(self.minitoolbar.rect[2]//5*2)
            self.minitoolbar.draw(pixel_canvas_rgb, offset=(mtbx, 0))

        #scale image double height
        pygame.transform.scale(pixel_canvas_rgb, (self.pixel_width, self.pixel_height*2), self.scaled_image)

        #draw mouse cursor
        self.cursor.draw()

        if self.scanlines:
            #blit scanlines onto double-high image
            self.scaled_image.blit(self.scanline_canvas, (0,0))

        #scale up image to screen resolution, blurring for retro effect
        pygame.transform.smoothscale(self.scaled_image, self.screen_size, self.screen)
        #blit tooltip layer
        if not self.toolbar.wait_for_tip and \
           self.toolbar.tip_canvas != None and \
           config.help_on:
            tx = self.pixel_width-self.toolbar.rect[2]+self.toolbar.tip_x
            ty = (self.fonty-1 if self.menubar.visible else 0) + self.toolbar.tip_y
            t_size = self.toolbar.tip_canvas.get_size()
            sx = (tx * self.screen_size[0] // self.pixel_width) - t_size[0]
            sy = (ty * self.screen_size[1] // self.pixel_height) - (t_size[1]//2)
            self.screen.blit(self.toolbar.tip_canvas, (sx,sy))

        #blit minitoolbar tooltip layer
        if not self.minitoolbar.wait_for_tip and \
           self.minitoolbar.tip_canvas != None and \
           config.help_on:
            tx = mtbx + self.minitoolbar.tip_x
            ty = self.minitoolbar.tip_y
            t_size = self.minitoolbar.tip_canvas.get_size()
            sx = (tx * self.screen_size[0] // self.pixel_width) - t_size[0]
            sy = (ty * self.screen_size[1] // self.pixel_height) - (t_size[1]//2)
            self.screen.blit(self.minitoolbar.tip_canvas, (sx,sy))

        pygame.display.flip()
        self.last_recompose_timer = pygame.time.get_ticks()


    def save_undo(self):
        if self.suppress_undo:
            self.suppress_undo = False
            return

        #Backup for undo
        self.undo_index = self.undo_index + 1
        if self.undo_index > self.UNDO_INDEX_MAX:
            self.undo_index = self.UNDO_INDEX_MAX
            self.undo_image.pop(0)

        #print "self.undo_index=" + str(self.undo_index) + "  len(self.undo_image)-1=" + str(len(self.undo_image)-1)

        if self.undo_index > len(self.undo_image)-1:
            self.undo_image.append("")

        while len(self.undo_image)-1 > self.undo_index:
            self.undo_image.pop()

        self.undo_image[self.undo_index] = pygame.Surface(self.pixel_canvas.get_size(),0, self.pixel_canvas)
        self.undo_image[self.undo_index].set_palette(self.pal)
        self.undo_image[self.undo_index].blit(self.pixel_canvas, (0,0))

    def clear_undo(self):
        self.suppress_undo = False
        self.undo_image = []
        self.undo_index = -1
        self.save_undo()
        self.suppress_undo = True

    def redo(self):
        config.undo_index = config.undo_index + 1
        if config.undo_index > len(config.undo_image) - 1:
            config.undo_index = len(config.undo_image) - 1
        config.pixel_canvas.blit(config.undo_image[config.undo_index], (0,0))

    def undo(self):
        config.undo_index = config.undo_index - 1
        if config.undo_index < 0:
            config.undo_index = 0
        config.pixel_canvas.blit(config.undo_image[config.undo_index], (0,0))

    def airbrush_coords(self, xc, yc, size=-1):
        if size < 0:
            size = self.airbrush_size
        angle = random.random() * 2.0 * 3.14159
        dist = random.random() * float(size)
        x = int(dist * math.cos(angle))
        y = int(dist * math.sin(angle))
        return ((xc+x, yc+y))

    def clear_pixel_draw_canvas(self):
        self.pixel_canvas.blit(self.undo_image[self.undo_index],(0,0))

    def stop_cycling(self):
        if self.cycling:
            self.cycling = False
            self.pal = list(self.backuppal)
            self.set_all_palettes(self.pal)
            config.brush.size = config.brush.size #invalidate bruch cache
            for rangenum, crange in enumerate(self.cranges):
                pygame.time.set_timer(pygame.USEREVENT+1+rangenum, 0)

    def start_cycling(self):
        if not self.cycling:
            self.backuppal = list(self.pal)
            self.cycling = True
            for rangenum, crange in enumerate(self.cranges):
                if crange.low < crange.high and crange.flags & 1 and crange.rate > 0:
                    pygame.time.set_timer(pygame.USEREVENT+1+rangenum, crange.rate_to_milli())

    def run(self):
        """
        This method is the main application loop.
        """

        config = self
        startX = 0
        startY = 0
        stopX = 0
        stopY = 0
        text_string = ""
        buttons = list(pygame.mouse.get_pressed())
        zoom_drag = None

        last_wait_for_mouseup_gui = False

        self.recompose()

        #main loop
        while 1:
            e = pygame.event.wait()

            if e.type == pygame.MOUSEMOTION and pygame.event.peek((MOUSEMOTION)):
                #get rid of extra mouse movements
                continue

            if e.type == pygame.VIDEORESIZE and pygame.event.peek((VIDEORESIZE)):
                #get rid of extra resize events
                continue

            if e.type >= pygame.USEREVENT:
                if e.type >= pygame.USEREVENT and pygame.event.peek(range(pygame.USEREVENT,pygame.USEREVENT+8)):
                    #get rid of extraneous color cycle and other user events
                    continue

            if e.type == pygame.QUIT:
                return

            if e.type == VIDEORESIZE:
                config.scale = config.closest_scale((e.w, e.h))
                config.resize_display()
                self.recompose()
                continue

            #Intercept keys for toolbar
            if e.type in [KEYDOWN,KEYUP]:
                if curr_action != None:
                    key_handled = False
                    if e.type == KEYDOWN:
                        key_handled = curr_action.keydown(e.key, e.mod, e.unicode)
                    elif e.type == KEYUP:
                        key_handled = curr_action.keyup(e.key, e.mod)
                    if key_handled:
                        self.recompose()
                        continue

            #Keep track of button states
            if e.type == MOUSEMOTION:
                buttons = list(e.buttons)
            elif e.type == MOUSEBUTTONDOWN:
                if e.button <= len(buttons):
                    buttons[e.button-1] = True
            elif e.type == MOUSEBUTTONUP:
                if e.button <= len(buttons):
                    buttons[e.button-1] = False

            #Get toolbar events if any and set current action to tool selected
            te_list = self.toolbar.process_event(self.screen, e, self.get_mouse_pointer_pos)
            if len(te_list) > 0:
                self.cycle_handled = True
            curr_action = None
            if config.zoom.box_on:
                curr_action = config.toolbar.tool_id("magnify").action
            elif config.toolbar.tool_id(config.tool_selected) != None and \
               config.toolbar.tool_id(config.tool_selected).action != None:
                curr_action = config.toolbar.tool_id(config.tool_selected).action

            #Get mintollbar events if any
            if self.menubar.visible:
                mte_list = self.minitoolbar.process_event(self.screen, e, self.get_mouse_pointer_pos)
            else:
                mte_list = []

            #Get menubar events if any
            if len(mte_list) > 0:
                me_list = []
            else:
                me_list = self.menubar.process_event(self.screen, e, self.get_mouse_pointer_pos)

            wait_for_mouseup_gui = True in config.toolbar.wait_for_mouseup or True in config.minitoolbar.wait_for_mouseup or True in config.menubar.wait_for_mouseup

            if wait_for_mouseup_gui:
                self.cycle_handled = True

            #Decide if in draw area
            if not True in config.wait_for_mouseup and \
               (self.toolbar.is_inside(self.get_mouse_pointer_pos(e)) or \
               self.menubar.is_inside(self.get_mouse_pointer_pos(e)) or \
               wait_for_mouseup_gui):
                self.cursor.shape = 1
                hide_draw_tool = True
            elif self.tool_selected == "fill":
                self.cursor.shape = 2
                hide_draw_tool = False
            else:
                self.cursor.shape = 0
                hide_draw_tool = False

            #Do move action for toolbar events
            if curr_action != None and not hide_draw_tool:
                for te in te_list:
                    print(te)
                    if te.gadget.tool_type == ToolGadget.TT_TOGGLE or \
                       te.gadget.tool_type == ToolGadget.TT_GROUP:
                        if e.type == KEYDOWN:
                            if pygame.mouse.get_pressed() == (0,0,0):
                                curr_action.move(self.get_mouse_pixel_pos(e))
                            else:
                                curr_action.drag(self.get_mouse_pixel_pos(e), pygame.mouse.get_pressed())
                        else:
                            curr_action.move(self.get_mouse_pixel_pos(e))
            elif curr_action != None and hide_draw_tool:
                curr_action.hide()

            #process mouse wheel for zoom and pan
            if config.zoom.on and e.type == MOUSEBUTTONDOWN and e.button in [2, 4,5]:
                if e.button == 2: #middle drag
                    zoom_drag = self.get_mouse_pixel_pos(e)
                elif e.button == 4: #scroll up
                    if config.zoom.factor < config.zoom.factor_max:
                        config.zoom.factor += 1
                elif e.button == 5: #scroll down
                    if config.zoom.factor > config.zoom.factor_min:
                        config.zoom.factor -= 1
            if e.type == MOUSEBUTTONUP and e.button == 2:
                zoom_drag = None
            if config.zoom.on and buttons[1] and zoom_drag != None:
                x,y = self.get_mouse_pixel_pos(e)
                cx,cy = config.zoom.center
                dx,dy = zoom_drag
                config.zoom.center = (cx+dx-x,cy+dy-y)

            #process global keys
            if e.type == KEYDOWN:
                self.cycle_handled = True
                gotkey = False
                if e.key == K_PERIOD:
                    gotkey = True
                elif e.key == K_PLUS or e.key == K_EQUALS:
                    gotkey = True
                    if self.tool_selected == "airbrush":
                        self.airbrush_size += 1
                        if self.airbrush_size > 50:
                            self.airbrush_size = 50
                    else:
                        self.brush.size += 1
                        setBIBrush()
                elif e.key == K_MINUS:
                    gotkey = True
                    if self.tool_selected == "airbrush": #Airbrush
                        self.airbrush_size -= 1
                        if self.airbrush_size < 5:
                            self.airbrush_size = 5
                    else:
                        self.brush.size -= 1
                        setBIBrush()
                elif e.key == K_RIGHTBRACKET:
                    gotkey = True
                    if e.mod & KMOD_SHIFT:
                        self.bgcolor = (self.bgcolor + 1) % config.NUM_COLORS
                    else:
                        self.color = (self.color + 1) % config.NUM_COLORS
                elif e.key == K_LEFTBRACKET:
                    gotkey = True
                    if e.mod & KMOD_SHIFT:
                        self.bgcolor = (self.bgcolor - 1) % config.NUM_COLORS
                    else:
                        self.color = (self.color - 1) % config.NUM_COLORS
                elif e.unicode == ",":
                    gotkey = True
                    config.toolbar.tool_id('swatch').pick_color()
                elif e.key == K_F9:
                    if config.menubar.visible:
                        config.menubar.visible = False
                    else:
                        config.menubar.visible = True
                elif e.key == K_F10:
                    if config.toolbar.visible:
                        config.toolbar.visible = False
                        config.menubar.visible = False
                    else:
                        config.toolbar.visible = True
                        config.menubar.visible = True
                elif e.key == K_DELETE:
                    config.cursor.visible = not config.cursor.visible

                if config.zoom.on:
                    gotkey |= config.zoom.process_event(self.screen, e)

                if gotkey:
                    self.doKeyAction(curr_action)

            #No toolbar event so process event as action on selected tool
            if curr_action != None and len(te_list) == 0 and \
               len(mte_list) == 0 and len(me_list) == 0 and \
               not wait_for_mouseup_gui and not hide_draw_tool:
                if e.type == MOUSEMOTION:
                    if e.buttons == (0,0,0):
                        curr_action.move(self.get_mouse_pixel_pos(e))
                    else:
                        curr_action.drag(self.get_mouse_pixel_pos(e), e.buttons)
                elif e.type == MOUSEBUTTONDOWN and buttons[0] != buttons[2]:
                    zoom_region = config.zoom.region(e.pos)
                    config.wait_for_mouseup[zoom_region] = True
                    curr_action.mousedown(self.get_mouse_pixel_pos(e), e.button)
                elif e.type == MOUSEBUTTONUP and buttons[0] == buttons[2]:
                    if last_wait_for_mouseup_gui:
                        curr_action.move(self.get_mouse_pixel_pos(e))
                    else:
                        curr_action.mouseup(self.get_mouse_pixel_pos(e), e.button)
                        config.wait_for_mouseup = [False] * len(config.wait_for_mouseup)
                elif e.type == USEREVENT:
                    if buttons[0] or buttons[2]:
                        curr_action.drag(self.get_mouse_pixel_pos(e), buttons)
                    else:
                        curr_action.move(self.get_mouse_pixel_pos(e))

            last_wait_for_mouseup_gui = wait_for_mouseup_gui

            """
            if not self.toolbar.process_event(self.screen, e, self.get_mouse_pointer_pos) and not self.toolbar.mousedown:
                if e.type == KEYDOWN:
                    shifted = (e.mod & KMOD_SHIFT) > 0
                    controlkey = (e.mod & KMOD_CTRL) > 0
                    if e.key == K_F12:
                        self.toolbar.sl_icons_on = not self.toolbar.sl_icons_on
                    elif e.key == K_F1:
                        self.drawmode.value = DrawMode.MATTE
                    elif e.key == K_F2:
                        self.drawmode.value = DrawMode.COLOR
                    elif e.key == K_F3:
                        self.drawmode.value = DrawMode.REPLACE
                    elif e.key == K_F4:
                        self.drawmode.value = DrawMode.SMEAR
                    elif e.key == K_F5:
                        self.drawmode.value = DrawMode.SHADE
                    elif e.key == K_F6:
                        self.drawmode.value = DrawMode.BLEND
                    elif e.key == K_F7:
                        self.drawmode.value = DrawMode.CYCLE
                    elif e.key == K_F8:
                        self.drawmode.value = DrawMode.SMOOTH
                    elif e.key == K_TAB:
                        if self.cycling:
                            self.stop_cycling()
                        else:
                            self.start_cycling()
                    elif e.key == K_DELETE:
                        self.cursor.visible = not self.cursor.visible
                    elif e.key == K_PLUS or e.key == K_EQUALS:
                        if self.tool_selected == 5: #Airbrush
                            self.airbrush_size += 1
                            if self.airbrush_size > 50:
                                self.airbrush_size = 50
                        else:
                            self.brush.size += 1
                    elif e.key == K_MINUS:
                        if self.tool_selected == 5: #Airbrush
                            self.airbrush_size -= 1
                            if self.airbrush_size < 5:
                                self.airbrush_size = 5
                        else:
                            self.brush.size -= 1
                    elif e.key == K_PERIOD:
                        self.brush.type = Brush.CIRCLE
                        self.brush.size = 1
                        if self.drawmode.value == DrawMode.MATTE:
                            self.drawmode.value = DrawMode.COLOR
                    elif e.key == K_x:
                        if self.brush.image != None and self.brush.image_orig != None:
                            self.brush.image = pygame.transform.flip(self.brush.image, True, False)
                            self.brush.image_orig = pygame.transform.flip(self.brush.image_orig, True, False)
                    elif e.key == K_y:
                        if self.brush.image != None and self.brush.image_orig != None:
                            self.brush.image = pygame.transform.flip(self.brush.image, False, True)
                            self.brush.image_orig = pygame.transform.flip(self.brush.image_orig, False, True)
                    elif e.key == K_z:
                        if self.brush.image != None and self.brush.image_orig != None:
                            self.brush.image = pygame.transform.rotate(self.brush.image, -90)
                            self.brush.image_orig = pygame.transform.rotate(self.brush.image_orig, -90)
                    elif e.key == K_s and controlkey:
                        if self.filename == "" or shifted:
                            pygame.mouse.set_visible(True)
                            self.filename = filedialog.asksaveasfilename(initialdir = self.filepath,title = "Save Picture",filetypes = (("BMP file","*.bmp"),("all files","*.*")))
                            pygame.mouse.set_visible(False)
                        if self.filename != "" and self.filename != (()):
                            #pygame.image.save(self.pixel_canvas, self.filename)
                            #save_iffinfo(self.filename)
                            save_iff(self.filename)
                        else:
                            self.filename = ""
                    elif e.key == K_o and controlkey:
                        pygame.mouse.set_visible(True)
                        self.filename = filedialog.askopenfilename(initialdir = self.filepath,title = "Load Picture",filetypes = (("BMP file","*.bmp"),("IFF file","*.iff"),("all files","*.*")))
                        pygame.mouse.set_visible(False)
                        if self.filename != (()) and self.filename != "":
                            try:
                                self.pixel_canvas = load_pic(self.filename)
                                config.truepal = list(config.pal)
                                config.pal = unique_palette(config.pal)
                                self.initialize_surfaces()
                                self.filepath = os.path.dirname(self.filename)
                            except:
                                pass
                        else:
                            self.filename = ""

                elif e.type == VIDEORESIZE:
                    self.screen_size = (e.w, e.h)
                    self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)

                is_real_event = True

                if e.type == MOUSEMOTION:
                    button1, button2, button3 = e.buttons
                elif e.type == MOUSEBUTTONDOWN:
                    if e.button == 1:
                        button1 = True
                    elif e.button == 2:
                        button2 = True
                    elif e.button == 3:
                        button3 = True
                elif e.type == MOUSEBUTTONUP:
                    if e.button == 1:
                        button1 = False
                    elif e.button == 2:
                        button2 = False
                    elif e.button == 3:
                        button3 = False
                elif e.type > USEREVENT:
                    is_real_event = False

                mouseX, mouseY = self.get_mouse_pixel_pos(e)

                if is_real_event:
                    #Setup drawing canvas
                    if not self.suppress_redraw:
                        config.clear_pixel_draw_canvas()

                    #Turn off modes
                    if last_tool_selected != self.tool_selected:
                        self.toolmode = 0
                        self.polylist = []
                        self.suppress_redraw = False
                        last_mouseX = mouseX
                        last_mouseY = mouseY
                        last_button1 = button1
                        last_button2 = button2
                        last_button3 = button3
                        text_string = ""
                        pygame.time.set_timer(pygame.USEREVENT, 0)

                    #Dotted Freehand
                    if self.tool_selected == 0:
                        if button1:
                            self.suppress_redraw = True
                            config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                        elif button3:
                            self.suppress_redraw = True
                            config.brush.draw(self.pixel_canvas, self.toolbar.bgcolor, (mouseX,mouseY), primprops=PrimProps(drawmode=DrawMode.COLOR))
                        elif not self.toolbar.inside:
                            self.suppress_redraw = False
                            config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Continuous Freehand
                    elif self.tool_selected == 1 and self.subtool_selected == 0:
                        if button1:
                            self.suppress_redraw = True
                            drawline_symm(self.pixel_canvas, self.toolbar.color, (last_mouseX,last_mouseY), (mouseX,mouseY))
                        elif button3:
                            self.suppress_redraw = True
                            drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (last_mouseX,last_mouseY), (mouseX,mouseY), drawmode=DrawMode.COLOR)
                        elif not self.toolbar.inside:
                            self.suppress_redraw = False
                            config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Continuous Polygon
                    elif self.tool_selected == 1 and self.subtool_selected == 1:
                        if button1:
                            self.suppress_redraw = True
                            self.polylist.append((mouseX,mouseY))
                            drawline_symm(self.pixel_canvas, self.toolbar.color, (last_mouseX,last_mouseY), (mouseX,mouseY), xormode=1, handlesymm=True)
                        elif button3:
                            self.suppress_redraw = True
                            self.polylist.append((mouseX,mouseY))
                            drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (last_mouseX,last_mouseY), (mouseX,mouseY), xormode=1, drawmode=DrawMode.COLOR, handlesymm=True)
                        elif e.type == MOUSEBUTTONUP and e.button == 1:
                            config.clear_pixel_draw_canvas()
                            fillpoly(self.pixel_canvas, self.toolbar.color, self.polylist)
                            self.polylist = []
                            self.suppress_redraw = False
                        elif e.type == MOUSEBUTTONUP and e.button == 3:
                            config.clear_pixel_draw_canvas()
                            fillpoly(self.pixel_canvas, self.toolbar.bgcolor, self.polylist, drawmode=DrawMode.COLOR)
                            self.polylist = []
                            self.suppress_redraw = False
                        else:
                            drawline_symm(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY), (mouseX,mouseY), xormode=True)
                    #Straight Line
                    elif self.tool_selected == 2:
                        cycle_handled = True
                        if e.type == MOUSEBUTTONDOWN and (e.button == 1 or e.button == 3):
                            startX = mouseX
                            startY = mouseY

                        if button1:
                            drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY), interrupt=True)
                        elif e.type == MOUSEBUTTONUP and e.button == 1:
                            drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY))
                        elif button3:
                            drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), interrupt=True, drawmode=DrawMode.COLOR)
                        elif e.type == MOUSEBUTTONUP and e.button == 3:
                            drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), drawmode=DrawMode.COLOR)
                        elif not self.toolbar.inside:
                            config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Curve
                    elif self.tool_selected == 3:
                        cycle_handled = True
                        if self.toolmode == 0:
                            self.suppress_undo = True

                            if button1 and not last_button1:
                                startX = mouseX
                                startY = mouseY
                            elif button3 and not last_button3:
                                startX = mouseX
                                startY = mouseY

                            if button1:
                                drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY), interrupt=True)
                            elif last_button1 and not button1:
                                self.toolmode = 1
                                curvecolor = self.toolbar.color
                                stopX = mouseX
                                stopY = mouseY
                                drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY))
                            elif button3:
                                drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), interrupt=True, drawmode=DrawMode.COLOR)
                            elif last_button3 and not button3:
                                self.toolmode = 1
                                curvecolor = self.toolbar.bgcolor
                                stopX = mouseX
                                stopY = mouseY
                                drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), drawmode=DrawMode.COLOR)
                            elif not self.toolbar.inside:
                                config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                        elif not self.toolbar.inside:
                            if last_button1 and not button1:
                                drawcurve(self.pixel_canvas, curvecolor, (startX,startY), (stopX,stopY), (mouseX,mouseY))
                                self.toolmode = 0
                            elif last_button3 and not button3:
                                drawcurve(self.pixel_canvas, curvecolor, (startX,startY), (stopX,stopY), (mouseX,mouseY), drawmode=DrawMode.COLOR)
                                self.toolmode = 0
                            else:
                                drawmode = config.drawmode.value
                                if curvecolor == self.toolbar.bgcolor:
                                    drawmode = DrawMode.COLOR
                                drawcurve(self.pixel_canvas, curvecolor, (startX,startY), (stopX,stopY), (mouseX,mouseY), interrupt=True, drawmode=drawmode)
                    #Fill
                    elif self.tool_selected == 4:
                        if not self.toolbar.inside:
                            self.cursor.shape = 2
                        if button1 and not last_button1:
                            self.suppress_redraw = True
                            floodfill(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                        elif button3 and not last_button3:
                            self.suppress_redraw = True
                            floodfill(self.pixel_canvas, self.toolbar.bgcolor, (mouseX,mouseY))
                        else:
                            cycle_handled = True
                    #Airbrush
                    elif self.tool_selected == 5:
                        if button1:
                            self.suppress_redraw = True
                            for i in range(0,3):
                                config.brush.draw(self.pixel_canvas, self.toolbar.color, self.airbrush_coords(mouseX, mouseY))
                            pygame.time.set_timer(pygame.USEREVENT, 15)
                        elif button3:
                            self.suppress_redraw = True
                            for i in range(0,3):
                                config.brush.draw(self.pixel_canvas, self.toolbar.bgcolor, self.airbrush_coords(mouseX, mouseY))
                            pygame.time.set_timer(pygame.USEREVENT, 15)
                        elif not self.toolbar.inside:
                            self.suppress_redraw = False
                            config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                            pygame.time.set_timer(pygame.USEREVENT, 0)
                    #Rectangle
                    elif self.tool_selected == 6:
                        cycle_handled = True
                        if button1 and not last_button1:
                            startX = mouseX
                            startY = mouseY
                        elif button3 and not last_button3:
                            startX = mouseX
                            startY = mouseY

                        filled = self.subtool_selected
                        if button1:
                            drawrect(self.pixel_canvas, self.toolbar.color,
                                (startX,startY), (mouseX,mouseY),
                                filled=filled, interrupt=True)
                        elif last_button1 and not button1:
                            drawrect(self.pixel_canvas, self.toolbar.color,
                                (startX,startY), (mouseX,mouseY),
                                filled=filled)
                        elif button3:
                            drawrect(self.pixel_canvas, self.toolbar.bgcolor,
                                (startX,startY), (mouseX,mouseY),
                                filled=filled, drawmode=DrawMode.COLOR,
                                interrupt=True)
                        elif last_button3 and not button3:
                            drawrect(self.pixel_canvas, self.toolbar.bgcolor,
                                (startX,startY), (mouseX,mouseY),
                                drawmode=DrawMode.COLOR,
                                filled=filled)
                        elif not self.toolbar.inside:
                            drawline(self.pixel_canvas, self.toolbar.color,
                                (mouseX,0), (mouseX,self.pixel_canvas.get_height()),
                                xormode=True)
                            drawline(self.pixel_canvas, self.toolbar.color,
                                (0,mouseY), (self.pixel_canvas.get_width(),mouseY),
                                xormode=True)
                            if self.subtool_selected == 0:
                                config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Circle
                    elif self.tool_selected == 7:
                        cycle_handled = True
                        if button1 and not last_button1:
                            startX = mouseX
                            startY = mouseY
                        elif button3 and not last_button3:
                            startX = mouseX
                            startY = mouseY

                        radius = int(math.sqrt(abs(mouseX-startX)*abs(mouseX-startX) + abs(mouseY-startY)*abs(mouseY-startY)))
                        if button1:
                            drawcircle(self.pixel_canvas, self.toolbar.color, (startX,startY), radius, self.subtool_selected, interrupt=True)
                        elif last_button1 and not button1:
                            drawcircle(self.pixel_canvas, self.toolbar.color, (startX,startY), radius, self.subtool_selected)
                        elif button3:
                            drawcircle(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), radius, self.subtool_selected, drawmode=DrawMode.COLOR, interrupt=True)
                        elif last_button3 and not button3:
                            drawcircle(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), radius, self.subtool_selected, drawmode=DrawMode.COLOR)
                        elif not self.toolbar.inside:
                            drawline(self.pixel_canvas, self.toolbar.color, (mouseX,0), (mouseX,self.pixel_canvas.get_height()), xormode=True)
                            drawline(self.pixel_canvas, self.toolbar.color, (0,mouseY), (self.pixel_canvas.get_width(),mouseY), xormode=True)
                            if self.subtool_selected == 0:
                                config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Ellipse
                    elif self.tool_selected == 8:
                        cycle_handled = True
                        if button1 and not last_button1:
                            startX = mouseX
                            startY = mouseY
                        elif button3 and not last_button3:
                            startX = mouseX
                            startY = mouseY

                        radiusX = int(abs(mouseX-startX))
                        radiusY = int(abs(mouseY-startY))
                        if button1:
                            drawellipse(self.pixel_canvas, self.toolbar.color, (startX,startY), radiusX, radiusY, self.subtool_selected, interrupt=True)
                        elif last_button1 and not button1:
                            drawellipse(self.pixel_canvas, self.toolbar.color, (startX,startY), radiusX, radiusY, self.subtool_selected)
                        elif button3:
                            drawellipse(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), radiusX, radiusY, self.subtool_selected, drawmode=DrawMode.COLOR, interrupt=True)
                        elif last_button3 and not button3:
                            drawellipse(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), radiusX, radiusY, self.subtool_selected, drawmode=DrawMode.COLOR)
                        elif not self.toolbar.inside:
                            drawline(self.pixel_canvas, self.toolbar.color, (mouseX,0), (mouseX,self.pixel_canvas.get_height()), xormode=True)
                            drawline(self.pixel_canvas, self.toolbar.color, (0,mouseY), (self.pixel_canvas.get_width(),mouseY), xormode=True)
                            if self.subtool_selected == 0:
                                config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                    #Polygon
                    elif self.tool_selected == 9:
                        cycle_handled = True
                        if len(self.polylist) == 0:
                            self.suppress_undo = True

                            if button1 and not last_button1:
                                startX = mouseX
                                startY = mouseY
                            elif button3 and not last_button3:
                                startX = mouseX
                                startY = mouseY

                            if button1:
                                drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY), xormode=self.subtool_selected, handlesymm=True)
                            elif last_button1 and not button1:
                                self.polylist.append((startX,startY))
                                self.polylist.append((mouseX,mouseY))
                                curvecolor = self.toolbar.color
                                stopX = mouseX
                                stopY = mouseY
                                if self.subtool_selected:
                                    drawpoly(self.pixel_canvas, self.toolbar.color, self.polylist, xormode=1)
                                else:
                                    drawline_symm(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY))
                            elif button3:
                                if self.subtool_selected:
                                    drawpoly(self.pixel_canvas, self.toolbar.bgcolor, self.polylist, xormode=1)
                                else:
                                    drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY))
                            elif last_button3 and not button3:
                                self.polylist.append((startX,startY))
                                self.polylist.append((mouseX,mouseY))
                                curvecolor = self.toolbar.bgcolor
                                stopX = mouseX
                                stopY = mouseY
                                if self.subtool_selected:
                                    drawpoly(self.pixel_canvas, self.toolbar.bgcolor, self.polylist, xormode=1)
                                else:
                                    drawline_symm(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY))
                            elif not self.toolbar.inside:
                                if self.subtool_selected == 0:
                                    config.brush.draw(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY))
                                else:
                                    drawline_symm(self.pixel_canvas, self.toolbar.color, (mouseX,mouseY), (mouseX,mouseY), xormode=True, handlesymm=True, interrupt=True)
                        elif not self.toolbar.inside:
                            if last_button1 and not button1:
                                if mouseX >= startX - 2 and mouseX <= startX + 2 and mouseY >= startY - 2 and mouseY <= startY + 2:
                                    self.polylist.append((startX,startY))
                                    if self.subtool_selected:
                                        drawpoly(self.pixel_canvas, curvecolor, self.polylist, filled=1)
                                    else:
                                        drawline_symm(self.pixel_canvas, curvecolor, (stopX,stopY), (startX,startY))
                                    self.polylist = []
                                else:
                                    self.suppress_undo = True
                                    self.polylist.append((mouseX,mouseY))
                                    if self.subtool_selected:
                                        drawpoly(self.pixel_canvas, curvecolor, self.polylist, xormode=True)
                                    else:
                                        drawline_symm(self.pixel_canvas, curvecolor, (stopX,stopY), (mouseX,mouseY))
                                    stopX = mouseX
                                    stopY = mouseY
                            elif last_button3 and not button3:
                                if mouseX >= startX - 2 and mouseX <= startX + 2 and mouseY >= startY - 2 and mouseY <= startY + 2:
                                    self.polylist.append((startX,startY))
                                    if self.subtool_selected:
                                        drawpoly(self.pixel_canvas, curvecolor, self.polylist, filled=1)
                                    else:
                                        drawline_symm(self.pixel_canvas, curvecolor, (stopX,stopY), (startX,startY))
                                    self.polylist = []
                                else:
                                    self.suppress_undo = True
                                    self.polylist.append((mouseX,mouseY))
                                    if self.subtool_selected:
                                        drawpoly(self.pixel_canvas, curvecolor, self.polylist, xormode=True)
                                    else:
                                        drawline_symm(self.pixel_canvas, curvecolor, (stopX,stopY), (mouseX,mouseY))
                                    stopX = mouseX
                                    stopY = mouseY
                            else:
                                if self.subtool_selected:
                                    drawpoly(self.pixel_canvas, curvecolor, self.polylist, filled=0, xormode=True, interrupt=True)
                                drawline_symm(self.pixel_canvas, curvecolor, (stopX,stopY), (mouseX,mouseY), xormode=self.subtool_selected, handlesymm=True, interrupt=True)
                    #Brush
                    elif self.tool_selected == 10:
                        if button1 and not last_button1:
                            startX = mouseX
                            startY = mouseY
                        elif button3 and not last_button3:
                            startX = mouseX
                            startY = mouseY

                        if button1:
                            drawrect(self.pixel_canvas, self.toolbar.color, (startX,startY), (mouseX,mouseY), 0, xormode=True, handlesymm=False)
                        elif last_button1 and not button1:
                            self.brush = Brush(type=Brush.CUSTOM, screen=self.pixel_canvas, bgcolor=self.toolbar.bgcolor, coordfrom=(startX,startY), coordto=(mouseX,mouseY))
                            self.drawmode.value = DrawMode.MATTE
                            self.tool_selected = 0
                        elif button3:
                            drawrect(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), 0, xormode=True, handlesymm=False)
                        elif last_button3 and not button3:
                            self.brush = Brush(type=Brush.CUSTOM, screen=self.pixel_canvas, bgcolor=self.toolbar.bgcolor, coordfrom=(startX,startY), coordto=(mouseX,mouseY))
                            self.drawmode.value = DrawMode.MATTE
                            drawrect(self.pixel_canvas, self.toolbar.bgcolor, (startX,startY), (mouseX,mouseY), 1, xormode=True, handlesymm=False)
                            self.tool_selected = 0
                        elif not self.toolbar.inside:
                            drawline(self.pixel_canvas, self.toolbar.color, (mouseX,0), (mouseX,self.pixel_canvas.get_height()), xormode=True)
                            drawline(self.pixel_canvas, self.toolbar.color, (0,mouseY), (self.pixel_canvas.get_width(),mouseY), xormode=True)
                    #Text
                    elif self.tool_selected == 11:
                        if button1:
                            startX = mouseX
                            startY = mouseY
                            self.toolmode = 1
                            pygame.time.set_timer(pygame.USEREVENT, 500)

                        if self.toolmode == 0:
                            if e.type == KEYDOWN and e.key == K_ESCAPE:
                                self.tools_on = True
                                self.menu_on = True
                                self.tool_selected = 1
                                self.subtool_selected = 0
                            else:
                                drawrect(self.pixel_canvas, self.toolbar.color, (mouseX, mouseY), (mouseX+self.toolbar.font.xsize, mouseY+self.toolbar.font.ysize), 0, xormode=True)
                        else:
                            if e.type == KEYDOWN:
                                if e.key == K_BACKSPACE:
                                    if len(text_string) > 0:
                                        text_string = text_string[:-1]
                                elif e.key == K_ESCAPE:
                                    self.tools_on = True
                                    self.menu_on = True
                                    self.tool_selected = 1
                                    self.subtool_selected = 0
                                else:
                                    text_string += e.unicode
                                self.toolmode = 1
                            self.toolbar.font.blitstring(self.pixel_canvas, (startX, startY), text_string, config.pal[self.toolbar.color], config.pal[self.toolbar.bgcolor], 0) 
                            if e.type == USEREVENT:
                                self.toolmode = (self.toolmode % 2) + 1
                                pygame.time.set_timer(pygame.USEREVENT, 500)
                            if self.toolmode == 1:
                                drawrect(self.pixel_canvas, self.toolbar.color, (startX+self.toolbar.font.calcwidth(text_string), startY), (startX+self.toolbar.font.xsize+self.toolbar.font.calcwidth(text_string), startY+self.toolbar.font.ysize), 0, xormode=True)
                    #Grid
                    elif self.tool_selected == 12:
                        self.grid_on = not self.grid_on
                        self.tool_selected = last_tool_selected
                        self.subtool_selected = last_subtool_selected
                    #Symmetry
                    elif self.tool_selected == 13:
                        self.symm_on = not self.symm_on
                        self.tool_selected = last_tool_selected
                        self.subtool_selected = last_subtool_selected
                    #Magnifier
                    elif self.tool_selected == 14:
                        if last_button1 and not button1:
                            self.zoom_on = True
                            self.toolbar.zoom_center = (mouseX,mouseY)
                            self.tool_selected = zoom_last_tool_selected
                            self.subtool_selected = zoom_last_subtool_selected
                            self.suppress_undo = True
                        elif not self.toolbar.inside:
                            drawrect(self.pixel_canvas, self.toolbar.color, (mouseX-40,mouseY-40), (mouseX+40,mouseY+40), 0, xormode=True, handlesymm=False)
                    #Color Picker
                    elif self.tool_selected == 20:
                        if last_tool_selected != 20:
                            picker_last_tool_selected = last_tool_selected
                            picker_last_subtool_selected = last_subtool_selected

                        if not self.toolbar.inside:
                            self.cursor.shape = 3
                            #Choose color
                            if button1:
                                self.toolbar.color = get_at_mapped(self.pixel_canvas, (mouseX, mouseY))
                            elif button3:
                                self.toolbar.bgcolor = get_at_mapped(self.pixel_canvas, (mouseX, mouseY))
                                self.tool_selected = picker_last_tool_selected
                                self.subtool_selected = picker_last_subtool_selected
                            elif last_button1 and not button1:
                                self.tool_selected = picker_last_tool_selected
                                self.subtool_selected = picker_last_subtool_selected
                            elif last_button3 and not button3:
                                self.tool_selected = picker_last_tool_selected
                                self.subtool_selected = picker_last_subtool_selected


                    last_mouseX = mouseX
                    last_mouseY = mouseY
                    last_button1 = button1
                    last_button2 = button2
                    last_button3 = button3
                    last_tool_selected = self.tool_selected
                    last_subtool_selected = self.subtool_selected

            if e.type == pygame.MOUSEBUTTONUP or e.type == pygame.KEYDOWN:
                #Magnifier
                if self.tool_selected == 14:
                    if last_tool_selected != 14:
                        zoom_last_tool_selected = last_tool_selected
                        zoom_last_subtool_selected = last_subtool_selected

                    if self.zoom_on:
                        self.zoom_on = False
                        self.tool_selected = last_tool_selected
                        self.subtool_selected = last_subtool_selected
                    elif e.type == pygame.KEYDOWN:
                        self.zoom_on = True
                        self.toolbar.zoom_center = (mouseX,mouseY)
                        self.tool_selected = zoom_last_tool_selected
                        self.subtool_selected = zoom_last_subtool_selected
                        self.suppress_undo = True
                #Magnifier zoom in/out
                elif self.tool_selected == 15:
                    if e.type == pygame.MOUSEBUTTONUP:
                        if e.button == 1:
                            self.toolbar.zoom += 1
                            if self.toolbar.zoom > self.toolbar.zoom_max:
                                self.toolbar.zoom = self.toolbar.zoom_max
                    self.tool_selected = last_tool_selected
                    self.subtool_selected = last_subtool_selected
                #Clear
                elif self.tool_selected == 17:
                    self.pixel_canvas.fill(self.toolbar.bgcolor);
                    self.toolbar.menu_on_prev = False
                    self.toolbar.tools_on_prev = False
                    self.tool_selected = last_tool_selected
                    self.subtool_selected = last_subtool_selected
                    self.suppress_undo = False
                    self.save_undo()
                    self.suppress_undo = True

                #Magnifier zoom in/out scroll wheel
                if e.type == pygame.MOUSEBUTTONUP:
                    if e.button == 4:
                        self.toolbar.zoom += 1
                        if self.toolbar.zoom > self.toolbar.zoom_max:
                            self.toolbar.zoom = self.toolbar.zoom_max
                        self.suppress_undo = True
                    elif e.button == 5:
                        self.toolbar.zoom -= 1
                        if self.toolbar.zoom < 2:
                            self.toolbar.zoom = 2
                        self.suppress_undo = True

                #Undo/Redo
                if self.tool_selected == 16:
                    if (e.type == pygame.MOUSEBUTTONUP and e.button == 1) or \
                       (e.type == pygame.KEYDOWN and (e.mod & KMOD_SHIFT) == 0):
                        #undo
                        self.undo_index = self.undo_index - 1
                        if self.undo_index < 0:
                            self.undo_index = 0
                        self.pixel_canvas.blit(self.undo_image[self.undo_index], (0,0))
                        self.suppress_undo = True
                    elif (e.type == pygame.MOUSEBUTTONUP and e.button == 3) or \
                         (e.type == pygame.KEYDOWN and (e.mod & KMOD_SHIFT) > 0):
                        #redo
                        self.undo_index = self.undo_index + 1
                        if self.undo_index > len(self.undo_image) - 1:
                            self.undo_index = len(self.undo_image) - 1
                        self.pixel_canvas.blit(self.undo_image[self.undo_index], (0,0))
                        self.suppress_undo = True

                    self.toolbar.menu_on_prev = False
                    self.toolbar.tools_on_prev = False
                    self.tool_selected = last_tool_selected
                    self.subtool_selected = last_subtool_selected
            """
            if buttons[0] and e.type <= pygame.USEREVENT and not self.cycle_handled:
                cycle()
            self.cycle_handled = False

            #if e.type == pygame.MOUSEBUTTONUP and (e.button == 1 or e.button == 3):
            #    self.save_undo()

            #self.suppress_undo = False

            self.recompose()

