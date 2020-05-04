import ctypes
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from tileset import *
from level import level
from math import *

from fonttools import *
from UI import *

def main():
    SDL_Init(SDL_INIT_VIDEO)
    TTF_Init()
    window = SDL_CreateWindow(b"Motobug Studio (beta 0.2)",
                                SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                640, 480, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE)
    if not window:
        print("WINDOW COULD NOT BE CREATED!")
        exit(1)

    mainRenderer = SDL_CreateRenderer(window,-1,SDL_RENDERER_ACCELERATED)

    SDL_SetRenderDrawBlendMode(mainRenderer,SDL_BLENDMODE_BLEND)

    tiles = tileSet(mainRenderer)
    tiles.loadTexFromFile("projects/CrystalGeyser/tiles.txt")
    level1 = level(mainRenderer,tiles)
    
    tpal = tilePallet(mainRenderer,tiles)

    # set up the control bar
    cBar = controlBar(mainRenderer,["icons/list.png"],[tpal.toggle])

    editorScale = 1

    ft_Mono16 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",16)

    # should the program still be in the main loop?
    looping = True

    # keep track of editor conditions and controls
    camx, camy = 0,-32
    mousex, mousey = 0,0
    mouseMoving = False
    ctrlPress = False
    toolTipAlpha = 0
    hlRect = SDL_Rect()
    hlRect.x, hlRect.y, hlRect.w, hlRect.h = 0,0,128,128
    selectedTile = 0

    # window width and height values (updated within loop)
    winWidth,winHeight = ctypes.c_long(640), ctypes.c_long(480)

    while looping:
        SDL_GetWindowSize(window,winWidth,winHeight)

        # define situations where the mouse isn't available to the main editor
        # space
        mouseOut = mousey <= 40 or mousex <= tpal.xpos

        event = SDL_Event()
        while(SDL_PollEvent(ctypes.byref(event))):
            if(event.type == SDL_QUIT or (event.type == SDL_KEYUP and event.key.keysym.sym == SDLK_ESCAPE)):
                looping = False

            # panning 
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_MIDDLE:
                # when the middle mouse button is pressed, start panning, and activate
                # the relative mouse mode
                mouseMoving = True
                SDL_SetRelativeMouseMode(SDL_TRUE)
            if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_MIDDLE:
                # when the middle mouse button is released, stop panning, and deactivate
                # the relative mouse mode
                mouseMoving = False
                SDL_SetRelativeMouseMode(SDL_FALSE)
            if event.type == SDL_MOUSEMOTION:
                # if panning is active, pan the display with the given mouse motion
                if mouseMoving:
                    camx -= event.motion.xrel / editorScale
                    camy -= event.motion.yrel / editorScale
                # record the newest mouse position
                mousex, mousey = event.motion.x, event.motion.y

            # add tile
            if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_LEFT and not mouseOut:
                # add currently selected tile
                level1.add(floor((mousex+camx*editorScale)/(128*editorScale)),floor((mousey+camy*editorScale)/(128*editorScale)),tpal.getSelectedTile())
                
                # if tile was added out of bounds to the left or the top of the level, 
                # change the camera position accordingly
                if floor((mousey+camy*editorScale)/(128*editorScale)) < 0:
                    camy += 128*abs(floor((mousey+camy*editorScale)/(128*editorScale)))
                if floor((mousex+camx*editorScale)/(128*editorScale)) < 0:
                    camx += 128*abs(floor((mousex+camx*editorScale)/(128*editorScale)))
            
            # interact with the control bar
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousey <= 40:
                cBar.interact(mousex)
            
            # interact with the tilePallet
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousex < tpal.xpos:
                tpal.interact(mousey)

            # scroll the tilePallet
            if event.type == SDL_MOUSEWHEEL and mouseOut and mousex < tpal.xpos:
                tpal.scrollY(-event.wheel.y*40)
            
            # remove tile
            if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_RIGHT and not mouseOut:
                level1.remove(floor((mousex+camx*editorScale)/(128*editorScale)),floor((mousey+camy*editorScale)/(128*editorScale)))
                
            # keep track if CTRL is pressed or not
            if event.type == SDL_KEYDOWN and (event.key.keysym.sym == SDLK_LCTRL or event.key.keysym.sym == SDLK_RCTRL):
                ctrlPress = True
            if event.type == SDL_KEYUP and (event.key.keysym.sym == SDLK_LCTRL or event.key.keysym.sym == SDLK_RCTRL):
                ctrlPress = False
            
           
            
            # zooming 
            if event.type == SDL_MOUSEWHEEL and ctrlPress:
                toolTipAlpha = 400
                # zoom once for every unit change in y
                for i in range(abs(event.wheel.y)):
                    if event.wheel.y > 0:   # zoom in if the change in y is positive
                        # change the scaling factor
                        editorScale *= 1.25
                        # recenter zooming around the center of the window
                        camx = ((winWidth.value/2+camx*editorScale*0.8)*1.25-winWidth.value/2)/editorScale
                        camy = ((winHeight.value/2+camy*editorScale*0.8)*1.25-winHeight.value/2)/editorScale
                    else:
                        # change the scaling factor
                        editorScale *= 0.8
                        # recenter zooming around the center of the window
                        camx = ((winWidth.value/2+camx*editorScale*1.25)*0.8-winWidth.value/2)/editorScale
                        camy = ((winHeight.value/2+camy*editorScale*1.25)*0.8-winHeight.value/2)/editorScale

        # scale the editor display based on the scaling factor
        SDL_RenderSetScale(mainRenderer,editorScale,editorScale)

        # draw the level itself
        level1.draw(-round(camx),-round(camy))

        # draw the cursor highlight
        SDL_SetRenderDrawColor(mainRenderer, 255,255,255,100)
        if not mouseOut:
            hlRect.x, hlRect.y, hlRect.w, hlRect.h = round(floor((mousex/editorScale+camx)/128)*128-camx), round(floor((mousey/editorScale+camy)/128)*128-camy), 128,128
            SDL_RenderFillRect(mainRenderer,hlRect)

        # reset scaling for the UI section
        SDL_RenderSetScale(mainRenderer,1,1)

        tpal.draw()
        cBar.draw()

        # draw the viewport scale in the corner
        SDL_SetRenderDrawColor(mainRenderer, 255,255,255,min(max(toolTipAlpha,1),200))
        quickRenderText(mainRenderer,ft_Mono16,"scale: "+str(round(editorScale*100))+"%",10,winHeight.value-20)

        # fade away the scaling text
        if toolTipAlpha > 0:
            toolTipAlpha -= 2

        # 10,winHeight.value-texth.value,textw.value,texth.value

        # set the render color to black for the background
        SDL_SetRenderDrawColor(mainRenderer,0,0,0,0)

        # draw the renderer to screen, and clear the buffer for the next frame
        SDL_RenderPresent(mainRenderer)
        SDL_RenderClear(mainRenderer)

        # wait 10ms before the next frame
        SDL_Delay(10)
    
    # if we exit the loop, destroy the window
    SDL_DestroyWindow(window)
    SDL_Quit()

if __name__ == '__main__':
    main()