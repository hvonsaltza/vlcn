import os
import sys
from moviepy.editor import *
import random
import datetime
import numpy
sys.path.append(os.getcwd())
import structures

##contentpath = r"D:\VBN\Content\Titles\\"
##
##video = VideoFileClip(contentpath + "VHS Static Overlay.mp4")
##audio = AudioFileClip(contentpath + r'Audio\\' + "kindred.mp3")
##fog = audio.duration
##tako = video.duration
##print(tako)
##doggy = video.fx(vfx.loop, duration=fog)
##print(doggy.duration)
##print(fog)
#doggy.write_videofile(contentpath + "output.mp4", audio= contentpath + r'Audio\\' + "kindred.mp3")

class titlecard:
    def __init__(self, upcomingschedule, scheduleIndex=0, contentindex=0):
        self.contentpath = r"D:\VBN\Content\Titles\\"
        self.videolist = os.listdir(self.contentpath + r'BaseVideo\\')
        self.audiolist = os.listdir(self.contentpath + r'BaseAudio\\')
        numpy.random.shuffle(self.videolist)
        numpy.random.shuffle(self.audiolist)
        video = VideoFileClip(self.contentpath + r'BaseVideo\\' + self.videolist[1])
        audio = AudioFileClip(self.contentpath + r'BaseAudio\\' + self.audiolist[1])
        print ('selected this audio  and video for titlecard:')
        print (audio.filename)
        print (video.filename)
        fog = audio.duration
        vidtransform = video.fx(vfx.loop, duration=fog)
        scheduleString = ''
        i = 0
        ###print(upcomingschedule.blockindex)
        for x in upcomingschedule.scheduledata.remaining_schedule:
            ###print(x)
            if i >= upcomingschedule.blockindex:
                scheduleString = scheduleString + x.time_block + " " + x.contentname + '\n'
                ### print(scheduleString)
            i += 1

        txt = 'SCHEDULE:' + '\n' + scheduleString
        clip_txt = TextClip(txt, color='white', align='West', fontsize=32,
                            font='VCR-OSD-Mono', method='label')
        jiggle = clip_txt.set_pos(lambda t: (.05 + (.001*(numpy.cos(t))), 0.8), relative=True)

        txt = 'PLAY >'
        clip_txt = TextClip(txt, color='white', align='West', fontsize=48,
                            font='VCR-OSD-Mono', method='label')
        playsign = clip_txt.set_pos(lambda t: (.05 + (.0015*(numpy.cos(t))), 0.1), relative=True)

        final = CompositeVideoClip([
                vidtransform,
                jiggle, playsign])
        final.set_duration(fog).write_videofile(self.contentpath + str(scheduleIndex) + "out.mp4", audio=self.contentpath + r'BaseAudio\\' + self.audiolist[1], progress_bar = False)
        self.contentlocation = (self.contentpath + str(scheduleIndex) + "out.mp4")
        self.runtime = (fog)
        video.reader.close()
        video.audio.reader.close_proc()
        
class filler:
    def __init__(self, alottedtime):
        alottedtime = alottedtime
        print('filler time' + str(alottedtime))
        self.contentpath = r"D:\VBN\Content\Titles\\"
        video = VideoFileClip(self.contentpath + "PLITE.mp4")
        vidtransform = video.fx(vfx.loop, duration=alottedtime)
        final = final = CompositeVideoClip([
                vidtransform])
        final.set_duration(alottedtime).write_videofile(self.contentpath + "FILLER.mp4", audio = self.contentpath + "PLITE.mp4", progress_bar = False)
        self.contentlocation = (self.contentpath + "FILLER.mp4")
        self.runtime = alottedtime

class fillerup:
    def __init__(self, alottedtime):
        self.ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv", "m4v")
        self.contentpath = r"D:\VBN\Content\Filler"
        fillerList = os.listdir(self.contentpath)
        fillerContentList = []
        self.items = []
        for x in fillerList:
            if x.endswith(self.ext):
                fillerContentList.append(x)
        ubound = len(fillerContentList)
        tobeshuffled = list(range(0,ubound))
        numpy.random.shuffle(tobeshuffled)
        overtime = False
        i = 0
        while overtime == False:
            video = VideoFileClip(self.contentpath + '\\' + fillerContentList[tobeshuffled[i]])
            video.filepath = (self.contentpath + '\\' + fillerContentList[tobeshuffled[i]])
            if (alottedtime - video.duration) < 0:
                video.set_duration(alottedtime).write_videofile(self.contentpath + r'\\temp\\temp.mp4',audio=True, progress_bar = False)
                video = VideoFileClip(self.contentpath + r'\\temp\\temp.mp4')
                overtime = True
            vide = structures.ingested_content((self.contentpath + '\\' + fillerContentList[tobeshuffled[i]]), video.duration)
            self.items.append(vide)
            alottedtime = (alottedtime - video.duration)
            print(alottedtime)
            i += 1

class vid:
    def __init__(self, filepath, duration):
        self.filepath = filepath
        self.duration = duration

def best_fit_fill(duration, scheduler_inst, bfit=True):
    ext = (".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm", ".swf", ".vob", ".wmv", "m4v")
    contentpath = r"D:\VBN\Content\Filler"
    fillerList = os.listdir(contentpath)
    fillerContentList = []
    readylist = []
    for x in fillerList:
        if x.endswith(ext):
            fillerContentList.append(x)
    ubound = len(fillerContentList)
    tobeshuffled = list(range(0, ubound))
    numpy.random.shuffle(tobeshuffled)
    overtime = False
    i = 0
    alottedtime = duration
    ticker = 0
    print(alottedtime)
    if bfit == False:
        title = titlecard(scheduler_inst, scheduler_inst.blockindex)
        titlevid = structures.ingested_content(title.contentlocation, title.runtime)
        alottedtime = alottedtime - titlevid.runtime
        readylist.append(titlevid)
    while overtime == False:
        video = VideoFileClip(contentpath + '\\' + fillerContentList[tobeshuffled[i]])
        filepath = (contentpath + '\\' + fillerContentList[tobeshuffled[i]])
        vide = structures.ingested_content(filepath, video.duration)
        #print(filepath)
        if ticker > 3600 and bfit == False:
            readylist.append(titlevid)
            ticker = 0
            alottedtime = (alottedtime - titlevid.runtime)
        if (alottedtime - video.duration) < 0:
            if bfit == False:
                newvid = video.subclip(0, alottedtime)
                newvid.write_videofile(contentpath + r'\\temp\\' + str(int(scheduler_inst.blockindex)) + 'temp.mp4', audio=True, progress_bar=False)
                video = VideoFileClip(contentpath + r'\\temp\\' + str(int(scheduler_inst.blockindex)) + 'temp.mp4')
                vide = structures.ingested_content((contentpath + r'\\temp\\' + str(int(scheduler_inst.blockindex)) + 'temp.mp4'), video.duration)
                readylist.insert(0,vide)
            else:
                readylist.append(vide)
            overtime = True
        else:
            readylist.append(vide)
        video.reader.close()
        video.audio.reader.close_proc()
        alottedtime = (alottedtime - video.duration)
        ticker = (alottedtime + video.duration)
        i += 1
    if bfit == False:
        readylist.append(titlevid)
    return readylist

def get_vid_dura(filepath):
    video = VideoFileClip(filepath)
    video.reader.close()
    video.audio.reader.close_proc()
    return video.duration