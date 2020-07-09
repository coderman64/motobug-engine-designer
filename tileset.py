from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from ctypes import c_int
from fonttools import quickRenderText
from math import floor
import os

class tileSet:
    def __init__(self,renderer,project):
        self.texArray = []
        self.nameArray = []
        self.texCount = 0
        self.rend = renderer
        self.project = project
        self.path = ""
    def loadTex(self,texPath):
        image = IMG_Load(texPath)
        if not image:
            print("ERROR: image could not be found at %s",texPath)
            exit(1)
        self.nameArray.append(str(texPath)[str(texPath).rfind("/")+1:str(texPath).rfind(".")])
        self.texArray.append(SDL_CreateTextureFromSurface(self.rend,
                                            image))
        self.texCount += 1
    def getTex(self,index):
        if index >= 0 and index < self.texCount:
            return self.texArray[index]
        else:
            raise IndexError("Cannot access tileTexture "+str(index)+" of tileSet object")
    def loadTexFromFile(self,fileName):
        self.path = fileName
        file = open(fileName).read()
        self.tiles = []
        for i in file.splitlines():
            tileLoc = ""
            if(i.find("||") > -1):
                tileLoc = i[i.find("||")+2:]
            else:
                tileLoc = i[i.find(">")+1:]
            self.loadTex(bytes(os.path.join(self.project.projPath,tileLoc),"ASCII"))

class tilePallet:
    def __init__(self,rend,ts):
        """
        create a tile pallet object
        rend: SDL_Renderer responsible for drawing the pallet
        ts: tileSet
        """
        self.tileSet = ts
        self.open = False
        self.xpos = 0
        self.scroll = 0
        self.rend = rend
        self.ft_Mono16 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",16)
        self.selected = 0
        self.scrolling = False

    def setTileset(self,ts):
        self.tileSet = ts
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
            #draw the background for the tile pallet
            SDL_SetRenderDrawColor(self.rend,0,0,0,200)
            rect = SDL_Rect()
            rect.x, rect.y, rect.w, rect.h = round(self.xpos-200),0,200,disph.value
            SDL_RenderFillRect(self.rend,rect)

            # draw edge line 
            SDL_SetRenderDrawColor(self.rend,255,255,255,255)
            rect.x, rect.y, rect.w, rect.h = round(self.xpos-1),0,1,disph.value
            SDL_RenderFillRect(self.rend,rect)

            # draw tile previews
            for i in range(self.tileSet.texCount):
                # highlight selected tile
                if i == self.selected:
                    rect.x, rect.y, rect.w, rect.h = round(self.xpos-185),i*150+45-self.scroll,138,138
                    SDL_SetRenderDrawColor(self.rend,255,255,255,100)
                    SDL_RenderFillRect(self.rend,rect) 
                # draw tile preview
                rect.x, rect.y, rect.w, rect.h = round(self.xpos-180),i*150+50-self.scroll,128,128
                SDL_RenderCopy(self.rend,self.tileSet.getTex(i),None,rect)
                SDL_SetRenderDrawColor(self.rend,255,255,255,255)

                # draw the file name for the tile
                quickRenderText(self.rend,self.ft_Mono16,self.tileSet.nameArray[i],rect.x,rect.y+128)
    
    def interact(self,mouseY):
        index = floor((mouseY+self.scroll-50)/150)
        if index >= 0 and index < self.tileSet.texCount:
            self.selected = index
        #i*150+50-self.scroll

    def scrollbar(self,mouseY):
        self.scrolling = True
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)
        pixPerTex = (disph.value-50)/self.tileSet.texCount
        self.selected = round((mouseY-50)/pixPerTex)
        self.selected = max(min(self.selected,self.tileSet.texCount-1),0)

        self.scroll = self.selected*150

        if self.scroll <= 0:
            self.scroll = 0
        if self.scroll+disph.value >= self.tileSet.texCount*150+178:
            self.scroll = self.tileSet.texCount*150+178-disph.value
    
    def stopScroll(self):
        self.scrolling = False
        
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
        if self.scroll+disph.value >= self.tileSet.texCount*150+178:
            self.scroll = self.tileSet.texCount*150+178-disph.value
            
    
    def getSelectedTile(self):
        return self.selected
        