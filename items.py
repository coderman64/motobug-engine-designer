from defusedxml.ElementTree import parse
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from ctypes import c_int
from math import floor
import os
from parseMath import parseMath

from fonttools import quickRenderText

def isFloat(string):
    """returns true if the given string can be converted to a float"""
    return all(c in "0123456789." for c in string)

class itemlist:
    """stores definitions for how items should be managed by Motobug Studio"""
    def __init__(self):
        self.items = []
    def loadItemList(self,xmlFileName):
        xmlFile = parse(xmlFileName)
        xmlRoot = xmlFile.getroot()
        self.items.extend(xmlRoot.findall('item'))
    def clearItemList(self):
        self.items.clear()

class item:
    """represents one item in a Motobug level"""
    def __init__(self,itemType,x,y):
        self.itemType = itemType
        self.params = {}
        self.destroy = False
        for i in itemType.find('parameters'):
            paramType = i.find('type').text.strip()
            if paramType.startswith('position-x'):
                self.params[i.find('name').text] = x
            elif paramType.startswith('position-y'):
                self.params[i.find('name').text] = y
            elif paramType.startswith('float') or paramType.startswith('position') or paramType.startswith('size'):
                self.params[i.find('name').text] = float(i.get('default')) if i.get("default") and isFloat(i.get("default")) else 32
            elif paramType.startswith('int'):
                self.params[i.find('name').text] = int(i.get('default')) if i.get("default") and i.get("default").isdigit() else 1
            else:
                self.params[i.find('name').text] = i.get('default') if i.get('default') else ""
    def draw(self,renderer,dx,dy):
        """Draw the item as defined by its .mbitm configuration"""
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
        """
        Returns a list containing the x and y coordinates of the item. If not 
        available, returns (-1,-1)
        """
        pos = [None,None]
        try:
            for i in self.itemType.find('parameters'):
                paramType = i.find('type').text.strip()
                if paramType.startswith('position-x'):
                    pos[0] = round(float(self.params[i.find('name').text]))
                if paramType.startswith('position-y'):
                    pos[1] = round(float(self.params[i.find('name').text]))
        except:
            pos = [-1,-1]
        return pos
    
    def setPos(self,x,y):
        """
        Returns a list containing the x and y coordinates of the item. If not 
        available, returns (-1,-1)
        """
        for i in self.itemType.find('parameters'):
            paramType = i.find('type').text.strip()
            if paramType.startswith('position-x'):
                self.params[i.find('name').text] = x
            if paramType.startswith('position-y'):
                self.params[i.find('name').text] = y
    
    def getSize(self):
        """
        Returns a list containing the x and y coordinates of the item. If not 
        available, returns (16,16)
        """
        size = [None,None]
        try:
            for i in self.itemType.find('parameters'):
                paramType = i.find('type').text.strip()
                if paramType.startswith('size-w'):
                    size[0] = round(float(self.params[i.find('name').text]))
                if paramType.startswith('size-h'):
                    size[1] = round(float(self.params[i.find('name').text]))
        except:
            pos = [16,16]
        return size
    def setParam(self,param,value):
        """set a particular parameter (param) to a particular value (value)"""
        if param in self.params.keys():
            self.params[param] = value
    def getParam(self,param):
        """Returns the value of parameter param, or None, if it can't be found"""
        if param in self.params.keys():
            return self.params[param]
        else:
            return None
    def getString(self):
        """
        returns the string form of the function, as defined by "format" in
        the .mbitm file
        """
        string = self.itemType.find('format').text.strip()
        paramString = string[string.find('('):]
        string = string[:string.find('(')]
        for i in self.params.keys():
            paramString = paramString.replace(i,str(self.params[i]) if isFloat(str(self.params[i])) else '"'+str(self.params[i]).replace('"','\\"')+'"',1)
        return string+paramString
    def setDestroy(self):
        """set the item to be destroyed by its parent level"""
        self.destroy = True

class pathOpener:
    """
    a callback object to handle the "Browse..." button for items with path
    variables
    """
    def __init__(self,root,entryBox,initialdir):
        self.entrybox = entryBox
        self.initialdir = initialdir
        self.root = root
    def __call__(self,e=None):
        self.root.disableDestruction()
        path = filedialog.askopenfilename(initialdir = self.initialdir, title = "Motobug Studio - Open Path",filetypes = (("all files","*.*"),))
        self.entrybox.config(state=NORMAL)
        self.entrybox.delete(0,END)
        if path:
            self.entrybox.insert(0,os.path.relpath(path,self.initialdir).replace("\\","/"))
        else:
            self.entrybox.insert(0,"")
        self.entrybox.config(state="readonly")
        self.root.enableDestruction()

class itemUI(Tk):
    """A GUI box to edit an item's parameters"""
    def __init__(self,item,level):
        itemType = item.itemType
        self.level = level
        self.initialdir = level.project.projPath
        self.item = item
        Tk.__init__(self)
        self.resizable(False,False)
        # remove the window decoration of the context window in windows
        # this causes problems on linux. OSX is untested
        if sys.platform.startswith("win"):
            self.overrideredirect(1)

        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        abs_coord_x = self.winfo_pointerx() - self.winfo_rootx()
        abs_coord_y = self.winfo_pointery() - self.winfo_rooty()
        self.geometry("+%s+%s" % (str(abs_coord_x-5),str(abs_coord_y-5)))

        self.edits = {}
        self.paramTypes = {}

        label = Label(self,text=itemType.find('name').text)
        label.pack()
        for i in itemType.find('parameters'):
            label = Label(self,text=i.find('name').text)
            label.pack()
            paramType = i.find('type').text.strip()
            paramName = i.find('name').text
            self.paramTypes[paramName] = paramType
            if paramType.startswith('float') or paramType.startswith('position') or paramType.startswith('size'):
                box = Entry(self,validate='key',validatecommand=(self.register(lambda e: all(c in "0123456789.+-*/" for c in e) ),'%S'))
                box.insert(0,str(item.params[paramName]))
                box.pack()
                self.edits[paramName] = box
            elif paramType.startswith('int'):
                box = Entry(self,validate='key',validatecommand=(self.register(lambda e: all(c in "0123456789+-*" for c in e) ),'%S'))
                box.insert(0,str(item.params[paramName]))
                box.pack()
                self.edits[paramName] = box
            elif paramType.startswith('string-path'):
                box = Entry(self)
                box.insert(0,item.params[paramName])
                box.config(state='readonly')
                box.pack()
                self.edits[paramName] = box
                dialButton = Button(self,text='Browse...',command = pathOpener(self,box,self.initialdir))
                dialButton.pack()
            else:
                box = Entry(self)
                box.insert(0,item.params[paramName])
                box.pack()
                self.edits[paramName] = box
        self.bringFront = Button(self, text="Bring to front",command=self.bringToFront)
        self.bringFront.pack()
        self.sendBack = Button(self, text="Send to Back",command=self.sendToBack)
        self.sendBack.pack()
        self.destroyButton = Button(self,text = "Delete",command=self.setDestroy)
        self.destroyButton.pack()
        self.focus_force()
        self.bind("<FocusOut>",self.lostFocus)
        self.bind("<Return>",self.exitUI)
        self.destructable = True
        self.changed = False
        self.mainloop()
    def bringToFront(self):
        self.level.items = [i for i in self.level.items if i != self.item]+[self.item]
    def sendToBack(self):
        self.level.items = [self.item]+[i for i in self.level.items if i != self.item]
    def lostFocus(self,e=None):
        """internal callback"""
        if not self.focus_get() in self.winfo_children() and self.focus_get() != self and self.destructable:
            self.exitUI()
    def exitUI(self,e=None):
        """internal callback"""
        for i in self.edits.keys():
            if self.edits[i].get():
                if self.item.getParam(i) != str(self.edits[i].get()):
                    result = str(self.edits[i].get())
                    if self.paramTypes[i].startswith("position") or self.paramTypes[i].startswith("size") or self.paramTypes[i].startswith("float") or self.paramTypes[i].startswith("int"):
                        if not isFloat(result):
                            print(result)
                            try:
                                result = parseMath(result)
                            except:
                                print("failed to evaluate string %s" % result)
                    self.item.setParam(i,result)
                    self.changed = True
        self.destroy()
    def setDestroy(self,e=None):
        """set this ItemUI's associated item to be destroyed"""
        self.item.setDestroy()
        self.destroy()
    def disableDestruction(self):
        """stop the window from destroying itself when not in focus"""
        self.destructable = False
    def enableDestruction(self):
        """enable the window destroying itself when not in focus"""
        self.destructable = True
    def hadChanged(self):
        """returns true if the UI has changed any values in the item"""
        return self.changed

class itemPallet:
    """
    A GUI element that allows a user to select between adding different items
    or editing only
    """
    def __init__(self,rend,il):
        """
        create an item pallet object
        rend: SDL_Renderer responsible for drawing the pallet
        il: itemList containing relevant item definitions
        """
        self.itemList = il
        self.open = False
        self.xpos = 0
        self.scroll = 0
        self.rend = rend
        self.ft_Mono16 = TTF_OpenFont(b"fonts/RobotoMono-Regular.ttf",16)
        self.selected = -1
        self.level = None
    def draw(self):
        """draw the item pallet"""
        if self.open:
            self.xpos += (200-self.xpos) * 0.1
        else:
            self.xpos += (-self.xpos) * 0.1

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
            for i in range(len(self.itemList.items)+1):
                # highlight selected tile
                if i-1 == self.selected:
                    rect.x, rect.y, rect.w, rect.h = round(self.xpos-185),i*150+45-self.scroll,138,138
                    SDL_SetRenderDrawColor(self.rend,255,255,255,100)
                    SDL_RenderFillRect(self.rend,rect)
                # draw tile preview
                rect.x, rect.y, rect.w, rect.h = round(self.xpos-180),i*150+50-self.scroll,128,128
                if i >= 1:
                    for x in self.itemList.items[i-1].find('display'):
                        if x.tag == 'rect':
                            colors = x.find('color').text[1:-1].split(',')
                            SDL_SetRenderDrawColor(self.rend,int(colors[0]),int(colors[1]),int(colors[2]),int(colors[3]) if len(colors) > 3 else 255)
                            SDL_RenderFillRect(self.rend,rect)
                    #SDL_RenderCopy(self.rend,self.tileSet.getTex(i),None,rect)
                    SDL_SetRenderDrawColor(self.rend,255,255,255,255)

                    # draw the file name for the tile
                    quickRenderText(self.rend,self.ft_Mono16,self.itemList.items[i-1].find('name').text.strip(),rect.x,rect.y+128)
                else:
                    #SDL_RenderCopy(self.rend,self.tileSet.getTex(i),None,rect)
                    SDL_SetRenderDrawColor(self.rend,255,255,255,255)

                    # draw the file name for the tile
                    quickRenderText(self.rend,self.ft_Mono16,"Edit Only",rect.x,rect.y+128)
    
    def interact(self,mouseY):
        """
        Call this function if the mouse clicks the pallet at y-position mouseY
        """
        index = floor((mouseY+self.scroll-50)/150)-1
        if index >= -1 and index < len(self.itemList.items):
            self.selected = index
        #i*150+50-self.scroll
        
    def toggle(self):
        """Toggle if the pallet is open or not"""
        self.open = not self.open

    def scrollY(self,yrel):
        """
        scroll vertically by yrel pixels, 
        clamping at the ends of the scrolling area.
        """
        # get the display size
        dispw, disph = c_int(), c_int()
        SDL_GetRendererOutputSize(self.rend,dispw,disph)

        # scroll vertically
        self.scroll += yrel

        # limit scrolling
        if self.scroll <= 0:
            self.scroll = 0
        if self.scroll+disph.value >= (len(self.itemList.items)+1)*150+178:
            self.scroll = (len(self.itemList.items)+1)*150+178-disph.value
            
    def getSelectedItem(self):
        """
        returns the index of the item that is selected, or -1 if it is 
        edit-only mode
        """
        return self.selected
        


if __name__ == "__main__":
    IL = itemlist()
    IL.loadItemList("projects/Project1/pkg/default.mbitm")
    itemUI(item(IL.items[1],100,200))
