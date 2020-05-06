from tileset import tileSet
from sdl2 import *


class level:
    def __init__(self, renderer, _tileSet):
        self.rend = renderer
        self.tileSet = _tileSet
        self.lvMap = [[-1,-1,-1,-1,-1],[1,1,1,1,1],[0,0,0,0,0]]
        self.lvFilePath = ""
        self.zone = "TestZone"
    def draw(self,dx,dy):
        rt = SDL_Rect()
        rt.x, rt.y, rt.w, rt.h = dx,dy,128,128
        for row in self.lvMap:
            for col in row:
                if col >= 0 and col < self.tileSet.texCount:
                    SDL_RenderCopy(self.rend,self.tileSet.getTex(col),None,rt)
                rt.x += 128
            rt.x = dx
            rt.y += 128
    def add(self,x,y,id):
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
        self.lvMap[y][x] = id
    def remove(self,x,y):
        if x < 0 or y < 0 or y >= len(self.lvMap) or x >= len(self.lvMap[y]):
            return
        self.lvMap[y][x] = -1
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
        final = "level = [[],"
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
                    print(final[final.rfind("["):])

            final = final[:-1]+"],"
        final += """];backgroundMusic.src = "res/music/Dig3.ogg";backgroundMusic.play();cBack = 0;chunks = [];thisScript = document.createElement("script");thisScript.src = "levels/CGTiles.js";document.body.appendChild(thisScript);"""
        final += """levelName = ["%s","Zone","Act 0"]""" % self.zone
        fFile = open(name,'w')
        fFile.write(final)
    def clear(self):
        self.lvMap = [[]]
    def parseFromString(self,string):
        # clear the level map
        self.clear()

        # parse a new level map from the given string
        x,y = 0,0
        for line in string.splitlines():
            x = 0
            if "," in line:
                for i in line.split(","):
                    self.add(x,y,int(i))
                    x += 1
                y += 1
    def getLevelAsString(self):
        result = ""
        for row in self.lvMap:
            result += ",".join([str(i) for i in row])+"\n"
        return result

    def getSize(self):
        return (len(self.lvMap[0]),len(self.lvMap))