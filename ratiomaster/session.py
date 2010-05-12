from time import time
import random

class SessionState(object):
    def __init__(self, event='started', uploaded=0, rate=0, hostname='www.example.com'):
        self.state=event
        self.uploaded = int(uploaded)
        self.rate = rate
        self.hostname = hostname
        self.lasttime=time()
    def setState(self, event, uploaded, rate=None):
        if rate != None:
            self.rate = rate
        uploaded = int(uploaded)
        random.seed()
        newtime = time()
        fakeuploaded = int((newtime-self.lasttime)*(self.rate*1024)*(random.randrange(7000, 12000)/10000.)) + self.uploaded
        print "uploaded = %s" % uploaded
        print "fakeuploaded = %s" % fakeuploaded
        if self.state == 'stopped':
            if event=='started':
                self.uploaded = uploaded
        else: #(self.state == 'started' or self.state=='completed' or self.state=='' or self.state=='paused'):
            self.uploaded = fakeuploaded
        if uploaded > fakeuploaded:
            print "uploaded > fakeuploaded"
            self.uploaded = uploaded
        print "self.uploaded = %s" % self.uploaded
        self.lasttime = newtime
        self.state = event
    def update(self):
        self.setState(self.state, self.uploaded, self.rate)
    def getUploaded(self):
        return self.uploaded
    def setRate(self,rate):
        print "Rate set to %s" % rate
        self.rate=rate
        

class TrackerSessions(object):
    trackersessions = {}
    def get(self, info_hash):
        return self.trackersessions[info_hash]
    def getAll(self):
        return self.trackersessions
    def add(self, info_hash, event='started', uploaded=0, rate=0,hostname=None):
        s = SessionState(event, uploaded, rate,hostname=hostname)
        self.trackersessions[info_hash] = s
        return s
        
