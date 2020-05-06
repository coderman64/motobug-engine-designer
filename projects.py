import os
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox as tkMessagebox

from sdl2 import *

from tileset import *
from level import *

class project:
    def __init__(self):
        self.tilesets = []
        self.levels = []
        self.currentLevel = 0
        self.backupTilesets = []
        self.backupLevels = []

        self.projPath = ""
    def loadProject(self,renderer,filename):
        # keep backups in case the import goes wrong
        self.backupTilesets = self.tilesets.copy()
        self.backupLevels = self.levels.copy()

        # clear out project
        self.tilesets.clear()
        self.levels.clear()

        # get the path for the levels directory
        filepath = os.path.dirname(os.path.abspath(filename))
        self.projPath = filepath
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


            levelMap = file[file.find("TILEMAP:")+8:file.find("ITEMS",file.find("TILEMAP: "))]
            currentLevel = level(renderer,self.tilesets[tileSetIndex])
            currentLevel.lvFilePath = os.path.join(levelDir,i,"level1.mblvl")
            currentLevel.parseFromString(levelMap)
            self.levels.append(currentLevel)
            print(currentLevel.getLevelAsString())
        # set the currently selected level to 0
        self.currentLevel = 0

        # upon successful completion, clear the backups (to save on memory)
        self.backupTilesets.clear()
        self.backupLevels.clear()
    def openWithDialog(self,renderer):
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
        if self.projPath == "":
            return
        levelFile = "TILESET: "
        levelFile += os.path.relpath(self.levels[0].tileSet.path,os.path.dirname(self.levels[0].lvFilePath))+"\n"
        levelFile += "TILEMAP:\n"
        levelFile += self.levels[0].getLevelAsString()
        levelFile += "\nITEMS:\n"
        print(levelFile)
        open(self.levels[0].lvFilePath,"w").write(levelFile)
    def getCurrentLevel(self):
        return self.levels[self.currentLevel]
            
