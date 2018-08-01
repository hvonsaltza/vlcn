import datetime

class ingested_content:
    def __init__(self, rootname, runtime):
        self.directory = rootname
        self.runtime = runtime

class schedule:
    def __init__(self, path):
        self.linereader = ''
        with open(path, 'r', encoding='utf-8') as settings:
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
        self.blocklist = rawinfo
        self.final_list = []
        day = ''
        for x in self.blocklist:
            if x.find('DAY:') >= 0:
                day = x[-4:]
                continue
            h = scheduleline(x, day)
            #print(h)
            self.final_list.append(h)

    def remainingblocks(self):
        now = datetime.datetime.now()
        timenow = (str(now)[11:-10])
        hour = (int(str(now)[11:-13]))
        weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT','SUN']
        day = weekdays[(now.weekday())]
        #print(day)
        print(hour)
        self.remaining_schedule = []
        for x in self.final_list:
            timechk = (int((x.start_time)[:2]))
            backchk = (int((x.end_time)[:2]))
            if (timechk <= hour < backchk or hour <= timechk) and str(x.day_of_week) == str(day):
                self.remaining_schedule.append(x)    

class scheduleline:
    def __init__(self, line, day_of_week='Any'):
        self.time_block = line[:9]
        self.start_time = line[:4]
        self.end_time = line[5:9]
        self.contentname = line[10:-8]
        self.airtype = line[-7:-1]
        self.allotment = (((int(self.end_time) - int(self.start_time))/100)*3600)
        self.day_of_week = day_of_week[:-1]
        #print(self.time_block)
