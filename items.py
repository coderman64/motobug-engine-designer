from defusedxml.ElementTree import parse
from tkinter import *
from tkinter.ttk import *
from sdl2 import *


class itemlist:
    def __init__(self):
        self.items = []
    def loadItemList(self,xmlFileName):
        xmlFile = parse(xmlFileName)
        xmlRoot = xmlFile.getroot()
        self.items.extend(xmlRoot.findall('item'))
    def clearItemList(self):
        self.items.clear()

class itemUI(Tk):
    def __init__(self,item):
        itemType = item.itemType
        Tk.__init__(self)
        self.resizable(False,False)
        self.overrideredirect(1)

        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        abs_coord_x = self.winfo_pointerx() - self.winfo_rootx()
        abs_coord_y = self.winfo_pointery() - self.winfo_rooty()
        self.geometry("+%s+%s" % (str(abs_coord_x),str(abs_coord_y)))



        label = Label(self,text=itemType.find('name').text)
        label.pack()
        for i in itemType.find('parameters'):
            label = Label(self,text=i.find('name').text)
            label.pack()
            paramType = i.find('type').text.strip()
            paramName = i.find('name').text
            if paramType.startswith('float'):
                print(str(item.params[paramName]))
                box = Entry(self,validate='key',validatecommand=(self.register(lambda e: str.isnumeric(e) ),'%S'))
                box.insert(0,str(item.params[paramName]))
                box.pack()
            elif paramType.startswith('string-path'):
                box = Entry(self)
                box.insert(0,item.params[paramName])
                box.config(state='readonly')
                box.pack()
                dialButton = Button(self,text='Browse...')
                dialButton.pack()
            else:
                print(str(item.params[paramName]))
                box = Entry(self)
                box.insert(0,item.params[paramName])
                box.pack()
        self.focus_force()
        self.bind("<FocusOut>",self.lostFocus)
        
        self.mainloop()
    def lostFocus(self,e):
        print(self.focus_get())
        if not self.focus_get() in self.winfo_children() and self.focus_get() != self:
            self.destroy()

class item:
    def __init__(self,itemType,x,y):
        self.itemType = itemType
        self.params = {}
        for i in itemType.find('parameters'):
            paramType = i.find('type').text.strip()
            if paramType.startswith('position-x'):
                self.params[i.find('name').text] = x
            elif paramType.startswith('position-y'):
                self.params[i.find('name').text] = y
            elif paramType.startswith('float') or paramType.startswith('position') or paramType.startswith('size'):
                self.params[i.find('name').text] = 100
            else:
                self.params[i.find('name').text] = ""
        print(self.params)
    def draw(self,renderer,dx,dy):
        for i in self.itemType.find('display'):
            if i.tag == 'rect':
                colors = i.find('color').text[1:-1].split(',')
                SDL_SetRenderDrawColor(renderer,int(colors[0]),int(colors[1]),int(colors[2]),int(colors[3]) if len(colors) > 3 else 255)
                rect = SDL_Rect()
                rect.x, rect.y = self.getPos()
                rect.x, rect.y = rect.x+dx,rect.y+dy
                rect.w, rect.h = self.getSize()
                SDL_RenderFillRect(renderer,rect)
    def getPos(self):
        pos = [None,None]
        for i in self.itemType.find('parameters'):
            paramType = i.find('type').text.strip()
            if paramType.startswith('position-x'):
                pos[0] = int(self.params[i.find('name').text])
            if paramType.startswith('position-y'):
                pos[1] = int(self.params[i.find('name').text])
        return pos
    def getSize(self):
        size = [None,None]
        for i in self.itemType.find('parameters'):
            paramType = i.find('type').text.strip()
            if paramType.startswith('size-w'):
                size[0] = int(self.params[i.find('name').text])
            if paramType.startswith('size-h'):
                size[1] = int(self.params[i.find('name').text])
        return size
    def setParam(self,param,value):
        if param in self.params.keys():
            self.params[param] = value
    def getParam(self,param):
        if param in self.params.keys():
            return self.params[param]
        else:
            return None
    def getString(self):
        string = self.itemType.find('format').text.strip()
        for i in self.params.keys():
            string = string.replace(i,str(self.params[i]))
        return string

if __name__ == "__main__":
    IL = itemlist()
    IL.loadItemList("projects/Project1/pkg/default.mbitm")
    itemUI(item(IL.items[1],100,200))