from tileset import tileSet
from sdl2 import *
from items import *


class level:
    def __init__(self, renderer, _tileSet):
        self.rend = renderer
        self.tileSet = _tileSet
        self.lvMap = [[-1,-1,-1,-1,-1],[1,1,1,1,1],[0,0,0,0,0]]
        self.lvFilePath = ""
        self.zone = "TestZone"
        self.items = []
        self.undoList = []
        self.redoList = []
        self.project = None
    def draw(self,dx,dy,selLayer=-1):
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
    def add(self,x,y,id,layer=-1,undo=True):
        if len(self.lvMap) == 0:
            self.lvMap = [[]]
        while len(self.lvMap) <= y: 
            self.lvMap.append([-1 for i in self.lvMap[0]])
        while y < 0:
            self.lvMap.insert(0,[-1 for i in self.lvMap[0]])
            y += 1
        while x < 0:
            for i in self.lvMap:
                i.insert(0,-1)
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
    def remove(self,x,y,layer=-1,undo=True):
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
    def cleanExterior(self):
        if not (len(self.lvMap) == 1 and len(self.lvMap[0]) == 1):
            for row in self.lvMap:
                rowEmpty = True
                for tile in row:
                    if tile != -1:
                        rowEmpty = False
                if rowEmpty:
                    self.lvMap.remove(row)
                else:
                    break
            for row in self.lvMap[::-1]:
                rowEmpty = True
                for tile in row:
                    if tile != -1:
                        rowEmpty = False
                if rowEmpty:
                    self.lvMap.remove(row)
                else:
                    break
            if not len(self.lvMap) == 0:
                colEmpty = True
                while colEmpty:
                    for i in self.lvMap:
                        if i[0] != -1:
                            colEmpty = False
                    if colEmpty:
                        for i in self.lvMap:
                            i.pop(0)
    def export(self,name):
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
        final += """];backgroundMusic.src = "res/music/Dig3.ogg";backgroundMusic.play();cBack = 0;chunks = [];thisScript = document.createElement("script");thisScript.src = "levels/CGTiles.js";document.body.appendChild(thisScript);"""
        final += """levelName = ["%s","Zone","Act 0"]""" % self.zone
        fFile = open(name,'w')
        fFile.write(final)
    def clear(self):
        self.lvMap = [[]]
        self.undoList = []
        self.redoList = []
    def undo(self):
        if len(self.undoList) > 0:
            step = self.undoList.pop()
            print(step)
            if type(self.lvMap[step[1]][step[0]]) is int:
                self.redoList.append([step[0],step[1],self.lvMap[step[1]][step[0]]])
            else:
                self.redoList.append([step[0],step[1],self.lvMap[step[1]][step[0]].copy()])
            self.add(step[0],step[1],step[2],-1,False)
            self.cleanExterior()
    def redo(self):
        if len(self.redoList) > 0:
            step = self.redoList.pop()
            print(step)
            if type(self.lvMap[step[1]][step[0]]) is int:
                self.undoList.append([step[0],step[1],self.lvMap[step[1]][step[0]]])
            else:
                self.undoList.append([step[0],step[1],self.lvMap[step[1]][step[0]].copy()])
            self.add(step[0],step[1],step[2],-1,False)
            self.cleanExterior()
    def parseFromString(self,string):
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


    def getLevelAsString(self):
        result = ""
        for row in self.lvMap:
            result += ",".join([str(i) for i in row])+"\n"
        return result

    def getSize(self):
        return (len(self.lvMap[0]),len(self.lvMap))