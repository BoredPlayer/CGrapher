import zipfile
import os
import numpy as np
from sys import maxsize
from multiprocessing import Processing, Manager, cpu_count

class fileProcessing:
    class threadFiles:
        def __init__(dontusezip=False):
            self.zipfiles = []
            self.filelist = []
            self.previousZipFileIndex = 0
            self.previousFileIndex = 0
            self.currentZipFileIndex = 0
            self.currentFileIndex = 0
            self.currentZipFile = None
            self.currentFile = None
            self.dontusezip = dontusezip
            self.fullLength = 0
        
        def __len__():
            return self.fullLength
        
        def addFiles(self, filelist):
            if(len(self.zipfiles)<len(self.filelist)+1):
                print("Warning: number of zip file names and lists of files not equal!")
            self.filelist.append(filelist)
            self.fullLength += len(filelist)
            
        def addFileName(self, filename):
            '''
            Adds file to current zip file
            '''
            if(len(self.zipfiles)>len(self.filelist)):
                self.filelist.append([])
            if(isinstance(filename, str)):
                self.filelist[-1].append(filename)
            if(isinstance(filename, list)):
                if(len(filename)>0):
                    self.filelist[-1].append(filename[0])
                    self.addFileName(filename[1:])
            self.fullLength+=1
        
        def addZipFile(self, zipfilename):
            if(isinstance(zipfilename, str) or isinstance(zipfilename, type(None))):
                self.zipfiles.append(zipfilename)
                return
            if(isinstance(zipfilename, list)):
                self.zipfiles = [var for var in zipfilename]
            if(isinstance(self.currentZipFile, type(None)) and not self.dontusezip):
                self.currentZipFile = zipfile.ZipFile(self.zipfiles[0], "r")
        
        def getCurrentFileName(includeZip=False):
            if(includeZip):
                return self.zipfiles[self.currentZipFileIndex], self.filelist[self.currentZipFileIndex][self.currentFileIndex-1]
            return self.filelist[self.currentZipFileIndex][self.currentFileIndex-1]
        
        def getNextFileName(includeZip=False):
            self.previousZipFileIndex = self.currentZipFileIndex
            self.previousFileIndex = self.currentFileIndex
            self.currentFile+=1
            if(len(self.filelist[self.currentZipFile]) > self.currentFile):
                self.currentFile = 1
                self.currentZipFile += 1
            return self.getCurrentFileName(includeZip)
        
        def openNextFile():
            fzipname, filename = self.getNextFileName(includeZip=True)
            if(not isinstance(self.currentFile, type(None))):
                self.currentFile.close()
            if(self.previousZipFileIndex!=self.currentZipFileIndex and not self.dontusezip):
                self.currentZipFile.close()
                self.currentZipFile = zipfile.ZipFile(fzipname, "r")
            self.currentFile = self.currentZipFile.open(filename, "r")
            return self.currentFile
    
    def __init__(self):
        self.path = "./"
        self.threads = cpu_count()
        self.ziplist = []
        self.strip_columns = []
        self.threadFileList = []
        self.dontusezip = False
        self.maxFilesPerThread = maxsize
        self.alias = None
        
    def availCommands(self):
        print("cd\t\tchange operating directory")
        #print("tobin\tconvert files to binary")
        #print("strip\tdelete columns from files")
        print("pwd\t\tshow current operating path")
        print("findzip\tcreate list of zips in folder")
        print("listzip\tprint current list of zips")
        print("alias\tset characteristic string for searched files")
    
    def cd(self, args):
        if(len(args)<1):
            intext = input("/file/cd > ")
        else:
            print("/file/cd > "+args[0])
            intext = args[0]
        if(os.path.isdir(intext)):
            self.path = intext
            return
        print(f"Could not find path. Falling back to default path ({self.path})\n")
        
    def makeziplist(self):
        if(self.dontusezip):
            self.ziplist = [None]
            return
        self.ziplist = [var for var in os.listdir if
                        ((".zip" in var) or
                        (".Zip" in var) or
                        (".ZIP" in var))]
    
    def convertZipIndexToName(self, args):
        '''
        Finds wheather listed argument is an
        index of self.ziplist array and replaces
        it with proper name.
        '''
        for i in range(len(args)):
            if(args[i][-1]=="!"):
                args[i] = args[i][:-1]
            try:
                args[i] = int(args[i])
            except:
                continue
                
            indx = int(args[i])
            if(indx>len(self.ziplist)):
                print(f"Index {indx} not listed in zip file list.")
                continue
            args[i] = self.ziplist[indx]
        return args
            
    
    def printZipList(self):
        if(len(self.ziplist)==0):
            print("No zip files found.")
            return
        for i in range(len(self.ziplist)):
            print(f"{i}\t{self.ziplist[i]}")
    
    def checkZipList(self, args):
        '''
        Checks if all listed files are available
        in self.ziplist.
        '''
        for i in range(len(args)):
            if(not args[i] in self.ziplist):
                print(f"Warning: file \"{args[i]}\" not listed in zip file list. Ignoring.")

    def excludezip(self, args):
        '''
        Excludes paths to zip files from zip list.
        '''
        if(len(args<1)):
            intext = input("Which zip file(s) to exclue?\n/file/exclude > ")
        else:
            print(f"Which zip file to exclue?\n/file/exclude > {args[0]}")
            intext = " ".join(args)
        if(intext==""):
            self.printZipList()
            self.excludezip(args)
            return
        args = intext.split(" ")
        args = self.convertZipIndexToName(args)
        self.checkZipList(args)
        self.ziplist = [var for var in self.ziplist if not (var in args)]
        
    def pwd(self):
        print(f"Current path\n{self.path}")
        
    def prepareNonZipFileList(self):
        pass
    
    def prepareFileList(self):
        '''
        Separates available files into thread lists
        '''
        if(isinstance(self.alias, type(None))):
            self.setAlias([])
        filelist = []
        self.threadFileList = [threadFiles(dontusezip)]
        number_of_files = 0
        #read filelists in all zipfiles
        for zipfilename in self.ziplist:
            if(zipfilename==None):
                filelist.append(os.listdir(self.path))
                number_of_files = len(filelist[0])
                break
            zfile = zipfile.ZipFile(zipfilename, "r")
            filelist.append(zfile.namelist)
            number_of_files += len(zfile.namelist)
            
        #distribute file among threads
        filesPerThread = min(int(number_of_files/self.threads)+1, self.maxFilesPerThread)
        for z, zipfilename in enumerate(self.ziplist):
            self.threadFileList[-1].addZipFile(zipfilename)
            for filename in filelist[z]:
                #if the files per thread value is exceeded, create new list
                if(len(threadFileLists[-1])>=filesPerThread):
                    self.threadFileList.append(threadFiles(dontusezip))
                    self.threadFileList[-1].addZipFile(zipfilename)
                self.threadFileList[-1].addFileName(filename)
        #At this point all files are separated into lists
        #to be read by threads.
    
    def createProcess(self, function, arguments, managers):
        threads = []
        for t in range(self.threads):
            threads.append(Process(
                    target=functions,
                    args=(arguments, managers)
                ))
            threads[-1].start()
        for t in range(self.threads):
            threads[t].join()
    
    def tobin(self, args):
        pass
    
    def setstrip(self, args):
        pass
        
    def setAlias(self, args):
        if(len(args)==0):
            alias =  input("Please specify alias of the visualised files:\n/file/alias > ")
        else:
            alias = " ".join(args)
        print(f"Alias set to: {alias}")
        self.alias = alias
        
    def menu(self, args):
        if(len(args)<1):
            intext = input("/file > ")
        else:
            print("/file > "+args[0])
            intext = " ".join(args)
        args = intext.split(" ")
        while(intext!='q' and intext!="exit"):
            if(intext == ""):
                self.availCommands()
                continue
            if(args[0] == "cd"):
                self.cd(args[1:])
                continue
            if(args[0] == "tobin"):
                self.tobin(args[1:])
                continue
            if(args[0] == "strip"):
                self.setstrip(args[1:])
                continue
            if(args[0] == "pwd"):
                self.pwd()
            if(args[0] == "findzip"):
                self.makeziplist()
            if(args[0] == "listzip"):
                self.printZipList()