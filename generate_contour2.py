#Graphics libraries
import matplotlib
# just to make it more universal it is good to turn off graphical mode
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
from mpl_toolkits.axisartist.axislines import Subplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
#math libraries
import numpy as np
#file manipulation libraries
import os
import zipfile
#multiprocessing library
from multiprocessing import Process, Manager, cpu_count
from copy import deepcopy as copy
import subprocess as sp
import processingFunctions

### Setup for output type ###

# if results require fast calculation or frame-by-frame analysis
# set to False - it will activate multiprocessing of data and image
# export.
direct = True

# Set as needed.
proc_num = 1
visualisation_column="pressure"

#zip file name
zipfilenames = None#'contours/plots.zip'

#Searching for necessary folders

xlims=[0.08, 0.22]
ylims=[-0.04, 0.04]
#xlims=[0.18, 0.22]
#ylims=[-0.03, 0.01]

class maskSettings:
    def __init__(self):
        self.files = []
        self.xarray = []
        self.yarray = []
        self.xcol = 0
        self.ycol = 1
        self.removeFlag = False
        self.color = "#8e8e8e"
        self.name = "mask"
        self.filename=""
    
    class fileSettings:
        def __init__(self):
            self.filename = ""
            self.reverseColumn = [None]
            self.separator = " "
            self.labelSeparator = " "
            self.xcol = 0
            self.ycol = 1

    def menu(self, args):
        intext = ""
        while(intext!="q"):
            if(len(args)<1):
                intext = input("mask > ")
            else:
                intext = " ".join(args)
                print(f"mask > {args[0]}")
            args = [var for var in intext.split(" ") if var]
            if(intext == 'q'):
                break
            if(intext == ""):
                self.printAvailable()
                continue
            if(args[0] == "filename"):
                self.setFilename(args[1:])
            if(args[0] == "name"):
                self.setMaskName(args[1:])
            if(args[0] == "color"):
                self.setColor(args[1:])
            if(args[0] == "print"):
                self.printFiles(args=args[1:])
            if(args[0] == "del"):
                self.removeFileFromList(args[1:])
            if(args[0]=="cols"):
                self.setColumns(args[1:])
            if(args[0]=="rev"):
                self.setReverse(args[1:])
            if(args[0]=="separators"):
                self.setSeparators(args[1:])
            if(args[0]=="settings"):
                self.printSettings()
            if(args[0]=="load"):
                self.loadFile(args[1:])
            args = []
            intext = ""
    
    def printAvailable(self):
        print("filename\tadd file to list of mask contours")
        print("name\t\tset mask name")
        print("color\t\tset mask colour")
        print("print\t\tprint all listed files")
        print("del\t\tremove file from list")
        print("cols\t\tset X and Y columns of mask file")
        print("rev\t\treverse direction of axis")
        print("separators\tspecify data and label separators in file")
        print("settings\tlist settings for all files")
        print("load\t\taccept changes and load listed files")
        print("remove\t\tremove mask")
        print("q\t\treturn to main menu")

    def flagMaskForDeletion(self):
        self.deleteFlag = True
    
    def setMaskName(self, args):
        if(len(args)<1):
            intext = input(f"Please specify name for current mask:\n[{self.name}]\nmask name > ")
        else:
            intext = args[0]
            print(f"Please specify name for current mask:\n[{self.name}]\nmask name > {args[0]}")
        self.name = intext
        print(f"New name: {self.name}")
    
    def setColor(self, args):
        if(len(args)<1):
            intext = input(f"Please specify color for current mask:\n[{self.color}]\nmask color > ")
        else:
            intext = args[0]
            print(f"Please specify name for current mask:\n[{self.color}]\nmask color > {args[0]}")
        self.color = intext
        print(f"New color: {self.color}")
    
    def printSettings(self):
        print(f"Name: {self.name}")
        print(f"Colour: {self.color}")
        print(f"Number of files listed: {len(self.files)}")
        print(f"Current number of points loaded: {len(self.xarray)}")
        print("File settings:")
        for i, file in enumerate(self.files):
            print(f"File index: ({i})")
            print(f"\tFile name:\t\t{file.filename}")
            print(f"\tColumn reversed:\t{file.reverseColumn}")
            print(f"\tData separator:\t\t\"{file.separator}\"")
            print(f"\tLabel separator:\t\"{file.labelSeparator}\"")
            print(f"\tX-coordinate column:\t{file.xcol}")
            print(f"\tY-coordinate column:\t{file.ycol}")
    
    def setFilename(self, args=[]):
        if(len(args)<1):
            intext = input(f"Please provide mask file name:\nmask filename > ")
        else:
            print(f"Please provide mask file name:\nmask filename > ")
            intext = args[0]
        if(intext=='q'):
            return
        if(os.path.isfile(intext)):
            file = self.fileSettings()
            file.filename = intext
            file.reverseColumn = [None]
            file.xcol = self.xcol
            file.ycol = self.ycol
            file.separator = " "
            file.labelSeparator = " "
            print(f"File added to list:\n\"{intext}\"")
            self.files.append(file)
            return
        if(os.path.isdir(intext)):
            localFilelist = os.listdir(intext)
            for filename in localFilelist:
                file = self.fileSettings()
                file.filename = intext+"/"+filename
                file.xcol = self.xcol
                file.ycol = self.ycol
                file.reverseColumn = [None]
                file.separator = " "
                file.labelSeparator = " "
                self.files.append(file)
            print(f"Directory added to list:\n\"{intext}\"\nFiles added:")
            for i, filename in enumerate(os.listdir(intext)):
                print(f"{i}:\t{filename}")
            return
        print("Could not find file or directory.")
        if(len(args)==0):
            self.setFilename()
        
    def printFiles(self, mark=[], args=[]):
        if(len(self.files)==0):
            print("No files currently on list.")
            return
        print("Files on list:")
        for i in range(len(self.files)):
            if(len(mark)>i):
                print(f"{i}:\t{self.files[i].filename}\t{mark[i]}")
            else:
                print(f"{i}:\t{self.files[i].filename}")

    def removeFileFromList(self, args=[]):
        if(len(self.files)==0):
            print("No files to delete from list.")
            return
        print("Select file index to remove from list ('q' to cancel):")
        self.printFiles()
        if(len(args)<1):
            intext = input("mask remove > ")
        else:
            print(f"mask remove > {args[0]}")
            intext = args[0]
        if(intext=='q'):
            print("Cancelling module")
            return
        try:
            intext = int(intext)
        except:
            print("Could not load index. Please provide a file number.")
        if(intext>=len(self.files) or intext<0):
            print("Index out of range. Please select correct file number.")
        self.files.pop(intext)
        if(len(args)>0):
            args = args[:-1]
        self.removeFileFromList(args)
    
    def setColumns(self, args = []):
        print("Please select file index ('q' to cancel):")
        self.printFiles(mark=[(file.xcol, file.ycol) for file in self.files])
        if(len(args)<1):
            intext = input("mask setcol > ")
        else:
            intext = args[0]
            print(f"mask setcol > {args[0]}")
        if(intext=='q'):
            return
        try:
            intext = int(intext)
        except:
            print("Could not read file index. Cancelling.")
            return
        fileIndex = intext
        if(len(args)<2):
            intext = input(f"Please provide mask X-coordinate column:\n[{self.xcol}]\nmask X-coordinate > ")
        else:
            print(f"Please provide mask X-coordinate column:\n[{self.xcol}]\nmask X-coordinate > {args[1]}")
            intext = args[1]
        if(intext!=""):
            if(intext[-1]=="!"):
                try:
                    self.files[fileIndex].xcol = int(intext[:-1])
                except:
                    print("Could not read collumn index. Falling back to default value.")
            else:
                self.files[fileIndex].xcol = intext
        if(len(args)<3):
            intext = input(f"Please provide mask Y-coordinate column:\n[{self.ycol}]\nmask Y-coordinate > ")
        else:
            print(f"Please provide mask Y-coordinate column:\n[{self.ycol}]\nmask Y-coordinate > {args[2]}")
            intext = args[2]
        if(intext!=""):
            if(intext[-1]=="!"):
                try:
                    self.files[fileIndex].ycol = int(intext[:-1])
                except:
                    print("Could not read collumn index. Falling back to default value.")
            else:
                self.files[fileIndex].ycol = intext
        if(len(args)>0):
            args = args[:-3]
        self.setColumns(args)
    
    def setReverse(self, args=[]):
        print("Select file to reverse column ('q' to cancel).")
        self.printFiles([var.reverseColumn for var in self.files if var.reverseColumn[0]!=None])
        if(len(args)<1):
            intext = input(f"mask reverse > ")
        else:
            print(f"mask reverse > {args[0]}")
            intext = args[0]
        if(intext=='q'):
            return
        try:
            intext = int(intext)
        except:
            print("Could not load index. Please provide a file number.")
        if(intext>=len(self.filename) or intext<0):
            print("Index out of range. Please select correct file number.")
        if(len(args)<2):
            intext2 = input("Please specify axis (X, Y):\nmask reverse axis > ")
        else:
            print(f"Please specify axis (X, Y):\nmask reverse axis > {args[1]}")
            intext2 = args[1]
        if("X" in intext2 or "x" in intext2):
            if(not "X" in self.files[intext].reverseColumn):
                self.files[intext].reverseColumn = ["X"]+self.files[intext].reverseColumn
            else:
                self.files[intext].reverseColumn.pop(self.files[intext].reverseColumn.index("X"))
                print(f"X column of file {intext} will not be reversed.")
        if("Y" in intext2 or "y" in intext2):
            if(not "Y" in self.files[intext].reverseColumn):
                self.files[intext].reverseColumn = ["Y"]+self.files[intext].reverseColumn
            else:
                self.files[intext].reverseColumn.pop(self.files[intext].reverseColumn.index("Y"))
                print(f"Y column of file {intext} will not be reversed.")
        if(len(args)>0):
            args = args[:-2]
        self.setReverse(args)
    
    def fixWhiteSigns(self, text):
        if(text=='\\t'):
            text = '\t'
        if(text=="space"):
            text = " "
        return text

    def setSeparators(self, args=[]):
        print("Select file to set separators ('q' to cancel).")
        self.printFiles([(var.separator, var.labelSeparator) for var in self.files])
        if(len(args)<1):
            intext = input(f"mask separators > ")
        else:
            print(f"mask separators > {args[0]}")
            intext = args[0]
        if(intext=='q'):
            return
        try:
            intext = int(intext)
        except:
            print("Could not load index. Please provide a file number.")
        if(intext>=len(self.filename) or intext<0):
            print("Index out of range. Please select correct file number.")
        if(len(args)<2):
            intext2 = input("Please specify data separator:\nmask separators data > ")
        else:
            print(f"Please specify data separator:\nmask separators data > {args[1]}")
            intext2 = args[1]
        self.files[intext].separator = self.fixWhiteSigns(intext2)
        if(len(args)<3):
            intext2 = input("Please specify label separator:\nmask separators label > ")
        else:
            print(f"Please specify label separator:\nmask separators label > {args[2]}")
            intext2 = args[2]
        self.files[intext].labelSeparator = self.fixWhiteSigns(intext2)
        if(len(args)>1):
            args = args[:-3]
        self.setSeparators(args)
    
    def getFileContents(self, file):
        print(f"Opening file {file.filename}")
        ffile = open(file.filename, "r")
        if(ffile==None):
            print("Could not open file.")
            return [[], []]
        legend = []
        contents = [[], []]
        for line in ffile:
            ll = [var for var in line.split(file.separator) if var]
            if(len(ll)<=1):
                continue
            try:
                float(ll[0])
            except:
                legend = [var for var in line.split(file.labelSeparator) if var]
                continue
            if(isinstance(file.xcol, str)):
                try:
                    file.xcol = legend.index(file.xcol)
                except:
                    print(f"Could not find legend for {file.xcol}. Falling back to 0.")
                    file.xcol = 0
            if(isinstance(file.ycol, str)):
                try:
                    file.ycol = legend.index(file.xcol)
                except:
                    print(f"Could not find legend for {file.ycol}. Falling back to 1.")
                    file.ycol = 1
            contents[0].append(float(ll[file.xcol]))
            contents[1].append(float(ll[file.ycol]))
        ffile.close()
        print("File closed.")
        return contents
    
    def loadFile(self, args):
        print("Loading mask contours.")
        for i, file in enumerate(self.files):
            contents = self.getFileContents(file)
            print(f"Loaded {len(contents[0])} points from file {i}.")
            if("X" in file.reverseColumn):
                contents = [contents[0][::-1], contents[1]]
            if("Y" in file.reverseColumn):
                contents = [contents[0], contents[1][::-1]]
            self.xarray += contents[0]
            self.yarray += contents[1]
        print("Done.")

#class for settings management
class graphSettings:
    def __init__(self):
        self.alias = "."
        self.XCoord = 1
        self.YCoord = 2
        self.number_of_threads = cpu_count()
        self.width = 7
        self.xlims = [-1., 1.]
        self.ylims = [-1., 1.]
        self.height = width*np.abs(((ylims[1]-ylims[0])/(xlims[1]-xlims[0])))*2
        self.maxfiles = None
        self.numbering_method="flow-time"
        self.draw_airfoil = False
        self.airfoil_chord = 1.
        self.airfoil_thickness = 0.12
        self.airfoil_aoa = 0.
        self.n18x = []
        self.n18y = []
        self.masks = []
        self.zipfilenames = None
        self.maxfiles = None
        self.visualisation_column=3
        self.levels = None
        self.dt = 0.001
        self.xaxis_scale = 1.
        self.yaxis_scale = 1.
        self.xlabel = "X Coordinate [m]"
        self.ylabel = "Y Coordinate [m]"
        self.processing_method = processingFunctions.plainProcess
        self.probes = [[], []]
        self.probe_coords = []
        self.probe_avg = []
        self.probe_amp = []
        self.h = 0.001
        self.number_of_threads = 12
        self.start_time = 0
        self.end_time = 0
        self.videoname = "output.mp4"
        self.horizontal_resolution = 1280
        self.preserveRAM = False

#Miscancellous
def rotationMatrix(a):
    '''
    Function generating rotation matrix around Z axis for a
    specified rotation angle.
    Prerequisites:
    -> numpy
    Arguments:
    -> a (float) - rotation angle in radians
    Results:
    -> rtmt (ndarray) - rotation matrix
    '''
    rtmt = [[np.cos(a), -np.sin(a), 0],
            [np.sin(a), np.cos(a), 0],
            [0, 0, 1]]
    return np.asarray(rtmt)

def generateNACA(thickness, chord, aoa, xoffset=0, points=50):
    '''
    Function generating an array of points in accordance to NACA
    symmetrical airfoils definition. Airfoil generated consists of
    top and bottom side, and is generated clockwise from leading
    edge.
    Prerequisites:
    -> numpy
    Arguments:
    -> thickness (float) - airfoil thickness as chord %
    -> chord (float) - airfoil chord
    -> aoa (float) - airfoil's angle of attack
    -> points (int) - number of points on ONE side (total num. of
                      points = 2*points)
    Results:
    -> x (ndarray) - array of X coordinates
    -> y (ndarray) - array of Y coordinates
    '''
    rt = rotationMatrix(aoa)
    x = np.linspace(0, 1, num=points)
    xr = np.linspace(0, 1, num=points)
    x = x**2*chord
    xr = xr**2*chord
    y = np.zeros(points)
    yr = np.zeros(points)
    y = 5*thickness*(0.2969*np.sqrt((x/chord))-
                            0.1260*(x/chord)-
                            0.3516*(x/chord)**2+
                            0.2843*(x/chord)**3-
                            0.1015*(x/chord)**4)
    for i in range(points):
        rv = np.matmul(rt, np.asarray([[x[i]], [y[i]], [0]]))
        x[i] = rv[0]
        y[i] = rv[1]
    rt = rotationMatrix(aoa)
    yr = -5*thickness*(0.2969*np.sqrt((xr/chord))-
                              0.1260*(xr/chord)-
                              0.3516*(xr/chord)**2+
                              0.2843*(xr/chord)**3-
                              0.1015*(xr/chord)**4)
    for i in range(points):
        rv = np.matmul(rt, np.asarray([[xr[i]], [yr[i]], [0]]))
        xr[i] = rv[0]
        yr[i] = rv[1]
    x = np.append(x, x)
    y = np.append(y, yr)
    #offset = min(x)
    x = x+xoffset
    return x[:points], y[:points], y[points:]
    
def limit_region(mp, xlims, ylims, rows=None, cols=None):
    #limiting visualisation size
    if(isinstance(rows, type(None))):
        rows = np.where(mp[:,0]>xlims[0])
        tb = mp[rows]
        rows = np.where(tb[:,0]<xlims[1])
    tb = tb[rows]
    if(isinstance(cols, type(None))):
        cols = np.where(tb[:,1]>ylims[0])
        tb = tb[cols]
        cols = np.where(tb[:,1]<ylims[1])
    #final form of array
    return tb[cols], rows, cols
    
def getNumbering(name, numbering_method):
    if(numbering_method=="flow-time"):
        return float(name.split("-")[-1].split(".")[0]+'.'+name.split("-")[-1].split(".")[1])
    if(numbering_method=="time-step"):
        return float(name.split("-")[-1].split(".")[0])
    return 0

def proc2(zipfilename, filename, frame_time, numbering_method, probe_coords, probes, xlims, ylims, contents=None, rows=None, cols=None):
    #print(f"Opening file: {filename}")
    h=0.001
    print("Reading region")
    if(not isinstance(contents, type(None))):
        mp=copy(contents)
        print(f"contents copied, length: {len(mp)}x{len(mp[0])}")
    else:
        zipf = zipfile.ZipFile(zipfilename, "r")
        if(zipfilename!=None):
            file = zipf.open(filename, "r")
            map_contents = file.read().decode().split("\n")
        else:
            file = open("plots/"+filename, "r")
            map_contents = file.read().split("\n")
        #how many lines of the file read should not be analysed
        manual_offset = 1
        sections = 8
        print("Reading file")
        #read single file
        file.close()

        #split lines into single values and clean up empty values
        param_num = len([float(var) for var in map_contents[manual_offset].split(" ") if var])
        #frame_time = getNumbering(filename, numbering_method)#float(filename.split("-")[-1].split(".")[0]+'.'+filename.split("-")[-1].split(".")[1])

        #convert read values into a readable numpy array
        mp = np.zeros((len(map_contents)-manual_offset-1, param_num))
        for i in range(manual_offset, len(map_contents)-1):
            line = [float(var) for var in map_contents[i].split(" ") if var]
            for j in range(len(line)):
                mp[i-1, j]=line[j]
    for pt in range(len(probe_coords)):
        tb2, rows_p, cols_p = limit_region(mp,
                        [probe_coords[pt][0]-h/2., probe_coords[pt][0]+h/2.],
                        [probe_coords[pt][1]-h/2., probe_coords[pt][1]+h/2.])
        probes[0][pt].append(frame_time)
        probes[1][pt].append(np.average(tb2[:,2]))
    mp, rows, cols = limit_region(mp, xlims, ylims)
    return mp, probes, rows, cols

def readToAverage(t, zipfilenames,
            minfiles, maxfiles, sumlist,
            alias,
            numbering_method, dt,
            average_manager, filenum_manager, legend_manager, coords_manager):
    legend = None
    averager = None
    filenum = 0
    coords_flag = False
    coords = None
    for zipfilename in zipfilenames:
        print(f"[{t}]\tOpening zip file: {zipfilename}")
        fzip = zipfile.ZipFile(zipfilename, "r")
        filelist = []
        if(zipfilename!=None):
            if(isinstance(zipfilename, list)):
                for zipfilename in zipfilenames:
                    print(f"reading filelist of {zipfilename}")
                    zfile = zipfile.ZipFile(zipfilename, 'r')
                    filelist.append([])
                    for filename in zfile.filelist:
                        if(alias in filename.filename):
                            filelist[-1].append(filename.filename)
                    zfile.close()
            else:
                zfile = zipfile.ZipFile(zipfilename, 'r')
                filelist.append([])
                for filename in zfile.filelist:
                    if(alias in filename.filename):
                        filelist[0].append(filename.filename)
        else:
            raise Exception("Fast read currently not available for non-zipped files")
        for filename in filelist[0]:
            content = []
            if(filenum-(minfiles-sumlist)<0):
                filenum += 1
                continue
            print(f"[{t}]\tReading text file: {filename} ({filenum-(minfiles-sumlist)+1} of {maxfiles})")
            file = zfile.open(filename, "r")
            lines = file.read().decode().split("\n")
            prev_len = 0
            for l, line in enumerate(lines):
                ll = [var for var in line.split(" ") if var]
                try:
                    float(ll[0])
                except:
                    if(len(ll)>0):
                        prev_line = ll
                    continue
                if(len(ll)<prev_len):
                    break
                for ln in range(len(ll)):
                    if(len(content)<len(ll)):
                        content.append([])
                    content[ln].append(float(ll[ln]))
                if(isinstance(coords, type(None))):
                    coords = [[], [], []]
                    coords_flag = True
                if(coords_flag):
                    coords[0].append(ll[1])
                    coords[1].append(ll[2])
                    coords[2].append(ll[3])
                prev_len = len(ll)
            if(isinstance(legend, type(None))):
                legend = copy(prev_line)
            if(isinstance(averager, type(None))):
                averager = np.asarray(content)
            else:
                averager = (averager*((filenum-(minfiles-sumlist))-1)+np.asarray(content))/(filenum-(minfiles-sumlist))
            filenum += 1
            del(content)
            del(lines)
            file.close()
            coords_flag = False
            if(maxfiles+(minfiles-sumlist)==filenum):
                break
    average_manager[t] = averager
    filenum_manager[t] = filenum-(minfiles-sumlist)
    legend_manager[t] = legend
    coords_manager[t] = coords
    pass

def averageFiles(s, args = []):
    intext = ""
    outputfilename = "output.png"
    if(len(args)<1):
        intext = input(f"Please provide averaged data output file name:\n[{outputfilename}]\n/export average output filename > ")
    else:
        print(f"Please provide averaged data output file name:\n[{outputfilename}]\n/export average output filename > "+args[0])
        intext = args[0]
    if(intext != ""):
        outputfilename = intext
    if(os.path.exists(outputfilename) and os.path.isfile(outputfilename)):
        overwrite = "n"
        if(len(args)<2):
            intext = input(f"Warning: file already exists. Overwrite? (y/n)\n[{overwrite}]\n/singular output file ovewrite > ")
        else:
            intext = args[1]
        if(intext!=""):
            overwrite = intext
        if("n" in overwrite or "N" in overwrite):
            print("Appending output file name")
            outputfilename = ".".join(outputfilename.split(".")[:-1])+"_new."+outputfilename.split(".")[-1]
            print(f"New name:\n{outputfilename}")
        if("y" in overwrite or "ok" in overwrite or "Y" in overwrite):
            print("Overwriting file.")
    
    filelist = []
    if(s.zipfilenames!=None):
        if(isinstance(s.zipfilenames, list)):
            for zipfilename in s.zipfilenames:
                print(f"reading filelist of {zipfilename}")
                zfile = zipfile.ZipFile(zipfilename, 'r')
                filelist.append([])
                for filename in zfile.filelist:
                    if(s.alias in filename.filename):
                        filelist[-1].append(filename.filename)
                zfile.close()
        else:
            zfile = zipfile.ZipFile(s.zipfilenames, 'r')
            filelist.append([])
            for filename in zfile.filelist:
                if(s.alias in filename.filename):
                    filelist[0].append(filename.filename)
            zfile.close()
    else:
        filelist = [[var for var in os.listdir("plots/") if "full" in var]]
        
    sumlist=0
    for i in range(len(filelist)):
        sumlist = sumlist+len(filelist[i])
    if(s.maxfiles == None):
        s.maxfiles = int(sumlist/s.number_of_threads)+1
    sumlist=0
    endlist=len(filelist[0])
    sumlist_tab = []
    start_index = 0
    end_index = 0
    sumlist1 = 0
    sumlist2 = s.maxfiles
    average_manager = Manager().dict()
    filenum_manager = Manager().dict()
    legend_manager = Manager().dict()
    coords_manager = Manager().dict()
    threads = []
    for t in range(s.number_of_threads):
        while(sumlist2>endlist):
            end_index+=1
            if(len(filelist)<=end_index):
                break
            endlist+=len(filelist[end_index])
        while(sumlist1-len(filelist[start_index])>sumlist):
            sumlist+=len(filelist[start_index])
            start_index+=1
        print(f"[{t}]\t{start_index}@{sumlist1}, {end_index}@{sumlist2}\tsumlist={sumlist}")
        print(f"Adding new process: zipfiles at ({start_index}:{end_index+1})")
        #t, s.zipfilenames, minfiles, s.maxfiles, sumlist, s.alias, visualisation_column, xlims, ylims, probes, probe_coords, content_manager, time_manager, probes_manager
        threads.append(Process(target=readToAverage, args=(t, s.zipfilenames[start_index:end_index+1],
                            sumlist1, s.maxfiles, sumlist,
                            s.alias,
                            s.numbering_method, s.dt,
                            average_manager, filenum_manager, legend_manager, coords_manager)))
        threads[-1].start()
        sumlist1+=s.maxfiles
        sumlist2+=s.maxfiles
    for t in threads:
        t.join()
    
    averager = np.zeros_like(average_manager[0])
    filenum = 0
    print(legend_manager[0])
    for t in range(s.number_of_threads):
        averager = averager+average_manager[t]*filenum_manager[t]
        filenum += filenum_manager[t]
        print(f"Number of files at process {t}: {filenum_manager[t]}")
    averager = np.transpose(averager)/filenum
    file = open(outputfilename, "w")
    for lgi, lg in enumerate(legend_manager[0]):
        file.write(lg)
        if(lgi<len(legend_manager[0])-1):
            file.write(" ")
        else:
            file.write("\n")
    coords = coords_manager[s.number_of_threads-1]
    for ln in range(len(averager)):
        for tt in range(len(averager[ln])):
            if(tt>0 and tt<=3):
                file.write(coords[tt-1][ln])
            else:
                file.write("{0:.9e}".format(averager[ln][tt]))
            if(tt<len(averager[ln])-1):
                file.write(" ")
            else:
                file.write("\n")
    print(f"File written to: {outputfilename}")
    
def readFiles(t, zipfilenames, s,
            minfiles, maxfiles, sumlist,
            content_manager,
            time_manager,
            probes_manager, image_manager):
    content = []
    lim_content = []
    time_table = []
    image_array = []
    number_of_files = 0
    rows = None
    cols = None
    probes_ret = []
    for i in range(len(s.probes)):
        probes_ret.append([])
        for j in range(len(s.probes[i])):
            probes_ret[i].append([])
    labels = []
    prev_line = ""
    vis_col_num = None
    print(f"[{t}]\tBuilding list of files")
    udm = []
    for zipfilename in zipfilenames:
        print(f"[{t}]\tOpening zip file: {zipfilename}")
        fzip = zipfile.ZipFile(zipfilename, "r")
        filelist = []
        if(zipfilename!=None):
            if(isinstance(zipfilename, list)):
                for zipfilename in zipfilenames:
                    print(f"reading filelist of {zipfilename}")
                    zfile = zipfile.ZipFile(zipfilename, 'r')
                    filelist.append([])
                    for filename in zfile.filelist:
                        if(s.alias in filename.filename):
                            filelist[-1].append(filename.filename)
                    zfile.close()
            else:
                zfile = zipfile.ZipFile(zipfilename, 'r')
                filelist.append([])
                for filename in zfile.filelist:
                    if(s.alias in filename.filename):
                        filelist[0].append(filename.filename)
        else:
            raise Exception("Fast read currently not available for non-zipped files")
        
        print(f"[{t}]\tReading text files")
        for filename in filelist[0]:
            if(number_of_files-(minfiles-sumlist)<0):
                number_of_files += 1
                continue
            print(f"[{t}]\tReading text file: {filename} ({number_of_files-(minfiles-sumlist)+1} of {maxfiles})")
            file = zfile.open(filename, "r")
            lines = file.read().decode().split("\n")
            prev_len = 0
            if(s.preserveRAM):
                content_rotated = []
            else:
                content.append([])
            time_table.append(getNumbering(filename, s.numbering_method)*s.dt)
            for l, line in enumerate(lines):
                ll = [var for var in line.split(" ") if var]
                try:
                    float(ll[0])
                except:
                    print(f"Could not read line:\n{line}")
                    prev_line = ll
                    continue
                if(isinstance(s.XCoord, str)):
                    s.XCoord = prev_line.index(s.XCoord)
                if(isinstance(s.YCoord, str)):
                    s.YCoord = prev_line.index(s.YCoord)
                if(vis_col_num==None):
                    if(isinstance(s.visualisation_column, int)):
                        vis_col_num = s.visualisation_column
                    if(isinstance(s.visualisation_column, str)):
                        vis_col_num = prev_line.index(s.visualisation_column)
                if(len(ll)<prev_len):
                    break
                if(not s.preserveRAM):
                    for ln in range(3):
                        if(len(content[-1])<3):
                            content[-1].append([])
                        content[-1][ln].append(0.)
                a, b, c, s.visualisation_column, udm = s.processing_method(s.XCoord, s.YCoord, prev_line, ll, s.visualisation_column, udm)
                if(s.preserveRAM):
                    content_rotated.append([a, b, c])
                else:
                    content[-1][0][-1] = a
                    content[-1][1][-1] = b
                    content[-1][2][-1] = c
                prev_len = len(ll)
                #print(content)
                #make image
            if(s.preserveRAM):
                image_array.append(makeSingularImage(s, np.asarray(content_rotated), returnString = True))
                #content.pop(0)
            print(f"[{t}]\tXCol = {s.XCoord}\tYCol = {s.YCoord}\n[{t}]\tvis = {[s.visualisation_column]}")
            number_of_files += 1
            if(maxfiles+(minfiles-sumlist)==number_of_files):
                break
        zfile.close()
    for i in range(len(content)):
        s.probes_nw = copy(s.probes)
        lim_content.append([])
        lim_content[i], s.probes_nw, rows, cols = proc2(None, None, time_table[i], s.numbering_method, s.probe_coords, s.probes_nw, s.xlims, s.ylims, np.transpose(np.asarray(content[i])), rows, cols)
        for pt in range(len(s.probes[1])):
            probes_ret[0][pt].append(s.probes_nw[0][pt][0])
            probes_ret[1][pt].append(s.probes_nw[1][pt][0])
        print(f"[{t}]max[1]={np.max(content[i][0])}")
    print(f"[{t}]\tSending data to main thread")
    if(not s.preserveRAM):
        content_manager[t] = lim_content
    else:
        content_manager[t] = []
        image_manager[t] = image_array
    time_manager[t] = time_table
    probes_manager[t] = probes_ret
    
def makeImage(z, s,
            number_of_files, n18y2,
            h,
            content_manager, time_manager, image_manager,
            returnImage = False):
    images = []
    print(f"[{z}]\t Starting process")
    fig = plt.figure(
        figsize=(s.width, s.height),
        dpi = 1080/s.height
    )
    if(len(s.probe_coords)>0):
        ax = fig.add_subplot(2,1,1)
        axb = fig.add_subplot(2, 1, 2)
        axb.set_box_aspect(1/3)
        axb.grid(True)
    else:
        ax = fig.add_subplot(1,1,1)
    ax.set_xlim((s.xlims[0]*s.xaxis_scale, s.xlims[1]*s.xaxis_scale))
    ax.set_ylim((s.ylims[0]*s.yaxis_scale, s.ylims[1]*s.yaxis_scale))
    ax.set_aspect(1)
    #ax.set_xlim(np.min(content_manager[z][0][0]), np.max(content_manager[z][0][0]))
    fig.canvas.draw()
    bg = fig.canvas.copy_from_bbox(fig.bbox)
    '''
    cont = ax.tricontourf(content_manager[z][0][:,0],
                          content_manager[z][0][:,1],
                          content_manager[z][0][:,2],
                          cmap='jet', s.levels=levels)
    if(draw_airfoil):
            c = ax.fill_between(n18x, n18y, n18y2, color = 'grey', linewidth=0)
    lns = []
    pts = [[], []]
    for pt in range(len(probe_coords)):
            ax.fill_between([probe_coords[pt][0]-h/2., probe_coords[pt][0]+h/2.],
                        probe_coords[pt][1]-h/2., probe_coords[pt][1]+h/2.,
                        color="white")
            ax.text(probe_coords[pt][0]+h/2., probe_coords[pt][1]+h/2., str(pt))
            axb.text(probes[0][pt][number_of_files], probes[1][pt][number_of_files], str(pt))
            lns.append(None)
            (lns[-1],) = axb.plot(probes[0][pt][:number_of_files], probes[1][pt][:number_of_files], c=f"C{pt}", alpha=0.5, animated=True)
            axb.draw_artist(lns[-1])
            pts[0].append(axb.scatter(probes[0][pt][number_of_files], probes[1][pt][number_of_files], c=f"C{pt}"))
            pts[1].append(f"point {pt}")
    fig.canvas.blit(fig.bbox)
    '''
    content = content_manager[z]
    for i in range(len(content)):
        #fig.canvas.restore_region(bg)
        fig.clf()
        fig.canvas.restore_region(bg)
        #fig.set_size_inches(width,height)
        #fig.set_dpi(1920/width)
        if(len(s.probe_coords)>0):
            ax = fig.add_subplot(2,1,1)
            axb = fig.add_subplot(2, 1, 2)
        else:
            ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim((xlims[0]*s.xaxis_scale, xlims[1]*s.xaxis_scale))
        ax.set_ylim((ylims[0]*s.yaxis_scale, ylims[1]*s.yaxis_scale))
        ax.set_aspect(1)
        pts = [[], []]
        print(f"[{z}]\tFrame: {number_of_files}")
        #tb, probes, rows, cols = proc2(None, None, time_manager[z][i], probe_coords, probes, content_manager[z][i], rows, cols)
        #naca0018
        cont = ax.tricontourf(content[i][:,0]*s.xaxis_scale,
                              content[i][:,1]*s.yaxis_scale,
                              content[i][:,2],
                              cmap='jet', levels=s.level)
        #apply mask
        if(s.draw_airfoil):
            c = ax.fill_between(s.n18x*s.xaxis_scale, s.n18y*s.yaxis_scale, n18y2*s.yaxis_scale, color = 'grey', linewidth=0)
        for mask in s.masks:
            ax.fill(mask.xarray*s.xaxis_scale, mask.yarray*s.yaxis_scale, mask.color)
        #write frame time
        tx = fig.text(0.7, 0.03,
                      "t="+str(time_manager[z][i])+"s")
        if(len(s.probe_coords)>0):
            for pt in range(len(s.probe_coords)):
                ax.fill_between([(s.probe_coords[pt][0]-h/2)*s.xaxis_scale, (s.probe_coords[pt][0]+h/2.)*s.yaxis_scale],
                            (s.probe_coords[pt][1]-h/2.)*s.xaxis_scale, (s.probe_coords[pt][1]+h/2.)*s.yaxis_scale,
                            color="white")
                ax.text((s.probe_coords[pt][0]+h/2.)*s.xaxis_scale, (s.probe_coords[pt][1]+h/2.)*s.yaxis_scale, str(pt))
                axb.text(s.probes[0][pt][number_of_files], s.probes[1][pt][number_of_files], str(pt))
                axb.plot(s.probes[0][pt][:number_of_files], s.probes[1][pt][:number_of_files], c=f"C{pt}", alpha=0.5)
                #lns.append(axb.plot(probes[0][pt][:number_of_files], probes[1][pt][:number_of_files], c=f"C{pt}", alpha=0.5))
                #lns[pt].set_ydata(probes[1][pt][:number_of_files])
                pts[0].append(axb.scatter(s.probes[0][pt][number_of_files], s.probes[1][pt][number_of_files], c=f"C{pt}"))
                pts[1].append(f"point {pt}")
            #axb.legend(pts[0], pts[1], scatterpoints=1, loc='upper right')
            axb.set_xlim(s.start_time, s.end_time)
            axb_avg = np.average(np.asarray(s.probe_avg))
            axb_amp = np.max(s.probe_amp)
            axb.set_ylabel("Normalised visualised value")
            axb.set_xlabel("time [s]")
            axb.set_ylim(-1.2, 1.2)
            axb.grid(True)
        if(s.draw_airfoil):
            ax.draw_artist(c)
        #for ln in lns:
        #    axb.draw_artist(ln)
        fig.canvas.draw()
        if(returnImage):
            return fig.canvas.tostring_argb()
        images.append(fig.canvas.tostring_argb())
        number_of_files+=1
    image_manager[z] = images

def execute(s):
    '''
    fig = plt.figure(
        figsize=(width, height),
        dpi = 1920/35*5
    )
    ax = fig.add_subplot(2,1,1)
    axb = fig.add_subplot(2, 1, 2)
    ax.set_xlim((xlims[0], xlims[1]))
    #ax.set_ylim((ylims[0], ylims[1]))
    ax.set_aspect(1)
    axb.set_box_aspect(1/3)
    '''
    #naca0018
    s.n18x, s.n18y, n18y2 = generateNACA(s.airfoil_thickness*s.airfoil_chord, s.airfoil_chord, -airfoil_aoa*np.pi/180.0, points=200)

    filelist = []
    if(s.zipfilenames!=None):
        if(isinstance(s.zipfilenames, list)):
            for zipfilename in s.zipfilenames:
                print(f"reading filelist of {zipfilename}")
                zfile = zipfile.ZipFile(zipfilename, 'r')
                filelist.append([])
                for filename in zfile.filelist:
                    if(s.alias in filename.filename):
                        filelist[-1].append(filename.filename)
                zfile.close()
        else:
            zfile = zipfile.ZipFile(s.zipfilenames, 'r')
            filelist.append([])
            for filename in zfile.filelist:
                if(s.alias in filename.filename):
                    filelist[0].append(filename.filename)
            zfile.close()
    else:
        filelist = [[var for var in os.listdir("plots/") if "full" in var]]
    #print(filelist)
    if(s.numbering_method == "flow-time"):
        s.dt = getNumbering(filelist[0][1], s.numbering_method)-getNumbering(filelist[0][0], s.numbering_method)
    start_time = getNumbering(filelist[0][0], s.numbering_method)#float(filelist[0][0].split("-")[-1].split(".")[0]+'.'+filelist[0][0].split("-")[-1].split(".")[1])
    end_time = getNumbering(filelist[-1][-1], s.numbering_method)#float(filelist[-1][-1].split("-")[-1].split(".")[0]+'.'+filelist[-1][-1].split("-")[-1].split(".")[1])
    if(s.numbering_method=="time-step"):
        start_time *= s.dt
        end_time *= s.dt
    #axb.set_xlim((start_time, end_time))
    for i in range(len(s.probe_coords)):
        s.probes[0].append([])
        s.probes[1].append([])
    
    content_manager = Manager().dict()
    time_manager = Manager().dict()
    probes_manager = Manager().dict()
    image_manager = Manager().dict()#[[] for var in range(s.number_of_threads)]
    threads = []
    sumlist = 0
    for i in range(len(filelist)):
        sumlist = sumlist+len(filelist[i])
    if(s.maxfiles == None):
        s.maxfiles = int(sumlist/s.number_of_threads)+1
    sumlist=0
    endlist=len(filelist[0])
    minfiles = 0
    sumlist_tab = []
    start_index = 0
    end_index = 0
    sumlist1 = 0
    sumlist2 = s.maxfiles
    for t in range(s.number_of_threads):
        while(sumlist2>endlist):
            end_index+=1
            if(len(filelist)<=end_index):
                break
            endlist+=len(filelist[end_index])
        while(sumlist1-len(filelist[start_index])>sumlist):
            sumlist+=len(filelist[start_index])
            start_index+=1
        print(f"[{t}]\t{start_index}@{sumlist1}, {end_index}@{sumlist2}\tsumlist={sumlist}")
        print(f"Adding new process: zipfiles at ({start_index}:{end_index+1})")
        #t, s.zipfilenames, minfiles, s.maxfiles, sumlist, s.alias, s.visualisation_column, s.xlims, s.ylims, s.probes, s.probe_coords, content_manager, time_manager, probes_manager
        threads.append(Process(target=readFiles,
                args=(t, s.zipfilenames[start_index:end_index+1], s,
                    sumlist1,
                    s.maxfiles, sumlist,
                    content_manager, time_manager, probes_manager, image_manager)))
        threads[-1].start()
        sumlist1+=s.maxfiles
        sumlist2+=s.maxfiles
    for t in threads:
        t.join()
    
    sumlist=0
    for i in range(len(filelist)):
        sumlist = sumlist+len(filelist[i])
    
    #s.levels of contours
    if(isinstance(s.levels, type(None))):
        s.levels = np.linspace(-1000, 1000, 256)
        values_range = content_manager[0][0][:,2]
        #read initial file
        #t, LE, HE, s.levels, s.xlims, s.ylims, zipfilename, filelist, multiproc, s.visualisation_column, s.probes, s.probe_coords, contents=None, start_time=0, end_time = 2e-1
        #tb, s.probes, rows, cols = proc2(s.zipfilenames[0], filelist[0][0], 0, s.probe_coords, s.probes, s.xlims, s.ylims, content_manager[0][0])
        s.levels = np.linspace(np.min(values_range)*1.2, np.max(values_range)*1.2, len(s.levels))

    #generate initial contours
    #cont = ax.tricontourf(content_manager[0][0][:,0], content_manager[0][0][:,1], content_manager[0][0][:,2], cmap='jet')
    
    if(len(s.probe_coords)>0):
        s.probes = [[], []]#time, value
        for i in range(len(s.probe_coords)):
            s.probes[0].append([])
            s.probes[1].append([])
            for t in range(s.number_of_threads):
                s.probes[0][i] += probes_manager[t][0][i]
                s.probes[1][i] += probes_manager[t][1][i]
            s.probe_avg[i] = np.average(s.probes[1][i])
            s.probe_amp[i] = (np.max(s.probes[1][i])-np.min(s.probes[1][i]))/2.
        
        #calculate fft of s.probes
        s.dt = np.round(s.probes[0][0][3]-s.probes[0][0][2], decimals=6)
        print(f"s.dt={s.dt}, sumlist={sumlist}")
        freqs = np.linspace(0, (min(sumlist, sumlist1)-1)/(s.dt*min(sumlist, sumlist1)), min(sumlist, sumlist1))
        s.probes_freq = [[], []]
        fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize=(7, 4), dpi=500)
        for pt in range(len(s.probe_coords)):
            s.probes_freq[0].append(freqs)
            s.probes_freq[1].append(20.*np.log10(np.abs(np.fft.fft(s.probes[1][pt]))/sumlist/2e-5))
            ax2.plot(s.probes_freq[0][pt][np.where(s.probes_freq[0][pt]<750)], s.probes_freq[1][pt][np.where(s.probes_freq[0][pt]<750)], label=f"point {pt}")
        ax2.grid(True)
        ax2.legend()
        #ax2.set_xlim(50, 750)
        ax2.set_xlabel("Frequency [Hz]")
        ax2.set_ylabel("SPL [dB]")
        fig2.savefig(".".join(s.videoname.split(".")[:-1])+"_probe_fft.png")
        plt.close(fig2)

    #prepare mask for unnecessarly triangulated values
    #if(s.draw_airfoil):
    #    c = ax.fill_between(n18x, n18y, n18y2)
    #add initial text
    #filename=filelist[0][0]
    #tx = fig.text(0.7, 0.03,
    #              "t="+filename.split("-")[-1].split(".")[0]+
    #              '.'+filename.split("-")[-1].split(".")[1]+"s")
    if(direct==False):
        for z, zipfilename in enumerate(s.zipfilenames):
            threads = []
            for t in range(proc_num):
                LE = int(t*(len(filelist)-1)/proc_num)
                if(t<proc_num-1):
                    HE = int((t+1)*(len(filelist)-1)/proc_num)
                else:
                    HE = (len(filelist))
                threads.append(Process(target=proc, args=(t, LE, HE, s.levels, s.xlims, s.ylims, zipfilename, filelist[z], True, s.visualisation_column, s.probes, s.probe_coords, fig, ax, axb, None, start_time, end_time)))
                threads[-1].start()
            for i in range(proc_num):
                threads[i].join()

    if(direct==True):
        number_of_files=0
        writer = animation.FFMpegWriter(codec="h264",fps=30)
        print(f"Liczba klatek: {min(sumlist, sumlist1)}")
        #with writer.saving(fig, s.videoname, 1920/7):#sumlist
        threads = []
        executed_frames = 0
        if(not s.preserveRAM):
            for z, zipfilename in enumerate(content_manager):
                for i in range(number_of_files, number_of_files+len(content_manager[z])):
                    if(not isinstance(s.probe_avg, type(None))):
                        try:
                            for o in range(len(s.probes[1])):
                                s.probes[1][o][i] -= s.probe_avg[o]
                        except:
                            print("Could not induce average")
                    if(not isinstance(s.probe_amp, type(None))):
                        try:
                            for o in range(len(s.probes[1])):
                                s.probes[1][o][i] /= s.probe_amp[o]
                        except:
                            print("Could not induce amplitude")
                threads.append(Process(target=makeImage, args=(z, s,
                            number_of_files, n18y2,
                            h,
                            content_manager, time_manager, image_manager)))
                threads[-1].start()
                number_of_files+=len(content_manager[z])
            for t in threads:
                t.join()
        print(len(image_manager[0][0]))
        cmd_out = ['ffmpeg',
           '-f', 'rawvideo',
           '-pix_fmt', 'argb',
           '-s', f'{s.horizontal_resolution}x{int(len(image_manager[0][0])/s.horizontal_resolution/4)}',#{int(len(image_manager[0][0])/1080/4)}
           '-r', '75',  # FPS 
           '-i', '-',  # Indicated input comes from pipe 
           '-f', 'mp4',
           '-pix_fmt', 'yuv420p',
           #'-s', f'{int(len(image_manager[0][0])/1080/4)}x1080',#1080#int(len(image_manager[0][0])/1080/4)
           '-b:v', '32000k',
           '-vcodec', 'h264_nvenc',#mpeg4
           s.videoname]
        if(os.path.exists(s.videoname)):
            os.remove(s.videoname)
        pipe = sp.Popen(cmd_out, stdin=sp.PIPE)
        img_mg = []
        for z in range(s.number_of_threads):
                img_mg.append(image_manager[z])
        for z in range(s.number_of_threads):
            for i in range(len(img_mg[z])):
                #print(image_manager[z][i])
                pipe.stdin.write(img_mg[z][i])
        pipe.stdin.close()
        pipe.wait()
        if(isinstance(s.probe_avg, type(None)) or isinstance(s.probe_amp, type(None))):
                outfile = open("s.probes.txt", "w")
                outfile.write(f"coords\t{len(s.probe_coords)}\n")
                for i in range(len(s.probe_coords)):
                    outfile.write(f"{s.probe_coords[i][0]}\t{s.probe_coords[i][1]}\n")
                outfile.write(f"average_vals\t{len(s.probes[1])}\n")
                for i in range(len(s.probes[1])):
                    outfile.write(f"{np.average(s.probes[1][i])}\t \n")
                outfile.write(f"Ra\t{len(s.probes[1])}\n")
                for i in range(len(s.probes[1])):
                    outfile.write(f"{(np.max(s.probes[1][i])-np.min(s.probes[1][i]))/2}\t \n")                
                outfile.close()
    
def findZipFiles(zipfilenames, args = []):
    if(not os.path.exists('plots/') and not os.path.exists('plots.zip') and zipfilenames==None):
        pathflag = False
        print("No known input files found. Would you like to select all zip files in folder?")
        print(os.listdir())
        if(len(args)<1):
            answer = input("[y/n] > ")
        else:
            print("[y/n] > "+args[0])
            answer = args[0]
        if(answer == "Y" or answer=="y" or answer=="yes" or answer=="Yes"):
            for listitem in os.listdir():
                if(".zip" in listitem or ".Zip" in listitem or ".ZIP" in listitem):
                    pathflag = True
                    break
                else:
                    pathflag = False
            if(pathflag):
                zipfilenames = [var for var in os.listdir() if any((".zip" in var, ".Zip" in var, ".ZIP" in var)) and not "filepart" in var]
        else:
            answer = "./"
            if(len(args)<2):
                intext = input(f"Please provide path to external zip file(s):\n[{answer}]\n> ")
                if(intext!=""):
                    answer = intext
            else:
                print(f"Please provide path to external zip file(s):\n[{answer}]\n> "+args[1])
                answer = args[1]
            if(os.path.exists(answer)):
                if(os.path.isdir(answer)):
                    zipfilenames = [answer+"/"+var for var in os.listdir(answer) if any((".zip" in var, ".Zip" in var, ".ZIP" in var)) and not "filepart" in var]
                    pathflag = True
                else:
                    if(os.path.isfile(answer)):
                        if(any((".zip" in answer, ".Zip" in answer, ".ZIP" in answer)) and not "filepart" in answer):
                            zipfilenames = [answer]
                            pathflag = True
                        else:
                            pathflag = False
                    else:
                        pathflag = False
            else:
                pathflag = False
        if(pathflag==False):
            raise Exception("No input folder found!\nPlease insert files into 'contours/plots/'\nfolder or provide zipfile called 'plots.zip'")
    '''
    if(os.path.exists('plots/') and not os.path.exists('plots.zip')):
            zipfilenames = None
            print("Information: Could not find ./plots.zip file.\nReading from text files in ./plots/.")
        if(not os.path.exists('output')):
            os.makedirs('output')
            print("Information: New folder ('output') created!")
    '''
    zipfilenames.sort()
    print(zipfilenames)
    return zipfilenames

def makeSingularImage(s, contents, outputfilename = "0.png", returnString = False):
    fig = plt.figure(
        figsize=(s.width, s.width*(s.ylims[1]-s.ylims[0])/(s.xlims[1]-s.xlims[0])),
        dpi = s.horizontal_resolution/s.width
    )
    ax = fig.add_subplot(111)
    ax.set_xlabel(s.xlabel)
    ax.set_ylabel(s.ylabel)
    print("Setting visualisation levels")
    contents_lim, rows, cols = limit_region(contents, s.xlims, s.ylims)
    if(isinstance(s.levels, type(None))):
        s.levels = np.linspace(np.min(contents_lim[:,2]), np.max(contents_lim[:,2]), 1000)
    print(f"levels' range: {s.levels[0]} - {s.levels[-1]}")
    cont = ax.tricontourf(contents[:, 0]*s.xaxis_scale, contents[:, 1]*s.yaxis_scale, contents[:, 2], cmap='jet', levels = s.levels)
    plt.subplots_adjust(top=0.95)
    #generowanie mapy konturów
    if(s.draw_airfoil):
        print("Applying mask")
        n18x, n18y, n18y2 = generateNACA(s.airfoil_thickness*s.airfoil_chord, s.airfoil_chord, -s.airfoil_aoa*np.pi/180.0, points=200)
        ax.fill_between(n18x*s.xaxis_scale, n18y*s.yaxis_scale, n18y2*s.yaxis_scale, color = 'grey', linewidth=0)
    for i, mask in enumerate(s.masks):
        print(f"Applying mask {i}: \"{mask.name}\"")
        ax.fill(np.asarray(mask.xarray)*s.xaxis_scale, np.asarray(mask.yarray)*s.xaxis_scale, mask.color)
    ax.set_xlim(s.xlims[0]*s.xaxis_scale, s.xlims[1]*s.xaxis_scale)
    ax.set_ylim(s.ylims[0]*s.yaxis_scale, s.ylims[1]*s.yaxis_scale)
    ax.set_aspect(1)
    divider = make_axes_locatable(ax)
    cax = divider.new_horizontal(size='5%', pad=0.1, pack_start=False)
    fig.add_axes(cax)
    plt.colorbar(cont, ax=[ax], cax=cax, orientation="vertical")
    if(returnString):
        fig.canvas.draw()
        imgstring = fig.canvas.tostring_argb()
        plt.close()
        return imgstring
    print(f"Saving file to: {outputfilename}")
    plt.savefig(outputfilename)
    plt.close(fig)

def runSingular(s, args = []):
    s.horizontal_resolution=3840
    completefilelist = []
    inputfilename = None
    if(not isinstance(s.zipfilenames, type(None))):
        for z, zipfilename in enumerate(s.zipfilenames):
            zfile = zipfile.ZipFile(zipfilename, "r")
            completefilelist.append(zfile.namelist())
            zfile.close()
        inputfilename = completefilelist[0][0]
    zfile = None
    lines = None
    data = []
    #ładowanie nazwy pliku
    if(len(args)<1):
        intext = input(f"Please provide input filename:\n[{inputfilename}]\n/singular input file name > ")
    else:
        print(f"Please provide input filename:\n[{inputfilename}]\n/singular input file name > "+args[0])
        intext = args[0]
    if(intext!=""):
        inputfilename = intext
    #ładowanie treści pliku
    if(not os.path.exists(inputfilename) or not isinstance(s.zipfilenames, type(None))):
        for z, filelist in enumerate(completefilelist):
            if(inputfilename in filelist):
                print(f"Opening zip file: {s.zipfilenames[z]}")
                zfile = zipfile.ZipFile(s.zipfilenames[z], "r")
                lines = zfile.open(inputfilename, 'r').read().decode().split("\n")
                break
        if(isinstance(zfile, type(None))):
            print("No file found in zips!!")
            return
    else:
        try:
            lines = open(inputfilename, "r").read().split("\n")
        except:
            print("File not found!")
    if(isinstance(lines, type(None))):
        print("No lines loaded! Interrupting.")
        return
        
    #ładowanie nazwy pliku wyjściowego
    outputfilename = "output.png"
    if(len(args)<2):
        intext = input(f"Please specify ontput file path:\n[{outputfilename}]\n/singular output file name > ")
    else:
        print(f"Please specify ontput file path:\n[{outputfilename}]\n/singular output file name > "+args[1])
        intext = args[1]
    if(intext != ""):
        outputfilename = intext
    if(os.path.exists(intext) and os.path.isfile(intext)):
        overwrite = "n"
        if(len(args)<3):
            intext = input(f"Warning: file already exists. Overwrite? (y/n)\n[{overwrite}]\n/singular output file ovewrite > ")
        else:
            intext = args[2]
        if(intext!=""):
            overwrite = intext
        if("n" in overwrite or "N" in overwrite):
            print("Appending output file name")
            outputfilename = ".".join(outputfilename.split(".")[:-1])+"_new."+outputfilename.split(".")[-1]
            print(f"New name:\n{outputfilename}")
        if("y" in overwrite or "ok" in overwrite or "Y" in overwrite):
            print("Overwriting file.")
    
    #konwersja pliku
    contents = [[], [], []]
    llwidth = 0
    prev_line = []
    if(isinstance(s.XCoord, str)):
        s.XCoord = prev_line.index(s.XCoord)
    if(isinstance(s.YCoord, str)):
        s.YCoord = prev_line.index(s.YCoord)
    print("Loading data")
    udm = []
    for line in lines:
        ll = [var for var in line.split(" ") if var]
        try:
            float(ll[0])
        except: 
            prev_line = ll
            continue
        if(llwidth==0):
            llwidth = len(ll)
        #kiedy zmniejszy się szerokość tablicy przerwij konwersję
        if(len(ll)<llwidth):
            break
        (d1,d2,vmag,d3,udm) = s.processing_method(s.XCoord, s.YCoord, prev_line, ll, s.visualisation_column, udm)
        contents[0].append(d1)
        contents[1].append(d2)
        contents[2].append(vmag)
    contents = np.transpose(np.asarray(contents))
    print("Preparing figure")
    
    makeSingularImage(s, contents, outputfilename, False)
    print("Done.")

def exportData(s, args = []):
    completefilelist = []
    inputfilename = None
    if(not isinstance(s.zipfilenames, type(None))):
        for z, zipfilename in enumerate(s.zipfilenames):
            zfile = zipfile.ZipFile(zipfilename, "r")
            completefilelist.append(zfile.namelist())
            zfile.close()
        inputfilename = completefilelist[0][0]
    zfile = None
    lines = None
    data = []
    #ładowanie nazwy pliku
    if(len(args)<1):
        intext = input(f"Please provide input filename:\n[{inputfilename}]\n/singular input file name > ")
    else:
        print(f"Please provide input filename:\n[{inputfilename}]\n/singular input file name > "+args[0])
        intext = args[0]
    if(intext!=""):
        inputfilename = intext
    #ładowanie treści pliku
    if(not os.path.exists(inputfilename) or not isinstance(s.zipfilenames, type(None))):
        for z, filelist in enumerate(completefilelist):
            if(inputfilename in filelist):
                print(f"Opening zip file: {s.zipfilenames[z]}")
                zfile = zipfile.ZipFile(s.zipfilenames[z], "r")
                lines = zfile.open(inputfilename, 'r').read().decode().split("\n")
                break
        if(isinstance(zfile, type(None))):
            print("No file found in zips!!")
            return
    else:
        try:
            lines = open(inputfilename, "r").read().split("\n")
        except:
            print("File not found!")
    if(isinstance(lines, type(None))):
        print("No lines loaded! Interrupting.")
        return
        
    #ładowanie nazwy pliku wyjściowego
    outputfilename = "output.txt"
    if(len(args)<2):
        intext = input(f"Please specify ontput file path:\n[{outputfilename}]\n/singular output file name > ")
    else:
        print(f"Please specify ontput file path:\n[{outputfilename}]\n/singular output file name > "+args[1])
        intext = args[1]
    if(intext != ""):
        outputfilename = intext
    if(os.path.exists(intext) and os.path.isfile(intext)):
        overwrite = "n"
        if(len(args)<3):
            intext = input(f"Warning: file already exists. Overwrite? (y/n)\n[{overwrite}]\n/singular output file ovewrite > ")
        else:
            intext = args[2]
        if(intext!=""):
            overwrite = intext
        if("n" in overwrite or "N" in overwrite):
            print("Appending output file name")
            outputfilename = ".".join(outputfilename.split(".")[:-1])+"_new."+outputfilename.split(".")[-1]
            print(f"New name:\n{outputfilename}")
        if("y" in overwrite or "ok" in overwrite or "Y" in overwrite):
            print("Overwriting file.")
    contents = [[], [], []]
    llwidth = 0
    prev_line = []
    if(isinstance(s.XCoord, str)):
        s.XCoord = prev_line.index(s.XCoord)
    if(isinstance(s.YCoord, str)):
        s.YCoord = prev_line.index(s.YCoord)
    print("Loading data")
    udm = None
    for line in lines:
        ll = [var for var in line.split(" ") if var]
        try:
            float(ll[0])
        except: 
            prev_line = ll
            continue
        if(llwidth==0):
            llwidth = len(ll)
        #kiedy zmniejszy się szerokość tablicy przerwij konwersję
        if(len(ll)<llwidth):
            break
        (d1,d2,vmag,d3,udm) = s.processing_method(s.XCoord, s.YCoord, prev_line, ll, s.visualisation_column, udm)
        contents[0].append(d1)
        contents[1].append(d2)
        contents[2].append(vmag)
    print("Exporting data")
    file = open(outputfilename, "w")
    file.write(f"xcol ycol {s.processing_method.__name__}\n")
    for ln in range(len(contents[0])):
        for cl in range(len(contents)):
            file.write("{:.9e}".format(contents[cl][ln]))
            if(cl<len(contents)-1):
                file.write(" ")
            else:
                file.write("\n")
    file.close()
    print("Done writing file.")

def findAlias(alias, args = []):
    if(len(args)==0):
        alias =  input("Please specify alias of the visualised files:\n/alias > ")
    else:
        alias = " ".join(args)
    print(f"Alias set to: {alias}")
    return alias

def findXLims(xlims, width, height, args = []):
    if(len(args)==0):
        intext = input(f"Please specify visualisation x size (divide by \" \" sign and use \".\" as decimal point):\n[{xlims[0]} {xlims[1]}]\n/xlims > ")
    if(len(args)>1):
        intext = " ".join(args)
    if(intext!=""):
            try:
                intext_t = intext.split(" ")
                xlims = [float(intext_t[0]), float(intext_t[1])]
            except:
                print("Could not convert line to float!\nFalling back to default xlims.")
    print(f"xlims set to: {xlims}")
    height = 1.4*width*2*np.abs((ylims[1]-ylims[0])/(xlims[1]-xlims[0]))
    return xlims, width, height

def findYLims(ylims, width, height, args = []):
    if(len(args)==0):
        intext = input(f"Please specify visualisation y size (divide by \" \" sign and use \".\" as decimal point):\n[{ylims[0]} {ylims[1]}]\n/ylims > ")
    if(len(args)>1):
        intext = " ".join(args)
    if(intext!=""):
            try:
                intext_t = intext.split(" ")
                ylims = [float(intext_t[0]), float(intext_t[1])]
            except:
                print("Could not convert line to float!\nFalling back to default ylims.")
    print(f"ylims set to: {ylims}")
    height = 1.4*width*2*np.abs((ylims[1]-ylims[0])/(xlims[1]-xlims[0]))
    return ylims, width, height
    
def findVisCol(visualisation_column, args= []):
    if(len(args)==0):
        intext = input(f"Please specify visualised column (add \"!\" at the end if providing column index):\n[{visualisation_column}]\n/vis > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            try:
                if(intext[-1]=="!"):
                    visualisation_column = int(intext[:-1])
                else:
                    visualisation_column = intext
            except:
                print("Could not read line!\nFalling back to default visualised column.")
    print(f"Visualisation column set to: {visualisation_column}")
    return visualisation_column
    
def findXCoord(XCoord, args = []):
    if(len(args)==0):
        intext = input(f"Please specify coordinate X column (add \"!\" at the end if providing column index):\n[{XCoord}]\n/xcol > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            try:
                if(intext[-1]=="!"):
                    XCoord = int(intext[:-1])
                else:
                    XCoord = intext
            except:
                print("Could not read line!\nFalling back to default visualised column.")
    print(f"X-coordinate column set to {XCoord}")
    return XCoord

def findYCoord(YCoord, args = []):
    if(len(args)==0):
        intext = input(f"Please specify coordinate Y column (add \"!\" at the end if providing column index):\n[{YCoord}]\n/ycol > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            try:
                if(intext[-1]=="!"):
                    YCoord = int(intext[:-1])
                else:
                    YCoord = intext
            except:
                print("Could not read line!\nFalling back to default visualised column.")
    print(f"Y-coordinate column set to {YCoord}")
    return YCoord

def findXScale(Scale, args = []):
    if(len(args)==0):
        intext = input(f"Please specify X-axis scale factor:\n[{Scale}]\n/xscale > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            try:
                intext = float(intext)
            except:
                print("Could not read line!\nFalling back to 1.")
    print(f"X-axis scale factor set to {intext}.")
    return intext

def findYScale(Scale, args = []):
    if(len(args)==0):
        intext = input(f"Please specify Y-axis scale factor:\n[{Scale}]\n/yscale > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            try:
                intext = float(intext)
            except:
                print("Could not read line!\nFalling back to 1.")
    print(f"Y-axis scale factor set to {intext}.")
    return intext

def findYLabel(label, args = []):
    if(len(args)==0):
        intext = input(f"Please specify X-axis label:\n[{Scale}]\n/xlabel > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
        if("\\n" in intext):
            intext = '\n'.join(intext.split("\\n"))
        if("\\t" in intext):
            intext = '\t'.join(intext.split("\\t"))
    print(f"X-axis label set to {intext}.")
    return intext

def findYLabel(label, args = []):
    if(len(args)==0):
        intext = input(f"Please specify Y-axis label:\n[{Scale}]\n/ylabel > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
        if("\\n" in intext):
            intext = '\n'.join(intext.split("\\n"))
        if("\\t" in intext):
            intext = '\t'.join(intext.split("\\t"))
    print(f"Y-axis label set to {intext}.")
    return intext

def findLevels(levels, args=[]):
    if(isinstance(levels, type(None))):
        minlev = 0.
        maxlev = 1.
    else:
        minlev = levels[0]
        maxlev = levels[-1]
    n=256
    if(len(args)<1):
        intext = input(f"Please specify minimum contour plot value:\n[{minlev}]\n/levels minval > ")
    else:
        print(f"Please specify minimum contour plot value (auto for both values to be found automatically):\n[{minlev}]\n/levels minval > "+args[0])
        intext = args[0]
    if(intext!=""):
        try:
            minlev = float(intext)
        except:
            if(intext=='auto'):
                return None
            print("Could not read minimum level. Falling back to default value.")
    if(len(args)<2):
        intext = input(f"Please specify maximum contour plot level value:\n[{maxlev}]/levels maxval > ")
    else:
        print(f"Please specify maximum contour plot level value:\n[{maxlev}]/levels maxval > "+args[1])
        intext = args[1]
    if(intext!=""):
        try:
            maxlev = float(intext)
        except:
            print("Could not read maximum level. Falling back to default value.")
    if(len(args)<3):
        intext = input(f"Please specify number of contour plot level values:\n[{n}]/levels n > ")
    else:
        print(f"Please specify number of contour plot level values:\n[{n}]/levels n > "+args[2])
        intext = args[2]
    if(intext!=""):
        try:
            n = int(intext)
        except:
            print("Could not read number of level values. Falling back to default value.")
    levels = np.linspace(minlev, maxlev, n)
    return levels
    
def findNumMethod(numbering_method, dt, args):
    if(len(args)==0):
        intext = input(f"Please specify numbering method (time-step or flow-time):\n[{numbering_method}]\n/numbering method > ")
    else:
        intext = " ".join(args)
    if(intext!=""):
            if("step" in intext):
                numbering_method = "time-step"
                if(len(args)<1):
                    try:
                        dt = float(input(f"Please specify length of time step [dt]:\n/numbering time step > "))
                    except:
                        print("Could not read time step.\nFalling back to default value.")
                else:
                    try:
                        dt = float(args[1])
                    except:
                        print("Could not read time step.\nFalling back to default value.")
            else:
                if("flow" in intext):
                    numbering_method = "flow-time"
                    dt = None
                else:
                    print("No method recognised! Falling back to default.")
    print(f"File numbering method set to: {numbering_method}")
    return numbering_method, dt
    
def findVideoName(videoname, args):
    if(len(args)==0):
        videoname = input("Please specify name for animation:\nVideo name > ")
    else:
        videoname = " ".join(args)
    print(f"Video name set to: {videoname}")
    return videoname

def findAirfoil(airfoil_chord, airfoil_thickness, airfoil_aoa, args):
    if(len(args)<1):
        intext = input(f"Please set airfoil chord (m) [{airfoil_chord}]:\n/airfoil chord > ")
        try:
            airfoil_chord = float(intext)
        except:
            print("Could not set airfoil chord. Falling back to default value.")
    else:
        try:
            airfoil_chord = float(args[0])
        except:
            print(f"Could not set airfoil chord. Falling back to default value ({airfoil_chord}).")
    if(len(args)<2):
        intext = input(f"Please set airfoil thickness (%c) [{airfoil_thickness}]:\n/airfoil thickness > ")
        try:
            airfoil_thickness = float(intext)
        except:
            print("Could not set airfoil thickness. Falling back to default value.")
    else:
        try:
            airfoil_thickness = float(args[1])
        except:
            print(f"Could not set airfoil thickness. Falling back to default value ({airfoil_thickness}).")
    if(len(args)<3):
        intext = input(f"Please set airfoil angle of attack (deg) [{airfoil_aoa}]:\n/airfoil aoa > ")
        try:
            airfoil_aoa = float(intext)
        except:
            print("Could not set airfoil angle of attack. Falling back to default value.")
    else:
        try:
            airfoil_aoa = float(args[2])
        except:
            print(f"Could not set airfoil angle of attack. Falling back to default value ({airfoil_aoa}).")
    print(f"Airfoil parameters set to:\n\tairfoil chord = {airfoil_chord},\n\tairfoil thickness = {airfoil_thickness},\n\tairfoil angle of attack = {airfoil_aoa}")
    return airfoil_chord, airfoil_thickness, airfoil_aoa
    
def findProbes(probe_coords, probe_amp, probe_avg, filepath = "probes.txt", args = []):
    if(len(args)<1):
        intext = input(f"Please specify file containing probe coordinates:\n[{filepath}]\n/probes > ")
    else:
        intext = args[0]
    if(intext!=""):
        filepath = intext
    if(os.path.exists(filepath)):
        coord_lines = 0
        avg_lines = 0
        amp_lines = 0
        infile = open(filepath, "r")
        for line in infile:
            ll = line.split("\t")
            if(ll[0] == "coords"):
                coord_lines = int(ll[1])
                probe_avg = []
                probe_amp = []
                probe_coords = []
                continue
            if(ll[0] == "average_vals"):
                avg_lines = int(ll[1])
                continue
            if(ll[0] == "Ra"):
                amp_lines = int(ll[1])
                continue
            if(coord_lines>0):
                probe_coords.append([float(ll[0]), float(ll[1])])
                coord_lines -= 1
            if(avg_lines>0):
                probe_avg.append(float(ll[0]))
                avg_lines -= 1
            if(amp_lines>0):
                probe_amp.append(float(ll[0]))
                amp_lines -= 1
        if(len(probe_amp)<len(probe_coords)):
            for i in range(len(probe_amp), len(probe_coords)):
                probe_amp.append(0)
        if(len(probe_avg)<len(probe_coords)):
            for i in range(len(probe_avg), len(probe_coords)):
                probe_avg.append(0)
        infile.close()
        print(probe_coords)
        print(probe_avg)
        print(probe_amp)
    return probe_coords, probe_amp, probe_avg
    
def findThreads(number_of_threads, args):
    if(len(args)==0):
        try:
            number_of_threads = int(input(f"Please specify number of threads to be used while\nopening files [{number_of_threads}]\n/threads > "))
        except:
            print("Could not set number of threads. Falling back to default value.")
    else:
        try:
            number_of_threads = int(args[0])
        except:
            print("Could not set number of threads. Falling back to default value.")
    print(f"Number of threads set to: {number_of_threads}")
    return number_of_threads
    
def findMaxFiles(maxfiles, args):
    if(len(args)==0):
        try:
            maxfiles = int(input(f"Please provide number of files to be read by single thread [{maxfiles}]\n:/maxfiles > "))
        except:
            print("Could not set number of files per thread. Falling back to default value.")
    else:
        try:
            maxfiles = int(args[0])
        except:
            print(f"Could not set number of files per thread. Falling back to default value ({maxfiles}).")
    return maxfiles

def printAvailableMasks(settings, printMaskSettings=False):
    if(len(settings.masks)==0):
        print("Masks: No masks set")
        return
    for i, mask in enumerate(settings.masks):
        if(not printMaskSettings):
            print(f"Mask ({i})\t\"{mask.filename}\"")
        else:
            print(f"Mask ({i}):")
            mask.printSettings()

def checkMaskRemoveFlags(settings):
    for i, mask in enumerate(settings.masks):
        if(mask.removeFlag):
            settings.masks.pop(i)
    return settings

def findMask(settings, args):
    if(len(settings.masks)==0):
        mask = maskSettings()
        mask.menu(args)
        settings.masks.append(mask)
        return checkMaskRemoveFlags(settings)
    if(len(settings.masks)>=1):
        print("Please select mask to edit (n! for new):")
        printAvailableMasks(settings)
        if(len(args)<1):
            intext = input("mask select > ")
        else:
            intext = args[0]
            args = args[1:]
            print(f"mask select > {intext}")
        if(intext=="n!"):
            mask = maskSettings()
            mask.menu(args)
            settings.masks.append(mask)
            return checkMaskRemoveFlags(settings)
        try:
            intext = int(intext)
        except:
            try:
                intext = [mask.name for mask in settings.masks].index(intext)
            except:
                print(f"Could not find mask name: {intext}")
                return
        settings.masks[intext].menu(args[:-1])
        return checkMaskRemoveFlags(settings)


def findPreseveRAM(preserveRAM, args):
    if(len(args)==0):
        pass
    
def printAvailable():
    print("zipname\t\tfind zip files in given directory")
    print("alias\t\tset part of the name that files will be recognised by")
    print("xlims\t\tset x limits of visualised domain")
    print("ylims\t\tset x limits of visualised domain")
    print("processing\tset processing method")
    print("vis\t\tset visualised column name or index number")
    print("xcol\t\tset X-coordinate column name or index number")
    print("ycol\t\tset Y-coordinate column name or index number")
    print("num-method\tset file numbering recognision metod")
    print("airfoil\t\tdraw airfoil mask")
    print("mask\t\tload contour from external file as mask")
    print("levels\t\tset level range of contour plot")
    print("videoname\tset name of the output video file")
    print("singular\tgenerate a static image for given file")
    print("average\t\tgenerate file contaning averaged values from given zip files")
    print("threads\t\tset number of threads used while opening files")
    print("maxfiles\tset maximum number of files read per thread")
    print("settings\tprint all current settings")
    print("run\t\texecute visualisation")
    print("exit\t\tquit program")
    print("q\t\tquit program")

def printCurrentSettings(s):
    print(f"Width of image: {s.width}")
    print(f"Height of image: {s.height}")
    print(f"X limits of visualised domain: {s.xlims}")
    print(f"Y limits of visualised domain: {s.ylims}")
    if(isinstance(s.levels, type(None))):
        print(f"Contour plot level range: calculated")
    else:
        print(f"Contour plot level range: {s.levels[0]} - {s.levels[-1]}")
    print(f"Apply airfoil mask?: {s.draw_airfoil}")
    print(f"Chord of airfoil mask: {s.airfoil_chord}")
    print(f"Thickness of airfoil mask: {s.airfoil_thickness}")
    print(f"Angle of attack of airfoil mask: {s.airfoil_aoa}")
    printAvailableMasks(s, True)
    print(f"Data processing method: {s.processing_method.__name__}")
    print(f"Zip filenames:\n{s.zipfilenames}")
    print(f"File alias: {s.alias}")
    print(f"X-coordinate column: {s.XCoord}")
    print(f"Y-coordinate column: {s.YCoord}")
    print(f"Visualised column: {s.visualisation_column}")
    print(f"File numbering method: {s.numbering_method}")
    if(s.dt!=None):
        print(f"Time step length: {s.dt}")
    else:
        print(f"Time step length: calculated")
    print(f"Max files per thread: {s.maxfiles}")
    print(f"Probe coordinates:\n{s.probe_coords}")
    print(f"Number of threads for file opening: {s.number_of_threads}")
    print(f"Output video name: {s.videoname}")

#times of animation are found automatically
start_time = 0
end_time = 0
if(__name__=='__main__'):
    #times of animation are found automatically
    start_time = 0
    end_time = 0
    h=0.001
    dt=1e-5
    probe_coords = []#[0.115, 0.011]
    probes = [[], []]#time, value
    probe_avg = None
    probe_amp = None
    alias = "."
    XCoord = 1
    YCoord = 2
    number_of_threads = cpu_count()
    levels = None
    width = 7
    height = width*np.abs(((ylims[1]-ylims[0])/(xlims[1]-xlims[0])))*2
    maxfiles = None
    numbering_method="flow-time"
    processing_method = processingFunctions.plainProcess
    preserveRAM = True
    #probe_coords, probe_amp, probe_avg = findProbes(probe_coords, probe_amp, probe_avg, "probes.txt")
    airfoil_chord = 0.2
    airfoil_thickness = 0.18
    airfoil_aoa = 4
    draw_airfoil = False
    videoname = "output.mp4"
    line = ""

    settings = graphSettings()

    while(line!="exit" and line!="q"):
        args = []
        ll = []
        try:
            line = input("> ")
            if(line!=""):
                if(line[0]==";"):
                    continue
            ll = line.split(" ")
            if(len(ll)>1):
                args = ll[1:]
            if(ll[0] == "zipname"):
                settings.zipfilenames = findZipFiles(settings.zipfilenames, args)
            if(ll[0] == "singular"):
                runSingular(settings, args)
            if(ll[0] == "alias"):
                settings.alias = findAlias(settings.alias, args)
            if(ll[0] == "xlims"):
                settings.xlims, settings.width, settings.height = findXLims(settings.xlims, settings.width, settings.height, args)
                if(len(probe_coords)<1):
                    settings.height = settings.height/2.
            if(ll[0] == "ylims"):
                settings.ylims, settings.width, settings.height = findYLims(settings.ylims, settings.width, settings.height, args)
                if(len(probe_coords)<1):
                    settings.height = settings.height/2.
            if(ll[0] == "vis"):
                '''
                visualisation_column = findVisCol(visualisation_column, args)
                '''
                settings.visualisation_column = settings.processingFunctions.findVis(settings.processing_method, settings.visualisation_column, args)
            if(ll[0] == "xcol"):
                settings.XCoord = findXCoord(settings.XCoord, args)
            if(ll[0] == "ycol"):
                settings.YCoord = findYCoord(settings.YCoord, args)
            if(ll[0] == "xscale"):
                settings.xaxis_scale = findXScale(settings.xaxis_scale, args)
            if(ll[0] == "yscale"):
                settings.yaxis_scale = findYScale(settings.yaxis_scale, args)
            if(ll[0] == "xlabel"):
                settings.xlabel = findXScale(settings.xlabel, args)
            if(ll[0] == "ylabel"):
                settings.ylabel = findYScale(settings.ylabel, args)
            if(ll[0] == "num-method" or ll[0]=="num"):
                settings.numbering_method, settings.dt = findNumMethod(settings.numbering_method, settings.dt, args)
            if(ll[0] == "airfoil"):
                if(not settings.draw_airfoil):
                    settings.draw_airfoil = True
                    settings.airfoil_chord, settings.airfoil_thickness, settings.airfoil_aoa = findAirfoil(settings.airfoil_chord, settings.airfoil_thickness, settings.airfoil_aoa, args)
                    print("Airfoil mask enabled")
                else:
                    settings.draw_airfoil = False
                    print("Airfoil mask disabled")
            if(ll[0] == "mask"):
                settings = findMask(settings, args)
            if(ll[0]=="maxfiles"):
                settings.maxfiles = findMaxFiles(settings.maxfiles, args)
            if(ll[0] == "reload-probes" or ll[0] == "rp"):
                settings.probe_coords, settings.probe_amp, settings.probe_avg = findProbes(settings.probe_coords, settings.probe_amp, settings.probe_avg, "probes.txt", args)
            if(ll[0] == "levels"):
                settings.levels = findLevels(settings.levels, args)
            if(ll[0] == "videoname"):
                settings.videoname = findVideoName(settings.videoname, args)
            if(ll[0] == "export" or ll[0] == "wd"):
                exportData(settings, args)
            if(ll[0] == "processing"):
                settings.processing_method, settings.visualisation_column = processingFunctions.setProcessingMethod(settings.processing_method, settings.visualisation_column, args)
            if(ll[0] == "average"):
                averageFiles(settings, args)
            if(ll[0] == "settings"):
                printCurrentSettings(settings)
            if(ll[0] == "threads"):
                number_of_threads = findThreads(number_of_threads, args)
            if(ll[0] == "run"):
                execute(settings)
            if(line==""):
                printAvailable()
        except KeyboardInterrupt:
            print("Interrupted.")
    '''
    fig = plt.figure(figsize=(7.*1., 7.*((ylims[1]-ylims[0])/(xlims[1]-xlims[0]))), dpi = 1920/35*5)
    ax = fig.add_subplot(111)
    '''
    
