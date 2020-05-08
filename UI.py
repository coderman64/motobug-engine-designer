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
        self.hlList = [False for i in iconList]
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
            if self.hlList[i]:
                SDL_SetRenderDrawColor(self.rend,255,255,255,255)
                SDL_RenderFillRect(self.rend,uiRect)
            SDL_RenderCopy(self.rend,self.icons[i],None,uiRect)
        if self.interactionTimer > 0:
            self.interactionTimer -= 0.1
        
    def interact(self,x):
        selectedAct = floor(x/40)
        if len(self.actions) > selectedAct and selectedAct >= 0:
            self.actions[selectedAct]()
            self.lastInteracted = selectedAct
            self.interactionTimer = 2
    def toggleHighlight(self,index):
        self.hlList[index] = not self.hlList[index]
    
class layerPallet:
    def __init__(self,rend):
        """
        create a layer pallet object
        
        rend: SDL_Renderer responsible for drawing the pallet
        """
        self.open = False
        self.xpos = 0
        self.scroll = 0
        self.rend = rend
        self.ft_Mono16 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",16)
        self.selected = -1
        self.layercount = 3
    def draw(self):

        if self.open:
            self.xpos += (200-self.xpos)*0.1
        else:
            self.xpos += (-self.xpos)*0.1

        # get the display size
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)

        # don't waste resources drawing the pallet if it isn't onscreen
        if self.xpos > 5:
            #draw the background for the layer pallet
            SDL_SetRenderDrawColor(self.rend,0,0,0,200)
            rect = SDL_Rect()
            rect.x, rect.y, rect.w, rect.h = dispw.value-round(self.xpos-1),0,200,disph.value
            SDL_RenderFillRect(self.rend,rect)

            # draw edge line 
            SDL_SetRenderDrawColor(self.rend,255,255,255,255)
            rect.x, rect.y, rect.w, rect.h = dispw.value-round(self.xpos-1),0,1,disph.value
            SDL_RenderFillRect(self.rend,rect)

            for i in range(self.layercount):
                # highlight selected layer
                if i-1 == self.selected:
                    rect.x, rect.y, rect.w, rect.h = dispw.value-round(self.xpos-1),i*150+45-self.scroll,138,138
                    SDL_SetRenderDrawColor(self.rend,255,255,255,100)
                    SDL_RenderFillRect(self.rend,rect) 
                # draw the number of the layer
                SDL_SetRenderDrawColor(self.rend,255,255,255,255)
                if i-1 >= 0:
                    quickRenderText(self.rend,self.ft_Mono16,"Layer "+str(i-1),rect.x+20,i*150+178-self.scroll)
                else:
                    quickRenderText(self.rend,self.ft_Mono16,"All layers",rect.x+20,i*150+178-self.scroll)
    
    def interact(self,mouseY):
        index = floor((mouseY+self.scroll-50)/150)
        if index >= 0 and index < self.layercount:
            self.selected = index-1
        
    def toggle(self):
        self.open = not self.open

    def scrollY(self,yrel):
        # get the display size
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)

        # scroll vertically
        self.scroll += yrel

        # limit scrolling
        if self.scroll <= 0:
            self.scroll = 0
        if self.scroll+disph.value >= self.layercount*150+178:
            self.scroll = self.layercount*150+178-disph.value
            
    
    def getSelectedLayer(self):
        return self.selected