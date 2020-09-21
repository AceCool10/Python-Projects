#!/usr/bin/python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os.path, colorsys

import gadget
from gadget import *

from prim import *

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

config = None

def menureq_set_config(config_in):
    global config
    config = config_in


def place_point(symm_center):
    point_coords = (0,0)
    pixel_req_rect_bak = config.pixel_req_rect
    config.pixel_req_rect = None
    config.recompose()
    point_placed = False
    first_time = True
    while not point_placed:
        event = pygame.event.poll()
        while event.type == pygame.MOUSEMOTION and pygame.event.peek((MOUSEMOTION)):
            #get rid of extra mouse movements
            event = pygame.event.poll()

        if event.type == pygame.NOEVENT and not first_time:
            event = pygame.event.wait()

        mouseX, mouseY = config.get_mouse_pixel_pos(event, ignore_grid=True)
        if event.type == MOUSEMOTION:
            pass
        elif event.type == MOUSEBUTTONUP:
            point_coords = (mouseX, mouseY)
            point_placed = True
        config.clear_pixel_draw_canvas()
        #old center
        scx,scy = symm_center
        ph = config.pixel_canvas.get_height()
        pw = config.pixel_canvas.get_width()
        drawline(config.pixel_canvas, 1,
            (scx,scy-(ph//10)), (scx,scy+(ph//10)),
            xormode=True)
        drawline(config.pixel_canvas, 1,
            (scx-int(ph/(10*config.pixel_aspect)),scy), (scx+int(ph/(10*config.pixel_aspect)),scy),
            xormode=True)
        #current center
        drawline(config.pixel_canvas, 1,
            (mouseX,0), (mouseX,config.pixel_canvas.get_height()),
            xormode=True)
        drawline(config.pixel_canvas, 1,
            (0,mouseY), (config.pixel_canvas.get_width(),mouseY),
            xormode=True)
        config.recompose()
        first_time = False

    config.pixel_req_rect = pixel_req_rect_bak
    config.clear_pixel_draw_canvas()
    config.recompose()

    return point_coords

def place_grid(gcoords):
    n = 4
    w = gcoords[2]
    ow = w
    h = gcoords[3]
    oh = h
    point_coords = (0,0)
    mpoint_coords = point_coords
    pixel_req_rect_bak = config.pixel_req_rect
    config.pixel_req_rect = None
    config.recompose()
    dragging = False
    point_placed = False
    first_time = True
    while not point_placed:
        event = pygame.event.poll()
        while event.type == pygame.MOUSEMOTION and pygame.event.peek((MOUSEMOTION)):
            #get rid of extra mouse movements
            event = pygame.event.poll()

        if event.type == pygame.NOEVENT and not first_time:
            event = pygame.event.wait()

        mouseX, mouseY = config.get_mouse_pixel_pos(event, ignore_grid=True)
        if not dragging:
            point_coords = (mouseX-(n*w), mouseY-(n*h))
            mpoint_coords = (mouseX, mouseY)
        if event.type == MOUSEMOTION:
            if dragging:
                diffX = mouseX - mpoint_coords[0]
                diffY = mouseY - mpoint_coords[1]
                h = oh + (diffY // n)
                if h == 0:
                    h = 1
                w = ow + (diffX // n)
                if w == 0:
                    w = 1
        elif event.type == MOUSEBUTTONDOWN:
            dragging = True
        elif event.type == MOUSEBUTTONUP:
            point_placed = True
        config.clear_pixel_draw_canvas()

        pcx,pcy = point_coords
        for x in range(0,n+1):
            drawline(config.pixel_canvas, 1,
                (pcx+(x*w),pcy), (pcx+(x*w),pcy+(n*h)),
                xormode=True)
        for y in range(0,n+1):
            drawline(config.pixel_canvas, 1,
                (pcx+(n*w),pcy+(y*h)), (pcx,pcy+(y*h)),
                xormode=True)

        config.menutitle_extra = str(pcx) + ", " + str(pcy) + ", " + str(w) + ", " + str(h)
        config.recompose()
        first_time = False

    config.menutitle_extra = ""
    config.pixel_req_rect = pixel_req_rect_bak
    config.clear_pixel_draw_canvas()
    config.recompose()

    w = int(abs(w))
    h = int(abs(h))
    return (point_coords[0]%w, point_coords[1]%h, w, h)

def grid_req(screen):
    req = str2req("Grid", """
          X     Y
Size:   _____ _____
Offset: _____ _____
[Visual]
[Cancel][OK]
""", "", mouse_pixel_mapper=config.get_mouse_pixel_pos, font=config.font)
    req.center(screen)
    config.pixel_req_rect = req.get_screen_rect()

    sizeXg = req.gadget_id("8_1")
    sizeYg = req.gadget_id("14_1")
    offsetXg = req.gadget_id("8_2")
    offsetYg = req.gadget_id("14_2")
    visualg = req.gadget_id("0_3")

    sizeXg.value = str(config.grid_size[0])
    sizeXg.numonly = True
    sizeYg.value = str(config.grid_size[1])
    sizeYg.numonly = True
    offsetXg.value = str(config.grid_offset[0])
    offsetXg.numonly = True
    offsetYg.value = str(config.grid_offset[1])
    offsetYg.numonly = True

    req.draw(screen)
    config.recompose()

    running = 1
    while running:
        event = pygame.event.wait()
        gevents = req.process_event(screen, event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = 0 

        for ge in gevents:
            if ge.gadget.type == Gadget.TYPE_BOOL:
                if ge.gadget.label == "OK" and not req.has_error():
                    config.grid_size = (int(sizeXg.value), int(sizeYg.value))
                    config.grid_offset = (int(offsetXg.value)%int(sizeXg.value), int(offsetYg.value)%int(sizeYg.value))
                    running = 0
                elif ge.gadget.label == "Cancel":
                    running = 0 
                elif ge.gadget == visualg and not req.has_error():
                    gcoords = place_grid((int(offsetXg.value)%int(sizeXg.value), int(offsetYg.value)%int(sizeYg.value), int(sizeXg.value), int(sizeYg.value)))
                    offsetXg.value = str(gcoords[0])
                    offsetXg.need_redraw = True
                    offsetYg.value = str(gcoords[1])
                    offsetYg.need_redraw = True
                    sizeXg.value = str(gcoords[2])
                    sizeXg.need_redraw = True
                    sizeYg.value = str(gcoords[3])
                    sizeYg.need_redraw = True
                    req.draw(screen)

        if not pygame.event.peek((KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, VIDEORESIZE)):
            req.draw(screen)
            config.recompose()

    config.pixel_req_rect = None
    config.recompose()

    return

def symmetry_tile_req(screen):
    req = str2req("Symmetry", """
[Point ][ Tile ]

Width:   ____
Height:  ____
[Cancel][OK]
""", "", mouse_pixel_mapper=config.get_mouse_pixel_pos, font=config.font)
    req.center(screen)
    config.pixel_req_rect = req.get_screen_rect()

    pointg = req.gadget_id("0_0")
    tileg = req.gadget_id("8_0")

    cyclicg = req.gadget_id("0_1")
    mirrorg = req.gadget_id("8_1")

    widthl = req.gadget_id("0_2")
    widthg = req.gadget_id("9_2")

    heightl = req.gadget_id("0_3")
    heightg = req.gadget_id("9_3")

    widthg.value = str(config.symm_width)
    widthg.numonly = True
    heightg.value = str(config.symm_height)
    heightg.numonly = True
    tileg.state = 1
    req.draw(screen)
    config.recompose()

    running = 1
    while running:
        event = pygame.event.wait()
        gevents = req.process_event(screen, event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = 0 

        for ge in gevents:
            if ge.gadget.type == Gadget.TYPE_BOOL:
                if ge.gadget.label == "OK" and not req.has_error():
                    config.symm_mode = 1
                    config.symm_width = int(widthg.value)
                    config.symm_height = int(heightg.value)
                    running = 0 
                elif ge.gadget.label == "Cancel":
                    running = 0 
                elif ge.gadget == pointg:
                    return 0

        tileg.state = 1
        if not pygame.event.peek((KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, VIDEORESIZE)):
            req.draw(screen)
            config.recompose()
    return -1

def symmetry_point_req(screen):
    req = str2req("Symmetry", """
[Point ][ Tile ]
[Cyclic][Mirror]
Order:   ___
        [Place ]
[Cancel][OK]
""", "", mouse_pixel_mapper=config.get_mouse_pixel_pos, font=config.font)
    req.center(screen)
    config.pixel_req_rect = req.get_screen_rect()

    pointg = req.gadget_id("0_0")
    tileg = req.gadget_id("8_0")

    cyclicg = req.gadget_id("0_1")
    mirrorg = req.gadget_id("8_1")

    orderl = req.gadget_id("0_2")
    orderg = req.gadget_id("9_2")

    placeg = req.gadget_id("8_3")

    orderg.value = str(config.symm_num)
    orderg.numonly = True
    pointg.state = 1

    if config.symm_type == 0:
        cyclicg.state = 1
    elif config.symm_type == 1:
        mirrorg.state = 1

    symm_center = config.symm_center

    req.draw(screen)
    config.recompose()

    running = 1
    while running:
        event = pygame.event.wait()
        gevents = req.process_event(screen, event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = 0 

        for ge in gevents:
            if ge.gadget.type == Gadget.TYPE_BOOL:
                if ge.gadget.label == "OK" and not req.has_error():
                    config.symm_mode = 0
                    config.symm_num = int(orderg.value)
                    config.symm_center = symm_center
                    running = 0 
                elif ge.gadget.label == "Cancel":
                    running = 0 
                elif ge.gadget == tileg:
                    return 1
                elif ge.gadget == cyclicg:
                    config.symm_type = 0
                elif ge.gadget == mirrorg:
                    config.symm_type = 1
                elif ge.gadget == placeg:
                    symm_center = place_point(symm_center)

        pointg.state = 1

        if config.symm_type == 0:
            cyclicg.state = 1
        elif config.symm_type == 1:
            mirrorg.state = 1

        if not pygame.event.peek((KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, VIDEORESIZE)):
            req.draw(screen)
            config.recompose()
    return -1


def symmetry_req(screen):
    symm_mode = config.symm_mode

    while symm_mode >= 0:
        if symm_mode == 0:
            symm_mode = symmetry_point_req(screen)
        elif symm_mode == 1:
            symm_mode = symmetry_tile_req(screen)

    config.pixel_req_rect = None

def spacing_req(screen):
    req = str2req("Spacing", """
[N Total]      ____
[Every Nth dot]____
[Airbrush]     ____
[Continuous]
[Cancel][OK]
""", "", mouse_pixel_mapper=config.get_mouse_pixel_pos, font=config.font)
    req.center(screen)
    config.pixel_req_rect = req.get_screen_rect()

    n_totalg = req.gadget_id("0_0")
    n_total_valueg = req.gadget_id("15_0")
    n_total_valueg.numonly = True
    n_total_valueg.value = str(config.primprops.drawmode.n_total_value)

    every_ng = req.gadget_id("0_1")
    every_n_valueg = req.gadget_id("15_1")
    every_n_valueg.numonly = True
    every_n_valueg.value = str(config.primprops.drawmode.every_n_value)

    airbrushg = req.gadget_id("0_2")
    airbrush_valueg = req.gadget_id("15_2")
    airbrush_valueg.numonly = True
    airbrush_valueg.value = str(config.primprops.drawmode.airbrush_value)

    continuousg = req.gadget_id("0_3")

    spacing = config.primprops.drawmode.spacing
    button_list = [continuousg, n_totalg, every_ng, airbrushg]
    button_list[spacing].state = 1

    req.draw(screen)
    config.recompose()

    running = 1
    while running:
        event = pygame.event.wait()
        gevents = req.process_event(screen, event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = 0 

        button_list[spacing].state = 1

        for ge in gevents:
            if ge.gadget.type == Gadget.TYPE_BOOL:
                if ge.gadget.label == "OK" and not req.has_error():
                    config.primprops.drawmode.spacing = spacing
                    config.primprops.drawmode.n_total_value = int(n_total_valueg.value)
                    config.primprops.drawmode.every_n_value = int(every_n_valueg.value)
                    config.primprops.drawmode.airbrush_value = int(airbrush_valueg.value)
                    if config.primprops.drawmode.n_total_value < 2:
                        config.primprops.drawmode.n_total_value = 2
                    if config.primprops.drawmode.every_n_value < 1:
                        config.primprops.drawmode.every_n_value = 1
                    if config.primprops.drawmode.airbrush_value < 1:
                        config.primprops.drawmode.airbrush_value = 1
                    running = 0
                elif ge.gadget.label == "Cancel":
                    running = 0 
                elif ge.gadget in button_list:
                    button_list[spacing].state = 0
                    button_list[spacing].needs_redraw = True
                    spacing = button_list.index(ge.gadget)
                    ge.gadget.state = 1
                    ge.gadget.needs_redraw = True

        if not pygame.event.peek((KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, VIDEORESIZE)):
            req.draw(screen)
            config.recompose()

    config.pixel_req_rect = None
    config.recompose()

    return

def fill_req(screen):
    req = str2req("Fill Type", """
[Solid~Tint~Brush~Wrap]
[Perspective]
             #########
             #########
[Pattern]    #########
 [From brush]#########
             #########
             #########
Gradient: [^v~"u~<>~()]
Dither: --------------
        ##############
[Cancel][OK]
""", "", mouse_pixel_mapper=config.get_mouse_pixel_pos, font=config.font)
    req.center(screen)
    config.pixel_req_rect = req.get_screen_rect()

    #assign gadget variables

    req.draw(screen)
    config.recompose()

    running = 1
    while running:
        event = pygame.event.wait()
        gevents = req.process_event(screen, event)

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = 0

        for ge in gevents:
            if ge.gadget.type == Gadget.TYPE_BOOL:
                if ge.gadget.label == "OK" and not req.has_error():
                    running = 0
                elif ge.gadget.label == "Cancel":
                    running = 0

        if not pygame.event.peek((KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, VIDEORESIZE)):
            req.draw(screen)
            config.recompose()

    config.pixel_req_rect = None
    config.recompose()

    return

