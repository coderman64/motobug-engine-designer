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

    def draw(self):
        # get the display size
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)
        

        # draw the background to the control bar
        SDL_SetRenderDrawColor(self.rend, 255,255,255,200)

        uiRect = SDL_Rect()
        uiRect.x, uiRect.y, uiRect.w, uiRect.h = 0,0,dispw.value,40
        SDL_RenderFillRect(self.rend,uiRect)

        uiRect.x = -36
        for i in self.icons:
            uiRect.x, uiRect.y, uiRect.w, uiRect.h = uiRect.x+40,4,32,32
            SDL_RenderCopy(self.rend,i,None,uiRect)
    def interact(self,x):
        selectedAct = floor(x/40)
        if len(self.actions) > selectedAct and selectedAct >= 0:
            self.actions[selectedAct]()