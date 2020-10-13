import pygame
import random

pygame.init()

display_height=600
display_width=400
gamedisplay=pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Piano Tiles by Sdzero')

clock=pygame.time.Clock()
font1=pygame.font.SysFont(None,80)
font2=pygame.font.SysFont(None,30)

FPS=30
grey=(180,180,180)
white=(255,255,255)
black=(0,0,0)

speed=5
accelaration=1
(gridx,gridy)=(4,4)
rectl=[]
rectx=[0,display_width/4,display_width/2,3*display_width/4]
#======================= VERTICLE LINES  ==============================================================================
def setup():
    pygame.draw.line(gamedisplay,black,(rectx[1],0),(rectx[1],display_height))
    pygame.draw.line(gamedisplay,black,(rectx[2],0),(rectx[2],display_height))
    pygame.draw.line(gamedisplay,black,(rectx[3],0),(rectx[3],display_height))

#================  TEXT  ============================================================================================
def message(msg,color,font,y_disp=0):
    textSurf=font.render(msg,True,color)
    textRect=textSurf.get_rect()
    textRect.center=display_width/2,display_height/2+y_disp
    gamedisplay.blit(textSurf,textRect)
#=============================================================================================================
class rectangles:
    def __init__(self,rectlist):
        self.rectlist=rectlist
        self.speed=speed
        self.accelaration=accelaration
    def move(self):
        for i in self.rectlist:
            i[1]+=self.speed
            #self.speed=self.speed+self.accelaration
    def addrect(self):
        self.rectlist.append(pygame.Rect(rectx[random.randint(0,3)],-300,rectx[1],150))
    def drawthem(self):
        for i in self.rectlist:
            pygame.draw.rect(gamedisplay,black,i)

#============================================================================================================
gameon=True
rects=rectangles(rectl)
rects.addrect()
score=0
while gameon:

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            quit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            #print(event.pos)
            if gamedisplay.get_at(event.pos)==white:
                gameon=False
            else :
                score+=1
                pygame.draw.rect(gamedisplay,grey,rects.rectlist[0])
                rects.rectlist.pop(0)
                FPS+=accelaration

            '''elif event.pos[0]>rects.rectlist[-1][0] and event.pos[0]<rects.rectlist[-1][0]+100:
                print("passed x")
                if event.pos[1]>rects.rectlist[-1][1] and event.pos[1]<rects.rectlist[-1][1]+150:
                    print("clicked")'''
    gamedisplay.fill(white)
    setup()
    rects.drawthem()
    rects.move()
    message(f"Score:{score}",(255,0,0),font1,250)
    if rects.rectlist[-1][1]==-150:
        rects.addrect()
    elif rects.rectlist[0][1]>600:
        gameon=False

    pygame.display.update()
    clock.tick(FPS)
while not gameon:
    gamedisplay.fill(white)
    message("you lost",black,font1)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            quit()
pygame.quit()
quit()
