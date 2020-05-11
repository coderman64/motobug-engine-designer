import os
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox as tkMessagebox

from sdl2 import *

from tileset import *
from level import *
from items import *

class project:
    """Object type that represents an open project"""
    def __init__(self):
        self.tilesets = []
        self.levels = []
        self.currentLevel = 0
        self.backupTilesets = []
        self.backupLevels = []
        self.itemList = itemlist()

        self.projPath = ""
    def loadProject(self,renderer,filename):
        """
        load the project from the given filename. Renderer should be an
        SDL_Renderer instance, and is used to import textures
        """
        # keep backups in case the import goes wrong
        self.backupTilesets = self.tilesets.copy()
        self.backupLevels = self.levels.copy()

        # clear out project
        self.tilesets.clear()
        self.levels.clear()

        # get the path for the pkg directory
        filepath = os.path.dirname(os.path.abspath(filename))
        itemDir = os.path.join(filepath,'pkg')

        #import all itemLists
        for i in os.listdir(itemDir):
            self.itemList.loadItemList(os.path.join(itemDir,i))

        # get the path for the levels directory
        levelDir = os.path.join(filepath,'levels')

        # import all levels and tilesets
        for i in os.listdir(levelDir):
            file = open(os.path.join(levelDir,i,"level1.mblvl")).read()
            tileSetName = file[file.find("TILESET: ")+9:file.find("\n",file.find("TILESET: "))]
            tileSetName = os.path.join(levelDir,i,tileSetName)
            tileSetIndex = -1
            if not tileSetName in [ts.path for ts in self.tilesets]:
                thisTileset = tileSet(renderer)
                thisTileset.loadTexFromFile(tileSetName)
                tileSetIndex = len(self.tilesets)
                self.tilesets.append(thisTileset)
            else:
                tileSetIndex = [ts.path for ts in self.tilesets].index(tileSetName)

            # parse the level map
            levelMap = file[file.find("TILEMAP:")+8:file.rfind("ITEMS:")]
            currentLevel = level(renderer,self.tilesets[tileSetIndex])
            currentLevel.project = self
            currentLevel.lvFilePath = os.path.join(levelDir,i,"level1.mblvl")
            currentLevel.parseFromString(levelMap)
            currentLevel.zone = file[file.find("NAME:")+5:file.find("\n",file.find("NAME:"))].strip()
            bkgIndex = file[file.find("BKGINDEX:")+9:file.find("\n",file.find("BKGINDEX:"))].strip()
            currentLevel.bkgIndex = int(bkgIndex) if bkgIndex.isdecimal() else 0
            currentLevel.musicPath = file[file.find("MUSIC:")+6:file.find("\n",file.find("MUSIC:"))].strip()
            

            # parse the item list
            itemList = file[file.find('\n',file.rfind("ITEMS")):]
            currentLevel.items.clear()
            currentLevel.parseItems(itemList,self.itemList)

            # reset level state to "unchanged"
            currentLevel.setUnchanged()

            self.levels.append(currentLevel)
        # set the currently selected level to 0
        self.currentLevel = 0
        self.projPath = filepath

        # upon successful completion, clear the backups (to save on memory)
        self.backupTilesets.clear()
        self.backupLevels.clear()
    def openWithDialog(self,renderer):
        """Load the project with a path from a Tk file dialog"""
        # create a root Tk window, and hide it (this is required for use of the tk file dialog)
        root = Tk()
        root.withdraw()

        # use tk to ask for the file from the dialog (will pause program)
        result = filedialog.askopenfilename(initialdir = "./projects", title = "Motobug Studio - Open Project",filetypes = (("Motobug Studio Project","*.mbproj"),("all files","*.*")))

        # load the project from the given filename
        try:
            self.loadProject(renderer,result)
            # destroy the invisible root window
            root.destroy()
            return 0

        except Exception as e:
            tkMessagebox.showerror("Error opening project","""Could not open the project file specified: %s\nEnsure that your project has the correct directory structure and formatting.\n\nERROR: \n%s""" % (result,str(e)))
            self.levels = self.backupLevels
            self.tilesets = self.backupTilesets
            # destroy the invisible root window
            root.destroy()
            return 1
    def save(self):
        """saves the current level to disk."""
        # if no project is open, don't save it (there is nothing to save)
        if self.projPath == "":
            return
        
        levelFile = "NAME: " + self.levels[0].zone +"\n"
        levelFile += "MUSIC: " + self.levels[0].musicPath +"\n"
        levelFile += "BKGINDEX: " + str(self.levels[0].bkgIndex) +"\n"

        # write tileset information
        levelFile += "TILESET: "
        levelFile += os.path.relpath(self.levels[0].tileSet.path,os.path.dirname(self.levels[0].lvFilePath))+"\n"

        # write tilemap information
        levelFile += "TILEMAP:\n"
        levelFile += self.levels[0].getLevelAsString()

        # add level items
        levelFile += "\nITEMS:\n"
        levelFile += "\n".join([i.getString() for i in self.levels[0].items])

        # write to the level file
        open(self.levels[0].lvFilePath,"w").write(levelFile)

        # reset level state to "unchanged"
        self.levels[0].setUnchanged()
    def getCurrentLevel(self):
        """ returns the currently selected level in the project"""
        return self.levels[self.currentLevel]
    def setCurrentLevel(self,index):
        """set the current level to the one at index index"""
        if index >= 0 and index < len(self.levels):
            self.currentLevel = index
            
