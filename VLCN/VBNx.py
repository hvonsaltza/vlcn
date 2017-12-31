import sys
import os
#import tk
import numpy
import subprocess
import json
import datetime
sys.path.append(os.getcwd())
from vlcfox import VLC

class scheduler:
    def __init__(self):
        self.filepath = os.path.dirname(os.path.abspath(__file__))
        self.txtSettingsPath = (self.filepath + '\\' + 'Settings.txt')
        self.schedulesPath = (self.filepath + '\\' + 'Schedules')
        self.dbPath = (self.filepath + '\\' + 'db.txt')
        self.cdbPath = (self.filepath + '\\' + 'cdb.txt')
        self.vlcPath = (self.filepath + '\\' + 'VLC\\' + 'vlc.exe')
        self.contentPath = (self.filepath + '\\' + 'Content')
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv")
#        self.player = VLCclass

#Checks for the daily schedule file in the schedules folder
    def checkforschedule(self):
        now = datetime.datetime.now()
        tocheck = (str(now)[:10])
        if os.path.exists(self.schedulesPath + tocheck + '.txt'):
            self.queuefiles()
        else:
            self.buildSchedule()

#Root method to construct the schedule
    def buildSchedule(self):
        showList = self.getScheduleSettings(self.txtSettingsPath)
        print('Building...')
        for x in showList:
            print(x)
            self.loadblock(x,'nochoice')

#Opens, reads, and returns the daily schedule settings                
    def getScheduleSettings(self,dataSource):
        self.linereader = ''
        with open(dataSource,'r',encoding = 'utf-8') as settings:
            rawinfo = []
            cleaninfo = []
            Take = False
            for line in settings:
                if Take == True:
                    rawinfo.append(line)
                if '###SCHEDULE###' in line:
                    Take = True
                elif '#X#ENDSCHEDULE#X#' in line:
                    Take = False
                    del rawinfo[-1]
        for x in rawinfo:
           cleaninfo.append(x[10:-1])
        return cleaninfo

#Loads up a passed 'block' by opening up the content folder, reading the Data.txt file, shuffling it, and selecting until the time block is full.
    def loadblock(self, content, choosing):
        if os.path.exists(self.contentPath + '\\' + content + '\\Data.txt'):
            print('Loading Blocks...')
            with open(chauncy,'r', encoding = 'utf-8') as cdb:
                linereader = cdb.read().splitlines()
            splitline = self.linesplitter(linereader)
            ubound = len(splitline)
            tobeshuffled = list(range(0,ubound))
            numpy.random.shuffle(tobeshuffled)
            i = 0
            blockcontent = []
            tottime = 0
            timeclear = True
            while timeclear == True:
                blockcontent.append(splitline[[tobeshuffled[i]],0])
                timechuck = splitline[[tobeshuffled[i]],1]
                if tottime + timechuck > 3000:
                    timeclear = False
                tottime = tottime + timechuck
            self.passblock = block(blockcontent, tottime)
        else:
            print('Generating Data.txt for ' + content)
            #self.buildtxt(
               
    def linesplitter(self, lines):
        for x in lines:
            Rbound = x.find('length: ')
            Array1.append(x[:Rbound-3])
        for x in lines:
            Lbound = x.find('length: ')
            Rbound = x.find(' endl')
            Array2.append(int(x[Lbound+8:Rbound-2]))
        for x in lines:
            Lbound = x.find('aired: ')
            Array3.append(x[Lbound+7:])
        fullArray = numpy.column_stack((Array1,Array2,Array3))
         
    def cdb_interpret(self, stringline):
        stringlist = []
        if len(stringline) < 30:
            stringlist.append('INVALID')
        else:
           boundL = stringline.find('length')
           boundR = stringline.find('endl')
           stringline = stringline[boundL:boundR]
           print('this is stringline' + stringline)
           
    def checkDirectory(self):
        pass

    def get_len(self, filename):
        result = subprocess.Popen([r'C:\Users\hvons\Videos\VBN\Plugins\ffprobe.exe', filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        return numpy.ceil(float(json.loads(result.stdout.read())['streams'][0]['duration']))

    def write_len(self,database,contentdir,Desc):
        linereader = []
        i = 0
        rememberLines = []
        newLenValues = []
        with open(database,'r', encoding = 'utf-8') as cdb:
            linereader = cdb.read().splitlines()
        for x in linereader:
            i += 1
            if x.find('length') == -1 and x.find(Desc) > 0:
                rememberLines.append(i)
                xlength = self.get_len(contentdir + x)
                x = (x + '   length: ' + str(xlength) + ' endl')
                newLenValues.append(x)
        i = 0
        for g in rememberLines:
            linereader.pop((g-1))
            linereader.insert((g-1), newLenValues[i])
            i +=1
        with open(database, 'w', encoding = 'utf-8') as cdb:
            cdb.write("\n".join(map(str, linereader)))

class ingestedContent:
    def __init__(self,rootname):
        pass



class block:
    def __init__(self,contentList,runtime):
        self.contentList = contentList
        self.runtime = runtime

class ContentIndexer:
    def __init__(self):
        self.CollectionPath = (localSettings.filepath + '\\' + 'Content')
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv")

    def directorySearch(self, databasepath):
        os.listdir(self.CollectionPath)

    def dataReader(self,dataSource):
        self.linereader = []
        with open(dataSource,'r',encoding = 'utf-8') as db:
            self.linereader = db.read().splitlines()
            return self.linereader

    def checkContent(self,dataSource,filepath):
        contentData = self.dataReader(dataSource)
        contentActual = os.listdir(filepath)
        if contentData != contentActual:
            print('Creating Content Database')
            self.ingestContent(contentActual)
            self.writeContent(dataSource,contentActual)

    def writeContent(self,dataDestination,toWrite):
        with open(dataDestination,'w', encoding = 'utf-8') as db:
            db.write("\n".join(map(str, toWrite)))
            print('Content Written to ' + str(dataDestination))

    def ingestContent(self,contentActual):
        allContent = []
        for x in contentActual:
            lookdir = (self.CollectionPath + '\\' + x)
            contentInDir = os.listdir(lookdir)
            for x in contentInDir:
                if x.endswith(self.ext):
                    print(lookdir + '\\' + x) 
                    allContent.append(x) 
        self.writeContent(localSettings.cdbPath,allContent)
                
dayScheduler = scheduler()
dayScheduler.checkforschedule()

