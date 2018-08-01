import sys
import os
import time
import numpy
import subprocess
import json
import datetime
sys.path.append(os.getcwd())
import mpgen
import structures
from vlcfox import VLC

# Base class that enqueues content to the VLCclass
# Pass a vlcfox 'VLC' Class to it to specify the specific VLC instance it is attached to
class scheduler:
    def __init__(self, VLCclass):
        self.filepath = os.path.dirname(os.path.abspath(__file__))
        self.txtSettingsPath = (self.filepath + '\\' + 'Settings.txt')
        self.schedulesPath = (self.filepath + '\\' + 'Schedules')
        self.dbPath = (self.filepath + '\\' + 'db.txt')
        self.cdbPath = (self.filepath + '\\' + 'cdb.txt')
        self.vlcPath = (self.filepath + '\\' + 'VLC\\' + 'vlc.exe')
        self.contentPath = (self.filepath + '\\' + 'Content')
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv",
                    ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv", "m4v")
        self.player = VLCclass

#Checks for the daily schedule file in the schedules folder and if it exists, queues it. 
#Currently deprecated and simply builds the schedule fresh every startup.
    def checkforschedule(self):
        now = datetime.datetime.now()
        tocheck = (str(now)[:10])
        if os.path.exists(self.schedulesPath + tocheck + '.txt'):
            #self.queuefiles()
            pass
        else:
            self.buildSchedule()

#Constructs the schedule out of 'block' classes which are in turn made up of 'structures.ingested_content' classes.
#Contains a booleanflag "setupstatus" to avoid moviepy pausing to encode video at startup.
    def buildSchedule(self):
        self.scheduledata = structures.schedule(self.txtSettingsPath)
        print('Building...')
        self.scheduledata.remainingblocks()
        culledBlockList = self.scheduledata.remaining_schedule
        now = datetime.datetime.now()
        self.timenow = (str(now)[11:-7])
        self.blockindex = 0
        onthehour = (self.timenow)[:2]
        #print(onthehour)
        ontheminute = (self.timenow)[3:-3]
        #print(ontheminute)
        #print(self.scheduledata.remaining_schedule[0].start_time)
        crushhour = (int(onthehour) - int(self.scheduledata.remaining_schedule[0].start_time[:2]))*3600
        crushminute = (int(ontheminute) - int(self.scheduledata.remaining_schedule[0].start_time[2:]))*60
        sectime = crushhour + crushminute
        #print(sectime)
        i = 0
        blockruntime = 0
        overrun = 0
        setupstatus = True
        blockSeek = False
        self.overrun = 0
        print('Starting Enqueue Loop')
        for x in culledBlockList:
            hard_block = block(x, setupstatus, self, overrun, x.airtype)
            overrun = hard_block.overrun
            print(hard_block.debugline())
            for y in hard_block.full_content:
                if not blockSeek:
                    blockruntime = (y.runtime + blockruntime)
                    if blockruntime >= sectime:
                        self.player.add(y.directory)
                        self.player.seek((sectime - (blockruntime - y.runtime)))
                        blockSeek = True
                elif blockSeek == True:
                    self.player.enqueue(y.directory)
            i += 1
            setupstatus = False
            self.blockindex += 1

#Takes a schedule passed from the daily schedule settings and cuts it    down to 
# just blocks proceeding from the current time.

    def buildtxt(self, archiveDir):
        datapath = (archiveDir + '\\Data.txt')
        archiveList = os.listdir(archiveDir)
        print(archiveList)
        datatotals = []
        for x in archiveList:
            if x.endswith(self.ext):
                xlength = mpgen.get_vid_dura(archiveDir + '\\' + x)
                xlength = int(numpy.ceil(xlength))
                x = (x + '   length: ' + str(xlength) + ' endl  aired: NO')
                datatotals.append(x)
        with open(datapath,'w+',encoding = 'utf-8') as db:
            db.write("\n".join(map(str, datatotals)))

    def write_serial(self, archivedir, content):
        datapath = (archivedir + '\\Data.txt')
        with open(datapath, 'r', encoding='utf-8') as cdb:
            linereader = cdb.read().splitlines()
        newlines = []
        for x in linereader:
            skipx = False
            Rbound = x.find('length: ')
            xname = (x[:Rbound-3])
            if x.endswith('NO'):
                for y in content:
                    if y.directory == archivedir + '\\' + xname:
                        i = x[:-3] + ' YS'
                        newlines.append(i)
                        skipx = True
            if skipx == False:
                newlines.append(x)
        with open(datapath,'w+',encoding = 'utf-8') as db:
            db.write("\n".join(map(str, newlines)))   
            print('wrotenew')     
        
'''The 'block' class contains the list of 'IngestedContent' classes that should be loaded by the scheduler. it is provided, from the scheduler, mainly:
contentLine, a 'scheduleline' class that contains all the settings for a fiven block, taken from a single line in the settings folder.
setupbool, a boolean value of whether or not the script has loaded any content/ initialized yet. this is always passed as 'True' at first, 
    and for all subsequent blocks it is passed as 'false'
schedulerInst, the specific 'scheduler' that called the block.
last_block_ov, the overrun (in seconds) from the last block.
airtype, a currently useless param that determines what kind of fill should be used for getting content, future types should include:
    Random, the type for random episode airing with no specific order
    Serial, the type for airing episodes in order over days/weeks. Keeps track by rewriting DATA.txt after an episode is set to be aired. Not implemented yet.
'''
class block:
    def __init__(self, contentLine, setupbool, schedulerInst, last_block_ov, airtype='Random'):
        self.allotment = contentLine.allotment
        self.allotment = (self.allotment - last_block_ov)
        self.content_dir = (schedulerInst.contentPath + '\\' + (contentLine.contentname))
        self.runtime = 0
        print(airtype)
        print(self.content_dir)
        #print(os.path.exists(self.content_dir + '\\Data.txt'))
        if os.path.exists(self.content_dir + '\\Data.txt') == False:
            print('Generating Data.txt for ' + (contentLine.contentname))
            schedulerInst.buildtxt(self.content_dir)
        with open((self.content_dir + '\\Data.txt'), 'r', encoding='utf-8') as cdb:
            linereader = cdb.read().splitlines()
        self.content_array = []
        for x in linereader:
            tline = dataline(x)
            self.content_array.append(tline)
        print('Content Array:')
        print(self.content_array)
        self.index_array = self.fetch_index_array(self.content_array, airtype)
        self.main_content = self.get_main(self.content_array, self.index_array, self.allotment)
        for x in self.main_content:
            self.runtime = self.runtime + x.runtime
        self.difference = (self.allotment - self.runtime)
        if self.difference > 1000:
            self.difference = 1000
        if self.difference > 0:
            self.full_content = self.get_filler(self.main_content, self.difference, setupbool, schedulerInst)
        else:
            self.full_content = self.main_content
        self.runtime = 0
        for x in self.full_content:
            self.runtime = self.runtime + x.runtime
        self.overrun = (self.runtime - self.allotment)
        print('THE AIRTYPE IS ' + airtype)
        if airtype == 'SERIAL':
            schedulerInst.write_serial(self.content_dir, self.full_content)

    def getdir(self, contentline):
        os.listdir

    def fetch_index_array(self, content_array, airtype):
        ubound = len(content_array)
        print('Airtype and Ubound')
        print(airtype)
        print(ubound)
        tobeshuffled = []
        if airtype == 'RANDOM':
            tobeshuffled = list(range(0, ubound))
            numpy.random.shuffle(tobeshuffled)
        if airtype == 'SERIAL':
            i = 0
            for x in content_array:
                #print(x.status)
                print(i)
                if x.status == 'NO':
                    tobeshuffled = list(range(i, ubound-1))
                    print('Tobeshuffled:')
                    print(tobeshuffled)
                    print(content_array[i])
                    break
                elif i >= ubound:
                    tobeshuffled = list(range(0, ubound))
                    print('Tobeshuffled:')
                    print(tobeshuffled)
                    break
                i += 1
        if not tobeshuffled:
            print ('Array Index was null. Check to make sure SERIAL airing had remaining eps.')
            tobeshuffled = list(range(0, ubound))
            numpy.random.shuffle(tobeshuffled)
        return tobeshuffled

    def get_main(self, contentarray, indexarray, allotment):
        content = []
        fselect = (contentarray[indexarray[0]])
        print('FSELECT NAME: AND CONTENTARRAY')
        print(fselect.name)
        for x in contentarray:
            print(x.name)
        first_selection = structures.ingested_content((self.content_dir + '\\' + fselect.name), fselect.length)
        content.append(first_selection)
        runtime = (content[0]).runtime
        print(runtime)
        timeclear = True
        print(len(contentarray))
        if (content[0]).runtime > allotment:
            return content
        if len(contentarray) == 1:
            return content
        else:
            i = 1
            while timeclear == True:
                print(len(contentarray))
                print(len(indexarray))
                print(i)
                fselect = (contentarray[indexarray[i]])
                first_selection = structures.ingested_content((self.content_dir + '\\' + fselect.name), fselect.length)
                print(fselect.name)
                print(fselect.length)
                print(first_selection.runtime)
                if runtime + first_selection.runtime > (allotment + 300):
                    timeclear = False
                else:
                    runtime = runtime + first_selection.runtime
                    content.append(first_selection)
                    i += 1
                if i == len(indexarray):
                    return content
        return content

    def build_content(self, contentarray, indexarray, allotment):
       seed = self.getmain()
       allotment = allotment - seed.duration
       while allotment > 0:
           add = self.getmain()


    def get_filler(self, main_content, difference, setupbool, scheduler_inst):
        print('DIFFERENCE:')
        print(difference)
        unpack = mpgen.best_fit_fill(difference, scheduler_inst, setupbool)
        unpacked = []
        for x in unpack:
            y = structures.ingested_content(x.directory, x.runtime)
            unpacked.append(y)
        j = len(unpacked)
        #print(j)
        h = len(main_content)
        #print(h)
        distro = int(numpy.floor((j/h)))
        #print(distro)
        if distro < 1:
            distro = 1
        #print(distro)
        i = 1
        k = 1
        final_content = []
        while i <= h:
            final_content.append(main_content[i-1]) 
            while k <= distro:
                if unpacked == []:
                    print('skippedapack')
                    break
                nextcontent = unpacked.pop()
                final_content.append(nextcontent)
                k += 1
            i += 1
            k = 1
        return final_content

    def debugline(self):
        contentstring = ''
        for x in self.full_content:
            contentstring = contentstring + x.directory[-15:]
        allotmentstr = str(self.allotment)
        diffstr = str(self.difference)
        allstr = contentstring + '  Allotment:  ' + allotmentstr + '  Difference:  ' + diffstr + '  Overrun:  ' + str(self.overrun)
        return allstr

class dataline:
    def __init__(self, line):
        Rbound = line.find('length: ')
        self.name = (line[:Rbound-3])
        Lbound = line.find('length: ')
        Rbound = line.find(' endl')
        self.length = (int(line[Lbound+8:Rbound]))
        Lbound = line.find('aired: ')
        self.status = str(line[Lbound+7:])
        print(self.status)

#gary = block('0200-0400', 'gary',)
player = VLC((os.path.dirname(os.path.abspath(__file__))) + '\\' + 'VLC\\' + 'vlc.exe')
dayScheduler = scheduler(player)
dayScheduler.checkforschedule()
#time.sleep(7)
#dayScheduler.player.fullscreen()