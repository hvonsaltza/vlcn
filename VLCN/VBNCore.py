import sys
import os
#import tk
import numpy
import subprocess
import json
sys.path.append(os.getcwd())
from vlcfox.py import VLC

class settings:
    def __init__(self):
        self.filepath = os.path.dirname(os.path.abspath(__file__))
        self.txtSettingsPath = (self.filepath + '\\' + 'Settings.txt')
        self.dbPath = (self.filepath + '\\' + 'db.txt')
        self.cdbPath = (self.filepath + '\\' + 'cdb.txt')
        self.vlcPath = (self.filepath + '\\' + 'VLC\\' + 'vlc.exe')

class scheduler:
    def __init__(self,settingsobj):
        self.cdbPath = settingsobj.cdbPath
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv")
        
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

    def loadblock(self,blockindex,scheduleinfo,air_type):
        selectedcontent = []
        mountBlock = scheduleinfo[blockindex]
        mountDir = (localSettings.filepath + '\\' + 'Content' + '\\' + mountBlock)
        contentNames = os.listdir(mountDir)
        if mountBlock[-3:-2] == 'S':
            contenttype = 'Television'
        while full == 0:
            if air_type == 'type_random':
                identcontent = (numpy.random.choice(contentNames))
                selectedcontent.append(numpy.random.choice(contentNames))
            else:
                identcontent = (numpy.random.choice(contentNames))
            chauncy = localSettings.cdbPath
            with open(chauncy,'r', encoding = 'utf-8') as cdb:
            linereader = cdb.read().splitlines()
            for x in linereader:
                if x.find(identcontent) >= 0:
                    identData = x
                    break
                else
        
        
    def cdb_interpret(self, stringline):
        stringlist = []
        if len(stringline) < 30:
            stringlist.append('INVALID')
        else:
           boundL = stringline.find('length')
           boundR = stringline.find('endl')
           stringline = stringline[boundL:boundR]
           print('this is stringline' + stringline)

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
                                                
   # def get_len_bulk(self,directory):
   #     contentNames = os.listdir(directory)
   #     contentList = list((directory + '\\' + x) for x in contentNames if x.endswith(self.ext))
   #     total=0
   #     for obj in contentList:
   #         total = total + self.get_len(obj)
   #     print(total)

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
                

localSettings = settings()        
Scanner = ContentIndexer()
Scanner.checkContent(localSettings.dbPath, Scanner.CollectionPath)
dayScheduler = scheduler(localSettings)
dailysettings = dayScheduler.getScheduleSettings(localSettings.txtSettingsPath)
dayScheduler.loadblock(1,dailysettings,'type_random')
dayScheduler.write_len(localSettings.cdbPath, (r'C:\Users\hvons\Videos\VBN\Content\Community S02\\'), 'S02')
#Basecontent.get_len_bulk(r'C:\Users\hvons\Videos\VBN\Content\Community S02')
#dayScheduler.get_len_bulk(r'C:\Users\hvons\Videos\VBN\Content\Community S02')
#PlayerInstance = VLC(localSettings.vlcPath)
#PlayerInstance.add((Scanner.CollectionPath + '\\' + 'Community S02\\Community S02E02.avi'))
#PlayerInstance.fullscreen()
dayScheduler.cdb_interpret('Community S02E01.avi   length: 1258.423832')



#def get_len(filename):
#   result = subprocess.Popen([r'C:\Users\hvons\Videos\VBN\Plugins\ffprobe.exe', filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
#     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
#   return float(json.loads(result.stdout.read())['streams'][0]['duration'])
       

#doggo = list((r'C:\Users\hvons\Videos\VBN\Content\Community S02' + '\\' + x) for x in test if x.endswith('.avi'))
#total=0
#for obj in doggo:
#    total = total + get_len(obj)
#print(total)
