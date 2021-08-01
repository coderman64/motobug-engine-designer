import os
import shutil
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox as tkMessagebox
from copy_tree_overwrite import copytree
from webbrowser import open as web_open

from sdl2 import *

from tileset import *
from level import *
from items import *
from scanImage import startScan

def CloseAndSave(project):
    """
    if the project isn't saved, open a dialog to ask the user if they want it
    to be. Save the level if yes, don't save the level on no. Returns True in
    all cases except when cancel is pressed, or the dialog is closed with the 
    "x" button
    """
    if not project.getCurrentLevel().unchanged:
        root = Tk()
        root.withdraw()
        shouldSave = tkMessagebox.askyesnocancel("Close and Save Project","The project has been changed. Do you want to save before exiting?")
        if shouldSave:
            project.save()
        root.destroy()
        return shouldSave in [True,False]
    else:
        return True

class exportPathOpener:
    """Callback object to open a directory using a file dialog"""
    def __init__(self,root,entryBox,initialdir):
        self.entrybox = entryBox
        self.initialdir = initialdir
        self.root = root
    def __call__(self,e=None):
        path = filedialog.askdirectory(initialdir = self.initialdir, title = "Motobug Studio - Export")
        if not path:
            tkMessagebox.showinfo("Motobug Studio - Info","No path selected")
            return
        if not "index.html" in os.listdir(path) or not "engine" in os.listdir(path):
            result = tkMessagebox.askyesno("Motobug Studio - Engine not Found","We could not find Motobug Engine in the given directory. Are you sure you want to export to %s" % path)
            if result == False:
                return
        self.entrybox.config(state=NORMAL)
        self.entrybox.delete(0,END)
        if path:
            self.entrybox.insert(0,path)
        else:
            self.entrybox.insert(0,"")
        self.entrybox.config(state="readonly")

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
        self.projFile = ""
        self.exportPath = ""

        self.skipMenus = False
        self.firstLevel = 0
    def newProject(self,renderer,filename):
        """create a new project at path filename"""
        dirname = filename
        if "." in os.path.basename(filename):
            dirname = filename[:filename.rfind(".")]

        os.makedirs(os.path.join(dirname,"levels"))
        os.makedirs(os.path.join(dirname,"levels","Zone1"))
        os.makedirs(os.path.join(dirname,"pkg"))
        os.makedirs(os.path.join(dirname,"res"))

        defaultProject = "CURRENTLVL: 0\nFIRSTLVL: 0\nSKIPMENUS: FALSE\nEXPORTPATH: "
        defaultFile = open(os.path.join(dirname,"project.mbproj"),"w")
        defaultFile.write(defaultProject)
        defaultFile.close()

        defaultLevel = "NAME: Default | Zone | Act 1\nMUSIC:\nBKGINDEX:0\nTILESET:tiles.mbtiles"
        defaultLevel += "\nTILEMAP:\n-1,-1,-1\n1,1,1"
        defaultLevel += "\nITEMS:"
        defaultFile = open(os.path.join(dirname,"levels/Zone1/level1.mblvl"),"w")
        defaultFile.write(defaultLevel)
        defaultFile.close()

        defaultSourceFile = open("res/defaultTileset/tiles.mbtiles")
        defaultFile = open(os.path.join(dirname,"levels","Zone1","tiles.mbtiles"),"w")
        defaultFile.write(defaultSourceFile.read())
        defaultSourceFile.close()
        defaultFile.close()

        copytree("res/defaultTileset",os.path.join(dirname,"res","Level","defaultTileset"))
        shutil.copyfile("res/default.mbitm",os.path.join(dirname,"pkg","default.mbitm"))
        os.remove(os.path.join(dirname,"res","Level","defaultTileset","tiles.mbtiles"))
        
        self.loadProject(renderer,os.path.join(dirname,"project.mbproj"))

    def newWithDialog(self,renderer):
        """Create a new project with a path from a Tk file dialog"""
        # create a root Tk window, and hide it (this is required for use of the tk file dialog)
        root = Tk()
        root.withdraw()

        # use tk to ask for the file from the dialog (will pause program)
        result = filedialog.asksaveasfilename(initialdir = "./projects", title = "Motobug Studio - New Project",filetypes = (("directory","*/"),("all files","*.*")))

        if result == "":
            tkMessagebox.showerror("Error creating project","""Cannot create project with empty path (file dialog cancelled).""")
            return 1

        self.backupLevels = self.levels
        self.backupTilesets = self.tilesets
        self.backupProjPath = self.projPath
        # create the project from the given filename
        try:
            self.newProject(renderer,result)
            # destroy the invisible root window
            root.destroy()
            return 0

        except Exception as e:
            tkMessagebox.showerror("Error creating project","""Could not create the specified project: %s\nCheck the project path.\n\nERROR: \n%s""" % (result,str(e)))
            self.levels = self.backupLevels
            self.tilesets = self.backupTilesets
            self.projPath = self.backupProjPath
            # destroy the invisible root window
            root.destroy()
            return 1
    
    def reloadProject(self,renderer):
        if CloseAndSave(self):
            self.loadProject(renderer,self.projFile)

    def loadProject(self,renderer,filename):
        """
        load the project from the given filename. Renderer should be an
        SDL_Renderer instance, and is used to import textures
        """
        # keep backups in case the import goes wrong
        self.backupTilesets = self.tilesets.copy()
        self.backupLevels = self.levels.copy()
        self.backupProjPath = self.projPath

        # clear out project
        self.tilesets.clear()
        self.levels.clear()


        # load basic project settings from the .mbproj file
        mbproj = open(filename).read().splitlines()
        for i in mbproj:
            print(i[11:].strip(),i[11:].strip().isdecimal())
            if i.startswith("CURRENTLVL:") and i[11:].strip().isdigit():
                self.currentLevel = int(i[11:].strip())
                print("deci: %d" % self.currentLevel)
            if i.startswith("EXPORTPATH:"):
                self.exportPath = i[11:].strip()
            if i.startswith("FIRSTLVL:") and i[9:].strip().isdigit():
                self.firstLevel = int(i[9:].strip())
            if i.startswith("SKIPMENUS:") and i[10:].strip() in ["TRUE","FALSE"]:
                self.skipMenus = True if i[10:].strip() == "TRUE" else False


        # get the path for the pkg directory
        self.projPath = os.path.dirname(os.path.abspath(filename))
        itemDir = os.path.join(self.projPath,'pkg')

        #import all itemLists
        for i in os.listdir(itemDir):
            self.itemList.loadItemList(os.path.join(itemDir,i))

        # get the path for the levels directory
        levelDir = os.path.join(self.projPath,'levels')

        # import all levels and tilesets
        for i in os.listdir(levelDir):
            file = open(os.path.join(levelDir,i,"level1.mblvl")).read()
            
            tileSetName = file[file.find("TILESET:")+8:file.find("\n",file.find("TILESET:"))].strip()
            tileSetName = os.path.join(levelDir,i,tileSetName)
            tileSetIndex = -1
            
            if not tileSetName in [ts.path for ts in self.tilesets]:
                thisTileset = tileSet(renderer,self)
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

        self.projFile = filename

        # upon successful completion, clear the backups (to save on memory)
        self.backupTilesets.clear()
        self.backupLevels.clear()
    def openWithDialog(self,renderer,result=None):
        """Load the project with a path from a Tk file dialog"""
        # create a root Tk window, and hide it (this is required for use of the tk file dialog)
        root = Tk()
        root.withdraw()

        if result == None:
            # use tk to ask for the file from the dialog (will pause program)
            result = filedialog.askopenfilename(initialdir = "./projects", \
                title = "Motobug Studio - Open Project",filetypes = (("Motobug Studio Project","*.mbproj"),("all files","*.*")))

        if result == "":
            tkMessagebox.showerror("Error opening project","""Cannot load project from empty path (file dialog cancelled).""")
            return 1

        # load the project from the given filename
        try:
            self.loadProject(renderer,result)
            # destroy the invisible root window
            root.destroy()
            return 0

        except Exception as e:
            tkMessagebox.showerror("Error opening project","""Could not open the project file specified: %s\
                Ensure that your project has the correct directory structure and formatting.\n\nERROR: \n%s""" % (result,str(e)))
            self.levels = self.backupLevels
            self.tilesets = self.backupTilesets
            self.projPath = self.backupProjPath
            # destroy the invisible root window
            root.destroy()
            return 1
    def save(self):
        """saves the current level to disk."""
        # if no project is open, don't save it (there is nothing to save)
        if self.projPath == "":
            return
        
        # save project informaition
        projectFile = "CURRENTLVL: " + str(self.currentLevel) + "\n"
        projectFile += "FIRSTLVL: " + str(self.firstLevel) + "\n"
        projectFile += "SKIPMENUS: " + ("TRUE" if self.skipMenus else "FALSE") + "\n"
        projectFile += "EXPORTPATH: " + str(self.exportPath) + "\n"

        open(self.projFile,'w').write(projectFile)

        for i in self.levels:
            if not i.unchanged:
                i.save()
    def export(self):
        """export the project using a dialog"""
        self.exportCanceled = False
        root = Tk()
        self.tkRoot = root
        root.resizable(False,False)
        root.title("Motobug Studio - Export Project")

        Label(root,text="Directory of Motobug project to export to:").grid(row=0,column=0,columnspan=2)
        exportPathVar = StringVar()
        exportPathBox = Entry(root,textvariable=exportPathVar)
        exportPathBox.insert(0,self.exportPath)
        exportPathBox.config(state="readonly")
        exportPathBox.grid(row=1,column=0,sticky="ew")

        exportBrowseButton = Button(root,text="Browse...",command=exportPathOpener(root,exportPathBox,self.exportPath if self.exportPath else self.projPath))
        exportBrowseButton.grid(row=1,column=1,sticky="ew")
        
        finalExportButton = Button(root,text="Export",command=root.destroy)
        finalExportButton.grid(row=2,column=0,columnspan=2,sticky="e")

        root.protocol("WM_DELETE_WINDOW",self.export_canceled)
        root.mainloop()

        if self.exportCanceled:
            return False
        
        self.exportPath = exportPathVar.get()

        if self.exportPath.strip() == "":
            return False

        # export levels 
        levelExportPath = os.path.join(self.exportPath,"levels")
        levelList = []
        levelIndex = 0
        for i in self.levels:
            levelList.append("level_"+str(levelIndex))
            i.export(os.path.join(levelExportPath,"level_"+str(levelIndex)+".js"),"levels/tileset"+str(self.tilesets.index(i.tileSet))+".js" )
            levelIndex += 1
        
        # export list of levels to level.js
        levelEngineFile = open(os.path.join(self.exportPath,"engine/level.js")).read()
        finalLevelEngineFile = ""
        for i in levelEngineFile.splitlines():
            if i.startswith("var levelsList"):
                finalLevelEngineFile += "var levelsList = "+str(levelList)+";\n"
            else:
                finalLevelEngineFile += i+"\n"
        open(os.path.join(self.exportPath,"engine/level.js"),'w').write(finalLevelEngineFile)

        # export basic configuration
        if not os.path.exists(os.path.join(self.exportPath,"engine/config_bkp.js")):
            # backup default config
            copytree(os.path.join(self.exportPath,"engine/config.js"),\
                os.path.join(self.exportPath,"engine/config_bkp.js"))
        configFile = "var configuration = {"
        configFile += "classicAngles: false,"
        configFile += "mBlurDefault: true,"
        configFile += "skipMenus: "+ ("true" if self.skipMenus else "false") + ","
        configFile += "startLevel: " + str(self.firstLevel)
        configFile += "};"
        open(os.path.join(self.exportPath,"engine/config.js"),"w").write(configFile)

        # export item code
        codeFile = ""
        for i in self.itemList.items:
            if i.find("code") != None:
                codeFile += i.find("code").text
        print("CODE:\n\n"+codeFile)
        open(os.path.join(self.exportPath,"res/user_items.js"),"w").write(codeFile)
            

        # export tile scanner configuration
        tileScanText = ""
        for i in range(len(self.tilesets)):
            tileScanText += open(self.tilesets[i].path).read()
            tileScanText += "\n%"+os.path.join(self.exportPath,"levels","tileset"+str(i)+".js")+"\n"
        temp = os.getcwd()
        os.chdir(self.projPath)
        open("toScan.txt","w").write(tileScanText)

        # run tile scanner
        startScan()
        os.chdir(temp)
        
        copytree(os.path.join(self.projPath,"res"),os.path.join(self.exportPath,"res"))
        self.save()

        return True
    def runProject(self):
        """similar to export, but runs the project after exporting"""
        result = self.export()
        if result:
            web_open(os.path.join(self.exportPath,"index.html"))
        return result
    def export_canceled(self,*args):
        self.exportCanceled = True
        self.tkRoot.destroy()
    def getCurrentLevel(self):
        """ returns the currently selected level in the project"""
        return self.levels[self.currentLevel]
    def setCurrentLevel(self,index):
        """set the current level to the one at index index"""
        if index >= 0 and index < len(self.levels):
            self.currentLevel = index
            
