import os
from moviepy.editor import *
import random
import datetime
import numpy

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
    def __init__(self, upcomingschedule, scheduleIndex=0):
        self.schedule = upcomingschedule
        self.contentpath = r"D:\VBN\Content\Titles\\"
        video = VideoFileClip(self.contentpath + "VHS Static Overlay.mp4")
        audio = AudioFileClip(self.contentpath + r'Audio\\' + "kindred.mp3")
        fog = audio.duration
        vidtransform = video.fx(vfx.loop, duration=fog)
        scheduleString = ''
        i = 0
        for x in self.schedule:
            if i >= scheduleIndex:
                docker = x
                #print(docker)
                scheduleString = scheduleString + docker
            i += 1
        txt = 'SCHEDULE:' + '\n' + scheduleString
        clip_txt = TextClip(txt,color='white', align='West',fontsize=32,
                    font='VCR-OSD-Mono', method='label')
        jiggle = clip_txt.set_pos(lambda t:(.05 + (.001*(numpy.cos(t))), 0.8), relative=True)
        txt = 'PLAY >'
        clip_txt = TextClip(txt,color='white', align='West',fontsize=48,
                    font='VCR-OSD-Mono', method='label')
        playsign = clip_txt.set_pos(lambda t:(.05 + (.0015*(numpy.cos(t))), 0.1), relative=True)
        final = CompositeVideoClip([
                vidtransform,
                jiggle, playsign])
        final.set_duration(fog/5).write_videofile(self.contentpath + str(scheduleIndex) + "out.mp4", audio= self.contentpath + r'Audio\\' + "kindred.mp3", progress_bar = False)
        self.contentlocation = (self.contentpath + str(scheduleIndex) + "out.mp4")
        self.runtime = (fog)
        
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
            vide = vid((self.contentpath + '\\' + fillerContentList[tobeshuffled[i]]), video.duration)
            self.items.append(vide)
            alottedtime = (alottedtime - video.duration)
            print(alottedtime)
            i += 1

class vid:
    def __init__(self, filepath, duration):
        self.filepath = filepath
        self.duration = duration
