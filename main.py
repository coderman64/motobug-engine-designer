import ctypes
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from tileset import *
from level import level
from math import *

from fonttools import *
from UI import *
from projects import *
from items import *
from sys import argv

def main():
    global lastMessage, motobugTex,triedArgs
    SDL_Init(SDL_INIT_VIDEO)
    TTF_Init()
    window = SDL_CreateWindow(b"Motobug Studio (beta 0.4)",
                                SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                640,480, SDL_WINDOW_SHOWN)
    if not window:
        print("WINDOW COULD NOT BE CREATED!")
        exit(1)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # set window icon
    icon = IMG_Load(b"icons/motobug.png")
    SDL_SetWindowIcon(window,icon)

    mainRenderer = SDL_CreateRenderer(window,-1,SDL_RENDERER_ACCELERATED)
    motobugTex = SDL_CreateTextureFromSurface(mainRenderer,icon)

    SDL_SetRenderDrawBlendMode(mainRenderer,SDL_BLENDMODE_BLEND)
    triedArgs = False
    openLoop(window,mainRenderer)

def openLoop(window,mainRenderer):
    global motobugTex, triedArgs
    SDL_RestoreWindow(window)
    SDL_SetWindowResizable(window,SDL_FALSE)
    SDL_SetWindowSize(window,640,480)
    SDL_SetWindowPosition(window,SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED)
    SDL_SetWindowBordered(window,SDL_FALSE)

    inOpenLoop = True
    ft_Mono24 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",24)
    ft_Mono18 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",18)

    # pre-render the text
    SDL_SetRenderDrawColor(mainRenderer,255,255,255,255)

    texts = [
        preRenderTextCenter(mainRenderer,ft_Mono24,"Welcome to Motobug Studio (beta 0.4)!",320,20),
        preRenderTextCenter(mainRenderer,ft_Mono18,"New Project",320,210),
        preRenderTextCenter(mainRenderer,ft_Mono18,"Load Project",320,240),
        preRenderTextCenter(mainRenderer,ft_Mono18,"Quit",320,270)
    ]

    mainProject = project()
    tiles = tileSet(mainRenderer,mainProject)
    #tiles.loadTexFromFile("projects/CrystalGeyser/tiles.txt")
    mainProject.levels = [level(mainRenderer,tiles)]
    mainProject.tilesets = [tiles]

    mousex,mousey = 0,0
    windowdrag = False
    windowdragstart = [0,0]
    currentTicks = SDL_GetTicks()

    while inOpenLoop:
        currentTicks = SDL_GetTicks()
        event = SDL_Event()
        while(SDL_PollEvent(ctypes.byref(event))):
            if(event.type == SDL_QUIT or (event.type == SDL_KEYUP and event.key.keysym.sym == SDLK_ESCAPE)):
                # close the program
                SDL_DestroyWindow(window)
                SDL_Quit()
                exit()
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT:
                if mousey > 200 and mousey < 280 and (mousey-200)%30 < 20:
                    index = floor((mousey-200)/30)
                    if index == 0:
                        success = mainProject.newWithDialog(mainRenderer)
                        if success == 0:
                            inOpenLoop = False
                    elif index == 1:
                        success = mainProject.openWithDialog(mainRenderer)
                        if success == 0:
                            inOpenLoop = False
                    elif index == 2:
                        SDL_DestroyWindow(window)
                        SDL_Quit()
                        exit()
                else:
                    windowdrag = True
                    windowdragstart = [mousex,mousey]
            if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_LEFT:
                windowdrag = False
            if event.type == SDL_MOUSEMOTION:
                # record the newest mouse position
                mousex, mousey = event.motion.x, event.motion.y
                if windowdrag:
                    winPosx, winPosy = ctypes.c_int(), ctypes.c_int()
                    SDL_GetWindowPosition(window,winPosx,winPosy)
                    SDL_SetWindowPosition(window,winPosx.value+(mousex-windowdragstart[0]),winPosy.value+(mousey-windowdragstart[1]))

        if mousey > 200 and mousey < 280 and (mousey-200)%30 < 20:

            SDL_SetRenderDrawColor(mainRenderer, 255,255,255,100)
            uiRect = SDL_Rect()
            uiRect.x, uiRect.y, uiRect.w, uiRect.h = 0,floor((mousey-200)/30)*30+200,640,20
            SDL_RenderFillRect(mainRenderer,uiRect)

        if len(argv) > 1 and argv[1].endswith(".mbproj") and not triedArgs:
            success = mainProject.openWithDialog(mainRenderer,argv[1])
            if success == 0:
                inOpenLoop = False
            triedArgs = True

        renderTextCenter(mainRenderer,ft_Mono24,"Welcome to Motobug Studio (beta 0.4)!",320,150,texts[0])
        renderTextCenter(mainRenderer,ft_Mono18,"New Project",320,210,texts[1])
        renderTextCenter(mainRenderer,ft_Mono18,"Load Project",320,240,texts[2])
        renderTextCenter(mainRenderer,ft_Mono18,"Quit",320,270,texts[3])

        rt = SDL_Rect()
        rt.x,rt.y,rt.w,rt.h = 320-64,0,128,128
        SDL_RenderCopy(mainRenderer,motobugTex,None,rt)

        # draw the renderer to screen, and clear the buffer for the next frame
        SDL_RenderPresent(mainRenderer)

        # set the render color to black for the background
        SDL_SetRenderDrawColor(mainRenderer,0,0,0,0)
        SDL_RenderClear(mainRenderer)

        # wait 10ms before the next frame
        SDL_Delay(10-min(9,max(round(SDL_GetTicks()-currentTicks),0)))

    SDL_SetWindowResizable(window,SDL_TRUE)
    SDL_SetWindowSize(window,1280,720)
    SDL_SetWindowPosition(window,SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED)
    SDL_SetWindowBordered(window,SDL_TRUE)

    editor(window,mainRenderer,mainProject)

def editor(window,mainRenderer,mainProject):
    global lastMessage, toolTipAlpha, itemMode

    lastMessage = "Welcome to Motobug Studo (beta 0.4)"
    oldMessage = lastMessage

    tiles = mainProject.levels[0].tileSet
    
    tpal = tilePallet(mainRenderer,tiles)
    lpal = layerPallet(mainRenderer)
    ipal = itemPallet(mainRenderer,mainProject.itemList)

    itemMode = False

    def exportGame():
        global lastMessage
        if mainProject.export():
            lastMessage = "project exported to %s" % mainProject.exportPath
        else:
            lastMessage = "export canceled"
    def exportAndPlay():
        global lastMessage
        if mainProject.runProject():
            lastMessage = "Running!"
        else:
            lastMessage = "export canceled"
    def saveProject():
        global lastMessage, toolTipAlpha
        mainProject.save()
        toolTipAlpha = 400
        lastMessage = "project saved."
        cBar.hitButton(4)
    def toggleItemMode():
        global itemMode
        itemMode = not itemMode
        temp = tpal.open
        tpal.open = ipal.open
        ipal.open = temp
        cBar.toggleHighlight(6)

    # set up the control bar
    cBar = controlBar(mainRenderer,
            [
                "icons/list.png",
                "icons/export.png",
                "icons/run.png",
                "icons/open.png",
                "icons/save.png",
                "icons/levelInfo.png",
                "icons/itemMode.png",
                "icons/layers.png"
            ],
            [
                lambda: tpal.toggle() if not itemMode else ipal.toggle(), 
                exportGame, 
                exportAndPlay,
                lambda: mainProject.openWithDialog(mainRenderer),
                saveProject,
                levelInfoOpener(mainProject),
                toggleItemMode,
                lpal.toggle
            ])

    editorScale = 1

    ft_Mono16 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",16)

    # should the program still be in the main loop?
    looping = True

    # keep track of editor conditions and controls
    camx, camy = 0,0
    mousex, mousey = 0,0
    mouseMoving = False
    ctrlPress = False
    toolTipAlpha = 400
    hlRect = SDL_Rect()
    hlRect.x, hlRect.y, hlRect.w, hlRect.h = 0,0,128,128
    selectedTile = 0

    # window width and height values (updated within loop)
    winWidth,winHeight = ctypes.c_int(640), ctypes.c_int(480)

    while looping:
        SDL_GetWindowSize(window,winWidth,winHeight)

        # define situations where the mouse isn't available to the main editor
        # space
        mouseOut = mousey <= 40 or mousex <= tpal.xpos or mousex >= winWidth.value-lpal.xpos or mousex <= ipal.xpos

        if lastMessage != oldMessage:
            toolTipAlpha = 400
            oldMessage = lastMessage

        if tpal.tileSet != mainProject.getCurrentLevel().tileSet:
            tpal.setTileset(mainProject.getCurrentLevel().tileSet)

        event = SDL_Event()

        currentTicks = SDL_GetTicks()
        while(SDL_PollEvent(ctypes.byref(event))):
            currentTicks = SDL_GetTicks()
            if(event.type == SDL_QUIT): # or (event.type == SDL_KEYUP and event.key.keysym.sym == SDLK_ESCAPE)):
                if CloseAndSave(mainProject):
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
                    mainProject.getCurrentLevel().camx -= event.motion.xrel / editorScale
                    mainProject.getCurrentLevel().camy -= event.motion.yrel / editorScale
                # record the newest mouse position
                mousex, mousey = event.motion.x, event.motion.y

            if not itemMode:
                # add tile
                if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_LEFT and not mouseOut:
                    # add currently selected tile
                    mainProject.getCurrentLevel().add(floor((mousex+camx*editorScale)/(128*editorScale)),floor((mousey+camy*editorScale)/(128*editorScale)),tpal.getSelectedTile(),lpal.getSelectedLayer())
                    
                    # if tile was added out of bounds to the left or the top of the level, 
                    # change the camera position accordingly
                    # if floor((mousey+camy*editorScale)/(128*editorScale)) < 0:
                    #     camy += 128*abs(floor((mousey+camy*editorScale)/(128*editorScale)))
                    # if floor((mousex+camx*editorScale)/(128*editorScale)) < 0:
                    #     camx += 128*abs(floor((mousex+camx*editorScale)/(128*editorScale)))
                
                # remove tile
                if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_RIGHT and not mouseOut:
                    mainProject.getCurrentLevel().remove(floor((mousex+camx*editorScale)/(128*editorScale)),floor((mousey+camy*editorScale)/(128*editorScale)),lpal.getSelectedLayer())
            
                if event.type == SDL_KEYUP and event.key.keysym.sym == SDLK_z and ctrlPress:
                    mainProject.getCurrentLevel().undo()
                elif event.type == SDL_KEYUP and event.key.keysym.sym == SDLK_y and ctrlPress:
                    mainProject.getCurrentLevel().redo()
            else:
                if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_RIGHT and not mouseOut:
                    mainProject.getCurrentLevel().openItemMenuAt(mousex,mousey,editorScale)
                if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_LEFT and not mouseOut and ipal.getSelectedItem() >= 0:
                    newItem = item(ipal.itemList.items[ipal.getSelectedItem()],round(mousex/editorScale+camx),round(mousey/editorScale+camy))

                    # if Ctrl is not pressed, snap the item to the grid
                    if not ctrlPress:
                        newItem.setParam('x',floor((mousex/editorScale+camx)/16)*16)
                        newItem.setParam('y',floor((mousey/editorScale+camy)/16)*16)
                    if newItem.getParam('w') <= 0 or newItem.getParam('h') <= 0:
                        newItem.setParam('w',32)
                        newItem.setParam('h',32)
                    mainProject.getCurrentLevel().addItem(newItem)

            # interact with the control bar
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousey <= 40:
                cBar.interact(mousex)
            
            # interact with the tilePallet
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousex < tpal.xpos:
                if mousex < tpal.xpos-32:
                    tpal.interact(mousey)
                else:
                    tpal.scrollbar(mousey)
            if event.type == SDL_MOUSEBUTTONUP and event.button.button == SDL_BUTTON_LEFT and tpal.scrolling:
                tpal.stopScroll()

            # scroll the tilePallet
            if event.type == SDL_MOUSEWHEEL and mouseOut and mousex < tpal.xpos:
                tpal.scrollY(-event.wheel.y*40)

            # interact with the item pallet
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousex < ipal.xpos:
                ipal.interact(mousey)

            #scroll the item pallet
            if event.type == SDL_MOUSEWHEEL and mousex < ipal.xpos:
                ipal.scrollY(-event.wheel.y*40)
            
            # interact with the layer pallet
            if event.type == SDL_MOUSEBUTTONDOWN and event.button.button == SDL_BUTTON_LEFT and mousex > winWidth.value-lpal.xpos:
                lpal.interact(mousey)

            # scroll the layer Pallet
            if event.type == SDL_MOUSEWHEEL and mouseOut and mousex > winWidth.value-lpal.xpos:
                lpal.scrollY(-event.wheel.y*40)
                

            # keep track if CTRL is pressed or not
            if event.type == SDL_KEYDOWN and (event.key.keysym.sym == SDLK_LCTRL or event.key.keysym.sym == SDLK_RCTRL):
                ctrlPress = True
            if event.type == SDL_KEYUP and (event.key.keysym.sym == SDLK_LCTRL or event.key.keysym.sym == SDLK_RCTRL):
                ctrlPress = False
            
            # save the project with Ctrl-S
            if event.type == SDL_KEYUP and ctrlPress and event.key.keysym.sym == SDLK_s:
               saveProject()
            
            # zooming 
            if event.type == SDL_MOUSEWHEEL and ctrlPress:
                # zoom once for every unit change in y
                for i in range(abs(event.wheel.y)):
                    camx = mainProject.getCurrentLevel().camx
                    camy = mainProject.getCurrentLevel().camy
                    if event.wheel.y > 0 and editorScale < 10:   # zoom in if the change in y is positive
                        # change the scaling factor
                        editorScale *= 1.25
                        # recenter zooming around the center of the window
                        mainProject.getCurrentLevel().camx = ((winWidth.value/2+camx*editorScale*0.8)*1.25-winWidth.value/2)/editorScale
                        mainProject.getCurrentLevel().camy = ((winHeight.value/2+camy*editorScale*0.8)*1.25-winHeight.value/2)/editorScale
                    elif event.wheel.y < 0 and editorScale > 0.01:
                        # change the scaling factor
                        editorScale *= 0.8
                        # recenter zooming around the center of the window
                        mainProject.getCurrentLevel().camx = ((winWidth.value/2+camx*editorScale*1.25)*0.8-winWidth.value/2)/editorScale
                        mainProject.getCurrentLevel().camy = ((winHeight.value/2+camy*editorScale*1.25)*0.8-winHeight.value/2)/editorScale
                    lastMessage = "scale: "+str(round(editorScale*100))+"%"

        if tpal.scrolling:
            tpal.scrollbar(mousey)


        camx = mainProject.getCurrentLevel().camx
        camy = mainProject.getCurrentLevel().camy

        # scale the editor display based on the scaling factor
        SDL_RenderSetScale(mainRenderer,editorScale,editorScale)

        # draw the level itself
        mainProject.getCurrentLevel().draw(lpal.getSelectedLayer())

        # draw the cursor highlight
        SDL_SetRenderDrawColor(mainRenderer, 255,255,255,100)
        if not mouseOut and not itemMode:
            hlRect.x, hlRect.y, hlRect.w, hlRect.h = round(floor((mousex/editorScale+camx)/128)*128-camx), round(floor((mousey/editorScale+camy)/128)*128-camy), 128,128
            SDL_RenderFillRect(mainRenderer,hlRect)
        if itemMode and editorScale >=1:
            for x in range(8):
                for y in range(8):
                    SDL_SetRenderDrawColor(mainRenderer, 255,255,255,max(round((4-abs(x-((mousex/editorScale+8)/16.)%1-3.5)-abs(y-((mousey/editorScale+8)/16.)%1-3.5))*255/4),0))
                    SDL_RenderDrawPoint(mainRenderer,x*16+round((mousex/editorScale-80)/16)*16+16-round(camx)%16,y*16+round((mousey/editorScale-80)/16)*16+16-round(camy)%16)

        # reset scaling for the UI section
        SDL_RenderSetScale(mainRenderer,1,1)

        tpal.draw()
        ipal.draw()
        lpal.draw()
        cBar.draw()

        # draw the last tooltip text in the corner
        SDL_SetRenderDrawColor(mainRenderer, 255,255,255,min(max(toolTipAlpha,1),200))
        quickRenderText(mainRenderer,ft_Mono16,lastMessage,round(max(tpal.xpos,ipal.xpos))+10,winHeight.value-20)

        # fade away the scaling text
        if toolTipAlpha > 0:
            toolTipAlpha -= 2
        elif lastMessage == oldMessage:
            lastMessage = ""

        # set the render color to black for the background
        SDL_SetRenderDrawColor(mainRenderer,0,0,0,0)

        # draw the renderer to screen, and clear the buffer for the next frame
        SDL_RenderPresent(mainRenderer)
        SDL_RenderClear(mainRenderer)

        # wait 10ms before the next frame
        SDL_Delay(10-min(9,max(round(SDL_GetTicks()-currentTicks),0)))
    
    openLoop(window,mainRenderer)

if __name__ == '__main__':
    main()
