import sys
import os
import time
import numpy
import subprocess
import json
import datetime
sys.path.append(os.getcwd())
from vlcfox import VLC
import mpgen

class scheduler:
    def __init__(self, VLCclass):
        self.filepath = os.path.dirname(os.path.abspath(__file__))
##        print(self.filepath)#DEBUG
        self.txtSettingsPath = (self.filepath + '\\' + 'Settings.txt')
        self.schedulesPath = (self.filepath + '\\' + 'Schedules')
        self.dbPath = (self.filepath + '\\' + 'db.txt')
        self.cdbPath = (self.filepath + '\\' + 'cdb.txt')
        self.vlcPath = (self.filepath + '\\' + 'VLC\\' + 'vlc.exe')
        self.contentPath = (self.filepath + '\\' + 'Content')
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv", "m4v")
        self.player = VLCclass

#Checks for the daily schedule file in the schedules folder
    def checkforschedule(self):
        now = datetime.datetime.now()
        tocheck = (str(now)[:10])
        if os.path.exists(self.schedulesPath + tocheck + '.txt'):
            self.queuefiles()
        else:
            self.buildSchedule()

    def buildSchedule(self):
        self.scheduledata = self.getScheduleSettings(self.txtSettingsPath)
        print('Building...')
        culledBlockList = self.remainingblocks(self.scheduledata)
        
        now = datetime.datetime.now()
        self.timenow = (str(now)[11:-7])
        self.blockindex = (numpy.floor(((int((self.timenow)[:2]))/2)))
        sectime = (60*(int((self.timenow)[3:-3])) + (int((self.timenow)[3:-3])))
        
        i = 0
        blockruntime = 0
        totalruntime = 0
        setupstatus = True
        blockSeek = False
        self.overrun = 0
        for x in culledBlockList:
            #y = x[10:-1]
            #print(y)
            hardBlock = (self.loadblock(x, setupstatus))
            #print(i+self.blockindex)
            for x in hardBlock:
                if blockSeek == False:
                    blockruntime = (x.runtime + blockruntime)
                    totalruntime = (totalruntime + x.runtime)
                    if blockruntime >= sectime:
                        self.player.add(x.directory)
                        self.player.seek((sectime - (blockruntime - x.runtime)))
                        blockSeek = True
                    else:
                        next
                elif blockSeek == True:
                    totalruntime = (totalruntime + x.runtime)
                    self.player.enqueue(x.directory)
            i += 1
            if setupstatus == True:
                firstTitles = mpgen.titlecard(self.scheduledata, self.blockindex)
                self.player.enqueue(firstTitles.contentlocation)
                totalruntime = (totalruntime + firstTitles.runtime)
                setupstatus = False
            self.blockindex += 1
            #print(self.blockindex)
                
    def remainingblocks(self, schedule):
        now = datetime.datetime.now()
        timenow = (str(now)[11:-10])
        hour = (int(str(now)[11:-13]))
        #print(hour)
        newschedule = []
        for x in schedule:
            timechk = (int((x)[:2]))
            if hour <= timechk:
                newschedule.append(x)
        return newschedule
                
#Opens, reads, and returns the daily schedule settings                
    def getScheduleSettings(self,dataSource):
        self.linereader = ''
        with open(dataSource,'r',encoding = 'utf-8') as settings:
            rawinfo = []
            Take = False
            for line in settings:
                if Take == True:
                    rawinfo.append(line)
                if '###SCHEDULE###' in line:
                    Take = True
                elif '#X#ENDSCHEDULE#X#' in line:
                    Take = False
                    del rawinfo[-1]
        return rawinfo

    def loadblock(self, contentLine, setupbool):
        blocktime = ((((int((contentLine[5:9])) - (int((contentLine[:4]))))/100)*3600))
        folderpath = (self.contentPath + '\\' + (contentLine[10:-1]))
        if os.path.exists(folderpath + '\\Data.txt') == False:
            print('Generating Data.txt for ' + (contentLine[10:-1]))
            self.buildtxt(folderpath)
        print('Loading Blocks ' + contentLine)
        with open((folderpath + '\\Data.txt'),'r', encoding = 'utf-8') as cdb:
            linereader = cdb.read().splitlines()
        splitline = self.linesplitter(linereader)
        ubound = len(splitline)
        tobeshuffled = list(range(0,ubound))
        numpy.random.shuffle(tobeshuffled)
        i = 0
        titlecard = False
        blockcontent = []
        self.inContent = []
        rollover = 0
        tottime = 0
        titletime = 0
        timeclear = True
        while timeclear == True:
            #print(setupbool)
            if rollover > 3300 and blocktime >= 6900 and setupbool == False:
                #print('mid-block title generating')
                if titlecard == False:
                    print('building mid titles')
                    titlecardx = mpgen.titlecard(self.scheduledata, (self.blockindex))
                    ingestedcard = ingestedContent(titlecardx.contentlocation, titlecardx.runtime)
                    #print(titlecardx.contentpath)
                    #print(titlecardx.runtime)
                    titlecard = True
                self.inContent.append(ingestedcard)
                tottime = (tottime + ingestedcard.runtime)
                rollover = 0
            blockcontent.append(splitline[tobeshuffled[i],0])
            timechuck = (splitline[[tobeshuffled[i]],1])
            timechuck = int(numpy.asscalar(timechuck))
            sub = ingestedContent((folderpath + '\\' + str(splitline[tobeshuffled[i], 0])), timechuck)
            if (tottime + timechuck) > blocktime and setupbool == True and self.inContent != False:
                self.overrun = (tottime - blocktime)
                return self.inContent
                timeclear = False
            elif (tottime + timechuck) > (blocktime - self.overrun) and setupbool == False:
                print('Building trailing titles')
                if titlecard == False:
                    titlecardx = mpgen.titlecard(self.scheduledata, (self.blockindex))
                    ingestedcard = ingestedContent(titlecardx.contentlocation, titlecardx.runtime)
                    titlecard = True
                self.inContent.append(ingestedcard)
                tottime = (tottime + ingestedcard.runtime)
                print(titletime)
                self.overrun = (((tottime) - (blocktime)) + self.overrun)-200
                print(self.overrun)
                if (self.overrun < 0):
                    filler = mpgen.fillerup(-(self.overrun))
                    for x in filler.items:
                        print('whynowork')
                        ingestedfiller = ingestedContent(x.filepath, x.duration)
                        self.inContent.append(ingestedfiller)
                print(self.overrun)
                return self.inContent
                timeclear = False
            else:
                self.inContent.append(sub)
                tottime = (tottime + timechuck)
                rollover = (rollover + timechuck)
                i += 1

    def writeContent(self,dataDestination,toWrite):
        with open(dataDestination,'w', encoding = 'utf-8') as db:
            db.write("\n".join(map(str, toWrite)))
            print('Content Written to ' + str(dataDestination))

    def linesplitter(self, lines):
        Array1 = []
        Array2 = []
        Array3 = []
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
        return fullArray
         
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

    def buildtxt(self, archiveDir):
        datapath = (archiveDir + '\\Data.txt')
        archiveList = os.listdir(archiveDir)
        print(archiveList)
        datatotals = []
        for x in archiveList:
            if x.endswith(self.ext):
                xlength = self.get_len(archiveDir + '\\' + x)
                x = (x + '   length: ' + str(xlength) + ' endl')
                datatotals.append(x)
        with open(datapath,'w+',encoding = 'utf-8') as db:
            db.write("\n".join(map(str, datatotals)))       

class ingestedContent:
    def __init__(self,rootname,runtime):
        self.directory = rootname
        self.runtime = runtime

player = VLC((os.path.dirname(os.path.abspath(__file__))) + '\\' + 'VLC\\' + 'vlc.exe')
dayScheduler = scheduler(player)
dayScheduler.checkforschedule()
time.sleep(7)
dayScheduler.player.fullscreen()

