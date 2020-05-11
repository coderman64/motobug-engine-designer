from tileset import tileSet
from sdl2 import *
from items import *


class level:
    """Stores one stage"""
    def __init__(self, renderer, _tileSet):
        self.rend = renderer
        self.tileSet = _tileSet
        self.lvMap = [[-1,-1,-1,-1,-1],[1,1,1,1,1],[0,0,0,0,0]]
        self.lvFilePath = ""
        self.zone = "TestZone | Zone | Act1"
        self.musicPath = ""
        self.bkgIndex = 0
        self.items = []
        self.undoList = []
        self.redoList = []
        self.project = None
        self.unchanged = True
    def draw(self,dx,dy,selLayer=-1):
        """
        draw the level to the renderer\n
        \tdx, dy: the position of the level compared to the upper left corner
        \t\tof the screen
        \tselLayer (optional): the layer which should be drawn as selected
        \t\t(-1 for all layers)
        """
        rt = SDL_Rect()
        rt.x, rt.y, rt.w, rt.h = dx,dy,128,128
        for row in self.lvMap:
            for col in row:
                if type(col) is int and col >= 0 and col < self.tileSet.texCount:
                    SDL_RenderCopy(self.rend,self.tileSet.getTex(col),None,rt)
                elif type(col) is list:
                    for layer in range(len(col))[::-1]:
                        if col[layer] != -1:
                            if selLayer != layer and selLayer != -1:
                                SDL_SetTextureAlphaMod(self.tileSet.getTex(col[layer]),100)
                                SDL_SetTextureColorMod(self.tileSet.getTex(col[layer]),255,100,100)
                            SDL_RenderCopy(self.rend,self.tileSet.getTex(col[layer]),None,rt)
                            SDL_SetTextureAlphaMod(self.tileSet.getTex(col[layer]),255)
                            SDL_SetTextureColorMod(self.tileSet.getTex(col[layer]),255,255,255)
                rt.x += 128
            rt.x = dx
            rt.y += 128
        for i in self.items:
            i.draw(self.rend,dx,dy)
            if i.destroy:
                self.items.remove(i)
                self.unchanged = False
    def add(self,x,y,id,layer=-1,undo=True):
        """
        Add the tile with index "id" at the given position\n
        \tx, y: the x and y cordinates of the tile (in tiles)
        \tid: the index of the tile in the tileset
        \tlayer (optional): the layer of the tile (-1 for all layers)
        \tundo (optional): set to false if you don't want to save this action
        \t\tin the level's undo history
        """
        if len(self.lvMap) == 0:
            self.lvMap = [[]]
        while len(self.lvMap) <= y: 
            self.lvMap.append([-1 for i in self.lvMap[0]])
        while y < 0:
            self.lvMap.insert(0,[-1 for i in self.lvMap[0]])
            self.moveAllItemsBy(0,128)
            y += 1
        while x < 0:
            for i in self.lvMap:
                i.insert(0,-1)
            self.moveAllItemsBy(128,0)
            x += 1
        while x >= len(self.lvMap[y]):
            for i in self.lvMap: 
                i.append(-1)
        if undo and type(self.lvMap[y][x]) is int:
            self.undoList.append([x,y,self.lvMap[y][x]])
            self.redoList = []
        elif undo:
            self.undoList.append([x,y,self.lvMap[y][x].copy()])
            self.redoList = []
        if layer < 0:
            self.lvMap[y][x] = id
        else:
            if not type(self.lvMap[y][x]) is list:
                self.lvMap[y][x] = [self.lvMap[y][x] for i in range(layer)]
            while len(self.lvMap[y][x]) <= min(2,layer):
                self.lvMap[y][x].append(-1)
            self.lvMap[y][x][layer] = id
        self.unchanged = False

    def remove(self,x,y,layer=-1,undo=True):
        """
        remove the tile at the given position\n
        \tx, y: the x and y cordinates of the tile (in tiles)
        \tlayer (optional): the layer of the tile (-1 for all layers)
        \tundo (optional): set to false if you don't want to save this action
        \t\tin the level's undo history
        """
        if x < 0 or y < 0 or y >= len(self.lvMap) or x >= len(self.lvMap[y]):
            return
        if undo and type(self.lvMap[y][x]) is int:
            self.undoList.append([x,y,self.lvMap[y][x]])
            self.redoList = []
        elif undo:
            self.undoList.append([x,y,self.lvMap[y][x].copy()])
            self.redoList = []
        if layer < 0:
            self.lvMap[y][x] = -1
        elif type(self.lvMap[y][x]) is list and len(self.lvMap[y][x]) > layer:
            self.lvMap[y][x][layer] = -1
            for i in range(len(self.lvMap[y][x]))[::-1]:
                if not self.lvMap[y][x][i] == -1:
                    break
                self.lvMap[y][x].pop(i)
            if len(self.lvMap[y][x]) == 0:
                self.lvMap[y][x] = -1
            while len(self.lvMap[y][x]) <= 2:
                self.lvMap[y][x].append(-1)
        self.cleanExterior()
        self.unchanged = False

    def cleanExterior(self):
        """remove empty rows and columns around the outside of the level's
        map"""
        if not (len(self.lvMap) == 1 and len(self.lvMap[0]) == 1):
            rowindex = 0
            while rowindex < len(self.lvMap):
                rowEmpty = True
                row = self.lvMap[rowindex]
                for tile in row:
                    if not tile == -1:
                        rowEmpty = False
                if rowEmpty:
                    self.lvMap.pop(rowindex)
                    self.moveAllItemsBy(0,-128)
                    rowindex -= 1
                else:
                    break
                rowindex += 1
            rowindex = len(self.lvMap)-1
            while rowindex >= 0:
                rowEmpty = True
                row = self.lvMap[rowindex]
                for tile in row:
                    if tile != -1:
                        rowEmpty = False
                if rowEmpty:
                    self.lvMap.pop(rowindex)
                else:
                    break
                rowindex -= 1
            if not len(self.lvMap) == 0:
                colEmpty = True
                while colEmpty:
                    for i in self.lvMap:
                        if i[0] != -1:
                            colEmpty = False
                    if colEmpty:
                        for i in self.lvMap:
                            i.pop(0)
                        self.moveAllItemsBy(-128,0)
                                
    def moveAllItemsBy(self,dx,dy):
        """move all items in the level by a certain amount (in pixels)"""
        for i in self.items:
            pos = i.getPos()
            i.setPos(pos[0]+dx,pos[1]+dy)
    def export(self,name):
        """
        export the level to the file at "name" in a Motobug-engine-compatible 
        .js format
        """
        level = self.lvMap
        final = "level = [["+",".join(["new "+i.getString() for i in self.items])+"],"
        for y in range(len(level)):
            final += "["
            for x in range(len(level[y])):
                if type(level[y][x]) == int:
                    final += str(level[y][x])+","
                else:
                    final += "["
                    for i in level[y][x]:
                        final += str(i)+","
                    final = final[:-1]+"],"

            final = final[:-1]+"],"
        final += "];backgroundMusic.src = \""+ self.musicPath+"\";backgroundMusic.play();cBack = "+str(self.bkgIndex)+";chunks = [];thisScript = document.createElement(\"script\");thisScript.src = \"levels/CGTiles.js\";document.body.appendChild(thisScript);"
        final += """levelName = ["%s","%s","%s"]""" % tuple([i.strip() for i in self.zone.split('|')]+["" for i in range(3-len(self.zone.split('|')))])
        fFile = open(name,'w')
        fFile.write(final)
    def clear(self):
        """Clear the level's map and undo history"""
        self.lvMap = [[]]
        self.undoList = []
        self.redoList = []
    def undo(self):
        """undo the previously completed tile action (UNSTABLE!)"""
        if len(self.undoList) > 0:
            step = self.undoList.pop()
            if type(self.lvMap[step[1]][step[0]]) is int:
                self.redoList.append([step[0],step[1],self.lvMap[step[1]][step[0]]])
            else:
                self.redoList.append([step[0],step[1],self.lvMap[step[1]][step[0]].copy()])
            self.add(step[0],step[1],step[2],-1,False)
            self.cleanExterior()
    def redo(self):
        """redo the last undoed tile action (UNSTABLE!)"""
        if len(self.redoList) > 0:
            step = self.redoList.pop()
            if type(self.lvMap[step[1]][step[0]]) is int:
                self.undoList.append([step[0],step[1],self.lvMap[step[1]][step[0]]])
            else:
                self.undoList.append([step[0],step[1],self.lvMap[step[1]][step[0]].copy()])
            self.add(step[0],step[1],step[2],-1,False)
            self.cleanExterior()
    def parseFromString(self,string):
        """
        Parse the tile layout from the given CSV-styled string. Tiles in the 
        same place on different layers are represented using Python list style
        (i.e. [1,0]).
        """
        # clear the level map
        self.clear()

        # parse a new level map from the given string
        x,y = 0,0
        for line in string.splitlines():
            x = 0
            if "," in line:
                layer = -1
                for i in line.split(","):
                    if i.strip().startswith("[") and i.strip().endswith("]"):
                        self.add(x,y,[int(i[1:-1]),-1],-1)
                    elif i.strip().startswith("["):
                        self.add(x,y,int(i[1:]),0)
                        layer = 1
                    elif i.strip().endswith("]"):
                        self.add(x,y,int(i[:-1]),layer)
                        layer = -1
                    else:
                        self.add(x,y,int(i),layer)
                        if layer >= 0:
                            layer += 1
                    if layer < 0:
                        x += 1
                y += 1
        self.undoList = []
        self.redoList = []
    def parseItems(self,itemString,_itemlist):
        """
        parses the given item string with the given itemList. The each item
        should follow the formats given by the .mbitm files, and should be 
        seperated using a newline (\\n) character
        """
        itemList = itemString.splitlines()
        for i in itemList:
            if not ("(" in i and ")" in i):
                continue
            else:
                itemType = i[:i.find("(")]
                itemParams = i[i.find("(")+1:i.find(")")].split(",")
                for i in _itemlist.items:
                    if i.find('format').text.strip().startswith(itemType):
                        newItem = item(i,0,0)
                        pIndex = 0
                        for p in i.find('parameters'):
                            newItem.setParam(p.find('name').text,itemParams[pIndex][1:-1].replace('\\"','"') if itemParams[pIndex].startswith('"') else itemParams[pIndex])
                            pIndex += 1
                        self.items.append(newItem)
                        break
    def setUnchanged(self):
        """set state to "unchanged." Should only happen when the project is saved"""
        self.unchanged = True

    def getLevelAsString(self):
        """
        returns a CSV-style string for the tile layout. Tiles in the 
        same place on different layers are represented using Python list style
        (i.e. [1,0]).
        """
        result = ""
        for row in self.lvMap:
            result += ",".join([str(i) for i in row])+"\n"
        return result

    def getSize(self):
        """gets the level width and height in tiles"""
        return (len(self.lvMap[0]),len(self.lvMap))
    
    def addItem(self,item):
        """add the given item to the level"""
        self.unchanged = False
        self.items.append(item)
    
    def openItemMenuAt(self,x,y,dx,dy,editorScale):
        """Opens an itemUI at the given x and y position. Additional values are
        required to detect which item to open a UI for:\n
        \tdx,dy: camera pan position
        \teditorScale: the scale of the view
        """
        # loop through all items (in reverse, since later items appear on top)
        for i in self.items[::-1]:
            pos = SDL_Point()
            pos.x, pos.y = x,y
            rect = SDL_Rect()
            rect.x, rect.y = i.getPos()
            rect.x, rect.y = round((rect.x-dx)*editorScale),round((rect.y-dy)*editorScale)
            rect.w, rect.h = [round(x*editorScale) for x in i.getSize()]
            # if the location is on the item, open the itemUI for that item
            if SDL_PointInRect(pos,rect) == SDL_TRUE:
                iui = itemUI(i,self.project.projPath)
                if iui.hadChanged():
                    self.unchanged = False
                break

class musicPathOpener:
    """Callback object to open a music/audio file using a file dialog"""
    def __init__(self,root,entryBox,initialdir):
        self.entrybox = entryBox
        self.initialdir = initialdir
        self.root = root
    def __call__(self,e=None):
        path = filedialog.askopenfilename(initialdir = self.initialdir, title = "Motobug Studio - Open Path",filetypes = (("Vorbis audio","*.ogg"),("WAV audio","*.wav"),("MP3 audio","*.mp3"),("all files","*.*")))
        self.entrybox.config(state=NORMAL)
        self.entrybox.delete(0,END)
        if path:
            self.entrybox.insert(0,os.path.relpath(path,self.initialdir).replace("\\","/"))
        else:
            self.entrybox.insert(0,"")
        self.entrybox.config(state="readonly")

class levelInfo(Tk):
    """A UI to view and edit basic level information"""
    def __init__(self,project):
        self.project = project
        Tk.__init__(self)
        self.title("Motobug Studio - Level Info")
        self.resizable(False,False)

        self.levelStr = StringVar()
        self.levelBox = Combobox(self,state='readonly',textvar=self.levelStr,values=[i.zone for i in project.levels])
        self.levelBox.grid(row=0,column=0,columnspan=3,sticky="ew")
        self.levelBox.current(self.project.currentLevel)

        Label(self,text="Zone Name (seperate sections with '|'):").grid(row=1,column=0)
        self.nameString = StringVar()
        self.nameBox = Entry(self,textvariable=self.nameString)
        self.nameBox.insert(0,self.project.getCurrentLevel().zone)
        self.nameBox.grid(row=1,column=1,columnspan=2,sticky="ew")

        Label(self,text="Music Path:").grid(row=2,column=0)
        self.musicVar = StringVar()
        self.musicBox = Entry(self,textvariable=self.musicVar)
        self.musicBox.insert(0,self.project.getCurrentLevel().musicPath)
        self.musicBox.config(state="readonly")
        self.musicBox.grid(row=2,column=1)
        self.musicBrowse = Button(self,text="Browse...",command=musicPathOpener(self,self.musicBox,self.project.projPath))
        self.musicBrowse.grid(row=2,column=2)
        
        Label(self,text="Background Index:").grid(row=3,column=0)
        self.backVar = StringVar()
        self.backBox = Entry(self,validate='key',validatecommand=(self.register(lambda e: e.isdigit() ),'%S'),textvariable=self.backVar)
        self.backBox.insert(0,self.project.getCurrentLevel().bkgIndex)
        self.backBox.grid(row=3,column=1,columnspan=2,sticky="ew")

        # player properties will be implimented later... for now, just change it
        # within motobug itself

        # self.playerFrame = LabelFrame(self,text="Player Properties")
        # self.playerFrame.grid(row=4,column=0,columnspan=3,sticky="nesw")
        # self.playerFrame.columnconfigure(1,weight=1)

        # Label(self.playerFrame,text="Player X Position: ").grid(row=0,column=0)
        # self.playerX = Entry(self.playerFrame)
        # self.playerX.grid(row=0,column=1,sticky="ew")

        # Label(self.playerFrame,text="Player Y Position: ").grid(row=1,column=0)
        # self.playerY = Entry(self.playerFrame)
        # self.playerY.grid(row=1,column=1,sticky="ew")

        self.levelStr.trace('w',self.levelChanged)
        self.bind('<Destroy>',self.setLevelInfo)

        self.mainloop()
    def levelChanged(self,*args):
        """internal event"""
        self.setLevelInfo()
        self.project.setCurrentLevel(self.levelBox.current())
        self.nameBox.delete(0,END)
        self.nameBox.insert(0,self.project.getCurrentLevel().zone)

        self.musicBox.config(state=NORMAL)
        self.musicBox.delete(0,END)
        self.musicBox.insert(0,self.project.getCurrentLevel().musicPath)
        self.musicBox.config(state='readonly')

        self.backBox.delete(0,END)
        self.backBox.insert(0,str(self.project.getCurrentLevel().bkgIndex))
    def setLevelInfo(self,*args):
        """internal event"""
        self.project.getCurrentLevel().zone = self.nameString.get()
        self.project.getCurrentLevel().musicPath = self.musicVar.get()
        self.project.getCurrentLevel().bkgIndex = int(self.backVar.get())

class levelInfoOpener:
    """
    Callback object that opens the level info dialog for the given
    project
    """
    def __init__(self,project):
        self.project = project
    def __call__(self,*args):
        levelInfo(self.project)