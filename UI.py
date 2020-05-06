import ctypes
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from fonttools import *
from math import floor


class controlBar:
    def __init__(self,rend,iconList,actionList):
        # save a link to the renderer
        self.rend = rend

        # load in all the icons
        self.icons = []
        for i in iconList:
            image = IMG_Load(bytes(i,"ASCII"))
            self.icons.append(SDL_CreateTextureFromSurface(self.rend,
                                            image))
        self.actions = actionList
        self.lastInteracted = -1
        self.interactionTimer = 0

    def draw(self):
        # get the display size
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)
        

        # draw the background to the control bar
        SDL_SetRenderDrawColor(self.rend, 255,255,255,200)

        uiRect = SDL_Rect()
        uiRect.x, uiRect.y, uiRect.w, uiRect.h = 0,0,dispw.value,40
        SDL_RenderFillRect(self.rend,uiRect)

        for i in range(len(self.icons)):
            if i == self.lastInteracted:
                uiRect.x, uiRect.y, uiRect.w, uiRect.h = i*40+round(self.interactionTimer)+4,4+round(self.interactionTimer),32,32
            else:
                uiRect.x, uiRect.y, uiRect.w, uiRect.h = i*40+4,4,32,32
            SDL_RenderCopy(self.rend,self.icons[i],None,uiRect)
        if self.interactionTimer > 0:
            self.interactionTimer -= 0.1
        
    def interact(self,x):
        selectedAct = floor(x/40)
        if len(self.actions) > selectedAct and selectedAct >= 0:
            self.actions[selectedAct]()
            self.lastInteracted = selectedAct
            self.interactionTimer = 2